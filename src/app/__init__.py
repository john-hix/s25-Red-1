"""Build the Flask app so it can be used by the flask CLI, a production
middleware like Gunicorn, etc."""

import os

from flask import Flask, jsonify, redirect

from common import app_config
from common.app_config import FlaskConfig
from common.models.base import db

from .api.bp_api import create_blueprint as create_api_blueprint
from .portal.bp_portal import create_blueprint as create_portal_blueprint


def create_app():
    """create and configure the app"""

    app = Flask(__name__)
    app.config.from_object(FlaskConfig())

    app.config["SQLALCHEMY_DATABASE_URI"] = app_config.SQLALCHEMY_DATABASE_URI
    db.init_app(app)

    # Apply blueprints
    # https://flask.palletsprojects.com/en/stable/blueprints/
    portal_bp = create_portal_blueprint()
    app.register_blueprint(portal_bp, url_prefix="/portal")

    api_bp = create_api_blueprint()
    app.register_blueprint(api_bp, url_prefix="/api")

    # health check endpoint
    @app.route("/health-check", methods=["GET"])
    def health():
        return jsonify(
            {
                "status": "UP",
                "database": "UP - [To be worked upon]",  # TODO: add database health pylint: disable=fixme
            }
        )

    @app.route("/")
    def index():
        """If the user visits the root path, redirect them to the Portal"""
        return redirect("/portal")

    return app
