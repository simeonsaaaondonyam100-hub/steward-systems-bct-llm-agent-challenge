from pathlib import Path
import json
import math
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agents.review_simulation_agent import ReviewSimulationAgent  # noqa: E402
from app.models.schemas import PastReview, SimulateReviewRequest  # noqa: E402
from app.services.data_loader import DataLoader  # noqa: E402


def main() -> None:
    loader = DataLoader(ROOT / "data" / "sample")
    items = {item["item_id"]: item for item in loader.load_items()}
    users = {user["user_id"]: user for user in loader.load_users()}
    agent = ReviewSimulationAgent()
    squared_errors = []
    absolute_errors = []
    text_lengths = []
    sample_predictions = []
    qualitative_samples = []

    for review in loader.load_reviews():
        history = [
            PastReview(**row)
            for row in loader.get_user_history(review["user_id"])
            if row["item_name"] != items[review["item_id"]]["name"]
        ][:5]
        user = users[review["user_id"]]
        item = items[review["item_id"]]
        request = SimulateReviewRequest(
            user_persona={
                "user_id": user["user_id"],
                "description": user["description"],
                "past_reviews": history,
            },
            item=item,
        )
        prediction = agent.simulate(request)
        error = prediction.predicted_rating - review["rating"]
        squared_errors.append(error**2)
        absolute_errors.append(abs(error))
        text_lengths.append(len(prediction.generated_review.split()))
        if len(sample_predictions) < 8:
            sample_predictions.append(
                {
                    "user_id": review["user_id"],
                    "item_name": item["name"],
                    "actual_rating": review["rating"],
                    "predicted_rating": prediction.predicted_rating,
                    "absolute_error": round(abs(error), 3),
                }
            )
        if len(qualitative_samples) < 5:
            qualitative_samples.append(
                {
                    "user_id": review["user_id"],
                    "item_name": item["name"],
                    "generated_review": prediction.generated_review,
                    "profile_summary": prediction.user_profile_summary,
                }
            )

    rmse = math.sqrt(sum(squared_errors) / len(squared_errors))
    mae = sum(absolute_errors) / len(absolute_errors)
    avg_words = sum(text_lengths) / len(text_lengths)
    results = {
        "num_examples": len(squared_errors),
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "generated_review_average_words": round(avg_words, 1),
        "sample_predictions": sample_predictions,
        "qualitative_samples": qualitative_samples,
    }
    results_dir = ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_dir.joinpath("task_a_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("Task A Evaluation")
    print(f"Reviews evaluated: {len(squared_errors)}")
    print(f"Rating RMSE: {rmse:.3f}")
    print(f"Rating MAE: {mae:.3f}")
    print(f"Generated review average length: {avg_words:.1f} words")
    print("Sample predicted vs actual:")
    for row in sample_predictions[:5]:
        print(
            f"- {row['user_id']} | {row['item_name']} | actual={row['actual_rating']} "
            f"predicted={row['predicted_rating']} abs_error={row['absolute_error']}"
        )
    print(f"Wrote results to {results_dir / 'task_a_results.json'}")


if __name__ == "__main__":
    main()
