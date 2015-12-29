import re
from common.security import pwd_context

__author__ = 'jslvtr'


def email_is_valid(email):
    address = re.compile('^[\w\d.+-]+@([\w\d.]+\.)+[\w]+$')
    return True if address.match(email) else False


def hash_password(password):
    return pwd_context.encrypt(password)


def check_hashed_password(password, hashed):
    return pwd_context.verify(password, hashed)
