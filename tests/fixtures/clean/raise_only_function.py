"""R3 must SKIP: function whose body is exactly one ``raise``.

The function provably never returns (it always raises), so the
absence of a ``return`` statement is intentional. mypy also
accepts this shape.
"""

from __future__ import annotations


def not_implemented(x: int) -> int:
    raise NotImplementedError("subclass must override")
