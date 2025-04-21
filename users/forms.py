"""This module is responsible for containing the Flask forms as well as the
validation checks for the flask form and the user input.p
"""
import re
import datetime
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, IntegerField, SelectField, PasswordField, DateField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo


def weight_check(form, field):
    """ This function checks the weight user input to see if it meets the
        correct specifications

        The weight must be between 10 and 900 kg

        :param form: the user input form from the front end
        :param field: the weight input
        :return: raise validation error if weight does not meet the specification
    """
    if field.data < 10 or field.data > 900:
        raise ValidationError("Please enter your weight correctly.")


def height_check(form, field):
    """ This function checks the height user input to see if it meets the
        correct specifications

        The height must be between 90 and 300 cm

        :param form: the user input form from the front end
        :param field: the height input
        :return: raise validation error if height does not meet the specification
        """
    if field.data < 90 or field.data > 300:
        raise ValidationError("Please enter your height correctly.")


def character_check(form, field):
    """ This function checks the first name and surname to see if it meets the
        correct specifications

        :param form: the user input form from the front end
        :param field: the first/surname input
        :return: raise validation error if name or surname do not meet the specification
        """
    excluded_chars = "*?!'^+%&/()=}][{$#@<>0123456789"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


def validate_password(form, field):
    """ This function checks the password user input to see if it meets the
        correct specifications

        Password must contain at least 1 digit, 1 lowercase, 1 uppercase and
        1 special character

        :param form: the user input form from the front end
        :param field: the password input
        :return: raise validation error if password does not meet the specification
        """
    regex_expression = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*')
    if not regex_expression.match(field.data):
        raise ValidationError("Password must contain at least 1 digit, 1 lowercase, "
                              "1 uppercase and 1 special "
                              "character.")


def validate_date(form, field):
    """ This function checks if the user entered a valid date

           The date must be between today and 01/01/1900

           :param form: the user input form from the front end
           :param field: the date input
           :return: raise validation error if the date does not meet the specification
       """
    if field.data > datetime.date.today() or field.data < datetime.date(1900, 1, 1):
        print(datetime.date.today())
        raise ValidationError("Please enter your date of birth correctly")


class LoginForm(FlaskForm):
    """ A subclass of Flask form to take the user login details.
        Form contains email, password input classes and submit field.
    """
    email = StringField(validators=[Email(), InputRequired()])
    password = PasswordField(validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()


class RegisterForm(FlaskForm):
    """ A subclass of Flask form to take the user register details.
        Form contains a set of fields for the user to input and submit
        field so the user submit their input.
     """
    email = StringField(validators=[Email(), InputRequired()])
    firstname = StringField(validators=[InputRequired(), character_check])
    surname = StringField(validators=[InputRequired(), character_check])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=8,
                                                max=15,
                                                message='Password must be between 8 '
                                                        'and 15 characters in '
                                                        'length.'), validate_password])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 Length(min=8,
                                                        max=15,
                                                        message='Password must be '
                                                                'between 8 and 15 '
                                                                'characters in '
                                                                'length.'),
                                                 EqualTo('password',
                                                         message='Both password fields '
                                                                 'must be equal!')])
    weight = IntegerField(validators=[InputRequired(), weight_check])
    height = IntegerField(validators=[InputRequired(), height_check])
    activity_level = SelectField(InputRequired(), choices=['High', 'Medium', 'Low'])
    gender = SelectField(InputRequired(), choices=['Male', 'Female'])
    date = DateField(validators=[validate_date,InputRequired()])
    submit = SubmitField()


class SettingsFormPersonalData(FlaskForm):
    """ A subclass of Flask form to take the updated user details.
        Form contains first name and surname input classes and submit field.
    """
    firstname = StringField(validators=[InputRequired(), character_check])
    surname = StringField(validators=[InputRequired(), character_check])
    gender = SelectField(InputRequired(), choices=['Male', 'Female'])
    submit = SubmitField()
