from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT / "data" / "sample"


def main() -> None:
    users = json.loads((SAMPLE_DIR / "users.json").read_text(encoding="utf-8"))
    items = json.loads((SAMPLE_DIR / "items.json").read_text(encoding="utf-8"))
    reviews = json.loads((SAMPLE_DIR / "reviews.json").read_text(encoding="utf-8"))

    item_ids = {item["item_id"] for item in items}
    user_ids = {user["user_id"] for user in users}
    invalid = [
        review
        for review in reviews
        if review["user_id"] not in user_ids or review["item_id"] not in item_ids or not 1 <= review["rating"] <= 5
    ]
    if invalid:
        raise ValueError(f"Found invalid review rows: {invalid[:3]}")

    required_metadata = {
        "spice_level",
        "delivery_time_minutes",
        "portion_size",
        "location",
        "category",
        "tags",
        "popularity_score",
        "average_rating",
    }
    invalid_items = [item["item_id"] for item in items if not required_metadata <= set(item.get("metadata", {}))]
    if invalid_items:
        raise ValueError(f"Items missing required metadata: {invalid_items[:5]}")

    print(f"Prepared sample data: {len(users)} users, {len(items)} items, {len(reviews)} reviews.")


if __name__ == "__main__":
    main()
