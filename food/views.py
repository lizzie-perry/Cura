"""This file holds the code to render the food search page as well as the food list page.
It also hold the code for the functionality of those pages"""
from datetime import datetime
import openfoodfacts
from flask_login import login_required, current_user
from flask import Blueprint, render_template, flash
from food.forms import FoodIntakeForm
from Classes.classes import FoodIntake
from app import db

foodIntake_blueprint = Blueprint('food', __name__, template_folder='templates')


@foodIntake_blueprint.route('/food')
@login_required
def food_intake():
    """Method for rendering the foodIntake web page"""
    form = FoodIntakeForm()

    return render_template('foodIntake.html', form=form)


@foodIntake_blueprint.route('/enter_food', methods=['POST'])
@login_required
def enter_food():
    """Method for the functionality of the foodIntake webpage to
     allow the user to search for food items"""
    form = FoodIntakeForm()

    if form.validate_on_submit():
        search_result = openfoodfacts.products.advanced_search({
            "search_terms":form.foodType.data,
            "page_size":"250"})

        if search_result['count'] < 1:
            flash('No food type for ' + form.foodType.data + ' found! Please try again!')
            return food_intake()

        product_list = search_result['products']

        return render_template('foodList.html', foodType=form.foodType.data,
                               foodList=product_list, form=form)

    if not enter_food:
        flash('Please ensure all fields are filled in and please try again!')

    return food_intake()


@foodIntake_blueprint.route('/<p_name>/<float:calories>/record_meal', methods=['POST', 'GET'])
@login_required
def record_meal(p_name, calories):
    """Method to allow the user to record a food item from the foodList webpage"""
    new_recorded_meal = FoodIntake(user_id=current_user.id,
                                 date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                 food_type=p_name,
                                 calorie_count=calories)

    db.session.add(new_recorded_meal)
    db.session.commit()

    flash('Meal recorded!')

    return food_intake()


@foodIntake_blueprint.route('/todaysCalorieGoal', methods=['POST'])
@login_required
def get_todays_calorie_goal():
    """Method to return and show the user how many calories they have consumed today
    against their personal goal"""
    form = FoodIntakeForm()

    calorie_goal = 0
    user_calories = FoodIntake.query.filter_by(user_id=current_user.id).all()

    for item in user_calories:
        if str(item.date_time) > datetime.today().strftime('%Y-%m-%d'):
            calorie_goal = calorie_goal + item.calorie_count

    return render_template('foodIntake.html', calorieGoal=calorie_goal,
                           userCalorieGoal=current_user.calories, form=form)


@foodIntake_blueprint.route('/show_todays_meals', methods=['POST'])
@login_required
def get_todays_meals():
    """Method to remind the user of the food they have eaten today"""
    form = FoodIntakeForm()

    todays_meals = []
    user_meals = FoodIntake.query.filter_by(user_id=current_user.id).all()

    for meal in user_meals:
        if str(meal.date_time) > datetime.today().strftime('%Y-%m-%d'):
            todays_meals.append(meal)

    if len(todays_meals) != 0:
        # display the meals
        return render_template('foodIntake.html', todays_meals=todays_meals, form=form)

    flash('You have not recorded a meal for today!')
    return render_template('foodIntake.html', form=form)
