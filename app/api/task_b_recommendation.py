from fastapi import APIRouter, HTTPException

from app.agents.recommendation_agent import RecommendationAgent
from app.models.schemas import RecommendRequest, RecommendResponse


router = APIRouter(prefix="/api/task-b", tags=["Task B - Recommendation"])
agent = RecommendationAgent()


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    try:
        return agent.recommend(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
