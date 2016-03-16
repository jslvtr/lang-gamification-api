import logging

from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from models.lectures.lecture import Lecture
from models.words.tag import Tag
from models.words.word import Word
from models.modules.module import Module
from models.users.decorators import requires_access_level
from models.words.forms import CreateWordForm
from common.forms import SearchForm
import models.words.errors as WordErrors
import models.users.constants as UserConstants

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


__author__ = 'jslvtr'

bp = Blueprint('words', __name__, url_prefix='/words')


@bp.route('/new/<string:lecture_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def new(lecture_id):
    log.info("Called /new endpoint, creating form")
    form = CreateWordForm(request.form)
    log.info("Form created, validating...")
    lecture = Lecture.query.get(lecture_id)
    if form.validate_on_submit():
        log.info("Form validated, attempting to create module.")
        try:
            log.info("Saving tags to database.")
            tags = Tag.get_tags_from_csv(form.tags.data)
            Tag.save_tags_to_db(tags)

            Word(name=form.name.data,
                 meaning=form.meaning.data,
                 difficulty=form.difficulty.data,
                 lecture=lecture,
                 tags=tags).save_to_db()
            log.info("Word created.")
        except WordErrors.WordError as e:
            log.warn("Word error with message '{}', redirecting to lecture page".format(e.message))
            return redirect(url_for('lectures.lecture', lecture_id=lecture_id, message=e.message))
        log.info("Word created, redirecting to word list for this module.")
        return redirect(url_for('.word_list', lecture_id=lecture_id))
    log.info("Form not valid or this is GET request, presenting words/new.html template")
    return render_template('words/new.html', form=form, bg="#3498DB", lecture=lecture)


@bp.route('/lecture/<string:lecture_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def word_list(lecture_id):
    if not g.user.is_course_creator():
        return redirect(url_for('.teach'))
    form = SearchForm(request.form)
    lecture = Lecture.query.get(lecture_id)
    if form.validate_on_submit():
        search_term = form.term.data
        words = Word.search_by_tag_or_name(search_term=search_term, lecture_id=lecture_id)
        return render_template('words/list.html', lecture=lecture, words=words, form=form)
    return render_template('words/list.html', lecture=lecture, form=form)


@bp.route('/lecture/<string:lecture_id>/tag/<string:tag_name>', methods=['GET'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def get_word_by_tag(lecture_id, tag_name):
    return jsonify({"answers": [word.name for word in Word.search_by_tag_query(tag=tag_name, lecture_id=lecture_id).all()]}), 200
