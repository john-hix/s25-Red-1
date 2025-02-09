"""The main driver for the CueCode configuration algorithm"""

from common.database_engine import DBEngine
from common.models.openapi_spec import OpenAPISpec

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

    # Initialize empty list of openapi_server, openapi_entity, open_api

    # Encode each OpenAPI server from YAML as an openapi_server database entity

    # parallel over Schema Object in OpenAPI spec
        # parallel over HTTP verb in Path OpenAPI spec object    
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

    # Update status of config job in DB (user-facing record, not Dramatiq job)

    # Commit PostgreSQL transaction

    # Ack config job queue task

    print(openapi_spec)
