"""R3 must SKIP: ``@overload``-decorated stubs are signatures only.

Only the implementation (no ``@overload`` decorator) needs to
return. R3's skip-list recognizes ``overload`` (bare) and
``typing.overload`` (dotted).
"""

from __future__ import annotations

from typing import overload


@overload
def parse(x: int) -> int: ...


@overload
def parse(x: str) -> str: ...


def parse(x: int | str) -> int | str:
    return x
