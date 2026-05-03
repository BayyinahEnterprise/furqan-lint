"""Direct unit tests for the language-agnostic
:func:`furqan_lint.additive.compare_name_sets` helper.

The Python-specific :func:`check_additive_api` already exercises
this function via the public_surface and CLI tests; these direct
tests pin (a) the language-aware re-export hint dispatch (the
v0.8.1 refactor's load-bearing addition) and (b) the
sorted-and-stable diagnostic ordering when removed names are not
already in alphabetical order.
"""

from __future__ import annotations

import pytest

from furqan_lint.additive import compare_name_sets

pytestmark = pytest.mark.unit


def test_compare_name_sets_emits_language_aware_rename_hint() -> None:
    """The ``language`` kwarg picks the matching hint template
    from ``_RENAME_HINT``. Pinning the three v0.8.1 entries
    (python, rust, go) guards against future regressions where
    a hint is silently changed and a CI pipeline that greps the
    diagnostic output for the old phrasing breaks.
    """
    previous = frozenset({"PublicName"})
    current: frozenset[str] = frozenset()

    py = compare_name_sets(previous, current, "m.py", language="python")
    assert len(py) == 1
    assert "PublicName = <new_name>" in py[0].minimal_fix

    rs = compare_name_sets(previous, current, "m.rs", language="rust")
    assert len(rs) == 1
    assert "pub use <new> as PublicName;" in rs[0].minimal_fix

    go = compare_name_sets(previous, current, "m.go", language="go")
    assert len(go) == 1
    assert "var PublicName = <new>" in go[0].minimal_fix


def test_compare_name_sets_returns_diagnostics_in_sorted_order() -> None:
    """Removed names are emitted in sorted order regardless of
    insertion order in the source sets. Stability matters for
    snapshot tests and for users who diff diagnostic output
    across releases.
    """
    previous = frozenset({"Zeta", "Alpha", "Mu"})
    current: frozenset[str] = frozenset()
    diagnostics = compare_name_sets(previous, current, "m.py", language="python")
    names_in_diagnostics = [
        line for d in diagnostics for line in [d.diagnosis] if "Public name" in line
    ]
    # Each diagnostic's "Public name 'X'" prefix encodes which name
    # fired; assert the order matches sorted(removed).
    assert "'Alpha'" in names_in_diagnostics[0]
    assert "'Mu'" in names_in_diagnostics[1]
    assert "'Zeta'" in names_in_diagnostics[2]
