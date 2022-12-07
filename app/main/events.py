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

@socketio.on('track', namespace='/transfer')
def get_playlist():
  id = session.get('id')
  user: List[User] = db.session.execute(db.select(User).filter_by(id=id)).one()

  login = TidalLogin()
  login.credentials = TidalCredentials(user[0].token_type, user[0].access_token, user[0].refresh_token, user[0].expiry_time)
  login.login()

  spotify_playlist: SpotifyPlaylist = client.get_playlist(session['plid'])
  tracks: List[SpotifyTrack] = spotify_playlist.tracks
  track_index: int = session['cur'] if session.get('cur') else 0

  transfer = TidalTransfer(login)
  tidal_playlist: UserPlaylist = transfer.create_playlist(spotify_playlist)
  tidal_track: Optional[Track] = transfer.find_track(tracks[track_index])

  if tidal_track:
    tidal_playlist.add([tidal_track.id])

  session['cur'] += 1

  emit('track', {
    'data': {
      'index': track_index,
      'found': True if tidal_track else False,
      'name': tracks[track_index].name,
      'artists': ", ".join([artist for artist in tracks[track_index].artists]),
      'playlist': spotify_playlist.name,
      'total': len(tracks)
      }
    })