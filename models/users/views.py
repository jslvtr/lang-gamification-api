from flask import Blueprint, request, session, render_template, redirect, url_for
import models.users.errors as UserErrors
from models.users.forms import LoginForm, RegisterForm

from models.users.user import User

__author__ = 'jslvtr'

bp = Blueprint('user', __name__, url_prefix='/users')


@bp.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        try:
            user = User.login(email=form.email.data,
                              password=form.password.data)
            session['email'] = user.email
        except UserErrors.UserError as e:
            return redirect(url_for('.login', message=e.message))
        return redirect(url_for('.profile'))
    return render_template('users/login.html', form=form)


@bp.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        try:
            user = User.register(email=form.email.data,
                                 password=form.password.data)
            session['email'] = user.email
        except UserErrors.UserError as e:
            return redirect(url_for('index', message=e.message))
        return redirect(url_for('.profile'))
    return render_template('users/register.html', form=form)


@bp.route('/profile')
def profile():
    user = User.find_by_email(session['email']) if 'email' in session.keys() else None
    if not user:
        return redirect(url_for('.login', message="You need to be logged in to access that!"))
    return render_template('users/profile.html', user_email=user.email)


@bp.route('/logout')
def logout():
    if 'email' in session.keys() and session['email']:
        session.pop('email')
        return redirect(url_for('index', message="You have been logged out."))
    else:
        return redirect(url_for('index'))
