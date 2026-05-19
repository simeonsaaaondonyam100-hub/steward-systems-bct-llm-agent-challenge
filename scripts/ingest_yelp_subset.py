from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


DEFAULT_OUTPUT_DIR = Path("data") / "processed" / "yelp"


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def parse_categories(raw: str | list[str] | None) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        values = raw
    else:
        values = raw.split(",")
    return [value.strip() for value in values if value and value.strip()]


def category_matches(categories: list[str], filters: set[str]) -> bool:
    lowered = {category.lower() for category in categories}
    return bool(lowered & {value.lower() for value in filters})


def normalise_popularity(review_count: int) -> int:
    if review_count <= 0:
        return 0
    return max(1, min(100, int(round(review_count ** 0.5 * 9))))


def load_businesses(path: Path, category_filter: set[str]) -> dict[str, dict[str, Any]]:
    businesses: dict[str, dict[str, Any]] = {}
    for business in iter_jsonl(path):
        categories = parse_categories(business.get("categories"))
        if category_filter and not category_matches(categories, category_filter):
            continue
        business_id = business.get("business_id")
        if not business_id:
            continue
        location = ", ".join(
            part for part in [business.get("city"), business.get("state")] if part
        ) or "Unknown"
        review_count = int(business.get("review_count") or 0)
        stars = float(business.get("stars") or 0)
        businesses[business_id] = {
            "item_id": business_id,
            "name": business.get("name") or "Unnamed Yelp Business",
            "category": "Food" if category_matches(categories, {"Restaurants", "Food", "Cafes", "Bars"}) else "Restaurant",
            "price": None,
            "metadata": {
                "source": "yelp_open_dataset",
                "yelp_business_id": business_id,
                "tags": categories,
                "location": location,
                "category": "Food",
                "average_rating": stars,
                "quality_score": stars,
                "review_count": review_count,
                "popularity_score": normalise_popularity(review_count),
                "spice_level": 0,
                "delivery_time_minutes": 0,
                "portion_size": "unknown",
            },
        }
    return businesses


def collect_reviews(
    path: Path,
    allowed_businesses: dict[str, dict[str, Any]],
    max_reviews: int,
) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for review in iter_jsonl(path):
        business_id = review.get("business_id")
        if business_id not in allowed_businesses:
            continue
        reviews.append(
            {
                "review_id": review.get("review_id") or f"yelp_review_{len(reviews) + 1}",
                "user_id": review.get("user_id") or "unknown_yelp_user",
                "item_id": business_id,
                "rating": float(review.get("stars") or 0),
                "review": review.get("text") or "",
                "timestamp": review.get("date"),
                "source": "yelp_open_dataset",
            }
        )
        if len(reviews) >= max_reviews:
            break
    return reviews


def apply_minimum_counts(
    reviews: list[dict[str, Any]],
    min_user_reviews: int,
    min_business_reviews: int,
) -> list[dict[str, Any]]:
    user_counts = Counter(review["user_id"] for review in reviews)
    item_counts = Counter(review["item_id"] for review in reviews)
    return [
        review
        for review in reviews
        if user_counts[review["user_id"]] >= min_user_reviews
        and item_counts[review["item_id"]] >= min_business_reviews
    ]


def load_users(path: Path | None, review_user_ids: set[str]) -> list[dict[str, Any]]:
    users_by_id: dict[str, dict[str, Any]] = {}
    if path and path.exists():
        for user in iter_jsonl(path):
            user_id = user.get("user_id")
            if not user_id or user_id not in review_user_ids:
                continue
            name = user.get("name") or f"Yelp user {user_id[:8]}"
            users_by_id[user_id] = {
                "user_id": user_id,
                "name": name,
                "description": (
                    f"Yelp Open Dataset user with {user.get('review_count', 0)} reviews "
                    f"and average rating {user.get('average_stars', 'unknown')}."
                ),
                "review_count": user.get("review_count"),
                "average_stars": user.get("average_stars"),
                "source": "yelp_open_dataset",
            }
    for user_id in review_user_ids:
        users_by_id.setdefault(
            user_id,
            {
                "user_id": user_id,
                "name": f"Yelp user {user_id[:8]}",
                "description": "An anonymised Yelp Open Dataset user.",
                "source": "yelp_open_dataset",
            },
        )
    return sorted(users_by_id.values(), key=lambda user: user["user_id"])


def write_output(
    output_dir: Path,
    users: list[dict[str, Any]],
    items: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "users.json").write_text(json.dumps(users, indent=2), encoding="utf-8")
    (output_dir / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    (output_dir / "reviews.json").write_text(json.dumps(reviews, indent=2), encoding="utf-8")
    readme = f"""# Yelp Open Dataset Processed Subset

This folder was generated by `scripts/ingest_yelp_subset.py`.

The full Yelp Open Dataset is not included in this repository. These files are a small converted subset in the same internal schema used by the Steward Systems agent.

## Source Inputs

- Business file: `{args.business_file}`
- Review file: `{args.review_file}`
- User file: `{args.user_file or 'not provided'}`

## Output Counts

- Users: {len(users)}
- Items: {len(items)}
- Reviews: {len(reviews)}

Default app startup still uses `data/sample/`. To experiment with this processed subset, point `STEWARD_DATA_DIR` to this folder.
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")


def ingest(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    category_filter = set(parse_categories(args.category_filter))
    businesses = load_businesses(Path(args.business_file), category_filter)
    reviews = collect_reviews(Path(args.review_file), businesses, args.max_reviews)
    reviews = apply_minimum_counts(reviews, args.min_user_reviews, args.min_business_reviews)
    used_item_ids = {review["item_id"] for review in reviews}
    items = [business for item_id, business in businesses.items() if item_id in used_item_ids]
    users = load_users(Path(args.user_file) if args.user_file else None, {review["user_id"] for review in reviews})
    return users, items, reviews


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert a small Yelp Open Dataset subset into app JSON files.")
    parser.add_argument("--business-file", required=True)
    parser.add_argument("--review-file", required=True)
    parser.add_argument("--user-file")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--max-reviews", type=int, default=5000)
    parser.add_argument("--min-user-reviews", type=int, default=3)
    parser.add_argument("--min-business-reviews", type=int, default=3)
    parser.add_argument("--category-filter", default="Restaurants")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    users, items, reviews = ingest(args)
    output_dir = Path(args.output_dir)
    write_output(output_dir, users, items, reviews, args)
    print(
        f"Wrote Yelp subset to {output_dir}: "
        f"{len(users)} users, {len(items)} items, {len(reviews)} reviews."
    )


if __name__ == "__main__":
    main()
