from typing import Optional


def find_item(item_id: int) -> Optional[dict]:
    if item_id <= 0:
        return None
    return {"id": item_id}


def outer() -> str:
    def inner():
        result = find_item(1)
        return result
    return "done"
