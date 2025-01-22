""" Common config for the entire CueCode server application"""
import os

VERSION = '0.0.0'

# Flask
SECRET_KEY = os.getenv('SECRET_KEY')
SERVER_NAME  = os.getenv('SERVER_NAME')
PREFERRED_URL_SCHEME  = os.getenv('PREFERRED_URL_SCHEME', 'http')
