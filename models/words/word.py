from app import db
import models.words.constants as WordConstants
import common.helper_tables as HelperTables


class Word(db.Model):
    __tablename__ = WordConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    meaning = db.Column(db.String(80))
    difficulty = db.Column(db.Integer)

    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module',
                             backref=db.backref('words', lazy='dynamic'))
    tags = db.relationship('Tag', secondary=HelperTables.words_tags,
                           backref=db.backref('words', lazy='dynamic'))

    def __init__(self, name, meaning, difficulty, module, tags=None):
        self.name = name
        self.meaning = meaning
        self.difficulty = difficulty
        self.module = module
        self.tags = tags or []

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()