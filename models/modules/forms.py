from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Regexp, Length

__author__ = 'josesalvatierra'


class CreateCourseForm(Form):
    course_name = StringField('Course Name',
                              [DataRequired(),
                               Regexp(r"[a-zA-Z]{4,}",
                                      message="The course name may only contain letters."),
                               Length(min=4,
                                      max=80,
                                      message="The course name must be between 4 and 80 characters long.")])
    public = BooleanField('This course is public.')
