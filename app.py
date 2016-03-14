from flask import Flask, render_template, g, session
import os

from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.serving import run_simple

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = os.urandom(32)
assert app.secret_key is not None, "The app secret key was None even though we tried to set it!"


@app.errorhandler(Exception)
def handle_internal_exception(ex):
    if app.debug:
        log.warn("App in DEBUG mode, raising exception.")
        raise ex
    log.error("An exception occurred with message {}".format(str(ex)))
    return render_template("error.html", message=str(ex))


@app.before_first_request
def init_db():
    get_db()


def get_db():
    log.info("Creating/Checking database tables with URI {}.".format(app.config['SQLALCHEMY_DATABASE_URI']))
    db.create_all()


@app.route('/')
def index():
    return render_template('home.html')


@app.before_request
def before_request():
    """
    pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


from models.users.views import bp as userViews
from models.modules.views import bp as moduleViews
from models.words.views import bp as wordViews
from models.lectures.views import bp as lectureViews

app.register_blueprint(userViews)
app.register_blueprint(moduleViews)
app.register_blueprint(wordViews)
app.register_blueprint(lectureViews)

# Have to import these at the bottom so SQLAlchamy sees them and can create the tables associated with the models.
from models.users.user import User
from models.modules.module import Module
from models.cities.city import City
from models.words.word import Word
from models.words.tag import Tag
from models.lectures.lecture import Lecture
from models.quizzes.quiz import Quiz
from models.quizzes.question import Question

if __name__ == '__main__':
    run_simple('localhost', 4995, app)
