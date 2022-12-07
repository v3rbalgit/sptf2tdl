from app import db

class User(db.Model): # type: ignore
  id = db.Column(db.String, primary_key=True, unique=True)
  token_type = db.Column(db.String, unique=False, nullable=False)
  access_token = db.Column(db.String, unique=True, nullable=False)
  refresh_token = db.Column(db.String, unique=True, nullable=False)
  expiry_time = db.Column(db.DateTime, unique=True, nullable=False)

  def __repr__(self):
    return f"User ID: {self.id}"