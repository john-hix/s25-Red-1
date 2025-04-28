import json

from langchain.chat_models import init_chat_model

from common.app_config import LLM_BASE_URL, LLM_MODEL

llm = init_chat_model(
    LLM_MODEL, model_provider="openai", base_url=LLM_BASE_URL, api_key="sdf"
)

llm.bind_tools([], "any")


json_schema = {
    "title": "joke",
    "description": "Joke to tell user.",
    "type": "object",
    "properties": {
        "setup": {
            "type": "string",
            "description": "The setup of the joke",
        },
        "punchline": {
            "type": "string",
            "description": "The punchline to the joke",
        },
        "rating": {
            "type": "integer",
            "description": "How funny the joke is, from 1 to 10",
            "default": None,
        },
    },
    "required": ["setup", "punchline"],
}
structured_llm = llm.with_structured_output(json_schema)

response = structured_llm.invoke("Tell me a joke about cats")

print(type(response))
print(response)
print(json.dumps(response, indent=2))
