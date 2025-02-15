"""Adapter to OpenAPI schema from the spec text to the dictionary format used
in CueCode algorithms. Inspiration and code examples drawn from two sources under
license:
- https://github.com/openai/openai-cookbook/blob/main/examples/Function_calling_with_an_OpenAPI_spec.ipynb # pylint: disable=line-too-long
- https://github.com/python-openapi/openapi-spec-validator?tab=readme-ov-file#python-package

The ODU CS 411W Team Red thanks Sean Baker for finding the OpenAI example.
"""
from jsonref import JsonRef, loads # pylint: disable=import-error
from openapi_spec_validator.readers import read_from_filename
from common.models.openapi_spec import OpenAPISpec

class OpenAPISchemaAdapter():
    """Adapter to OpenAPI schema from the spec text to the dictionary format used
    in CueCode algorithms"""
    def __init__(self, spec: OpenAPISpec):
        self.spec = spec

    def get_dereferencing_json(self) -> JsonRef:
        """Get the spec as a dict, with all JSON references lazily dereferenced
        on access, to allow us to follow the `'$ref'`s in the OpenAPI spec """
        return loads(self.spec.spec_text)
