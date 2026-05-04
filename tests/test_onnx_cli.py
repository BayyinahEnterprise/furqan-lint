"""Tests for the ONNX CLI integration.

Covers the three commit-5 tests:

* ``test_onnx_file_detected_by_extension`` - a .onnx file routed
  through ``furqan-lint check`` exercises ``_check_onnx_file``,
  not the Python adapter.
* ``test_onnx_cross_language_rejection`` - a .py vs .onnx diff
  pair is rejected with exit code 2 (Guard 1 of the diff
  dispatcher; round-24 finding m1 ordering preserved).
* ``test_onnx_files_walked_in_directory_check`` - the directory
  walker actually walks .onnx files (round-24 finding C2
  closure: prior to v0.9.0 the walker had a hardcoded
  {.py, .rs, .go} suffix set that silently dropped .onnx files).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")

from tests.fixtures.onnx.builders import (  # noqa: E402
    make_relu_model,
    make_unreachable_output_model,
    write_model,
)


def test_onnx_file_detected_by_extension(tmp_path: Path) -> None:
    """Running ``furqan-lint check <file.onnx>`` exits 0 for a
    clean ONNX model. The 'PASS' line names the structural
    checks that ran (D24-onnx + opset-compliance) so we know
    we routed through ``_check_onnx_file`` and not the Python
    adapter."""
    path = write_model(tmp_path / "clean.onnx", make_relu_model())
    result = subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert (
        result.returncode == 0
    ), f"expected exit 0; got {result.returncode}\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout
    assert "D24-onnx" in result.stdout
    assert "opset-compliance" in result.stdout


def test_onnx_cross_language_rejection(tmp_path: Path) -> None:
    """A diff pair with mismatched suffixes (.py vs .onnx) hits
    Guard 1 of ``_check_additive`` and exits 2 with a
    'Cross-language diff not supported' line."""
    py_path = tmp_path / "old.py"
    py_path.write_text("# placeholder\n")
    onnx_path = write_model(tmp_path / "new.onnx", make_relu_model())
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "furqan_lint.cli",
            "diff",
            str(py_path),
            str(onnx_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Cross-language diff not supported" in result.stdout


def test_onnx_files_walked_in_directory_check(tmp_path: Path) -> None:
    """Round-24 finding C2 closure: ``furqan-lint check <dir>``
    walks .onnx files now (prior to v0.9.0 it hardcoded
    {.py, .rs, .go} and silently skipped .onnx).

    Setup: a directory containing one clean .py file plus one
    .onnx file with a known D24-onnx finding (declared output
    'z' has no producer node).

    Expected: the walker visits both files; the .onnx file fires
    MARAD; the directory check exits 1.
    """
    py_path = tmp_path / "clean.py"
    py_path.write_text("def f() -> None:\n    return\n")
    onnx_path = write_model(tmp_path / "broken.onnx", make_unreachable_output_model())
    result = subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    # The .onnx file's MARAD bumps the directory exit code to 1.
    assert (
        result.returncode == 1
    ), f"expected exit 1; got {result.returncode}\n{result.stdout}\n{result.stderr}"
    # The walker visited the .onnx file and reported on it.
    assert str(onnx_path) in result.stdout
    assert "all_paths_emit" in result.stdout
