"""Documented limitation (v1.0.1): an Optional stored in a container.

The caller keeps the ``None`` arm inside a dict value typed
``str | None``, so nothing is collapsed, but D11 does not track values
through containers and still reports the call. Pinned so that widening
D11 to container flows is a deliberate, recorded change. furqan-lint's
own ``gate11/rust_signature_canonicalization._function_signature_dict``
is this shape.
"""

from __future__ import annotations

from typing import Optional


def find_name(uid: int) -> Optional[str]:
    return "alice" if uid == 1 else None


def describe(uid: int) -> dict[str, Optional[str]]:
    return {"name": find_name(uid)}
