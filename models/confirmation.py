from db import db
from typing import List
from uuid import uuid4
from time import time

CONFIRMATION_EXPIRY_DELTA = 1800  # 30mins


class ConfirmationModel(db.Model):

    __tablename__ = "confirmations"

    id = db.Column(db.String(80), primary_key=True)
    expires_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, userid: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = userid
        self.id = uuid4().hex
        self.confirmed = False
        self.expires_at = int(time()) + CONFIRMATION_EXPIRY_DELTA

    @classmethod
    def find_by_id(cls, id: str) -> "ConfirmationModel":
        return cls.query.filter_by(id=id).first()

    def expired(self):
        return time() > self.expires_at

    def force_to_expire(self) -> None:
        if not self.expired():
            self.expires_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

