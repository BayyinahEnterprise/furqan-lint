"""Documented limitation (v1.0.1): terminal recognition is syntactic.

D24 treats ``raise`` and the ``sys.exit`` / ``os._exit`` /
``os.abort`` spellings as ending a path without asking whether they
really do. Each function below can fall through and return None, and
D24 stays silent:

* ``suppressed_raise``: the ``raise`` sits in a ``with`` block whose
  context manager (``contextlib.suppress``) swallows it.
* ``shadowed_sys``: ``sys`` is a parameter, not the module, so
  ``sys.exit()`` may return.
* ``shadowed_sys_guard``: the same recognition decides whether a D11
  None-guard ends its branch, so D11 is silent too.

Pinned so that tightening recognition (context-manager awareness,
binding resolution for ``sys`` / ``os``) is a deliberate, recorded
change.
"""

from __future__ import annotations

import contextlib
from typing import Any, Optional


def suppressed_raise(flag: int) -> int:
    if flag:
        return 1
    with contextlib.suppress(ValueError):
        raise ValueError(flag)


def shadowed_sys(flag: int, sys: Any) -> int:
    if flag:
        return 1
    sys.exit()


def find_name(uid: int) -> Optional[str]:
    return None


def shadowed_sys_guard(uid: int, sys: Any) -> str:
    # The same syntactic recognition feeds D11's guard check: a
    # ``sys.exit`` on a parameter named ``sys`` is trusted as ending
    # the None branch, so D11 is silent if that ``exit`` returns.
    name = find_name(uid)
    if name is None:
        sys.exit(1)
    return name
