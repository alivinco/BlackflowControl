from extensions.auth.datamodel import UserManager
from flask import render_template, Blueprint, request , url_for
import flask
from libs.flask_login import LoginManager, login_user, logout_user, login_required
__author__ = 'alivinco'

global_context = {}
mod_auth = Blueprint('mod_auth', __name__)
login_manager = LoginManager()
login_manager.login_view ="/ui/login"


# user = User("shurik","test")
um = UserManager()


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    # print "Loading user :%s"%user_id
    return um.get_user(user_id)


@mod_auth.route('/ui/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us.
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = um.get_user(username)
        if user :
            if user.check_password(password):
                # Login and validate the user.
                login_user(user,remember=True)

                flask.flash('Logged in successfully.')

                next = flask.request.args.get('next')

                return flask.redirect(next or "/ui/index")

    return render_template('auth/login.html',global_context=global_context)


@mod_auth.route('/ui/auth_manager', methods=['GET', 'POST'])
@login_required
def auth_manager():
    if request.method == "POST":
        action = request.form["action"]
        username = request.form["username"]
        password = request.form["password"]
        if action == "add_user":
            um.add_user(username,password)

    return render_template('auth/auth_manager.html',global_context=global_context,users=um.users)


@mod_auth.route('/ui/logout', methods=['GET'])
def logout():
    # user = current_user
    logout_user()
    return flask.redirect(url_for(".login"))