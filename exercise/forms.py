"""This module is responsible for containing the Flask forms as well as the
validation checks for the flask form and the user input for the exercise page.
"""
import csv
import os
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField
from wtforms.validators import InputRequired, ValidationError


# Checking if duration is valid
def duration_check(form, field):
    """Checks the user has entered a correct duration for the exercise"""
    if field.data < 5 or field.data > 250:
        raise ValidationError("Please enter exercise duration correctly.")


class ExerciseInputForm(FlaskForm):
    """ A subclass of Flask form to take the user login details.
        Form contains email, password input classes and submit field.
    """

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'exercise_list.csv')
    with open(filename, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        data = list(csv_reader)

    exercise_list = []
    for line in data:
        exercise_list.append(line[0])

    exerciseType = SelectField(InputRequired(), choices=exercise_list)
    exerciseDuration = IntegerField(validators=[InputRequired(), duration_check])
    submit = SubmitField()
