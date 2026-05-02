"""Example API v1."""

__all__ = ["greet", "farewell", "VERSION"]

VERSION = "1.0.0"


def greet(name: str) -> str:
    return f"hello {name}"


def farewell(name: str) -> str:
    return f"goodbye {name}"
