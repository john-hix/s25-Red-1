"""Module for the class that represents the OpenAPI spec and its CueCode config"""

import uuid
from typing import List

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from common.models.openapi_path import OpenAPIPath

from .base import Base


# CREATE TABLE cuecode_account (
#     cuecode_account_id UUID PRIMARY KEY,
#     email VARCHAR(255) NOT NULL UNIQUE,  -- Added UNIQUE constraint
#     display_name VARCHAR(255),
#     password VARCHAR(255) NOT NULL -- Consider using a more secure hashing mechanism
# );
class Account(Base):  # pylint: disable=too-few-public-methods
    """Portal user account"""

    __tablename__ = "cuecode_account"

    cuecode_account_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email = Column(Text)
    display_name = Column(String)
    password = Column(String)
