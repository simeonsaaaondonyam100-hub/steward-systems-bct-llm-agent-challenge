from app.models.schemas import ItemInput
from app.services.nigerian_context_adapter import NigerianContextAdapter
from app.services.rating_prediction_service import RatingPrediction
from app.services.user_profile_builder import UserProfile


class ReviewGenerationService:
    def __init__(self, context_adapter: NigerianContextAdapter | None = None) -> None:
        self.context_adapter = context_adapter or NigerianContextAdapter()

    def generate(self, profile: UserProfile, item: ItemInput, prediction: RatingPrediction) -> str:
        rating = prediction.rating
        metadata = item.metadata
        details = self._feature_sentence(item, prediction)
        local_line = self.context_adapter.local_review_line(rating, metadata)
        item_detail = self._item_detail(metadata)
        tone_bridge = self._tone_bridge(profile, rating)

        if rating >= 4.5:
            opener = self._pick(profile, [
                f"I really enjoyed the {item.name}.",
                f"The {item.name} worked very well for me.",
                f"This {item.name} delivered the kind of experience I was hoping for.",
            ])
            closer = self._pick(profile, [
                "I would order it again without thinking too much.",
                "It is the kind of option I can comfortably recommend.",
                "For me, the value and taste came together nicely.",
            ])
        elif rating >= 3.5:
            opener = self._pick(profile, [
                f"The {item.name} was a solid option.",
                f"I had a decent experience with the {item.name}.",
                f"The {item.name} mostly did what I needed.",
            ])
            closer = self._pick(profile, [
                "It is worth trying if the price and timing work for you.",
                "I would not call it perfect, but it made sense overall.",
                "I can see myself picking it again on the right day.",
            ])
        elif rating >= 2.5:
            opener = self._pick(profile, [
                f"The {item.name} was just okay for me.",
                f"I was a bit mixed on the {item.name}.",
                f"The {item.name} had some good points, but it did not fully land.",
            ])
            closer = self._pick(profile, [
                "I might try something else next time unless they improve the weak parts.",
                "It is manageable, but I would not rush back to it.",
                "A few fixes would make the experience much better.",
            ])
        else:
            opener = self._pick(profile, [
                f"I was not impressed with the {item.name}.",
                f"The {item.name} did not meet my expectations.",
                f"This {item.name} was disappointing for what it promised.",
            ])
            closer = self._pick(profile, [
                "For the money, I expected a better experience.",
                "I would choose another option next time.",
                "They need to fix the basics before I can recommend it.",
            ])

        if "Pidgin" in profile.tone_style and rating < 3.5:
            closer = f"{closer} Sha, they can do better."
        elif "Pidgin" in profile.tone_style and rating >= 4:
            closer = f"{closer} No wahala on this one."

        return " ".join(part for part in [opener, item_detail, details, local_line, tone_bridge, closer] if part)

    def reasoning_summary(self, profile: UserProfile, item: ItemInput, prediction: RatingPrediction) -> str:
        tone = self.context_adapter.tone_hint(prediction.rating)
        signal_text = ", ".join(prediction.positive_signals[:3] + prediction.negative_signals[:3])
        if not signal_text:
            signal_text = "limited explicit behavioural signals, so the agent leaned on persona and item metadata"
        return (
            f"Predicted {prediction.rating}/5 for a {profile.summary}. "
            f"The review uses a {tone} tone because the item signals show: {signal_text}."
        )

    def _feature_sentence(self, item: ItemInput, prediction: RatingPrediction) -> str:
        if prediction.positive_signals and prediction.negative_signals:
            return f"I liked that {prediction.positive_signals[0]}, but {prediction.negative_signals[0]}."
        if prediction.positive_signals:
            return f"The strongest point for me was that {prediction.positive_signals[0]}."
        if prediction.negative_signals:
            return f"My main issue is that {prediction.negative_signals[0]}."
        price = f" at NGN {int(item.price):,}" if item.price else ""
        return f"It feels like a practical {item.category.lower()} choice{price}."

    def _item_detail(self, metadata: dict) -> str:
        details = []
        if metadata.get("delivery_time_minutes"):
            minutes = int(metadata["delivery_time_minutes"])
            if minutes <= 30:
                details.append("delivery was quick")
            elif minutes <= 50:
                details.append(f"delivery took about {minutes} minutes")
            else:
                details.append(f"delivery stretched to about {minutes} minutes")
        if metadata.get("portion_size"):
            portion = metadata["portion_size"]
            if portion in {"large", "family", "sharing"}:
                details.append(f"the {portion} portion made sense")
            else:
                details.append(f"the portion was {portion}")
        if metadata.get("spice_level") is not None:
            spice = int(metadata["spice_level"])
            if spice >= 4:
                details.append("the pepper was noticeable")
            elif spice <= 1:
                details.append("the spice was mild")
            else:
                details.append("the spice level was balanced")
        if not details:
            return ""
        return self._join_naturally(details[:3]) + "."

    def _tone_bridge(self, profile: UserProfile, rating: float) -> str:
        if profile.price_sensitivity_level == "high" and rating >= 3.5:
            return "For the price, it felt like a sensible pick."
        if profile.time_sensitive and rating < 4:
            return "Timing matters to me, so that part affected the experience."
        if profile.portion_preference == "sharing" and rating >= 4:
            return "It also works for sharing, which is important for my kind of order."
        if profile.rating_strictness > 0.55 and rating >= 4:
            return "I am not usually easy to impress, so that says something."
        if profile.rating_strictness < 0.35 and rating < 3.5:
            return "Even as someone who gives places room, this one had clear gaps."
        return ""

    def _join_naturally(self, parts: list[str]) -> str:
        if len(parts) == 1:
            return parts[0].capitalize()
        if len(parts) == 2:
            return f"{parts[0].capitalize()} and {parts[1]}"
        return f"{parts[0].capitalize()}, {parts[1]}, and {parts[2]}"

    def _pick(self, profile: UserProfile, options: list[str]) -> str:
        seed = (profile.user_id or profile.description) + profile.tone_style
        return options[sum(ord(char) for char in seed) % len(options)]
