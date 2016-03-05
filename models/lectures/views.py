import logging

from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from models.contents.lecture_content import LectureContent
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
    form.order.choices = [(len(module.lectures.all()), 'Last')] + [(x, str(x)) for x in range(0, len(module.lectures.all()))]

    if form.validate_on_submit():
        log.info("Form validated, attempting to create lecture.")
        try:
            Lecture(name=form.name.data,
                    module=module,
                    description=form.description.data,
                    order=form.order.data if form.order.data > 0 else None).save_to_db()
            log.info("Lecture created.")
        except WordErrors.WordError as e:
            log.warn("Word error with message '{}', redirecting to teach".format(e.message))
            return redirect(url_for('modules.teach', message=e.message))
        log.info("Word created, redirecting to word list for this module.")
        return redirect(url_for('.lecture_list', module_id=module_id))
    log.info("Form not valid or this is GET request, presenting words/new.html template")
    return render_template('lectures/new.html', form=form, bg="#3498DB", module=module)


@bp.route('/module/<string:module_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def lecture_list(module_id):
    module = Module.query.get(module_id)
    is_owner = g.user.is_course_creator(module)
    form = SearchForm(request.form)
    search_term = ""
    if form.validate_on_submit():
        search_term = form.term.data
    lectures = Lecture.search_by_name(module_id=module_id, search_term="", order_by=Lecture.order, direction=1)
    return render_template('lectures/list.html',
                           module=module,
                           lectures=lectures,
                           reorder=search_term == "" and is_owner,
                           is_owner=is_owner,
                           form=form)


@bp.route('/reorder/<string:module_id>', methods=['POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def reorder(module_id):
    request_json = request.get_json(force=True)
    lecture_id = int(request_json['lecture_id'])
    new_position = int(request_json['new_position'])
    Lecture.change_order(lecture_id=lecture_id,
                         module_id=module_id,
                         new_position=new_position)
    return jsonify({"message": "Lecture order changed to position {}.".format(new_position)}), 201


@bp.route('/<string:lecture_id>')
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def lecture(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    module = lecture.module
    if not g.user.is_course_creator(module):
        return redirect(url_for('modules.dashboard'))

    return render_template('lectures/add_content.html', lecture=lecture)


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
