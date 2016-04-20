from app import db
import models.quizzes.constants as QuizConstants


class QuestionAnswered(db.Model):
    __tablename__ = 'questions_answered'

    id = db.Column(db.Integer, primary_key=True)
    quiz_attempt_id = db.Column(db.Integer,
                                db.ForeignKey('{}.id'.format(QuizConstants.ATTEMPTS_TABLE_NAME)))
    question_id = db.Column(db.Integer,
                            db.ForeignKey('{}.id'.format(QuizConstants.QUESTION_TABLE_NAME)))
    correct = db.Column(db.Boolean)
    question = db.relationship("Question")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class QuizAttempt(db.Model):
    __tablename__ = QuizConstants.ATTEMPTS_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    user = db.relationship('User')

    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quiz = db.relationship('Quiz')

    questions_answered = db.relationship('QuestionAnswered', lazy='dynamic')

    def __init__(self, student_id, quiz_id):
        self.student_id = student_id
        self.quiz_id = quiz_id
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
            "num_questions": len(self.quiz.questions),
            "gold_earned": score * 2
        }