"""Test harness"""
from common.database_engine import DBEngine
from .config_algo import config_algo_openapi

config_algo_openapi(DBEngine(), "ca754e5d-4f5d-47b6-a06e-e786b8e45b55")
