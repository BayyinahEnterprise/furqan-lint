"""Documented limitation: aliased decorator imports for R3 skip-list.

R3's skip-list resolution in v0.6.0 is name-only (``abstractmethod``,
``abc.abstractmethod``, ``overload``, ``typing.overload``). It does
NOT follow ``from abc import abstractmethod as abstract`` aliases.
A method decorated with the aliased name will trigger R3 even
though it is genuinely abstract.

mypy (and pyright) resolve this through their import/symbol table.
furqan-lint v0.6.0 does not yet have a symbol table; v0.6.1 will
add one so this case can be skipped.

Pinned as a regression target: when v0.6.1 closes the limit, this
fixture must transition from "fires R3" to "skipped".

See README.md "Remaining limitations" -> "Aliased decorator
imports for R3 skip-list."
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod as abstract


class Base(ABC):
    @abstract
    def required(self, x: int) -> int:
        # Genuinely abstract via aliased import. R3 v0.6.0 fires
        # (false positive). v0.6.1 will resolve the alias and skip.
        """Subclasses must implement."""
