from flask import Blueprint, request, session, render_template, redirect, url_for, g
import models.users.errors as UserErrors
from models.users.forms import LoginForm, RegisterForm
import logging
from models.users.user import User

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


__author__ = 'jslvtr'

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/login', methods=['POST', 'GET'])
def login():
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
def profile():
    user = User.query.filter_by(id=session['user_id']).first() if 'user_id' in session.keys() else None
    if not user:
        return redirect(url_for('.login', message="You need to be logged in to access that!"))
    return render_template('users/profile.html', user=user)


@bp.route('/logout')
def logout():
    if 'user_id' in session.keys() and session['user_id']:
        session.pop('user_id')
        return redirect(url_for('index', message="You have been logged out."))
    else:
        return redirect(url_for('index'))
