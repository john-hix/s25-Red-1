"""Module contains the class for an OpenAPI endpoint operation, called an 
Operation Object in OpenAPI spec parlance."""

import enum
import uuid

from sqlalchemy import JSON, Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


# Are these the only operations we plan to support?
class HttpVerb(enum.Enum):
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",


class OpenAPIOperation(Base):  # pylint: disable=too-few-public-methods
    """Class for an OpenAPI endpoint, called a path in OpenAPI
    spec parlance."""

    __tablename__ = "openapi_operation"

    openapi_operation_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # An operation can belong to a list of servers, and is said to be defined
    # for each of those servers
    # As a constraint for CueCode, there must be exactly one server per path.
    oa_server_id = Column(
        UUID(as_uuid=True),
        ForeignKey("openapi_server.openapi_server_id"),
        nullable=False,
    )
    oa_path_id = Column(
        UUID(as_uuid=True), ForeignKey("openapi_path.openapi_path_id"), nullable=False
    )

    http_verb: Column = Column(Enum(HttpVerb), nullable=False)

    selection_prompt = Column(Text, nullable=False)
    llm_content_gen_tool_call_spec = Column(JSON)
    # TODO: add embedding pylint: disable=fixme
