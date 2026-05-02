"""Example API v2 - breaking."""

__all__ = ["greet", "VERSION"]

VERSION = "2.0.0"


def greet(name: str) -> str:
    return f"hello {name}"
