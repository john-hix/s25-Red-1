"""Validator for OpenAPI schema
"""

import os
from uuid import uuid4

from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

from common.models.openapi_spec import OpenAPISpec


def validate_openapi_spec(spec: OpenAPISpec, temp_file_dir="/tmp"):
    """Raises an error if the OpenAPI spec text is not a valid OpenAPI spec."""
    # Build file at /tmp from text in spec.spec_text
    # This is advantageous because we keep the text in the DB
    # and avoid having to have a distributed file system - we only
    # need this temp file on the host (in the container) that our program
    # is running on (in).
    file_name = "cuecode_openapi_spec_" + str(uuid4())
    file_path = os.path.join(temp_file_dir, file_name)

    # Create temp directory if it doesn't exist.
    os.makedirs(temp_file_dir, exist_ok=True)

    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(spec.spec_text)
    spec_tuple = read_from_filename(file_path)
    validate(spec_tuple[0])
