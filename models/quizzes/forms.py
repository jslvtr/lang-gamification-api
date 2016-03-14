from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Regexp, Length

__author__ = 'josesalvatierra'


class CreateQuizForm(Form):
    name = StringField('Topic',
                       [DataRequired(),
                        Regexp(r"[a-zA-Z]{1,}",
                               message="The lecture topic may only contain letters."),
                        Length(min=1,
                               max=80,
                               message="The lecture topic must be between 4 and 80 characters long.")])
    description = StringField('Description',
                              validators=[DataRequired(), Length(min=10, max=140)])
    order = SelectField(label='Position',
                        validators=[],
                        coerce=int,
                        choices=[])
    tags = StringField('Tags',
                       [Regexp(r"[a-zA-Z,]{0,}",
                               message="The tags may only contain letters or commas.")])
