from flask import session
from flask_socketio import emit
from typing import List, Optional

from .. import socketio
from dotenv import load_dotenv
load_dotenv()
from os import getenv

from .classes import TidalLogin, TidalCredentials, TidalTransfer, SpotifyClient, SpotifyPlaylist, SpotifyTrack

from tidalapi import UserPlaylist, Track

from app import db
from ..models import User

client = SpotifyClient(getenv('client_id', ''), getenv('client_secret', ''))

@socketio.on('start_transfer', namespace='/transfer')
def get_playlist(overwrite):
  id = session.get('id')
  user: List[User] = db.session.execute(db.select(User).filter_by(id=id)).first()

  login = TidalLogin()
  login.credentials = TidalCredentials(user[0].token_type, user[0].access_token, user[0].refresh_token, user[0].expiry_time)
  login.login()

  spotify_playlist: SpotifyPlaylist = client.get_playlist(session['splid'])
  tracks: List[SpotifyTrack] = spotify_playlist.tracks

  transfer = TidalTransfer(login)

  tidal_playlist: Optional[UserPlaylist] = transfer.find_playlist(spotify_playlist.name)

  if tidal_playlist and not overwrite:
    emit('overwrite_playlist', spotify_playlist.name)
    return None
  elif tidal_playlist and overwrite:
    tidal_playlist.delete()

  tidal_playlist: Optional[UserPlaylist] = transfer.create_playlist(spotify_playlist)

  for i, track in enumerate(tracks):
    data = {
      'data': {
        'index': i,
        'name': track.name,
        'artists': ", ".join([artist for artist in track.artists]),
        'playlist': spotify_playlist.name,
        'total': len(tracks)
        }
    }
    emit('next_track', data)

    tidal_track: Optional[Track] = transfer.find_track(track)

    if tidal_track:
      tidal_playlist.add([tidal_track.id])
    else:
      emit('not_found', data)

  emit('finished')