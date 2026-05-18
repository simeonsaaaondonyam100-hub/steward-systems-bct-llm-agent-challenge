from collections import defaultdict
from pathlib import Path
import json
import math
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agents.recommendation_agent import RecommendationAgent  # noqa: E402
from app.config import Settings  # noqa: E402
from app.models.schemas import PastReview, RecommendRequest  # noqa: E402
from app.services.data_loader import DataLoader  # noqa: E402
from app.services.item_profile_builder import ItemProfileBuilder  # noqa: E402
from app.services.recommendation_ranking_service import RecommendationRankingService  # noqa: E402
from app.services.retrieval_service import RetrievalService  # noqa: E402
from app.services.user_profile_builder import UserProfileBuilder  # noqa: E402


def dcg(relevances: list[int]) -> float:
    return sum(rel / math.log2(index + 2) for index, rel in enumerate(relevances))


def metrics_at_k(recommended_ids: list[str], positives: set[str], k: int) -> dict[str, float]:
    top_ids = recommended_ids[:k]
    relevances = [1 if item_id in positives else 0 for item_id in top_ids]
    ideal = sorted(relevances, reverse=True)
    return {
        f"hit_rate@{k}": 1.0 if any(relevances) else 0.0,
        f"ndcg@{k}": dcg(relevances) / dcg(ideal) if any(ideal) else 0.0,
    }


def average_metric(rows: list[dict[str, float]], key: str) -> float:
    return sum(row[key] for row in rows) / len(rows) if rows else 0.0


def popularity_content_baseline(profile_text: str, items: list[dict], top_k: int) -> list[str]:
    retrieval = RetrievalService()
    builder = ItemProfileBuilder()
    scored = []
    for item in items:
        metadata = item.get("metadata", {})
        popularity = float(metadata.get("popularity_score", metadata.get("popularity", 50))) / 100
        quality = (float(metadata.get("average_rating", metadata.get("quality_score", 3.5))) - 1) / 4
        content = retrieval.similarity(profile_text, builder.build_text(item))
        scored.append((0.45 * popularity + 0.35 * quality + 0.20 * content, item["item_id"]))
    return [item_id for _, item_id in sorted(scored, reverse=True)[:top_k]]


def main() -> None:
    loader = DataLoader(ROOT / "data" / "sample")
    users = {user["user_id"]: user for user in loader.load_users()}
    items = loader.load_items()
    reviews_by_user = defaultdict(list)
    for review in loader.load_reviews():
        reviews_by_user[review["user_id"]].append(review)

    agent = RecommendationAgent()
    hybrid_rows = []
    baseline_rows = []
    no_ng_rows = []
    profile_builder = UserProfileBuilder()
    no_ng_ranker = RecommendationRankingService(
        settings=Settings(
            semantic_weight=0.34,
            preference_weight=0.28,
            context_weight=0.22,
            quality_weight=0.16,
            nigerian_context_weight=0.0,
        )
    )

    for user_id, reviews in reviews_by_user.items():
        positives = {review["item_id"] for review in reviews if review["rating"] >= 4}
        history = [
            PastReview(**row)
            for row in loader.get_user_history(user_id)
        ][:5]
        request = RecommendRequest(
            user_persona={
                "user_id": user_id,
                "description": users[user_id]["description"],
                "past_reviews": history,
            },
            current_context="Find something that fits this user's current habits and Nigerian context.",
            top_k=10,
        )
        response = agent.recommend(request)
        recommended_ids = [item.item_id for item in response.recommendations]
        row = {}
        row.update(metrics_at_k(recommended_ids, positives, 5))
        row.update(metrics_at_k(recommended_ids, positives, 10))
        hybrid_rows.append(row)

        baseline_ids = popularity_content_baseline(users[user_id]["description"], items, 10)
        baseline_row = {}
        baseline_row.update(metrics_at_k(baseline_ids, positives, 5))
        baseline_row.update(metrics_at_k(baseline_ids, positives, 10))
        baseline_rows.append(baseline_row)

        profile = profile_builder.build(
            request.user_persona
        )
        no_ng_ids = [
            entry["item"]["item_id"]
            for entry in no_ng_ranker.rank(
                profile=profile,
                items=items,
                current_context=request.current_context,
                candidate_domain=request.candidate_domain,
                top_k=10,
            )
        ]
        no_ng_row = {}
        no_ng_row.update(metrics_at_k(no_ng_ids, positives, 5))
        no_ng_row.update(metrics_at_k(no_ng_ids, positives, 10))
        no_ng_rows.append(no_ng_row)

    metric_keys = ["hit_rate@5", "hit_rate@10", "ndcg@5", "ndcg@10"]
    hybrid_metrics = {key: round(average_metric(hybrid_rows, key), 4) for key in metric_keys}
    baseline_metrics = {key: round(average_metric(baseline_rows, key), 4) for key in metric_keys}
    no_ng_metrics = {key: round(average_metric(no_ng_rows, key), 4) for key in metric_keys}

    results_dir = ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    task_b_results = {
        "num_users": len(hybrid_rows),
        "metrics": hybrid_metrics,
        "k_values": [5, 10],
        "notes": "Positive items are sample reviews with rating >= 4.",
    }
    ablation = {
        "popularity_content_baseline": baseline_metrics,
        "hybrid_without_nigerian_context": no_ng_metrics,
        "hybrid_with_nigerian_context": hybrid_metrics,
    }
    results_dir.joinpath("task_b_results.json").write_text(json.dumps(task_b_results, indent=2), encoding="utf-8")
    results_dir.joinpath("ablation_summary.json").write_text(json.dumps(ablation, indent=2), encoding="utf-8")

    print("Task B Evaluation")
    print(f"Users evaluated: {len(hybrid_rows)}")
    for key in metric_keys:
        print(f"{key}: {hybrid_metrics[key]:.3f}")
    print("Ablation comparison:")
    for name, metrics in ablation.items():
        print(f"- {name}: " + ", ".join(f"{key}={value:.3f}" for key, value in metrics.items()))
    print(f"Wrote results to {results_dir}")


if __name__ == "__main__":
    main()
