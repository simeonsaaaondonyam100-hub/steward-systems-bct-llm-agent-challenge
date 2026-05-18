from typing import Any

from app.models.schemas import ItemInput


class ItemProfileBuilder:
    def build_text(self, item: ItemInput | dict[str, Any]) -> str:
        if isinstance(item, ItemInput):
            metadata = item.metadata
            price = item.price
            name = item.name
            category = item.category
        else:
            metadata = item.get("metadata", {})
            price = item.get("price")
            name = item.get("name", "")
            category = item.get("category", "")

        metadata_text = " ".join(
            f"{key} {' '.join(value) if isinstance(value, list) else value}" for key, value in metadata.items()
        )
        return f"{name} {category} price {price or metadata.get('price', '')} {metadata_text}".strip()

    def as_metadata(self, item: ItemInput | dict[str, Any]) -> dict[str, Any]:
        if isinstance(item, ItemInput):
            metadata = dict(item.metadata)
            if item.price is not None:
                metadata["price"] = item.price
            return metadata
        metadata = dict(item.get("metadata", {}))
        if item.get("price") is not None:
            metadata["price"] = item.get("price")
        return metadata
