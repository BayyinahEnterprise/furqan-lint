"""R3 fires: function declares non-None return but has zero
``return`` statements anywhere on any path.

mypy: "Missing return statement".
furqan-lint v0.6.0+: ``zero_return_path`` (R3, ring-close).

Until v0.5.x this case was a documented limitation (D24 skipped
zero-return functions; R3 was not wired). v0.6.0 retired the
limitation by wiring R3 into the runner.
"""

from __future__ import annotations


def f(x: int) -> str:
    # Declares ``-> str`` but has no return statement on any path.
    # R3 fires.
    if x > 0:
        x = x + 1
    # No return here; falls off the end.
