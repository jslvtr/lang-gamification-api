from app import db, get_db
from unittest import TestCase

from models.lectures.lecture import Lecture
from models.modules.module import Module
from models.users.user import User


class TestLecture(TestCase):

    @classmethod
    def setUpClass(cls):
        get_db()

    def tearDown(self):
        for user in User.query.filter(User.email.endswith('@testcourse.com')).all():
            db.session.delete(user)
        for lecture in Lecture.query.filter(Lecture.name.endswith('_test')).all():
            db.session.delete(lecture)
        for module in Module.query.filter(Module.name.endswith("_test")).all():
            db.session.delete(module)
        db.session.commit()

    def test_create_lecture(self):
        user = User.register("testcreatelecture@testcourse.com", "123")
        user.save_to_db()

        module = Module(name="Spanish_test", user_owner=user, public=True)
        module.save_to_db()

        lecture = Lecture(name="Fruits_test", order=1, module=module)
        lecture.save_to_db()

        self.assertEqual(lecture.name, "Fruits_test")
        self.assertEqual(lecture.order, 1)
        self.assertEqual(lecture.module, module)

    def test_create_multiple_lectures_in_order(self):
        user = User.register("testmultiplelectures@testcourse.com", "123")
        user.save_to_db()

        module = Module(name="Spanish_test", user_owner=user, public=True)
        module.save_to_db()

        lecture = Lecture(name="LectureInOrder_test", module=module)
        lecture.save_to_db()

        lecture2 = Lecture(name="LectureInOrder2_test", module=module)
        lecture2.save_to_db()

        self.assertEqual(lecture.order, 1)
        self.assertEqual(lecture2.order, 2)

    def test_reorder_lecture(self):
        user = User.register("testreorderlecture@testcourse.com", "123")
        user.save_to_db()

        module = Module(name="Spanish_test", user_owner=user, public=True)
        module.save_to_db()

        lecture = Lecture(name="LectureInOrder_test", module=module)
        lecture.save_to_db()

        lecture2 = Lecture(name="LectureInOrder2_test", module=module)
        lecture2.save_to_db()

        lecture2.reorder(new_position=1)

        self.assertEqual(lecture.order, 2)
        self.assertEqual(lecture2.order, 1)
