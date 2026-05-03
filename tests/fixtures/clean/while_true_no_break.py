"""R3 must SKIP: function whose body is exactly one ``while True:``
with no ``break``.

The loop never exits, so reaching the function's end (with no
return) is provably unreachable. R3's recognition is canonical-form
only: ``while 1:`` is NOT recognized in v0.6.0 (false-positive
risk on idiomatic shapes outweighs precision).
"""

from __future__ import annotations


def serve_forever(x: int) -> int:
    while True:
        x = x + 1
        # No break; loop never exits.
