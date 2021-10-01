import pytest
import json
from app import app as flask_app
from flask import jsonify

token = None


@flask_app.route("/ping")
def ping():
    return jsonify(ping="pong")


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index(app, client):
    res = client.get("/ping")
    assert res.status_code == 200
    expected = {"ping": "pong"}
    assert expected == json.loads(res.get_data(as_text=True))


def test_login(app, client):
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    req = {"username": "test", "password": "test"}
    res = client.post("/login", data=json.dumps(req), headers=headers)
    assert res.status_code == 200
    # print(res.get_data())
    res_dict = json.loads(res.get_data(as_text=True))
    assert "access_token" in res_dict
    if "access_token" in res_dict:
        global token
        token = res_dict["access_token"]
