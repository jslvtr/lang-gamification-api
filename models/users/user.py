import uuid
from common.database import Database
import models.users.errors as UserErrors
import common.utils as Utils
import models.users.constants as UserConstants

__author__ = 'jslvtr'


class User(object):

    def __init__(self, email, password, courses, _id=None):
        self.email = email
        self.password = password
        self.courses = courses
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<User {}, {}>".format(self.email, self._id)

    def get_id(self):
        return self._id

    @classmethod
    def find_by_id(cls, id_):
        user_data = Database.find_one(UserConstants.COLLECTION, {"_id": id_})
        return cls(**user_data) if user_data else None

    @classmethod
    def find_by_email(cls, email):
        user_data = Database.find_one(UserConstants.COLLECTION, {"email": email})
        return cls(**user_data) if user_data else None

    def json(self, private=True):
        data = {
            "email": self.email,
            "courses": self.courses,
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

        if Utils.check_hashed_password(password, user.password):
            return user

    @staticmethod
    def login(email, password):
        user = User._check_login(email, password)
        if user:
            return user
        raise UserErrors.IncorrectPasswordException("Your password or e-mail were incorrect.")

    @staticmethod
    def register(email, password):
        if not Utils.email_is_valid(email):
            raise UserErrors.InvalidEmailException("The e-mail you used to register was invalid.")
        if User.find_by_email(email) is not None:
            raise UserErrors.UserAlreadyExistsException("An user already exists with that e-mail.")

        user = User(email=email,
                    password=Utils.hash_password(password),
                    courses=[])

        user.save_to_db()
        return user

    def save_to_db(self):
        Database.insert(UserConstants.COLLECTION, self.json(private=True))

    def allowed(self, course=None):
        if course is not None:
            return course in self.courses
        return True
