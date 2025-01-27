"""Build the Flask app so it can be used by the flask CLI, a production
middleware like Gunicorn, etc."""

import os

from flask import Flask, jsonify, redirect

from common.server_config import FlaskConfig

from .api.bp_api import create_blueprint as create_api_blueprint
from .portal.bp_portal import create_blueprint as create_portal_blueprint


def create_app():
    """create and configure the app"""

    app = Flask(__name__)
    app.config.from_object(FlaskConfig())

    # Apply blueprints
    # https://flask.palletsprojects.com/en/stable/blueprints/
    portal_bp = create_portal_blueprint()
    app.register_blueprint(portal_bp, url_prefix="/portal")

    api_bp = create_api_blueprint()
    app.register_blueprint(api_bp, url_prefix="/api")

    # pylint: disable-next=fixme
    # TODO: replace with a health check endpoint
    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route("/")
    def index():
        """If the user visits the root path, redirect them to the Portal"""
        return redirect("/portal")

    return app
