"""Stores CueCode config for any kind of API, since in the RWP CueCode could
worka gainst GraphQL and other API types"""

import uuid

from sqlalchemy import Boolean, Column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, db


class CuecodeConfig(db.Model):
    """Stores CueCode config for any kind of API, since in the RWP CueCode could
    work against GraphQL and other API types"""

    __tablename__ = "cuecode_config"

    cuecode_config_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_is_finished = Column(Boolean)
    is_live = Column(Boolean)
