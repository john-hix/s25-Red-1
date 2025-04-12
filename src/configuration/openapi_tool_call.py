# pylint: skip-file
from jsonref import JsonRef  # pylint: disable = import-error

from common.models.openapi_path import OpenAPIOperation
from configuration.openapi import OperationObject, PathItemObject, OpenAPIObject, ServerObject
from typing import List

from uuid import UUID, uuid4

def set_tool_call_spec(operation: OpenAPIOperation, operationJson: JsonRef):
    pass

def make_tool_call_spec(
    path_name: str,
    operation_object: OperationObject,
    http_verb: str,
    func_prompt: str,
) -> dict:
    params: dict = {}
    required = []
    if operation_object.parameters is not None:
        for param in operation_object.parameters:

            if param.schema_ is None:
                continue

            param_description = param.x_cuecode_prompt
            if param_description is None:
                param_description = param.description

            param_info: dict = {}
            if param.schema_ is not None:
                param_info = param.schema_

            if param_description is not None:
                param_info["description"] = param_description
            if param.examples is not None:
                param_info["examples"] = param.examples

            param_name = param.in_ + "+" + param.name
            params[param_name] = param_info

            if param.required:
                required.append(param_name)

    props: dict = {**params}
    if operation_object.request_body is not None:
        if operation_object.request_body.required:
            required.append("requestBody")

        one_of: dict = {}

        for k, v in operation_object.request_body.content.items():
            param_info = {}
            if v.schema_ is not None:
                param_info = v.schema_

            one_of[k] = param_info

        request_body: dict = {"requestBody": {"type": "object", "oneOf": one_of}}
        props.update(**request_body)
    out: dict = {}


    out = {
        "type": "function",
        "function": {
            "name": path_name + "+" + http_verb,
            "description": func_prompt,
            "parameters": {
                "type": "object",
                "properties": props,
            },
            "required": required,
        },
    }
    return out

    # def generate_tools(self) -> dict[int, list]:
    #     """generate function calls for the api"""

    #     out: List[dict] = []

    #     out2: defaultdict = defaultdict(list)

    #     server_stack = [self.servers]

    #     for path, path_item in self.paths.items():
    #         if path_item.servers is not None:
    #             server_stack.append(path_item.servers)
    #         if path_item.get is not None:
    #             result = self._gen_func(server_stack[-1], path, path_item.get, "get")
    #             for k, v in result.items():
    #                 out2[k].append(v)
    #         if path_item.post is not None:
    #             result = self._gen_func(server_stack[-1], path, path_item.post, "post")
    #             for k, v in result.items():
    #                 out2[k].append(v)
    #         if path_item.head is not None:
    #             result = self._gen_func(server_stack[-1], path, path_item.head, "head")
    #             for k, v in result.items():
    #                 out2[k].append(v)
    #         if path_item.put is not None:
    #             result = self._gen_func(server_stack[-1], path, path_item.put, "put")
    #             for k, v in result.items():
    #                 out2[k].append(v)
    #         if path_item.patch is not None:
    #             result = self._gen_func(
    #                 server_stack[-1], path, path_item.patch, "patch"
    #             )
    #             for k, v in result.items():
    #                 out2[k].append(v)
    #         if path_item.trace is not None:
    #             result = self._gen_func(
    #                 server_stack[-1], path, path_item.trace, "trace"
    #             )
    #             for k, v in result.items():
    #                 out2[k].append(v)
    #     return out2
