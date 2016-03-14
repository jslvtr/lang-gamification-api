from sqlalchemy import and_

from app import db
import models.quizzes.constants as QuizConstants
from models.searchable import SearchableModel
from models.words.word import Word


class Question(db.Model, SearchableModel):
    __tablename__ = QuizConstants.QUESTION_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    tag = db.Column(db.String)
    answer_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    answer = db.relationship('Word')

    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quiz = db.relationship("Quiz", back_populates="questions")

    def __init__(self, title, tag, answer):
        self.title = title
        self.tag = tag
        self.answer = answer
        self.answer_id = answer.id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def other_answers(self):
        answers = Word.search_by_tag_query(self.tag, self.quiz.lecture_id).filter(Word.id != self.answer_id).all()
        return answers[:5]
