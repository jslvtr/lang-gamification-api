__author__ = 'jslvtr'


class CourseError(Exception):
    def __init__(self, message):
        self.message = message


class NotOwnerException(CourseError):
    pass


class CourseNotFoundException(CourseError):
    pass