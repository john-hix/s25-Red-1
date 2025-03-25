"""Module for OpenAPIValidatorToSpecEntitiesMapper"""

import uuid

from sqlalchemy.orm import scoped_session

from common.models.openapi_operation import OpenAPIOperation
from common.models.openapi_path import OpenAPIPath
from common.models.openapi_server import OpenAPIServer
from common.models.openapi_spec import OpenAPISpec
from configuration.openapi import OpenAPIObject, OperationObject, PathItemObject
from configuration.openapi_spec_entity_collection import OpenAPISpecEntityCollection
from configuration.openapi_tool_call import make_tool_call_spec


def validator_to_entity_collection(
    session: scoped_session,
    validator: OpenAPIObject,
    db_spec: OpenAPISpec,  # pylint: disable=unused-argument
) -> OpenAPISpecEntityCollection:
    """Map the OpenAPI OpenAPIObject object members to SQLAlchemy entities that are
    relevant to the runtime algorithm

    Guarantees consistent entity relationships.
    """
    openapi_server = OpenAPIServer(
        openapi_server_id=uuid.uuid4(),
        spec_id=db_spec.openapi_spec_id,
        base_url=db_spec.base_url,
    )
    session.add(openapi_server)

    for path_key in validator.paths:
        # Get Path obj
        v_path = validator.paths[path_key]
        path = OpenAPIPath(
            openapi_spec_id=db_spec.openapi_spec_id,
            spec=db_spec,
            path_templated=make_templated_path(path_key),
        )
        session.add(path)
        # Pull only HTTP methods used for data mutation

        operation_info: list[dict[str, OperationObject]] = [
            {"verb": "POST", "op_obj": v_path.post},
            {"verb": "PATCH", "op_obj": v_path.patch},
            {"verb": "PUT", "op_obj": v_path.put},
            {"verb": "DELETE", "op_obj": v_path.delete},
        ]

        for op in operation_info:
            op_obj: OperationObject = op["op_obj"]
            op_post_prompt: str = make_selection_prompt_for_operation(
                path, op_obj, "POST"
            )
            # pylint: disable-next=unused-variable
            op_post_prompt_vector = None
            db_op_post = OpenAPIOperation(
                openapi_path_id=path.openapi_path_id,
                path=path,
                openapi_server_id=openapi_server.openapi_server_id,
                http_verb=op["verb"],
                selection_prompt=op_post_prompt,
                llm_content_gen_tool_call_spec=make_tool_call_spec(
                    path, op_obj, op["verb"]
                ),
            )
            path.operations.append(db_op_post)

        db_spec.paths.append(path)

    return OpenAPISpecEntityCollection()


def make_templated_path(path: str) -> str:
    """Standardize the path string stored"""
    return path


def make_selection_prompt_for_operation(
    path: PathItemObject,  # pylint: disable=unused-argument
    operation_object: OperationObject,  # pylint: disable=unused-argument
    http_verb: str,  # pylint: disable=unused-argument
) -> str:
    """Create a prompt used for the selecting the operation"""
    return ""
