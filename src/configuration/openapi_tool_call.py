# pylint: skip-file
from typing import List
from uuid import UUID, uuid4

from jsonref import JsonRef  # pylint: disable = import-error

from common.models.openapi_operation import OpenAPIOperation
from common.models.openapi_path import OpenAPIOperation
from configuration.openapi import (
    OpenAPIObject,
    OperationObject,
    PathItemObject,
    ServerObject,
)


def set_tool_call_spec(operation: OpenAPIOperation, operationJson: JsonRef):
    pass


def format_tool_call_identifier(id: str) -> str:
    return id.replace("{", "_").replace("}", "_").replace("/", "-")


def make_tool_call_description_for_operation(
    path_str: str,  # pylint: disable=unused-argument
    operation_object: OperationObject,
    http_verb: str,  # pylint: disable=unused-argument
) -> str:
    """Create a prompt used for the selecting the HTTP Operation"""

    prompt = (
        "Apply the HTTP verb "
        + http_verb
        + " to the REST API endpoint described by: \n"
        + " * Path: "
        + path_str
    )

    if operation_object and operation_object.x_cuecode_prompt:
        prompt += "\n" + " * Summary: " + operation_object.x_cuecode_prompt
        return prompt

    if operation_object.summary:
        prompt += "\n" + " * Summary: " + operation_object.summary
    if operation_object.description:
        prompt += "\n" + " * Description: " + operation_object.description
    return prompt


def _make_parameters_dict(operation_object: OperationObject) -> tuple[dict, List[str]]:
    params: dict = {}
    required_parameter_list = []
    if operation_object.parameters is not None:
        for param in operation_object.parameters:

            if param.schema_ is None:
                continue

            tool_call_param_object: dict = {}

            if param.schema_ is not None:
                tool_call_param_object = param.schema_

            tool_call_param_object["description"] = param.x_cuecode_prompt
            if tool_call_param_object["description"] is None:
                tool_call_param_object["description"] = param.description

            if param.examples is not None:
                tool_call_param_object["examples"] = param.examples
            if param.in_ is not None:
                tool_call_param_object["parameter_location"] = param.in_

            param_name_in_tool_call = param.name + "_in_" + param.in_
            param_name_in_tool_call = format_tool_call_identifier(
                param_name_in_tool_call
            )
            params[param_name_in_tool_call] = tool_call_param_object

            if param.required:
                required_parameter_list.append(param_name_in_tool_call)
    return (params, required_parameter_list)


def _make_tool_call_request_body(
    operation_object: OperationObject,
) -> tuple[dict | None, bool]:
    request_body_is_required = False
    if operation_object.request_body and operation_object.request_body.required:
        request_body_is_required = True
    request_body = None
    if operation_object.request_body:
        request_body = operation_object.request_body.content["application/json"].schema_
    return (
        request_body,
        request_body_is_required,
    )


def remove_none_keys(d) -> dict:
    """Recursively remove keys with None values from a dictionary."""
    if not isinstance(d, dict):
        return d

    cleaned = {}
    for key, value in d.items():
        if isinstance(value, dict):
            nested = remove_none_keys(value)
            cleaned[key] = nested
        elif isinstance(value, list):
            new_list = [
                remove_none_keys(item) if isinstance(item, dict) else item
                for item in value
            ]
            cleaned[key] = new_list  # type: ignore
        elif value is not None:
            cleaned[key] = value
    # Remove keys with value None
    return {k: v for k, v in cleaned.items() if v is not None}


def make_tool_call_spec(
    path_name: str,
    operation_object: OperationObject,
    http_verb: str,
) -> dict:

    func_prompt = make_tool_call_description_for_operation(
        path_name, operation_object, http_verb
    )

    params, required_params_list = _make_parameters_dict(operation_object)
    request_body, request_body_is_required = _make_tool_call_request_body(
        operation_object
    )

    tool_call_props: dict = dict()
    if len(params.keys()) > 0:
        tool_call_props["parameters"] = params
    if request_body and len(request_body.keys()) > 0:
        tool_call_props["requestBody"] = request_body

    required_tool_call_parameter_list = []
    required_tool_call_parameter_list.extend(required_params_list)
    if request_body_is_required:
        required_tool_call_parameter_list.append("requestBody")

    return remove_none_keys(
        {
            "type": "function",
            "function": {
                "name": format_tool_call_identifier(http_verb + "_" + path_name),
                "description": func_prompt,
                "parameters": {
                    "type": "object",
                    "properties": remove_none_keys(tool_call_props),
                },
                "required": required_tool_call_parameter_list,
            },
        }
    )
