from flask import Blueprint

blue_reg = Blueprint('registration', __name__)


@blue_reg.route('/')
def index():
    return "Hello reg!"
