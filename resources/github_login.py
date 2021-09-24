from oauth2 import github
from flask_restful import Resource
from flask import g, request, url_for
from models.user import UserModel
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)


class GithubLogin(Resource):
    @classmethod
    def get(cls):
        redirect_url = url_for("github.authorize", _external=True)
        print("::::" + redirect_url)
        return github.authorize(callback=redirect_url)


class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        resp = github.authorized_response()
        print("::::")
        print(resp)
        if resp is None or resp.get("access_token") is None:
            return {
                "error": resp["error"],
                "error_description": resp["error_description"],
            }

        g.access_token = resp["access_token"]

        githubuser = github.get("user/emails")

        for item in githubuser.data:
            if item["primary"] == True and item["verified"] == True:
                githubusername = item["email"]

        # githubusername = githubuser.data["email"]

        user = UserModel.find_by_username(githubusername)
        if not user:
            user = UserModel(
                username=githubusername, email=githubusername, password=None
            )
            user.save_to_db()
        access_token = create_access_token(
            identity=user.id,
            fresh=True,
            additional_claims={"claim": "admin"} if user.id == 2 else {"claim": "user"},
        )
        refresh_token = create_refresh_token(user.id)
        return (
            {"access_token": access_token, "refresh_token": refresh_token},
            200,
        )
