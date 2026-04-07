from flask_restful import Resource
from flask import request
from backend.services.reg_s import register_user


class Register(Resource):
    def post(self):
        data = request.get_json()

        try:
            user = register_user(data["email"], data["password"])
            return {"message": "User created", "id": user.id}, 201
        except ValueError as e:
            return {"error": str(e)}, 400
