"""This file holds the class for the search for food functionality"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, SearchField
from wtforms.validators import InputRequired


class FoodIntakeForm(FlaskForm):
    """This class represents the form used by the user to search for food items"""
    foodType = SearchField(validators=[InputRequired()])
    submit = SubmitField()
