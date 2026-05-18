from fastapi import APIRouter

from app.config import get_settings
from app.models.schemas import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.service_name, version=settings.app_version)
