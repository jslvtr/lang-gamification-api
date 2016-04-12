class QuizError(Exception):
    def __init__(self, message):
        self.message = message


class IncompleteChallengeException(QuizError):
    pass


class DrawChallengeException(QuizError):
    pass


class NotParticipantException(QuizError):
    pass


class NotEnoughGoldForWagerException(QuizError):
    pass


class NotEnoughQuestionsException(QuizError):
    pass
