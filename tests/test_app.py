# Third party modules
import pytest

# First party modules
from app import app
from db import db
from models.user import UserModel
import json
import tempfile
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models.confirmation import ConfirmationModel


token: str = None
store_id = None
item_name = "chair"


@pytest.fixture(scope="session")
def client():

    app.config["TESTING"] = True
    app.testing = True

    # This creates an in-memory sqlite db
    # See https://martin-thoma.com/sql-connection-strings/
    db_fd, db_path = tempfile.mkstemp(dir=os.environ["PYTHONPATH"])
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    client = app.test_client()
    with app.app_context():
        db.create_all()
        author1 = UserModel(
            id=1,
            username="foo",
            password=generate_password_hash("bar"),
            email="test@gmail.com",
        )
        confirmation = ConfirmationModel(author1.id)
        confirmation.confirmed = True
        db.session.add(author1)
        db.session.add(confirmation)
        db.session.commit()
    yield client
    os.close(db_fd)
    os.unlink(db_path)


def test_login(client):
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    req = {"username": "foo", "password": "bar"}
    res = client.post("/login", data=json.dumps(req), headers=headers)
    assert res.status_code == 200
    # print(res.get_data())
    res_dict = json.loads(res.get_data(as_text=True))
    assert "access_token" in res_dict
    if "access_token" in res_dict:
        global token
        token = res_dict["access_token"]
    # print(token)


def test_store_creation(client):
    store_name = "grocery"
    res = client.post(f"/store/{store_name}")
    assert res.status_code == 201
    # print(res.get_data())
    res_dict = json.loads(res.get_data(as_text=True))
    assert res_dict["id"] is not None
    assert store_name == res_dict["name"]
    global store_id
    store_id = res_dict["id"]


def test_item_creation(client):
    mimetype = "application/json"
    headers = {
        "Content-Type": mimetype,
        "Authorization": f"Bearer {token}",
    }
    req = {"store_id": store_id, "price": "50"}
    res = client.post(f"/item/{item_name}", data=json.dumps(req), headers=headers)
    assert res.status_code == 201
    # print(res.get_data())
    res_dict = json.loads(res.get_data(as_text=True))
    assert item_name == res_dict["name"]
    assert store_id == res_dict["store_id"]
    assert res_dict["id"] is not None


def test_get_all_items(client):
    mimetype = "application/json"
    headers = {
        "Content-Type": mimetype,
        "Authorization": f"Bearer {token}",
    }
    res = client.get(f"/items", headers=headers)
    assert res.status_code == 200
    print(res.get_data())
    res_dict = json.loads(res.get_data())
    assert item_name == res_dict["items"][0]["name"]


def test_logout(client):
    mimetype = "application/json"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    res = client.post("/logout", headers=headers)
    assert res.status_code == 200
    print(res.get_data())
    res_dict = json.loads(res.get_data())
    assert "Successfully logged out" == res_dict["message"]
