from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Regexp, Length

__author__ = 'josesalvatierra'


class CreateWordForm(Form):
    name = StringField('Word',
                       [DataRequired(),
                        Length(min=1,
                               max=80,
                               message="The word must be between 1 and 80 characters long.")])
    meaning = StringField('Meaning',
                          [DataRequired(),
                           Length(min=1,
                                  max=80,
                                  message="The word must be between 1 and 80 characters long.")])
    difficulty = SelectField(label='Difficulty',
                             validators=[DataRequired()],
                             coerce=int,
                             choices=[(x, str(x)) for x in range(1, 6)])
    tags = StringField('Tags',
                       [Regexp(r"[a-zA-Z,]{0,}",
                               message="The tags may only contain letters or commas.")])
