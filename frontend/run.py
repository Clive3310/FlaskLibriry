from flask import Flask

app = Flask(__name__)

from frontend.handlers.main_page import blue_main_page
from frontend.handlers.auth import blue_auth
from frontend.handlers.reg import blue_reg

app.register_blueprint(blue_main_page, url_prefix="/")
app.register_blueprint(blue_auth, url_prefix="/authenticate")
app.register_blueprint(blue_reg, url_prefix="/register")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
