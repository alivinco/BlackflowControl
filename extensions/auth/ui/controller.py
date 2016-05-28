from extensions.auth.datamodel import UserManager
from flask import render_template, Blueprint, request , url_for
import flask
from libs.flask_login import LoginManager, login_user, logout_user, login_required
from auth0.v2.authentication import Database
import logging

__author__ = 'alivinco'

log = logging.getLogger("auth_ctrl")

AUTH0_CLIENT_ID = ""
global_context = {}
mod_auth = Blueprint('mod_auth', __name__)
login_manager = LoginManager()
# login_manager.login_view ="%s/ui/login"%mod_auth.url_prefix


# user = User("shurik","test")
um = UserManager()


def init_auth0():
    return Database('zmarlin.eu.auth0.com')


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
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        auth_type = global_context["auth_type"]
        if auth_type=="local":
            user = um.get_user(username)
            if user :
                if user.check_password(password):
                    # Login and validate the user.
                    login_user(user,remember=True)
                    log.info("User %s logged in successfully . Using %s"%(username,auth_type))
                    flask.flash('Logged in successfully.')

                    next = flask.request.args.get('next')

                    return flask.redirect(next or url_for("index"))
                else :
                    log.info("User %s used wrong password . Using %s"%(username,auth_type))

        elif auth_type=="auth0":
            auth0 = init_auth0()
            try:
                result = auth0.login(AUTH0_CLIENT_ID,username=username,password=password,connection="Username-Password-Authentication",
                            grant_type="password", scope="openid email nickname app_metadata")
                if result:
                    user = um.get_user(username)
                    if not user:
                        user=um.add_user(username,"")
                    user.set_id_token(result["id_token"])
                    log.info("User %s logged in successfully . Using %s"%(username,auth_type))
                    login_user(user,remember=True)
                    next = flask.request.args.get('next')
                    return flask.redirect(next or url_for("index"))
            except Exception as ex :
                error = ex.message
    return render_template('auth/login.html',error=error,global_context=global_context)


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