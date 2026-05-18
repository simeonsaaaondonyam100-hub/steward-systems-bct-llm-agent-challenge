import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import get_settings


class DataLoader:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or get_settings().data_dir

    def _load_json(self, filename: str) -> list[dict[str, Any]]:
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Sample data file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def load_users(self) -> list[dict[str, Any]]:
        return self._load_json("users.json")

    def load_items(self) -> list[dict[str, Any]]:
        return self._load_json("items.json")

    def load_reviews(self) -> list[dict[str, Any]]:
        return self._load_json("reviews.json")

    def get_user_history(self, user_id: str | None) -> list[dict[str, Any]]:
        if not user_id:
            return []
        items_by_id = {item["item_id"]: item for item in self.load_items()}
        history = []
        for review in self.load_reviews():
            if review.get("user_id") == user_id:
                item = items_by_id.get(review.get("item_id"), {})
                history.append(
                    {
                        "item_name": item.get("name", review.get("item_id", "Unknown item")),
                        "category": item.get("category", "Unknown"),
                        "rating": review["rating"],
                        "review": review["review"],
                    }
                )
        return history


@lru_cache
def get_data_loader() -> DataLoader:
    return DataLoader()
