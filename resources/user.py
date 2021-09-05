from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)
import constants
from datetime import timedelta
from models.user import UserModel
from blacklist import BLACKLIST
from redis_util import jwt_redis_blocklist
from werkzeug.security import generate_password_hash, check_password_hash


_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help=constants.BLANK_FIELD
)
_user_parser.add_argument(
    "password", type=str, required=True, help=constants.BLANK_FIELD
)


class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "A user with that username already exists"}, 400

        user = UserModel(data["username"], generate_password_hash(data["password"]))
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    @jwt_required()
    def get(cls, user_id: int):
        claims = get_jwt()
        if claims["claim"] == "admin":
            user = UserModel.find_by_id(user_id)
            if not user:
                return {"message": "User Not Found"}, 404
            return user.json(), 200
        return {"message": "access rights violation"}, 401

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User Not Found"}, 404
        user.delete_from_db()
        return {"message": "User deleted."}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data["username"])
        password = data["password"]

        # this is what the `authenticate()` function did in security.py
        if user and check_password_hash(user.password, password):
            # identity= is what the identity() function did in security.py—now stored in the JWT

            access_token = create_access_token(
                identity=user.id,
                fresh=True,
                additional_claims={"claim": "admin"}
                if user.id == 2
                else {"claim": "user"},
            )
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": "Invalid Credentials!"}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        # BLACKLIST.add(jti)
        jwt_redis_blocklist.set(jti, "", ex=timedelta(hours=30))
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.

        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
