"""Documented limitation (v1.0.1): terminal calls D24 does not recognise.

v1.0.1 treats ``raise``, ``sys.exit(...)``, ``os._exit(...)`` and
``os.abort()`` as ending a path. Recognition is syntactic on the
``module.attr`` spelling, so the shapes below still look like a
fall-through and D24 reports each function, although none of them can
return None. Pinned so that widening recognition (import alias
tracking, ``typing.NoReturn`` resolution) is a deliberate, recorded
change.
"""

from __future__ import annotations

from sys import exit
from typing import NoReturn


def fail(message: str) -> NoReturn:
    raise SystemExit(message)


def aliased_exit(code: int) -> int:
    if code == 0:
        return 0
    exit(code)


def via_noreturn_helper(code: int) -> int:
    if code == 0:
        return 0
    fail("nonzero")


def assert_false(code: int) -> int:
    if code == 0:
        return 0
    assert False, code
