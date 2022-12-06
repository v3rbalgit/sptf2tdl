from __future__ import annotations
from dataclasses import dataclass
import tidalapi
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from itertools import chain

from sptf_classes import SpotifyTrack, SpotifyPlaylist
from tools import filter_name


@dataclass
class TidalCredentials:
  token_type: Optional[str]
  access_token: Optional[str]
  refresh_token: Optional[str]
  expiry_time: Optional[datetime]


class LoginError(ValueError):
  '''Error indicating a login has failed'''
  pass

class PlaylistError(ValueError):
  '''Error indicating a playlist already exists'''
  pass


class TidalUser:
  def __init__(self, /, credentials: Optional[TidalCredentials]) -> None:
    self._credentials: Optional[TidalCredentials] = credentials
    self._session: tidalapi.Session = tidalapi.Session()
    self._login: tidalapi.session.LinkLogin | None = None
    self._login_uri: Any | None = None
    self._login_future = None

    if not self._credentials:
      self._login, self._login_future = self._session.login_oauth()
      self._login_uri = self._login.verification_uri_complete

  @property
  def login_uri(self):
    return self._login_uri

  @property
  def user(self):
    return self._session.user

  @property
  def session(self):
    return self._session

  @property
  def credentials(self):
    return self._credentials

  def check_login(self) -> bool:
    if self._session.check_login() == True:
      return True
    else:
      raise LoginError('User not logged in')

  def login(self, /, callback: Optional[Callable] = None) -> bool:
    if not self._credentials:
      try:
        self._login_future.result()
        self._credentials = TidalCredentials(
          self._session.token_type,
          self._session.access_token,
          self._session.refresh_token,
          self._session.expiry_time,
        )

        if callback: callback(self._credentials)       # <- get notified when the user has logged in

        return self.check_login()
      except TimeoutError:
        raise LoginError('Login time has expired')
    else:
      self._session.load_oauth_session(self._credentials.token_type, self._credentials.access_token, self._credentials.refresh_token, self._credentials.expiry_time)

      return self.check_login()


class TidalTransfer:
  def __init__(self, /, user: TidalUser, playlist: SpotifyPlaylist) -> None:
    self._user: Optional[tidalapi.User] = user.user
    self._session: tidalapi.Session = user.session
    self._playlist_to_transfer: SpotifyPlaylist = playlist
    self._new_playlist: tidalapi.UserPlaylist
    self._tracks_not_found: List[SpotifyTrack] = []

  @property
  def tracks_not_found(self):
    return self._tracks_not_found

  @property
  def new_playlist(self):
    return self._new_playlist

  def _compare_tracks(self, /, tracks: List[tidalapi.media.Track], track_name: str, artists: List[str], album_name: str, track_duration: int) -> tidalapi.Track | None:
    selected_tracks: List[Dict[str, tidalapi.media.Track | List[str]] | float] = []

    # Filter every track in search results by common track name words and artist name words
    for track in tracks:
      common_names: List[str] = list(set(filter_name(track.name)) & set(filter_name(track_name)))
      if common_names:
        common_artists: List[str] = list(set(chain.from_iterable(filter_name(artist.name) for artist in track.artists)) & set(chain.from_iterable(filter_name(a) for a in artists)))
        if common_artists:
          selected_tracks.append({
            'track': track,
            'common_names': common_names,
            'common_artists': common_artists,
            'common_album': list(set(filter_name(track.album.name)) & set(filter_name(album_name))),
            'duration_score': 10 ** (1 - (abs(track_duration - (track.duration * 1000)) / track_duration))  # score the found track length based on its proximity to original track length
          })

    if not selected_tracks:
      return None

    # Further filtering
    for key in ['common_names', 'common_artists', 'common_album']:
      selected_tracks.sort(key=lambda x: len(x[key]), reverse=True)
      selected_tracks: List[tidalapi.media.Track] = list(filter(lambda x: len(x[key]) == len(selected_tracks[0][key]), selected_tracks))
    selected_tracks.sort(key=lambda x: x['duration_score'], reverse=True)

    # Prefer master quality tracks
    master_tracks: List[tidalapi.media.Track] = list(filter(lambda x: x['track'].audio_quality == tidalapi.Quality.master, selected_tracks))

    return master_tracks[0]['track'] if master_tracks else selected_tracks[0]['track']


  def create_playlist(self, overwrite: bool = False) -> None:
    existing_playlist: List[tidalapi.UserPlaylist] = list(filter(lambda pl: pl.name == self._playlist_to_transfer.name, self._user.playlists()))  # type: ignore

    if existing_playlist:
      if overwrite:
        existing_playlist[0].delete()
        self.create_playlist(overwrite)
      raise PlaylistError(f'Playlist with name "{self._playlist_to_transfer.name}" already exists', self._playlist_to_transfer.name)

    self._new_playlist: tidalapi.UserPlaylist = self._user.create_playlist(self._playlist_to_transfer.name, self._playlist_to_transfer.description)  # type: ignore


  def transfer_playlist(self, callback: Optional[Callable] = None) -> None:
    if not self._new_playlist:
      raise PlaylistError(f'Playlist with name {self._playlist_to_transfer.name} does not exist on user "{self._user.id}"', self._playlist_to_transfer.name, self._user.id)

    for i, track in enumerate(self._playlist_to_transfer.tracks):
      track_name: str = track.name
      artists: List[str] = [str(artist) for artist in track.artists]
      album: str = track.album
      track_duration: int = track.length

      if callback: callback(i, track)

      tracks_found: List[tidalapi.media.Track] = []
      artist_words: List[str] = list(chain.from_iterable(filter_name(artist) for artist in artists))
      track_words: List[str] = list(filter(lambda x: (x not in ('feat.', 'ft.')) and (x not in artist_words), filter_name(track_name)))
      whole_phrase: List[str] = track_words + artist_words

      # Use words in track's and artists' names to search
      for j, word in enumerate(whole_phrase):
        if j == 0: continue   # skip using just one word (too vague)

        limit: int = 5 + len(whole_phrase) - j
        search_result: Dict[str, Any] = self._session.search(" ".join(whole_phrase[:j+1]), models=[tidalapi.media.Track], limit=limit)
        isrc_found: List[tidalapi.Track] = list(filter(lambda tr: tr.isrc == track.isrc, search_result['tracks']))

        # Check for exact match
        if isrc_found:
          # Prefer master quality tracks
          master_tracks: List[tidalapi.Track] = list(filter(lambda x: x.audio_quality == tidalapi.Quality.master, isrc_found))
          self._new_playlist.add([master_tracks[0].id if master_tracks else isrc_found[0].id])            # found by isrc => 1:1 match
          break
        else:
          # If the search results generate fewer entries than we asked for, there is no need to continue adding words to the search query, it will only generate fewer results...
          if len(search_result['tracks']) < limit:
            if len(search_result['tracks']) == 0 and j == 1:
              self._tracks_not_found.append(track)                  # found nothing (extremely rare)
              break
            else:
              # ...fill list with all search results and break out of the loop to search for another track
              tracks_found.extend(search_result['tracks'])
              found_track: tidalapi.Track | None = self._compare_tracks(tracks_found, track_name, artists, album, track_duration)

              if found_track:
                self._new_playlist.add([found_track.id])            # found by similar name, artists, album
                break
              else:
                self._tracks_not_found.append(track)           # found nothing (extremely rare)
                break

          # Fill list with tracks found until we go through the whole phrase of name and artists
          tracks_found.extend(search_result['tracks'])

          # When we're on the last word and no exact match was found, use the comparison algorithm
          if len(whole_phrase) - 1 == j:
            found_track: tidalapi.Track | None = self._compare_tracks(tracks_found, track_name, artists, album, track_duration)

            if found_track:
              self._new_playlist.add([found_track.id])              # found by similar name and artists
            else:
              self._tracks_not_found.append(track)                  # found nothing (extremely rare)

