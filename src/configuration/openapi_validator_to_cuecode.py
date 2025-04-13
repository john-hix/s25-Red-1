"""Module for OpenAPIValidatorToSpecEntitiesMapper"""

import uuid

from sqlalchemy.orm import scoped_session

from common.models.openapi_operation import OpenAPIOperation
from common.models.openapi_path import OpenAPIPath
from common.models.openapi_server import OpenAPIServer
from common.models.openapi_spec import OpenAPISpec
from configuration.openapi import OpenAPIObject, OperationObject
from configuration.openapi_operation_embedding import (
    create_operation_prompts_without_embeddings,
)
from configuration.openapi_spec_entity_collection import OpenAPISpecEntityCollection
from configuration.openapi_tool_call import make_tool_call_spec


def openapi_spec_validator_to_cuecode_config(
    session: scoped_session,
    validator: OpenAPIObject,
    db_spec: OpenAPISpec,  # pylint: disable=unused-argument
) -> OpenAPISpecEntityCollection:
    """Map the OpenAPI OpenAPIObject object members to SQLAlchemy entities that are
    relevant to the runtime algorithm

    Guarantees consistent entity relationships.
    """
    db_spec.base_url = validator.base_url
    session.add(db_spec)

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
            openapi_path_id=uuid.uuid4(),
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
            if not op_obj:
                continue

            # pylint: disable-next=unused-variable
            db_op = OpenAPIOperation(
                openapi_path_id=path.openapi_path_id,
                # path=path,
                openapi_server_id=openapi_server.openapi_server_id,
                http_verb=op["verb"],
                llm_content_gen_tool_call_spec=make_tool_call_spec(
                    path, op_obj, op["verb"]
                ),
            )
            create_operation_prompts_without_embeddings(
                db_op, op["verb"], path, path_key, op_obj, session
            )
            path.operations.append(db_op)

        db_spec.paths.append(path)

    return OpenAPISpecEntityCollection()


def make_templated_path(path: str) -> str:
    """Standardize the path string stored"""
    return path
