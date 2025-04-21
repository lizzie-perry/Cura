"""This module is used to render the sleep pages and holds the functionality to allow
the user to record their sleep patterns and view previous nights sleep"""
from datetime import datetime
from flask_login import login_required, current_user
from flask import Blueprint, render_template, flash
from Classes.classes import SleepTable
from app import db
from sleep.forms import SleepIntakeForm

sleepIntake_blueprint = Blueprint('sleep', __name__, template_folder='templates')


@sleepIntake_blueprint.route('/sleep')
@login_required
def record_sleep():
    """This method is used to render the sleep.html page"""
    form = SleepIntakeForm()

    return render_template('sleep.html', form=form)


@sleepIntake_blueprint.route('/enter_sleep', methods=['POST', 'GET'])
@login_required
def enter_sleep():
    """This method is used to take the information the user has
     entered and record it in the database"""
    form = SleepIntakeForm()

    if form.validate_on_submit():
        sleep_start_time = datetime.strptime(str(form.sleepStartTime.raw_data[0]).replace('T', ' '),
                                             '%Y-%m-%d %H:%M')
        sleep_end_time = datetime.strptime(str(form.sleepEndTime.raw_data[0]).replace('T', ' '),
                                           '%Y-%m-%d %H:%M')
        new_sleep_record = SleepTable(user_id=current_user.id,
                                      sleep_start=sleep_start_time,
                                      sleep_end=sleep_end_time)

        db.session.add(new_sleep_record)
        db.session.commit()

        flash('Sleep times recorded!')

        return render_template('sleep.html', form=form)

    return render_template('sleep.html', form=form)


@sleepIntake_blueprint.route('/show_previous_sleep', methods=['POST'])
@login_required
def show_previous_sleep():
    """This method is used to show the user their previous sleep patterns"""
    # find all previous exercises for the day
    form = SleepIntakeForm()

    previous_sleep = SleepTable.query.filter_by(user_id=current_user.id).all()

    # if there are any previous exercises
    if len(previous_sleep) != 0:
        # display the exercises
        return render_template('sleep.html', previous_sleep=previous_sleep, form=form)

    flash('No exercises have been entered yet!')
    return render_template('sleep.html', form=form)
