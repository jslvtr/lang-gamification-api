from flask import Blueprint

__author__ = 'jslvtr'


bp = Blueprint('user', __name__, url_prefix='users')


@bp.route('/login', methods=['POST', 'GET'])
def login():
    pass


@bp.route('/register', methods=['POST', 'GET'])
def register():
    pass


@bp.route('/profile', methods=['POST', 'GET'])
def profile():
    pass


@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    pass
