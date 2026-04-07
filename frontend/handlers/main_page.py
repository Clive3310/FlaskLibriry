from flask import Blueprint, render_template

blue_main_page = Blueprint('front_page', __name__)


@blue_main_page.route('/')
def index():
    return render_template("base.html")
