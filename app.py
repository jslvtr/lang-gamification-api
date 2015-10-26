from flask import Flask, render_template
import os
from passlib.context import CryptContext
from common.database import Database

mongo_uri = os.environ.get("MONGODB_URI")

assert mongo_uri is not None, "The MongoDB URI was not set. Create an environment variable MONGODB_URI"

app = Flask(__name__)
assert app.session_interface is not None, "The app session interface was None even though we tried to set it!"

app.secret_key = os.urandom(32)
assert app.secret_key is not None, "The app secret key was None even though we tried to set it!"

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    all__vary_rounds=0.1,
    pbkdf2_sha256__default_rounds=8000
)


def get_db():
    Database.initialize(mongo_uri)


@app.before_first_request
def init_db():
    get_db()


@app.errorhandler(Exception)
def handle_internal_exception(ex):
    return render_template("error.html", message=str(ex))


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(port=4995)
