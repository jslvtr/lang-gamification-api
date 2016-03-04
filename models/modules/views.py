import logging

from flask import Blueprint, redirect, url_for, request, g, render_template

from models.cities.city import City
from models.modules.module import Module
from models.users.decorators import requires_access_level
from models.modules.forms import CreateCourseForm
from common.forms import SearchForm
import models.modules.errors as ModuleErrors
import models.users.constants as UserConstants

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


__author__ = 'jslvtr'

bp = Blueprint('modules', __name__, url_prefix='/modules')


@bp.route('/teach', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def teach():
    log.info("Called /teach endpoint, creating form")
    form = CreateCourseForm(request.form)
    log.info("Form created, validating...")
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to create module.")
        try:
            course = Module(name=form.course_name.data,
                            user_owner=g.user,
                            public=form.public.data)
            course.save_to_db()
            city = City(name=form.course_name.data,
                        user_owner=g.user,
                        module=course)
            city.save_to_db()
            g.user.make_module_creator()
            log.info("Module created.")
        except ModuleErrors.CourseError as e:
            log.warn("Module error with message '{}', redirecting to teach".format(e.message))
            return redirect(url_for('.teach', message=e.message))
        log.info("Module created, redirecting to teaching dashboard.")
        return redirect(url_for('.dashboard'))
    log.info("Form not valid or this is GET request, presenting modules/teach.html template")
    return render_template('modules/teach.html', form=form, bg="#3498DB")


@bp.route('/dashboard')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def dashboard():
    if not g.user.is_course_creator():
        return redirect(url_for('.teach'))
    return render_template('modules/dashboard.html', modules=g.user.modules.all())


@bp.route('/module/<string:id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def module(id):
    module = Module.query.get(id)
    return render_template('modules/module.html', module=module, user_already_enrolled=g.user in module.students)


@bp.route('/public', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def public_modules():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        search_term = form.term.data
        modules = Module.search_by_name(search_term)
        return render_template('modules/list.html', modules=modules, form=form)
    return render_template('modules/list.html', modules=Module.find_public(), form=form)


@bp.route('/activate/<string:module_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def activate(module_id):
    module_to_join = Module.query.get(module_id)
    if g.user not in module_to_join.students:
        g.user.enroll_in(module_to_join)
        return redirect(url_for('.enrolled_in', module_id=module_id))
    else:
        g.user.set_city(module_to_join)
        return redirect(url_for('users.profile'))


@bp.route('/enrolled/<string:module_id>')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def enrolled_in(module_id):
    return render_template('modules/enrolled_in.html', module=Module.query.get(module_id))
