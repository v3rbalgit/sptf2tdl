from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class PlaylistForm(FlaskForm):
  playlist = StringField('Enter playlist link or id', validators=[DataRequired()])
  submit = SubmitField('Submit')

from datetime import datetime

from sptf_classes import SpotifyPlaylist
from tidal_classes import TidalUser, TidalCredentials, TidalTransfer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

@app.route("/", methods=['GET', 'POST'])
def index():
  form = PlaylistForm()
  if form.validate_on_submit():
    session['playlist'] = form.playlist.data
    return redirect(url_for('index'))
  return render_template('index.html', playlist=session.get('playlist'), form=form)



bootstrap = Bootstrap(app)

if __name__ == "__main__":
  app.run(host="localhost", port=8000, debug=True)
  # playlist = SpotifyPlaylist.from_id('7lITlpVyxTA4eHzOGq5Ocq')
  # pprint.pprint(f'{playlist.name=}')
  # pprint.pprint(f'{playlist.description=}')
  # pprint.pprint(f'{playlist.owner=}')
  # pprint.pprint(playlist.tracks)

  credentials = TidalCredentials('Bearer',
  'eyJraWQiOiJ2OU1GbFhqWSIsImFsZyI6IkVTMjU2In0.eyJ0eXBlIjoibzJfYWNjZXNzIiwidWlkIjoxODc4MDYzODYsInNjb3BlIjoid19zdWIgcl91c3Igd191c3IiLCJnVmVyIjowLCJzVmVyIjowLCJjaWQiOjMyMzUsImV4cCI6MTY3MDU4NDcwMywic2lkIjoiZGRmNGYxNjQtMDAyOS00NjhjLThiYmEtOTk2MWE1NTI4MWVlIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLnRpZGFsLmNvbS92MSJ9.vs0T_1J5vxJPyeRyJ3r2XcRmtAU1Rpje0S9ny5BwWr9ElRhoq6fVs3TsGPu0iPvl3cL6Is72bGsMAbAIuzK-Hw',
  'eyJraWQiOiJoUzFKYTdVMCIsImFsZyI6IkVTNTEyIn0.eyJ0eXBlIjoibzJfcmVmcmVzaCIsInVpZCI6MTg3ODA2Mzg2LCJzY29wZSI6Indfc3ViIHJfdXNyIHdfdXNyIiwiY2lkIjozMjM1LCJzVmVyIjowLCJnVmVyIjowLCJpc3MiOiJodHRwczovL2F1dGgudGlkYWwuY29tL3YxIn0.AVfmi3pyDgeiRnqeigJAwm7VHI2Q6PmWSh-_jRMbpmuVwIHUguZheUh-egYwPNwOjFmICiJi5jaFsY-FhgEQ585dASTg3lue51O8dW_xxAP7DCN_XOIqPjNSYFscA0YThi9lHxqeWEuGcY3HNGg3R89rrRyTiepIJwF1bfTeAOiR4rJw',
  datetime(2022, 12, 9, 12, 18, 23, 221508)
  )

  tidal_user = TidalUser(credentials)
  print(tidal_user.login_uri)
  print(tidal_user.login())