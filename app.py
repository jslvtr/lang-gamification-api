from flask import Flask, render_template, session, request
import os
from common.database import Database
from common.sessions import MongoSessionInterface
from models.users.user import User
from models.users.views import bp

mongo_uri = os.environ.get("MONGODB_URI")

assert mongo_uri is not None, "The MongoDB URI was not set. Create an environment variable MONGODB_URI"

app = Flask(__name__)
app.session_interface = MongoSessionInterface(mongo_uri)
assert app.session_interface is not None, "The app session interface was None even though we tried to set it!"

app.secret_key = os.urandom(32)
assert app.secret_key is not None, "The app secret key was None even though we tried to set it!"


def get_db():
    Database.initialize(mongo_uri)


@app.before_first_request
def init_db():
    get_db()


@app.errorhandler(Exception)
def handle_internal_exception(ex):
    return render_template("error.html", message=str(ex))


@app.after_request
def serve_layout(response):
    if response.content_type == 'text/html; charset=utf-8' and 'static/' not in request.base_url:
        data = response.get_data()
        data = data.decode('utf-8')
        user_email = session['email'] if 'email' in session.keys() and session['email'] is not None else None
        data = render_template('base.html', is_course_creator=User.is_course_creator(user_email), data=data,
                               user_email=user_email)
        response.set_data(data)
        response.direct_passthrough = False

        return response
    return response


@app.route('/')
def index():
    return 'Hello World!'


app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(port=4995)
