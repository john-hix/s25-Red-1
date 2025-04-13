"""Module to general API payloads"""

import logging

import psycopg2
from numpy import ndarray
from sentence_transformers import SentenceTransformer


def simple_endpoint_search(configuration_id: str, sentence: str):
    """Example of the similarity search"""

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    logging.debug("simple_endpoint_search starting embedding for text")
    sentence_list = [sentence]
    embeddings: ndarray = model.encode(sentence_list)
    sentence_embedding = embeddings[0]

    # Use config instead
    conn = psycopg2.connect(
        database="postgres",
        host="localhost",
        user="postgres",
        password="postgres",
        port="5432",
    )

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

    cursor.execute(cosine_simililarity_search_sql, cosine_simililarity_search_variables)
    results = cursor.fetchall()
    conn.commit()
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
