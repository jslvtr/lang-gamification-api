from unittest import TestCase
from app import get_db
from common.database import Database
from models.users.user import User
import models.users.errors as UserErrors
import models.users.constants as UserConstants

__author__ = 'jslvtr'


class TestUserIntegration(TestCase):
    @classmethod
    def setUpClass(cls):
        get_db()

    def tearDown(self):
        Database.remove(UserConstants.COLLECTION, {"email": {"$regex": ".*@example.com"}})

    def test_find_by_id(self):
        # Register user first
        user = User.register("findbyid@example.com", "123")

        # Find by id
        self.assertIsNotNone(User.find_by_id(user.get_id()))

    def test_find_by_email(self):
        user = User.register("findbyemail@example.com", "123")

        self.assertIsNotNone(User.find_by_email(user.email))

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
