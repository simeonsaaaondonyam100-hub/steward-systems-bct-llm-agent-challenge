from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from app.agents.review_simulation_agent import ReviewSimulationAgent
from app.models.schemas import SimulateReviewRequest, SimulateReviewResponse


router = APIRouter(prefix="/api/task-a", tags=["Task A - Review Simulation"])
agent = ReviewSimulationAgent()


TASK_A_OPENAPI_EXAMPLE = {
    "user_persona": {
        "user_id": "user_001",
        "description": "A Lagos-based university student who likes spicy food, affordable meals, large portions, and fast delivery.",
        "past_reviews": [
            {
                "item_name": "Jollof Rice and Chicken",
                "category": "Food",
                "rating": 4,
                "review": "The food was tasty and the portion was fair, but delivery took too long.",
            },
            {
                "item_name": "Suya Platter",
                "category": "Food",
                "rating": 5,
                "review": "Very spicy and fresh. The portion was generous and worth the price.",
            },
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
            "tags": ["spicy", "quick meal", "chicken", "affordable"],
        },
    },
}


@router.post(
    "/simulate-review",
    response_model=SimulateReviewResponse,
    summary="Simulate a user review",
    description=(
        "Predict a rating and generate a realistic review from a user profile and item details. "
        "Swagger may show schema placeholders in some views; for realistic examples, use the "
        "Example Value here or docs/sample_payloads.md."
    ),
)
def simulate_review(
    request: Annotated[
        SimulateReviewRequest,
        Body(
            openapi_examples={
                "lagos_student_shawarma": {
                    "summary": "Lagos student reviewing spicy shawarma",
                    "description": "A realistic Task A request using Nigerian food, price, delivery, and portion signals.",
                    "value": TASK_A_OPENAPI_EXAMPLE,
                }
            }
        ),
    ],
) -> SimulateReviewResponse:
    try:
        return agent.simulate(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
