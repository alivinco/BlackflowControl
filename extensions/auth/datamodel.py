import json
import os

__author__ = 'alivinco'
from werkzeug.security import generate_password_hash,check_password_hash

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
