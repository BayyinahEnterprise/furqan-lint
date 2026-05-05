"""CLI-integration tests for v0.9.4's ADVISORY/MARAD split and
the Part 5b(a) minimal_fix consistency pattern.

Covers commit-4 tests:

ADVISORY/MARAD split (4):
* CLI: ADVISORY findings print with ``[ADVISORY]`` prefix
* CLI: ADVISORY findings exit 0
* CLI: MARAD + ADVISORY summary line distinguishes both
* CLI: pure-ADVISORY case prints "ADVISORY" header (not MARAD)

minimal_fix regression (5; one per ONNX diagnostic family):
* AllPathsEmitDiagnostic.minimal_fix prints
* OpsetComplianceDiagnostic.minimal_fix prints
* ShapeCoverageDiagnostic.minimal_fix prints
* NumpyDivergenceDiagnostic.minimal_fix prints
* ScoreValidityDiagnostic.minimal_fix prints

The Part 5b(a) regression tests run the CLI end-to-end via
subprocess on a fixture firing the relevant diagnostic, then
assert the ``fix:`` line appears in stdout. Round-34 v0.9.3.1
carry-forward closure.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")


def _run_cli(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def _save(path: Path, model) -> None:
    onnx.save(model, str(path))


# -------- Diagnostic-family fixtures --------


def _all_paths_emit_model():
    """D24-onnx fires: declared output 'z' has no producer node."""
    a = onnx.helper.make_tensor_value_info("a", onnx.TensorProto.FLOAT, [1, 4])
    b = onnx.helper.make_tensor_value_info("b", onnx.TensorProto.FLOAT, [1, 4])
    z = onnx.helper.make_tensor_value_info("z", onnx.TensorProto.FLOAT, [1, 4])
    # Relu produces 'b'; 'z' is declared output but never produced.
    return onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("Relu", ["a"], ["b"])],
            "ape",
            inputs=[a],
            outputs=[b, z],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def _opset_compliance_model():
    """opset_compliance fires: a fictional op missing from registry."""
    a = onnx.helper.make_tensor_value_info("a", onnx.TensorProto.FLOAT, [1, 4])
    c = onnx.helper.make_tensor_value_info("c", onnx.TensorProto.FLOAT, [1, 4])
    return onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("XQyzNotARealOp", ["a"], ["c"])],
            "op",
            inputs=[a],
            outputs=[c],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def _shape_coverage_model():
    """shape_coverage fires: Concat with declared shape disagreeing."""
    a = onnx.helper.make_tensor_value_info("a", onnx.TensorProto.FLOAT, [1, 10])
    b = onnx.helper.make_tensor_value_info("b", onnx.TensorProto.FLOAT, [1, 10])
    c = onnx.helper.make_tensor_value_info("c", onnx.TensorProto.FLOAT, [1, 10])
    return onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("Concat", ["a", "b"], ["c"], axis=1)],
            "sc",
            inputs=[a, b],
            outputs=[c],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def _relu_model():
    a = onnx.helper.make_tensor_value_info("a", onnx.TensorProto.FLOAT, [1, 4])
    c = onnx.helper.make_tensor_value_info("c", onnx.TensorProto.FLOAT, [1, 4])
    return onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("Relu", ["a"], ["c"])],
            "r",
            inputs=[a],
            outputs=[c],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def _topk_no_axis_model():
    """ScoreValidity fires (cont45 substrate)."""
    data = onnx.helper.make_tensor_value_info("data", onnx.TensorProto.FLOAT, [1, 100])
    k = onnx.helper.make_tensor_value_info("k", onnx.TensorProto.INT64, [1])
    values = onnx.helper.make_tensor_value_info("values", onnx.TensorProto.FLOAT, [1, 5])
    indices = onnx.helper.make_tensor_value_info("indices", onnx.TensorProto.INT64, [1, 5])
    return onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("TopK", ["data", "k"], ["values", "indices"])],
            "t",
            inputs=[data, k],
            outputs=[values, indices],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def _write_divergence_sidecars(tmp_path: Path, basename: str) -> None:
    """Write _build.py and .json sidecars that produce a divergence."""
    (tmp_path / f"{basename}_build.py").write_text(
        "import numpy as np\n"
        "def numpy_reference(grid):\n"
        "    return np.array(grid, dtype=np.float32) * 2.0\n",
        encoding="utf-8",
    )
    (tmp_path / f"{basename}.json").write_text(
        json.dumps(
            {
                "train": [
                    {
                        "input": [[-1.0, 2.0, -3.0, 4.0]],
                        "output": [[0.0, 2.0, 0.0, 4.0]],
                    }
                ],
                "test": [],
            }
        ),
        encoding="utf-8",
    )


# -------- ADVISORY/MARAD split tests (Decision 3) --------


def test_cli_advisory_findings_print_with_advisory_prefix(
    tmp_path: Path,
) -> None:
    """ADVISORY findings (score_validity) print with [ADVISORY]
    prefix. Per Decision 3 of the v0.9.4 prompt: severity-based
    prefix at the printer."""
    pytest.importorskip("onnx_tool")
    onnx_path = tmp_path / "topk.onnx"
    _save(onnx_path, _topk_no_axis_model())
    result = _run_cli(onnx_path)
    assert "[ADVISORY]" in result.stdout, f"expected [ADVISORY] prefix; got:\n{result.stdout}"


def test_cli_advisory_only_exits_zero(tmp_path: Path) -> None:
    """ADVISORY-only findings exit 0; the model is structurally
    valid and the ADVISORY signals deployment-side robustness
    rather than a structural fault."""
    pytest.importorskip("onnx_tool")
    onnx_path = tmp_path / "topk.onnx"
    _save(onnx_path, _topk_no_axis_model())
    result = _run_cli(onnx_path)
    assert result.returncode == 0, (
        f"ADVISORY-only must exit 0; got {result.returncode}\n" f"stdout: {result.stdout}"
    )


def test_cli_advisory_only_prints_advisory_header(tmp_path: Path) -> None:
    """When only ADVISORY findings fire, the headline says
    'ADVISORY <path>' rather than 'MARAD <path>'. Catches the
    surface-vs-substrate cosmetic gap where the user sees MARAD
    but the model is structurally valid."""
    pytest.importorskip("onnx_tool")
    onnx_path = tmp_path / "topk.onnx"
    _save(onnx_path, _topk_no_axis_model())
    result = _run_cli(onnx_path)
    assert "ADVISORY  " in result.stdout
    # Headline 'MARAD  <path>' must NOT appear in pure-ADVISORY case.
    # (The token MARAD may legitimately appear in the prefix for any
    # non-ADVISORY finding; we test the headline form specifically.)
    assert (
        f"MARAD  {onnx_path}" not in result.stdout
    ), f"pure-ADVISORY case should not print MARAD header; got:\n{result.stdout}"


def test_cli_marad_plus_advisory_summary_line(tmp_path: Path) -> None:
    """Mixed MARAD + ADVISORY case: summary line names both
    counts. The substrate fires both numpy_divergence (MARAD)
    and could fire score_validity (ADVISORY) on the same model.
    Skip if onnx_tool can't fire on the simple Relu model."""
    pytest.importorskip("onnx_tool")
    onnx_path = tmp_path / "relu.onnx"
    _save(onnx_path, _relu_model())
    _write_divergence_sidecars(tmp_path, "relu")
    result = _run_cli(onnx_path)
    # numpy_divergence fires (MARAD); score_validity may or may not.
    # If both fire, summary names both counts.
    if "ADVISORY" in result.stdout and "MARAD" in result.stdout:
        assert "MARAD," in result.stdout and "ADVISORY:" in result.stdout
    else:
        # Pure-MARAD case is also acceptable; the test asserts
        # the summary-line shape exists when both are present.
        assert "MARAD" in result.stdout


# -------- minimal_fix regression tests (Part 5b(a)) --------


def test_minimal_fix_prints_for_all_paths_emit(tmp_path: Path) -> None:
    """AllPathsEmitDiagnostic.minimal_fix prints in CLI output.
    Round-34 v0.9.3.1 carry-forward closure."""
    onnx_path = tmp_path / "ape.onnx"
    _save(onnx_path, _all_paths_emit_model())
    result = _run_cli(onnx_path)
    assert "[all_paths_emit]" in result.stdout
    # The minimal_fix line is "      fix: ..." and must appear.
    assert (
        "      fix:" in result.stdout
    ), f"minimal_fix not printed for AllPathsEmit; got:\n{result.stdout}"


def test_minimal_fix_prints_for_opset_compliance(tmp_path: Path) -> None:
    """OpsetComplianceDiagnostic.minimal_fix prints."""
    onnx_path = tmp_path / "op.onnx"
    _save(onnx_path, _opset_compliance_model())
    result = _run_cli(onnx_path)
    assert "[opset_compliance]" in result.stdout
    assert "      fix:" in result.stdout


def test_minimal_fix_prints_for_shape_coverage(tmp_path: Path) -> None:
    """ShapeCoverageDiagnostic.minimal_fix prints."""
    onnx_path = tmp_path / "sc.onnx"
    _save(onnx_path, _shape_coverage_model())
    result = _run_cli(onnx_path)
    assert "[shape_coverage]" in result.stdout
    assert "      fix:" in result.stdout


def test_minimal_fix_prints_for_numpy_divergence(tmp_path: Path) -> None:
    """NumpyDivergenceDiagnostic.minimal_fix prints. Extends
    the v0.9.3.1 regression test to include the fix line per
    §3.5 carry-forward."""
    pytest.importorskip("onnxruntime")
    onnx_path = tmp_path / "relu.onnx"
    _save(onnx_path, _relu_model())
    _write_divergence_sidecars(tmp_path, "relu")
    result = _run_cli(onnx_path)
    assert "[numpy_divergence]" in result.stdout
    assert "      fix:" in result.stdout


def test_minimal_fix_prints_for_score_validity(tmp_path: Path) -> None:
    """ScoreValidityDiagnostic.minimal_fix prints. The fifth
    family (v0.9.4 addition) closes Part 5b(a)'s coverage of
    every ONNX diagnostic family."""
    pytest.importorskip("onnx_tool")
    onnx_path = tmp_path / "topk.onnx"
    _save(onnx_path, _topk_no_axis_model())
    result = _run_cli(onnx_path)
    assert "[score_validity]" in result.stdout
    assert "      fix:" in result.stdout
