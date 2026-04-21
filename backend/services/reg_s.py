from backend.extensions import db
from backend.models.users import User
from werkzeug.security import generate_password_hash


def register_user(username: str, email: str, password: str):
    if User.query.filter_by(email=email).first():
        raise ValueError("User already exists")

    password_hash = generate_password_hash(password)

    user = User(username=username, email=email, password_hash=password_hash)

    db.session.add(user)
    db.session.commit()

    return user
