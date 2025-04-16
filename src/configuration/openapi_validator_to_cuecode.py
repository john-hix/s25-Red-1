"""Module for OpenAPIValidatorToSpecEntitiesMapper"""

import uuid
from urllib.parse import urlparse

import jsonref
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


class CueCodeOpenAPIConstraintError(ValueError):
    pass


def build_and_add_server_from_spec(
    validator: OpenAPIObject, db_spec: OpenAPISpec, session: scoped_session
) -> OpenAPIServer:
    """Builds the OpenAPI server model instance and raises an exception if the spec
    does not meet CueCode's constraints on OpenAPI spec structure with
    respect to Servers."""

    if len(validator.servers) > 1 or len(validator.servers) < 1:
        raise CueCodeOpenAPIConstraintError(
            "CueCode accepts 1 and only 1 OpenAPI server. "
            + f"You have supplied {len(validator.servers)}"
        )

    validator_server = validator.servers[0]

    if not urlparse(validator_server.url):
        raise CueCodeOpenAPIConstraintError(
            f"OpenAPI server URL {validator_server.url} is not a fully qualified URL."
        )

    openapi_server = OpenAPIServer(
        openapi_server_id=uuid.uuid4(),
        spec_id=db_spec.openapi_spec_id,
        base_url=validator_server.url,
    )
    session.add(openapi_server)
    return openapi_server


def openapi_spec_validator_to_cuecode_config(
    session: scoped_session,
    validator: OpenAPIObject,
    db_spec: OpenAPISpec,  # pylint: disable=unused-argument
) -> OpenAPISpecEntityCollection:
    """Map the OpenAPI OpenAPIObject object members to SQLAlchemy entities that are
    relevant to the runtime algorithm

    Guarantees consistent entity relationships.
    """

    openapi_server = build_and_add_server_from_spec(
        validator=validator, db_spec=db_spec, session=session
    )

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

            tool_call_spec = jsonref.replace_refs(
                make_tool_call_spec(
                    path_name=path_key, operation_object=op_obj, http_verb=op["verb"]
                )
            )
            print(type(tool_call_spec))  # DEBUG

            db_op = OpenAPIOperation(
                openapi_path_id=path.openapi_path_id,
                # path=path,
                openapi_server_id=openapi_server.openapi_server_id,
                http_verb=op["verb"],
                llm_content_gen_tool_call_spec=tool_call_spec,
            )
            create_operation_prompts_without_embeddings(
                db_op, op["verb"], path, path_key, op_obj, session
            )
            path.operations.append(db_op)

        db_spec.paths.append(path)

    return OpenAPISpecEntityCollection()


def create_selection_embeddings(db_spec: OpenAPISpec, session: scoped_session):
    """Begin the long process of embedding each OpenAPI operation's selection prompt"""
    for path in db_spec.paths:
        for op in path.operations:
            # When LiteLLM outage is over, use/modify this:
            # res = llm_client.embeddings.create(
            #     input=op.selection_prompt, model=LLM_MODEL
            # )
            # vec = embedding(op.selection_prompt)
            # op.selection_prompt_embedding = vec
            session.add(op)


def make_templated_path(path: str) -> str:
    """Standardize the path string stored"""
    return path
