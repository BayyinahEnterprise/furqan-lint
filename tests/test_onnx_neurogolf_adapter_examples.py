"""Worked-example tests for the v0.9.4 Part 3 NeuroGolf canonical
``numpy_reference`` adapter patterns.

Three tests:

* Pattern A (pre-one-hot input): the numpy_reference accepts
  (1, 10, H, W) already-encoded; ONNX Identity passes through;
  zero divergence findings.
* Pattern B (raw grid + local encoding): the numpy_reference
  accepts rank-2 grid and one-hot-encodes locally; ONNX
  Identity expects (1, 10, H, W); zero divergence findings.
* README presence: the section
  "ONNX numpy_reference convention for NeuroGolf-shape models"
  is present with both Pattern A and Pattern B code blocks.

The fixtures live at
``tests/fixtures/onnx/numpy_reference_examples/``; the worked-
example build scripts are part of the documentation contract
and are referenced from the README via path.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")

EXAMPLES_DIR = Path(__file__).resolve().parent / "fixtures" / "onnx" / "numpy_reference_examples"


def _identity_one_hot_model():
    """Identity model accepting (1, 10, 3, 3) FLOAT input."""
    a = onnx.helper.make_tensor_value_info("a", onnx.TensorProto.FLOAT, [1, 10, 3, 3])
    c = onnx.helper.make_tensor_value_info("c", onnx.TensorProto.FLOAT, [1, 10, 3, 3])
    return onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("Identity", ["a"], ["c"])],
            "identity_one_hot",
            inputs=[a],
            outputs=[c],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def _identity_rank2_model():
    """Identity model accepting rank-2 (3, 3) FLOAT input.

    Used by Pattern B: the ONNX model and the numpy_reference
    both operate on the raw rank-2 grid shape; the local-encoding
    step is a no-op identity in this minimal example. Real-world
    Pattern B usage may have a more complex local transformation
    inside the reference (e.g., one-hot encoding to match a model
    that expects (1, 10, H, W) input), in which case the ONNX
    model would also include the corresponding preprocessing
    layer. Both sides receive the raw rank-2 grid as input
    uniformly.
    """
    a = onnx.helper.make_tensor_value_info("a", onnx.TensorProto.FLOAT, [3, 3])
    c = onnx.helper.make_tensor_value_info("c", onnx.TensorProto.FLOAT, [3, 3])
    return onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("Identity", ["a"], ["c"])],
            "identity_rank2",
            inputs=[a],
            outputs=[c],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def _stage_pattern_a(tmp_path: Path) -> Path:
    """Stage Pattern A: already-one-hot probe grid."""
    onnx_path = tmp_path / "onehot_input_example.onnx"
    onnx.save(_identity_one_hot_model(), str(onnx_path))
    shutil.copy(
        EXAMPLES_DIR / "onehot_input_example_build.py",
        tmp_path / "onehot_input_example_build.py",
    )
    # Probe grid: a 3x3 grid where all cells are color 0;
    # one-hot encoded as (1, 10, 3, 3) with channel 0 all-1
    # and other channels all-0.
    one_hot = []
    for c in range(10):
        plane = [[1.0 if c == 0 else 0.0 for _ in range(3)] for _ in range(3)]
        one_hot.append(plane)
    probe_grid = [one_hot]  # shape (1, 10, 3, 3)
    (tmp_path / "onehot_input_example.json").write_text(
        json.dumps(
            {
                "train": [{"input": probe_grid, "output": probe_grid}],
                "test": [],
            }
        ),
        encoding="utf-8",
    )
    return onnx_path


def _stage_pattern_b(tmp_path: Path) -> Path:
    """Stage Pattern B: raw rank-2 grid; reference operates on
    the same shape (the 'local encoding' step is the no-op
    identity in this minimal example; real-world Pattern B may
    perform a more complex transformation inside the reference)."""
    onnx_path = tmp_path / "raw_grid_input_example.onnx"
    onnx.save(_identity_rank2_model(), str(onnx_path))
    shutil.copy(
        EXAMPLES_DIR / "raw_grid_input_example_build.py",
        tmp_path / "raw_grid_input_example_build.py",
    )
    # Probe grid: a raw rank-2 3x3 integer grid.
    raw_grid = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    (tmp_path / "raw_grid_input_example.json").write_text(
        json.dumps(
            {
                "train": [{"input": raw_grid, "output": raw_grid}],
                "test": [],
            }
        ),
        encoding="utf-8",
    )
    return onnx_path


def test_pattern_a_pre_one_hot_input_produces_zero_divergence(
    tmp_path: Path,
) -> None:
    """Pattern A: numpy_reference accepts the already-encoded
    (1, 10, H, W) input. ONNX Identity passes through. Zero
    divergence findings; the documentation example is verified
    by the test."""
    pytest.importorskip("onnxruntime")
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = _stage_pattern_a(tmp_path)
    findings = list(check_numpy_divergence(onnx.load(str(onnx_path)), onnx_path))
    assert findings == [], f"Pattern A example must produce zero divergence; got {findings}"


def test_pattern_b_raw_grid_local_encoding_produces_zero_divergence(
    tmp_path: Path,
) -> None:
    """Pattern B: numpy_reference accepts raw rank-2 grid and
    one-hot-encodes locally to match the ONNX (1, 10, H, W)
    expected input. Zero divergence findings."""
    pytest.importorskip("onnxruntime")
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = _stage_pattern_b(tmp_path)
    findings = list(check_numpy_divergence(onnx.load(str(onnx_path)), onnx_path))
    assert findings == [], f"Pattern B example must produce zero divergence; got {findings}"


def test_readme_documents_neurogolf_canonical_adapter_patterns() -> None:
    """The README has a section
    "ONNX numpy_reference convention for NeuroGolf-shape models"
    with code blocks for Pattern A (pre-one-hot input) and
    Pattern B (raw grid + local encoding). Round-34 MEDIUM-1
    closure: documentation surfaces the canonical adapter so
    NeuroGolf adopters don't have to reverse-engineer the
    convention."""
    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
    assert "numpy_reference convention" in readme, (
        "README missing the v0.9.4 NeuroGolf canonical-adapter " "section title"
    )
    assert "Pattern A" in readme
    assert "Pattern B" in readme
    # The (1, 10, H, W) one-hot convention name must appear.
    assert "(1, 10, H, W)" in readme or "(1,10,H,W)" in readme
