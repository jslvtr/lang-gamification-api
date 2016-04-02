__author__ = 'jslvtr'


class UserError(Exception):
    def __init__(self, message):
        self.message = message


class UserNotFoundException(UserError):
    pass


class IncorrectPasswordException(UserError):
    pass


class InvalidEmailException(UserError):
    pass


class UserAlreadyExistsException(UserError):
    pass


class FriendAddingError(UserError):
    pass


class NotNotificationOwnerException(UserError):
    pass