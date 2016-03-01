import logging

from flask import Blueprint, redirect, url_for, request, g, render_template

from models.words.tag import Tag
from models.words.word import Word
from models.modules.module import Module
from models.users.decorators import requires_access_level
from models.words.forms import CreateWordForm, WordSearchForm
import models.words.errors as WordErrors
import models.users.constants as UserConstants

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


__author__ = 'jslvtr'

bp = Blueprint('words', __name__, url_prefix='/words')


@bp.route('/new/<string:module_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def new(module_id):
    log.info("Called /new endpoint, creating form")
    form = CreateWordForm(request.form)
    log.info("Form created, validating...")
    module = Module.query.get(module_id)
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to create module.")
        try:
            tags = [Tag(tag.strip()) for tag in form.tags.data.split(",")]
            for tag in tags:
                tag.save_to_db()
            log.info("Saving tags to database.")
            Word(name=form.name.data,
                 meaning=form.meaning.data,
                 difficulty=form.difficulty.data,
                 module=module,
                 tags=tags).save_to_db()
            log.info("Word created.")
        except WordErrors.WordError as e:
            log.warn("Word error with message '{}', redirecting to teach".format(e.message))
            return redirect(url_for('.teach', message=e.message))
        log.info("Word created, redirecting to word list for this module.")
        return redirect(url_for('.word_list', module_id=module_id))
    log.info("Form not valid or this is GET request, presenting words/new.html template")
    return render_template('words/new.html', form=form, bg="#3498DB", module=module)


@bp.route('/module/<string:module_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def word_list(module_id):
    if not g.user.is_course_creator():
        return redirect(url_for('.teach'))
    form = WordSearchForm(request.form)
    if form.validate_on_submit():
        search_term = form.term.data
        words = Word.search_by_tag_or_name(search_term)
        return render_template('words/list.html', module=Module.query.get(module_id), words=words, form=form)
    return render_template('words/list.html', module=Module.query.get(module_id), form=form)
