"""R3 fires: a method on a class declares non-None return but has
zero ``return`` statements.

R3 walks methods inside ``ClassDef`` bodies via ``ast.walk``.
"""

from __future__ import annotations


class Service:
    def process(self, x: int) -> int:
        # Declares -> int but never returns. R3 fires on
        # 'process'.
        if x > 0:
            x = x + 1
