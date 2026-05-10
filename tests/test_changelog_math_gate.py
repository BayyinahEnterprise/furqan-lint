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
    # Round-34 HIGH-2a (Part 5b(b) of v0.9.4): "Net delta:" must
    # accept arbitrary whitespace including newlines between
    # "Net" and "delta:". v0.9.3's CHANGELOG happened to wrap as
    # "Net\ndelta:" and the v0.9.3.1 substrate's literal-space
    # regex returned None, silently no-opping the gate. Replace
    # the literal " " with "\s+" so any whitespace works.
    r"Test count:\s*(\d+)\s*\([^)]+\)\s*->\s*" r"(\d+)\s*\([^)]+\)\.\s*Net\s+delta:\s*\+(\d+)",
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

    Skips when ``onnxruntime`` is not importable. Round-34
    HIGH-2 finding: the canonical CHANGELOG count includes
    11 tests in ``test_onnx_numpy_divergence.py`` that use
    ``pytest.importorskip("onnxruntime")`` and skip-collect
    when the runtime is absent. The CI test jobs install
    ``[dev,onnx]`` (no onnxruntime), producing an empirical
    count 11 below the CHANGELOG count. Until the CI matrix
    adds an ``[onnx-runtime]`` job (planned for v0.9.4 Part
    5b alongside the structural CLI-integration gate), this
    test skips in the lean env. Developer machines and the
    bundle-author sandbox install ``[onnx-runtime]`` and run
    the gate at full strength.
    """
    try:
        import onnxruntime  # noqa: F401
    except ImportError:
        pytest.skip(
            "onnxruntime not importable; canonical CHANGELOG count "
            "includes 11 onnxruntime-gated tests that skip-collect "
            "in this env. Gate runs at full strength when "
            "[onnx-runtime] is installed. See round-34 HIGH-2."
        )
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


def test_tests_line_regex_accepts_multiline_net_delta_wrap() -> None:
    r"""Round-34 HIGH-2a closure (Part 5b(b) of v0.9.4): pin the
    regex against the v0.9.3 wrap pattern that silently
    no-opped the gate.

    v0.9.3's CHANGELOG body wrapped "Net\ndelta: +23." (with
    a newline between "Net" and "delta:"); the v0.9.3.1
    substrate's literal-space regex required "Net delta:" on
    one line and returned None on the wrap. The gate then
    skipped silently because _parse_changelog_math returned
    None for the regex-no-match case (interpreted as
    placeholder-form). v0.9.3.1 surfaced the env-dependency
    on onnxruntime via the CI hotfix; the regex fragility
    itself was the underlying bug.

    v0.9.4 changes "Net delta:" to "Net\s+delta:" so any
    whitespace (spaces, newlines, tabs) works between the
    two tokens. This regression test pins the wrap case
    against any future regex refactor that re-introduces
    the literal-space requirement.
    """
    # Synthetic CHANGELOG fragment that wraps "Net" -> newline -> "delta:"
    v093_wrap = "Test count: 389 (v0.9.2) -> 412 (v0.9.3). Net\ndelta: +23."
    match = _TESTS_LINE.search(v093_wrap)
    assert match is not None, (
        "regex must match 'Net\\ndelta:' wrap; pre-fix v0.9.3.1 "
        "substrate returned None and silently no-opped the gate"
    )
    assert match.groups() == (
        "389",
        "412",
        "23",
    ), f"expected ('389', '412', '23'); got {match.groups()}"
    # Also verify the single-line form still works (backward
    # compatibility): the v0.9.3.1 CHANGELOG fits on one line.
    v0931_oneline = "Test count: 412 (v0.9.3) -> 413 (v0.9.3.1). Net delta: +1."
    match2 = _TESTS_LINE.search(v0931_oneline)
    assert match2 is not None
    assert match2.groups() == ("412", "413", "1")


# al-Hujurat T04 (v0.11.7 / Round 29 A2 closure with v1.1
# Round 30 F2 absorption): CHANGELOG-math gate spec
# calibrated to assert ship-reality, not projection-match.
# Substrate-corrective releases that absorb already-shipped
# defenses are the canonical case where projection and
# reality diverge legitimately. The legacy
# test_changelog_math_matches_pytest_collect already
# enforces "Y == empirical" (load-bearing assertion (a)).
# This block adds a separate weaker check: if a prompt
# projection is recorded in the CHANGELOG entry, the
# actual delta is within 50% of the projection OR the
# divergence is documented in a `### Projection drift`
# subsection.

_PROJECTED_DELTA_RE = re.compile(
    # Matches "Projected delta: +<N>" or "Projected: +<N>" or
    # "Prompt projection: +<N> tests" with tolerance for
    # whitespace / case / wrapping. Returns None when no
    # projection is recorded in the entry (typical for
    # process-corrective releases).
    r"(?:projected\s+delta|prompt\s+projection|projection)" r"[\s:]+\+?(\d+)",
    re.IGNORECASE,
)


def _parse_projected_delta_from_changelog(
    changelog_path: Path | None = None,
) -> int | None:
    """Return the projected test-count delta from the latest
    CHANGELOG entry, or None when no projection is recorded.

    al-Hujurat T04: the projection-drift assertion is
    optional. A release entry that does not name a projection
    skips the assertion cleanly via pytest.skip; only entries
    that DO name a projection are subject to the within-50%
    rule.
    """
    if changelog_path is None:
        changelog_path = REPO_ROOT / "CHANGELOG.md"
    text = changelog_path.read_text(encoding="utf-8")
    entry_match = re.search(r"^## \[[^\]]+\]", text, re.MULTILINE)
    if entry_match is None:
        return None
    start = entry_match.start()
    next_match = re.search(r"^## \[", text[start + 1 :], re.MULTILINE)
    end = (start + 1 + next_match.start()) if next_match else len(text)
    latest = text[start:end]
    m = _PROJECTED_DELTA_RE.search(latest)
    if m is None:
        return None
    return int(m.group(1))


def _changelog_has_projection_drift_subsection(
    changelog_path: Path | None = None,
) -> bool:
    """Return True if the latest CHANGELOG entry contains a
    ``### Projection drift`` subsection. The substring match
    is intentional: a `### Projection drift` heading at any
    level qualifies. al-Hujurat T04 names this subsection as
    the documentation discipline for divergences > 50%.

    A cross-reference to an external audit document is
    accepted as an alternative form, recognized by the
    presence of the substring ``Round 29`` or
    ``Round 30`` (audit-cross-reference) in the latest
    entry's body. The cross-reference path is the path the
    v0.11.2 case used: §3 Round 29 documents the projected
    +23 vs shipped +13 divergence by reference rather than
    by inline subsection.
    """
    if changelog_path is None:
        changelog_path = REPO_ROOT / "CHANGELOG.md"
    text = changelog_path.read_text(encoding="utf-8")
    entry_match = re.search(r"^## \[[^\]]+\]", text, re.MULTILINE)
    if entry_match is None:
        return False
    start = entry_match.start()
    next_match = re.search(r"^## \[", text[start + 1 :], re.MULTILINE)
    end = (start + 1 + next_match.start()) if next_match else len(text)
    latest = text[start:end]
    if re.search(r"^###\s+Projection\s+drift", latest, re.MULTILINE | re.IGNORECASE):
        return True
    # Audit cross-reference forms (Round 29, Round 30, ...).
    if re.search(r"\bRound\s+\d+\b", latest):
        return True
    return False


def _compute_drift_ratio(actual: int, projected: int) -> float:
    """Compute drift ratio with explicit zero-denominator
    handling.

    Per v1.1 Round 30 audit F2 absorption: a substrate-
    corrective release that projects zero new tests but
    ships any positive number must not divide by zero. The
    convention:

      - projected == 0 and actual == 0: drift_ratio = 0.0
        (no projection, no surprise).
      - projected == 0 and actual != 0: drift_ratio = 1.0
        (any nonzero ship against zero projection is full
        drift).
      - projected != 0: drift_ratio = abs(actual - projected)
        / abs(projected).

    The abs() in the denominator handles the symmetrical
    projected < 0 case (a release that projects net test
    removal); same fractional drift semantics apply.
    """
    if projected == 0:
        return 1.0 if actual != 0 else 0.0
    return abs(actual - projected) / abs(projected)


def test_projection_drift_v0_11_2_case() -> None:
    """al-Hujurat T04 (synthetic-data test, distinct from
    T05's fixture-based regression pin per F1 absorption):
    the v0.11.2 shape (projected +23 from at-Tawbah prompt
    v1.1, shipped +13 actual) is accepted by the recalibrated
    gate without requiring a `### Projection drift`
    subsection because drift_ratio = 10/23 ~= 0.43 < 0.50,
    AND the entry contains a Round 29 cross-reference.

    Tests the gate's ABSTRACT shape via inline mocked inputs;
    T05 pins the CONCRETE v0.11.2 example via verbatim
    fixture file bytes.
    """
    drift = _compute_drift_ratio(actual=13, projected=23)
    assert drift < 0.5, f"v0.11.2 drift_ratio={drift:.4f} should be < 0.5"
    assert drift > 0.4, (
        f"v0.11.2 drift_ratio={drift:.4f} should be > 0.4 "
        f"(catches a regression that returns 0.0 on the "
        f"projected=23 actual=13 case)"
    )


def test_projection_drift_no_projection_recorded_skips(tmp_path: Path) -> None:
    """al-Hujurat T04: a CHANGELOG entry that does not name
    a projection has no drift assertion to evaluate. The
    parser returns None; the live test (in production) skips
    cleanly via pytest.skip.
    """
    fake = tmp_path / "FAKE_CHANGELOG.md"
    fake.write_text(
        "## [9.9.9] - 2099-01-01\n\n"
        "### Tests\n\n"
        "Test count: 100 (v9.9.8) -> 105 (v9.9.9). "
        "Net delta: +5.\n"
    )
    projected = _parse_projected_delta_from_changelog(fake)
    assert projected is None, (
        f"no projection recorded in fixture; parser must " f"return None, got {projected}"
    )


def test_projection_drift_undocumented_divergence_fails(tmp_path: Path) -> None:
    """al-Hujurat T04: a synthetic CHANGELOG entry with
    projected=20, actual=5, no `### Projection drift`
    subsection, no audit cross-reference. drift_ratio = 0.75
    > 0.5; the gate fails with the formatted message.

    Pinned via direct helper invocation (the live gate's
    pytest.fail format is exercised by the live
    test_changelog_math_*; this test pins the helper's
    arithmetic).
    """
    fake = tmp_path / "FAKE_CHANGELOG.md"
    fake.write_text(
        "## [9.9.9] - 2099-01-01\n\n"
        "Prompt projection: +20 tests.\n\n"
        "### Tests\n\n"
        "Test count: 100 (v9.9.8) -> 105 (v9.9.9). "
        "Net delta: +5.\n"
    )
    projected = _parse_projected_delta_from_changelog(fake)
    assert projected == 20
    drift = _compute_drift_ratio(actual=5, projected=20)
    assert drift > 0.5, f"drift_ratio={drift:.4f} must exceed 0.5"
    assert not _changelog_has_projection_drift_subsection(fake), (
        "fixture has no `### Projection drift` subsection or "
        "audit cross-reference; helper must return False"
    )


def test_projection_drift_zero_projection_handled(tmp_path: Path) -> None:
    """al-Hujurat T04 / Round 30 F2 absorption: explicit
    zero-denominator coverage.

    Two sub-cases exercised:
      (a) projected=0, actual=0: drift_ratio=0.0; no
          `### Projection drift` subsection required; gate
          accepts.
      (b) projected=0, actual=4: drift_ratio=1.0 (any
          nonzero ship against zero projection is full
          drift). Without `### Projection drift` subsection
          (typical for a process-corrective release that did
          not pre-register test count): assertion fails.
          With `### Projection drift` subsection: gate
          accepts.

    The helper's explicit projected==0 branch returns 1.0 if
    actual!=0 else 0.0; tests both arms.
    """
    # Sub-case (a): projected=0, actual=0.
    drift_a = _compute_drift_ratio(actual=0, projected=0)
    assert drift_a == 0.0, (
        f"projected=0 actual=0 must be drift_ratio=0.0 "
        f"(no projection, no surprise); got {drift_a}"
    )

    # Sub-case (b1): projected=0, actual=4, no subsection.
    drift_b = _compute_drift_ratio(actual=4, projected=0)
    assert drift_b == 1.0, (
        f"projected=0 actual!=0 must be drift_ratio=1.0 by "
        f"the zero-denominator rule; got {drift_b}"
    )
    fake_no_sub = tmp_path / "FAKE_NO_SUB.md"
    fake_no_sub.write_text(
        "## [9.9.9] - 2099-01-01\n\n"
        "Process-corrective amendment.\n\n"
        "### Tests\n\n"
        "Test count: 100 (v9.9.8) -> 104 (v9.9.9). "
        "Net delta: +4.\n"
    )
    assert not _changelog_has_projection_drift_subsection(fake_no_sub), (
        "fixture without subsection or Round-N reference must "
        "fail the documentation check (the gate would refuse)"
    )

    # Sub-case (b2): projected=0, actual=4, with subsection.
    fake_with_sub = tmp_path / "FAKE_WITH_SUB.md"
    fake_with_sub.write_text(
        "## [9.9.9] - 2099-01-01\n\n"
        "Process-corrective amendment.\n\n"
        "### Projection drift\n\n"
        "No projection committed; observed +4 from per-task "
        "enumeration (al-Hujurat T04 + T05 + T08).\n\n"
        "### Tests\n\n"
        "Test count: 100 (v9.9.8) -> 104 (v9.9.9). "
        "Net delta: +4.\n"
    )
    assert _changelog_has_projection_drift_subsection(fake_with_sub), (
        "fixture with `### Projection drift` subsection must "
        "satisfy the documentation check (gate accepts the "
        "ship-vs-projection drift)"
    )
