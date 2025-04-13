# pylint: skip-file
from jsonref import JsonRef  # pylint: disable = import-error

from common.models.openapi_operation import OpenAPIOperation
from configuration.openapi import OperationObject, PathItemObject


def set_tool_call_spec(operation: OpenAPIOperation, operationJson: JsonRef):
    pass


def make_tool_call_spec(
    path: PathItemObject, operation_object: OperationObject, http_verb: str
) -> dict:
    return {}

    # @model_validator(mode="wrap")
    # @classmethod
    # def validate_model(cls, values, handler):
    #     if values["servers"] is None or values["servers"].empty():
    #         values["servers"] = [
    #             ServerObject(
    #                 url=values["base_url"],
    #                 description=None,
    #                 variables=None,
    #                 uuid=uuid5(namespace=NAMESPACE_URL, name="/"),
    #                 oas_uuid=id.get(),
    #             )
    #         ]

    #     try:
    #         spec_id = values["openapi_spec_id"]
    #     except KeyError:
    #         raise ValueError(
    #             "openapi_spec_id must be passed first as a `uuid.UUID` object"
    #         )

    #     try:
    #         session = values["db_session"]
    #     except KeyError:
    #         raise ValueError(
    #             "db_session must be passed as the second positional keyword"
    #         )

    #     try:
    #         base_url = values["base_url"]
    #     except KeyError:
    #         raise ValueError("base_url must be passed as the third positional keyword")

    #     id_token = openapi_spec_id.set(values["openapi_spec_uuid"])
    #     config_info[spec_id]["session"] = session
    #     # session_token = context_session.set(values.pop("db_session"))
    #     # tag_uuids_token = context_tag_uuids.set({})
    #     try:
    #         return handler(values)
    #     finally:
    #         # context_session.reset(session_token)
    #         openapi_spec_id.reset(id_token)
    #         # tag_uuids_token.reset(tag_uuids_token)

    # # TODO: Review & test this, high priority
    # @staticmethod
    # def _gen_func(
    #     servers: List[ServerObject],
    #     path: str,
    #     operation: OperationObject,
    #     operation_name: str,
    # ) -> dict:
    #     if operation.servers is not None:
    #         servers = operation.servers

    #     func_name = path + "+" + operation_name
    #     func_description = operation.x_cuecode
    #     if func_description is None:
    #         func_description = operation.description
    #     if func_description is None:
    #         func_description = operation.summary

    #     params: dict = {}
    #     required = []
    #     if operation.parameters is not None:
    #         for param in operation.parameters:

    #             if not isinstance(param, ParameterObjectSchema):
    #                 continue

    #             param_description = param.x_cuecode
    #             if param.description is None:
    #                 param_description = param.description
    #             param_info: dict = {}
    #             if param.schema_ is not None:
    #                 param_info = param.schema_

    #             if param_description is not None:
    #                 param_info["description"] = param_description
    #             if param.examples is not None:
    #                 param_info["examples"] = param.examples

    #             param_name = param.in_ + "/" + param.name
    #             params[param_name] = param_info

    #             if param.required:
    #                 required.append(param_name)

    #     if operation.request_body is not None:
    #         request_body_required = False
    #         if operation.request_body.required:
    #             request_body_required = True
    #             required.append("requestBody")

    #         one_of: dict = {}

    #         for k, v in operation.request_body.content.items():
    #             param_info = {}
    #             if v.schema_ is not None:
    #                 param_info = v.schema_

    #             one_of[k] = param_info

    #         request_body: dict = {"requestBody": {"type": "object", "oneOf": one_of}}

    #     out: dict = {}

    #     if len(servers) > 1:
    #         raise ValueError(
    #             "Per CueCode restrictions, each unique path must have one and only one server"
    #         )

    #     for server in servers:
    #         out[(server.uuid.int, server.url + path)] = {
    #             "type": "function",
    #             "function": {
    #                 "name": server.url + func_name,
    #                 "description": func_description,
    #                 "parameters": {
    #                     "type": "object",
    #                     "properties": {**params, **request_body},
    #                 },
    #                 "required": required,
    #             },
    #         }

    #     return out

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
