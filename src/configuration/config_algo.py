"""The main driver for the CueCode configuration algorithm"""
from configuration.openapi_parsing import make_oa_servers_from_json
from jsonref import JsonRef #pylint: disable = import-error

from common.database_engine import DBEngine
from common.models.openapi_entity import OpenAPIEntity
from common.models.openapi_path import OpenAPIPath
from common.models.openapi_path import OpenAPIOperation
from common.models.openapi_server import OpenAPIServer
from common.models.openapi_spec import OpenAPISpec
from common.openapi.openapi_schema_adapter import OpenAPISchemaAdapter
import subprocess
from uuid import UUID

from jsonref import JsonRef  # pylint: disable = import-error
import jsonref

from common.database_engine import DBEngine
from common.models.openapi_entity import OpenAPIEntity
from common.models.openapi_path import OpenAPIPath
from common.models.openapi_server import OpenAPIServer
from common.models.openapi_spec import OpenAPISpec
from common.openapi.openapi_schema_adapter import OpenAPISchemaAdapter
from configuration.openapi_parsing import make_oa_servers_from_json

from .openapi import OpenAPIObject

from openapi_spec_validator import validate # This

db_engine_for_workaround = DBEngine()  # would be managed in dramatiq actor code
# if workaround to avoid Dramatiq fails.


def config_algo_openapi(db_engine: DBEngine, openapi_spec_id: str):
    """Runs the CueCode config algo against an OpenAPI spec. This is not the
    Dramatiq actor! If we need to use an actor, define a function that calls this
    one and then decorate the new function as the Dramatiq actor, all under a
    new 'actors' module."""

    db_engine = db_engine_for_workaround
    session = db_engine.get_session()

    # Fetch OpenAPI spec from PostgreSQL
    openapi_spec = session.get(OpenAPISpec, openapi_spec_id)
    spec_adapter = OpenAPISchemaAdapter(openapi_spec)
    spec_json = spec_adapter.get_dereferencing_json()

    # Initialize empty list of openapi_server, openapi_entity, open_api
    oa_servers: list[OpenAPIServer] = []
    oa_entities: list[OpenAPIEntity] = []
    oa_operations: list[OpenAPIOperation] = []

    # Encode each OpenAPI server from JSON spec as an openapi_server database entity
    make_oa_servers_from_json(oa_servers, spec_json)

    # parallel over Schema Object in OpenAPI spec
        # parallel over HTTP verb in Path OpenAPI spec object
            # Schema object has x-cuecode-exclude? Yes then
                # next item in loop
            # Initialize new OpenApiEntity object
            
            # Schema object has x-cuecode-prompt? Yes then
                # Save x-cuecode-prompt to OpenApiEntity .nounPrompt
            # else
                # Save Schema Object name to OpenApiEntity .nounPrompt
            
            # Call Ollama for embedding of nounPrompt

    # parallel over Schema Object in OpenAPI spec

    # UPSERT entity list to PostgreSQL (but do not commit transactinon)

    # Parallel over Path Object in OpenAPI spec
        # Iterate over HTTP verb in Path object
            # Path object has x-cuecode-exclude? Yes then
                # next item in loop
            # Initialize new OpenApiPath object
            # Path object has x-cuecode-prompt? Yes then
                # Save x-cuecode-prompt to OpenApiPath .selectionPrompt
            # else
                # Save Schema Object name to OpenApiPath .selectionPrompt
            # Call Ollama for embedding of selectionPrompt

    # UPSERT endpoint list to PostgreSQL (but do not commit transactinon)

    # Build graph of entity relationships based on $ref pointers in OpenAPI spec

    # UPSERT graph edges to PostgreSQL as openapi_entity_dependency rows

    # Encode OpenAPI Paths and verbs as LLM Tool calls with the .selectionPrompt chosen earlier

    # Build LLM tool call JSON from Path objects and to PostgreSQL
    # do it

    # Update status of config job in DB (user-facing record, not Dramatiq job)

    # Commit PostgreSQL transaction

    # Ack config job queue task

    print(openapi_spec)

    # BEGIN Chase's work
    openapi_spec = session.get(OpenAPISpec, openapi_spec_id)

    #Needed in the event no server is specified in the servers array
    base_server_url = openapi_spec.base_url

    # Update OpenAPI to v3.1, validate spec, and fix empty schemas
    formatted_openapi_spec = format_convert(openapi_spec)

    openapi_repr = OpenAPIObject.from_formatted_json(
        UUID(openapi_spec_id), 
        session,
        base_server_url,
        formatted_openapi_spec
    )

    if not openapi_repr.session_errors_encountered:
        session.commit()

    print(openapi_repr)


def fix_empty_schemas(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, dict):
            fix_empty_schemas(v)
        elif k == "schema" and isinstance(v, list) and not v:
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
        input=input,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            [
                "node",
                "node_modules/openapi-format-wrapper",
                result.stdout,
                result.stderr,
            ],
        )

    spec = fix_empty_schemas(jsonref.loads(result.stdout))
    spec = fix_broken_security(spec)

    validate(spec)

    return spec
