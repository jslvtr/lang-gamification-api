from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Regexp, Length

__author__ = 'josesalvatierra'


class CreateWordForm(Form):
    name = StringField('Word',
                       [DataRequired(),
                        Regexp(r"[a-zA-Z]{1,}",
                               message="The word may only contain letters."),
                        Length(min=1,
                               max=80,
                               message="The word must be between 4 and 80 characters long.")])
    meaning = StringField('Meaning',
                          [DataRequired(),
                           Regexp(r"[a-zA-Z]{1,}",
                                  message="The word may only contain letters."),
                           Length(min=1,
                                  max=80,
                                  message="The word must be between 4 and 80 characters long.")])
    difficulty = SelectField(label='Difficulty',
                             validators=[DataRequired()],
                             coerce=int,
                             choices=[(x, str(x)) for x in range(1, 6)])
    tags = StringField('Tags',
                       [Regexp(r"[a-zA-Z]{0,}",
                               message="The tags may only contain letters.")])


class WordSearchForm(Form):
    term = StringField('Search',
                       [Regexp(r"[a-zA-Z]*",
                               message="The search may only contain letters."),
                        Length(max=80,
                            message="The search can be up to 80 characters long.")])
