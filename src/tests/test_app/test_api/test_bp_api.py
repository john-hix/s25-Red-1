"""Test the API blueprint
Fixture code adapted from the following source:
https://flask.palletsprojects.com/en/stable/testing/
"""

import pytest
from flask import Flask

# pylint: disable=redefined-outer-name
from hamcrest import assert_that, contains_string, equal_to

# pylint: disable-next=import-error
from app.api import create_blueprint  # type: ignore

API_KEY = "TEST_API_KEY"


@pytest.fixture()
def app():
    """Build a flask app that does nothing but run our Blueprint"""

    flask_app = Flask(__name__)
    flask_app.register_blueprint(create_blueprint(db=None))
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here,
    # such as setting up Postgres

    yield flask_app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    """HTTP client for tests"""
    return app.test_client()


@pytest.fixture()
def runner(app):
    """Run the tests"""
    return app.test_cli_runner()


def test_index_unauthorized(client):
    """Test that accessing `/` without an API key returns 401 error"""
    response = client.get("/")
    assert_that(response.status_code, equal_to(401))
    assert_that(response.json, equal_to({"error": "Unauthorized"}))


def test_index_authorized(client):
    """Test that accessing `/` with a valid API key returns success"""
    response = client.get("/", headers={"Authorization": API_KEY})
    assert_that(response.status_code, equal_to(200))
    assert_that(response.content_type, equal_to("application/json"))
    assert_that(response.json, equal_to({"example": "JSON"}))


def test_not_found(client):
    """Test a route not found"""
    response = client.get("/walruses")
    assert_that(response.content_type, equal_to("application/json"))
