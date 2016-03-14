import logging

from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from models.contents.lecture_content import LectureContent
from models.lectures.lecture import Lecture
from models.quizzes.quiz import Quiz
from models.users.decorators import requires_access_level
from models.quizzes.forms import CreateQuizForm
from common.forms import SearchForm
import models.words.errors as WordErrors
import models.users.constants as UserConstants
from models.words.tag import Tag

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
            tags = [Tag(tag.strip()) for tag in form.tags.data.split(",")]
            Quiz(name=form.name.data,
                 lecture=lecture,
                 tags=tags).save_to_db()
            log.info("Lecture created.")
        except WordErrors.WordError as e:
            log.warn("Lecture error with message '{}', redirecting to teach".format(e.message))
            return redirect(url_for('modules.teach', message=e.message))
        log.info("Word created, redirecting to word list for this module.")
        return redirect(url_for('.quiz_list', lecture_id=lecture_id))
    log.info("Form not valid or this is GET request, presenting words/new.html template")
    return render_template('quizzes/new.html', form=form, bg="#3498DB", module=lecture)


@bp.route('/lecture/<string:lecture_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def quiz_list(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    is_owner = g.user.is_course_creator(lecture)
    form = SearchForm(request.form)
    search_term = ""
    if form.validate_on_submit():
        search_term = form.term.data
    lectures = Quiz.search_by_name(lecture_id=lecture_id, search_term=search_term, order_by=Lecture.order, direction=1)
    return render_template('quizzes/list.html',
                           module=lecture,
                           quizzes=lectures,
                           is_owner=is_owner,
                           form=form)


@bp.route('/<string:quiz_id>')
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def lecture(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    module = quiz.module
    if not g.user.is_course_creator(module):
        return redirect(url_for('modules.dashboard'))

    return render_template('quizzes/questions.html', quiz=quiz)


@bp.route('/view/<string:quiz_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def study_lecture(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    return render_template('quizzes/view.html', quiz=quiz)


@bp.route('/<string:lecture_id>/text', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def add_text_content(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    module = lecture.module
    if not g.user.is_course_creator(module):
        return redirect(url_for('modules.dashboard'))
    if request.method == 'POST':
        content = request.form.get('editable') or None
        if not content:
            return jsonify({"message": "No changes sent!"})
        lecture_content = LectureContent.query.filter_by(lecture_id=lecture_id).first()
        if lecture_content:
            lecture_content.update_text_content(content)
        else:
            LectureContent(lecture, type="html", text=content).save_to_db()
        return jsonify({"message": "Content saved successfully"}), 201
    return render_template('lectures/content/text.html', lecture=lecture, module=module)
