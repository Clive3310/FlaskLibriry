import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")  # Расположение БД
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 5)))  # Считается в минутах
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 2)))  # Считается в днях

    JWT_VERIFY_SUB = False  # Решение проблемы "jwt.exceptions.DecodeError: Invalid crypto padding" @_@
