from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.services.semantic_similarity_service import SemanticSimilarityService  # noqa: E402
from evaluation.recommendation_eval_utils import evaluate_recommender, load_default_eval_data  # noqa: E402


def candidate_weights() -> list[dict[str, float]]:
    return [
        {
            "semantic_weight": 0.24,
            "preference_weight": 0.31,
            "context_weight": 0.18,
            "quality_weight": 0.12,
            "nigerian_context_weight": 0.12,
            "penalty_weight": 0.03,
        },
        {
            "semantic_weight": 0.22,
            "preference_weight": 0.34,
            "context_weight": 0.20,
            "quality_weight": 0.11,
            "nigerian_context_weight": 0.10,
            "penalty_weight": 0.03,
        },
        {
            "semantic_weight": 0.20,
            "preference_weight": 0.36,
            "context_weight": 0.18,
            "quality_weight": 0.12,
            "nigerian_context_weight": 0.10,
            "penalty_weight": 0.04,
        },
        {
            "semantic_weight": 0.26,
            "preference_weight": 0.30,
            "context_weight": 0.18,
            "quality_weight": 0.10,
            "nigerian_context_weight": 0.12,
            "penalty_weight": 0.04,
        },
        {
            "semantic_weight": 0.18,
            "preference_weight": 0.38,
            "context_weight": 0.20,
            "quality_weight": 0.10,
            "nigerian_context_weight": 0.10,
            "penalty_weight": 0.04,
        },
        {
            "semantic_weight": 0.21,
            "preference_weight": 0.33,
            "context_weight": 0.22,
            "quality_weight": 0.10,
            "nigerian_context_weight": 0.11,
            "penalty_weight": 0.03,
        },
    ]


def objective(metrics: dict[str, float]) -> float:
    return (
        0.35 * metrics["ndcg@10"]
        + 0.25 * metrics["hit_rate@10"]
        + 0.25 * metrics["ndcg@5"]
        + 0.15 * metrics["hit_rate@5"]
    )


def main() -> None:
    _, items, cases, _ = load_default_eval_data(ROOT)
    runs = []
    for weights in candidate_weights():
        settings = Settings(**weights)
        metrics, _, semantic_mode = evaluate_recommender(
            cases,
            items,
            settings=settings,
            semantic_service=SemanticSimilarityService(enable_sentence_transformers=False),
        )
        runs.append(
            {
                "weights": weights,
                "metrics": metrics,
                "semantic_mode": semantic_mode,
                "objective": round(objective(metrics), 6),
            }
        )

    runs.sort(key=lambda row: row["objective"], reverse=True)
    result = {
        "selection_note": (
            "Small explainable grid over reasonable weights. Objective balances NDCG@10, Hit Rate@10, "
            "NDCG@5, and Hit Rate@5; sentence-transformers are disabled during tuning for reproducibility."
        ),
        "best_weights": runs[0]["weights"],
        "best_metrics": runs[0]["metrics"],
        "best_objective": runs[0]["objective"],
        "all_runs": runs,
    }
    results_dir = ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "recommendation_weight_tuning.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("Recommendation Weight Tuning")
    print(f"Best objective: {runs[0]['objective']:.4f}")
    print("Best weights:")
    for key, value in runs[0]["weights"].items():
        print(f"- {key}: {value}")
    print("Best metrics:")
    for key, value in runs[0]["metrics"].items():
        print(f"- {key}: {value:.3f}")
    print(f"Wrote results to {output_path}")


if __name__ == "__main__":
    main()
