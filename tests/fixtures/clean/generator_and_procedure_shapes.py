"""D24, D11 and R3 must stay silent on generators and ``-> None``.

v1.0.1 regression fixture. A generator's annotation describes what it
yields: a bare ``return`` or reaching the end ends iteration. A
``-> None`` procedure may return early or fall through by design.
Before v1.0.1, D24 reported "missing return" on both shapes and R3
reported generators with no ``return``. (A ``-> None`` procedure that
calls an Optional producer is covered by an inline test: it now gets
D11's informational S2 advisory instead of an S1 error.)
"""

from __future__ import annotations

from collections.abc import Iterator


def evens(limit: int) -> Iterator[int]:
    if limit < 0:
        return
    for n in range(limit):
        if n % 2 == 0:
            yield n


def chained(a: list[int], b: list[int]) -> Iterator[int]:
    yield from a
    yield from b


def record(events: list[str], item: str) -> None:
    if not item:
        return
    events.append(item)
