#!/bin/env python
from app import create_app, db
from app.models import User
from flask_migrate import Migrate
from app import create_app, socketio

app = create_app(debug=False)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
  return dict(db=db, User=User)

if __name__ == '__main__':
  socketio.run(app)