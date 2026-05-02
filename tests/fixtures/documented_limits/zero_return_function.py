"""Documented limitation: zero-return functions.

A function that declares a return type but has no ``return``
statement at all is silently passed by furqan-lint.

D24 (the upstream all-paths-return checker) skips functions whose
return-statement count is zero, deferring that case to ring-close
R3 (a separate Furqan checker that asserts every declared
producer eventually emits at least one terminal value). furqan-lint
does not yet run R3, so the zero-return case falls through both
layers.

mypy reports this as "Missing return statement"; furqan-lint will
report it when R3 is wired into the runner.

For v0.4.x: callers who want zero-return functions flagged should
run mypy alongside furqan-lint. The two tools' coverage is
deliberately complementary; neither subsumes the other.

See README.md "Remaining limitations" -> "Zero-return functions."
"""
from __future__ import annotations


def f(x: int) -> str:
    # Declares ``-> str`` but has no return statement on any path.
    # mypy: "Missing return statement". furqan-lint: silent PASS
    # because D24 skips zero-return functions and R3 is not yet
    # wired into the runner.
    if x > 0:
        x = x + 1
    # No return here; falls off the end.
