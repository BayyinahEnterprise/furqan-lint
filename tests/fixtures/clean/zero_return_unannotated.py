"""R3 must SKIP: function with no return annotation at all.

R3 has no contract for an unannotated function; it can return
anything (or nothing). Furqan's checkers only opine on declared
producers.
"""

from __future__ import annotations


def something(x):
    # No return annotation. R3 has no contract. Skipped.
    if x > 0:
        x = x + 1
