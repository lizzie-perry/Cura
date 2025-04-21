"""This holds the form for the sleep page to allow the user to record their sleep"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateTimeLocalField
from wtforms.validators import InputRequired

class SleepIntakeForm(FlaskForm):
    """This class is representative of the sleep form which allows the user to record sleep.
    It has three fields: sleepStartTime - DateTime field, sleepEndTime - DateTime field
    submit - submit button"""
    sleepStartTime = DateTimeLocalField(format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    sleepEndTime = DateTimeLocalField(format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    submit = SubmitField()
