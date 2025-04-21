"""This file holds the methods used to render the pages and
 also the functionality of the pages"""
import os
import math
import csv
from datetime import datetime
from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from app import db
from Classes.classes import ExerciseTable
from exercise.forms import ExerciseInputForm

# CONFIG
exercise_blueprint = Blueprint('exercise', __name__, template_folder='templates')


def get_data():
    """Gets the data from the exercise_list.csv to be used in calorie calculations"""
    # get correct dynamic path to the exercise_list.csv file
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'exercise_list.csv')
    with open(filename, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        return list(csv_reader)


@exercise_blueprint.route('/exercise')
@login_required
def exercise():
    """Method for rendering the exercise page"""
    form = ExerciseInputForm()

    return render_template('exercise.html', form=form)


# Enter a new exercise
@exercise_blueprint.route('/enter_exercise', methods=['GET', 'POST'])
@login_required
def enter_exercise():

    form = ExerciseInputForm()

    entered_exercise = ''
    cals = 0
    data = get_data()
    for line in data:
        if line[0] == form.exerciseType.data:
            cals = int(math.ceil(current_user.weight * float(line[1])
                                 * (form.exerciseDuration.data / 60)))

    if form.validate_on_submit():
        new_exercise = ExerciseTable(user_id=current_user.id,
                                     exercise_duration=form.exerciseDuration.data,
                                     exercise_type=form.exerciseType.data,
                                     exercise_calories=cals,
                                     exercise_start_time=(datetime.now()
                                                          .strftime("%Y-%m-%d %H:%M:%S.%f")))

        db.session.add(new_exercise)
        db.session.commit()
        flash('Exercise has been submitted.')

        return exercise()

    if not entered_exercise:
        flash('Exercise is blank, please enter!')

    return exercise()


# Display previous exercises
@exercise_blueprint.route('/show_previous_exercise', methods=['POST'])
@login_required
def show_previous_exercises():
    """Method to show all the users previous exercises"""
    # find all previous exercises for the day
    form = ExerciseInputForm()

    previous_exercises = ExerciseTable.query.filter_by(user_id=current_user.id).all()

    # if there are any previous exercises
    if len(previous_exercises) != 0:
        # display the exercises
        return render_template('exercise.html', previous_exercises=previous_exercises, form=form)

    flash('No exercises have been entered yet!')
    return render_template('exercise.html', form=form)


@exercise_blueprint.route('/show_todays_exercise', methods=['POST'])
@login_required
def show_todays_exercises():
    """Method to show the user all of their previous exercises for the current day"""
    form = ExerciseInputForm()
    todays_exercises = []
    alluserexercises = ExerciseTable.query.filter_by(user_id=current_user.id).all()
    for exerc in alluserexercises:
        if str(exerc.exercise_start_time) > datetime.today().strftime('%Y-%m-%d'):
            todays_exercises.append(exerc)

    if len(todays_exercises) != 0:
        # display the exercises
        return render_template('exercise.html', todays_exercises=todays_exercises, form=form)

    flash('You have no recorded exercises yet today!')
    return render_template('exercise.html', form=form)

# Show example exercises
# @exercise_blueprint.route('/show_example_exercises', methods=['GET', 'POST'])
# @login_required
# def show_example_exercises():
