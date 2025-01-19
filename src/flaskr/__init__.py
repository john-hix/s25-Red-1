"""Build the Flask app so it can be used by the flask CLI, a production
middleware like Gunicorn, etc."""

import os

from flask import Flask


def create_app(test_config=None):
    """create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",  # TODO: get config values like this from environment
        # variables in a structured way.
        DATABASE=os.path.join(
            app.instance_path, "flaskr.sqlite"
        ),  # TODO: update to Postgres
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # TODO: replace with a health check endpoint
    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app
