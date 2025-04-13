"""Module contains the class for an OpenAPI endpoint operation, called an 
Operation Object in OpenAPI spec parlance."""

import enum
import uuid
from typing import List

from sqlalchemy import JSON, Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from .base import Base


# Are these the only operations we plan to support?
class HttpVerb(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


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
    openapi_server_id = Column(
        UUID(as_uuid=True),
        ForeignKey("openapi_server.openapi_server_id"),
        nullable=False,
    )
    openapi_path_id = Column(
        UUID(as_uuid=True), ForeignKey("openapi_path.openapi_path_id"), nullable=False
    )

    http_verb: Column = Column(Enum(HttpVerb), nullable=False)

    llm_content_gen_tool_call_spec = Column(JSON)

    # path: Mapped["OpenAPIPath"] = relationship("OpenAPIPath", back_populates="operations", foreign_keys="[OpenAPIOperation.openapi_path_id]")  # type: ignore
    selection_prompts: Mapped[List["OpenAPIOperationSelectionPrompt"]] = relationship(  # type: ignore
        "OpenAPIOperationSelectionPrompt",
        back_populates="openapi_operation",
    )

    server: Mapped["OpenAPIServer"] = relationship(
        "OpenAPIServer", back_populates="operations"
    )

    path: Mapped["OpenAPIPath"] = relationship(
        "OpenAPIPath", back_populates="operations"
    )
