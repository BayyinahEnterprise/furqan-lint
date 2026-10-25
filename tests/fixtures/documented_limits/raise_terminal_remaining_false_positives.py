"""Documented limitation (v1.0.1): raise shapes D24 still misreads.

Each function below ends every path in ``return`` or ``raise``, mypy
accepts it, and D24 still reports a missing return:

* ``search``: ``raise`` in a ``for ... else`` (the loop and its
  ``else`` are translated as maybe-runs branches).
* ``poll``: a ``while True:`` loop whose only exits are ``return``
  and ``raise`` (loop bodies are maybe-runs).
* ``guarded``: ``try`` / ``finally`` with no ``except`` clause.

Pinned so that teaching the adapter loop-else, infinite-loop and
handler-less ``try`` semantics is a deliberate, recorded change.
"""

from __future__ import annotations


def search(items: list[int], target: int) -> int:
    for i, item in enumerate(items):
        if item == target:
            return i
    else:
        raise LookupError(target)


def poll(values: list[int]) -> int:
    while True:
        if values:
            return values.pop()
        raise TimeoutError("empty")


def guarded(flag: int) -> int:
    try:
        if flag:
            return 1
        raise ValueError(flag)
    finally:
        print("done")
