import models.users.errors as UserErrors
import common.utils as Utils
import models.users.constants as UserConstants
import logging
import sys
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.warn(sys.path)
from app import db

__author__ = 'jslvtr'


class User(db.Model):

    __tablename__ = UserConstants.TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255), unique=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User {}>".format(self.email)

    @staticmethod
    def _check_login(email, password):
        user = User.query.filter_by(email=email).first()

        if not user:
            raise UserErrors.UserNotFoundException("An user with this e-mail could not be found.")

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
        if User.query.filter_by(email=email).first() is not None:
            raise UserErrors.UserAlreadyExistsException("An user already exists with that e-mail.")

        user = User(email=email,
                    password=Utils.hash_password(password))

        db.session.add(user)
        db.session.commit()
        return user

    def is_course_creator(self):
        return len(self.courses.all()) > 0

    def allowed(self, course=None):
        if course is not None:
            return course in self.courses
        return True

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
