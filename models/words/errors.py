__author__ = 'jslvtr'


class WordError(Exception):
    def __init__(self, message):
        self.message = message
