from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, emit
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from datetime import datetime

from sptf_classes import SpotifyPlaylist
from tidal_classes import TidalUser, TidalCredentials, TidalTransfer, PlaylistError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['CORS_HEADERS'] = 'Content-Type'

socketio = SocketIO(app, cors_allowed_origins="*")

user: TidalUser | None = None
handler: TidalTransfer | None = None

class PlaylistForm(FlaskForm):
  link = StringField('Playlist Link/ID', validators=[DataRequired()])
  submit = SubmitField('Submit')


@app.route("/", methods=['GET', 'POST'])
def index():
  global user
  form = PlaylistForm()

  if form.validate_on_submit():
    session['link'] = form.link.data

    playlist: str = session['link'].split('/')[-1]
    session['id'] = playlist.split('?')[0]

    if (not user) and (not session.get('access_token')):
      user = TidalUser(None)
      return render_template('index.html', form=form, link=f'https://{user.login_uri}')

    if not user:
      credentials = TidalCredentials(session['token_type'], session['access_token'], session['refresh_token'], session['expiry_time'])
      user = TidalUser(credentials)

    return redirect(url_for('transfer'))
  return render_template('index.html', form=form)

@app.route("/transfer")
def transfer():
  global user
  user.login()

  # ...waiting for the login future...
  if not session.get('access_token'):
    session['token_type'] = user.credentials.token_type
    session['access_token'] = user.credentials.access_token
    session['refresh_token'] = user.credentials.refresh_token
    session['expiry_time'] = user.credentials.expiry_time

  playlist: SpotifyPlaylist = SpotifyPlaylist.from_id(session.get('id'))

  return render_template('transfer.html', playlist_name=playlist.name, playlist_id=session.get('id'))

@app.route("/success")
def success():
  global handler
  playlist = SpotifyPlaylist.from_id(session.get('id'))

  return render_template('success.html', not_found=handler.tracks_not_found, playlist=playlist)

@app.route("/error")
def error():
  global handler
  playlist = SpotifyPlaylist.from_id(session.get('id'))
  error = request.args.get('error')

  return render_template('error.html', error=error, playlist=playlist)


@socketio.on('track', namespace='/transfer')
def get_playlist():
  global user
  global handler
  try:

    playlist = SpotifyPlaylist.from_id(session.get('id'))
    handler = TidalTransfer(user, playlist)
    handler.create_playlist()
    handler.transfer_playlist(lambda i, track: emit('track', {'data': {'index': i+1, 'name': track.name, 'artists': ", ".join([artist for artist in track.artists])}, 'total': len(playlist.tracks)}))

    emit('success', { 'url': url_for('success') })
  except PlaylistError as err:
    emit('error', { 'url': url_for('error', error=err.args[0])})

if __name__ == "__main__":
  socketio.run(app, debug=True)