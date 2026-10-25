"""furqan-lint's own source must stay at its documented self-check (v1.0.2).

v1.0.1's CHANGELOG reported the self-check as 1 error (the documented
``optional_stored_in_container`` limit) plus 1 informational note. PR
#30, merged into the same release, added two more errors in
``gate11/cli.py`` (an Optional result checked for None inside a ``try``,
the documented ``guard_inside_try`` limit), and nothing noticed. This
gate runs the linter over its own ``src/`` and fails on any S1 error
other than the documented one, so a claim about the self-check cannot
drift from the code again.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from furqan.errors.marad import Marad

from furqan_lint.adapter import translate_file
from furqan_lint.runner import check_python_module

SRC = Path(__file__).resolve().parents[1] / "src" / "furqan_lint"

# The one documented S1 finding on furqan-lint's own source
# (tests/fixtures/documented_limits/optional_stored_in_container.py).
EXPECTED = {("gate11/rust_signature_canonicalization.py", "_function_signature_dict")}


@pytest.mark.unit
def test_self_check_reports_only_the_documented_error() -> None:
    found: set[tuple[str, str]] = set()
    for path in sorted(SRC.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        diags = check_python_module(translate_file(path), ast.parse(source))
        for _name, d in diags:
            if isinstance(d, Marad) or type(d).__name__ == "ZeroReturnDiagnostic":
                text = str(d)
                fn = getattr(d, "function_name", None) or text.split("function '")[1].split("'")[0]
                found.add((path.relative_to(SRC).as_posix(), fn))
    assert (
        found == EXPECTED
    ), f"self-check drifted: {sorted(found - EXPECTED)} new, {sorted(EXPECTED - found)} gone"
