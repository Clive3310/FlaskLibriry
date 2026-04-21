from flask import Flask
from backend.config import Config

from backend.extensions import api, jwt, db
from backend.all_resources import add_resources


def create_back():
    app = Flask(__name__)
    app.config.from_object(Config)

    add_resources(api)  # Добавляет ВСЕ ресурсы

    # Отдельно интитим api, jwt_manager, БД
    api.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_back()
    app.run(host='127.0.0.1', port=8080)
