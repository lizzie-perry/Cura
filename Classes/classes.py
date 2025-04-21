"""This is the main python file that holds the classes that correspond
to tables in the database - they are used to create objects which each
correspond to a row in a table"""
import base64
from flask_login import UserMixin, current_user
from sqlalchemy import Integer, String, DateTime
from werkzeug.security import generate_password_hash
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet
from app import db


def encrypt(data, data_key):
    """Used to encrypt sensitive data:
    :param data - The data to be encrypted
    :param data_key - The key to encrypt the data with"""
    return Fernet(data_key).encrypt(bytes(data, 'utf-8'))


# User model
class User(db.Model, UserMixin):
    """ This class is a subclass of db.Model and UserMixin and is used an
        instance of a User object with attributes the same as the ones in
        the database. Developed by Andrew W, Matous E and Justina M"""
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    firstname = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')
    weight = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    activity_level = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(25), nullable=False)
    bmi = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    # crypto key for user's data
    data_key = db.Column(db.BLOB)

    def __init__(self, id, email, bmi, firstname, surname, password, role,
                 weight, height, activity_level, gender, age, calories, dob):
        """ This method initializes the user object

        :param id: user id
        :param email: user email address
        :param bmi: bmi based on users weight and height
        :param firstname: users firstname
        :param surname: users surname
        :param password: users encrypted password
        :param role: users role on the website
        :param weight: users weight
        :param height: users height
        :param activity_level: users activity level
        :param gender: users sex
        :param age: users age
        """
        self.id = id
        self.email = email
        # crypto key for user's data
        self.data_key = base64.urlsafe_b64encode(scrypt(password,
                                                        str(get_random_bytes(32)),
                                                        32, N=2 ** 14, r=8, p=1))
        self.firstname = encrypt(firstname, self.data_key)
        self.surname = encrypt(surname, self.data_key)
        self.password = generate_password_hash(password)
        self.role = role
        self.weight = weight
        self.height = height
        self.activity_level = activity_level
        self.gender = gender
        self.bmi = bmi
        self.age = age
        self.calories = calories
        self.dob = dob

    def calculate_updated_cals_and_bmi(self, weight, height, gender, activity_level):
        """Used to recalculate calorie target and bmi when user weight, height,
         gender or activity level change"""
        bmi = (weight / current_user.height / 100) ** 2
        calories = 0

        if gender == 'Male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - \
                  (5.677 * current_user.age)
            if activity_level == 'High':
                calories = bmr * 1.9
            elif activity_level == 'Medium':
                calories = bmr * 1.550
            elif activity_level == 'Low':
                calories = bmr * 1.2
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - \
                  (4.330 * current_user.age)
            if activity_level == 'High':
                calories = bmr * 1.9
            elif activity_level == 'Medium':
                calories = bmr * 1.550
            elif activity_level == 'Low':
                calories = bmr * 1.2
        return calories, bmi

    def update_personal_details(self, firstname, surname, gender):
        """Used to update user personal details in the database if they change"""
        self.firstname = encrypt(firstname, self.data_key)
        self.surname = encrypt(surname, self.data_key)
        self.gender = gender
        self.calories = self.calculate_updated_cals_and_bmi(current_user.weight,
                                                            current_user.height,
                                                            gender,
                                                            current_user.activity_level)[0]

    def update_measurements(self, weight, height):
        """Used to update user weight and height if they change"""
        self.weight = weight
        self.height = height
        self.bmi = self.calculate_updated_cals_and_bmi(weight,
                                                       height,
                                                       current_user.gender,
                                                       current_user.activity_level)[1]
        self.calories = self.calculate_updated_cals_and_bmi(weight,
                                                            height,
                                                            current_user.gender,
                                                            current_user.activity_level)[0]


# Water intake model
class WaterIntake(db.Model, UserMixin):
    """ This class is a subclass of db.Model and UserMaxin and is used an
        instance of a WaterIntake object with attributes the same as the ones in
        the database. Developed by Andrew W"""
    __tablename__ = 'waterTable'

    waterID = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    water_amount = db.Column(Integer, nullable=False)

    def __init__(self, user_id, date_time, water_amount):
        """ This method is an initializer for the WaterIntake class.

        :param user_id: unique userID
        :param date_time: date of the water intake
        :param water_amount: quantity of water intake
        """
        self.user_id = user_id
        self.date_time = date_time
        self.water_amount = water_amount


class FoodIntake(db.Model, UserMixin):
    """ This class is a subclass of db.Model and UserMaxin and is used an
        instance of a FoodIntake object with attributes the same as the ones in
        the database. Developed by Andrew W"""
    __tablename__ = 'foodTable'

    foodID = db.Column(Integer, primary_key=True)

    user_id = db.Column(Integer, nullable=False)
    date_time = db.Column(DateTime, nullable=False)
    food_type = db.Column(String(100), nullable=False)
    calorie_count = db.Column(Integer, nullable=False)

    def __init__(self, user_id, date_time, food_type, calorie_count):
        """ Initializer for the FoodIntake class

        :param foodUserID: user ID foreign key
        :param date_time: date of food intake
        :param food_type: food intake type
        :param calorie_count: food calories
        """
        self.user_id = user_id
        self.date_time = date_time
        self.food_type = food_type
        self.calorie_count = calorie_count


class ExerciseTable(db.Model, UserMixin):
    """This class is a subclass of db.Model and UserMaxin and is used an
        instance of a Exercise object with attributes the same as the ones in
        the database. Developed by Andrew W"""
    __tablename__ = 'UserExercise'

    ExerciseID = db.Column(Integer, primary_key=True)

    user_id = db.Column(Integer, nullable=False)
    exercise_type = db.Column(String(100), nullable=False)
    exercise_start_time = db.Column(DateTime, nullable=False)
    exercise_duration = db.Column(Integer, nullable=False)
    exercise_calories = db.Column(Integer, nullable=False)

    def __init__(self, user_id, exercise_type, exercise_start_time,
                 exercise_duration, exercise_calories):
        """ This method initializes the Exercise object

        :param exerciseUserID: user id
        :param exerciseStart: exercise date
        :param exerciseDuration: duration of the exercise
        :param exerciseType: type of exercise
        """
        self.user_id = user_id
        self.exercise_type = exercise_type
        self.exercise_start_time = exercise_start_time
        self.exercise_duration = exercise_duration
        self.exercise_calories = exercise_calories


class ExampleExercise(db.Model, UserMixin):
    """ This class is a subclass of db.Model and UserMixin and is used an
            instance of a exampleExercise object with attributes the same as the ones in
            the database. Developed by Andrew W"""
    __tablename__ = 'exampleExercises'

    EID = db.Column(Integer, primary_key=True)

    exercise_name = db.Column(String(100), nullable=False)
    exercise_type = db.Column(String(100), nullable=False)
    exercise_description = db.Column(db.TEXT, nullable=False)
    exercise_burn_cal = db.Column(Integer, nullable=False)
    exercise_image = db.Column(db.TEXT, nullable=False)

    def __init__(self, exercise_name, exercise_type, exercise_description,
                 exercise_burn_cal, exercise_image):
        """ This method initializes the Exercise object

                :param exercise_name: Name of the exercise
                :param exercise_type: Type of exercise(E.G. Running)
                :param exercise_description: Description of the exercise
                :param exercise_burn_cal: Amount of calories burned during this exercise
                :param exercise_image: Image name to go along with the exercise on the application
                """
        self.exercise_name = exercise_name
        self.exercise_type = exercise_type
        self.exercise_description = exercise_description
        self.exercise_burn_cal = exercise_burn_cal
        self.exercise_image = exercise_image


class SleepTable(db.Model, UserMixin):
    """ This class is a subclass of db.Model and UserMixin and is used an
            instance of a sleep table object with attributes the same as the ones in
            the database. Developed by Andrew W"""
    __tablename__ = 'sleepTable'

    SID = db.Column(Integer, primary_key=True)

    user_id = db.Column(Integer, nullable=False)
    sleep_start = db.Column(DateTime, nullable=False)
    sleep_end = db.Column(DateTime, nullable=False)

    def __init__(self, user_id, sleep_start, sleep_end):
        """This method initialises a SleepTable object
        :param user_id - the users id
        :param sleep_start - time the user fell asleep
        :param sleep_end - time the user awoke"""
        self.user_id = user_id
        self.sleep_start = sleep_start
        self.sleep_end = sleep_end
