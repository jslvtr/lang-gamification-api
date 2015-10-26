from flask import Flask, render_template
import os
from passlib.context import CryptContext
from common.database import Database

mongodb_user = os.environ.get("MONGODB_USER")
mongodb_password = os.environ.get("MONGODB_PASSWORD")
mongo_url = os.environ.get("MONGODB_URL")
mongo_port = os.environ.get("MONGODB_PORT")
mongo_database = os.environ.get("MONGODB_DATABASE")

assert mongodb_user is not None, "The MongoDB user was not set. Create an environment variable MONGODB_USER"
assert mongodb_password is not None, "The MongoDB password was not set. Create an environment variable MONGODB_PASSWORD"
assert mongo_url is not None, "The MongoDB url was not set. Create an environment variable MONGODB_URL"
assert mongo_port is not None, "The MongoDB port was not set. Create an environment variable MONGODB_PORT"
assert mongo_database is not None, "The MongoDB database was not set. Create an environment variable MONGODB_DATABASE"

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
    Database.initialize(mongodb_user, mongodb_password, mongo_url, int(mongo_port), mongo_database)


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
