"""Actors for running the CueCode config algorithm"""

import logging

import dramatiq

from common.database_engine import DBEngine
from configuration.config_algo import config_algo_openapi


@dramatiq.actor
def actor_config_algo_openapi_spec(spec_id: str):
    """Run CueCode config algo on the given OpenAPI spec saved in the DB"""
    logging.info("Processing OpenAPI spec ID %s", spec_id)
    config_algo_openapi(DBEngine(), spec_id)
    logging.info("Finished processing OpenAPI spec ID %s", spec_id)
