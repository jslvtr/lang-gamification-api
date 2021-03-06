from flask import session
from sqlalchemy import and_

import models.users.errors as UserErrors
import common.utils as Utils
import models.users.constants as UserConstants
import common.helper_tables as HelperTables
from app import db
from models.active_modules.activemodule import ActiveModule
from models.quizzes.challenge import Challenge
from models.quizzes.question import Question
from models.quizzes.quiz import Quiz
from models.users.email_confirmation import EmailConfirmation
from models.users.friend_request import FriendRequest
from models.users.notification import Notification

__author__ = 'jslvtr'


class User(db.Model):
    __tablename__ = UserConstants.TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255), unique=False)
    gold = db.Column(db.Integer)
    access = db.Column(db.Integer)
    gamified = db.Column(db.Boolean)
    friends = db.relationship('User', secondary=HelperTables.friends,
                              primaryjoin=HelperTables.friends.c.student_id == id,
                              secondaryjoin=HelperTables.friends.c.friend_id == id, lazy='dynamic')

    def __init__(self, email, password, access=UserConstants.USER_TYPES['USER'], gamified=True):
        self.email = email
        self.password = password
        self.access = access
        self.gamified = gamified
        self.gold = 0

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
        user = User._check_login(email.lower(), password)
        if user:
            if EmailConfirmation.query.filter(EmailConfirmation.student_id == user.id).first().confirmed:
                return user
            raise UserErrors.UserNotConfirmedException("The e-mail for this user has not been confirmed.")
        raise UserErrors.IncorrectPasswordException("Your password or e-mail were incorrect.")

    @staticmethod
    def register(email, password, confirm_email=False):
        email = email.lower()
        if not Utils.email_is_valid(email):
            raise UserErrors.InvalidEmailException("The e-mail you used to register was invalid.")
        if User.query.filter_by(email=email).first() is not None:
            raise UserErrors.UserAlreadyExistsException("An user already exists with that e-mail.")

        user = User(email=email,
                    password=Utils.hash_password(password),
                    gamified=User.query.filter().count() % 2 == 0)
        confirmation = EmailConfirmation(user)
        if not confirm_email:
            confirmation.confirmed = True
        confirmation.save_to_db()
        if confirm_email:
            confirmation.send()

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

    def get_current_active_module(self):
        if session.get('active_module'):
            return ActiveModule.query.get(session['active_module'])
        else:
            return self.active_modules[0] if len(self.active_modules.all()) > 0 else None

    def set_active_module(self, module):
        active_module = ActiveModule.query.filter(
            and_(ActiveModule.module_id == module.id, ActiveModule.owner_id == self.id)).first()
        session['active_module'] = active_module.id

    def enroll_in(self, module):
        module.students.append(self)
        module.save_to_db()
        active_module = ActiveModule(name=module.name,
                                     user_owner=self,
                                     module=module)
        active_module.save_to_db()
        session['active_module'] = active_module.id

    def pending_friendships(self):
        return FriendRequest.pending_requests_for_user(self)

    def _get_active_module(self, module_id):
        return ActiveModule.get_by_student_id(module_id, self.id)

    def get_questions_in_active_module(self, module_id):
        return self._get_active_module(module_id).get_all_questions_in_completed_lectures()

    def challenges_won(self, module_id):
        return Challenge.query.filter(Challenge.winner_id == self.id, Challenge.module_id == module_id).count()

    def increase_gold(self, amount, reason):
        self.gold += amount
        self.add_notification(reason, "gold", None)

    def decrease_gold(self, amount, reason):
        self.gold -= amount
        if self.gold < 0:
            self.gold = 0
        self.add_notification(reason, "gold", None)

    def add_notification(self, message, type, data):
        Notification(message, type, data, self).save_to_db()

    @property
    def unread_notifications(self):
        return self.notifications.filter(Notification.read == False)

    def read_notifications(self):
        for notification in self.unread_notifications:
            notification.read = True
            db.session.add(notification)
        db.session.commit()

    def delete_notification(self, notification_id):
        notification = Notification.query.filter(Notification.student_id == self.id, Notification.id == notification_id).first()
        if notification is None:
            raise UserErrors.NotNotificationOwnerException("Error deleting notification.")
        notification.remove_from_db()

    def delete_notifications_except_challenges(self):
        notifications = Notification.query.filter(Notification.student_id == self.id,
                                                  Notification.read == True,
                                                  Notification.type != "challenge")
        for notification in notifications:
            db.session.delete(notification)
        db.session.commit()

    @property
    def friends_ordered_by_trophies(self):
        return self.friends.order_by(User.gold.desc())
