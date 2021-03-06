import logging

from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from models.active_modules.activemodule import ActiveModule
from models.contents.lecture_content import LectureContent
from models.lectures.lecture import Lecture
from models.modules.module import Module
from models.users.decorators import requires_access_level
from models.lectures.forms import CreateLectureForm
from common.forms import SearchForm
import models.words.errors as WordErrors
import models.active_modules.errors as ActiveModuleErrors
import models.users.constants as UserConstants
from models.words.tag import Tag

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
            log.info("Saving tags to database.")
            tags = Tag.get_tags_from_csv(form.tags.data)
            Tag.save_tags_to_db(tags)

            Lecture(name=form.name.data,
                    module=module,
                    description=form.description.data,
                    order=form.order.data if form.order.data > 0 else None,
                    tags=tags,
                    cost=int(form.cost.data)).save_to_db()
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
    lectures = Lecture.search_by_name(module_id=module_id, search_term=search_term, order_by=Lecture.order, direction=1)
    return render_template('lectures/list.html',
                           module=module,
                           lectures=lectures,
                           completed_lectures=ActiveModule.query.filter(ActiveModule.module_id == module.id).first().completed_lectures.all(),
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


@bp.route('/view/<string:lecture_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def study_lecture(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    if lecture in g.user.get_current_active_module().bought_lectures:
        return render_template('lectures/view.html', lecture=lecture)
    else:
        return redirect(url_for('.view_unlock', lecture_id=lecture_id, warn="You have not unlocked this lecture yet!"))


@bp.route('/complete/<string:lecture_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def complete(lecture_id):
    try:
        lecture = Lecture.query.get(lecture_id)
        active_module = g.user.get_current_active_module()
        active_module.complete_lecture(lecture_id)
        g.user.increase_gold(10, "Completed {}! (10 trophies)".format(lecture.name))
        experience = lecture.order * 10
        active_module.increase_experience(experience,
                                          "Completed {}! ({} experience in {})".format(
                                              lecture.name,
                                              experience,
                                              active_module.module.name
                                          ))
    except ActiveModuleErrors.LectureAlreadyCompletedException as e:
        pass
    except ActiveModuleErrors.LectureNotOwnedException as ex:
        return redirect(url_for('.view_unlock', lecture_id=lecture_id, warn=ex.message))
    return redirect(url_for('users.profile'))


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


@bp.route('/unlock/view/<int:lecture_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def view_unlock(lecture_id):
    return render_template('lectures/unlock.html', lecture=Lecture.query.get(lecture_id))