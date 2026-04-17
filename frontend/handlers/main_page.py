from flask import Blueprint, render_template

blue_main = Blueprint('front_page', __name__)


@blue_main.route('/')
def index():
    return render_template("base.html")
