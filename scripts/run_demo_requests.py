from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agents.recommendation_agent import RecommendationAgent  # noqa: E402
from app.agents.review_simulation_agent import ReviewSimulationAgent  # noqa: E402
from app.models.schemas import RecommendRequest, SimulateReviewRequest  # noqa: E402


def main() -> None:
    task_a_payload = {
        "user_persona": {
            "user_id": "user_001",
            "description": "A Lagos-based university student who likes spicy food, affordable meals, and fast delivery.",
            "past_reviews": [
                {
                    "item_name": "Jollof Rice and Chicken",
                    "category": "Food",
                    "rating": 4,
                    "review": "The food was tasty and the portion was fair, but delivery took too long.",
                }
            ],
        },
        "item": {
            "item_id": "item_001",
            "name": "Spicy Chicken Shawarma",
            "category": "Food",
            "price": 2500,
            "metadata": {
                "spicy": True,
                "delivery_time_minutes": 35,
                "portion_size": "medium",
                "location": "Lagos",
            },
        },
    }
    task_b_payload = {
        "user_persona": {
            "user_id": "user_001",
            "description": "A Lagos-based university student who prefers affordable spicy meals and quick delivery.",
            "past_reviews": [],
        },
        "current_context": "Needs dinner after lectures and wants something filling but not expensive.",
        "top_k": 5,
    }

    task_a = ReviewSimulationAgent().simulate(SimulateReviewRequest(**task_a_payload))
    task_b = RecommendationAgent().recommend(RecommendRequest(**task_b_payload))
    print("Task A response:")
    print(task_a.model_dump_json(indent=2))
    print("\nTask B response:")
    print(task_b.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
