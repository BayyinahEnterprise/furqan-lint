"""Pinning tests for the CLI diff dispatcher's guard ordering
(file renamed in v0.8.2 from
``tests/test_rust_diff_not_implemented.py`` after the v0.8.1
Rust-diff-not-impl contract was retired by v0.8.2's Rust diff
implementation).

Two tests remain:

* Cross-language rejection (any suffix mismatch -> exit 2).
* Cross-language guard takes precedence over the now-real Rust
  diff path (a .py vs .rs pair says "cross-language", NOT a
  Rust-diff MARAD verdict). The v0.8.1 form of this test
  asserted absence of the "Rust diff not implemented" string;
  v0.8.2 flips it to assert the same precedence in the
  presence of a working Rust diff path.

Locked decision 4 (cross-language guard MUST be first) is
unchanged from v0.8.1 and remains load-bearing in v0.8.2: the
guard ordering invariant must survive the addition of the
Rust diff helper.
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


def test_cross_language_takes_precedence_over_rust_diff(
    tmp_path: Path,
) -> None:
    """A .py vs .rs pair MUST surface the cross-language message,
    NOT route to the v0.8.2 Rust diff helper.

    v0.8.2 flip: the v0.8.1 form of this test asserted absence
    of the now-defunct 'Rust diff not implemented' string. The
    invariant being pinned is the same (cross-language guard 1
    fires before Rust guard 2), but the negative assertion is
    flipped to absence of any Rust-diff verdict (PASS/MARAD on
    a single .rs file would mean the Rust helper was reached
    -- which would only happen if the cross-language guard
    were broken or reordered).
    """
    py = tmp_path / "old.py"
    rs = tmp_path / "new.rs"
    py.write_text("def f(): pass\n")
    rs.write_text("pub fn f() {}\n")
    result = _run_diff(py, rs)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Cross-language diff not supported" in result.stdout
    # The Rust diff verdict prefix would be "PASS  ... (additive-only)"
    # or "MARAD  ... (additive-only)"; absence of "(additive-only)"
    # combined with PARSE ERROR in stdout pins that no language-
    # specific helper was reached.
    assert "PARSE ERROR" in result.stdout
    # Defensive: the v0.8.1 anti-string is still absent (it
    # would only appear via a regression that revived the
    # v0.8.1 stub code path).
    assert "Rust diff not implemented" not in result.stdout
