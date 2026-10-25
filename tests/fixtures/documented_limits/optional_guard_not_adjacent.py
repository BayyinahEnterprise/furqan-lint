"""Documented limitation (v1.0.1): None handling D11 does not see.

v1.0.1 withholds a call from D11 only when the None arm is handled at
the call site: ``or`` default, ``==`` / ``is`` comparison, walrus
guard, or a None-guard on the statement immediately after the
binding, where the guard's branch is straight-line up to its exit or
rebind. Each function below handles None correctly by another route,
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


def branch_before_exit(uid: int, verbose: bool) -> str:
    # v1.0.1 audit F-01 consequence: the None branch must be
    # straight-line up to its exit or rebind. A nested ``if`` that
    # never touches ``name`` is safe here, but D11 cannot tell without
    # control-flow analysis, so it stays visible.
    name = find_name(uid)
    if name is None:
        if verbose:
            print("missing", uid)
        raise KeyError(uid)
    return name


def guard_inside_try(uid: int) -> str:
    # v1.0.1 verification-round consequence: inside a ``try`` with
    # handlers or ``finally`` (or a ``with`` block) a guard's raise may
    # be caught, so D11 does not trust it. Here only OSError is caught
    # and the KeyError escapes, so the guard is safe, but D11 cannot
    # tell without exception-flow analysis.
    try:
        name = find_name(uid)
        if name is None:
            raise KeyError(uid)
        return name
    except OSError:
        return ""
