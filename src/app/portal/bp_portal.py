import os
import uuid

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField

from common.models import CuecodeConfig, OpenAPISpec
from common.models.base import db


class OpenAPISpecUploadForm(FlaskForm):
    spec_file = FileField("Upload OpenAPI Specification")
    submit = SubmitField("Upload")


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

        # pylint: disable-next=fixme
        # TODO: will need to add a decorator and add "context" param once
        # auth is added. The same goes for all handlers.

        return render_template("index.html")

    @portal_bp.route("/upload-spec", methods=["GET", "POST"])
    def upload_spec():
        # Design note: spec upload diagram found at the following link.
        # https://app.diagrams.net/?src=about#G1pe-I-vJEF1rdLu7zXhRyQhJHBGLgtCJX#%7B%22pageId%22%3A%22VpygQNfUVgPvtDY-Q96l%22%7D
        # We hope to avoid using Dramatiq. use a call to ________ function instead.
        form = OpenAPISpecUploadForm()

        if request.method == "POST" and form.validate_on_submit():
            spec_file = form.spec_file.data

            if spec_file:
                filename = secure_filename(spec_file.filename)
                spec_content = spec_file.read().decode(
                    "utf-8"
                )  # Read the content as text

                # Create DB records
                cuecode_config = CuecodeConfig(config_is_finished=False, is_live=False)
                db.session.add(cuecode_config)
                db.session.commit()

                openapi_spec = OpenAPISpec(
                    openapi_spec_id=uuid.uuid4(),
                    spec_text=spec_content,
                    file_name=filename,
                )
                db.session.add(openapi_spec)
                db.session.commit()

                flash("OpenAPI spec uploaded successfully!", "success")
                return redirect(url_for("portal.upload_spec"))

        return render_template("upload_spec.html", form=form)

    return portal_bp
