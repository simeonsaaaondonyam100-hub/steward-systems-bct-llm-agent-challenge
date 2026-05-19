from typing import Any

from app.utils.text_utils import clamp, tokenize


class NigerianContextAdapter:
    affordability_terms = {"affordable", "cheap", "budget", "student", "value", "price", "expensive", "cost"}
    spice_terms = {"spicy", "pepper", "peppered", "suya", "asun", "peppery", "hot", "yaji"}
    mild_spice_terms = {"mild", "pepperless"}
    portion_terms = {"filling", "portion", "large", "small", "hungry", "sharing", "family"}
    delivery_terms = {"delivery", "quick", "fast", "traffic", "late", "delay", "lagos", "mainland", "island"}
    local_food_terms = {
        "jollof",
        "suya",
        "shawarma",
        "amala",
        "egusi",
        "bole",
        "zobo",
        "chapman",
        "asun",
        "moi",
        "pepper",
        "soup",
        "small",
        "chops",
    }

    def infer_user_signals(self, text: str) -> dict[str, bool]:
        tokens = set(tokenize(text))
        lowered = text.lower()
        return {
            "price_sensitive": bool(tokens & self.affordability_terms),
            "likes_spice": bool(tokens & self.spice_terms) and "not too much pepper" not in lowered,
            "prefers_mild_spice": bool(tokens & self.mild_spice_terms) or "not too much pepper" in lowered,
            "cares_about_portion": bool(tokens & self.portion_terms),
            "time_sensitive": bool(tokens & self.delivery_terms),
            "nigerian_context": bool(tokens & (self.local_food_terms | {"nigerian", "naija", "lagos"})),
        }

    def score_item_context(
        self,
        user_text: str,
        context_text: str | None,
        item_metadata: dict[str, Any],
        item_name: str = "",
    ) -> tuple[float, list[str], list[str]]:
        combined_text = f"{user_text} {context_text or ''}"
        signals = self.infer_user_signals(combined_text)
        positives: list[str] = []
        negatives: list[str] = []
        score = 0.45

        price = item_metadata.get("price")
        if price is not None:
            try:
                price_value = float(price)
            except (TypeError, ValueError):
                price_value = 0.0
            if signals["price_sensitive"] and price_value <= 3500:
                score += 0.18
                positives.append("price looks reasonable for a budget-conscious Nigerian user")
            elif signals["price_sensitive"] and price_value > 7000:
                score -= 0.20
                negatives.append("price may feel high for a value-focused user")

        spice_level = self._spice_level(item_metadata)
        if signals["likes_spice"] and spice_level >= 4:
            score += 0.16
            positives.append("spice level matches the user's pepper preference")
        elif signals["likes_spice"] and spice_level <= 1:
            score -= 0.08
            negatives.append("item may be too mild for the user's stated taste")
        if signals.get("prefers_mild_spice") and spice_level <= 2:
            score += 0.12
            positives.append("mild spice level fits a low-pepper preference")
        elif signals.get("prefers_mild_spice") and spice_level >= 4:
            score -= 0.16
            negatives.append("pepper level may be too intense for this user")

        portion = str(item_metadata.get("portion_size", "")).lower()
        if signals["cares_about_portion"] and portion in {"large", "family", "generous"}:
            score += 0.14
            positives.append("portion size supports value for money")
        elif signals["cares_about_portion"] and portion == "small":
            score -= 0.15
            negatives.append("small portion may disappoint a filling-meal need")

        delivery_minutes = item_metadata.get("delivery_time_minutes")
        if delivery_minutes is not None:
            try:
                minutes = int(delivery_minutes)
            except (TypeError, ValueError):
                minutes = 0
            if signals["time_sensitive"] and minutes <= 35:
                score += 0.12
                positives.append("delivery time is realistic for a quick Lagos order")
            elif signals["time_sensitive"] and minutes >= 60:
                score -= 0.18
                negatives.append("delivery delay may be painful with Lagos traffic expectations")

        locality = f"{item_name} {' '.join(self._stringify(value) for value in item_metadata.values())}".lower()
        local_overlap = [term for term in self.local_food_terms if term in combined_text.lower() and term in locality]
        if local_overlap:
            score += min(0.18, 0.06 * len(local_overlap))
            positives.append(f"matches local preference cues: {', '.join(local_overlap[:3])}")
        wants_food_context = (
            "food" in combined_text.lower()
            or bool(local_overlap)
            or signals["likes_spice"]
            or signals["cares_about_portion"]
        )
        if wants_food_context and any(term in locality for term in self.local_food_terms):
            score += 0.10
            positives.append("item carries familiar Nigerian food or drink cues")

        return clamp(score, 0.0, 1.0), positives, negatives

    def tone_hint(self, rating: float) -> str:
        if rating >= 4.5:
            return "warm and satisfied, with a natural Nigerian English feel"
        if rating >= 3.5:
            return "balanced and practical, praising the good parts while noting small issues"
        if rating >= 2.5:
            return "mixed and slightly disappointed, but still specific"
        return "direct and dissatisfied without sounding abusive"

    def local_review_line(self, rating: float, metadata: dict[str, Any]) -> str:
        location = metadata.get("location")
        if rating >= 4 and self._spice_level(metadata) >= 4:
            return "The pepper had flavour without overpowering the meal."
        if rating >= 4 and location:
            return f"For {location}, it felt like good value."
        if rating <= 2 and metadata.get("delivery_time_minutes", 0) >= 60:
            return "By the time it arrived, the Lagos delay had already spoiled the mood."
        if rating <= 3 and str(metadata.get("portion_size", "")).lower() == "small":
            return "The portion did not really match the price."
        return "It felt familiar enough for the Nigerian market without overdoing it."

    def _spice_level(self, metadata: dict[str, Any]) -> int:
        value = metadata.get("spice_level", 5 if metadata.get("spicy") else 0)
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _stringify(self, value: Any) -> str:
        if isinstance(value, list):
            return " ".join(str(item) for item in value)
        return str(value)
