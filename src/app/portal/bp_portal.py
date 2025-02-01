from flask import Blueprint, render_template


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
        # TODO: add WTForms for spec upload. pylint: disable=fixme
        # Design note: spec upload diagram found at the following link.
        # https://app.diagrams.net/?src=about#G1pe-I-vJEF1rdLu7zXhRyQhJHBGLgtCJX#%7B%22pageId%22%3A%22VpygQNfUVgPvtDY-Q96l%22%7D
        # We hope to avoid using Dramatiq. use a call to ________ function instead.
        return render_template("upload_spec.html")

    return portal_bp
