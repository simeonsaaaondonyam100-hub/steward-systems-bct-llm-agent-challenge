from collections import Counter
from dataclasses import dataclass

from app.models.schemas import PastReview, UserPersona
from app.services.nigerian_context_adapter import NigerianContextAdapter
from app.utils.text_utils import clean_placeholder_text, is_placeholder_text, tokenize


@dataclass
class UserProfile:
    user_id: str | None
    description: str
    average_rating: float
    rating_strictness: float
    preferred_categories: list[str]
    category_affinity: dict[str, float]
    preferred_terms: list[str]
    common_complaints: list[str]
    positive_preference_signals: list[str]
    negative_complaint_signals: list[str]
    tone_style: str
    price_sensitive: bool
    price_sensitivity_level: str
    likes_spice: bool
    spice_preference: str
    time_sensitive: bool
    cares_about_portion: bool
    portion_preference: str
    nigerian_context: bool
    history_count: int
    limited_profile_evidence: bool

    @property
    def summary(self) -> str:
        if self.limited_profile_evidence:
            return (
                "limited profile evidence; using cold-start defaults; "
                f"price sensitivity: {self.price_sensitivity_level}; spice preference: {self.spice_preference}; "
                f"portion preference: {self.portion_preference}; tone: {self.tone_style}"
            )
        strictness = "strict" if self.rating_strictness > 0.55 else "generous" if self.rating_strictness < 0.35 else "balanced"
        preferences = ", ".join(self.preferred_terms[:5]) or "general quality"
        categories = ", ".join(self.preferred_categories[:3]) or "limited category evidence"
        return (
            f"{strictness} reviewer with interest in {categories}; strongest preference cues: {preferences}; "
            f"price sensitivity: {self.price_sensitivity_level}; spice preference: {self.spice_preference}; "
            f"portion preference: {self.portion_preference}; tone: {self.tone_style}"
        )


class UserProfileBuilder:
    positive_terms = {
        "tasty",
        "fresh",
        "fast",
        "quick",
        "affordable",
        "spicy",
        "filling",
        "clean",
        "crispy",
        "value",
        "portion",
        "smooth",
        "generous",
        "hot",
        "neat",
        "premium",
        "healthy",
        "protein",
        "durable",
        "local",
        "sharing",
    }
    complaint_terms = {
        "late",
        "delay",
        "expensive",
        "cold",
        "small",
        "bland",
        "soggy",
        "slow",
        "salty",
        "dry",
        "careless",
        "inflated",
        "weak",
        "oily",
        "watery",
        "stale",
        "tiny",
        "burnt",
    }

    def __init__(self, context_adapter: NigerianContextAdapter | None = None) -> None:
        self.context_adapter = context_adapter or NigerianContextAdapter()

    def build(self, persona: UserPersona) -> UserProfile:
        real_reviews = [review for review in persona.past_reviews if self._has_real_review_evidence(review)]
        clean_description = clean_placeholder_text(persona.description)
        ratings = [review.rating for review in real_reviews]
        average_rating = sum(ratings) / len(ratings) if ratings else 3.5
        spread_penalty = 0.0
        if ratings:
            low_ratings = sum(1 for rating in ratings if rating <= 2)
            spread_penalty = low_ratings / len(ratings) * 0.25
        rating_strictness = max(0.0, min(1.0, (4.6 - average_rating) / 2.6 + spread_penalty))

        category_counts = Counter(clean_placeholder_text(review.category) for review in real_reviews if review.rating >= 4 and not is_placeholder_text(review.category))
        inferred_categories = self._infer_categories_from_text(clean_description)
        for category in inferred_categories:
            category_counts[category] += 2
        all_category_counts = Counter(clean_placeholder_text(review.category) for review in real_reviews if not is_placeholder_text(review.category))
        category_affinity = {
            category: round(category_counts.get(category, 0) / max(count, 1), 2)
            for category, count in all_category_counts.items()
        }
        review_text = " ".join(clean_placeholder_text(review.review) for review in real_reviews)
        positive_item_text = " ".join(
            f"{clean_placeholder_text(review.item_name)} {clean_placeholder_text(review.category)}"
            for review in real_reviews
            if review.rating >= 4 and not is_placeholder_text(review.item_name)
        )
        negative_item_text = " ".join(
            f"{clean_placeholder_text(review.item_name)} {clean_placeholder_text(review.category)}"
            for review in real_reviews
            if review.rating <= 2 and not is_placeholder_text(review.item_name)
        )
        combined_text = f"{clean_description} {review_text} {positive_item_text} {positive_item_text} {negative_item_text}"
        tokens = tokenize(combined_text)
        token_counts = Counter(token for token in tokens if len(token) > 2 and not is_placeholder_text(token))

        preferred = [term for term, _ in token_counts.most_common() if term in self.positive_terms]
        if not preferred and clean_description:
            preferred = [term for term, _ in token_counts.most_common(8)]

        complaints = [term for term, _ in token_counts.most_common() if term in self.complaint_terms]
        signals = self.context_adapter.infer_user_signals(combined_text)
        tone = self._infer_tone(persona.past_reviews)
        price_level = self._price_sensitivity_level(combined_text, persona.past_reviews)
        spice_preference = self._spice_preference(combined_text)
        portion_preference = self._portion_preference(combined_text)

        return UserProfile(
            user_id=persona.user_id,
            description=clean_description,
            average_rating=average_rating,
            rating_strictness=rating_strictness,
            preferred_categories=[category for category, _ in category_counts.most_common()],
            category_affinity=category_affinity,
            preferred_terms=preferred[:10],
            common_complaints=complaints[:8],
            positive_preference_signals=preferred[:10],
            negative_complaint_signals=complaints[:8],
            tone_style=tone,
            price_sensitive=signals["price_sensitive"],
            price_sensitivity_level=price_level,
            likes_spice=signals["likes_spice"],
            spice_preference=spice_preference,
            time_sensitive=signals["time_sensitive"],
            cares_about_portion=signals["cares_about_portion"],
            portion_preference=portion_preference,
            nigerian_context=signals["nigerian_context"],
            history_count=len(real_reviews),
            limited_profile_evidence=not clean_description and not real_reviews,
        )

    def _infer_tone(self, reviews: list[PastReview]) -> str:
        if not reviews:
            return "practical, concise, Nigerian-context aware"
        text = " ".join(review.review for review in reviews).lower()
        if any(word in text for word in ["abeg", "sha", "jare", "wahala"]):
            return "casual Nigerian English with mild Pidgin"
        if len(text) / max(len(reviews), 1) > 120:
            return "detailed and balanced"
        return "short, practical, and direct"

    def _price_sensitivity_level(self, text: str, reviews: list[PastReview]) -> str:
        lowered = text.lower()
        budget_terms = ["budget", "affordable", "cheap", "student", "nysc", "price", "pocket", "value"]
        premium_terms = ["premium", "does not mind paying", "quality", "date-night", "ambience"]
        complaint_count = sum(1 for review in reviews if review.rating <= 3 and any(term in review.review.lower() for term in ["expensive", "price", "money", "cost"]))
        if any(term in lowered for term in budget_terms) or complaint_count >= 2:
            return "high"
        if any(term in lowered for term in premium_terms):
            return "low"
        return "medium"

    def _spice_preference(self, text: str) -> str:
        lowered = text.lower()
        if any(phrase in lowered for phrase in ["not too much pepper", "mild spice", "too spicy", "pepperless"]):
            return "mild"
        if any(term in lowered for term in ["spice lover", "peppery", "spicy", "suya", "asun", "pepper soup"]):
            return "high"
        return "medium"

    def _portion_preference(self, text: str) -> str:
        lowered = text.lower()
        if any(term in lowered for term in ["family", "sharing", "group", "office hangout", "birthday"]):
            return "sharing"
        if any(term in lowered for term in ["filling", "large", "portion", "hungry"]):
            return "large"
        return "standard"

    def _infer_categories_from_text(self, text: str) -> list[str]:
        lowered = text.lower()
        categories = []
        if any(term in lowered for term in ["food", "meal", "restaurant", "jollof", "suya", "shawarma", "pepper soup", "snack"]):
            categories.append("Food")
        if any(term in lowered for term in ["drink", "zobo", "chapman", "juice", "low sugar"]):
            categories.append("Drink")
        if any(term in lowered for term in ["book", "reading", "stories", "literature"]):
            categories.append("Book")
        if any(term in lowered for term in ["movie", "entertainment", "stream", "nollywood"]):
            categories.append("Movie")
        if any(term in lowered for term in ["product", "electronics", "durable", "grocery", "router", "power bank", "fan"]):
            categories.append("Product")
        return categories

    def _has_real_review_evidence(self, review: PastReview) -> bool:
        return not (
            is_placeholder_text(review.item_name)
            and is_placeholder_text(review.category)
            and is_placeholder_text(review.review)
        )
