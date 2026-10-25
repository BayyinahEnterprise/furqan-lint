"""D11 must still fire: the None arm is NOT handled at the call site.

v1.0.1 true-positive guard for the narrowing fix. Each function below
receives ``str | None`` and returns a bare ``str`` or ``bool`` without
explicitly handling None where it was received. Expected: six D11
diagnostics, one per function.
"""

from __future__ import annotations

from typing import Optional


def find_name(uid: int) -> Optional[str]:
    return "alice" if uid == 1 else None


def leaky(uid: int) -> str:
    return find_name(uid)  # None leaks out as str


def late_guard(uid: int) -> str:
    name = find_name(uid)
    print(name)  # used before the guard
    if name is None:
        return ""
    return name


def ordered(uid: int) -> bool:
    return find_name(uid) < "m"  # ordering is undefined for None


def guard_without_exit(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        print("missing")  # neither ends the path nor rebinds
    return str(name)


def has_letter_a(uid: int) -> bool:
    return "a" in find_name(uid)  # ``"a" in None`` raises TypeError


def in_alphabet(uid: int) -> bool:
    return find_name(uid) in "abc"  # ``None in "abc"`` raises TypeError
