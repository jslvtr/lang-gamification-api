from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from models.quizzes.question import Question
import models.quizzes.errors as QuizErrors
from models.quizzes.challenge import create_challenge, Challenge, ChallengeAttempt, ChallengeQuestionAnswered
from models.users.decorators import requires_access_level
import models.users.constants as UserConstants
from models.users.user import User
from models.quizzes.forms import ChallengeForm

__author__ = 'jslvtr'

bp = Blueprint('challenges', __name__, url_prefix='/challenges')


@bp.route('/challenge/<int:user_id>/', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def do_challenge(user_id):
    form = ChallengeForm(request.form)
    challenged_user = User.query.get(user_id)
    if user_id == g.user.id:
        return redirect(url_for('users.profile', warn="You tried to challenge yourself! We can't let you do that."))
    if challenged_user is None:
        return redirect(url_for('users.profile', warn="You challenged a user that doesn't exist."))

    if form.validate_on_submit():
        try:
            challenge = create_challenge(g.user, challenged_user, int(form.wager.data),
                                         g.user.get_current_active_module().module)
            Challenge.remove_old_challenges(keep=challenge.id)
        except QuizErrors.NotEnoughGoldForWagerException as e:
            return redirect(url_for('.do_challenge', user_id=user_id, warn=e.message))
        return render_template('quizzes/challenge.html', challenge=challenge, challenged_user=challenged_user)
    return render_template('quizzes/challenge_screen.html', challenged_user=challenged_user, form=form)


@bp.route('<int:challenge_id>/question/check', methods=['POST'])
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


@bp.route('/<int:challenge_id>/question/skip', methods=['POST'])
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


@bp.route('/<int:challenge_id>/finish', methods=['GET'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def finish_challenge(challenge_id):
    attempt = ChallengeAttempt.find(challenge_id, g.user.id)
    attempt.completed = True
    attempt.save_to_db()
    challenge = Challenge.query.get(challenge_id)
    try:
        winner_json = challenge.calculate_winner_attempt()
        return jsonify(winner_json), 200
    except QuizErrors.IncompleteChallengeException:
        challenge.notify_challengee()
        return jsonify(challenge.no_winner_json()), 200
    except QuizErrors.DrawChallengeException:
        return jsonify(challenge.draw_json()), 200


@bp.route('/respond/<int:challenge_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def respond_challenge(challenge_id):
    challenge = Challenge.query.get(challenge_id)
    if challenge.winner_id is not None:
        return redirect(url_for('users.notifications', message="You have already responded to that challenge."))
    try:
        challenge.accept_wager(g.user)
    except QuizErrors.NotParticipantException:
        return redirect(url_for('users.notifications', warn="You are not a participant in this challenge!"))
    return render_template('quizzes/challenge.html', challenge=challenge, challenged_user=challenge.challenger)
