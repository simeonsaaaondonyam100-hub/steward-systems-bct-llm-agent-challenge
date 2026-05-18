from fastapi import APIRouter, HTTPException

from app.agents.review_simulation_agent import ReviewSimulationAgent
from app.models.schemas import SimulateReviewRequest, SimulateReviewResponse


router = APIRouter(prefix="/api/task-a", tags=["Task A - Review Simulation"])
agent = ReviewSimulationAgent()


@router.post("/simulate-review", response_model=SimulateReviewResponse)
def simulate_review(request: SimulateReviewRequest) -> SimulateReviewResponse:
    try:
        return agent.simulate(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
