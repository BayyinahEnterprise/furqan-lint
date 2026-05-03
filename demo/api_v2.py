"""Document processing API v2."""

from __future__ import annotations

__all__ = ["categorize", "validate_document"]


def validate_document(data: dict) -> dict | None:
    if "title" not in data:
        return None
    return {"title": data["title"], "valid": True}


def categorize(data: dict) -> str:
    return data.get("category", "uncategorized")
