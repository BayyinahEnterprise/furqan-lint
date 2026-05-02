"""PEP 604 with redundant ``None`` arms.

``int | None | None`` is treated as ``int | None`` by Python's
type system (mypy and pyright both collapse the redundant arm).
furqan-lint correctly produces zero diagnostics on a matching
``return None`` body. The intermediate AST shape (a binary
``UnionType`` whose arms may both be ``None`` after inner
extraction) is incidentally correct but not structurally defended
the way the ``Union[None]`` path is in v0.3.3 and the
``Optional[None]`` path is in v0.3.4.

Pinned as a documented limitation. Full symmetric tightening
across the Optional / Union / PEP 604 pipe paths is a v0.4.0
candidate. Caught by Fraz's round-7 review (Observation 2). See
README.md \"Remaining limitations\" -> \"Redundant ``None`` arms in
PEP 604 unions.\"
"""

from __future__ import annotations


def f() -> int | None | None:
    return None


def g() -> None | None:
    return None
