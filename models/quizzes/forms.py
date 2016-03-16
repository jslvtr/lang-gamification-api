from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Regexp, Length

__author__ = 'josesalvatierra'


class CreateQuizForm(Form):
    name = StringField('Topic',
                       [DataRequired(),
                        Regexp(r"[a-zA-Z]{4,}",
                               message="The lecture topic may only contain letters."),
                        Length(min=4,
                               max=80,
                               message="The lecture topic must be between 4 and 80 characters long.")])
