import random
from app import db
import models.quizzes.constants as QuizConstants
import common.helper_tables as HelperTables


def create_challenge(challenger, challengee, module):
    questions = get_all_matching_questions(challenger, challengee, module.id)
    ten_questions = set()
    while len(ten_questions) < min(len(questions), 10):
        ten_questions.add(random.choice(list(questions)))

    challenge = Challenge(challenger, challengee, list(ten_questions))
    challenger_attempt = ChallengeAttempt(challenger, challenge)
    challengee_attempt = ChallengeAttempt(challengee, challenge)

    db.session.add(challenge)
    db.session.add(challenger_attempt)
    db.session.add(challengee_attempt)
    db.session.commit()

    return challenge


def get_all_matching_questions(challenger, challengee, module_id):
    challenger_questions = set(challenger.get_questions_in_active_module(module_id))
    challengee_questions = set(challengee.get_questions_in_active_module(module_id))

    return challenger_questions.intersection(challengee_questions)


class Challenge(db.Model):
    __tablename__ = QuizConstants.CHALLENGE_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)

    challenger_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    challenger = db.relationship('User', foreign_keys=[challenger_id])

    challengee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    challengee = db.relationship('User', foreign_keys=[challengee_id])

    questions = db.relationship('Question', secondary=HelperTables.challenges_questions)

    def __init__(self, challenger_attempt, challengee_attempt, questions):
        self.challenger_attempt = challenger_attempt
        self.challengee_attempt = challengee_attempt
        self.questions = questions

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class ChallengeAttempt(db.Model):
    __tablename__ = QuizConstants.CHALLENGE_ATTEMPTS_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    challenge = db.relationship('Challenge')

    questions_answered = db.relationship('ChallengeQuestionAnswered', lazy='dynamic')

    def __init__(self, user, challenge):
        self.user = user
        self.challenge = challenge
        self.completed = False

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        for question_answered in self.questions_answered:
            db.session.delete(question_answered)
        db.session.delete(self)
        db.session.commit()

    def json(self):
        score = self.questions_answered.filter_by(correct=True).count()
        return {
            "score": score,
            "num_questions": len(self.challenge.questions),
            "gold_earned": score * 2
        }


class ChallengeQuestionAnswered(db.Model):
    __tablename__ = 'challenge_questions_answered'

    id = db.Column(db.Integer, primary_key=True)
    challenge_attempt_id = db.Column(db.Integer,
                                     db.ForeignKey('{}.id'.format(QuizConstants.CHALLENGE_ATTEMPTS_TABLE_NAME)))
    question_id = db.Column(db.Integer,
                            db.ForeignKey('{}.id'.format(QuizConstants.QUESTION_TABLE_NAME)))
    correct = db.Column(db.Boolean)
    question = db.relationship("Question")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
