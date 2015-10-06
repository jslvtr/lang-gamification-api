from functools import wraps
from os import abort
from flask import session, make_response
from models.users.user import User
from models.modules.module import Module

__author__ = 'jslvtr'


def secure(access_level, module_name=None):
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            if 'email' in session.keys() and session['email'] is not None:
                user = User.find_by_email(session['email']).allowed(access_level)
                if user.allowed(access_level):
                    if not module_name or (module_name and Module.allowed(module_name, user.email)):
                        return make_response(func(*args, **kwargs))
            else:
                abort(401)

        return func_wrapper

    return decorator
