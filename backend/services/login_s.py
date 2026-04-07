from backend.models.users import User
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token


def login_user(email: str, password: str):
    user = User.query.filter_by(email=email).first()

    if not user:
        raise ValueError("User doesn't exists")

    if not check_password_hash(user.password_hash, password):
        raise ValueError("Wrong password")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return [access_token, refresh_token]
