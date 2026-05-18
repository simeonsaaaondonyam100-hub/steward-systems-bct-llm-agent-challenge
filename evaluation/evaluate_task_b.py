from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.services.semantic_similarity_service import SemanticSimilarityService  # noqa: E402
from evaluation.recommendation_eval_utils import (  # noqa: E402
    METRIC_KEYS,
    cold_start_proxy_eval,
    content_only_baseline,
    evaluate_recommender,
    load_default_eval_data,
    popularity_baseline,
)


def write_ablation_markdown(path: Path, ablation: dict, task_b_results: dict) -> None:
    lines = [
        "# Recommendation Ablation Summary",
        "",
        f"Semantic mode: `{task_b_results['semantic_mode']}`",
        f"Held-out examples: `{task_b_results['held_out_examples']}`",
        "",
        "| Variant | Hit Rate@5 | Hit Rate@10 | NDCG@5 | NDCG@10 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, metrics in ablation.items():
        if "metrics" in metrics:
            metric_row = metrics["metrics"]
        else:
            metric_row = metrics
        lines.append(
            f"| {name} | {metric_row.get('hit_rate@5', 0):.3f} | {metric_row.get('hit_rate@10', 0):.3f} | "
            f"{metric_row.get('ndcg@5', 0):.3f} | {metric_row.get('ndcg@10', 0):.3f} |"
        )
    lines.extend(
        [
            "",
            "The held-out protocol uses early reviews as profile history and later reviews as target relevance labels.",
            "Known training items are removed from the candidate pool before ranking.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    _, items, cases, cold_start_users = load_default_eval_data(ROOT)

    default_metrics, _, semantic_mode = evaluate_recommender(cases, items)
    no_ng_metrics, _, _ = evaluate_recommender(
        cases,
        items,
        settings=Settings(
            semantic_weight=0.26,
            preference_weight=0.34,
            context_weight=0.20,
            quality_weight=0.17,
            nigerian_context_weight=0.0,
            penalty_weight=0.03,
        ),
        semantic_service=SemanticSimilarityService(enable_sentence_transformers=False),
    )
    semantic_metrics, _, semantic_ablation_mode = evaluate_recommender(
        cases,
        items,
        semantic_service=SemanticSimilarityService(enable_sentence_transformers=True),
    )

    results_dir = ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    history_counts = {
        "cold_start_examples": len(cold_start_users),
        "sparse_history_examples": sum(1 for case in cases if case.history_level == "sparse"),
        "normal_history_examples": sum(1 for case in cases if case.history_level == "normal"),
    }
    task_b_results = {
        "num_users": len({case.user_id for case in cases}),
        "held_out_examples": sum(len(case.test_reviews) for case in cases),
        **history_counts,
        "metrics": default_metrics,
        "k_values": [5, 10],
        "semantic_mode": semantic_mode,
        "notes": "Held-out reviews are later review rows per user; train items are removed from candidates.",
    }
    ablation = {
        "popularity_baseline": popularity_baseline(cases, items),
        "content_only_baseline": content_only_baseline(cases, items),
        "hybrid_without_nigerian_context": no_ng_metrics,
        "hybrid_with_nigerian_context": default_metrics,
        "hybrid_with_semantic_embeddings_if_available": {
            "semantic_mode": semantic_ablation_mode,
            "metrics": semantic_metrics,
        },
        "cold_start_only": cold_start_proxy_eval(cold_start_users, items),
    }

    task_b_path = results_dir / "task_b_results.json"
    ablation_path = results_dir / "ablation_summary.json"
    task_b_path.write_text(json.dumps(task_b_results, indent=2), encoding="utf-8")
    ablation_path.write_text(json.dumps(ablation, indent=2), encoding="utf-8")
    write_ablation_markdown(results_dir / "ablation_summary.md", ablation, task_b_results)

    print("Task B Evaluation")
    print(f"Users evaluated: {task_b_results['num_users']}")
    print(f"Held-out examples: {task_b_results['held_out_examples']}")
    print(f"Cold-start examples: {task_b_results['cold_start_examples']}")
    print(f"Sparse-history examples: {task_b_results['sparse_history_examples']}")
    print(f"Normal-history examples: {task_b_results['normal_history_examples']}")
    print(f"Semantic mode: {semantic_mode}")
    for key in METRIC_KEYS:
        print(f"{key}: {default_metrics[key]:.3f}")
    print("Ablation comparison:")
    for name, metrics in ablation.items():
        metric_row = metrics["metrics"] if "metrics" in metrics else metrics
        printable = ", ".join(
            f"{key}={metric_row[key]:.3f}" for key in METRIC_KEYS if key in metric_row
        )
        if not printable and "contextual_fit@5" in metric_row:
            printable = f"contextual_fit@5={metric_row['contextual_fit@5']:.3f}"
        print(f"- {name}: {printable}")
    print(f"Wrote results to {results_dir}")


if __name__ == "__main__":
    main()
