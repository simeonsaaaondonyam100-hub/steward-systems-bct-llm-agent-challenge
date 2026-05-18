from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.task_a_review_simulation import router as task_a_router
from app.api.task_b_recommendation import router as task_b_router
from app.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A Nigerian-contextualised behavioural intelligence agent for review simulation "
        "and personalised recommendation."
    ),
)


@app.get("/")
def root() -> dict:
    return {
        "project": settings.app_name,
        "team": "Team Steward Systems",
        "description": (
            "A local, reproducible AI agent application covering review simulation and "
            "personalised recommendation for the DSN x BCT LLM Agent Challenge."
        ),
        "tasks": {
            "task_a": "Task A - User Modelling / Review Simulation",
            "task_b": "Task B - Personalised Recommendation",
        },
        "endpoints": [
            "/health",
            "/docs",
            "/api/task-a/simulate-review",
            "/api/task-b/recommend",
        ],
    }


app.include_router(health_router)
app.include_router(task_a_router)
app.include_router(task_b_router)
