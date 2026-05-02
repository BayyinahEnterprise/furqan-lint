from typing import Optional


def find(key: str) -> Optional[str]:
    if not key:
        return None
    return f"found:{key}"
