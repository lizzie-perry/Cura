"""This is the main file for the Cura web application
"""
import os
import logging
import socket
import sshtunnel
from flask import render_template, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


class SecurityFilter(logging.Filter):
    """This class acts as subclass of the logging.Filter class for
    """
    def filter(self, record):
        """ This function filters the log file for all logs within the file

        :param record: the log file containing all the logs
        :return: all logs containing the word security within it
        """
        return "SECURITY" in record.getMessage()


# get correct dynamic path to the log file
# (fix for logs not being written to the file on some operating systems/
# file not being created due to insufficient permissions)
filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Cura.log')
fh = logging.FileHandler(filename, 'w')  #
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

#
logger = logging.getLogger('')
logger.propagate = False
logger.addHandler(fh)

# Initialising the SSH tunnel so the web application can connect to the database
tunnel = sshtunnel.SSHTunnelForwarder(
    ('linux.cs.ncl.ac.uk', 22),
    ssh_username='b9027301',
    ssh_password='FineWouldDig12092000',
    remote_bind_address=('cs-db.ncl.ac.uk', 3306)
)
tunnel.start()  # Starting the tunnel

# CONFIGURATION
app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://csc2033_team06:Net,?AteLuck@127.0.0.1:' \
                                 f'{str(tunnel.local_bind_port)}/csc2033_team06?charset=utf8mb4'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['RECAPTCHA_PUBLIC_KEY']='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
app.config['RECAPTCHA_PRIVATE_KEY']='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

# initialise database
db = SQLAlchemy(app)


@app.route('/')
def index():
    """ This function renders the home page view of the web application

    :return: a render of the index.html template
    """
    return render_template("index.html")


# ERROR PAGE VIEWS
@app.errorhandler(400)
def page_bad_request(error):
    """ If a 400 error occurs this function renders the 400 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
    """
    return render_template('400.html'), 400


@app.errorhandler(401)
def page_unauthorized(error):
    """ If a 401 error occurs this function renders the 401 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
    """
    return render_template('401.html'), 401


@app.errorhandler(403)
def page_forbidden(error):
    """ If a 403 error occurs this function renders the 403 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
    """
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(error):
    """ If a 404 error occurs this function renders the 404 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
        """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """ If a 500 error occurs this function renders the 500 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
    """
    return render_template('500.html'), 500


@app.errorhandler(502)
def page_bad_gateway(error):
    """ If a 502 error occurs this function renders the 502 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
    """
    return render_template('502.html'), 502


@app.errorhandler(503)
def internal_service_unavailable(error):
    """ If a 503 error occurs this function renders the 503 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
    """
    return render_template('503.html'), 503


@app.errorhandler(504)
def page_gateway_timeout(error):
    """ If a 504 error occurs this function renders the 504 html template

        :param error: indicates the function is an error page for flask
        :return: a render of the html template and error code number
    """
    return render_template('504.html'), 504


if __name__ == "__main__":
    MY_HOST = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((MY_HOST, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from Classes.classes import User


    @login_manager.user_loader
    def load_user(user_id):
        """This method gets a user object based on the user_id

            :param user_id: the id of the user being searched for the
            :return User object
        """

        return User.query.get(int(user_id))


    from users.views import users_blueprint
    from exercise.views import exercise_blueprint
    from water.views import waterIntake_blueprint
    from food.views import foodIntake_blueprint
    from admin.views import admins_blueprint
    from sleep.views import sleepIntake_blueprint

    app.register_blueprint(users_blueprint)
    app.register_blueprint(exercise_blueprint)
    app.register_blueprint(waterIntake_blueprint)
    app.register_blueprint(foodIntake_blueprint)
    app.register_blueprint(admins_blueprint)
    app.register_blueprint(sleepIntake_blueprint)

    app.run(host=MY_HOST, port=free_port, debug=True, threaded=False)
