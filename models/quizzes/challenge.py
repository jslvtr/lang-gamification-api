import datetime
import random
from app import db
import models.quizzes.constants as QuizConstants
import common.helper_tables as HelperTables
import models.quizzes.errors as QuizErrors
from models.active_modules.activemodule import ActiveModule


def create_challenge(challenger, challengee, wager, module):

    if challenger.gold < wager:
        raise QuizErrors.NotEnoughGoldForWagerException("You don't have enough trophies for this wager (max: {})".format(challenger.gold))
    if challengee.gold < wager:
        raise QuizErrors.NotEnoughGoldForWagerException("{} doesn't have enough trophies for this wager (max: {})".format(challengee.email, challengee.gold))

    questions = get_all_matching_questions(challenger, challengee, module.id)
    if len(questions) < 3:
        raise QuizErrors.NotEnoughQuestionsException("You and your opponent have not completed enough of the module to challenge each other!")
    ten_questions = set()
    while len(ten_questions) < min(len(questions), 10):
        ten_questions.add(random.choice(list(questions)))

    challenge = Challenge(challenger, challengee, wager, list(ten_questions), module)
    challenger_attempt = ChallengeAttempt(challenger, challenge)
    challengee_attempt = ChallengeAttempt(challengee, challenge)

    challenge.accept_wager(challenger)

    db.session.add(challenge)
    db.session.add(challenger_attempt)
    db.session.add(challengee_attempt)
    db.session.add(challenger)
    db.session.commit()

    return challenge


def get_all_matching_questions(challenger, challengee, module_id):
    challenger_questions = set(challenger.get_questions_in_active_module(module_id))
    challengee_questions = set(challengee.get_questions_in_active_module(module_id))

    return challenger_questions.intersection(challengee_questions)


class Challenge(db.Model):
    __tablename__ = QuizConstants.CHALLENGE_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)

    challenger_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    challenger = db.relationship('User', foreign_keys=[challenger_id])

    challengee_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    challengee = db.relationship('User', foreign_keys=[challengee_id])

    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module')

    wager = db.Column(db.Integer, default=5)

    winner_id = db.Column(db.Integer, default=None)
    created_date = db.Column(db.DateTime)

    questions = db.relationship('Question', secondary=HelperTables.challenges_questions)

    def __init__(self, challenger, challengee, wager, questions, module):
        self.challenger = challenger
        self.challengee = challengee
        self.wager = wager
        self.questions = questions
        self.module = module
        self.created_date = datetime.datetime.utcnow()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def declare_winner(self, student_id):
        self.winner_id = student_id
        self.conclude_challenge()

    def conclude_challenge(self):
        experience = 15
        if self.winner_id == -1:
            self.return_wager_to_players()
        else:
            if self.winner_id == self.challenger.id:
                active_module = ActiveModule.query.filter(ActiveModule.module_id == self.module_id,
                                                          ActiveModule.student_id == self.challenger.id).first()
                active_module.increase_experience(experience,
                                                  "Won against {} ({} experience in {})".format(
                                                      self.challengee.email,
                                                      experience,
                                                      self.module.name
                                                  ))
                self.pay_wager(winner=self.challenger,
                               loser=self.challengee)
            else:
                active_module = ActiveModule.query.filter(ActiveModule.module_id == self.module_id,
                                                          ActiveModule.student_id == self.challengee.id).first()
                active_module.increase_experience(experience,
                                                  "Won {} ({} experience in {})".format(
                                                      self.challenger.email,
                                                      experience,
                                                      self.module.name
                                                  ))
                self.pay_wager(winner=self.challengee,
                               loser=self.challenger)

    def return_wager_to_players(self):

        def draw_against(opponent):
            return QuizConstants.CHALLENGE_DRAW_GOLD_REASON.format(opponent.email,
                                                                   self.wager)

        self.challengee.increase_gold(self.wager,
                                      reason=draw_against(self.challenger))
        self.challenger.increase_gold(self.wager,
                                      reason=draw_against(self.challengee))

        db.session.add(self.challenger)
        db.session.add(self.challengee)
        db.session.commit()

    def pay_wager(self, winner, loser):
        winner.increase_gold(self.wager * 2,
                             QuizConstants.CHALLENGE_WON_GOLD_REASON.format(loser.email,
                                                                            self.wager * 2))

    def calculate_winner_attempt(self):
        challenger_attempt = ChallengeAttempt.find(self.id, self.challenger_id, completed=True)
        challengee_attempt = ChallengeAttempt.find(self.id, self.challengee_id, completed=True)

        if challengee_attempt and challenger_attempt:

            challenger_correct_questions = challenger_attempt.correct_questions.count()
            challengee_correct_questions = challengee_attempt.correct_questions.count()

            if challenger_correct_questions > challengee_correct_questions:
                self.declare_winner(self.challenger.id)
                return {
                    "challenge": True,
                    "win": False,
                    "icon": "thumbs-down",
                    "message": "You lost :(",
                    "submessage": "You really should practice more..."
                }
            elif challengee_correct_questions > challenger_correct_questions:
                self.declare_winner(self.challengee.id)
                return {
                    "challenge": True,
                    "win": True,
                    "gold_earned": self.wager * 2,
                    "icon": "trophy",
                    "message": "You won!",
                    "submessage": "You've clearly got this. You win {} gold.".format(self.wager)
                }
            else:
                self.declare_winner(-1)
                raise QuizErrors.DrawChallengeException("This challenge was a draw!")
        else:
            raise QuizErrors.IncompleteChallengeException("Only one player has completed this challenge.")

    def no_winner_json(self):
        return {
            "challenge": True,
            "icon": "thumbs-up",
            "message": "Your friend has been notified!",
            "submessage": "We will notify you once they have responded to your challenge."
        }

    def draw_json(self):
        return {
            "challenge": True,
            "draw": True,
            "wager": self.wager,
            "icon": "star",
            "message": "You completed the challenge!",
            "submessage": "It's a draw! We've returned your wager."
        }

    @staticmethod
    def remove_old_challenges(keep):
        old_challenges = Challenge.query.filter(Challenge.id < keep,
                                                Challenge.winner_id == None).all()
        challenge_attempts = filter(lambda x: x, [ChallengeAttempt.find(c.id, c.challenger.id) for c in old_challenges])
        old_unattempted_challenges = [challenge_attempt.challenge for challenge_attempt in challenge_attempts if not challenge_attempt.completed]
        for old_challenge in old_unattempted_challenges:
            db.session.delete(old_challenge)
        db.session.commit()

    def notify_challengee(self):
        self.challengee.add_notification("You were challenged by {} for {} gold!".format(
            self.challenger.email,
            self.wager
        ), "challenge", self.id)

    def accept_wager(self, user):
        if user.id == self.challenger.id:
            self.challenger.decrease_gold(self.wager, "You waged {} trophies against {}.".format(self.wager, self.challengee.email))
        elif user.id == self.challengee.id:
            self.challengee.decrease_gold(self.wager, "You waged {} trophies against {}.".format(self.wager, self.challenger.email))


class ChallengeAttempt(db.Model):
    __tablename__ = QuizConstants.CHALLENGE_ATTEMPTS_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
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

    @classmethod
    def find(cls, challenge_id, student_id, completed=False):
        return ChallengeAttempt.query.filter(ChallengeAttempt.student_id == student_id,
                                             ChallengeAttempt.challenge_id == challenge_id,
                                             ChallengeAttempt.completed == completed).first()

    @property
    def correct_questions(self):
        return self.questions_answered.filter_by(correct=True)


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
