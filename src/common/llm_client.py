"""Interface to the litellm server to which we have access for the prototype"""

import logging

import requests  # pylint: disable=unused-import
from ollama import Client

from common.app_config import LLM_API_KEY  # pylint: disable=unused-import
from common.app_config import LLM_BASE_URL  # pylint: disable=unused-import
from common.app_config import LLM_MODEL  # pylint: disable=unused-import

# Temporary Ollama server on John's network during outage of CS Systems group's
# LiteLLM-proxied Ollama server. The client library will need to change once
# using LiteLLM again.

# ollama_client = Client(host="http://192.168.17.7:11434")
logging.warning("LLM API KEY: " + LLM_API_KEY)
ollama_client = Client(
    host="https://chat.cs.odu.edu/ollama",
    headers={"Authorization": "Bearer " + str(LLM_API_KEY)},
)


# def embedding(text) -> dict | None:
#     """Provide the embedding for the text"""
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": "Bearer " + LLM_API_KEY,
#     }

#     json_data = {
#         "model": LLM_MODEL,
#         "input": text,
#     }
#     response = requests.post(
#         f"{LLM_BASE_URL}/embeddings?llama-70b",
#         headers=headers,
#         json=json_data,
#         timeout=6000,
#     )
#     return response.json()


def embedding(text) -> dict | None:
    """Get the embedding for some text"""
    ollama_response = ollama_client.embed(model="llama3.1:8b", input=text)
    return ollama_response.get("embeddings")[0]
