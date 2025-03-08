"""Base class for SQLAlchemy active record style classes"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base

Base = declarative_base()
db = SQLAlchemy()
