"""Documented limitation (v1.0.1): None handling D11 does not see.

v1.0.1 withholds a call from D11 only when the None arm is handled at
the call site: ``or`` default, ``==`` / ``is`` comparison, walrus
guard, or a None-guard on the statement immediately after the
binding. Each function below handles None correctly by another route,
and D11 still reports it. Pinned so that widening narrowing is a
deliberate, recorded change.

``assert name is not None`` is left visible on purpose: ``python -O``
strips asserts, so the guard is not guaranteed to run.
"""

from __future__ import annotations

from typing import Optional


def find_name(uid: int) -> Optional[str]:
    return "alice" if uid == 1 else None


def guard_two_lines_down(uid: int) -> str:
    name = find_name(uid)
    prefix = "user:"
    if name is None:
        return prefix
    return prefix + name


def asserted(uid: int) -> str:
    name = find_name(uid)
    assert name is not None
    return name
