from sqlalchemy import and_

from app import db
import models.quizzes.constants as QuizConstants
import common.helper_tables as HelperTables


class Quiz(db.Model):
    __tablename__ = QuizConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'))
    lecture = db.relationship('Lecture', secondary=HelperTables.quizzes_lectures,
                              backref=db.backref('quizzes', lazy='dynamic'))
    questions = db.relationship("Question", back_populates="quiz")

    def __init__(self, name, lectures):
        self.name = name
        self.lecture = lectures

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()
