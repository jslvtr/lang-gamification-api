import logging

from flask import Blueprint, redirect, url_for, request, g, render_template

from models.lectures.lecture import Lecture
from models.modules.module import Module
from models.users.decorators import requires_access_level
from models.lectures.forms import CreateLectureForm
from common.forms import SearchForm
import models.words.errors as WordErrors
import models.users.constants as UserConstants

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


__author__ = 'jslvtr'

bp = Blueprint('lectures', __name__, url_prefix='/lectures')


@bp.route('/new/<string:module_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def new(module_id):
    log.info("Called /new endpoint, creating form")
    form = CreateLectureForm(request.form)
    log.info("Form created, validating...")
    module = Module.query.get(module_id)
    if form.validate_on_submit():
        log.info("Form validated, attempting to create lecture.")
        try:
            Lecture(name=form.name.data,
                    module=module,
                    order=form.order.data if form.order.data > 0 else None).save_to_db()
            log.info("Lecture created.")
        except WordErrors.WordError as e:
            log.warn("Word error with message '{}', redirecting to teach".format(e.message))
            return redirect(url_for('modules.teach', message=e.message))
        log.info("Word created, redirecting to word list for this module.")
        return redirect(url_for('.lecture_list', module_id=module_id))
    log.info("Form not valid or this is GET request, presenting words/new.html template")
    form.order.choices = [(0, 'Last')] + [(x, str(x)) for x in range(1, len(module.lectures.all()) + 1)]
    return render_template('lectures/new.html', form=form, bg="#3498DB", module=module)


@bp.route('/module/<string:module_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def lecture_list(module_id):
    if not g.user.is_course_creator():
        return redirect(url_for('modules.teach'))
    form = SearchForm(request.form)
    module = Module.query.get(module_id)
    if form.validate_on_submit():
        search_term = form.term.data
        lectures = Lecture.search_by_name(module_id=module_id, search_term=search_term)
        return render_template('lectures/list.html', module=module, lectures=lectures, form=form)
    return render_template('lectures/list.html', module=module, form=form)
