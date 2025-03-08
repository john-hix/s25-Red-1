"""Module for OpenAPISpecEntityCollection"""

from sqlalchemy.orm import scoped_session

from common.models.openapi_entity import OpenAPIEntity
from common.models.openapi_operation import OpenAPIOperation
from common.models.openapi_server import OpenAPIServer


# pylint: disable-next=too-few-public-methods
class OpenAPISpecEntityCollection:
    """A collection of all OpenAPI SQLAlchemy model objects associated with
    one OpenAPI specification, as parsed by @class OpenAPIObject"""

    oa_servers: list[OpenAPIServer] = []
    oa_entities: list[OpenAPIEntity] = []
    oa_operations: list[OpenAPIOperation] = []

    def session_add(self, session: scoped_session):
        """Add all entities to the passed database session"""
        # TODO: implement OpenAPISpecEntityCollection.session_add()
