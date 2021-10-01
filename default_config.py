import os
from datetime import timedelta

DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
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
UPLOADED_IMAGES_DEST = os.path.join("static", "images")
MAX_CONTENT_LENGTH = int(os.environ["MAX_CONTENT_LENGTH"])
