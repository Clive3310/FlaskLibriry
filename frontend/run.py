from flask import Flask
from flask_cors import CORS


def create_front():
    app = Flask(__name__)
    CORS(app)

    from frontend.handlers.main_page import blue_main
    from frontend.handlers.login import blue_auth
    from frontend.handlers.reg import blue_reg

    app.register_blueprint(blue_main, url_prefix="/")
    app.register_blueprint(blue_auth, url_prefix="/login")
    app.register_blueprint(blue_reg, url_prefix="/register")

    return app

if __name__ == '__main__':
    app = create_front()
    app.run(host='127.0.0.1', port=80)
