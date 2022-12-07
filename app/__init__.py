from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os

socketio = SocketIO()
db = SQLAlchemy()

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    return app