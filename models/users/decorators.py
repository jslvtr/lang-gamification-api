from functools import wraps
from flask import g, url_for, request, redirect

__author__ = 'jslvtr'


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('users.login', next=request.path))
            elif not g.user.allowed(access_level):
                return redirect(url_for('users.profile', message="You do not have access to that page. Sorry!", next=request.path))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
