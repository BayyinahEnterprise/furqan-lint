"""R3 must SKIP: a method decorated with ``@abstractmethod``
(directly imported from ``abc``) is intentionally a stub.

The skip-list resolves ``abstractmethod`` (bare name) and
``abc.abstractmethod`` (dotted attribute access).
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Base(ABC):
    @abstractmethod
    def required(self, x: int) -> int:
        # Body is intentionally a docstring-only stub.
        """Subclasses must implement."""

    @abstractmethod
    def required_with_pass(self, x: int) -> int:
        pass
