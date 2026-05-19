from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from app.agents.recommendation_agent import RecommendationAgent
from app.models.schemas import RecommendRequest, RecommendResponse


router = APIRouter(prefix="/api/task-b", tags=["Task B - Recommendation"])
agent = RecommendationAgent()


TASK_B_OPENAPI_EXAMPLE = {
    "user_persona": {
        "user_id": "user_002",
        "description": (
            "A Lagos-based university student who likes spicy food, affordable meals, filling portions, and quick "
            "delivery. He dislikes expensive meals with small portions and slow delivery."
        ),
        "past_reviews": [
            {
                "item_name": "Suya Platter",
                "category": "Food",
                "rating": 5,
                "review": (
                    "Fresh, spicy, affordable, and very satisfying. The pepper was just right and the portion "
                    "was worth the price."
                ),
            },
            {
                "item_name": "Burger Meal",
                "category": "Food",
                "rating": 2,
                "review": "Too expensive for the portion. Delivery was slow and the food was already cold when it arrived.",
            },
            {
                "item_name": "Jollof Rice and Chicken",
                "category": "Food",
                "rating": 4,
                "review": "The jollof had good smoky flavour and the chicken was tasty. The portion was fair for the price.",
            },
        ],
    },
    "current_context": "Needs dinner after lectures and wants something filling, spicy, affordable, and not too slow to deliver.",
    "category": "Food",
    "top_k": 5,
}


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Recommend personalised items",
    description=(
        "Return ranked recommendations with score breakdowns, context fit, and cold-start handling. "
        "Swagger may show schema placeholders in some views; for realistic examples, use the "
        "Example Value here or docs/sample_payloads.md."
    ),
)
def recommend(
    request: Annotated[
        RecommendRequest,
        Body(
            openapi_examples={
                "lagos_student_dinner": {
                    "summary": "Lagos student dinner recommendation",
                    "description": "A realistic Task B request using Nigerian food preferences, dislikes, and current context.",
                    "value": TASK_B_OPENAPI_EXAMPLE,
                }
            }
        ),
    ],
) -> RecommendResponse:
    try:
        return agent.recommend(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
