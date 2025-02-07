"""Configuration for the application, supplied via environment variables
to support 12-factor app methodology"""

import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

DB_HOST = os.getenv("DB_HOST", "not_configured")
DB_PORT = os.getenv("DB_PORT", "not_configured")
DB_USER = os.getenv("DB_USER", "not_configured")
DB_PASSWORD = os.getenv("DB_PASSWORD", "not_configured")
DB_DATABASE = os.getenv("DB_DATABASE", "not_configured")
DB_URI = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@"
    + f"{DB_HOST}:{DB_PORT}/{DB_DATABASE}?application_name=cuecode"
)

SQLALCHEMY_POOL_RECYCLE = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "35"))
SQLALCHEMY_POOL_TIMEOUT = int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "7"))
