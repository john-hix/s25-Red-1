from typing import Literal, NotRequired, Optional, TypedDict

from openai.types.chat.chat_completion_tool_param import (
    ChatCompletionToolParam,
    FunctionDefinition,
)


class OpenApiPayloadSchema(FunctionDefinition):
    title: str


# class OpenApiPayload(TypedDict):
#     title: str


def tool_call_spec_to_payload_json_schema(
    tool_call_spec: ChatCompletionToolParam,
) -> OpenApiPayloadSchema:
    """Convert the tool call spec into a JSON schema suitable for constraining
    LLM output in JSON mode or via Tool calls, using LangChain"""
    json_schema: OpenApiPayloadSchema = {
        "title": tool_call_spec["function"]["name"],
        **(tool_call_spec["function"]),
    }
    return json_schema


# class OpenApiPayload(TypedDict):
#     title: str
#     name: str
#     description: str
#     requestBody: NotRequired[dict]
#     parameters: NotRequired[dict]


# def tool_call_spec_to_payload_json_schema(
#     tool_call_spec: ChatCompletionToolParam,
# ) -> OpenApiPayload:
#     json_schema: OpenApiPayload = {
#         "name": tool_call_spec["function"]["name"],
#         "title": tool_call_spec["function"]["name"],
#         "description": tool_call_spec["function"]["description"],
#     }

#     if tool_call_spec["function"]["parameters"].get("parameters"):
#         json_schema["parameters"] = tool_call_spec["function"]["parameters"][
#             "parameters"
#         ]  # type: ignore

#     if tool_call_spec["function"]["parameters"].get("requestBody"):
#         json_schema["requestBody"] = tool_call_spec["function"]["parameters"][
#             "requestBody"
#         ]  # type: ignore

#         # "parameters": tool_call_spec["function"]["parameters"]["parameters"],
#         # "requestBody": tool_call_spec["function"]["parameters"]["requestBody"],

#     return json_schema
