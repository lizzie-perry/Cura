"""This module is responsible for containing the Flask form for the admin page."""
import os
import csv
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, SelectField, FileField
from wtforms.validators import InputRequired


class AdminForm(FlaskForm):
    """ This is the class that is used to create the form used on the admin page. """
    filename = os.path.join(os.path.dirname(
        os.path.realpath('app.py')), 'exercise/exercise_list.csv')
    with open(filename, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        data = list(csv_reader)

    exercise_list = []
    for line in data:
        exercise_list.append(line[0])

    ExerciseName = StringField(validators=[InputRequired()])
    ExerciseType = SelectField(InputRequired(), choices=exercise_list)
    ExerciseDescription = StringField(validators=[InputRequired()])
    ExerciseBurnCal = IntegerField(validators=[InputRequired()])
    ExerciseImage = FileField()
    submit = SubmitField()
