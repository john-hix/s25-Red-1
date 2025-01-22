"""Build the Flask app so it can be used by the flask CLI, a production
middleware like Gunicorn, etc."""

import os

from flask import Flask

from common.server_config import FlaskConfig

def create_app():
    """create and configure the app"""
    app = Flask(__name__)

    app.config.from_object(FlaskConfig())

    # TODO: replace with a health check endpoint
    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app
