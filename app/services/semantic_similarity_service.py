from __future__ import annotations

from collections import Counter
from typing import Any

from app.config import get_settings
from app.services.retrieval_service import RetrievalService
from app.utils.text_utils import clamp


class SemanticSimilarityService:
    def __init__(
        self,
        enable_sentence_transformers: bool | None = None,
        model_name: str | None = None,
    ) -> None:
        settings = get_settings()
        self.enable_sentence_transformers = (
            settings.enable_sentence_transformers
            if enable_sentence_transformers is None
            else enable_sentence_transformers
        )
        self.model_name = model_name or settings.sentence_transformer_model
        self.retrieval_service = RetrievalService()
        self.model: Any | None = None
        self.mode = "tfidf_fallback"
        self._corpus_texts: list[str] = []

    def fit_or_load_corpus(self, items: list[dict[str, Any]] | list[str]) -> None:
        self._corpus_texts = [
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in items
        ]
        if not self.enable_sentence_transformers:
            self.mode = "tfidf_fallback"
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self.model = SentenceTransformer(self.model_name)
            self.mode = "sentence_transformer"
        except Exception:
            self.model = None
            self.mode = "tfidf_fallback"

    def similarity(self, query_text: str, candidate_text: str) -> float:
        return self.batch_similarity(query_text, [candidate_text])[0]

    def batch_similarity(self, query_text: str, candidate_texts: list[str]) -> list[float]:
        if not candidate_texts:
            return []
        if self.model is not None and self.mode == "sentence_transformer":
            try:
                embeddings = self.model.encode([query_text] + candidate_texts, normalize_embeddings=True)
                query_embedding = embeddings[0]
                return [
                    round(clamp(float(query_embedding @ candidate_embedding), 0.0, 1.0), 4)
                    for candidate_embedding in embeddings[1:]
                ]
            except Exception:
                self.mode = "tfidf_fallback"
                self.model = None
        return [self._fallback_similarity(query_text, candidate_text) for candidate_text in candidate_texts]

    def _fallback_similarity(self, query_text: str, candidate_text: str) -> float:
        lexical = self.retrieval_service.similarity(query_text, candidate_text)
        query_terms = self._phrase_terms(query_text)
        candidate_terms = self._phrase_terms(candidate_text)
        phrase_overlap = 0.0
        if query_terms and candidate_terms:
            phrase_overlap = len(query_terms & candidate_terms) / max(len(query_terms | candidate_terms), 1)
        return round(clamp(0.82 * lexical + 0.18 * phrase_overlap, 0.0, 1.0), 4)

    def _phrase_terms(self, text: str) -> set[str]:
        lowered = text.lower()
        phrase_map = {
            "pepper soup": "pepper_soup",
            "small chops": "small_chops",
            "jollof rice": "jollof_rice",
            "grilled chicken": "grilled_chicken",
            "power bank": "power_bank",
            "low sugar": "low_sugar",
            "office lunch": "office_lunch",
            "date night": "date_night",
        }
        phrases = {token for phrase, token in phrase_map.items() if phrase in lowered}
        tokens = Counter(lowered.replace("-", " ").split())
        keywords = {
            "jollof",
            "suya",
            "shawarma",
            "zobo",
            "chapman",
            "amala",
            "egusi",
            "spicy",
            "budget",
            "family",
            "office",
            "book",
            "movie",
            "durable",
            "healthy",
            "quick",
            "delivery",
        }
        return phrases | {token.strip(".,;:!?") for token in tokens if token.strip(".,;:!?") in keywords}
