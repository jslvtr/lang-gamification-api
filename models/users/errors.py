__author__ = 'jslvtr'


class UserNotFoundException(Exception):
    pass


class IncorrectPasswordException(Exception):
    pass


class InvalidEmailException(Exception):
    pass


class UserAlreadyExistsException(Exception):
    pass