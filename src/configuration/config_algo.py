"""The main driver for the CueCode configuration algorithm"""

from uuid import UUID

from common.database_engine import DBEngine
from common.models.openapi_spec import OpenAPISpec
from configuration.openapi_operation_embedding import (
    create_operation_prompt_embeddings_not_resumable,
)
from configuration.openapi_schema_adapter import OpenAPISchemaAdapter
from configuration.openapi_schema_validate import validate_openapi_spec
from configuration.openapi_spec_entity_collection import OpenAPISpecEntityCollection
from configuration.openapi_validator_to_cuecode import (
    openapi_spec_validator_to_cuecode_config,
)

from .openapi import OpenAPIObject

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
    db_spec = session.get(OpenAPISpec, openapi_spec_id)

    # Ensure the text spec is a valid OpenAPI specification as such, apart any
    # knowledge of CueCode's requirements for OpenAPI spec structure.
    validate_openapi_spec(db_spec)

    # Prepare the spec text for CueCode's parsing and validation, since
    # CueCode constrains some OpenAPI options and also provides extensions
    # to the OpenAPI spec
    spec_adapter = OpenAPISchemaAdapter(db_spec)
    spec_json = spec_adapter.get_cleaned_json_dict()

    # Parse the OpenAPI specification
    parsed_spec = from_formatted_json(UUID(openapi_spec_id), spec_json)

    # Pull from the parsed spec all SQLAlchemy entities represented in the spec
    # pylint: disable-next=unused-variable
    spec_entities: OpenAPISpecEntityCollection = (
        openapi_spec_validator_to_cuecode_config(session, parsed_spec, db_spec)
    )

    session.add(db_spec)

    # Later, we might want to make the embedding resumable because it takes so long.
    create_operation_prompt_embeddings_not_resumable(db_spec, session)
    session.commit()

    # NOTE The comments below describe the config algo from the Activity Diagram
    # in our Design docs, but it does NOT really follow how the code will be
    # structured if using OOP! A TODO is to clean up these comments in prep for
    # using the output of validator_to_entity_collection().

    # parallel over Schema Object

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

    # print(openapi_spec)

    # BEGIN Chase's work

    # Needed in the event no server is specified in the servers array


def from_formatted_json(spec_id: UUID, data: dict):
    """create openapi object from json"""
    return OpenAPIObject(
        openapi_spec_uuid=spec_id, base_url=data["servers"][0]["url"], **data
    )
