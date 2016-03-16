import logging

from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from models.contents.lecture_content import LectureContent
from models.lectures.lecture import Lecture
from models.quizzes.question import Question
from models.quizzes.quiz import Quiz
from models.users.decorators import requires_access_level
from models.quizzes.forms import CreateQuizForm
from common.forms import SearchForm
import models.words.errors as WordErrors
import models.users.constants as UserConstants
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
    return render_template('quizzes/view.html', quiz=quiz)


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
