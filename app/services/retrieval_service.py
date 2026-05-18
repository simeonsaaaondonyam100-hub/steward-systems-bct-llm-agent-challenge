import math
from collections import Counter
from typing import Any

from app.services.item_profile_builder import ItemProfileBuilder
from app.utils.text_utils import clamp, cosine_from_counters, tokenize


class RetrievalService:
    def __init__(self) -> None:
        self.item_profile_builder = ItemProfileBuilder()

    def similarity(self, query: str, document: str) -> float:
        docs = [tokenize(query), tokenize(document)]
        if not docs[0] or not docs[1]:
            return 0.0
        vocabulary = set(docs[0]) | set(docs[1])
        idf = {}
        for token in vocabulary:
            containing = sum(1 for doc in docs if token in doc)
            idf[token] = math.log((1 + len(docs)) / (1 + containing)) + 1
        query_counter = Counter({token: count * idf[token] for token, count in Counter(docs[0]).items()})
        doc_counter = Counter({token: count * idf[token] for token, count in Counter(docs[1]).items()})
        return clamp(cosine_from_counters(query_counter, doc_counter), 0.0, 1.0)

    def score_items(self, query: str, items: list[dict[str, Any]]) -> dict[str, float]:
        scores = {}
        for item in items:
            document = self.item_profile_builder.build_text(item)
            scores[item["item_id"]] = self.similarity(query, document)
        return scores
