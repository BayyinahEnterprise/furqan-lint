"""R3 must SKIP: function annotated ``-> None``.

The implicit ``None`` return is the declared type. Not a R3
violation. Furqan's D11 also exempts None-returning functions
from status-coverage.
"""

from __future__ import annotations


def void_op(x: int) -> None:
    # No return statement; implicit None return matches -> None.
    if x > 0:
        x = x + 1
