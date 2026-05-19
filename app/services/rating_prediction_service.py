from dataclasses import dataclass

from app.models.schemas import ItemInput
from app.services.item_profile_builder import ItemProfileBuilder
from app.services.nigerian_context_adapter import NigerianContextAdapter
from app.services.user_profile_builder import UserProfile
from app.utils.text_utils import clamp, keyword_overlap_score


@dataclass
class RatingPrediction:
    rating: float
    positive_signals: list[str]
    negative_signals: list[str]
    confidence: float


class RatingPredictionService:
    def __init__(self, context_adapter: NigerianContextAdapter | None = None) -> None:
        self.context_adapter = context_adapter or NigerianContextAdapter()
        self.item_profile_builder = ItemProfileBuilder()

    def predict(self, profile: UserProfile, item: ItemInput) -> RatingPrediction:
        metadata = self.item_profile_builder.as_metadata(item)
        item_text = self.item_profile_builder.build_text(item)
        user_text = f"{profile.description} {' '.join(profile.preferred_terms)} {' '.join(profile.common_complaints)}"

        preference_match = keyword_overlap_score(user_text, item_text)
        context_score, context_positive, context_negative = self.context_adapter.score_item_context(
            user_text=user_text,
            context_text=None,
            item_metadata=metadata,
            item_name=item.name,
        )

        rating = profile.average_rating
        positives: list[str] = []
        negatives: list[str] = []

        if preference_match > 0.06:
            rating += 0.35 + min(preference_match, 0.4)
            positives.append("target item overlaps with the user's stated preferences")
        if item.category in profile.preferred_categories:
            affinity = profile.category_affinity.get(item.category, 0.5)
            rating += 0.20 + affinity * 0.20
            positives.append(f"user has previously rated {item.category} items positively")

        rating += (context_score - 0.5) * 1.7
        positives.extend(context_positive)
        negatives.extend(context_negative)

        rating += self._quality_adjustment(metadata, positives, negatives)
        rating -= profile.rating_strictness * 0.30
        if profile.price_sensitivity_level == "high" and (item.price or metadata.get("price", 0)) and float(item.price or metadata.get("price", 0)) > 8000:
            rating -= 0.35
            negatives.append("price sensitivity suggests this item may feel too expensive")
        if profile.spice_preference == "mild" and int(metadata.get("spice_level", 0) or 0) >= 4:
            rating -= 0.25
            negatives.append("spice level may be higher than the user's tolerance")
        if profile.portion_preference in {"large", "sharing"} and str(metadata.get("portion_size", "")).lower() == "small":
            rating -= 0.25
            negatives.append("portion size conflicts with the user's usual need")

        rounded_rating = round(clamp(rating, 1.0, 5.0), 1)
        if rounded_rating < 3 and not negatives:
            negatives.append("limited evidence that this item matches the user's preferences or context")
            rounded_rating = max(rounded_rating, 2.5)
        confidence = self._confidence(profile.history_count, abs(context_score - 0.5), preference_match)
        return RatingPrediction(
            rating=rounded_rating,
            positive_signals=positives[:8],
            negative_signals=negatives[:8],
            confidence=confidence,
        )

    def _quality_adjustment(self, metadata: dict, positives: list[str], negatives: list[str]) -> float:
        adjustment = 0.0
        popularity = metadata.get("popularity_score", metadata.get("popularity"))
        quality_score = metadata.get("average_rating", metadata.get("quality_score"))
        if isinstance(quality_score, int | float):
            adjustment += (float(quality_score) - 3.5) * 0.18
            if quality_score >= 4.2:
                positives.append("sample item metadata suggests strong quality")
        if isinstance(popularity, int | float) and popularity >= 80:
            adjustment += 0.10
            positives.append("item has strong sample popularity")
        if metadata.get("delivery_time_minutes", 0) and int(metadata.get("delivery_time_minutes", 0)) >= 75:
            adjustment -= 0.25
            negatives.append("delivery time is likely too slow for a satisfying experience")
        if isinstance(quality_score, int | float) and quality_score <= 3.1:
            adjustment -= 0.12
            negatives.append("sample item metadata suggests weaker quality")
        return adjustment

    def _confidence(self, history_count: int, context_distance: float, preference_match: float) -> float:
        history_component = min(history_count / 8, 1.0) * 0.35
        signal_component = min(context_distance * 1.6 + preference_match, 1.0) * 0.45
        base = 0.20
        return round(clamp(base + history_component + signal_component, 0.0, 1.0), 2)
