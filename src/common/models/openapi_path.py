"""Module contains the class for an OpenAPI endpoint, called a path in OpenAPI
spec parlance."""

import uuid

from sqlalchemy import JSON, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class OpenAPIPath(Base):  # pylint: disable=too-few-public-methods
    """Class for an OpenAPI endpoint, called a path in OpenAPI
    spec parlance."""

    __tablename__ = "openapi_path"

    openapi_path_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    oa_server_id = Column(
        UUID(as_uuid=True),
        ForeignKey("openapi_server.openapi_server_id"),
        nullable=False,
    )
    url_templated = Column(String, nullable=False)
    selection_prompt = Column(Text, nullable=False)
    llm_content_gen_tool_call_spec = Column(JSON)
    # TODO: add embedding pylint: disable=fixme
