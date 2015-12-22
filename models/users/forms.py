from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email

__author__ = 'josesalvatierra'


class LoginForm(Form):
    def generate_csrf_token(self, **kwargs):
        pass

    email = StringField('Email address', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])


class RegisterForm(Form):
    def generate_csrf_token(self, **kwargs):
        pass

    name = StringField('NickName', [DataRequired()])
    email = StringField('Email address', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])
    confirm = PasswordField('Repeat Password', [
      DataRequired(),
      EqualTo('password', message='The passwords do not match.')
      ])
    accept_tos = BooleanField('I accept the Terms and Conditions.', [DataRequired()])
    recaptcha = RecaptchaField()
