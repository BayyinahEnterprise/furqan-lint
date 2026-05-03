"""Pinning tests for v0.8.1's three diff-dispatcher guards added
in commit 3:

* Cross-language rejection (any suffix mismatch -> exit 2).
* Cross-language takes precedence over Rust-not-implemented
  (a .py vs .rs pair says "cross-language", not "Rust not
  implemented") -- this is the load-bearing ordering pin.
* Rust diff returns exit 2 with the "Rust diff not implemented
  in v0.8.1" message.

Locked decision 4 (cross-language guard MUST be first) and
locked decision 2 (Rust diff deferred to v0.8.2). The Rust
diff fixture in
``tests/fixtures/rust/documented_limits/diff_not_implemented.rs``
documents the contract; the pinning tests below use
tmp_path-generated trivial .rs files (matching the v0.8.0
test_go_diff_returns_exit_2 pattern: the diff dispatcher fires
before the language-specific extras would load, so the test
does not require either [rust] or [go] extras).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.integration


def _run_diff(old: Path, new: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "diff", str(old), str(new)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
    )


def test_cross_language_diff_returns_exit_2(tmp_path: Path) -> None:
    """A .py vs .go pair returns exit 2 with the cross-language
    message. The dispatcher catches this BEFORE attempting any
    language-specific parse."""
    py = tmp_path / "old.py"
    go = tmp_path / "new.go"
    py.write_text("def f(): pass\n")
    go.write_text("package x\nfunc F() {}\n")
    result = _run_diff(py, go)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "PARSE ERROR" in result.stdout
    assert "Cross-language diff not supported" in result.stdout
    assert "'.py'" in result.stdout
    assert "'.go'" in result.stdout


def test_cross_language_takes_precedence_over_rust_not_implemented(
    tmp_path: Path,
) -> None:
    """A .py vs .rs pair MUST surface the cross-language message,
    NOT the 'Rust diff not implemented' message. Pins the
    guard-ordering invariant: cross-language is guard 1, Rust
    is guard 2."""
    py = tmp_path / "old.py"
    rs = tmp_path / "new.rs"
    py.write_text("def f(): pass\n")
    rs.write_text("pub fn f() {}\n")
    result = _run_diff(py, rs)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Cross-language diff not supported" in result.stdout
    assert "Rust diff not implemented" not in result.stdout


# Retired in v0.8.2 commit 2: test_rust_diff_returns_exit_2_with_v0_8_2_schedule_message
# pinned the v0.8.1 'Rust diff not implemented' contract. v0.8.2 implements
# Rust diff via rust_adapter.extract_public_names + compare_name_sets;
# detailed coverage moved to tests/test_rust_diff.py. Replacement is the
# positive PASS verdict (test_rust_diff_additive_only_passes) in that new
# file. The remaining two tests in this file (cross-language guard + its
# precedence over the now-defunct Rust-not-impl message) get renamed and
# their precedence assertion flipped in v0.8.2 commit 4 (file moves to
# tests/test_cli_diff_dispatcher.py).
