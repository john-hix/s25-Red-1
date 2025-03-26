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
SQLALCHEMY_DATABASE_URI = DB_URI

LLM_BASE_URL = str(os.getenv("LLM_BASE_URL"))
LLM_API_KEY = str(os.getenv("LLM_API_KEY"))
LLM_MODEL = str(os.getenv("LLM_MODEL"))


# Flask
# pylint: disable-next=too-few-public-methods
class FlaskConfig:
    """Handles getting config from environment variables to pass to the Flask
    application"""

    SERVER_NAME = os.getenv("SERVER_NAME")
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "http")
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", "testing")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
