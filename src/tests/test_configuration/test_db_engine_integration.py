"""Integration tests for the configuration algorithm"""

from common.database_engine import DBEngine
from configuration.config_algo import config_algo_openapi


def test_config_algo_integration():
    """Integration test that runs the config algorithm"""
    # config_algo_openapi(DBEngine(), "ca754e5d-4f5d-47b6-a06e-e786b8e45b55")
    # Commented out because this is a long-running integration/regression test
    # that must run on the ODU CS VPN, which is not accessible to GitHub runners
