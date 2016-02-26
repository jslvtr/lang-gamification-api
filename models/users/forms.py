from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, Length

__author__ = 'josesalvatierra'


class LoginForm(Form):
    email = StringField('Email', [DataRequired(), Email(message="This is not a valid e-mail format.")])
    password = PasswordField('Password', [DataRequired()])


class RegisterForm(Form):
    email = StringField('Email', [DataRequired(), Email(message="This is not a valid e-mail format.")])
    password = PasswordField('Password', [DataRequired()])
    confirm = PasswordField('Confirm', [
        DataRequired(),
        EqualTo('password', message='The passwords do not match.')
    ])
    accept_tos = BooleanField('I accept the Terms and Conditions.', [DataRequired()])
    recaptcha = RecaptchaField()


class CreateCourseForm(Form):
    course_name = StringField('Course Name',
                              [DataRequired(),
                               Regexp(r"[a-zA-Z]{4,}",
                                      message="The course name may only contain letters."),
                               Length(min=4,
                                      max=80,
                                      message="The course name must be between 4 and 80 characters long.")])
    password = PasswordField('Public Course', [DataRequired()])
