"""Adapter to OpenAPI schema from the spec text to the dictionary format used
in CueCode algorithms. Inspiration and code examples drawn from two sources under
license:
- https://github.com/openai/openai-cookbook/blob/main/examples/Function_calling_with_an_OpenAPI_spec.ipynb # pylint: disable=line-too-long
- https://github.com/python-openapi/openapi-spec-validator?tab=readme-ov-file#python-package

The ODU CS 411W Team Red thanks Sean Baker for finding the OpenAI example.
"""

from jsonref import JsonRef, loads  # pylint: disable=import-error
from openapi_spec_validator.readers import read_from_filename

from common.models.openapi_spec import OpenAPISpec


class OpenAPISchemaAdapter:
    """Adapter to OpenAPI schema from the spec text to the Pydantic dictionary
    format used in CueCode algorithms"""

    def __init__(self, spec: OpenAPISpec):
        self.spec = spec

    def get_raw_json_dict(self) -> JsonRef:
        """Get the spec as a dict, with all JSON references lazily dereferenced
        on access, to allow us to follow the `'$ref'`s in the OpenAPI spec"""
        return loads(self.spec.spec_text)

    def get_cleaned_json_dict(self) -> JsonRef:
        """Get the preprocessed version of the spec as a dict,
        with all JSON references lazily dereferenced
        on access, to allow us to follow the `'$ref'`s in the OpenAPI spec.

        Preprocessing applies fixes to common, easily corrected CueCode
        compatability problems in OpenAPI specs
        """
        raw = self.get_raw_json_dict()
        cleaned = OpenAPISchemaAdapter._fix_empty_schemas(raw)
        cleaned = OpenAPISchemaAdapter._fix_broken_security(cleaned)
        return cleaned

    @staticmethod
    def _fix_empty_schemas(d: JsonRef) -> JsonRef:
        for k, v in d.items():
            if isinstance(v, JsonRef):
                OpenAPISchemaAdapter._fix_broken_security(v)
            elif k == "schema" and isinstance(v, list) and not v:
                d[k] = {}
        return d

    @staticmethod
    def _fix_broken_security(d: JsonRef) -> JsonRef:
        for k, v in d.items():
            if isinstance(v, JsonRef):
                OpenAPISchemaAdapter._fix_broken_security(v)
            elif k == "security" and isinstance(v, list):
                while {} in v:
                    v.remove({})
        return d
