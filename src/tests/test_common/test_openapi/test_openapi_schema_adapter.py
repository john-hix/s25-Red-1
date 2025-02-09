"""Unit and integration tests for OpenAPISchemaAdapter"""
import os
from hamcrest import assert_that, equal_to
from jsonref import JsonRef #pylint: disable = import-error
from common.models.openapi_spec import OpenAPISpec
from common.openapi.openapi_schema_adapter import OpenAPISchemaAdapter

def test_integration_json_ref_dict():
    """Test the json ref"""
    with open(os.path.join("src", "tests", "fixtures", "openapi", "nextcloud-v27.json"),
              "r", encoding="UTF-8") as f:
        spec: OpenAPISpec = OpenAPISpec() # type: ignore
        spec.spec_text = f.read()

        adapter_under_test: OpenAPISchemaAdapter = OpenAPISchemaAdapter(spec) # type: ignore
        json: JsonRef = adapter_under_test.get_dereferencing_json() # type: ignore
        # Index into a referenced object and confirm that works.
        assert_that(True,
                    equal_to(json["paths"]["/ocs/v2.php/core/getapppassword"]["get"]
                             ["responses"]["200"]["content"]["application/json"]
                             ["schema"]["properties"]["ocs"]["properties"]["meta"] # "meta" is the dereferenced key
                             ["properties"]["itemsperpage"]["type"] == "string"))
