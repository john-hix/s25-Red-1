"""OpenAPI Path object, as defined in the OpenAPI spec. This object stores
the OpenAPI endpoint"""

import uuid
from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from common.models.openapi_operation import OpenAPIOperation

from .base import Base


class OpenAPIPath(Base):  # pylint: disable=too-few-public-methods
    """OpenAPI Server object, as defined in the OpenAPI spec."""

    __tablename__ = "openapi_path"

    openapi_path_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    openapi_spec_id = Column(
        UUID(as_uuid=True), ForeignKey("openapi_spec.openapi_spec_id"), nullable=False
    )
    path_templated = Column(String, nullable=False)
    operations: Mapped[List[OpenAPIOperation]] = relationship(back_populates="path")

    spec: Mapped["OpenAPISpec"] = relationship(back_populates="paths")
