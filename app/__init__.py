from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os

from . import config

socketio = SocketIO()
db = SQLAlchemy()

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
      db.init_app(app)
      socketio.init_app(app, cors_allowed_origins="*")

      db.create_all()

    return app