import os
from datetime import timedelta

DEBUG = False
uri = os.environ["DATABASE_URL"]  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URI = uri
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_SECRET_KEY = os.environ["APP_SECRET"]
SECRET_KEY = os.environ["APP_SECRET"]
JWT_ACCESS_TOKEN_EXPIRES = timedelta(
    minutes=int(os.environ["ACCESS_TOKEN_EXPIRY_IN_MINS"])
)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(
    minutes=int(os.environ["ACCESS_TOKEN_EXPIRY_IN_MINS"])
)

