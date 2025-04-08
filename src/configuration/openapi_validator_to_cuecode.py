"""Module for OpenAPIValidatorToSpecEntitiesMapper"""

import logging
import uuid

from sqlalchemy.orm import scoped_session

from common.llm_client import embedding
from common.models.openapi_operation import OpenAPIOperation
from common.models.openapi_path import OpenAPIPath
from common.models.openapi_server import OpenAPIServer
from common.models.openapi_spec import OpenAPISpec
from configuration.openapi import OpenAPIObject, OperationObject
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
            op_prompt: str = make_selection_prompt_for_operation(
                path_key, op_obj, op["verb"]
            )
            # pylint: disable-next=unused-variable
            op_prompt_vector = None
            db_op = OpenAPIOperation(
                openapi_path_id=path.openapi_path_id,
                path=path,
                openapi_server_id=openapi_server.openapi_server_id,
                http_verb=op["verb"],
                selection_prompt=op_prompt,
                llm_content_gen_tool_call_spec=make_tool_call_spec(
                    path, op_obj, op["verb"]
                ),
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
            logging.warning("Calling Ollama")
            vec = embedding(op.selection_prompt)
            op.selection_prompt_embedding = vec
            session.add(op)


def make_templated_path(path: str) -> str:
    """Standardize the path string stored"""
    return path


def make_selection_prompt_for_operation(
    path_str: str,  # pylint: disable=unused-argument
    operation_object: OperationObject,
    http_verb: str,  # pylint: disable=unused-argument
) -> str:
    """Create a prompt used for the selecting the HTTP Operation"""
    desc = ""
    if operation_object:
        if operation_object.x_cuecode_prompt:
            desc = operation_object.x_cuecode_prompt
        else:
            desc = operation_object.description

    prompt = (
        desc
        + ". This is done by applying the HTTP verb "
        + http_verb
        + " to the REST API endpoint with path '"
        + path_str
        + "'."
    )
    return prompt
