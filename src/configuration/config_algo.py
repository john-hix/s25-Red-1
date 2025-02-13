"""The main driver for the CueCode configuration algorithm"""
import subprocess
import jsonref
from uuid import UUID

from common.database_engine import DBEngine
from common.models.openapi_spec import OpenAPISpec
from openapi import OpenAPIObject

from openapi_spec_validator import validate

db_engine_for_workaround = DBEngine()  # would be managed in dramatiq actor code
# if workaround to avoid Dramatiq fails.


def config_algo_openapi(db_engine: DBEngine, openapi_spec_id: str):
    """Runs the CueCode config algo against an OpenAPI spec. This is not the
    Dramatiq actor! If we need to use an actor, define a function that calls this
    one and then decorate the new function as the Dramatiq actor, all under a
    new 'actors' module."""

    db_engine = db_engine_for_workaround
    session = db_engine.get_session()

    openapi_spec = session.get(OpenAPISpec, openapi_spec_id)

    # Update OpenAPI to v3.1, validate spec, and fix empty schemas
    formatted_openapi_spec = format_convert(openapi_spec)

    openapi_repr = OpenAPIObject.from_formatted_json(
        UUID(openapi_spec_id), 
        session, 
        formatted_openapi_spec
    )

    print(openapi_repr)

def fix_empty_schemas(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, dict):
            fix_empty_schemas(v)
        elif k == 'schema' and isinstance(v, list) and not v:
            d[k] = {}
    return d

def fix_broken_security(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, dict):
            fix_broken_security(v)
        elif k == "security" and isinstance(v, list):
            while {} in v:
                v.remove({})
    return d

def format_convert(input: str) -> dict:
    """Format OpenAPI to JSON and convert OpenAPI 3.0 spec to OpenAPI 3.1"""
    
    result = subprocess.run(
        ["node", "../../node_modules/openapi-format-wrapper"],
        input=input, text=True, capture_output=True
    )

    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, 
            ["node", "node_modules/openapi-format-wrapper", 
            result.stdout, result.stderr]
        )


    spec = fix_empty_schemas(jsonref.loads(result.stdout))
    spec = fix_broken_security(spec)

    validate(spec)

    return spec