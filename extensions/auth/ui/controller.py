import json
import os

from extensions.auth.datamodel import UserManager
from flask import render_template, Blueprint, request, url_for
import flask
from libs.flask_login import LoginManager, login_user, logout_user, login_required
from auth0.v2.authentication import Database
import requests
import logging

__author__ = 'alivinco'

log = logging.getLogger("auth_ctrl")

AUTH0_CLIENT_ID = ""
AUTH0_CLIENT_SECRET = ""
REDIRECT_URI = ""
APP_INSTANCE = ""

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
    auth_type = global_context["auth_type"]
    if request.method == "GET":
        if auth_type == "local":
            return render_template('auth/login.html', error=error, global_context=global_context)
        elif auth_type == "auth0":
            state = APP_INSTANCE+":123456"
            return render_template('auth/auth0login.html', global_context=global_context ,
                                   auth_client_id=AUTH0_CLIENT_ID,
                                   redirect_uri = REDIRECT_URI,
                                   state=state)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if auth_type == "local":
            user = um.get_user(username)
            if user:
                if user.check_password(password):
                    # Login and validate the user.
                    login_user(user, remember=True)
                    log.info("User %s logged in successfully . Using %s" % (username, auth_type))
                    flask.flash('Logged in successfully.')

                    next = flask.request.args.get('next')

                    return flask.redirect(next or url_for("index"))
                else:
                    log.info("User %s used wrong password . Using %s" % (username, auth_type))
            return render_template('auth/login.html', error=error, global_context=global_context)

        # elif auth_type == "auth0":
        #     auth0 = init_auth0()
        #     try:
        #         result = auth0.login(AUTH0_CLIENT_ID, username=username, password=password, connection="Username-Password-Authentication",
        #                              grant_type="password", scope="openid email nickname app_metadata")
        #         if result:
        #             user = um.get_user(username)
        #             if not user:
        #                 user = um.add_user(username, "")
        #             user.set_id_token(result["id_token"])
        #             log.info("User %s logged in successfully . Using %s" % (username, auth_type))
        #             login_user(user, remember=True)
        #             next = flask.request.args.get('next')
        #             return flask.redirect(next or url_for("index"))
        #     except Exception as ex:
        #         error = ex.message


@mod_auth.route('/authcallback')
def callback_handling():
    env = os.environ
    code = request.args.get('code')

    json_header = {'content-type': 'application/json'}

    token_url = "https://{domain}/oauth/token".format(domain='zmarlin.eu.auth0.com')

    token_payload = {
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI , #'http://192.168.80.237:5011',
        'code': code,
        'grant_type': 'authorization_code'
    }

    token_info = requests.post(token_url, data=json.dumps(token_payload), headers=json_header).json()

    user_url = "https://{domain}/userinfo?access_token={access_token}" \
        .format(domain='zmarlin.eu.auth0.com', access_token=token_info['access_token'])

    user_info = requests.get(user_url).json()
    log.info(user_info)

    if user_info :
        user = um.add_user(user_info["name"],"")
        user.set_id_token(token_info["id_token"])
        login_user(user, remember=True)
    # We're saving all user information into the session
    #session['profile'] = user_info

    # Redirect to the User logged in page that you want here
    # In our case it's /dashboard
    return flask.redirect(url_for("index"))
    # return redirect('/dashboard')


@mod_auth.route('/ui/auth_manager', methods=['GET', 'POST'])
@login_required
def auth_manager():
    if request.method == "POST":
        action = request.form["action"]
        username = request.form["username"]
        password = request.form["password"]
        if action == "add_user":
            um.add_user(username, password)

    return render_template('auth/auth_manager.html', global_context=global_context, users=um.users)


@mod_auth.route('/ui/logout', methods=['GET'])
def logout():
    # user = current_user
    logout_user()
    return flask.redirect(url_for(".login"))
