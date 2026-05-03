"""CHANGELOG-math gate (v0.8.3 round-21 corrective).

Parses the latest CHANGELOG entry's ``### Tests`` block and
asserts the claimed test count + delta match the empirical
counts from ``pytest --collect-only -q``.

Catches the v0.8.1 CHANGELOG-math drift (claimed 268 -> 291
delta +23, actual baseline was 294) and any future
arithmetic mistake in release commit bodies.

The gate exposes its parser as a module-private helper
(``_parse_changelog_math``) so the self-test
(``test_changelog_math_gate_catches_wrong_arithmetic``) can
exercise it against a fixture without spawning a subprocess
(no recursion risk; faster execution).

Placeholder handling: if the latest entry contains ``<TBD>``
or ``<DATE>`` markers, ``_parse_changelog_math`` returns None
and the live gate skips with a warning. This is the in-flight
release commit pattern: commit 1 of a release adds the
placeholder header so intermediate commits between 'add gate'
(commit 5 here) and 'final release populates math' (commit 7)
do not self-fail under the gate.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.unit

# Pattern matches the canonical "Test count: X (vA.B.C) -> Y
# (vD.E.F). Net delta: +Z." sentence used in v0.7.x onward.
# Tolerates whitespace + line wrapping + Markdown emphasis
# ``Y`` (backticks). The version tags are not validated; the
# load-bearing capture groups are X, Y, Z.
_TESTS_LINE = re.compile(
    r"Test count:\s*(\d+)\s*\([^)]+\)\s*->\s*" r"(\d+)\s*\([^)]+\)\.\s*Net delta:\s*\+(\d+)",
    re.IGNORECASE | re.DOTALL,
)


def _parse_changelog_math(changelog_path: Path) -> tuple[int, int, int] | None:
    """Parse the latest CHANGELOG entry's ``### Tests`` block.

    Returns ``(X, Y, Z)`` for the canonical sentence, or
    ``None`` when the latest entry contains ``<TBD>`` or
    ``<DATE>`` placeholders (in-flight release commit
    pattern; gate skips).

    Latest entry = the first ``## [...]`` block in the file.
    Older entries use different formats and are out of scope
    for this gate.
    """
    text = changelog_path.read_text(encoding="utf-8")
    # Find the latest entry (first match of "## [...]").
    entry_match = re.search(r"^## \[[^\]]+\]", text, re.MULTILINE)
    if entry_match is None:
        return None
    start = entry_match.start()
    # Find the next entry start (or EOF).
    next_match = re.search(r"^## \[", text[start + 1 :], re.MULTILINE)
    end = (start + 1 + next_match.start()) if next_match else len(text)
    latest = text[start:end]
    # Placeholder detection: look for the actual in-flight
    # markers in the entry HEADER (## [v] - <DATE>) or the
    # ### Tests block (-> <TBD> ...). Backtick-quoted prose
    # references to the literal strings (e.g. release CHANGELOG
    # bodies that describe the placeholder mechanism) do NOT
    # count as in-flight markers.
    if re.search(r"^## \[[^\]]+\] - <DATE>", latest, re.MULTILINE):
        return None
    if re.search(r"->\s*<TBD>", latest):
        return None
    if re.search(r"Net delta:\s*<TBD>", latest):
        return None
    # Extract X, Y, Z from the canonical sentence.
    m = _TESTS_LINE.search(latest)
    if m is None:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _empirical_test_count() -> int:
    """Run ``pytest --collect-only -q`` and parse the trailing
    summary line ``N tests collected``. Returns N.

    Uses --collect-only to avoid running the suite (fast, no
    side-effects). The ``cwd`` is the repo root so pytest
    discovers the conftest and pyproject config.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    # Look for "<N> tests collected" in stdout.
    m = re.search(r"(\d+)\s+tests?\s+collected", result.stdout)
    if m is None:
        raise RuntimeError(f"Could not parse pytest --collect-only output:\n{result.stdout}")
    return int(m.group(1))


def test_changelog_math_matches_pytest_collect() -> None:
    """The latest CHANGELOG entry's ### Tests math must match
    the empirical pytest count.

    Skips when the entry contains <TBD> / <DATE> placeholders
    (in-flight release commit; the release commit replaces
    placeholders with empirical values).
    """
    parsed = _parse_changelog_math(REPO_ROOT / "CHANGELOG.md")
    if parsed is None:
        pytest.skip(
            "CHANGELOG entry in flight (contains <TBD> / <DATE> "
            "placeholder); release commit will populate empirical "
            "math."
        )
    x, y, z = parsed
    empirical = _empirical_test_count()
    assert y == empirical, (
        f"CHANGELOG claims {y} tests, pytest --collect-only "
        f"reports {empirical}. The release commit body's "
        f"'### Tests' line must match the empirical count."
    )
    assert y - x == z, (
        f"CHANGELOG claims delta +{z} ({x} -> {y}), but the "
        f"actual delta is +{y - x}. The release commit body "
        f"arithmetic is wrong."
    )


def test_changelog_math_gate_catches_wrong_arithmetic(tmp_path: Path) -> None:
    """Self-test: a fixture CHANGELOG with deliberately wrong
    arithmetic must be parseable, and the parsed values must
    falsify the delta claim.

    Exercises the parser without spawning a subprocess (avoids
    recursion against the live gate).
    """
    fake = tmp_path / "FAKE_CHANGELOG.md"
    fake.write_text(
        "## [9.9.9] - 2099-01-01\n\n"
        "### Tests\n\n"
        "Test count: 100 (v9.9.8) -> 200 (v9.9.9). "
        "Net delta: +50.\n"
    )
    parsed = _parse_changelog_math(fake)
    assert parsed == (100, 200, 50), (
        f"parser must extract the literal X, Y, Z values " f"from the fixture; got {parsed}"
    )
    x, y, z = parsed
    assert y - x != z, (
        "the fixture's claim is wrong by construction: "
        "200 - 100 = 100 != 50; the gate's arithmetic check "
        "would fire on this input"
    )
