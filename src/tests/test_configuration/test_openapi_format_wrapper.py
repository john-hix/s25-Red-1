"""Integration test for openapi-format-wrapper node module"""

from configuration.config_algo import format_convert

def test_openapi_format_wrapper() -> None:
    """Test for openapi-format-wrapper"""
    input_file: str = open("data/nextcloud.json", "r").read()
    output_dict: dict = format_convert(input_file)
    assert output_dict["version"].startswith("3.1")

