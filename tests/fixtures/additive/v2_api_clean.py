"""Example API v2 - additive."""

__all__ = ["greet", "farewell", "VERSION", "greet_formal"]

VERSION = "2.0.0"


def greet(name: str) -> str:
    return f"hello {name}"


def farewell(name: str) -> str:
    return f"goodbye {name}"


def greet_formal(name: str) -> str:
    return f"Good day, {name}"
