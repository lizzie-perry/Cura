"""This file contains the methods for rendering the water intake page and also
the functionality behind it to record the user data to the database and to allow
the user see their progress for the day"""
from datetime import datetime
from flask_login import login_required, current_user
from flask import Blueprint, render_template, flash
from water.forms import WaterIntakeForm
from Classes.classes import WaterIntake
from app import db

waterIntake_blueprint = Blueprint('water', __name__, template_folder='templates')


@waterIntake_blueprint.route('/water')
@login_required
def water_intake():
    """Method to render the waterIntake page"""
    form = WaterIntakeForm()
    return render_template('waterIntake.html', form=form)


@waterIntake_blueprint.route('/enter_waterAmount', methods=['POST'])
@login_required
def enter_water_amount():
    """Method to get user input and create a new row in the waterTable table"""
    form = WaterIntakeForm()

    if form.validate_on_submit():
        if form.waterAmount.data > 5000:
            flash('Incorrect water amount entered! Please try again!')

        else:
            new_water_intake = WaterIntake(user_id=current_user.id,
                                           date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                           water_amount=form.waterAmount.data)

            db.session.add(new_water_intake)
            db.session.commit()

            flash('New water intake added!')

            return water_intake()

    if not enter_water_amount:
        flash('Please enter the amount of water you have consumed!')

    return water_intake()


@waterIntake_blueprint.route('/todaysGoal', methods=['POST'])
@login_required
def get_todays_goal():
    """Method to get the amount of water the user has consumed today and pass it to the
    page to be displayed"""
    form = WaterIntakeForm()

    water_goal = 0
    alluser_water_intake = WaterIntake.query.filter_by(user_id=current_user.id).all()
    if current_user.gender == "Male":
        user_goal = 3500
    else:
        user_goal = 2500

    for item in alluser_water_intake:
        if str(item.date_time) > datetime.today().strftime('%Y-%m-%d'):
            water_goal = water_goal + item.water_amount

    if user_goal > water_goal:
        tweet_button = False
    else:
        tweet_button = True

    return render_template('waterIntake.html', waterGoal=water_goal, userGoal=user_goal,
                           tweet_button=tweet_button, form=form)
