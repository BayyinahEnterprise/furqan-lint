"""R3 must SKIP: function annotated ``-> Optional[int]`` with zero
return statements.

Optional includes None, so the implicit None return that comes
from falling off the end satisfies the contract. R3 delegates the
Optional-recognition step to ``adapter._is_optional``, which
already encodes the v0.3.x degenerate-form fixes. D24 also skips
zero-return functions, so this fixture is silent on every checker.
"""

from __future__ import annotations

from typing import Optional


def maybe(x: int) -> Optional[int]:
    # Zero returns; implicit None falls through. Optional[int]
    # permits None; R3 skips. D24 also skips zero-return shapes.
    if x > 0:
        x = x + 1
