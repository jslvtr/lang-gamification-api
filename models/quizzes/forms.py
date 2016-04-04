from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Regexp, Length

__author__ = 'josesalvatierra'


class CreateQuizForm(Form):
    name = StringField('Topic',
                       [DataRequired(),
                        Regexp(r"[a-zA-Z]{4,}",
                               message="The quiz topic may only contain letters."),
                        Length(min=4,
                               max=80,
                               message="The quiz topic must be between 4 and 80 characters long.")])


class ChallengeForm(Form):
    wager = StringField('Wager', [DataRequired(), Regexp(r"[0-9]+", message="The wager may only contain numbers")])