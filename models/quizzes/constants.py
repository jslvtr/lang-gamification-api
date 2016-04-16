TABLE_NAME = "quiz"
CHALLENGE_TABLE_NAME = "challenge"
ATTEMPTS_TABLE_NAME = "quiz_attempt"
CHALLENGE_ATTEMPTS_TABLE_NAME = "challenge_attempt"
QUESTION_TABLE_NAME = "question"

CHALLENGE_WON_GOLD_REASON = "Won against {} ({} trophies)!"
CHALLENGE_DRAW_GOLD_REASON = "Drew against {}, recovering {} trophies."

QUESTIONS = [
    {'question': 'How do you say "{}"?',
     'replace': 'name'},
    {'question': 'What does "{}" mean?',
     'replace': 'meaning'}
]