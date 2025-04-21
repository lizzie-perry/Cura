"""This file is used to hold the class that represents the form used to allow
the user to record their water intake"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import InputRequired


class WaterIntakeForm(FlaskForm):
    """This class represents the form that is used by the user to record water intake
    waterAmount - Integer field
    submit - Submit button"""
    waterAmount = IntegerField(validators=[InputRequired()])
    submit = SubmitField()
