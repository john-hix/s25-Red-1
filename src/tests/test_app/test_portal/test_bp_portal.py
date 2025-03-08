"""Test the Portal blueprint
Fixture code adapted from the following source:
https://flask.palletsprojects.com/en/stable/testing/"""

import pytest
from flask import Flask

# pylint: disable=redefined-outer-name
from hamcrest import assert_that, contains_string, equal_to

# pylint: disable-next=import-error
from app.portal import create_blueprint  # type: ignore


@pytest.fixture()
def app():
    """Build a flask app that does nothing but run our Blueprint"""

    flask_app = Flask(__name__)
    flask_app.register_blueprint(create_blueprint())
    flask_app.config.update({"TESTING": True, "SECRET_KEY": "neededForTheForms"})

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


def test_index(client):
    """Test that the blueprint is registered and serving the index route"""
    response = client.get("/")
    assert_that(response.status_code, equal_to(200))
    assert_that(str(response.data), contains_string(("<html")))


def test_upload_spec(client):
    """Test that the blueprint is registered and serving the index route"""
    response = client.get("/upload-spec")
    assert_that(response.status_code, equal_to(200))
    assert_that(str(response.data), contains_string(("<html")))
