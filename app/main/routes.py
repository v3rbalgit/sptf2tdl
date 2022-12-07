from flask import session, redirect, url_for, render_template

from . import main
from .forms import PlaylistForm
from utils import check_url
from app import db
from ..models import User
from .classes import TidalLogin, SpotifyClient

from dotenv import load_dotenv
load_dotenv()
from os import getenv

import shelve
from uuid import uuid4

client = SpotifyClient(getenv('client_id', ''), getenv('client_secret', ''))

@main.route("/", methods=['GET', 'POST'])
def index():
  if session.get('cur'):
    del session['cur']

  form = PlaylistForm()

  if form.validate_on_submit():
    session['plid'] = check_url(form.link.data)

    if not session.get('id'):
      login = TidalLogin()
      id = uuid4().hex
      session['id'] = id

      with shelve.open('tidal') as sh:
        sh[id] = login

      return render_template('index.html', form=form, link=f'https://{login.login_uri}')

    return redirect(url_for('transfer'))

  return render_template('index.html', form=form)

@main.route("/transfer")
def transfer():
  id = session.get('id')
  user = db.session.execute(db.select(User).filter_by(id=id)).one()

  if not user:
    with shelve.open('tidal') as sh:
      login: TidalLogin = sh.pop(session['id'])
      login.login()
      user = User(
        id=session['id'],
        token_type=login.credentials.token_type,
        access_token=login.credentials.access_token,
        refresh_token=login.credentials.refresh_token,
        expiry_time=login.credentials.expiry_time
        )
      db.session.add(user)
      db.session.commit()
    return redirect(url_for('transfer'))

  playlist = client.get_playlist(session['plid'])

  return render_template('transfer.html', playlist_name=playlist.name)