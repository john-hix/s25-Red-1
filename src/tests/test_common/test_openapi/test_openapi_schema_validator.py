"""Test the validation function for OpenAPI specs"""

import os

from common.models.openapi_spec import OpenAPISpec
from common.openapi.openapi_schema_validate import validate_openapi_spec


def test_valid_spec_does_not_throw_pet_store():
    """Tests if a valid OpenAPI spec will throw an error."""
    spec_text = ""
    with open(
        os.path.join("src", "tests", "fixtures", "openapi", "pet-store.json"),
        "r",
        encoding="utf-8",
    ) as f:
        spec_text = f.read()

    spec: OpenAPISpec = OpenAPISpec(spec_text=spec_text)  # type: ignore
    validate_openapi_spec(spec, "./tmp")


# TODO: Commented out because the Nextcloud spec fails validation. Seeking insight pylint: disable=fixme
# on whether Nextcloud spec can be fixed.
# def test_valid_spec_does_not_throw_nextcloud():
#     """Tests if a valid OpenAPI spec will throw an error."""
#     spec_text = ""
#     with open(os.path.join("src", "tests", "fixtures", "openapi", "nextcloud-v27.json"),
#               "r", encoding="utf-8") as f:
#         spec_text = f.read()

#     spec: OpenAPISpec = OpenAPISpec(spec_text=spec_text) # type: ignore
#     validate_openapi_spec(spec, "./tmp")
