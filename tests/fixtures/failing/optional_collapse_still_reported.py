"""D11 must still fire: the None arm is NOT handled at the call site.

v1.0.1 true-positive guard for the narrowing fix. Each function below
receives ``str | None`` and returns a bare ``str`` or ``bool`` without
explicitly handling None where it was received. Expected: twenty-six D11
diagnostics, one per function.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
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


# v1.0.1 review round: shapes that look like a guard but still let
# None out. Each must keep firing.


def break_leaks(uids: list[int]) -> str:
    name = ""
    for uid in uids:
        name = find_name(uid)
        if name is None:
            break  # leaves the loop, name is still None below
    return name


def walrus_continue_leaks(uids: list[int]) -> str:
    name = ""
    for uid in uids:
        if (name := find_name(uid)) is None:
            continue
    return name


def returns_the_none(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        return name  # hands the None straight back
    return name


def or_none_default(uid: int) -> str:
    return find_name(uid) or None


def rebinds_to_none(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        name = None
    return name


def closure_reads_after_guard(uid: int) -> str:
    name = find_name(uid)
    if name is not None:
        print(name)
    return (lambda: name)()


# v1.0.1 audit F-01: a None branch that returns the None on a nested
# path before its rebind or raise. Each must keep firing.


def nested_return_before_rebind(uid: int, early: bool) -> str:
    name = find_name(uid)
    if name is None:
        if early:
            return name  # returns None before the fallback is assigned
        name = "fallback"
    return name


def nested_return_before_raise(uid: int, early: bool) -> str:
    name = find_name(uid)
    if name is None:
        if early:
            return name
        raise KeyError(uid)
    return name


def walrus_nested_return_before_raise(uid: int, early: bool) -> str:
    if (name := find_name(uid)) is None:
        if early:
            return name
        raise KeyError(uid)
    return name


# v1.0.1 verification round: the guard's exit is caught, suppressed or
# overridden, or the fallback is replaced by a binding form that can
# be None. Each must keep firing.


def caught_raise_leaks(uid: int) -> str:
    try:
        name = find_name(uid)
        if name is None:
            raise ValueError("missing")
    except ValueError:
        return name  # the raise was caught; name is still None
    return name


def caught_walrus_raise_leaks(uid: int) -> str:
    try:
        if (name := find_name(uid)) is None:
            raise KeyError(uid)
    except KeyError:
        return name
    return name


def caught_exit_leaks(uid: int) -> str:
    try:
        name = find_name(uid)
        if name is None:
            sys.exit(1)
    except SystemExit:
        pass
    return name


def finally_overrides_fallback(uid: int) -> str:
    try:
        name = find_name(uid)
        if name is None:
            return "fallback"
    finally:
        return name  # noqa: B012  overrides the fallback return


def tuple_rebind_to_none(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        name = "fallback"
        name, _ = None, 0
    return name


def match_capture_rebind(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        name = "fallback"
        match None:
            case name:
                pass
    return name


# v1.0.1 verification round two: a closure reads the variable when it
# runs, not when it is created, and a global can be rebound by any
# call. Each must keep firing.


def late_closure_continue(uids: list[int]) -> str:
    getters: list[Callable[[], str]] = []
    for uid in uids:
        name = find_name(uid)
        if name is None:
            continue
        getters.append(lambda: name)  # reads the last binding, maybe None
    return getters[0]()


def late_closure_positive(uids: list[int]) -> str:
    getter: Callable[[], str] = lambda: ""  # noqa: E731
    for uid in uids:
        name = find_name(uid)
        if name is not None:
            getter = lambda: name  # noqa: E731
    return getter()


def closure_return_fallback(uid: int) -> str:
    def fallback() -> str:
        return name  # reads the guarded name, which is None here

    name = find_name(uid)
    if name is None:
        return fallback()
    return name


_CURRENT: Optional[str] = None


def _clear() -> None:
    global _CURRENT
    _CURRENT = None


def global_rebound_after_guard(uid: int) -> str:
    global _CURRENT
    _CURRENT = find_name(uid)
    if _CURRENT is None:
        _CURRENT = "default"
    _clear()  # rebinds the global to None after the guard
    return _CURRENT


def locals_after_guard(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        return str(locals()["name"])  # dynamic scope access: not trusted
    return name
