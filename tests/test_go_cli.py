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


def test_go_diff_now_implemented_returns_exit_0_on_clean_pair(
    tmp_path: Path,
) -> None:
    """``furqan-lint diff foo.go bar.go`` returns exit 0 (PASS)
    on an additive-only diff in v0.8.1.

    RETIREMENT NOTE (v0.8.1): This replaces the v0.8.0
    ``test_go_diff_returns_exit_2`` test, which pinned locked
    decision 8 (Go diff returns exit 2 because not implemented).
    v0.8.1 implements Go diff via
    :func:`furqan_lint.go_adapter.extract_public_names` plus
    :func:`furqan_lint.additive.compare_name_sets`; the
    dispatcher routes ``.go`` pairs to the new helper. Locked
    decision 8 is now satisfied differently: the diff IS
    implemented, so the verdict reflects actual additive-only
    semantics, and CI pipelines that invoked
    ``furqan-lint diff *.go`` get real PASS / MARAD signals
    instead of an exit-2 placeholder.

    Detailed Go-diff coverage moved to
    ``tests/test_go_diff.py`` (8 tests). This pin remains in
    test_go_cli.py to make the retirement visible at the
    suite-organization layer.
    """
    if not _go_extras_present():
        pytest.skip("goast binary not built; install [go] extras")
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
    assert result.returncode == 0, (
        f"expected exit 0 (PASS), got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "PASS" in result.stdout
    assert "(additive-only)" in result.stdout


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
