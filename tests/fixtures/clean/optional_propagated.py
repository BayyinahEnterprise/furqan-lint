from typing import Optional


def find_user(user_id: int) -> Optional[dict]:
    if user_id <= 0:
        return None
    return {"id": user_id, "name": "test"}


def get_user_name(user_id: int) -> Optional[str]:
    user = find_user(user_id)
    if user is None:
        return None
    return user["name"]
