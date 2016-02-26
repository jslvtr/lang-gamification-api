import logging

from flask import Blueprint, redirect, url_for, request, g, render_template

from models.modules.module import Module
from models.users.decorators import requires_access_level
from models.modules.forms import CreateCourseForm
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
            course = Module(form.course_name.data,
                            g.user,
                            form.public.data)
            course.save_to_db()
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
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def module(id):
    return "The module page for module {}.".format(id)