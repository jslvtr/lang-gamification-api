from flask import session
from sqlalchemy import and_

import models.users.errors as UserErrors
import common.utils as Utils
import models.users.constants as UserConstants
from app import db
from models.cities.city import City

__author__ = 'jslvtr'


class User(db.Model):
    __tablename__ = UserConstants.TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255), unique=False)
    access = db.Column(db.Integer)
    gamified = db.Column(db.Boolean)

    def __init__(self, email, password, access=UserConstants.USER_TYPES['USER'], gamified=True):
        self.email = email
        self.password = password
        self.access = access
        self.gamified = gamified

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

    def is_course_creator(self, module=None):
        if module:
            return self.access > UserConstants.USER_TYPES['USER'] and module in self.modules
        return self.access > UserConstants.USER_TYPES['USER']

    def is_admin(self):
        return self.access == UserConstants.USER_TYPES['ADMIN']

    def allowed(self, access, module=None):
        if self.is_admin():
            return True
        elif self.access >= access and module is not None:
            return module in self.modules
        return self.access >= access

    def allowed_course(self, course):
        return self.allowed(1, course)

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def make_module_creator(self):
        if not self.is_course_creator():
            self.access = UserConstants.USER_TYPES['CREATOR']
        self.save_to_db()

    def get_current_city(self):
        if session.get('city_id'):
            return City.query.get(session['city_id'])
        else:
            return self.cities[0] if len(self.cities.all()) > 0 else None

    def set_city(self, module):
        city = City.query.filter(and_(City.module_id == module.id, City.owner_id >= self.id)).first()
        session['city_id'] = city.id

    def enroll_in(self, module):
        module.students.append(self)
        module.save_to_db()
        city = City(name=module.name,
                    user_owner=self,
                    module=module)
        city.save_to_db()
        session['city_id'] = city.id
