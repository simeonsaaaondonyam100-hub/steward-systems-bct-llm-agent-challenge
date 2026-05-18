from app.models.schemas import RecommendRequest, RecommendResponse, RecommendationItem
from app.services.data_loader import get_data_loader
from app.services.nigerian_context_adapter import NigerianContextAdapter
from app.services.recommendation_ranking_service import RecommendationRankingService
from app.services.user_profile_builder import UserProfileBuilder


class RecommendationAgent:
    ranking_formula = (
        "final_score = 0.30 * semantic_similarity + 0.25 * preference_match + "
        "0.20 * context_match + 0.15 * item_quality_or_popularity + 0.10 * nigerian_context_match"
    )

    def __init__(self) -> None:
        context_adapter = NigerianContextAdapter()
        self.profile_builder = UserProfileBuilder(context_adapter)
        self.ranking_service = RecommendationRankingService(context_adapter=context_adapter)
        self.data_loader = get_data_loader()

    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        profile = self.profile_builder.build(request.user_persona)
        ranked = self.ranking_service.rank(
            profile=profile,
            items=self.data_loader.load_items(),
            current_context=request.current_context,
            candidate_domain=request.candidate_domain,
            top_k=request.top_k,
        )
        recommendations = []
        cold_start_note = (
            "Cold-start mode used: no past reviews supplied, so ranking relies on persona text, current context, "
            "item metadata, and Nigerian-context rules."
            if not request.user_persona.past_reviews
            else "Personal history mode used: past reviews influenced profile strictness, preferences, and complaints."
        )
        for index, entry in enumerate(ranked, start=1):
            item = entry["item"]
            reason, context = self.ranking_service.reason_for(entry)
            recommendations.append(
                RecommendationItem(
                    rank=index,
                    item_id=item["item_id"],
                    item_name=item["name"],
                    name=item["name"],
                    category=item["category"],
                    final_score=entry["score"],
                    score=entry["score"],
                    score_breakdown=entry["components"],
                    reason=reason,
                    context_fit=context,
                    context_fit_explanation=context,
                    cold_start_note=cold_start_note if not request.user_persona.past_reviews else None,
                    metadata=item.get("metadata", {}),
                )
            )

        return RecommendResponse(
            recommendations=recommendations,
            profile_summary=profile.summary,
            cold_start_note=cold_start_note,
            ranking_formula=self.ranking_formula,
        )
