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
def get_playlist(message):
  session['cur'] = message['index']

  id = session.get('id')
  user: List[User] = db.session.execute(db.select(User).filter_by(id=id)).first()

  login = TidalLogin()
  login.credentials = TidalCredentials(user[0].token_type, user[0].access_token, user[0].refresh_token, user[0].expiry_time)
  login.login()

  spotify_playlist: SpotifyPlaylist = client.get_playlist(session['splid'])
  tracks: List[SpotifyTrack] = spotify_playlist.tracks

  transfer = TidalTransfer(login)

  if session['cur'] == 0:
    tidal_playlist: UserPlaylist = transfer.create_playlist(spotify_playlist)
    session['tlid'] = tidal_playlist.id
  else:
    tidal_playlist: UserPlaylist = transfer.find_playlist(session['tlid'])

  tidal_track: Optional[Track] = transfer.find_track(tracks[session['cur']])

  if tidal_track:
    tidal_playlist.add([tidal_track.id])

  emit('track', {
    'data': {
      'index': session['cur'],
      'found': True if tidal_track else False,
      'name': tracks[session['cur']].name,
      'artists': ", ".join([artist for artist in tracks[session['cur']].artists]),
      'playlist': spotify_playlist.name,
      'total': len(tracks)
      }
    })