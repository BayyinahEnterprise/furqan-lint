"""Documented limitation (v1.0.1): ``-> None`` carries no contract.

v1.0.1 translates ``-> None`` functions without a return type, so a
``-> None`` function that returns a value is not reported. Before
v1.0.1 D24 sometimes reported this shape, but only by accident (it
read ``-> None`` as a value contract and complained about the
fall-through, not about the value). No checker compares returned
values against ``-> None``; mypy does. Pinned so that adding a real
check is a deliberate, recorded change.
"""

from __future__ import annotations


def record(flag: int) -> None:
    if flag:
        return 5  # type: ignore[return-value]
