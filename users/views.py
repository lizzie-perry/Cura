""" This module is a container for the Flask web application views for
    the user blueprint.
"""
import logging
from datetime import date, datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from cryptography.fernet import Fernet
from app import db
from Classes.classes import User, ExerciseTable, FoodIntake, WaterIntake, SleepTable
from users.forms import RegisterForm, LoginForm, SettingsFormPersonalData


users_blueprint = Blueprint('users', __name__, template_folder='templates')


def get_dashboard_data():
    """This method is used to retrieve the user data so that it can be
    displayed in a more intuitive format using graphs"""
    exersice = ExerciseTable.query.filter_by(user_id=current_user.id, ).all()
    food = FoodIntake.query.filter_by(user_id=current_user.id).all()
    water = WaterIntake.query.filter_by(user_id=current_user.id).all()
    sleep = SleepTable.query.filter_by(user_id=current_user.id).all()

    exercise_list = []
    food_list = []
    water_list = []
    sleep_list = []

    for element in exersice:
        if (datetime.today().day - element.exercise_start_time.day) < 7:
            exercise_list.append(element)

    for element in food:
        if (datetime.today().day - element.date_time.day) < 7:
            food_list.append(element)

    for element in water:
        if (datetime.today().day - element.date_time.day) < 7:
            water_list.append(element)

    for element in sleep:
        if (datetime.today().day - element.sleep_start.day) < 7:
            sleep_list.append(element)

    labels = [*range(date.today().day - 6, date.today().day + 1)]

    activity_data = [0] * 7

    exercise_list.sort(key=lambda r: r.exercise_start_time.day)
    exercise_data = [0] * 7

    for i in range(len(exercise_data)):
        for exercise in exercise_list:
            if exercise.exercise_start_time.day == labels[i]:
                exercise_data[i] += exercise.exercise_calories
                activity_data[i] = 1

    food_list.sort(key=lambda r: r.date_time.day)
    food_data = [0] * 7

    for i in range(len(food_data)):
        for food in food_list:
            if food.date_time.day == labels[i]:
                food_data[i] += food.calorie_count
                activity_data[i] = 1

    water_list.sort(key=lambda r: r.date_time.day)
    water_data = [0] * 7

    for i in range(len(water_data)):
        for water in water_list:
            if water.date_time.day == labels[i]:
                water_data[i] += water.water_amount
                activity_data[i] = 1

    sleep_list.sort(key=lambda r: r.sleep_start.day)
    sleep_data = [0] * 7

    for i in range(len(sleep_data)):
        for sleep in sleep_list:
            if sleep.sleep_start.day == labels[i]:
                sleep_data[i] += (sleep.sleep_end - sleep.sleep_start).total_seconds() // 3600
                # print(type((sleep.sleepEnd - sleep.sleepStart).total_seconds()))
                activity_data[i] = 1

    return [exercise_data, food_data, water_data, activity_data, labels, sleep_data]


def calculate_age(born):
    """This method is used to calculate the users age from their date of birth
    :param born - date of birth"""
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def decrypt(data, datakey):
    """ This function takes some data and a data key and uses the data key to
        decrypt the data and then returns it/

    :param: data: the piece of data to be decrypted
    :param: datakey: the key used to decrypt the data
    :return: the decrypted data
    """
    return Fernet(datakey).decrypt(data).decode("utf-8")


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """ This method is the  flask view for the login page of the web application.
        It gets the user input and then checks to see if it is a valid login.
        If the login details are valid then the user will be logged in else the user
        redirected back to the login page.

    :return: rendered template of the html page
    """
    form = LoginForm()

    # if session attribute logins does not exist create attribute logins
    if not session.get('logins'):
        session['logins'] = 0
    # if login attempts is 3 or more create an error message
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    if form.validate_on_submit():
        # increase login attempts by 1
        session['logins'] += 1
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')
            return render_template('login.html', form=form)

        # if user is verified reset login attempts to 0
        session['logins'] = 0
        login_user(user)
        logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id,
                        current_user.email, request.remote_addr)

        dashboard_data = get_dashboard_data()

        labels = dashboard_data[4]
        exercise_data = dashboard_data[0]
        food_data = dashboard_data[1]
        water_data = dashboard_data[2]
        activity_data = dashboard_data[3]
        sleep_data = dashboard_data[5]

        return render_template('dashboard.html',
                               firstname=decrypt(current_user.firstname, current_user.data_key),
                               labels=labels,
                               exercise_data=exercise_data,
                               food_data=food_data,
                               water_data=water_data,
                               activity_data=activity_data,
                               sleep_data=sleep_data)

    return render_template('login.html', form=form)


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """ This method is the flask view fot the register page of the web application.
        It gets the register details and if the user doesn't already exist then it
        will save the users' information in the database.

    :return: rendered template of the html page
    """
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            last_id = (User.query.order_by(User.id)[-1]).id
        except IndexError:
            last_id = 0

        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        bmi = form.weight.data / (form.height.data / 100) ** 2
        calories = 0

        if form.gender.data == 'Male':
            bmr = 88.362 + (13.397 * form.weight.data) + (4.799 * form.height.data) - \
                  (5.677 * calculate_age(form.date.data))
            if form.activity_level.data == 'High':
                calories = bmr * 1.9
            elif form.activity_level.data == 'Medium':
                calories = bmr * 1.550
            elif form.activity_level.data == 'Low':
                calories = bmr * 1.2
        else:
            bmr = 447.593 + (9.247 * form.weight.data) + (3.098 * form.height.data) - \
                  (4.330 * calculate_age(form.date.data))
            if form.activity_level.data == 'High':
                calories = bmr * 1.9
            elif form.activity_level.data == 'Medium':
                calories = bmr * 1.550
            elif form.activity_level.data == 'Low':
                calories = bmr * 1.2

        new_user = User(id=last_id + 1,
                        email=form.email.data,
                        firstname=form.firstname.data,
                        bmi=round(bmi),
                        surname=form.surname.data,
                        password=form.password.data,
                        role='user',
                        weight=form.weight.data,
                        height=form.height.data,
                        activity_level=form.activity_level.data,
                        gender=form.gender.data,
                        age=calculate_age(form.date.data),
                        calories=calories,
                        dob=form.date.data
                        )
        db.session.add(new_user)
        db.session.commit()

        logging.warning('SECURITY - User registration [%s, %s]',
                        form.email.data,
                        request.remote_addr)

        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)


@users_blueprint.route('/dashboard')
@login_required
def dashboard():
    """ This method is the flask view for the dashboard page.

    :return: rendered template of the html page
    """
    dashboard_data = get_dashboard_data()

    labels = dashboard_data[4]
    exercise_data = dashboard_data[0]
    food_data = dashboard_data[1]
    water_data = dashboard_data[2]
    activity_data = dashboard_data[3]
    sleep_data = dashboard_data[5]

    return render_template('dashboard.html',
                           firstname=decrypt(current_user.firstname, current_user.data_key),
                           labels=labels,
                           exercise_data=exercise_data,
                           food_data=food_data,
                           water_data=water_data,
                           activity_data=activity_data,
                           sleep_data=sleep_data)


# @users_blueprint.route('/exercise')
# @login_required
# def exercise():
#     """ This method is the flask view for the exercise page.
#
#     :return: rendered template of the html page
#     """
#     return render_template('exercise.html')


@users_blueprint.route('/profile')
@login_required
def profile():
    """ This method is the flask view for the profile page.

    :return: rendered template of the html page
    """
    return render_template('profile.html',
                           email=current_user.email,
                           firstname=decrypt(current_user.firstname, current_user.data_key),
                           lastname=decrypt(current_user.surname, current_user.data_key),
                           weight=current_user.weight,
                           height=current_user.height,
                           activity=current_user.activity_level,
                           gender=current_user.gender)


@users_blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """ This method is the flask view for the settings page

    :return: rendered template of the html page
    """
    form = SettingsFormPersonalData()
    if form.validate_on_submit():
        User.query.filter_by(email=current_user.email) \
            .first().update_personal_details(form.firstname.data,
                                             form.surname.data,
                                             form.gender.data)
        db.session.commit()
        flash('Your personal details have been updated successfully.', 'info')
        return render_template('settings.html', user_firstname=form.firstname.data,
                               user_lastname=form.surname.data,
                               user_gender=form.gender.data,
                               form=form)
    return render_template('settings.html', user_firstname=decrypt(current_user.firstname,
                                                                   current_user.data_key),
                           user_lastname=decrypt(current_user.surname,
                                                 current_user.data_key),
                           user_gender=current_user.gender, form=form)


@users_blueprint.route('/logout')
@login_required
def logout():
    """ This method is the flask view for the logout page
        This method will automatically logout the current user who is logged in.

    :return: rendered template of the html page
    """
    logging.warning('SECURITY - Log out [%s, %s, %s]',
                    current_user.id,
                    current_user.email,
                    request.remote_addr)
    logout_user()
    return render_template('index.html')


@users_blueprint.route('/trainer')
@login_required
def trainer():
    """Method for rendering the trainer web page"""
    return render_template('trainer.html', firstname=decrypt(current_user.firstname,
                                                             current_user.data_key))
