from flask import Flask, render_template, request, g, session
import os

from flask.ext.sqlalchemy import SQLAlchemy

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
    db.create_all()


@app.after_request
def serve_layout(response):
    if response.content_type == 'text/html; charset=utf-8' and 'static/' not in request.base_url:
        data = response.get_data()
        data = data.decode('utf-8')
        if g.user:
            log.info("Request part of a session with valid user object.")
        else:
            log.info("Not a valid user object in the current request.")
        log.info("Rendering base.html template.")
        data = render_template('base.html', is_course_creator=g.user.is_course_creator() if g.user else False,
                               data=data,
                               user=g.user)
        log.info("base.html template rendered, setting data of response and returning.")
        response.set_data(data)
        response.direct_passthrough = False

        return response
    return response


@app.route('/')
def index():
    return 'Hello World!'


from models.users.views import bp as userViews

app.register_blueprint(userViews)

# from models.courses.views import courseViews
# app.register_blueprint(courseViews)

# Have to import these at the bottom so SQLAlchamy sees them and can create the tables associated with the models.
from models.users.user import User
from models.courses.course import Course


@app.before_request
def before_request():
    """
    pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

if __name__ == '__main__':
    app.run(port=4995)
