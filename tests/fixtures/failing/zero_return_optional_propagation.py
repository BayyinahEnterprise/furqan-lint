"""R3 fires on the outer function (which declares ``-> int``) but
NOT on the sibling Optional-returning helper.

Establishes that R3 respects Optional/Union-with-None propagation
exactly the same way the existing v0.3.x degenerate-form fixes do.
The two functions are siblings (not caller/callee) so D11
status-coverage is not in scope for this fixture.
"""

from __future__ import annotations

from typing import Optional


def helper(x: int) -> Optional[int]:
    # Declares Optional[int]; falling off the end yields None,
    # which is in the declared union. R3 must SKIP this.
    if x > 0:
        x = x + 1


def outer(x: int) -> int:
    # Declares -> int (non-Optional). Zero returns. R3 fires
    # on 'outer' but NOT on 'helper'.
    x = x + 1
