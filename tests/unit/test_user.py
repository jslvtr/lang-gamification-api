from unittest import TestCase

from models.users.user import User
import models.users.errors as UserErrors
from hashlib import sha512

__author__ = 'jslvtr'


class TestUser(TestCase):
    user = None
    course = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.user = User.register(email="test@example.com",
                                     password=sha512("123".encode("utf-8")).hexdigest())
        except UserErrors.UserAlreadyExistsException:
            cls.user = User.query.filter_by(email="test@example.com").first()

    @classmethod
    def tearDownClass(cls):
        cls.user.remove_from_db()
        if TestUser.course:
            TestUser.course.remove_from_db()

    def test_allowed(self):
        #TestUser.course = Course("test", TestUser.user)
        #TestUser.course.save_to_db()
        #self.assertTrue(TestUser.user.allowed(TestUser.course))
        pass

    def test_allowed_no_course(self):
        self.assertTrue(TestUser.user.allowed(0))

    def test_repr(self):
        self.assertEqual("<User {}>".format(TestUser.user.email),
                         str(TestUser.user))
