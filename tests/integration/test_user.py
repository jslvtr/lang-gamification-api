from unittest import TestCase
import logging
import sys
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.warn(sys.path)
from app import get_db, db
from models.users.user import User
import models.users.errors as UserErrors

__author__ = 'jslvtr'


class TestUserIntegration(TestCase):
    @classmethod
    def setUpClass(cls):
        get_db()

    def tearDown(self):
        for user in User.query.filter(User.email.endswith('@example.com')).all():
            db.session.delete(user)
        db.session.commit()

    def test_find_by_id(self):
        # Register user first
        user = User.register("findbyid@example.com", "123")

        # Find by id
        self.assertIsNotNone(User.query.filter_by(id=user.id).first())

    def test_find_by_email(self):
        user = User.register("findbyemail@example.com", "123")

        self.assertIsNotNone(User.query.filter_by(email=user.email).first())

    def test_register_user(self):
        user = User.register("register@example.com", "123")

        self.assertIsNotNone(user)
        self.assertEqual("register@example.com", user.email)

    def test_check_login(self):
        user = User.register("checklogin@example.com", "123")

        self.assertTrue(User._check_login(user.email, "123"))

    def test_login(self):
        user = User.register("login@example.com", "123")

        self.assertIsNotNone(User.login(user.email, "123"))

    def test_user_not_found(self):
        with self.assertRaises(UserErrors.UserNotFoundException):
            User._check_login("test@test.com", "123")

    def test_password_incorrect(self):
        user = User.register("loginpasswordtest@example.com", "123")
        if user:
            with self.assertRaises(UserErrors.IncorrectPasswordException):
                User.login("loginpasswordtest@example.com", "124")

    def test_register_invalid_email(self):
        with self.assertRaises(UserErrors.InvalidEmailException):
            User.register("test", "123")

    def test_already_exists_register(self):
        user = User.register("alreadyexists@example.com", "123")
        if user:
            with self.assertRaises(UserErrors.UserAlreadyExistsException):
                User.register("alreadyexists@example.com", "123")
