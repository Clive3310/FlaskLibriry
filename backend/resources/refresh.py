from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token


class Refresh(Resource):  # Refresh access AND refresh tokens
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        print(f"User {user_id} refreshes JWT tokens")
        new_access_token = create_access_token(identity=user_id)

        return {"access_token": new_access_token}
