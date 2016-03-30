from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from app import db
from models.quizzes.question import Question
from models.quizzes.quiz_attempt import QuestionAnswered
from models.quizzes.challenge import create_challenge, Challenge, ChallengeAttempt, ChallengeQuestionAnswered
from models.users.decorators import requires_access_level
import models.users.constants as UserConstants
from models.users.user import User

__author__ = 'jslvtr'

bp = Blueprint('challenges', __name__, url_prefix='/challenges')


@bp.route('/challenge/<string:user_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def do_challenge(user_id):
    challenged_user = User.query.get(user_id)
    challenge = create_challenge(g.user, challenged_user, g.user.get_current_active_module().module)
    return render_template('quizzes/challenge.html', challenge=challenge, challenged_user=challenged_user)


@bp.route('<string:challenge_id>/question/check', methods=['POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def check_question(challenge_id):
    request_json = request.get_json(force=True, silent=True)
    if request_json is None:
        return jsonify({"message": "The request was invalid."}), 400
    question = Question.query.get(request_json['question_id'])
    try:
        correct = question.correct_answer(request_json['meaning'] == "name") == request_json['answer']
        challenge_attempt = ChallengeAttempt.query.filter(ChallengeAttempt.user_id == g.user.id,
                                                          ChallengeAttempt.challenge_id == challenge_id,
                                                          ChallengeAttempt.completed == False).first()
        question_answered = ChallengeQuestionAnswered(correct=correct)
        question_answered.question = question
        challenge_attempt.questions_answered.append(question_answered)
        question_answered.save_to_db()
        return jsonify({"value": correct})
    except KeyError:
        challenge_attempt = ChallengeAttempt.query.filter(ChallengeAttempt.user_id == g.user.id,
                                                          ChallengeAttempt.challenge_id == challenge_id).first()
        question_answered = ChallengeQuestionAnswered(correct=False)
        question_answered.question = question
        challenge_attempt.questions_answered.append(question_answered)
        question_answered.save_to_db()
        return jsonify({"value": False})


@bp.route('<string:challenge_id>/question/skip', methods=['POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def skip_question(challenge_id):
    request_json = request.get_json(force=True, silent=True)
    if request_json is None:
        return jsonify({"message": "The request was invalid."}), 400
    question = Question.query.get(request_json['question_id'])
    challenge_attempt = ChallengeAttempt.query.filter(ChallengeAttempt.user_id == g.user.id,
                                                      ChallengeAttempt.challenge_id == challenge_id).first()
    question_answered = ChallengeQuestionAnswered(correct=False)
    question_answered.question = question
    challenge_attempt.questions_answered.append(question_answered)
    question_answered.save_to_db()
    return jsonify({"value": True})


@bp.route('/<string:challenge_id>/finish', methods=['GET'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def finish_challenge(challenge_id):
    challenge_attempt = ChallengeAttempt.query.filter(ChallengeAttempt.user_id == g.user.id,
                                                      ChallengeAttempt.challenge_id == challenge_id,
                                                      ChallengeAttempt.completed == False).first()
    return_values = challenge_attempt.json()
    g.user.gold += return_values['gold_earned']
    challenge_attempt.completed = True
    challenge_attempt.save_to_db()
    return jsonify(return_values), 200


@bp.route('/respond/<string:challenge_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def respond_challenge(challenge_id):
    challenge = Challenge.query.get(challenge_id)
    return render_template('quizzes/challenge.html', challenge=challenge, challenged_user=challenge.challenger)
