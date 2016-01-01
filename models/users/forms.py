from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email

__author__ = 'josesalvatierra'


class LoginForm(Form):
    email = StringField('Email address', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])


class RegisterForm(Form):
    email = StringField('Email address', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])
    confirm = PasswordField('Repeat Password', [
      DataRequired(),
      EqualTo('password', message='The passwords do not match.')
      ])
    accept_tos = BooleanField('I accept the Terms and Conditions.', [DataRequired()])
    # recaptcha = RecaptchaField()
