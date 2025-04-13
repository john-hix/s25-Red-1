"""Module for the class that represents the OpenAPI spec and its CueCode config"""

import uuid
from typing import List

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from common.models.openapi_path import OpenAPIPath

from .base import Base


class OpenAPISpec(Base):  # pylint: disable=too-few-public-methods
    """An OpenAPI spec as stored in the CueCode database"""

    __tablename__ = "openapi_spec"

    openapi_spec_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuecode_config_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cuecode_config.cuecode_config_id"),
        nullable=False,
    )
    spec_text = Column(Text)
    file_name = Column(String)
    base_url = Column(String)

    paths: Mapped[List[OpenAPIPath]] = relationship(
        "OpenAPIPath", back_populates="spec"
    )
