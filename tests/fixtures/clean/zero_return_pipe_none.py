"""R3 must SKIP: function annotated ``-> int | None`` (PEP 604
union with None) with zero return statements.

R3 delegates to ``adapter._is_pipe_union_with_none`` which already
handles this shape (and the degenerate ``None | None``). D24 also
skips zero-return functions, so this fixture is silent on every
checker.
"""

from __future__ import annotations


def maybe(x: int) -> int | None:
    # Zero returns; implicit None falls through. int | None
    # permits None; R3 skips. D24 also skips zero-return shapes.
    if x > 0:
        x = x + 1
