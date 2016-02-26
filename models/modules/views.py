import logging

from flask import Blueprint, redirect, url_for, request, g, render_template

from models.modules.module import Module
from models.users.decorators import requires_login
from models.users.forms import CreateCourseForm
import models.modules.errors as ModuleErrors

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


__author__ = 'jslvtr'

bp = Blueprint('users', __name__, url_prefix='/modules')


@bp.route('/teach')
@requires_login
def teach():
    if g.user:
        return redirect(url_for('.profile'))
    log.info("Called /teach endpoint, creating form")
    form = CreateCourseForm(request.form)
    log.info("Form created, validating...")
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to log user in.")
        try:
            course = Module()
            log.info("Module created.")
        except ModuleErrors.CourseError as e:
            log.warn("Module error with message '{}', redirecting to teach".format(e.message))
            return redirect(url_for('.teach', message=e.message))
        log.info("Module created, redirecting to teaching dashboard.")
        return redirect(url_for('.dashboard'))
    log.info("Form not valid or this is GET request, presenting modules/teach.html template")
    return render_template('modules/teach.html', form=form)


@bp.route('/dashboard')
@requires_login
def dashboard():
    return "This is the teaching dashboard"