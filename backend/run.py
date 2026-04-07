from flask import Flask
from config import Config

from backend.extensions import api, jwt, db
from all_resources import add_resources

app = Flask(__name__)
app.config.from_object(Config)

add_resources(api)  # Добавляет ВСЕ ресурсы

# Отдельно интитим api, jwt_manager, БД
api.init_app(app)
jwt.init_app(app)
db.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)
