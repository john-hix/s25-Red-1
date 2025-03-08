"""Module for OpenAPIValidatorToSpecEntitiesMapper"""

from configuration.openapi import OpenAPIObject
from configuration.openapi_spec_entity_collection import OpenAPISpecEntityCollection


def validator_to_entity_collection(
    validator: OpenAPIObject,
) -> OpenAPISpecEntityCollection:
    """Map the OpenAPI OpenAPIObject object members to SQLAlchemy entities that are
    relevant to the runtime algorithm

    Guarantees consistent entity relationships.

    Does NOT add the SQLAlchemy entities to a database session and therefore
    does not commit them to the database.
    """
    # TODO:
    # Over Operation Object in OpenAPI spec
    # Iterate over HTTP verb in Operation object
    # Operation object has x-cuecode-exclude? Yes then
    #   next item in loop
    # Initialize new OpenApiOperation object
    # Operation object has x-cuecode-prompt? Yes then
    #   Save x-cuecode-prompt to OpenApiOperation .selectionPrompt
    # else
    #   Save Schema Object name to OpenApiOperation .selectionPrompt
    return OpenAPISpecEntityCollection()
