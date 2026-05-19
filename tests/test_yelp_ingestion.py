import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "yelp"


def run_ingestion(output_dir: Path, max_reviews: int = 5) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ingest_yelp_subset.py"),
            "--business-file",
            str(FIXTURE_DIR / "business.jsonl"),
            "--review-file",
            str(FIXTURE_DIR / "review.jsonl"),
            "--user-file",
            str(FIXTURE_DIR / "user.jsonl"),
            "--output-dir",
            str(output_dir),
            "--max-reviews",
            str(max_reviews),
            "--min-user-reviews",
            "1",
            "--min-business-reviews",
            "1",
            "--category-filter",
            "Restaurants,Food,Cafes",
        ],
        cwd=ROOT,
        check=True,
    )


def test_yelp_ingestion_maps_businesses_reviews_and_users(tmp_path: Path) -> None:
    output_dir = tmp_path / "yelp"

    run_ingestion(output_dir)

    users = json.loads((output_dir / "users.json").read_text(encoding="utf-8"))
    items = json.loads((output_dir / "items.json").read_text(encoding="utf-8"))
    reviews = json.loads((output_dir / "reviews.json").read_text(encoding="utf-8"))

    assert {item["item_id"] for item in items} == {"biz_1", "biz_3"}
    assert items[0]["metadata"]["tags"]
    assert items[0]["metadata"]["location"]
    assert "average_rating" in items[0]["metadata"]
    assert "popularity_score" in items[0]["metadata"]

    assert len(reviews) == 5
    assert reviews[0]["item_id"] == "biz_1"
    assert reviews[0]["rating"] == 5
    assert reviews[0]["review"]
    assert reviews[0]["timestamp"]

    assert {user["user_id"] for user in users} >= {"user_a", "user_b", "user_c"}
    assert users[0]["description"]
    assert (output_dir / "README.md").exists()


def test_yelp_ingestion_respects_max_reviews(tmp_path: Path) -> None:
    output_dir = tmp_path / "limited_yelp"

    run_ingestion(output_dir, max_reviews=2)

    reviews = json.loads((output_dir / "reviews.json").read_text(encoding="utf-8"))
    assert len(reviews) == 2
