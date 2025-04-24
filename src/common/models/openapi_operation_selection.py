"""Module contains the class for an OpenAPI endpoint operation, called an 
Operation Object in OpenAPI spec parlance."""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.models.openapi_operation import OpenAPIOperation

from .base import Base


class OpenAPIOperationSelectionPrompt(Base):  # pylint: disable=too-few-public-methods
    """For selecting an OpenAPI Operation"""

    __tablename__ = "openapi_operation_selection_prompt"

    openapi_operation_selection_prompt_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    openapi_operation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("openapi_operation.openapi_operation_id"),
        default=uuid.uuid4,
        nullable=False,
    )

    selection_prompt = Column(Text, nullable=False)
    selection_prompt_embedding = mapped_column(Vector(384))

    openapi_operation: Mapped["OpenAPIOperation"] = relationship(  # type: ignore
        "OpenAPIOperation", back_populates="selection_prompts"
    )
