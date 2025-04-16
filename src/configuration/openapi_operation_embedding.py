"""Embed OpenAPI Operation descriptions for similiarity search at runtime"""

import logging
from typing import List

import spacy
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from common.models.openapi_operation import OpenAPIOperation
from common.models.openapi_operation_selection import OpenAPIOperationSelectionPrompt
from common.models.openapi_path import OpenAPIPath
from common.models.openapi_spec import OpenAPISpec

from .openapi import OperationObject, PathItemObject


# pylint: disable-next=too-many-arguments, too-many-positional-arguments
def create_operation_prompts_without_embeddings(
    db_op: OpenAPIOperation,
    http_verb: str,
    path: PathItemObject,  # pylint: disable=unused-argument
    path_str: str,
    op: OperationObject,
    session: scoped_session,
):
    """Build OpenAPI Operation Selection Prompts from the Pydantic model and add
    them to the DB session without committing."""

    prompt_list: List[str] = []
    prompt_list.append(
        make_http_oriented_selection_prompt_for_operation(path_str, http_verb)
    )
    # Handle the description vs x-cuecode-prompt behavior for old spec files
    prompt_list.extend(get_all_sentences(pick_op_description_field(op)))

    if op.x_cuecode_prompts:
        for prompt in op.x_cuecode_prompts:
            prompt_list.append(prompt)

    for prompt in prompt_list:
        this_oapi_op_select_prompt = OpenAPIOperationSelectionPrompt(
            openapi_operation_id=db_op.openapi_operation_id,
            selection_prompt=prompt,
        )
        db_op.selection_prompts.append(this_oapi_op_select_prompt)
        session.add(db_op)


def create_operation_prompt_embeddings_not_resumable(db_spec, session: scoped_session):
    """Create sentence embeddings for all `OpenAPIOperationSelectionPrompt`s associated
    with the passed `db_spec`. Side effect: all `OpenAPIOperationSelectionPrompt`s associated
    with the `db_spec` have been updated with a vector embedding value AND have been added
    to the ORM session."""
    # Get all Operation promtps from the db and embed all at once.

    # Get all Operation selection prompts for this target API from the DB
    logging.debug(
        "create_operation_prompt_embeddings_not_resumable getting selection prompt objets from db."
    )
    rows = session.execute(
        select(OpenAPIOperationSelectionPrompt)
        .join(OpenAPISpec.paths)
        .join(OpenAPIPath.operations)
        .join(OpenAPIOperation.selection_prompts)
        .where(OpenAPISpec.openapi_spec_id == db_spec.openapi_spec_id)
        .order_by(OpenAPIOperation.openapi_operation_id)
    ).all()

    # Embed all prompts
    sentence_list: List[str] = []
    for row in rows:
        sentence_list.append(row.OpenAPIOperationSelectionPrompt.selection_prompt)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    logging.debug(
        "create_operation_prompt_embeddings_not_resumable beginning embeddings"
    )
    embeddings = model.encode(sentence_list)
    logging.debug(
        "create_operation_prompt_embeddings_not_resumable done with embeddings"
    )
    assert len(embeddings) == len(sentence_list)
    assert len(sentence_list) == len(rows)

    # Store embeddings in the DB
    logging.debug(
        "create_operation_prompt_embeddings_not_resumable adding embeddings to DB records"
    )
    print(embeddings)

    for i, row in enumerate(rows):
        prompt: OpenAPIOperationSelectionPrompt = row.OpenAPIOperationSelectionPrompt
        prompt.selection_prompt_embedding = embeddings[i]
        session.add(prompt)
    logging.debug(
        "create_operation_prompt_embeddings_not_resumable done adding embeddings to DB records"
    )


def pick_op_description_field(
    operation_object: OperationObject,
) -> str:
    """Create a prompt used for the selecting the HTTP Operation"""

    desc = ""
    if operation_object:
        if operation_object.x_cuecode_prompt:
            desc = operation_object.x_cuecode_prompt
        else:
            desc = operation_object.description  # type: ignore
    return desc


def make_http_oriented_selection_prompt_for_operation(
    path_str: str,  # pylint: disable=unused-argument
    http_verb: str,  # pylint: disable=unused-argument
) -> str:
    """Create Operation prompt based on HTTP information"""
    prompt = (
        "Apply the HTTP verb "
        + http_verb
        + " to the REST API endpoint with path '"
        + path_str
        + "'."
    )
    return prompt


def get_all_sentences(text) -> List[str]:
    """Get the sentences in a string"""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    assert doc.has_annotation("SENT_START")
    return [sent.text for sent in doc.sents]
