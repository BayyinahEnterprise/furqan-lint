"""Documented limitation: try body raises, except falls through.

The body unconditionally raises; the except handler does not return.
mypy flags this as missing-return; furqan-lint v0.3.1 does not.

See README.md "Remaining limitations" -> "Exception-driven
fall-through."
"""
from __future__ import annotations


def f() -> int:
    try:
        raise ValueError
    except ValueError:
        pass
    # No return reachable; mypy: error: Missing return statement.
    # furqan-lint v0.3.1: PASS.
