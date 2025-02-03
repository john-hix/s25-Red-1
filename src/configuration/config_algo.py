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

    openapi_spec = session.get(OpenAPISpec, openapi_spec_id)

    print(openapi_spec)
