from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.utils.text_utils import is_placeholder_text


class PastReview(BaseModel):
    item_name: str
    category: str
    rating: float = Field(ge=1, le=5)
    review: str


class UserPersona(BaseModel):
    user_id: str | None = None
    description: str = Field(min_length=3)
    past_reviews: list[PastReview] = Field(default_factory=list)


class ItemInput(BaseModel):
    item_id: str
    name: str
    category: str
    price: float | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def reject_placeholder_name(cls, value: str) -> str:
        if is_placeholder_text(value):
            raise ValueError("item.name must be a real item name, not a placeholder")
        return value.strip()

    @field_validator("category")
    @classmethod
    def reject_placeholder_category(cls, value: str) -> str:
        if is_placeholder_text(value):
            raise ValueError("item.category must be a real category, not a placeholder")
        return value.strip()


class SimulateReviewRequest(BaseModel):
    user_persona: UserPersona
    item: ItemInput


class SimulateReviewResponse(BaseModel):
    predicted_rating: float
    predicted_star_rating: int = Field(ge=1, le=5)
    generated_review: str
    behavioural_reasoning_summary: str
    positive_signals: list[str]
    negative_signals: list[str]
    confidence: float = Field(ge=0, le=1)
    user_profile_summary: str


class RecommendRequest(BaseModel):
    user_persona: UserPersona
    current_context: str | None = None
    candidate_domain: str | None = Field(
        default=None,
        description="Optional category/domain filter. The Swagger example also accepts category as a friendly alias.",
    )
    top_k: int = Field(default=5, ge=1, le=20)

    @model_validator(mode="before")
    @classmethod
    def accept_category_alias(cls, values: object) -> object:
        if isinstance(values, dict) and "candidate_domain" not in values and "category" in values:
            values = dict(values)
            values["candidate_domain"] = values.get("category")
        return values

    @field_validator("candidate_domain")
    @classmethod
    def normalize_domain(cls, value: str | None) -> str | None:
        if is_placeholder_text(value):
            return None
        return value.strip().lower() if value else None


class RecommendationItem(BaseModel):
    rank: int
    item_id: str
    item_name: str
    name: str
    category: str
    final_score: float = Field(ge=0, le=1)
    score: float = Field(ge=0, le=1)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    reason: str
    context_fit: str
    context_fit_explanation: str
    preference_match_explanation: str
    penalty_explanation: str | None = None
    cold_start_note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecommendResponse(BaseModel):
    recommendations: list[RecommendationItem]
    profile_summary: str
    cold_start_note: str
    ranking_formula: str
    semantic_mode: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
