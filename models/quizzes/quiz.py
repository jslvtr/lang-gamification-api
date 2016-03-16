from sqlalchemy import and_

from app import db
import models.quizzes.constants as QuizConstants


class Quiz(db.Model):
    __tablename__ = QuizConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'))
    lecture = db.relationship("Lecture", back_populates="quizzes")

    questions = db.relationship("Question", back_populates="quiz")

    def __init__(self, name, lecture):
        self.name = name
        self.lecture = lecture

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def search_by_name(cls, search_term, lecture_id):
        result = Quiz.query.filter(and_(Quiz.lecture_id == lecture_id, Quiz.name.contains(search_term)))
        return result
