import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

SECRET_KEY = 'This string will be replaced with a proper key in production.'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'data.db')
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = True

THREADS_PER_PAGE = 8

ADMINS = frozenset(['jslvtr@gmail.com'])

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = 'noneyet'
RECAPTCHA_PRIVATE_KEY = 'noneyet'
RECAPTCHA_OPTIONS = {'theme': 'white'}

MAILGUN_API_KEY = 'key-1f1fb4afbcec8c5fca169a0c940767cc'
MAILGUN_DOMAIN = 'sandbox0fd1d065f521484b8af277034648e756.mailgun.org'
