from sqlalchemy import and_

from app import db
import models.quizzes.constants as QuizConstants
import common.helper_tables as HelperTables


class Quiz(db.Model):
    __tablename__ = QuizConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))

    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module',
                             backref=db.backref('quizzes', lazy='dynamic'))
    questions = db.relationship('Question', secondary=HelperTables.quizzes_questions,
                                backref=db.backref('quizzes', lazy='dynamic'))

    def __init__(self, title, module):
        self.title = title
        self.module = module

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()
