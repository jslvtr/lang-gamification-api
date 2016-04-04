from app import db
import models.conversations.constants as ConversationConstants
from models.searchable import SearchableModel
from models.words.word import Word
from common.names import two_random_names

import random


class Conversation(db.Model, SearchableModel):
    __tablename__ = ConversationConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String)
    answer_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    answer = db.relationship('Word')

    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'))
    lecture = db.relationship("Lecture", back_populates="conversations")

    player_one = db.Column(db.String(20))
    player_two = db.Column(db.String(20))

    utterances = db.relationship("Utterance")

    def __init__(self, tag, answer, lecture, player_one_name=None, player_two_name=None):
        self.lecture = lecture
        random_names = two_random_names()
        self.player_two = player_two_name or random_names[0]
        self.player_one = player_one_name or random_names[1]
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
    def gen(self):
        answers = [answer.meaning for answer in Word.search_by_tag_query(self.tag, self.answer.lecture_id).filter(Word.id != self.answer_id).all()]
        answers = answers[:4]
        answers.append(self.answer.meaning)
        random.shuffle(answers)

        return {'answers': answers,
                'title': ConversationConstants.CONVERSATION_TITLE,
                'replace': 'meaning'}

    def correct_answer(self, meaning):
        return self.answer.meaning if meaning else self.answer.name
