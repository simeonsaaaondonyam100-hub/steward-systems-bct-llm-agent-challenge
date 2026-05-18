from typing import Any

from app.config import Settings, get_settings
from app.services.item_profile_builder import ItemProfileBuilder
from app.services.nigerian_context_adapter import NigerianContextAdapter
from app.services.retrieval_service import RetrievalService
from app.services.user_profile_builder import UserProfile
from app.utils.text_utils import clamp, keyword_overlap_score


class RecommendationRankingService:
    def __init__(
        self,
        settings: Settings | None = None,
        retrieval_service: RetrievalService | None = None,
        context_adapter: NigerianContextAdapter | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.retrieval_service = retrieval_service or RetrievalService()
        self.context_adapter = context_adapter or NigerianContextAdapter()
        self.item_profile_builder = ItemProfileBuilder()

    def rank(
        self,
        profile: UserProfile,
        items: list[dict[str, Any]],
        current_context: str | None,
        candidate_domain: str | None,
        top_k: int,
    ) -> list[dict[str, Any]]:
        candidates = [
            item for item in items if not candidate_domain or item.get("category", "").lower() == candidate_domain
        ]
        if not candidates:
            candidates = items

        query = f"{profile.description} {' '.join(profile.preferred_terms)} {current_context or ''}"
        semantic_scores = self.retrieval_service.score_items(query, candidates)
        ranked = []
        seen_names: set[str] = set()
        for item in candidates:
            if item.get("name", "").lower() in seen_names:
                continue
            seen_names.add(item.get("name", "").lower())
            metadata = dict(item.get("metadata", {}))
            if item.get("price") is not None:
                metadata["price"] = item["price"]
            item_text = self.item_profile_builder.build_text(item)
            semantic = semantic_scores[item["item_id"]]
            preference = self._preference_match(profile, item, item_text)
            context = self.retrieval_service.similarity(current_context or profile.description, item_text)
            quality = self._quality_score(metadata)
            nigerian, positives, negatives = self.context_adapter.score_item_context(
                user_text=profile.description,
                context_text=current_context,
                item_metadata=metadata,
                item_name=item.get("name", ""),
            )
            final_score = (
                self.settings.semantic_weight * semantic
                + self.settings.preference_weight * preference
                + self.settings.context_weight * context
                + self.settings.quality_weight * quality
                + self.settings.nigerian_context_weight * nigerian
            )
            ranked.append(
                {
                    "item": item,
                    "score": round(clamp(final_score, 0.0, 1.0), 4),
                    "components": {
                        "semantic_similarity": round(semantic, 3),
                        "preference_match": round(preference, 3),
                        "context_match": round(context, 3),
                        "item_quality_or_popularity": round(quality, 3),
                        "nigerian_context_match": round(nigerian, 3),
                    },
                    "positive_context": positives,
                    "negative_context": negatives,
                    "cross_domain": item.get("category") not in profile.preferred_categories and bool(profile.preferred_categories),
                }
            )

        ranked.sort(key=lambda entry: entry["score"], reverse=True)
        return ranked[:top_k]

    def _preference_match(self, profile: UserProfile, item: dict[str, Any], item_text: str) -> float:
        score = keyword_overlap_score(" ".join(profile.preferred_terms), item_text)
        if item.get("category") in profile.preferred_categories:
            score += 0.35
        elif profile.preferred_categories and item.get("category") not in profile.preferred_categories:
            score -= 0.12
        if profile.likes_spice and item.get("metadata", {}).get("spicy"):
            score += 0.20
        if profile.spice_preference == "mild" and int(item.get("metadata", {}).get("spice_level", 0) or 0) <= 2:
            score += 0.18
        if profile.portion_preference in {"large", "sharing"} and item.get("metadata", {}).get("portion_size") in {"large", "family", "sharing"}:
            score += 0.18
        if profile.price_sensitive and float(item.get("price") or 0) <= 3500:
            score += 0.20
        return clamp(score, 0.0, 1.0)

    def _quality_score(self, metadata: dict[str, Any]) -> float:
        quality = metadata.get("average_rating", metadata.get("quality_score", 3.5))
        popularity = metadata.get("popularity_score", metadata.get("popularity", 50))
        try:
            quality_component = (float(quality) - 1) / 4
            popularity_component = float(popularity) / 100
        except (TypeError, ValueError):
            return 0.5
        return clamp(0.65 * quality_component + 0.35 * popularity_component, 0.0, 1.0)

    def reason_for(self, ranked_entry: dict[str, Any]) -> tuple[str, str]:
        item = ranked_entry["item"]
        components = ranked_entry["components"]
        positives = ranked_entry["positive_context"]
        negatives = ranked_entry["negative_context"]
        strongest = max(components, key=components.get)
        breakdown = ", ".join(f"{key.replace('_', ' ')}={value:.2f}" for key, value in components.items())
        reason = (
            f"Recommended because {item['name']} scores strongest on {strongest.replace('_', ' ')}. "
            f"Breakdown: {breakdown}."
        )
        if positives:
            context = positives[0]
        elif negatives:
            context = f"Watch-out: {negatives[0]}"
        else:
            context = "Context fit is based mainly on text similarity and item quality metadata."
        return reason, context
