import json
import os
from flask import render_template, Blueprint, request
import flask
from libs.flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash,check_password_hash

__author__ = 'alivinco'

mod_auth = Blueprint('mod_auth', __name__, template_folder='templates')
login_manager = LoginManager()
login_manager.login_view = "/ui/login"
global_context = None

class User:
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    def __init__(self,username,password):
        """

        :param username: username
        :param password: hashed password
        """
        self.username = username
        self.password = password
        self.authenticated = True

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def serialize(self):
        return {"username":self.username,"password":self.password}

    def check_password(self,password):
        return check_password_hash(self.password, password)


class UserManager:
    def __init__(self):
        self.users = {}
        self.app_root_path = os.getcwd()
        self.users_path = os.path.join(self.app_root_path, "configs", "users.json")
        self.load_from_storage()


    def load_from_storage(self):
        jobj  = json.load(file(self.users_path))
        for user in jobj:
            self.users[user["username"]] = User(user["username"],user["password"])


    def serialize_to_storage(self):
        ser_obj = []
        for k,user in self.users.iteritems():
            ser_obj.append(user.serialize())
        f = open(self.users_path,"w")
        f.write(json.dumps(ser_obj,indent=True))
        f.close()

    def get_user(self,username):
        try:
            return self.users[username]
        except:
            return None

    def add_user(self,username,password):
        self.users[username]=User(username,"")
        self.users[username].set_password(password)
        self.serialize_to_storage()


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

                return flask.redirect(next or "/ui/inter_console")

    return render_template('login.html',global_context=global_context)

@mod_auth.route('/ui/auth_manager', methods=['GET', 'POST'])
@login_required
def auth_manager():
    if request.method == "POST":
        action = request.form["action"]
        username = request.form["username"]
        password = request.form["password"]
        if action == "add_user":
            um.add_user(username,password)

    return render_template('auth_manager.html',global_context=global_context,users=um.users)

@mod_auth.route('/ui/logout', methods=['GET'])
def logout():
    # user = current_user
    logout_user()
    return flask.redirect("/ui/login")