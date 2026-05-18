from app.models.schemas import SimulateReviewRequest, SimulateReviewResponse
from app.services.nigerian_context_adapter import NigerianContextAdapter
from app.services.rating_prediction_service import RatingPredictionService
from app.services.review_generation_service import ReviewGenerationService
from app.services.user_profile_builder import UserProfileBuilder


class ReviewSimulationAgent:
    def __init__(self) -> None:
        context_adapter = NigerianContextAdapter()
        self.profile_builder = UserProfileBuilder(context_adapter)
        self.rating_service = RatingPredictionService(context_adapter)
        self.review_service = ReviewGenerationService(context_adapter)

    def simulate(self, request: SimulateReviewRequest) -> SimulateReviewResponse:
        profile = self.profile_builder.build(request.user_persona)
        prediction = self.rating_service.predict(profile, request.item)
        review = self.review_service.generate(profile, request.item, prediction)
        reasoning = self.review_service.reasoning_summary(profile, request.item, prediction)
        return SimulateReviewResponse(
            predicted_rating=prediction.rating,
            generated_review=review,
            behavioural_reasoning_summary=reasoning,
            positive_signals=prediction.positive_signals,
            negative_signals=prediction.negative_signals,
            confidence=prediction.confidence,
            user_profile_summary=profile.summary,
        )
