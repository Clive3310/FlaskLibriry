from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity


class CheckUser(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        return {"message": f"Hello user {user_id}"}
