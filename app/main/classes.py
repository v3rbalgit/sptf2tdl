from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from app.utils import filter_name
from enum import StrEnum

import spotify, tidalapi, asyncio
from tidalapi import Track, UserPlaylist, Quality

# Error enum
class Err(StrEnum):
  INVALID_URL = "You entered an invalid Spotify link. Check the URL and try again."
  LOGIN_ERR = "There was a problem with your TIDAL login. Please try logging in again."
  UNKNOWN_ERR = "Unknown error has occured. Please try again later."

# Error classes
class LoginError(ValueError):
  '''Error indicating a login has failed'''
  pass

# Spotify track dataclass
@dataclass
class SpotifyTrack:
  '''Holds Spotify track information'''
  name: str
  artists: List[str]
  album: str
  length: int
  isrc: str
  image: str

  def __str__(self) -> str:
    return f'"{self.name}" by {", ".join(self.artists)} from "{self.album}" ({int((self.length/1000)/60)}:{str(int((self.length/1000)%60)).zfill(2)})'

# Spotify playlist dataclass
@dataclass
class SpotifyPlaylist:
  '''Holds Spotify playlist information'''
  id: str
  tracks: List[SpotifyTrack]
  name: str
  description: Optional[str]
  owner: str

  def __str__(self) -> str:
    return f'Playlist {self.id} by {self.owner} (Name: {self.name}, Tracks: {len(self.tracks)})'

# Spotify client
class SpotifyClient:
  loop = asyncio.new_event_loop()

  def __init__(self, client_id: str, client_secret: str) -> None:
    self._client_id = client_id
    self._client_secret = client_secret

  # Find a Spotify playlist by ID
  def get_playlist(self, id: str) -> Optional[SpotifyPlaylist]:
    return self.loop.run_until_complete(self._get_playlist(id))

  async def _get_playlist(self, id: str) -> Optional[SpotifyPlaylist]:
    async with spotify.Client(self._client_id, self._client_secret) as client:
      try:
        playlist = await client.http.get_playlist(id)

        tracks = await client.http.get_playlist_tracks(id, limit=100)
        tracks = tracks['items']

        if len(tracks) == 100:
          offset: int = len(tracks)

          while offset == len(tracks):
            more_tracks = await client.http.get_playlist_tracks(id, offset=offset, limit=100)
            tracks.extend(more_tracks['items'])
            offset += 100

        return SpotifyPlaylist(
          id,
          [SpotifyTrack(
              track['track']['name'],
              [artist['name'] for artist in track['track']['artists']],
              track['track']['album']['name'],
              track['track']['duration_ms'],
              track['track']['external_ids']['isrc'],
              track['track']['album']['images'][0]['url']) for track in tracks] if tracks else [],      # index 0 for big image, 1 smaller, 2 smallest
          playlist['name'],
          playlist['description'],
          playlist['owner']['display_name'] if playlist['owner']['display_name'] else playlist['owner']['id']
        )
      except BaseException:
        return None

# Dataclass for holding TIDAL user's login credentials
@dataclass
class TidalCredentials:
  '''Holds user's login information'''
  token_type: Optional[str]
  access_token: Optional[str]
  refresh_token: Optional[str]
  expiry_time: Optional[datetime]

# Login to TIDAL
class TidalLogin:
  credentials: Optional[TidalCredentials]
  session: tidalapi.Session

  def __init__(self) -> None:
    self.session = tidalapi.Session()
    self.credentials = None
    self._login, self._login_future = self.session.login_oauth()
    self._login_uri = self._login.verification_uri_complete

  @property
  def login_uri(self):
    return self._login_uri

  # Helper function to check login status
  def check_login(self) -> bool:
    if self.session.check_login() == True:
      return True
    else:
      raise LoginError('User not logged into TIDAL')

  # Initiate login
  def login(self) -> None:
    if not self.credentials:
      try:
        self._login_future.result()

        self.credentials = TidalCredentials(
          self.session.token_type,
          self.session.access_token,
          self.session.refresh_token,
          self.session.expiry_time,
        )
      except TimeoutError:
        raise LoginError('Login time has expired', self.login_uri)
    else:
      try:
        self._login_future.cancel()
        self.session.load_oauth_session(self.credentials.token_type, self.credentials.access_token, self.credentials.refresh_token, self.credentials.expiry_time)
      except BaseException as e:
        raise LoginError(e.args[0])

# Methods for communicating with TIDAL using the TidalLogin
class TidalTransfer:
  session: tidalapi.Session

  def __init__(self, tidal_login: TidalLogin) -> None:
    tidal_login.check_login()
    self.session = tidal_login.session

  # Create new playlist from Spotify playlist
  def create_playlist(self, playlist: SpotifyPlaylist) -> Optional[UserPlaylist]:
    existing_playlist = list(filter(lambda pl: pl.name == playlist.name, self.session.user.playlists()))  # type: ignore

    return self.session.user.create_playlist(playlist.name, playlist.description) if not existing_playlist else None  # type: ignore

  # Find 1st playlist on user account matching by name
  def find_playlist(self, playlist: SpotifyPlaylist) -> Optional[UserPlaylist]:
    playlists = self.session.user.playlists()   #type: ignore
    found_playlist = list(filter(lambda pl: pl.name == playlist.name, playlists))

    return found_playlist[0] if found_playlist else None

  # Find a track from Spotify playlist on TIDAL
  def find_track(self, track: SpotifyTrack) -> Optional[Track]:
    tracks_found: List[Track] = []

    # Prepare search words
    artist_words: List[str] = [word for artist in track.artists for word in filter_name(artist)]
    track_words: List[str] = list(filter(lambda x: (x not in ('feat.', 'ft.', 'with')) and (x not in artist_words), filter_name(track.name)))
    whole_phrase: List[str] = track_words + artist_words

    # Try adding search words to query until match is found
    for i, word in enumerate(whole_phrase):
      if i == 0: continue   # skip using just one word (too vague)

      limit: int = 5 + len(whole_phrase) - i    # search limit inversely proportional to number of search words
      search_result = self.session.search(" ".join(whole_phrase[:i+1]), models=[tidalapi.media.Track], limit=limit)
      isrc_found: List[Track] = list(filter(lambda tr: tr.isrc == track.isrc, search_result['tracks']))

      # Check for exact match
      if isrc_found:
        # Prefer master quality tracks
        master_tracks: List[Track] = list(filter(lambda x: x.audio_quality == Quality.master, isrc_found))
        return master_tracks[0] if master_tracks else isrc_found[0]            # found by isrc => 1:1 match
      else:
        if len(search_result['tracks']) < limit:
          if not search_result['tracks'] and i == 1:
            return None
          tracks_found.extend(search_result['tracks'])
          return self._filter_tracks(tracks_found, track)

        tracks_found.extend(search_result['tracks'])

        if len(whole_phrase) - 1 == i:
          return self._filter_tracks(tracks_found, track)

  # Select closest match to the original track
  def _filter_tracks(self, /, tidal_tracks: List[Track], spotify_track: SpotifyTrack) -> Optional[Track]:
    selected_tracks = []

    # Filter every track in search results by common track name words and artist name words
    for tidal_track in tidal_tracks:
      common_names: List[str] = list(set(filter_name(tidal_track.name)) & set(filter_name(spotify_track.name)))   # type: ignore
      if common_names:
        common_artists: List[str] = list(set([word for artist in tidal_track.artists for word in filter_name(artist.name)]) & set([word for artist in spotify_track.artists for word in filter_name(artist)]))   # type: ignore
        if common_artists:
          selected_tracks.append({
            'track': tidal_track,
            'common_names': common_names,
            'common_artists': common_artists,
            'common_album': list(set(filter_name(tidal_track.album.name)) & set(filter_name(spotify_track.album))),  # type: ignore
            'duration_score': 10 ** (1 - (abs(spotify_track.length - (tidal_track.duration * 1000)) / spotify_track.length))  # score the found track length based on its proximity to original track length
          })

    if not selected_tracks:
      return None

    # Further filtering, by most common names, artists, album, and finally sort according to closest track length to the original
    for key in ['common_names', 'common_artists', 'common_album']:
      selected_tracks.sort(key=lambda x: len(x[key]), reverse=True)
      selected_tracks = list(filter(lambda x: len(x[key]) == len(selected_tracks[0][key]), selected_tracks))
    selected_tracks.sort(key=lambda x: x['duration_score'], reverse=True)

    # Prefer master quality tracks
    master_tracks = list(filter(lambda x: x['track'].audio_quality == Quality.master, selected_tracks))
    return master_tracks[0]['track'] if master_tracks else selected_tracks[0]['track']