from flask import Blueprint, request, session, render_template, redirect, url_for, g
import models.users.errors as UserErrors
from models.users.forms import LoginForm, RegisterForm
import logging
from models.users.user import User
from models.users.decorators import requires_access_level
import models.users.constants as UserConstants

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


__author__ = 'jslvtr'

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if g.user:
        return redirect(url_for('.profile'))
    log.info("Called /login endpoint, creating form")
    form = LoginForm(request.form)
    log.info("Form created, validating...")
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to log user in.")
        try:
            user = User.login(email=form.email.data,
                              password=form.password.data)
            session['user_id'] = user.id
            log.info("User logged in and e-mail in session.")
        except UserErrors.UserError as e:
            log.warn("User error with message '{}', redirecting to login".format(e.message))
            return redirect(url_for('.login', message=e.message))
        log.info("User logged in, redirecting to profile.")
        return redirect(url_for('.profile'))
    log.info("Form not valid or this is GET request, presenting users/login.html template")
    return render_template('users/login.html', form=form, bg="#3498DB")


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if g.user:
        return redirect(url_for('.profile'))
    log.info("Called /register endpoint, creating form")
    form = RegisterForm(request.form)
    log.info("Form created, validating...")
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        log.info("Form validated, attempting to log user in.")
        try:
            user = User.register(email=form.email.data,
                                 password=form.password.data)
            session['user_id'] = user.id
            log.info("User logged in and e-mail in session.")
        except UserErrors.UserError as e:
            log.warn("User error with message '{}', redirecting to login".format(e.message))
            return redirect(url_for('index', message=e.message))
        log.info("User logged in, redirecting to profile.")
        return redirect(url_for('.profile'))
    log.info("Form not valid or this is GET request, presenting users/register.html template")
    return render_template('users/register.html', form=form, bg="#3498DB")


@bp.route('/profile')
@requires_access_level(UserConstants.USER_TYPES['USER'])
def profile():
    return render_template('users/profile.html')


@bp.route('/logout')
def logout():
    if 'user_id' in session.keys() and session['user_id']:
        session.pop('user_id')
        return redirect(url_for('index', message="You have been logged out."))
    else:
        return redirect(url_for('index'))
