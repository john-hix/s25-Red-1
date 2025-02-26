"""Module for the class that represents the OpenAPI spec and its CueCode config"""

import uuid

from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, db


class OpenAPISpec(db.Model):  # pylint: disable=too-few-public-methods
    """Module for the class that represents the OpenAPI spec and its CueCode config"""

    __tablename__ = "openapi_spec"

    openapi_spec_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spec_text = Column(Text)
    file_name = Column(String)
