"""Module to general API payloads"""

import json
import logging
from typing import List

from flask_sqlalchemy import SQLAlchemy
from langchain.chat_models import init_chat_model
from numpy import ndarray
from openai import OpenAI
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from sentence_transformers import SentenceTransformer
from werkzeug.exceptions import NotFound

from common.app_config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
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

    _db: SQLAlchemy
    _llm_client: OpenAI

    def operation_tool_call_search(
        self, configuration_id: str, sentence: str
    ) -> List[dict]:
        """Tool call semantic search for a CueCode configuration"""

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logging.debug("simple_endpoint_search starting embedding for text")
        sentence_list = [sentence]
        embeddings: ndarray = model.encode(sentence_list)
        sentence_embedding = embeddings[0]

        # Use config instead
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
        return keyed_results

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
    ) -> List[ChatCompletionToolParam]:
        tools_possible_dupes: List[ChatCompletionToolParam] = []
        # Since all operations are embedded using one sentence, we split by
        # sentence, the collect all tool calls for all sentences together
        # to let the LLM decide how to use them.
        for sentence in get_all_sentences(text_input):
            for operation_tool_call_match in self.operation_tool_call_search(
                configuration_id, sentence
            ):
                tools_possible_dupes.append(
                    operation_tool_call_match["llm_content_gen_tool_call_spec"]
                )

        tools = self._dedupe_function_call_specs(tools_possible_dupes)

        if len(tools) < 1:
            raise NotFound(
                "LLM could not identify endpoints for input via tool call prompts."
            )

        print("tools")
        print(json.dumps(tools, indent=2))
        return tools

    def generate_operations(self, configuration_id, text_input) -> List[dict]:
        """Generates OpenAPI operations"""

        tools = self._build_tool_call_list_for_text_input(configuration_id, text_input)

        # Two prompts:
        #   1. a one-shot that selects the OpenAPI operations that must be
        #     performed, without regard for the content generated. The purpose
        #     of this prompt is to get a list of tool calls returned that we
        #     will then take over.
        #   2. for each tool call received, prompt again with structured output
        #    constraints.
        system_prompt = (
            "You are a helpful assistant. "
            + "You are to create HTTP Web API requests that effect the action described "
            + " by the user's input. The HTTP endpoints you may call are described "
            " as tool calls. To issue an HTTP request, you must use the tool calls provided. "
            " You may not generate the HTTP requests directly; instead, use the tool calls"
            " to accomplish your instructions."
        )

        # print(LLM_BASE_URL)
        # print(LLM_API_KEY)
        # print(LLM_MODEL)

        # This code happens to use OpenAI and LangChain.
        # TODO: Refactor to just LangChain in this method body.
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

        tool_call_requests = completion.choices[0].message.tool_calls

        if not tool_call_requests:
            raise NotFound(
                "LLM could not identify endpoints for input via tool call prompts."
            )

        llm = init_chat_model(
            LLM_MODEL,
            model_provider="openai",
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
        )

        payloads: List[dict] = []
        for tool_call_request in tool_call_requests:
            # Each OpenAPI operation prompt should have only its matching
            # tool call available.
            this_tool_call_spec = next(
                t
                for t in tools
                if t["function"]["name"] == tool_call_request.function.name
            )
            assert this_tool_call_spec is not None
            # Modifications to meet LangChain JSON Schema requirements
            # this_json_schema_for_output: dict = this_tool_call_spec["function"]  # type: ignore
            # this_json_schema_for_output["title"] = this_tool_call_spec["function"][
            #     "name"
            # ]
            this_json_schema_for_output: OpenApiPayloadSchema = (
                tool_call_spec_to_payload_json_schema(this_tool_call_spec)
            )
            # print("this_json_schema_for_output")
            # print(this_json_schema_for_output)
            this_operation_gen_model = llm.bind_tools(
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

            # print(type(response))
            # print(response)
            # print(json.dumps(response, indent=2))
            payloads.append(response)

        return payloads
