from typing import Optional


def fetch_a() -> Optional[str]:
    return None


def fetch_b() -> Optional[int]:
    return None


def aggregate() -> dict:
    a = fetch_a()
    b = fetch_b()
    return {"a": a, "b": b}
