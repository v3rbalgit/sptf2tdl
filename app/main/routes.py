from flask import session, redirect, url_for, render_template

from . import main
from .forms import PlaylistForm
from app import db
from ..models import User
from ..utils import check_url
from .classes import TidalLogin, SpotifyClient

from dotenv import load_dotenv
load_dotenv()
from os import getenv

from uuid import uuid4

client = SpotifyClient(getenv('client_id', ''), getenv('client_secret', ''))
tidal_users = {}

@main.route("/", methods=['GET', 'POST'])
def index():
  form = PlaylistForm()

  if form.validate_on_submit():
    session['splid'] = check_url(form.link.data)

    if not session.get('id'):
      login = TidalLogin()
      id = uuid4().hex
      session['id'] = id
      tidal_users[id] = login

      return render_template('index.html', form=form, link=f'https://{login.login_uri}')

    return redirect(url_for('main.transfer'))

  return render_template('index.html', form=form)

@main.route("/transfer")
def transfer():
  id = session.get('id')
  user = db.session.execute(db.select(User).filter_by(id=id)).first()

  if not user:
    login: TidalLogin = tidal_users[id]
    login.login()
    user = User(
      id=session['id'],
      token_type=login.credentials.token_type,      #type: ignore
      access_token=login.credentials.access_token,  #type: ignore
      refresh_token=login.credentials.refresh_token,#type: ignore
      expiry_time=login.credentials.expiry_time     #type: ignore
      )

    db.session.add(user)
    db.session.commit()

    del tidal_users[id]

    return redirect(url_for('main.transfer'))

  playlist = client.get_playlist(session['splid'])

  return render_template('transfer.html', playlist_name=playlist.name)