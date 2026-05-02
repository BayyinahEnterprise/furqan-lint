"""Documented limitation: try body is spliced as always-running.

A function whose only return is inside a ``try`` block is reported
PASS even though an exception in the body would prevent reaching
the return. mypy flags this; furqan-lint v0.3.1 does not.

See README.md "Remaining limitations" -> "Exception-driven
fall-through." The fix needs richer translation: splice ``finalbody``
always, wrap ``body`` as maybe-runs only when there are exception
handlers that don't all return.
"""
from __future__ import annotations


def f() -> int:
    try:
        return 42
    except ValueError:
        pass
    # Falls off the end if ValueError is raised. mypy says
    # "Missing return statement"; furqan-lint v0.3.1 says PASS.
