"""Go adapter CLI integration tests (v0.8.0 Phase 1).

3 tests covering the CLI-level contracts:

- The ``.go`` extension dispatches to the Go adapter.
- ``furqan-lint diff foo.go bar.go`` returns exit 2 (NOT 0) per
  locked decision 8 (CI pipelines must not silently treat the
  unimplemented case as PASS).
- Missing extras prints the install hint to stderr without a
  Python traceback (mirrors the v0.7.0.1 RustExtrasNotInstalled
  pattern).
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[1]


def _go_extras_present() -> bool:
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    pkg_root = Path(spec.origin).parent
    binary = pkg_root / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


_REASON = "goast binary not built; install [go] extras"
pytestmark_go = pytest.mark.skipif(not _go_extras_present(), reason=_REASON)


@pytestmark_go
def test_go_file_detected_by_extension(tmp_path: Path) -> None:
    """``furqan-lint check x.go`` dispatches to the Go adapter
    (not the Python adapter) and emits the Go-adapter PASS
    message string."""
    source = tmp_path / "ok.go"
    source.write_text("package ok\n\n" "func F() (int, error) { return 0, nil }\n")
    result = subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(source)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    # Check the Go-specific PASS message is emitted (vs the Rust
    # or Python one). This is the structural pin that .go went to
    # _check_go_file, not _check_python_file.
    assert "(D24, D11" in result.stdout


def test_go_diff_returns_exit_2(tmp_path: Path) -> None:
    """``furqan-lint diff foo.go bar.go`` returns exit 2 (PARSE
    ERROR), NOT exit 0 (PASS).

    Locked decision 8: CI pipelines invoking ``furqan-lint diff
    *.go`` must NOT silently treat the unimplemented case as
    PASS. The exit code matches the framework's PARSE ERROR
    semantics: the file cannot be parsed by the diff
    implementation, so no honesty claim is made.

    This test is NOT skipped on missing-extras because the
    decision is in the CLI dispatcher (cli._check_additive),
    not the go_adapter package; the dispatch fires before the
    extras would be loaded.
    """
    v1 = tmp_path / "v1.go"
    v2 = tmp_path / "v2.go"
    v1.write_text("package x\nfunc F() {}\n")
    v2.write_text("package x\nfunc F() {}\n")
    result = subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "diff", str(v1), str(v2)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 2, (
        f"expected exit 2 (PARSE ERROR), got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "Go diff is not implemented" in result.stdout
    assert "see CHANGELOG" in result.stdout


def test_go_missing_extras_prints_install_hint(tmp_path: Path) -> None:
    """When the bundled goast binary is missing, the CLI emits a
    one-line install hint to stderr and returns exit 1 (NOT a
    Python traceback).

    Mirrors the v0.7.0.1 RustExtrasNotInstalled pattern. The
    typed exception is raised inside parse_file and caught by
    the CLI dispatcher.
    """
    from unittest.mock import patch

    from furqan_lint.cli import _check_go_file
    from furqan_lint.go_adapter import GoExtrasNotInstalled

    source = tmp_path / "smoke.go"
    source.write_text("package smoke\n")

    def _raise_missing(path: Path) -> None:
        raise GoExtrasNotInstalled("Go support not installed. Run: pip install furqan-lint[go]")

    import io

    captured = io.StringIO()
    with (
        patch("furqan_lint.go_adapter.parse_file", side_effect=_raise_missing),
        patch.object(sys, "stderr", captured),
    ):
        exit_code = _check_go_file(source)

    assert exit_code == 1
    output = captured.getvalue()
    assert "Go support not installed" in output
    assert "pip install furqan-lint[go]" in output
    # Negative-control: must not contain Python traceback markers.
    assert "Traceback" not in output
    assert "GoExtrasNotInstalled" not in output  # typed name should not leak
