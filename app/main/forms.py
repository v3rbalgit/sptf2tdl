from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired


class PlaylistForm(FlaskForm):
  """Makes a form to enter playlist link"""
  link = StringField('Link to playlist:', validators=[DataRequired()])
  submit = SubmitField('Submit')
