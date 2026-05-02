"""Documented limitation: aliased typing.Optional import.

``from typing import Optional as MyOpt; -> MyOpt[X]`` is treated
as a non-Optional return type. The function returns None and fires
a false-positive ``return_none_mismatch``.

The proper fix needs symbol-table tracking (parse imports, build
alias map, resolve ``MyOpt`` -> ``typing.Optional`` before the
matcher runs). Probably Phase 4.

For v0.3.x: use the bare ``Optional`` form, the qualified
``typing.Optional[X]`` form, or rename the import (``import typing
as t``; ``t.Optional[X]`` is recognised).

See README.md "Remaining limitations" -> "Aliased Optional imports."
"""
from __future__ import annotations

from typing import Optional as MyOpt


def f(x: int) -> MyOpt[str]:
    # Legitimate Optional return; should not fire. v0.3.1 fires
    # return_none_mismatch as a false positive.
    if x > 0:
        return "y"
    return None
