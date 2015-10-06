import uuid
from flask import session
from common.database import Database
from models.permissions.permissions import Permissions
import models.users.errors as UserErrors
import common.utils as Utils
import models.users.constants as UserConstants

__author__ = 'jslvtr'


class User(object):

    def __init__(self, email, password, access_level, _id=None):
        self.email = email
        self.password = password
        self.access_level = access_level
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<User {}, {}>".format(self.email, self._id)

    def get_id(self):
        return self._id

    @classmethod
    def find_by_id(cls, id_):
        return cls(**Database.find_one(UserConstants.COLLECTION, {"_id": id_}))

    @classmethod
    def find_by_email(cls, email):
        return cls(**Database.find_one(UserConstants.COLLECTION, {"email": email}))

    def json(self, private=True):
        data = {
            "email": self.email,
            "access_level": self.access_level,
            "_id": self._id
        }
        if private:
            data.update({"password": self.password})

        return data

    @staticmethod
    def _check_login(email, password):
        user = User.find_by_email(email)

        if not user:
            raise UserErrors.UserNotFoundException("A user with this e-mail could not be found.")

        return user.password == password

    @staticmethod
    def login(email, password):
        if User._check_login(email, password):
            session['email'] = email
            return True
        raise UserErrors.IncorrectPasswordException("Your password or e-mail were incorrect.")

    @staticmethod
    def register(email, password):
        if not Utils.email_is_valid(email):
            raise UserErrors.InvalidEmailException("The e-mail you used to register was invalid.")
        if User.find_by_email(email) is not None:
            raise UserErrors.UserAlreadyExistsException("An user already exists with that e-mail.")

        user = User(email=email,
                    password=password,
                    access_level=Permissions.default().name)

        user.save_to_db()
        return True

    def save_to_db(self):
        Database.insert(UserConstants.COLLECTION, self.json(private=False))

    def allowed(self, access_level):
        return Permissions.find_by_name(self.access_level).allowed(Permissions.access_to(access_level))
