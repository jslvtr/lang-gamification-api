from flask import Blueprint, request, session, render_template, redirect, url_for
import models.users.errors as UserErrors

from models.users.user import User

__author__ = 'jslvtr'

bp = Blueprint('user', __name__, url_prefix='/users')


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        payload = request.get_json(silent=True)
        try:
            user = User.login(email=payload['email'],
                              password=payload['password'])
            session['email'] = user.email
        except UserErrors.UserError as e:
            return redirect(url_for('index', message=e.message))
        return redirect(url_for('.profile'))
    else:
        return render_template('users/login.html')


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        payload = request.get_json(silent=True)
        try:
            user = User.register(email=payload['email'],
                                 password=payload['password'])
            session['email'] = user.email
        except UserErrors.UserError as e:
            return redirect(url_for('index', message=e.message))
        return redirect(url_for('.profile'))
    else:
        return render_template('users/register.html')


@bp.route('/profile')
def profile():
    user = User.find_by_email(session['email'])
    if not user:
        return redirect(url_for('index', message="You need to be logged in to access that!"))
    return render_template('users/profile.html', user=user)


@bp.route('/logout')
def logout():
    if 'email' in session.keys() and session['email']:
        return redirect(url_for('index', message="You have been logged out."))
    else:
        return redirect(url_for('index'))
