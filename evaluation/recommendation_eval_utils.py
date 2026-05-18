from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import Settings
from app.models.schemas import PastReview, RecommendRequest, UserPersona
from app.services.data_loader import DataLoader
from app.services.item_profile_builder import ItemProfileBuilder
from app.services.recommendation_ranking_service import RecommendationRankingService
from app.services.semantic_similarity_service import SemanticSimilarityService
from app.services.user_profile_builder import UserProfileBuilder


METRIC_KEYS = ["hit_rate@5", "hit_rate@10", "ndcg@5", "ndcg@10"]


@dataclass
class EvalCase:
    user_id: str
    description: str
    train_reviews: list[dict[str, Any]]
    test_reviews: list[dict[str, Any]]
    history_level: str

    @property
    def held_out_positive_ids(self) -> set[str]:
        return {review["item_id"] for review in self.test_reviews if review["rating"] >= 4}

    @property
    def train_item_ids(self) -> set[str]:
        return {review["item_id"] for review in self.train_reviews}


def dcg(relevances: list[int]) -> float:
    return sum(rel / math.log2(index + 2) for index, rel in enumerate(relevances))


def metrics_at_k(recommended_ids: list[str], positives: set[str], k: int) -> dict[str, float]:
    top_ids = recommended_ids[:k]
    relevances = [1 if item_id in positives else 0 for item_id in top_ids]
    ideal_relevance_count = min(len(positives), k)
    ideal = [1] * ideal_relevance_count + [0] * (k - ideal_relevance_count)
    return {
        f"hit_rate@{k}": 1.0 if any(relevances) else 0.0,
        f"ndcg@{k}": dcg(relevances) / dcg(ideal) if any(ideal) else 0.0,
    }


def average_metric(rows: list[dict[str, float]], key: str) -> float:
    return sum(row[key] for row in rows) / len(rows) if rows else 0.0


def build_eval_cases(loader: DataLoader) -> tuple[list[EvalCase], list[dict[str, Any]]]:
    users = {user["user_id"]: user for user in loader.load_users()}
    reviews_by_user: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for review in loader.load_reviews():
        reviews_by_user[review["user_id"]].append(review)

    cases: list[EvalCase] = []
    for user_id, reviews in reviews_by_user.items():
        if len(reviews) < 4:
            continue
        split_index = max(2, int(len(reviews) * 0.7))
        train_reviews = reviews[:split_index]
        test_reviews = reviews[split_index:]
        if not any(review["rating"] >= 4 for review in test_reviews):
            continue
        if len(train_reviews) <= 2:
            history_level = "sparse"
        elif len(train_reviews) <= 5:
            history_level = "sparse"
        else:
            history_level = "normal"
        cases.append(
            EvalCase(
                user_id=user_id,
                description=users[user_id]["description"],
                train_reviews=train_reviews,
                test_reviews=test_reviews,
                history_level=history_level,
            )
        )
    cold_start_users = [user for user in users.values() if user.get("cold_start")]
    return cases, cold_start_users


def persona_from_case(case: EvalCase, items_by_id: dict[str, dict[str, Any]]) -> UserPersona:
    history = [
        PastReview(
            item_name=items_by_id[review["item_id"]]["name"],
            category=items_by_id[review["item_id"]]["category"],
            rating=review["rating"],
            review=review["review"],
        )
        for review in case.train_reviews
    ]
    return UserPersona(user_id=case.user_id, description=case.description, past_reviews=history)


def rank_for_case(
    case: EvalCase,
    items: list[dict[str, Any]],
    items_by_id: dict[str, dict[str, Any]],
    settings: Settings | None = None,
    semantic_service: SemanticSimilarityService | None = None,
    top_k: int = 10,
) -> tuple[list[str], str]:
    profile = UserProfileBuilder().build(persona_from_case(case, items_by_id))
    candidates = [item for item in items if item["item_id"] not in case.train_item_ids]
    ranker = RecommendationRankingService(settings=settings, semantic_service=semantic_service)
    ranked = ranker.rank(
        profile=profile,
        items=candidates,
        current_context="Recommend items that fit this user's recent behaviour and Nigerian context.",
        candidate_domain=None,
        top_k=top_k,
    )
    return [entry["item"]["item_id"] for entry in ranked], ranker.semantic_mode


def evaluate_recommender(
    cases: list[EvalCase],
    items: list[dict[str, Any]],
    settings: Settings | None = None,
    semantic_service: SemanticSimilarityService | None = None,
) -> tuple[dict[str, float], list[dict[str, float]], str]:
    items_by_id = {item["item_id"]: item for item in items}
    rows = []
    semantic_mode = "tfidf_fallback"
    for case in cases:
        recommended_ids, semantic_mode = rank_for_case(case, items, items_by_id, settings, semantic_service)
        row = {}
        row.update(metrics_at_k(recommended_ids, case.held_out_positive_ids, 5))
        row.update(metrics_at_k(recommended_ids, case.held_out_positive_ids, 10))
        rows.append(row)
    metrics = {key: round(average_metric(rows, key), 4) for key in METRIC_KEYS}
    return metrics, rows, semantic_mode


def popularity_baseline(cases: list[EvalCase], items: list[dict[str, Any]]) -> dict[str, float]:
    rows = []
    for case in cases:
        candidates = [item for item in items if item["item_id"] not in case.train_item_ids]
        ranked = sorted(
            candidates,
            key=lambda item: (
                float(item["metadata"].get("popularity_score", 0)),
                float(item["metadata"].get("average_rating", 0)),
            ),
            reverse=True,
        )
        ids = [item["item_id"] for item in ranked[:10]]
        row = {}
        row.update(metrics_at_k(ids, case.held_out_positive_ids, 5))
        row.update(metrics_at_k(ids, case.held_out_positive_ids, 10))
        rows.append(row)
    return {key: round(average_metric(rows, key), 4) for key in METRIC_KEYS}


def content_only_baseline(cases: list[EvalCase], items: list[dict[str, Any]]) -> dict[str, float]:
    rows = []
    builder = ItemProfileBuilder()
    semantic = SemanticSimilarityService(enable_sentence_transformers=False)
    for case in cases:
        candidates = [item for item in items if item["item_id"] not in case.train_item_ids]
        query = f"{case.description} {' '.join(review['review'] for review in case.train_reviews)}"
        texts = [builder.build_text(item) for item in candidates]
        scores = semantic.batch_similarity(query, texts)
        ranked = [item for _, item in sorted(zip(scores, candidates), key=lambda pair: pair[0], reverse=True)]
        ids = [item["item_id"] for item in ranked[:10]]
        row = {}
        row.update(metrics_at_k(ids, case.held_out_positive_ids, 5))
        row.update(metrics_at_k(ids, case.held_out_positive_ids, 10))
        rows.append(row)
    return {key: round(average_metric(rows, key), 4) for key in METRIC_KEYS}


def cold_start_proxy_eval(cold_start_users: list[dict[str, Any]], items: list[dict[str, Any]]) -> dict[str, Any]:
    if not cold_start_users:
        return {"num_examples": 0, "contextual_fit@5": 0.0}
    profile_builder = UserProfileBuilder()
    ranker = RecommendationRankingService()
    scores = []
    for user in cold_start_users:
        persona = UserPersona(user_id=user["user_id"], description=user["description"], past_reviews=[])
        profile = profile_builder.build(persona)
        ranked = ranker.rank(
            profile=profile,
            items=items,
            current_context=user["description"],
            candidate_domain=None,
            top_k=5,
        )
        fit_count = sum(1 for entry in ranked if entry["components"]["preference_match"] >= 0.3 or entry["components"]["context_match"] >= 0.15)
        scores.append(fit_count / 5)
    return {"num_examples": len(cold_start_users), "contextual_fit@5": round(sum(scores) / len(scores), 4)}


def load_default_eval_data(root: Path) -> tuple[DataLoader, list[dict[str, Any]], list[EvalCase], list[dict[str, Any]]]:
    loader = DataLoader(root / "data" / "sample")
    items = loader.load_items()
    cases, cold_start_users = build_eval_cases(loader)
    return loader, items, cases, cold_start_users
