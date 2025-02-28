from configuration import config_algo
from configuration.openapi import OpenAPIObject
from uuid import uuid4
from unittest.mock import MagicMock
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
import jsonref
import os
import shutil
from pathlib import Path
from src_dir import get_src_dir

dummy_session = MagicMock(spec=Session)

mock_sessionmaker = MagicMock(spec=sessionmaker)
mock_sessionmaker.return_value = dummy_session

dummy_scoped_session: scoped_session = scoped_session(mock_sessionmaker)

def test_configuration():
    regression_test_dir = get_src_dir() / "tests" / "test_configuration" / "regression"
    output_dir = regression_test_dir / "test_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir.__str__)
    input_file = regression_test_dir.parent / "data" / "nextcloud-31.json"
    with input_file.open() as file:
        openapi_spec = file.read()
        formatted_openapi_spec = config_algo.fix_empty_schemas(jsonref.loads(openapi_spec))
        formatted_openapi_spec = config_algo.fix_broken_security(formatted_openapi_spec)
        openapi = OpenAPIObject.from_formatted_json(
            uuid4(),
            dummy_scoped_session,
            "https://example.com/",
            formatted_openapi_spec,
            True
        )

    # TODO: Validate results are correct automatically

    