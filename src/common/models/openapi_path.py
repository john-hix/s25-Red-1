"""OpenAPI Path object, as defined in the OpenAPI spec. This object stores
the OpenAPI endpoint"""

import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class OpenAPIPath(Base):  # pylint: disable=too-few-public-methods
    """OpenAPI Server object, as defined in the OpenAPI spec."""

    __tablename__ = "openapi_path"

    openapi_path_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spec_id = Column(
        UUID(as_uuid=True), ForeignKey("openapi_spec.openapi_spec_id"), nullable=False
    )
    path_templated = Column(
        String, nullable=False
    )
