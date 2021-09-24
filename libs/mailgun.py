from typing import List
from requests import Response
from flask import request, url_for
import requests
import os


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    @classmethod
    def sendEmail(
        cls, emails: List[str], subject: str, body: str, html: str
    ) -> Response:

        if (
            os.environ.get("MAILGUN_URL") is None
            or os.environ.get("MAILGUN_API_KEY") is None
        ):
            raise MailGunException("mailgun url or api_key cannot be empty")
        response = requests.post(
            os.environ.get("MAILGUN_URL"),
            auth=("api", os.environ.get("MAILGUN_API_KEY")),
            data={
                "from": "Stores API {}".format(os.environ.get("MAILGUN_SENDER")),
                "to": emails,
                "subject": subject,
                "text": body,
                "html": "",
            },
        )
        if response.status_code != 200:
            raise MailGunException("Error in sending user confirmation email")

        return response

