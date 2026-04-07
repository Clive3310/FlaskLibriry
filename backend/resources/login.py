from flask_restful import Resource
from flask import request
from backend.services.login_s import login_user


class Login(Resource):
    def post(self):
        data = request.get_json()

        tokens = login_user(data["email"], data["password"])

        if not tokens:
            return {"error": "Invalid credentials"}, 401

        access_token, refresh_token = tokens

        return {"access_token": access_token, "refresh_token": refresh_token}
