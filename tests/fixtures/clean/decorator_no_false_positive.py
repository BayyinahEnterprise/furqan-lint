from typing import Optional


def find_item(item_id: int) -> Optional[dict]:
    if item_id <= 0:
        return None
    return {"id": item_id}


def retry(func):
    return func


@retry
def outer() -> str:
    return "done"
