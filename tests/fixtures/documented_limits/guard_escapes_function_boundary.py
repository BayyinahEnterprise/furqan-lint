"""Documented limitation (v1.0.1): checks stop at function boundaries.

Each function below can return None from a function declaring
``-> str``, and furqan-lint is silent:

* ``outer``: the body of a nested function is not checked at all, by
  D11 or by D24 (only top-level functions and class methods are).
* ``reloaded``: a nested function rebinds the outer variable through
  ``nonlocal`` after it was bound; following that needs
  cross-function data flow.
* ``swallowed``: a decorator whose ``__exit__`` returns True swallows
  the guard's ``raise``, so the guard does not end the path. This is
  the decorator form of the ``with contextlib.suppress`` limit.
* ``computed_locals``: ``locals`` reached through ``getattr`` with a
  built string is not recognised as dynamic scope access.

Pinned so that crossing function boundaries is a deliberate, recorded
change.
"""

from __future__ import annotations

import builtins
import contextlib
from typing import Optional


def find_name(uid: int) -> Optional[str]:
    return None


def outer(uid: int) -> str:
    def inner() -> str:
        return find_name(uid)  # type: ignore[return-value]

    return inner()


def reloaded(uid: int) -> str:
    name = "seed"

    def reload() -> None:
        nonlocal name
        name = find_name(uid)  # type: ignore[assignment]

    reload()
    return name


class _Swallow(contextlib.ContextDecorator):
    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc: object) -> bool:
        return True


@_Swallow()
def swallowed(uid: int) -> str:
    name = find_name(uid)
    if name is None:
        raise KeyError(uid)
    return name


def computed_locals(uid: int) -> str:
    # Dynamic scope reached through a computed name: guard narrowing is
    # disabled only for direct references to ``locals`` / ``vars`` /
    # ``eval`` / ``exec`` / frame attributes, not for ``getattr`` with
    # a built string.
    name = find_name(uid)
    if name is not None:
        print(name)
    return getattr(builtins, "loc" + "als")()["name"]  # type: ignore[no-any-return]
