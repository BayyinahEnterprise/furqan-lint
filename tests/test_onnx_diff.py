"""Tests for the ONNX additive-only diff path.

Covers the four commit-4 tests:

* ``test_onnx_diff_fires_on_removed_output``
* ``test_onnx_diff_fires_on_shape_change``
* ``test_onnx_diff_clean_when_additive_only``
* ``test_onnx_diff_cli_exits_1_on_removal``

The diff substrate is :func:`furqan_lint.additive.compare_name_sets`
(language-agnostic) plus
:func:`furqan_lint.onnx_adapter.extract_public_names` (ONNX-specific).
Public-name format: ``input:NAME:SHAPE`` / ``output:NAME:SHAPE``
per Decision 5 of the v0.9.0 prompt.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")

from tests.fixtures.onnx.builders import (  # noqa: E402
    make_additive_model,
    make_relu_model,
    make_renamed_output_model,
    make_shape_changed_model,
    write_model,
)


def test_onnx_diff_fires_on_removed_output(tmp_path: Path) -> None:
    """A new model whose graph.output renames a tensor is treated
    as a removal of the old name (MARAD on the additive contract)."""
    from furqan_lint.additive import compare_name_sets
    from furqan_lint.onnx_adapter import extract_public_names

    old = write_model(tmp_path / "old.onnx", make_relu_model())
    new = write_model(tmp_path / "new.onnx", make_renamed_output_model())
    diags = compare_name_sets(
        previous_names=extract_public_names(old),
        current_names=extract_public_names(new),
        filename=str(new),
        language="onnx",
    )
    assert len(diags) == 1
    # The MARAD names the removed output identifier.
    assert "output:y:1x4" in diags[0].diagnosis


def test_onnx_diff_fires_on_shape_change(tmp_path: Path) -> None:
    """A shape change on the same output name registers as a
    removal-plus-addition under the ``output:NAME:SHAPE`` format
    (different SHAPE = different identifier string)."""
    from furqan_lint.additive import compare_name_sets
    from furqan_lint.onnx_adapter import extract_public_names

    old = write_model(tmp_path / "old.onnx", make_relu_model())
    new = write_model(tmp_path / "new.onnx", make_shape_changed_model())
    diags = compare_name_sets(
        previous_names=extract_public_names(old),
        current_names=extract_public_names(new),
        filename=str(new),
        language="onnx",
    )
    assert len(diags) == 1
    assert "output:y:1x4" in diags[0].diagnosis


def test_onnx_diff_clean_when_additive_only(tmp_path: Path) -> None:
    """A new model that adds outputs without removing any old
    output passes the additive contract."""
    from furqan_lint.additive import compare_name_sets
    from furqan_lint.onnx_adapter import extract_public_names

    old = write_model(tmp_path / "old.onnx", make_relu_model())
    new = write_model(tmp_path / "new.onnx", make_additive_model())
    diags = compare_name_sets(
        previous_names=extract_public_names(old),
        current_names=extract_public_names(new),
        filename=str(new),
        language="onnx",
    )
    assert diags == []


def test_onnx_diff_cli_exits_1_on_removal(tmp_path: Path) -> None:
    """Running ``furqan-lint diff old.onnx new.onnx`` where the
    new model removes an output exits 1 with a MARAD line."""
    old = write_model(tmp_path / "old.onnx", make_relu_model())
    new = write_model(tmp_path / "new.onnx", make_renamed_output_model())
    result = subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "diff", str(old), str(new)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, (
        f"expected exit 1; got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "MARAD" in result.stdout
    assert "additive_only" in result.stdout
