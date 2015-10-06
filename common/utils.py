import re

__author__ = 'jslvtr'


def email_is_valid(email):
    address = re.compile('^[\w\d.+-]+@([\w\d.]+\.)+[\w]+$')
    return True if address.match(email) else False
