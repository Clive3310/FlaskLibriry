from flask import Blueprint

blue_auth = Blueprint('authentication', __name__)


@blue_auth.route('/')
def index():
    return "Hello auth!"
