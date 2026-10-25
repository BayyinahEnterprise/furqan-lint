"""Documented limitation (v1.0.1): terminal recognition is syntactic.

D24 treats ``raise`` and the ``sys.exit`` / ``os._exit`` /
``os.abort`` spellings as ending a path without asking whether they
really do. Each function below can fall through and return None, and
D24 stays silent:

* ``suppressed_raise``: the ``raise`` sits in a ``with`` block whose
  context manager (``contextlib.suppress``) swallows it.
* ``shadowed_sys``: ``sys`` is a parameter, not the module, so
  ``sys.exit()`` may return.

Pinned so that tightening recognition (context-manager awareness,
binding resolution for ``sys`` / ``os``) is a deliberate, recorded
change.
"""

from __future__ import annotations

import contextlib
from typing import Any


def suppressed_raise(flag: int) -> int:
    if flag:
        return 1
    with contextlib.suppress(ValueError):
        raise ValueError(flag)


def shadowed_sys(flag: int, sys: Any) -> int:
    if flag:
        return 1
    sys.exit()
