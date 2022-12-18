from flask import session
from flask_socketio import emit
from typing import List, Optional

from .. import socketio
import asyncio
from dotenv import load_dotenv
load_dotenv()
from os import getenv

from .classes import TidalLogin, TidalCredentials, TidalTransfer, SpotifyClient, SpotifyPlaylist, SpotifyTrack

from tidalapi import UserPlaylist, Track

from app import db
from ..models import User

client = SpotifyClient(getenv('client_id', ''), getenv('client_secret', ''))

async def handle_track(transfer: TidalTransfer, i: int, track: SpotifyTrack):
  data = {
    'index': i,
    'name': track.name,
    'artists': ", ".join(track.artists),
    'image': track.image
  }
  emit('next_track', data)

  tidal_track: Optional[Track] = await transfer.find_track(track)

  if not tidal_track:
    emit('no_match', data)
  return tidal_track

@socketio.on('start_transfer', namespace='/transfer')
def get_playlist(overwrite: bool):
  id = session.get('id')
  user: List[User] = db.session.execute(db.select(User).filter_by(id=id)).first()

  spotify_playlist: Optional[SpotifyPlaylist] = client.get_playlist(session['splid'])

  if spotify_playlist:
    tracks: List[SpotifyTrack] = spotify_playlist.tracks
    name: str = spotify_playlist.name

    if not tracks:
      emit('playlist_empty')
      return None

    emit('playlist_info', { 'name': name, 'total': len(tracks)})

    login = TidalLogin()
    login.credentials = TidalCredentials(user[0].token_type, user[0].access_token, user[0].refresh_token, user[0].expiry_time)
    login.login()

    transfer = TidalTransfer(login)

    tidal_playlist: Optional[UserPlaylist] = transfer.find_playlist(spotify_playlist)

    if tidal_playlist and not overwrite:
      emit('playlist_exists')
      return None
    elif tidal_playlist and overwrite:
      tidal_playlist.delete()

    tidal_playlist: Optional[UserPlaylist] = transfer.create_playlist(spotify_playlist)

    tasks = []
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for i, track in enumerate(tracks):
      task = loop.create_task(handle_track(transfer, i, track))
      tasks.append(task)

    task_group = asyncio.gather(*tasks, return_exceptions=True)
    found_tracks = loop.run_until_complete(task_group)
    loop.close()

    if tidal_playlist:
      tidal_playlist.add([track.id for track in found_tracks if track])

    emit('finished')