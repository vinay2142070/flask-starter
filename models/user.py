from db import db
from typing import Dict, List, Union
from flask import request, url_for
import requests
from requests import Response
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel
from time import time


userJSON = Dict[str, Union[int, str]]


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(1024))
    registeredAt = db.Column(db.Integer)

    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all,delete-orphan"
    )

    def most_recent_confirmation(self):
        return self.confirmation.order_by(db.desc(ConfirmationModel.expires_at)).first()

    # def json(self) -> userJSON:
    #     return {"id": self.id, "username": self.username}

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_usermailid(cls, mailid: str) -> "UserModel":
        return cls.query.filter_by(email=mailid).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def sendEmail(self):
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation().id
        )
        text = f"please click on the {link} to activate your account"
        html = f"<html><body><h1>please click on the link <a href={link}>link to activate your account</a></h1><body></html>"
        return Mailgun.sendEmail(self.email, "Registration for Stores API", text, html)

    def __str__(self):
        return str(self.id) + self.username + self.email + str(self.registeredAt)
