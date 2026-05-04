"""Release-time sweep gate (v0.7.3, round-17 workflow addition).

Round 17 found 5 MEDIUMs all in the same equivalence class:
v0.7.2's release-sweep workflow updated CHANGELOG correctly but
missed the user-facing surfaces (README headings, README rationale
text, source docstrings, CLI PASS string, documented_limits/README
preamble) that referenced the prior version's Phase number.

Round-17 recommendation:

> Add a release-time pre-flight gate: a grep across user-visible
> surfaces for the prior version's Phase number or version-anchored
> claims. Concretely, in the release runbook... This is the same
> pattern as the existing em-dash gate.

This module implements the gate. The two tests defend against:

1. **Stale Phase numbering.** Replaces the manual sweep with an
   automated grep that fails when "Phase N" appears in any
   user-visible Rust adapter surface (README, source comments,
   documented_limits README, CLI strings). Phase numbering
   belongs in CHANGELOG (audit trail) and nowhere else;
   replacing it elsewhere with substantive checker descriptions
   ("R3 + D24 + D11 with Option- and Result-aware status
   coverage") is more durable across phase increments.

2. **Stale version-anchored claims.** Replaces the manual sweep
   with a grep that fails when the README claims something is
   "v0.X.0" specifically AND that version is older than the
   current version (i.e., the version reference should have been
   bumped during release sweep but wasn't). Targets the exact
   shape that round-11 found on v0.6.0 and round-17 found on
   v0.7.2: a versioned claim that describes a prior release.

The gate is intentionally narrow. It does NOT check:

- CHANGELOG entries (those legitimately reference prior versions
  as historical record).
- Python adapter surfaces (return_none.py / additive.py / etc.
  reference Python adapter Phase 1/2 semantics that pre-date the
  multi-language release model and are not yet in the sweep
  scope).
- Source code docstrings that describe per-version semantics
  with specific reasoning ("v0.7.0 translator emits ...";
  "v0.7.2 widens the predicate to ..."; etc.) are
  intentional historical anchors, not stale claims.

The gate's job is to catch the failure mode where "Phase 2"
or "v0.7.0 Phase 1" appears in a surface that should have been
updated to the current state at release time. It is NOT
attempting to enforce a more general no-version-references rule.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]

# Surfaces the gate checks. Each is a user-facing artifact: a
# reader looks at this file to understand what furqan-lint does,
# what limitations it has, what the Rust adapter ships in the
# current version. CHANGELOG.md is excluded because it
# legitimately references prior versions as historical record.
_USER_VISIBLE_SURFACES: tuple[Path, ...] = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "tests" / "fixtures" / "rust" / "documented_limits" / "README.md",
    REPO_ROOT / "src" / "furqan_lint" / "cli.py",
    REPO_ROOT / "src" / "furqan_lint" / "rust_adapter" / "__init__.py",
    REPO_ROOT / "src" / "furqan_lint" / "rust_adapter" / "runner.py",
    REPO_ROOT / "src" / "furqan_lint" / "rust_adapter" / "translator.py",
    REPO_ROOT / "src" / "furqan_lint" / "rust_adapter" / "edition.py",
    REPO_ROOT / "src" / "furqan_lint" / "rust_adapter" / "parser.py",
    # Go adapter surfaces added in v0.8.0 (Go adapter Phase 1).
    REPO_ROOT / "src" / "furqan_lint" / "go_adapter" / "__init__.py",
    REPO_ROOT / "src" / "furqan_lint" / "go_adapter" / "runner.py",
    REPO_ROOT / "src" / "furqan_lint" / "go_adapter" / "translator.py",
    REPO_ROOT / "src" / "furqan_lint" / "go_adapter" / "parser.py",
    # Go documented_limits README is created in commit 6 of v0.8.0;
    # the path's existence is handled by the test (it skips files
    # that don't exist yet).
    REPO_ROOT / "tests" / "fixtures" / "go" / "documented_limits" / "README.md",
)

# Pattern catches "Phase 1", "Phase 2", etc. (with word boundary
# to avoid false positives on "phaseolus" or "Phase IV" if such
# strings ever appear).
_PHASE_PATTERN = re.compile(r"\bPhase \d+\b")


def test_no_phase_numbering_in_rust_user_surfaces() -> None:
    """No user-visible Rust adapter surface may reference
    "Phase N" numbering. Phase numbering belongs in CHANGELOG
    (where it serves the audit trail) and nowhere else.

    Round 17 found 5 MEDIUMs in this equivalence class on
    v0.7.2; this gate prevents the same failure from shipping
    on a future release.
    """
    findings: list[tuple[Path, int, str]] = []
    for path in _USER_VISIBLE_SURFACES:
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text().splitlines(), start=1):
            for _match in _PHASE_PATTERN.finditer(line):
                findings.append((path.relative_to(REPO_ROOT), line_no, line.strip()))
    if findings:
        msg_lines = [
            "Found Phase N references in user-visible Rust adapter surfaces.",
            "Phase numbering belongs in CHANGELOG only; user-facing surfaces",
            "should describe what runs (e.g., 'R3 + D24 + D11'), not when it",
            "shipped (e.g., 'Phase 2'). See round-17 audit findings 1-5.",
            "",
            "Findings:",
        ]
        for rel, line_no, line in findings:
            msg_lines.append(f"  {rel}:{line_no}  {line[:120]}")
        pytest.fail("\n".join(msg_lines))


# Versioned-claim pattern: matches "v0.X.Y Rust adapter" or
# "v0.X.Y Phase 1" or similar version-anchored claims that describe
# a specific prior release. The current version is loaded from
# pyproject.toml; any version claim that does NOT match the
# current version (and is not in CHANGELOG.md) is flagged.
_VERSION_CLAIM_PATTERN = re.compile(r"\bv0\.\d+\.\d+(\.\d+)?\s+(?:Rust adapter|Phase \d+)\b")


def test_no_stale_version_anchored_claims_in_user_surfaces() -> None:
    """No user-visible Rust adapter surface may anchor a claim
    to a specific version that is not the current version.

    Targets the exact shape that round-11 found on v0.6.0
    ("v0.3.5 fixed X" claim that was a stale historical note)
    and round-17 found on v0.7.2 ("Rust adapter (v0.7.0
    Phase 1)" subsection heading anchored to a release that
    pre-dated the work it described).

    Versioned historical references in CHANGELOG.md are fine
    (audit trail). Versioned references in source code that
    name specific implementation choices ("v0.7.0 translator
    emits ...") are intentional historical anchors and are not
    flagged by this gate (the pattern is narrow: it only
    catches "vX.Y.Z Rust adapter" or "vX.Y.Z Phase N" forms,
    not arbitrary version mentions).
    """
    findings: list[tuple[Path, int, str]] = []
    for path in _USER_VISIBLE_SURFACES:
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text().splitlines(), start=1):
            for _match in _VERSION_CLAIM_PATTERN.finditer(line):
                findings.append((path.relative_to(REPO_ROOT), line_no, line.strip()))
    if findings:
        msg_lines = [
            "Found version-anchored claims in user-visible Rust adapter surfaces.",
            "These reference a specific prior release in a position that",
            "should describe the current state (e.g., section headings,",
            "feature descriptions). See round-17 audit MEDIUM 2 for the",
            "v0.7.2 instance of this failure mode.",
            "",
            "Findings:",
        ]
        for rel, line_no, line in findings:
            msg_lines.append(f"  {rel}:{line_no}  {line[:120]}")
        pytest.fail("\n".join(msg_lines))


# ---------------------------------------------------------------------------
# v0.8.4 §7.5 extension: source-file forward-reference detection
# ---------------------------------------------------------------------------
#
# Round-22 LOW found go_adapter/public_names.py referencing
# "future v0.8.2" and "deferred to v0.8.2" though v0.8.2 had already
# shipped. Same shape as the existing phase-numbering check; this
# extension generalizes the family.
#
# Scope (per locked decision): cover ONLY source-code Python files at
# src/furqan_lint/**/*.py (module docstrings + inline comments). Do
# NOT scan CHANGELOG.md, README.md, or other narrative-prose files;
# those legitimately reference past versions in history-describing
# prose (e.g. "deferred to v0.8.4 in the original prompt"), and the
# regex would false-positive on honest narrative.

_FORWARD_REF_PATTERN = re.compile(
    r"\b(?:future|deferred to)\s+v(\d+)\.(\d+)(?:\.(\d+))?\b",
    re.IGNORECASE,
)


def _current_version_tuple() -> tuple[int, int, int]:
    """Parse the current version from pyproject.toml as a tuple."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text()
    match = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', pyproject, re.MULTILINE)
    if match is None:
        pytest.fail("could not parse version from pyproject.toml")
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _find_stale_forward_references(
    search_root: Path,
    current_version: tuple[int, int, int],
) -> list[tuple[Path, int, str]]:
    """Scan every ``.py`` file under ``search_root`` for stale
    forward-references of the shape ``future vN.M`` or
    ``deferred to vN.M`` where ``N.M[.P] <= current_version``.

    Returns a list of ``(path, line_no, line_text)`` tuples for
    each stale match. An empty list means the gate passes.
    """
    findings: list[tuple[Path, int, str]] = []
    for py_file in sorted(search_root.rglob("*.py")):
        try:
            text = py_file.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in _FORWARD_REF_PATTERN.finditer(line):
                major = int(match.group(1))
                minor = int(match.group(2))
                patch = int(match.group(3)) if match.group(3) else 0
                if (major, minor, patch) <= current_version:
                    findings.append((py_file, line_no, line.strip()))
    return findings


def test_no_forward_references_in_source_file_docstrings() -> None:
    """No source-file module-docstring or comment may reference
    'future vN.M' or 'deferred to vN.M' where N.M <= current
    version. Round-22 LOW found go_adapter/public_names.py
    referencing 'future v0.8.2' / 'deferred to v0.8.2' though
    v0.8.2 had shipped. Same shape as the existing phase-numbering
    check; mechanical extension.
    """
    search_root = REPO_ROOT / "src" / "furqan_lint"
    current = _current_version_tuple()
    findings = _find_stale_forward_references(search_root, current)
    if findings:
        msg_lines = [
            "Found stale forward-references in source-code .py files.",
            f"Current version: v{current[0]}.{current[1]}.{current[2]}.",
            "Phrases like 'future vN.M' or 'deferred to vN.M' that name a",
            "version <= current are stale and must be updated to describe",
            "the actual state, or pointed at a genuinely-future version.",
            "",
            "Findings:",
        ]
        for path, line_no, line in findings:
            rel = path.relative_to(REPO_ROOT)
            msg_lines.append(f"  {rel}:{line_no}  {line[:120]}")
        pytest.fail("\n".join(msg_lines))


def test_forward_reference_gate_self_test(tmp_path: Path) -> None:
    """Self-test: the gate must catch a stale forward-reference
    AND skip a genuinely-future one.

    Synthesizes two .py files under ``tmp_path``:

    * ``stale.py``: docstring references ``future v0.8.0`` (already
      shipped against a current version of 0.8.4). Must be reported.
    * ``future.py``: docstring references ``deferred to v0.9.0``
      (genuinely-future against a current version of 0.8.4). Must
      NOT be reported.

    Pinned current version of (0, 8, 4) makes the assertion deterministic
    independent of the real pyproject.toml version (which bumps in
    commit 10 of this same release).
    """
    stale = tmp_path / "stale.py"
    stale.write_text('"""Module that references future v0.8.0."""\n')
    future = tmp_path / "future.py"
    future.write_text('"""Module that defers behavior to v0.9.0."""\n# deferred to v0.9.0\n')

    findings = _find_stale_forward_references(tmp_path, current_version=(0, 8, 4))

    stale_hits = [f for f in findings if f[0] == stale]
    future_hits = [f for f in findings if f[0] == future]

    assert stale_hits, (
        f"gate failed to catch the stale 'future v0.8.0' reference; " f"findings: {findings}"
    )
    assert not future_hits, (
        f"gate false-positived on genuinely-future 'deferred to v0.9.0'; "
        f"findings: {future_hits}"
    )
