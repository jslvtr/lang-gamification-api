from unittest import TestCase
from app import get_db, db
from models.modules.module import Module
from models.users.user import User
from models.words.word import Word
from models.words.tag import Tag

__author__ = 'jslvtr'


class TestWordIntegration(TestCase):
    @classmethod
    def setUpClass(cls):
        get_db()

    def tearDown(self):
        for user in User.query.filter(User.email.endswith('@testcourse.com')).all():
            db.session.delete(user)
        for word in Word.query.filter(Word.name.endswith('testcoursexyz')).all():
            db.session.delete(word)
        for tag in Tag.query.filter(Tag.name.endswith("testcoursexyz")).all():
            db.session.delete(tag)
        for module in Module.query.filter(Module.name.endswith("_test")).all():
            db.session.delete(module)
        db.session.commit()

    def test_find_by_id(self):
        user = User.register("findbyid@testcourse.com", "123")
        module = Module("findbyid_test", user)
        module.save_to_db()
        word = Word(name="testfindidtestcoursexyz",
                    meaning="prueba",
                    difficulty=3,
                    module=module)
        word.save_to_db()

        # Find by id
        self.assertIsNotNone(Word.query.filter_by(id=word.id).first())

    def test_delete(self):
        user = User.register("testdelete@testcourse.com", "123")
        module = Module("testdelete_test", user)
        word = Word(name="testdeletetestcoursexyz",
                    meaning="prueba",
                    difficulty=3,
                    module=module)

        word.save_to_db()
        user.save_to_db()
        module.save_to_db()

        word.remove_from_db()
        self.assertEqual(len(Word.query.filter_by(id=word.id).all()), 0)

    def test_save_to_db_with_tags(self):
        user = User.register("testdelete@testcourse.com", "123")
        module = Module("testdelete_test", user)
        tags = [Tag(s) for s in ["test", "tag", "another"]]
        for tag in tags:
            tag.save_to_db()
        word = Word(name="testtagstestcoursexyz",
                    meaning="prueba",
                    difficulty=3,
                    module=module,
                    tags=tags)

        word.save_to_db()
        user.save_to_db()
        module.save_to_db()

        tags_from_db = Word.query.filter_by(id=word.id).first().tags
        for tag_from_db in tags_from_db:
            self.assertIn(tag_from_db.name, [t.name for t in tags])

    def test_filter_words_in_module_with_tag(self):
        user = User.register("testfilterbytag@testcourse.com", "123")
        module = Module("testfilterbytag_test", user)
        tag_name = "testtagnameintegration"
        tags = [Tag(tag_name)]
        for tag in tags:
            tag.save_to_db()
        word = Word(name="testtagstestcoursexyz",
                    meaning="prueba",
                    difficulty=3,
                    module=module,
                    tags=tags)
        word2 = Word(name="testtags2testcoursexyz",
                     meaning="prueba",
                     difficulty=3,
                     module=module)

        word.save_to_db()
        word2.save_to_db()

        words_from_db = Word.search_by_tag_or_name(module.id, tag_name)
        self.assertEqual(len(words_from_db), 1)

    def test_filter_words_in_module_by_name(self):
        user = User.register("testfilterbyname@testcourse.com", "123")
        module = Module("testfilterbyname_test", user)
        module_name = "testfilterbynametestcoursexyz"
        word = Word(name=module_name,
                    meaning="prueba",
                    difficulty=3,
                    module=module)

        word.save_to_db()

        words_from_db = Word.search_by_tag_or_name(module.id, module_name)
        self.assertEqual(len(words_from_db), 1)
