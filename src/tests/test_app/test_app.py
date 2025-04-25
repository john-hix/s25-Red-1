"""Test the main Flask app
Fixture code adapted from the following source:
https://flask.palletsprojects.com/en/stable/testing/"""

import pytest

# pylint: disable=redefined-outer-name
from hamcrest import assert_that, contains_string, equal_to

# pylint: disable-next=import-error
from app import create_app  # type: ignore

API_KEY = "TEST_API_KEY"


@pytest.fixture()
def app():
    """Create the entire Flask application"""
    flask_app = create_app()
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


def test_health_check_endpoint(client):
    """Test that the blueprint is registered and serving the index route"""
    response = client.get("/health-check")
    print(response.content_type)
    assert_that(response.content_type, equal_to("application/json"))
    assert_that(response.status_code, equal_to(200))
    assert_that(str(response.data), contains_string(("{")))


def test_portal_index_existence(client):
    """Test that the blueprint is registered and serving the index route"""
    response = client.get("/portal/")
    assert_that(response.status_code, equal_to(302))
    assert_that(str(response.data), contains_string(("<html")))


def test_upload_spec_existence(client):
    """Test that the blueprint is registered and serving the index route"""
    response = client.get("/portal/upload-spec")
    assert_that(response.status_code, equal_to(200))
    assert_that(str(response.data), contains_string(("<html")))


def test_app_index_redirect_to_portal_index(client):
    """Ensure the index route on the main app redirects to the portal index"""
    response_no_follow = client.get("/")
    assert_that(response_no_follow.status_code, equal_to(302))

    response_followed = client.get("/", follow_redirects=True)
    # Check that there was one redirect response.
    assert_that(len(response_followed.history), equal_to(3))
    # Check that the second request was to the index page.
    assert_that(response_followed.request.path, equal_to("/portal/login"))


def test_api_index(client):
    """Test that the blueprint is registered and serving the index route"""
    response = client.get("/api/", headers={"Authorization": API_KEY})
    print(response.content_type)
    assert_that(response.content_type, equal_to("application/json"))
    assert_that(response.status_code, equal_to(200))
    assert_that(str(response.data), contains_string(("{")))


def test_api_not_found_is_json(client):
    """Test a route not found"""
    response = client.get("/api/walruses")
    assert_that(response.content_type, equal_to("application/json"))
