from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import Regexp, Length


class SearchForm(Form):
    term = StringField('Search',
                       [Regexp(r"[a-zA-Z]*",
                               message="The search may only contain letters."),
                        Length(max=80,
                               message="The search can be up to 80 characters long.")])