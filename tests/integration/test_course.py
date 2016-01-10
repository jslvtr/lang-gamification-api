from unittest import TestCase
import logging
import sys
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.warn(sys.path)
from app import get_db, db
from models.courses.course import Course
from models.users.user import User
import models.courses.errors as CourseErrors

__author__ = 'jslvtr'


class TestCourseIntegration(TestCase):
    @classmethod
    def setUpClass(cls):
        get_db()

    def tearDown(self):
        for user in User.query.filter(User.email.endswith('@testcourse.com')).all():
            db.session.delete(user)
        for course in Course.query.filter(Course.name.endswith("_test")).all():
            db.session.delete(course)
        db.session.commit()

    def test_find_by_id(self):
        # Register user first
        user = User.register("findbyid@testcourse.com", "123")
        # Create the course to test
        course = Course("findbyid_test", user)
        course.save_to_db()

        # Find by id
        self.assertIsNotNone(Course.query.filter_by(id=course.id).first())

    def test_find_by_name(self):
        # Register user first
        user = User.register("findbyname@testcourse.com", "123")
        # Create the course to test
        course = Course("findbyname_test", user)

        # Find by id
        self.assertIsNotNone(Course.query.filter_by(name=course.name).first())

    def test_course_not_found(self):
        with self.assertRaises(CourseErrors.CourseNotFoundException):
            Course.find(name="test_not_found")

    def test_allowed(self):
        user = User.register("testallowed@testcourse.com", "123")
        course = Course("testallowed_test", user)

        user.save_to_db()
        course.save_to_db()

        self.assertTrue(Course.allowed(course.id, user))

    def test_not_allowed(self):
        user = User.register("testnotallowed@testcourse.com", "123")
        course = Course("testnotallowed_test", None)

        user.save_to_db()
        course.save_to_db()

        self.assertFalse(Course.allowed(course.id, user))

    def test_delete(self):
        user = User.register("testdelete@testcourse.com", "123")
        course = Course("testdelete_test", user)

        user.save_to_db()
        course.save_to_db()

        Course.delete(course.id, user)
        self.assertEqual(len(Course.query.filter_by(id=course.id).all()), 0)

    def test_delete_not_allowed(self):
        user = User.register("testdelete_notallowed@testcourse.com", "123")
        course = Course("testdelete_notallowed_test", None)

        with self.assertRaises(CourseErrors.NotOwnerException):
            Course.delete(course.id, user)

    def test_save_to_db(self):
        user = User.register("savedb@testcourse.com", "123")
        course = Course("savedb_test", user)

        course.save_to_db()

        self.assertIsNotNone(Course.query.filter_by(name=course.name).first())

    def test_remove_from_db(self):
        user = User.register("removedb@testcourse.com", "123")
        course = Course("removedb_test", user)

        course.save_to_db()

        self.assertIsNotNone(Course.query.filter_by(name=course.name).first())

        course.remove_from_db()

        self.assertEqual(len(Course.query.filter_by(id=course.id).all()), 0)
