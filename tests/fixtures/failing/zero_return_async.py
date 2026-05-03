"""R3 fires: ``async def`` function declares non-None return but
contains zero ``return`` statements.

R3 walks ``AsyncFunctionDef`` the same as ``FunctionDef``.
"""

from __future__ import annotations


async def fetch(x: int) -> int:
    # Declares -> int but never returns. R3 fires.
    if x > 0:
        x = x + 1
