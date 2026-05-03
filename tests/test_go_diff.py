"""End-to-end tests for the v0.8.1 Go additive-only diff.

Spawns the CLI via ``python -m furqan_lint.cli diff old.go new.go``
on the ``tests/fixtures/go/diff/`` fixture pairs and asserts the
verdict + exit code + diagnostic prose. Mirrors the v0.8.0
``test_go_cli.py`` shape.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DIFF_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "go" / "diff"


def _go_extras_present() -> bool:
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    pkg_root = Path(spec.origin).parent
    binary = pkg_root / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _go_extras_present(),
        reason="goast binary not built; install [go] extras",
    ),
]


def _run_diff(old: Path, new: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "diff", str(old), str(new)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_go_diff_additive_only_passes() -> None:
    """v1 -> v2_clean adds GoroutineCount and removes nothing.
    PASS with exit 0."""
    result = _run_diff(
        DIFF_FIXTURES / "api_v1.go",
        DIFF_FIXTURES / "api_v2_clean.go",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    assert "(additive-only)" in result.stdout
    assert "No public names removed" in result.stdout


def test_go_diff_removed_names_fire_marad() -> None:
    """v1 -> v2_failing removes Client and NewClient. Exit 1 with
    one diagnostic per removed name (sorted)."""
    result = _run_diff(
        DIFF_FIXTURES / "api_v1.go",
        DIFF_FIXTURES / "api_v2_failing.go",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "MARAD" in result.stdout
    assert "(additive-only)" in result.stdout
    assert "'Client'" in result.stdout
    assert "'NewClient'" in result.stdout
    # Sorted: 'Client' before 'NewClient'.
    assert result.stdout.index("'Client'") < result.stdout.index("'NewClient'")


def test_go_diff_uses_go_rename_hint() -> None:
    """Removed-name diagnostics use the Go re-export hint
    ('var Name = <new>'), not the Python alias hint."""
    result = _run_diff(
        DIFF_FIXTURES / "api_v1.go",
        DIFF_FIXTURES / "api_v2_failing.go",
    )
    assert result.returncode == 1
    assert "var Client = <new>" in result.stdout
    assert "var NewClient = <new>" in result.stdout
    # Python alias syntax must NOT appear.
    assert "Client = <new_name>" not in result.stdout


def test_go_diff_identical_files_passes() -> None:
    """Diff v1 against itself: no removals, PASS."""
    result = _run_diff(
        DIFF_FIXTURES / "api_v1.go",
        DIFF_FIXTURES / "api_v1.go",
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_go_diff_parse_error_returns_exit_2(tmp_path: Path) -> None:
    """A .go file that goast cannot parse returns exit 2 (PARSE
    ERROR), not exit 1 (MARAD) and not exit 0 (PASS). Pins the
    typed-exception dispatch in _check_go_additive."""
    bad = tmp_path / "bad.go"
    bad.write_text("package x; func F() { invalid syntax here }\n")
    good = DIFF_FIXTURES / "api_v1.go"
    result = _run_diff(good, bad)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "PARSE ERROR" in result.stdout


def test_extract_public_names_collects_uppercase_initials(tmp_path: Path) -> None:
    """extract_public_names returns all uppercase-initial names
    (functions, types, vars) and excludes lowercase-initial
    names."""
    from furqan_lint.go_adapter import extract_public_names

    src = tmp_path / "m.go"
    src.write_text(
        "package m\n"
        "type Public struct{}\n"
        "type private struct{}\n"
        "func PublicFn() {}\n"
        "func privateFn() {}\n"
        "var PublicVar = 1\n"
        "var privateVar = 2\n"
    )
    names = extract_public_names(src)
    assert "Public" in names
    assert "PublicFn" in names
    assert "PublicVar" in names
    assert "private" not in names
    assert "privateFn" not in names
    assert "privateVar" not in names


def test_extract_public_names_returns_frozenset(tmp_path: Path) -> None:
    """The return type is frozenset (not set or list) so callers
    can pass it directly to compare_name_sets without conversion
    and so the same value is hashable / safely shareable."""
    from furqan_lint.go_adapter import extract_public_names

    src = tmp_path / "m.go"
    src.write_text("package m\nfunc Foo() {}\n")
    names = extract_public_names(src)
    assert isinstance(names, frozenset)


def test_extract_public_names_includes_qualified_method_names(
    tmp_path: Path,
) -> None:
    """v0.8.2: method names are collected WITH receiver-type
    qualification (Counter.Foo, Logger.Foo). This is the FLIPPED
    form of the v0.8.1 anticipatory pin
    test_extract_public_names_includes_method_names_unqualified
    -- the v0.8.1 docstring explicitly noted "v0.8.2 will flip
    this assertion".

    The flip is what closes the v0.8.1-documented method-name
    conflation false-negative: distinct Foo methods on different
    receivers no longer collapse into one bare 'Foo' entry, so
    the additive-only diff catches the removal of one of them
    even when the other persists. The retirement of the
    method_conflation_v1 / v2 documented-limit fixtures lands
    in v0.8.2 commit 4.
    """
    from furqan_lint.go_adapter import extract_public_names

    src = tmp_path / "m.go"
    src.write_text(
        "package m\n"
        "type Counter struct{}\n"
        "type Logger struct{}\n"
        "func (c *Counter) Foo() {}\n"
        "func (l *Logger) Foo() {}\n"
    )
    names = extract_public_names(src)
    # v0.8.2 contract: method names are qualified by their
    # receiver type. Two distinct Foo methods now appear as
    # distinct names (Counter.Foo and Logger.Foo).
    assert names == frozenset({"Counter", "Logger", "Counter.Foo", "Logger.Foo"})


def test_go_diff_method_conflation_now_detected(tmp_path: Path) -> None:
    """v0.8.2: with qualified method-name emission in goast, the
    v0.8.1 method-name conflation false-negative is closed.

    RETIREMENT INVERSION (v0.8.2): replaces v0.8.1's
    test_go_diff_method_conflation_documented in
    test_go_documented_limits.py, which pinned the false-
    negative shape (only 'Logger' reported, 'Foo' missed).
    v0.8.2's qualified emission means Counter.Foo and Logger.Foo
    are distinct entries, so removing Logger AND Logger.Foo
    surfaces both removals.

    The fixture pair lived at
    tests/fixtures/go/documented_limits/method_conflation_v1.go
    and method_conflation_v2.go; both deleted in this commit.
    Replacement uses tmp_path to avoid recreating documented-
    limit infrastructure for a closed limit.
    """
    v1 = tmp_path / "v1.go"
    v2 = tmp_path / "v2.go"
    v1.write_text(
        "package api\n"
        "type Counter struct{}\n"
        "type Logger struct{}\n"
        "func (c *Counter) Foo() {}\n"
        "func (l *Logger) Foo() {}\n"
    )
    v2.write_text("package api\n" "type Counter struct{}\n" "func (c *Counter) Foo() {}\n")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "furqan_lint.cli",
            "diff",
            str(v1),
            str(v2),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "MARAD" in result.stdout
    # Logger IS reported (type removal disappears from the set).
    assert "'Logger'" in result.stdout
    # Logger.Foo IS reported (the v0.8.1 false-negative is now
    # closed; qualified emission keeps Logger.Foo and Counter.Foo
    # as distinct entries).
    assert "'Logger.Foo'" in result.stdout
    # Counter is preserved (still in v2).
    assert "'Counter'" not in result.stdout
    # Counter.Foo is preserved (still in v2).
    assert "'Counter.Foo'" not in result.stdout
