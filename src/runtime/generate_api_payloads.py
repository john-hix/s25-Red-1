"""Module to general API payloads"""

import json
import logging
from typing import List

from flask_sqlalchemy import SQLAlchemy
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from numpy import ndarray
from openai import OpenAI
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from sentence_transformers import SentenceTransformer
from werkzeug.exceptions import NotFound

from common.app_config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from common.models.openapi_path import OpenAPIPath
from common.payload import OpenApiPayloadSchema, tool_call_spec_to_payload_json_schema
from common.spacy_util import get_all_sentences


# pylint: disable-next=too-few-public-methods
class CueCodePayloadGenerator:
    """CueCode API payload generation"""

    def __init__(self, db):
        self._db = db
        self._llm_client = OpenAI(
            api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=(5 * 60 * 1000)
        )
        self.llm: ChatOpenAI = init_chat_model(
            LLM_MODEL,
            model_provider="openai",
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
        )

    _db: SQLAlchemy
    _llm_client: OpenAI
    llm: ChatOpenAI

    def operation_tool_call_search(
        self, configuration_id: str, sentence: str
    ) -> tuple[List[dict], dict[str, dict]]:
        """Tool call semantic search for a CueCode configuration"""

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logging.debug("simple_endpoint_search starting embedding for text")
        sentence_list = [sentence]
        embeddings: ndarray = model.encode(sentence_list)
        sentence_embedding = embeddings[0]

        conn = self._db.session.connection().connection
        cursor = conn.cursor()

        cosine_simililarity_search_sql = (
            "SELECT 1 - (selection_prompt_embedding <=> %s) AS cosine_similarity, "
            + " o.openapi_operation_id, "
            + "o.openapi_server_id, openapi_path_id, http_verb, selection_prompt, "
            + "llm_content_gen_tool_call_spec "
            + "FROM openapi_operation_selection_prompt sp "
            + "INNER JOIN openapi_operation as o "
            + "ON sp.openapi_operation_id = o.openapi_operation_id "
            + "INNER JOIN openapi_server as s on s.openapi_server_id = o.openapi_server_id "
            + "WHERE s.spec_id = %s "
            + "ORDER BY 1 - (selection_prompt_embedding <=> %s) desc LIMIT 10;"
        )
        input_vec_string = str(sentence_embedding.tolist()).replace(
            "ARRAY", ""
        )  # Update this.
        cosine_simililarity_search_variables = (
            input_vec_string,
            configuration_id,
            input_vec_string,
        )

        cursor.execute(
            cosine_simililarity_search_sql, cosine_simililarity_search_variables
        )
        results = cursor.fetchall()

        keyed_results = []
        for row in results:
            keyed_results.append(
                {
                    "cosine_similiarity": row[0],
                    "openapi_operation_id": row[1],
                    "openapi_server_id": row[2],
                    "openapi_path_id": row[3],
                    "http_verb": row[4],
                    "selection_prompt": row[5],
                    "llm_content_gen_tool_call_spec": row[6],
                }
            )
        # Map tool call names to database info so further information can
        # be pulled from the DB, should the tool call (Operation) be selected.
        tool_fn_to_operation_info: dict = {}
        for t in keyed_results:
            tool_fn_to_operation_info[
                t["llm_content_gen_tool_call_spec"]["function"]["name"]
            ] = {
                "openapi_path_id": t["openapi_path_id"],
                "http_verb": t["http_verb"],
                "cosine_similiarity": t["cosine_similiarity"],
            }
        return (keyed_results, tool_fn_to_operation_info)

    def _dedupe_function_call_specs(
        self, tools_possible_dupes: List[ChatCompletionToolParam]
    ) -> List[ChatCompletionToolParam]:
        seen = set()
        unique_tool_calls = []

        for t in tools_possible_dupes:
            func_name = t.get("function", {}).get("name")
            if func_name not in seen:
                seen.add(func_name)
                unique_tool_calls.append(t)
        return unique_tool_calls

    def _build_tool_call_list_for_text_input(
        self, configuration_id, text_input
    ) -> tuple[List[ChatCompletionToolParam], dict[str, dict]]:
        tools_possible_dupes: List[ChatCompletionToolParam] = []
        # Since all operations are embedded using one sentence, we split by
        # sentence, the collect all tool calls for all sentences together
        # to let the LLM decide how to use them.
        tool_fn_to_operation_info: dict[str, dict] = {}
        for sentence in get_all_sentences(text_input):
            keyed_results, this_batch_tool_fn_to_operation_info = (
                self.operation_tool_call_search(configuration_id, sentence)
            )
            for operation_tool_call_match in keyed_results:
                # Add tool call to our list for later deduplication
                tools_possible_dupes.append(
                    operation_tool_call_match["llm_content_gen_tool_call_spec"]
                )
                # Add tool call to OpenAPI Operation info mapping, unique for
                # each Operation
                fn_name = operation_tool_call_match["llm_content_gen_tool_call_spec"][
                    "function"
                ]["name"]
                if not tool_fn_to_operation_info.get(fn_name):
                    tool_fn_to_operation_info[fn_name] = (
                        this_batch_tool_fn_to_operation_info[fn_name]
                    )
        tools = self._dedupe_function_call_specs(tools_possible_dupes)

        if len(tools) < 1:
            raise NotFound(
                "LLM could not identify endpoints for input via tool call prompts."
            )

        # print("tools")
        # print(json.dumps(tools, indent=2))
        # print("mapping::===========================================")
        # print(tool_fn_to_operation_info)
        return (tools, tool_fn_to_operation_info)

    def generate_operations(self, configuration_id, text_input) -> List[dict]:
        """Generates OpenAPI operations"""

        tools, tool_fn_to_operation_info = self._build_tool_call_list_for_text_input(
            configuration_id, text_input
        )

        # Two prompts:
        #   1. a one-shot that selects the OpenAPI operations that must be
        #     performed, without regard for the content generated. The purpose
        #     of this prompt is to get a list of tool calls returned that we
        #     will then take over.
        #   2. for each tool call received, prompt again with structured output
        #    constraints.

        # Perform prompt 1:
        tool_call_requests = self._generate_tool_call_requests(text_input, tools)

        if not tool_call_requests:
            raise NotFound(
                "LLM could not identify endpoints for input via tool call prompts."
            )

        # Get ready for prompt 2 calls. Use LangChain for constraining output to the JSON schema
        # each endpoint requires
        payloads: List[dict] = []
        for tool_call_request in tool_call_requests:
            try:
                payloads.append(
                    self._generate_structured_payload(
                        tool_call_request, text_input, tools, tool_fn_to_operation_info
                    )
                )
            except ValueError as e:
                logging.warning("Error professing tool")
                logging.warning(e)

        return payloads

    def _generate_tool_call_requests(
        self, text_input: str, tools: List[ChatCompletionToolParam]
    ):
        """
        Given a list of endpoints from the similarity search, have the LLM pick
        which endpoints to hit.
        """
        # Get ready for prompt 1:
        system_prompt = (
            "You are a helpful assistant. "
            + "You are to create HTTP Web API requests that effect the action described "
            + " by the user's input. The HTTP endpoints you may call are described "
            " as tool calls. To issue an HTTP request, you must use the tool calls provided. "
            " You may not generate the HTTP requests directly; instead, use the tool calls"
            " to accomplish your instructions."
        )
        # Send prompt 1:
        completion = self._llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_input},
            ],
            tools=tools,
            tool_choice="required",
        )
        # print(completion)
        # print(completion.choices[0].message.tool_calls)

        # List of tool call requests
        return completion.choices[0].message.tool_calls

    def _generate_structured_payload(
        self,
        tool_call_request: ChatCompletionMessageToolCall,
        text_input,
        tools,
        tool_fn_to_operation_info: dict[str, dict],
    ) -> OpenApiPayloadSchema:
        # Each OpenAPI operation prompt should have only its matching
        # tool call available.
        this_tool_call_spec = next(
            t for t in tools if t["function"]["name"] == tool_call_request.function.name
        )
        assert this_tool_call_spec is not None
        # Modifications to meet LangChain JSON Schema requirements
        this_json_schema_for_output: OpenApiPayloadSchema = (
            tool_call_spec_to_payload_json_schema(this_tool_call_spec)
        )
        # print("this_json_schema_for_output")
        # print(this_json_schema_for_output)
        this_operation_gen_model = self.llm.bind_tools(
            [this_json_schema_for_output], tool_choice="any"
        )

        # Generate response according to strict JSON Schema defined for
        # this Operation
        structured_llm = this_operation_gen_model.with_structured_output(
            this_json_schema_for_output
        )
        structured_prompt = (
            "You are to create HTTP Web API requests that effect the action described "
            + " by the user's input. Find the action described in the text "
            + " that most closely matches the HTTP endpoint schema provided,"
            + " then generate an API request that conforms to the JSON schema."
            + " The user input is as follows:\n\n"
            + text_input
        )
        response = structured_llm.invoke(structured_prompt)
        print(response)

        # Get the Path associated with this Operation
        operation_info = tool_fn_to_operation_info[
            this_tool_call_spec["function"]["name"]
        ]
        print(operation_info)
        path = self._db.session.get_one(
            OpenAPIPath, str(operation_info["openapi_path_id"])
        )
        http_verb = operation_info["http_verb"]

        # print(type(response))
        # print(response)
        # print(json.dumps(response, indent=2))
        return {
            **response,
            "http_verb": http_verb,
            "path_templated": path.path_templated,
            "tool_call_spec": this_tool_call_spec,
            "sentence_operation_similarity": operation_info["cosine_similiarity"],
            "sentence_matched": "TODO",
        }
