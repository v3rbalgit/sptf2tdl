from flask import session, redirect, url_for, render_template, request

from . import main
from app import db
from ..models import User
from ..utils import check_url
from .classes import TidalLogin, SpotifyClient, LoginError

from dotenv import load_dotenv
load_dotenv()
from os import getenv

from uuid import uuid4

INVALID_URL = "You entered an invalid Spotify link. Check the URL and try again."
LOGIN_ERR = "There was a problem with your TIDAL login. Please try logging in again."
UNKNOWN_ERR = "Unknown error has occured. Please try again later."

client = SpotifyClient(getenv('client_id', ''), getenv('client_secret', ''))
tidal_users = {}

@main.route("/", methods=['GET', 'POST'])
def index():
  try:
    if request.form.get('link'):
      session['splid'] = check_url(request.form['link'])

      if not session.get('id'):
        id = uuid4().hex
        session['id'] = id
        tidal_users[id] = TidalLogin()

        return render_template('index.html', link=f'https://{tidal_users[id].login_uri}')

      return redirect(url_for('main.transfer'))

    return render_template('index.html')
  except TypeError as e:
    return render_template('error.html', msg=e.args[0], submsg=INVALID_URL)
  except LoginError as e:
    return render_template('error.html', msg=e.args[0], submsg=LOGIN_ERR)
  except BaseException as e:
    return render_template('error.html', msg=e.args[0], submsg=UNKNOWN_ERR)


@main.route("/transfer")
def transfer():
  id = session.get('id')
  user = db.session.execute(db.select(User).filter_by(id=id)).first()

  try:
    if not user:
      login: TidalLogin = tidal_users[id]
      login.login()
      user = User(
        id=session['id'],
        token_type=login.credentials.token_type,        #type: ignore
        access_token=login.credentials.access_token,    #type: ignore
        refresh_token=login.credentials.refresh_token,  #type: ignore
        expiry_time=login.credentials.expiry_time       #type: ignore
        )

      db.session.add(user)
      db.session.commit()

      del tidal_users[id]

      return redirect(url_for('main.transfer'))

    playlist = client.get_playlist(session['splid'])

    return render_template('transfer.html', playlist_name=playlist.name) if playlist else render_template('error.html', msg='Invalid Spotify URL', submsg=INVALID_URL)
  except LoginError as e:
    return render_template('error.html', msg=e.args[0], submsg=LOGIN_ERR)
  except BaseException as e:
    return render_template('error.html', msg=e.args[0], submsg=UNKNOWN_ERR)
