"""This file is responsible for rendering the admin page as well as the functionality
of the web page"""
import logging
import os
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from Classes.classes import ExampleExercise
from admin.forms import AdminForm
from app import db

admins_blueprint = Blueprint('admin', __name__, template_folder='templates')
PermittedExtensions = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_ext(filename):
    """This method checks the submitted image extension to ensure it is of a permitted format"""
    return filename.split('.')[1] in PermittedExtensions


@admins_blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    """Method responsible for running the admin page and the functionality"""
    form = AdminForm()
    upload_folder = os.path.dirname(os.path.realpath('app.py'))

    if form.validate_on_submit():
        file = request.files
        if form.ExerciseImage.data.filename == '':
            flash('No selected file')
            return render_template('admin.html', form=form)
        if file:
            try:
                imagename = secure_filename(form.ExerciseImage.data.filename)
                if allowed_ext(imagename):
                    filepath = (upload_folder + '/static/exerciseimages/' + imagename)
                    form.ExerciseImage.data.save(filepath)
                    new_example = ExampleExercise(exercise_name=form.ExerciseName.data,
                                                  exercise_type=form.ExerciseType.data,
                                                  exercise_description=form.ExerciseDescription.data,
                                                  exercise_burn_cal=form.ExerciseBurnCal.data,
                                                  exercise_image=imagename)
                    db.session.add(new_example)
                    db.session.commit()
                    flash('New Example Added')
                    return render_template('admin.html', form=form)

                flash('Incorrect file type! Please try again!')
                return render_template('admin.html', form=form)

            except:
                flash('Error during upload! Please try again!')
                return render_template('admin.html', form=form)

    if current_user.role == 'admin':
        return render_template('admin.html', form=form)

    logging.warning('SECURITY - UNAUTHORISED ACCESS ATTEMPT FROM USER: [%s, %s, %s]',
                    current_user.id,
                    current_user.email,
                    request.remote_addr)
    return render_template('403.html')
