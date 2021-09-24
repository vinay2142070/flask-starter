from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
import constants
from flask import request
from marshmallow import ValidationError
from models.confirmation import ConfirmationModel
from flask import make_response, render_template
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema
from time import time
from libs.strings import getText

confirmationSchema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": getText("NOT_FOUND")}, 404
        if confirmation.expired():
            return {"message": getText("EXPIRED")}, 400
        if confirmation.confirmed:
            return {"message": getText("ALREADY_CONFIRMED")}, 400
        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, userid: int):
        user = UserModel.find_by_id(userid)
        if not user:
            return {"messsage": getText("USER_NOT_FOUND")}, 404

        return {
            "currentTime": int(time()),
            "confirmations": [
                confirmationSchema.dump(item)
                for item in user.confirmation.order_by(ConfirmationModel.expires_at)
            ],
        }

    @classmethod
    def post(cls, userid: int):
        user = UserModel.find_by_id(userid)
        if not user:
            return {"messsage": getText("USER_NOT_FOUND")}, 404

        try:
            confirmation = user.most_recent_confirmation()
            if confirmation:
                if confirmation.confirmed:
                    return {"message": getText("ALREADY_CONFIRMED")}, 400
                confirmation.force_to_expire()

                new_confirmation = ConfirmationModel(userid)
                new_confirmation.save_to_db()
                user.sendEmail()
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": getText("RESEND_FAILED")}, 500

