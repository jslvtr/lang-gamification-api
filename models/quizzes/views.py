import logging

from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from app import db
from models.contents.lecture_content import LectureContent
from models.lectures.lecture import Lecture
from models.quizzes.question import Question
from models.quizzes.quiz import Quiz
from models.quizzes.quiz_attempt import QuizAttempt, QuestionAnswered
from models.users.decorators import requires_access_level
from models.quizzes.forms import CreateQuizForm
from common.forms import SearchForm
import models.words.errors as WordErrors
import models.users.constants as UserConstants
from models.users.user import User
from models.words.word import Word

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

__author__ = 'jslvtr'

bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')


@bp.route('/new/<string:lecture_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def new(lecture_id):
    log.info("Called /new endpoint, creating form")
    form = CreateQuizForm(request.form)
    log.info("Form created, validating...")
    lecture = Lecture.query.get(lecture_id)

    if form.validate_on_submit():
        log.info("Form validated, attempting to create lecture.")
        try:
            Quiz(name=form.name.data,
                 lecture=lecture).save_to_db()
            log.info("Lecture created.")
        except WordErrors.WordError as e:
            log.warn("Lecture error with message '{}', redirecting to teach.".format(e.message))
            return redirect(url_for('modules.teach', message=e.message))
        log.info("Word created, redirecting to word list for this module.")
        return redirect(url_for('.quiz_list', lecture_id=lecture_id))
    log.info("Form not valid or this is GET request, presenting words/new.html template")
    return render_template('quizzes/new.html', form=form, bg="#3498DB", lecture=lecture)


@bp.route('/lecture/<string:lecture_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def quiz_list(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    is_owner = g.user.is_course_creator(lecture.module)
    form = SearchForm(request.form)
    search_term = ""
    if form.validate_on_submit():
        search_term = form.term.data
    quizzes = Quiz.search_by_name(lecture_id=lecture_id, search_term=search_term)
    return render_template('quizzes/list.html',
                           lecture=lecture,
                           quizzes=quizzes,
                           is_owner=is_owner,
                           form=form)


@bp.route('/<string:quiz_id>')
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    module = quiz.lecture.module
    if not g.user.is_course_creator(module):
        return redirect(url_for('modules.dashboard'))

    return render_template('quizzes/questions.html', quiz=quiz, tag_names=[tag.name for tag in quiz.lecture.tags])


@bp.route('/<string:quiz_id>/view')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def do_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    complete_quiz_attempts(quiz_id)
    QuizAttempt(g.user.id, quiz.id).save_to_db()
    return render_template('quizzes/view.html', quiz=quiz)


def complete_quiz_attempts(quiz_id):
    attempts = QuizAttempt.query.filter(QuizAttempt.user_id == g.user.id, QuizAttempt.quiz_id == quiz_id, QuizAttempt.completed == False).all()
    for attempt in attempts:
        attempt.complete = True
        db.session.add(attempt)
    db.session.commit()


@bp.route('/<string:quiz_id>/question', methods=['POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def add_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    module = quiz.lecture.module
    if not g.user.is_course_creator(module):
        return redirect(url_for('modules.dashboard'))
    request_json = request.get_json(force=True, silent=True)
    if request_json is None:
        return jsonify({"message": "The request was invalid."}), 400
    question = Question(request_json['tag'], Word.query.filter(Word.name == request_json['answer']).first(), quiz)
    question.save_to_db()
    return jsonify({"message": "Question added successfully.", "question_url": url_for('quizzes.question', question_id=question.id)}), 201


@bp.route('/question/<string:question_id>')
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def question(question_id):
    question = Question.query.get(question_id)
    module = question.quiz.lecture.module
    if not g.user.is_course_creator(module):
        return redirect(url_for('modules.dashboard'))
    return "question view page"


@bp.route('/question/check', methods=['POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def check_question():
    request_json = request.get_json(force=True, silent=True)
    if request_json is None:
        return jsonify({"message": "The request was invalid."}), 400
    question = Question.query.get(request_json['question_id'])
    try:
        correct = question.correct_answer(request_json['meaning'] == "name") == request_json['answer']
        quiz_attempt = QuizAttempt.query.filter(QuizAttempt.user_id == g.user.id, QuizAttempt.quiz_id == question.quiz.id, QuizAttempt.completed == False).first()
        question_answered = QuestionAnswered(correct=correct)
        question_answered.question = question
        quiz_attempt.questions_answered.append(question_answered)
        question_answered.save_to_db()
        return jsonify({"value": correct})
    except KeyError:
        quiz_attempt = QuizAttempt.query.filter(QuizAttempt.user_id == g.user.id, QuizAttempt.quiz_id == question.quiz.id).first()
        question_answered = QuestionAnswered(correct=False)
        question_answered.question = question
        quiz_attempt.questions_answered.append(question_answered)
        question_answered.save_to_db()
        return jsonify({"value": False})


@bp.route('/question/skip', methods=['POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def skip_question():
    request_json = request.get_json(force=True, silent=True)
    if request_json is None:
        return jsonify({"message": "The request was invalid."}), 400
    question = Question.query.get(request_json['question_id'])
    quiz_attempt = QuizAttempt.query.filter(QuizAttempt.user_id == g.user.id, QuizAttempt.quiz_id == question.quiz.id).first()
    question_answered = QuestionAnswered(correct=False)
    question_answered.question = question
    quiz_attempt.questions_answered.append(question_answered)
    question_answered.save_to_db()
    return jsonify({"value": True})


@bp.route('/quizzes/<string:quiz_id>/finish', methods=['GET'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def finish_quiz(quiz_id):
    quiz_attempt = QuizAttempt.query.filter(QuizAttempt.user_id == g.user.id, QuizAttempt.quiz_id == quiz_id, QuizAttempt.completed == False).first()
    return_values = quiz_attempt.json()
    g.user.gold += return_values['gold_earned']
    quiz_attempt.completed = True
    quiz_attempt.save_to_db()
    return jsonify(return_values), 200
