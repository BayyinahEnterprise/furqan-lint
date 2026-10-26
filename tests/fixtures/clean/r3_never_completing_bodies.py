"""R3 must stay silent: no path through these bodies finishes normally.

v1.0.2 regression fixture. R3 (zero-return) used to recognise only two
shapes (every path ends in ``raise``; the body is exactly one
``while True:`` with no ``break``) and reported every function below,
although none of them can fall through and return None. Found by the
side-street map (``bench/sidestreets``).
"""

from __future__ import annotations

import os
import sys


def exits(code: int) -> int:
    print("fatal", code)
    sys.exit(code)


def raises_or_exits(flag: bool) -> int:
    if flag:
        raise ValueError("bad flag")
    os._exit(2)


def serve_forever(port: int) -> int:
    print("listening on", port)
    while True:
        print("tick")


def cleanup_then_exit(path: str) -> int:
    try:
        print("working on", path)
    finally:
        sys.exit(0)
