class ActiveModuleError(Exception):
    def __init__(self, message):
        self.message = message


class LectureAlreadyCompletedException(ActiveModuleError):
    pass


class InsufficientGoldForLectureUnlock(ActiveModuleError):
    pass


class LectureNotOwnedException(ActiveModuleError):
    pass
