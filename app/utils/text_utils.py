import math
import re
from collections import Counter


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9']+")
PLACEHOLDER_VALUES = {
    "",
    "string",
    "none",
    "null",
    "n/a",
    "na",
    "example",
    "placeholder",
    "your string",
    "swagger",
}


def tokenize(text: str | None) -> list[str]:
    if not text:
        return []
    return TOKEN_PATTERN.findall(text.lower())


def is_placeholder_text(text: str | None) -> bool:
    if text is None:
        return True
    cleaned = str(text).strip().lower()
    if cleaned in PLACEHOLDER_VALUES:
        return True
    return cleaned.startswith("string ") or cleaned.endswith(" string")


def clean_placeholder_text(text: str | None) -> str:
    return "" if is_placeholder_text(text) else str(text).strip()


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def normalize_score(value: float, lower: float = -1.0, upper: float = 1.0) -> float:
    if upper == lower:
        return 0.0
    return clamp((value - lower) / (upper - lower), 0.0, 1.0)


def keyword_overlap_score(source: str, target: str, keywords: set[str] | None = None) -> float:
    source_tokens = set(tokenize(source))
    target_tokens = set(tokenize(target))
    if keywords:
        source_tokens &= keywords
        target_tokens &= keywords
    if not source_tokens or not target_tokens:
        return 0.0
    overlap = source_tokens & target_tokens
    return len(overlap) / max(len(source_tokens | target_tokens), 1)


def cosine_from_counters(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(left[token] * right[token] for token in left.keys() & right.keys())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def compact_sentence(parts: list[str]) -> str:
    clean = [part.strip().rstrip(".") for part in parts if part and part.strip()]
    if not clean:
        return ""
    return "; ".join(clean) + "."
