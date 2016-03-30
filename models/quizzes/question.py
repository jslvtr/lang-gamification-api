from app import db
import models.quizzes.constants as QuizConstants
from models.searchable import SearchableModel
from models.words.word import Word

import random


class Question(db.Model, SearchableModel):
    __tablename__ = QuizConstants.QUESTION_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String)
    answer_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    answer = db.relationship('Word')

    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quiz = db.relationship("Quiz", back_populates="questions")

    def __init__(self, tag, answer, quiz):
        self.tag = tag
        self.answer = answer
        self.answer_id = answer.id
        self.quiz = quiz
        self.quiz_id = quiz.id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def gen(self):
        target = QuizConstants.QUESTIONS[random.randint(0, len(QuizConstants.QUESTIONS) - 1)]
        answers = [answer.meaning if target['replace'] == 'name' else answer.name for answer in Word.search_by_tag_query(self.tag, self.answer.lecture_id).filter(Word.id != self.answer_id).all()]
        answers = answers[:4]
        answers.append(self.answer.meaning if target['replace'] == 'name' else self.answer.name)
        random.shuffle(answers)

        return {'answers': answers,
                'title': target['question'].format(self.answer.name if target['replace'] == 'name' else self.answer.meaning),
                'replace': target['replace']}

    def correct_answer(self, meaning):
        return self.answer.meaning if meaning else self.answer.name
