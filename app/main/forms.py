from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class PlaylistForm(FlaskForm):
  playlist = StringField('Enter playlist link or id', validators=[DataRequired()])
  submit = SubmitField('Submit')