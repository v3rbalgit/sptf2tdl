from __future__ import annotations
from dataclasses import dataclass
from typing import cast, List, Tuple, Any
from dotenv import load_dotenv
from os import getenv

from urllib.parse import urlsplit
import spotify, asyncio

# Exception classes
class BadLink(ValueError):
  '''Error class indicating bad link to a Spotify playlist'''
  pass

class EmptyPlaylist(ValueError):
  '''Error class indicating an empty Spotify playlist'''
  pass

# Spotify track dataclass
@dataclass
class SpotifyTrack:
  name: str
  artists: List[str]
  album: str
  length: int
  isrc: str

# Spotify Link
class SpotifyLink:
  spotify_base: str = 'open.spotify.com'

  def __init__(self, /, url: str = None, playlist_id: str = None) -> None:
    self._url = url
    self._playlist_id = playlist_id

  @property
  def id(self) -> str | None:
    return self._playlist_id

  @property
  def url(self) -> str | None:
    return self._url

  @classmethod
  def from_url(cls, url: str) -> SpotifyLink:
    if not isinstance(url, str):
      raise TypeError('Link URL must be of type "string"')

    url_components = urlsplit(url)

    if url_components.netloc != SpotifyLink.spotify_base:
      raise BadLink(f'Not a Spotify url: "{url_components.netloc!r}" in {url}')

    resource, resource_id = url_components.path.split('/')[1:3]           # first element is an empty string

    if not resource in ('playlist'):                # can be extended to other resources if needed
      raise BadLink(f'Not a valid link: "{url_components.path!r}" in {url}')

    return cls(url, resource_id)

  @classmethod
  def from_id(cls, id: str) -> SpotifyLink:
    if not isinstance(id, str):
      raise TypeError('Link ID must be of type "string"')

    url = f'https://{cls.spotify_base}/playlist/{id}'

    return cls(url, id)

  def __repr__(self) -> str:
    return (
      f'{self.__class__.__name__}('
      f'{self._url},'
      f'{self._playlist_id})'
      )


# Spotify playlist with all required information (id, url, tracks, name, description)
class SpotifyPlaylist(SpotifyLink):
  def __init__(self, /, url: str = None, playlist_id: str = None):
    super().__init__(url, playlist_id)

    load_dotenv()

    self._loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self._loop)

    self._client_id: str | None = getenv('client_id')
    self._client_secret: str | None = getenv('client_secret')
    self._tracks: List[SpotifyTrack] = self._get_tracks()
    self._name, self._description, self._owner = self._get_info()

  @property
  def tracks(self):
    return self._tracks

  @property
  def name(self):
    return self._name

  @property
  def description(self):
    return self._description

  @property
  def owner(self):
    return self._owner

  def _get_tracks(self) -> List[SpotifyTrack]:
    tracks: List[Any] = self._loop.run_until_complete(self.__async_get_tracks())

    return [SpotifyTrack(
      track['track']['name'],
      [artist['name'] for artist in track['track']['artists']],
      track['track']['album']['name'],
      track['track']['duration_ms'],
      track['track']['external_ids']['isrc']) for track in tracks]

  async def __async_get_tracks(self):
    async with spotify.Client(self._client_id, self._client_secret) as client:
      playlist_tracks: List[spotify.PlaylistTrack] = await client.http.get_playlist_tracks(self.id)
      playlist_tracks: List[spotify.Track] = playlist_tracks['items']

      if not playlist_tracks:
        raise EmptyPlaylist(f'Playlist {self.id} is empty')
      elif len(playlist_tracks) == 100:
        offset: int = len(playlist_tracks)

        while offset == len(playlist_tracks):
          more_playlist_tracks = await client.http.get_playlist_tracks(self.id, offset=offset, limit=100)
          playlist_tracks.extend(more_playlist_tracks['items'])
          offset += 100

      return playlist_tracks

  def _get_info(self) -> Tuple[str, str]:
    return self._loop.run_until_complete(self.__async_get_info())

  async def __async_get_info(self) -> Tuple[str, str]:
    async with spotify.Client(self._client_id, self._client_secret) as client:
      playlist: spotify.Playlist = await client.http.get_playlist(self.id)

      return (playlist['name'],
      playlist['description'],
      playlist['owner']['display_name'] if playlist['owner']['display_name'] else playlist['owner']['id'])

  @classmethod
  def from_url(cls, url: str) -> SpotifyPlaylist:
      return cast(SpotifyPlaylist, super().from_url(url))

  @classmethod
  def from_id(cls, id: str) -> SpotifyPlaylist:
      return cast(SpotifyPlaylist, super().from_id(id))