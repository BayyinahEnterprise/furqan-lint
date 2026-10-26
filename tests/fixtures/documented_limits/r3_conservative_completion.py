"""Documented limitation (v1.0.2): R3's completion analysis is conservative.

R3 skips a function only when it can prove no path finishes normally.
It does not try to prove that a ``with`` block's context manager
re-raises, that a ``for`` loop or an ``except`` handler cannot fall
through, or which loop a nested ``break`` leaves. Each function below
never returns normally, yet R3 still reports it. Pinned so that a more
precise analysis is a deliberate, recorded change.
"""

from __future__ import annotations

import contextlib
import sys


def suppress_does_not_catch_exit(code: int) -> int:
    with contextlib.suppress(ValueError):
        sys.exit(code)  # SystemExit is not a ValueError


def inner_break_only(flag: bool) -> int:
    while True:
        while flag:
            break  # leaves the inner loop only
