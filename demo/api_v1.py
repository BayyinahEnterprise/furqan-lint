"""Document processing API v1."""

from __future__ import annotations

__all__ = ["classify", "process_intake", "validate_document"]


def validate_document(data: dict) -> dict | None:
    if "title" not in data:
        return None
    return {"title": data["title"], "valid": True}


def process_intake(data: dict) -> str | None:
    result = validate_document(data)
    if result is None:
        return None
    return f"accepted: {result['title']}"


def classify(data: dict) -> str:
    return data.get("category", "uncategorized")
