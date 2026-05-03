"""R3 fires: function with branching but zero ``return`` statements
on any path.

D24 does not fire because partial-path coverage requires at least
one return present. R3 catches the zero-coverage case.
"""

from __future__ import annotations


def f(x: int) -> int:
    if x > 0:
        x = x + 1
    elif x < 0:
        x = x - 1
    else:
        x = 0
    # No return on any path. R3 fires.
