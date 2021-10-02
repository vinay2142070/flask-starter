from flask import Flask, jsonify, make_response
from flask_restful import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
import json
from simplexml import dumps

from blacklist import BLACKLIST
from resources.user import (
    UserRegister,
    User,
    UserLogin,
    TokenRefresh,
    UserLogout,
    SetPassword,
)
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from redis_util import jwt_redis_blocklist
from ma import ma
from marshmallow import ValidationError
from resources.confirmation import Confirmation, ConfirmationByUser
from dotenv import load_dotenv

load_dotenv(".env", verbose=True)
from flask_uploads import configure_uploads  # , patch_request_class
from resources.image import ImageUpload, Image, Avatar, AvatarUpload
from libs.image_helper import IMAGE_SET
from flask_migrate import Migrate
from db import db
from resources.order import Order


from oauth2 import oauth
from resources.github_login import GithubLogin, GithubAuthorize

app = Flask(__name__)


# uri = os.getenv("DATABASE_URL", "sqlite:///data.db")  # or other relevant config var
# if uri.startswith("postgres://"):
#     uri = uri.replace("postgres://", "postgresql://", 1)
# app.config["SQLALCHEMY_DATABASE_URI"] = uri
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["PROPAGATE_EXCEPTIONS"] = True
# app.config["JWT_COOKIE_SECURE"] = False
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=30)
# app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=10)
# app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
# app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
# app.config["JWT_SECRET_KEY"] = os.environ.get("APP_SECRET")
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
db.init_app(
    app
)  # moved outside from __name__==__main__ due to error faced for flask db migrate
api = Api(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# flask uploads
# patch_request_class(app, 2 * 1024 * 1024)  # 10MB upload max
# app.config["MAX_CONTENT_LENGTH"] = 1000
configure_uploads(app, IMAGE_SET)

"""
`claims` are data we choose to attach to each jwt payload
and for each jwt protected endpoint, we can retrieve these claims via `get_jwt_claims()`
one possible use case for claims are access level control, which is shown below.
"""


@jwt.additional_claims_loader
def add_claims_to_jwt(
    identity,
):  # Remember identity is what we define when creating the access token
    if (
        identity == 1
    ):  # instead of hard-coding, we should read from a config file or database to get a list of admins instead
        return {"is_admin": True}
    return {"is_admin": False}


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    print("printed from redis::", token_in_redis)

    return (
        token_in_redis is not None
    )  # Here we blacklist particular JWTs that have been created in the past.


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback(hdr, payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(
    error,
):  # we have to keep the argument here, since it's passed in by the caller internally
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(hdr, payload):
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback(hdr, payload):
    return (
        jsonify(
            {"description": "The token has been revoked.!", "error": "token_revoked"}
        ),
        401,
    )


@app.errorhandler(ValidationError)
def handle_marshmallow_excep(err):
    return jsonify(err.messages), 400


@api.representation("application/json")
def output_json(data, code, headers=None):
    resp = make_response(json.dumps({"response": data}), code)
    resp.headers.extend(headers or {})
    return resp


@api.representation("application/xml")
def output_xml(data, code, headers=None):
    resp = make_response(dumps({"response": data}), code)
    resp.headers.extend(headers or {})
    return resp


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")
api.add_resource(Confirmation, "/user_confirm/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:userid>")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")
api.add_resource(GithubLogin, "/login/github")
api.add_resource(
    GithubAuthorize, "/login/github/authorized", endpoint="github.authorize"
)
api.add_resource(SetPassword, "/user/password")
api.add_resource(Order, "/order")


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    # from run import db

    ma.init_app(app)
    oauth.init_app(app)
    app.run(port=5000)
