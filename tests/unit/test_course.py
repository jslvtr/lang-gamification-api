from unittest import TestCase

from models.modules.module import Module
from models.users.user import User

import datetime


class TestCourse(TestCase):
    def test_create(self):
        user = User(email="test@example.com",
                    password="123")
        course = Module("test_course", user)

        self.assertEqual(course.name, "test_course")
        self.assertEqual(course.owner, user)
        self.assertEqual(course.created_date.strftime("%d-%m-%Y %H:%M"),
                         datetime.datetime.utcnow().strftime("%d-%m-%Y %H:%M"))

    def test_repr(self):
        course = Module("test_course", None)

        self.assertEqual(str(course), "<Course test_course>")
