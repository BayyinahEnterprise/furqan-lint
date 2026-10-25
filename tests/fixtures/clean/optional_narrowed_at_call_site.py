"""D11 must stay silent: the None arm is handled at the call site.

v1.0.1 regression fixture for the None-guard false positive. Before
v1.0.1, D11 reported every call to an Optional producer from a caller
declaring a bare return type, even when the caller handled ``None``
explicitly. mypy accepts every function below.
"""

from __future__ import annotations

from typing import Optional


def find_name(uid: int) -> Optional[str]:
    return "alice" if uid == 1 else None


def greet(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        return "hello, stranger"
    return "hello, " + name


def greet_or_default(uid: int) -> str:
    return find_name(uid) or "stranger"


def first_known(uids: list[int]) -> str:
    for uid in uids:
        name = find_name(uid)
        if not name:
            continue
        return name
    raise LookupError("no known user")


def label(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        name = "anonymous"
    return name


def is_alice(uid: int) -> bool:
    return find_name(uid) == "alice"


def shout(uid: int) -> str:
    if (name := find_name(uid)) is None:
        raise KeyError(uid)
    return name.upper()


def name_length(uid: int) -> int:
    name = find_name(uid)
    if name is not None:
        return len(name)
    return 0


# v1.0.1 audit F-01 clean siblings: a straight-line prefix that does
# not touch the name, then the fallback or the raise, is still handled.


def label_after_log(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        print("missing", uid)
        name = "anonymous"
    return name


def shout_after_log(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        print("missing", uid)
        raise KeyError(uid)
    return name.upper()
