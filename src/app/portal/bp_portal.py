"""Blueprint for the CueCode Dev Portal"""

import logging
import uuid
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField, PasswordField, StringField, SubmitField

from actors import actor_config_algo_openapi_spec
from common.models import Account, CuecodeConfig, OpenAPISpec
from common.models.base import db


class OpenAPISpecUploadForm(FlaskForm):
    """The form for receiving OpenAPI specification files"""

    spec_file = FileField("Upload OpenAPI Specification")
    submit = SubmitField("Upload")


class LoginForm(FlaskForm):
    """Login form for Developer Poral users"""

    username = StringField("Username (email)")
    password = PasswordField("Password")


def login_required(f):
    """
    function to check if user is logged in in session
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("portal.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def create_blueprint():
    """Build the CueCode developer portal blueprint.
    For the prototype, this is a bare-bones web app used only to upload
    the API spec. Other requirements like login may apply per instruction from
    our professor."""

    portal_bp = Blueprint(
        "portal", __name__, static_folder="static", template_folder="templates"
    )

    @portal_bp.route("/", methods=["GET"])
    def index():
        if "logged_in" in session:
            return redirect(url_for("portal.account"))
        return redirect(url_for("portal.login"))

    @portal_bp.route("/upload-spec", methods=["GET", "POST"])
    def upload_spec():
        # Design note: spec upload diagram found at the following link.
        # https://app.diagrams.net/?src=about#G1pe-I-vJEF1rdLu7zXhRyQhJHBGLgtCJX#%7B%22pageId%22%3A%22VpygQNfUVgPvtDY-Q96l%22%7D
        form = OpenAPISpecUploadForm()

        if request.method == "POST" and form.validate_on_submit():
            spec_file = form.spec_file.data

            if spec_file:
                filename = secure_filename(spec_file.filename)
                spec_content = spec_file.read().decode(
                    "utf-8"
                )  # Read the content as text

                # Create DB records
                cuecode_config = CuecodeConfig(
                    cuecode_config_id=uuid.uuid4(),
                    config_is_finished=False,
                    is_live=False,
                )
                db.session.add(cuecode_config)

                spec_id = uuid.uuid4()
                openapi_spec = OpenAPISpec(
                    openapi_spec_id=spec_id,
                    spec_text=spec_content,
                    file_name=filename,
                    cuecode_config_id=cuecode_config.cuecode_config_id,
                )
                db.session.add(openapi_spec)
                db.session.commit()

                # Publish to queue
                actor_config_algo_openapi_spec.send(str(spec_id))

                flash("OpenAPI spec uploaded successfully!", "success")
                return redirect(url_for("portal.upload_spec"))

        return render_template("upload_spec.html", form=form)

    @portal_bp.route("/login", methods=["GET", "POST"])
    def login():
        # Check if already logged in
        if "logged_in" in session:
            return redirect(url_for("portal.account"))

        next_page = url_for("portal.account")
        if request.args:
            next_page = request.args.get("next", next_page)

        login_failure_message: str | None = None
        form = LoginForm(request.form)
        if request.method == "POST":

            username = form.username.data

            user = (
                db.session.query(Account).where(Account.email == username).one_or_none()
            )
            if (not user) or (
                (not user.password == form.password.data) and user.password
            ):
                login_failure_message = "Incorrect username or password"

            else:
                session["logged_in"] = True
                session["username"] = username
                session["user"] = user
                flash(f"Successful login to {username}", "success")
                logging.info("Logged in user %s", session.get("username", "ERROR"))

                # Redirect user to the initial page they were accessing or default to account page
                return redirect(next_page)

        return render_template(
            "login.html",
            next=next_page,
            form=form,
            login_failure_message=login_failure_message,
        )

    @portal_bp.route("/account")
    @login_required
    def account():
        username = session.get("username", "ERROR")
        return render_template("account.html", username=username)

    @portal_bp.route("/logout")
    @login_required
    def logout():
        """Logs the user out by clearing the session."""
        session.pop("logged_in", None)
        session.pop("username", None)
        flash("Succesfully logged out", "info")
        return redirect(url_for("portal.login"))

    @portal_bp.route("/account/reset", methods=["POST"])
    @login_required
    def reset_password():
        """password reset functionality
        TODO: make password reset work
        """
        flash("Successfully reset password", "info")
        logging.info(
            "Successful password reset for %s", session.get("username", "ERROR")
        )
        return redirect(url_for("portal.account"))

    return portal_bp
