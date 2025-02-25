"""Flask Blueprint for the Web API that runs the CueCode runtime algorithm"""
from functools import wraps

from flask import Blueprint, jsonify, request

API_KEY = "TEST_API_KEY"


def authenticate(f):
    """Decorator to enforce API key authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


def create_blueprint():
    """Flask Blueprint for the Web API that runs the CueCode runtime algorithm"""

    api_bp = Blueprint("api/v0", __name__)

    @api_bp.errorhandler(404)
    def not_found():
        return jsonify({"error": "Not Found"}), 404

    @api_bp.route("/")
    @authenticate
    def index():

        # pylint: disable-next=fixme
        # TODO: decorator for API key session handling.
        return jsonify({"example": "JSON"})

    # Recommended Blueprint 404 handling from Flask Docs
    # (https://flask.palletsprojects.com/en/stable/blueprints/#blueprint-error-handlers)
    # does not work, so we add a catch-all handler.
    # The answer at https://stackoverflow.com/a/39770599
    # confirms this approach.
    @api_bp.route("/<path:path>")
    def endpoint_not_round(path):  # pylint: disable=unused-argument
        return jsonify({"error": "Endpoint not found."})

    return api_bp
