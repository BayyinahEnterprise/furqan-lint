"""Documented limitation (v1.0.1): comparisons are assumed to be bool.

D11 withholds a call to an Optional producer that is an operand of
``==``, ``!=``, ``is`` or ``is not``, because those comparisons are
defined for None and normally yield a bool. ``is`` / ``is not`` always
do. ``==`` / ``!=`` call ``__eq__`` / ``__ne__``, which a class may
override to return anything, including its argument; then the
producer's None is handed back and D11 is silent. Pinned so that
type-aware comparison handling is a deliberate, recorded change.
"""

from __future__ import annotations

from typing import Any, Optional


def find_name(uid: int) -> Optional[str]:
    return None


class Reflect:
    def __eq__(self, other: object) -> Any:
        return other


def reflected(uid: int) -> str:
    result: str = find_name(uid) == Reflect()
    return result
