from functools import wraps
from os import abort
from flask import session, make_response, g, url_for, request, redirect
from models.users.user import User
from models.courses.course import Course

__author__ = 'jslvtr'


def secure(access_level, module_name=None):
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if 'email' in session.keys() and session['email'] is not None:
                user = User.find_by_email(session['email']).allowed(access_level)
                if user.allowed(access_level):
                    if not module_name or (module_name and Course.allowed(module_name, user.email)):
                        return make_response(func(*args, **kwargs))
            else:
                abort(401)

        return func_wrapper

    return decorator


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('users.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function
