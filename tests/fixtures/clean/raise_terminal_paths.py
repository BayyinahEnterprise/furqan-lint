"""D24 must stay silent: every path either returns or exits.

v1.0.1 regression fixture for the raise-terminal false positive.
Before v1.0.1 the adapter skipped ``raise`` statements, so a final
``raise`` (or ``else: raise``) looked like a fall-through and D24
reported a missing return on code that cannot fall through. mypy
accepts every function below.
"""

from __future__ import annotations

import os
import sys


def grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    raise ValueError("below B")


def parse_flag(value: str) -> bool:
    if value == "yes":
        return True
    elif value == "no":
        return False
    else:
        raise ValueError(value)


def to_int(text: str) -> int:
    try:
        return int(text)
    except ValueError as exc:
        raise TypeError(text) from exc


def must_have(config: dict[str, str], key: str) -> str:
    if key in config:
        return config[key]
    sys.exit(f"missing config key: {key}")


def child_status(code: int) -> int:
    if code == 0:
        return 0
    os._exit(code)
