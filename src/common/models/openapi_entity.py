"""Class for storing the data objects, called entities, that the CueCode
Config algorithm can detect in an OpenAPI spec."""

import uuid

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class OpenAPIEntity(Base):  # pylint: disable=too-few-public-methods
    """Stores the data objects, called entities, that the CueCode
    Config algorithm can detect in an OpenAPI spec."""

    __tablename__ = "openapi_entity"

    openapi_entity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contained_in_oa_spec_id = Column(
        UUID(as_uuid=True), ForeignKey("openapi_spec.openapi_spec_id"), nullable=False
    )
    noun_prompt = Column(Text, nullable=False)
    # TODO: add embedding pylint: disable=fixme
