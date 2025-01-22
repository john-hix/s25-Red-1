""" Common config for the entire CueCode server application"""
import os

VERSION = '0.0.0'

# Flask
# pylint: disable-next=too-few-public-methods
    """Handles getting config from environment variables to pass to the Flask
    application"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    SERVER_NAME  = os.getenv('SERVER_NAME')
    PREFERRED_URL_SCHEME  = os.getenv('PREFERRED_URL_SCHEME', 'http')
