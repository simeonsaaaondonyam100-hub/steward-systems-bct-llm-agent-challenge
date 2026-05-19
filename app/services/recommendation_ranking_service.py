from typing import Any

from app.config import Settings, get_settings
from app.services.item_profile_builder import ItemProfileBuilder
from app.services.nigerian_context_adapter import NigerianContextAdapter
from app.services.retrieval_service import RetrievalService
from app.services.semantic_similarity_service import SemanticSimilarityService
from app.services.user_profile_builder import UserProfile
from app.utils.text_utils import clamp, clean_placeholder_text, keyword_overlap_score


class RecommendationRankingService:
    def __init__(
        self,
        settings: Settings | None = None,
        retrieval_service: RetrievalService | None = None,
        semantic_service: SemanticSimilarityService | None = None,
        context_adapter: NigerianContextAdapter | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.retrieval_service = retrieval_service or RetrievalService()
        self.semantic_service = semantic_service or SemanticSimilarityService()
        self.context_adapter = context_adapter or NigerianContextAdapter()
        self.item_profile_builder = ItemProfileBuilder()
        self.semantic_mode = self.semantic_service.mode

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

        clean_context = clean_placeholder_text(current_context)
        query = f"{profile.description} {' '.join(profile.preferred_terms)} {clean_context}"
        item_texts = [self.item_profile_builder.build_text(item) for item in candidates]
        self.semantic_service.fit_or_load_corpus(item_texts)
        self.semantic_mode = self.semantic_service.mode
        semantic_values = self.semantic_service.batch_similarity(query, item_texts)
        semantic_scores = {
            item["item_id"]: semantic_values[index]
            for index, item in enumerate(candidates)
        }
        ranked = []
        seen_names: set[str] = set()
        tag_cluster_counts: dict[str, int] = {}
        for item in candidates:
            if item.get("name", "").lower() in seen_names:
                continue
            seen_names.add(item.get("name", "").lower())
            metadata = dict(item.get("metadata", {}))
            if item.get("price") is not None:
                metadata["price"] = item["price"]
            item_text = self.item_profile_builder.build_text(item)
            semantic = semantic_scores[item["item_id"]]
            preference, preference_explanation = self._preference_match(profile, item, item_text)
            context, context_explanation = self._context_match(profile, item, item_text, clean_context)
            quality = self._quality_score(metadata)
            nigerian, positives, negatives = self.context_adapter.score_item_context(
                user_text=profile.description,
                context_text=clean_context,
                item_metadata=metadata,
                item_name=item.get("name", ""),
            )
            penalty, penalty_explanation = self._penalty(profile, item, tag_cluster_counts)
            cluster = self._primary_cluster(item)
            tag_cluster_counts[cluster] = tag_cluster_counts.get(cluster, 0) + 1
            final_score = (
                self.settings.semantic_weight * semantic
                + self.settings.preference_weight * preference
                + self.settings.context_weight * context
                + self.settings.quality_weight * quality
                + self.settings.nigerian_context_weight * nigerian
                - self.settings.penalty_weight * penalty
            )
            ranked.append(
                {
                    "item": item,
                    "raw_score": clamp(final_score, 0.0, 1.0),
                    "score": round(clamp(final_score, 0.0, 1.0), 4),
                    "components": {
                        "semantic_similarity": round(semantic, 3),
                        "preference_match": round(preference, 3),
                        "context_match": round(context, 3),
                        "item_quality_or_popularity": round(quality, 3),
                        "nigerian_context_match": round(nigerian, 3),
                        "penalty": round(penalty, 3),
                    },
                    "positive_context": positives,
                    "negative_context": negatives,
                    "context_explanation": context_explanation,
                    "preference_explanation": preference_explanation,
                    "penalty_explanation": penalty_explanation,
                    "cross_domain": item.get("category") not in profile.preferred_categories and bool(profile.preferred_categories),
                }
            )

        ranked.sort(
            key=lambda entry: (
                entry["raw_score"],
                entry["components"]["preference_match"],
                entry["components"]["context_match"],
                entry["components"]["nigerian_context_match"],
                -entry["components"]["penalty"],
                entry["components"]["item_quality_or_popularity"],
            ),
            reverse=True,
        )
        return ranked[:top_k]

    def _preference_match(self, profile: UserProfile, item: dict[str, Any], item_text: str) -> tuple[float, str]:
        score = keyword_overlap_score(" ".join(profile.preferred_terms), item_text)
        reasons = []
        if score > 0:
            reasons.append("item text overlaps with extracted preference terms")
        if item.get("category") in profile.preferred_categories:
            score += 0.35
            reasons.append(f"category matches profile affinity for {item.get('category')}")
        elif profile.preferred_categories and item.get("category") not in profile.preferred_categories:
            score -= 0.12
            reasons.append("category is outside the strongest profile affinities")
        if profile.likes_spice and item.get("metadata", {}).get("spicy"):
            score += 0.20
            reasons.append("spice level fits a pepper-friendly profile")
        if profile.spice_preference == "mild" and int(item.get("metadata", {}).get("spice_level", 0) or 0) <= 2:
            score += 0.18
            reasons.append("mild spice fits user tolerance")
        if profile.portion_preference in {"large", "sharing"} and item.get("metadata", {}).get("portion_size") in {"large", "family", "sharing"}:
            score += 0.18
            reasons.append("portion size fits the user's usual need")
        if profile.price_sensitive and float(item.get("price") or 0) <= 3500:
            score += 0.20
            reasons.append("price fits a value-conscious profile")
        return clamp(score, 0.0, 1.0), "; ".join(reasons) or "limited direct preference overlap"

    def _context_match(
        self,
        profile: UserProfile,
        item: dict[str, Any],
        item_text: str,
        current_context: str | None,
    ) -> tuple[float, str]:
        context_text = current_context or profile.description
        if not clean_placeholder_text(context_text) and profile.limited_profile_evidence:
            return 0.0, "Recommended from cold-start popularity and broad Nigerian-context fit"
        score = self.semantic_service.similarity(context_text, item_text)
        reasons = []
        metadata = item.get("metadata", {})
        lowered = context_text.lower()
        if any(term in lowered for term in ["dinner", "hungry", "filling"]) and metadata.get("portion_size") in {"large", "family", "sharing"}:
            score += 0.20
            reasons.append("portion fits a filling-meal context")
        if any(term in lowered for term in ["office", "lunch", "quick"]) and metadata.get("delivery_time_minutes", 99) <= 35:
            score += 0.18
            reasons.append("delivery time fits an office or quick-meal context")
        if any(term in lowered for term in ["family", "children", "kids"]) and metadata.get("portion_size") in {"family", "sharing", "large"}:
            score += 0.20
            reasons.append("sharing format fits a family context")
        if any(term in lowered for term in ["date", "ambience", "dessert"]) and any(tag in metadata.get("tags", []) for tag in ["date", "dessert", "premium"]):
            score += 0.18
            reasons.append("tags fit ambience or date-night context")
        if any(term in lowered for term in ["budget", "cheap", "not expensive"]) and float(item.get("price") or 0) <= 3500:
            score += 0.16
            reasons.append("price fits the current budget context")
        if score == 0 and not reasons:
            return 0.0, "Recommended from cold-start popularity and broad Nigerian-context fit"
        return clamp(score, 0.0, 1.0), "; ".join(reasons) or "text similarity offers a weak contextual signal"

    def _quality_score(self, metadata: dict[str, Any]) -> float:
        quality = metadata.get("average_rating", metadata.get("quality_score", 3.5))
        popularity = metadata.get("popularity_score", metadata.get("popularity", 50))
        try:
            quality_component = (float(quality) - 1) / 4
            popularity_component = float(popularity) / 100
        except (TypeError, ValueError):
            return 0.5
        return clamp(0.65 * quality_component + 0.35 * popularity_component, 0.0, 1.0)

    def _penalty(self, profile: UserProfile, item: dict[str, Any], tag_cluster_counts: dict[str, int]) -> tuple[float, str | None]:
        metadata = item.get("metadata", {})
        penalties = []
        value = 0.0
        price = float(item.get("price") or 0)
        delivery = int(metadata.get("delivery_time_minutes", 0) or 0)
        spice = int(metadata.get("spice_level", 0) or 0)
        portion = str(metadata.get("portion_size", "")).lower()
        if profile.price_sensitivity_level == "high" and price >= 9000:
            value += 0.45
            penalties.append("high price conflicts with strong price sensitivity")
        if profile.time_sensitive and delivery >= 60:
            value += 0.35
            penalties.append("delivery time conflicts with time sensitivity")
        if profile.spice_preference == "mild" and spice >= 4:
            value += 0.35
            penalties.append("spice level may exceed tolerance")
        if profile.portion_preference in {"large", "sharing"} and portion == "small":
            value += 0.30
            penalties.append("small portion conflicts with profile")
        cluster = self._primary_cluster(item)
        if tag_cluster_counts.get(cluster, 0) >= 3:
            value += 0.20
            penalties.append("similar tag cluster already appears several times")
        return clamp(value, 0.0, 1.0), "; ".join(penalties) if penalties else None

    def _primary_cluster(self, item: dict[str, Any]) -> str:
        tags = item.get("metadata", {}).get("tags", [])
        if tags:
            return str(tags[0])
        return str(item.get("category", "general"))

    def reason_for(self, ranked_entry: dict[str, Any]) -> tuple[str, str]:
        item = ranked_entry["item"]
        components = ranked_entry["components"]
        positives = ranked_entry["positive_context"]
        negatives = ranked_entry["negative_context"]
        context_explanation = ranked_entry["context_explanation"]
        strongest = max(components, key=components.get)
        reason = self._natural_reason(item, components, strongest, ranked_entry)
        if positives:
            context = f"{positives[0]}; {context_explanation}"
        elif negatives:
            context = f"Watch-out: {negatives[0]}"
        else:
            context = context_explanation
        return reason, context

    def _natural_reason(
        self,
        item: dict[str, Any],
        components: dict[str, float],
        strongest: str,
        ranked_entry: dict[str, Any],
    ) -> str:
        name = item["name"]
        tags = [str(tag) for tag in item.get("metadata", {}).get("tags", [])[:3]]
        category = item.get("category", "item").lower()
        portion = item.get("metadata", {}).get("portion_size")
        price = item.get("price")
        delivery = item.get("metadata", {}).get("delivery_time_minutes")

        if strongest == "preference_match":
            base = f"{name} ranks highly because it closely matches the user's taste profile"
        elif strongest == "context_match":
            base = f"{name} ranks highly because it fits the current need"
        elif strongest == "nigerian_context_match":
            base = f"{name} is a strong match because it carries practical Nigerian-context cues"
        elif strongest == "item_quality_or_popularity":
            base = f"{name} stands out because it combines reliable quality signals with broad appeal"
        else:
            base = f"{name} is recommended because it fits the user's profile better than most alternatives"

        details = []
        if tags:
            details.append(f"especially around {', '.join(tags)}")
        if portion in {"large", "family", "sharing"}:
            details.append(f"with a {portion} portion")
        elif portion:
            details.append(f"with a {portion} portion")
        if price and float(price) <= 3500:
            details.append("at a value-conscious price")
        if delivery and int(delivery) <= 35:
            details.append("with delivery timing that suits a quick order")
        if components.get("penalty", 0) > 0:
            details.append("though there are a few fit concerns to watch")

        if details:
            return base + ", " + ", ".join(details[:3]) + "."
        return base + f" as a relevant {category} option."
