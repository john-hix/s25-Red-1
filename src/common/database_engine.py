"""Management of SQLAlchemy database engine"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .app_config import DB_URI, SQLALCHEMY_POOL_RECYCLE, SQLALCHEMY_POOL_TIMEOUT

# See https://docs.sqlalchemy.org/en/20/core/pooling.html#dealing-with-disconnects
# on how the pre_pool_ping prevents errors.

# TODO: Flask SQLALchemy configuration function. pylint: disable=fixme


class DBEngine:  # pylint: disable=too-few-public-methods
    """Wrapper class for use in Dramatiq worker processes, not tied to
    Flask and does not instantiate connections by importing this module; must
    create a class instance first, which is good because this code will
    be imported by both the Flask app container code and the Dramatiq worker
    container code."""

    def __init__(self):
        self.engine = create_engine(
            DB_URI,
            pool_pre_ping=True,
            pool_recycle=SQLALCHEMY_POOL_RECYCLE,
            pool_timeout=SQLALCHEMY_POOL_TIMEOUT,
        )

    def get_session(self) -> scoped_session:
        """Get a SQLALchemy session from the DB engine"""
        session_factory = sessionmaker(self.engine)
        return scoped_session(session_factory)
