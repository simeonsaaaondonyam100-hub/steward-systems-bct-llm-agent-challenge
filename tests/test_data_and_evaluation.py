import json
import subprocess
import sys
from pathlib import Path

from app.services.data_loader import DataLoader


ROOT = Path(__file__).resolve().parent.parent


def test_phase_2_sample_data_is_expanded_and_contextual() -> None:
    loader = DataLoader(ROOT / "data" / "sample")
    users = loader.load_users()
    items = loader.load_items()
    reviews = loader.load_reviews()

    assert 15 <= len(users) <= 20
    assert 50 <= len(items) <= 80
    assert 150 <= len(reviews) <= 250
    assert any(user.get("cold_start") for user in users)

    categories = {item["category"].lower() for item in items}
    assert {"food", "drink", "book", "movie", "product"} <= categories

    required_metadata = {"spice_level", "delivery_time_minutes", "portion_size", "location", "tags", "popularity_score", "average_rating"}
    assert all(required_metadata <= set(item["metadata"]) for item in items)


def test_evaluation_scripts_create_judge_readable_result_files() -> None:
    results_dir = ROOT / "evaluation" / "results"
    task_a_path = results_dir / "task_a_results.json"
    task_b_path = results_dir / "task_b_results.json"
    ablation_path = results_dir / "ablation_summary.json"

    subprocess.run([sys.executable, str(ROOT / "evaluation" / "evaluate_task_a.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "evaluation" / "evaluate_task_b.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "tune_recommendation_weights.py")], cwd=ROOT, check=True)

    task_a = json.loads(task_a_path.read_text(encoding="utf-8"))
    task_b = json.loads(task_b_path.read_text(encoding="utf-8"))
    ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
    tuning = json.loads((results_dir / "recommendation_weight_tuning.json").read_text(encoding="utf-8"))

    assert {"num_examples", "rmse", "mae", "sample_predictions", "qualitative_samples"} <= set(task_a)
    assert {"num_users", "held_out_examples", "cold_start_examples", "sparse_history_examples", "normal_history_examples"} <= set(task_b)
    assert {"hit_rate@5", "hit_rate@10", "ndcg@5", "ndcg@10"} <= set(task_b["metrics"])
    assert {
        "popularity_baseline",
        "content_only_baseline",
        "hybrid_without_nigerian_context",
        "hybrid_with_nigerian_context",
        "hybrid_with_semantic_embeddings_if_available",
        "cold_start_only",
    } <= set(ablation)
    assert "best_weights" in tuning
    assert "best_metrics" in tuning
