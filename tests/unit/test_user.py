from unittest import TestCase
from models.users.user import User
from hashlib import sha512

__author__ = 'jslvtr'


class TestUser(TestCase):
    def setUp(self):
        self.user = User(email="test@example.com",
                         password=sha512("123".encode("utf-8")).hexdigest(),
                         courses=["test"],
                         _id="123")

    def test_get_id(self):
        self.assertEqual(self.user.get_id(), "123")

    def test_json(self):
        json = {
            "email": "test@example.com",
            "password": sha512("123".encode("utf-8")).hexdigest(),
            "courses": ["test"],
            "_id": "123"
        }

        self.assertEqual(self.user.json(private=True),
                         json)

    def test_json_private(self):
        json = {
            "email": "test@example.com",
            "courses": ["test"],
            "_id": "123"
        }

        self.assertEqual(self.user.json(private=False),
                         json)

    def test_allowed(self):
        self.assertTrue(self.user.allowed("test"))

    def test_allowed_no_course(self):
        self.assertTrue(self.user.allowed())

    def test_repr(self):
        self.assertEqual("<User {}, {}>".format(self.user.email, self.user.get_id()),
                         str(self.user))
