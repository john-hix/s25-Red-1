from typing import List

import spacy


def get_all_sentences(text) -> List[str]:
    """Get the sentences in a string"""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    assert doc.has_annotation("SENT_START")
    return [sent.text for sent in doc.sents]
