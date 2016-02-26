from unittest import TestCase
from app import get_db, db
from models.modules.module import Module
from models.users.user import User
import models.modules.errors as CourseErrors

__author__ = 'jslvtr'


class TestCourseIntegration(TestCase):
    @classmethod
    def setUpClass(cls):
        get_db()

    def tearDown(self):
        for user in User.query.filter(User.email.endswith('@testcourse.com')).all():
            db.session.delete(user)
        for course in Module.query.filter(Module.name.endswith("_test")).all():
            db.session.delete(course)
        db.session.commit()

    def test_find_by_id(self):
        # Register user first
        user = User.register("findbyid@testcourse.com", "123")
        # Create the course to test
        course = Module("findbyid_test", user)
        course.save_to_db()

        # Find by id
        self.assertIsNotNone(Module.query.filter_by(id=course.id).first())

    def test_find_by_name(self):
        # Register user first
        user = User.register("findbyname@testcourse.com", "123")
        # Create the course to test
        course = Module("findbyname_test", user)

        # Find by id
        self.assertIsNotNone(Module.query.filter_by(name=course.name).first())

    def test_course_not_found(self):
        with self.assertRaises(CourseErrors.CourseNotFoundException):
            Module.find(name="test_not_found")

    def test_delete(self):
        user = User.register("testdelete@testcourse.com", "123")
        course = Module("testdelete_test", user)

        user.save_to_db()
        course.save_to_db()
        user.access = 1

        Module.delete(course.id, user)
        self.assertEqual(len(Module.query.filter_by(id=course.id).all()), 0)

    def test_delete_not_allowed(self):
        user = User.register("testdelete_notallowed@testcourse.com", "123")
        course = Module("testdelete_notallowed_test", None)

        with self.assertRaises(CourseErrors.NotOwnerException):
            Module.delete(course.id, user)

    def test_save_to_db(self):
        user = User.register("savedb@testcourse.com", "123")
        course = Module("savedb_test", user)

        course.save_to_db()

        self.assertIsNotNone(Module.query.filter_by(name=course.name).first())

    def test_remove_from_db(self):
        user = User.register("removedb@testcourse.com", "123")
        course = Module("removedb_test", user)

        course.save_to_db()

        self.assertIsNotNone(Module.query.filter_by(name=course.name).first())

        course.remove_from_db()

        self.assertEqual(len(Module.query.filter_by(id=course.id).all()), 0)
