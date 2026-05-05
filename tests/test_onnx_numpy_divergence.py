"""Tests for numpy-vs-ONNX divergence checker (v0.9.3 commit 3).

Covers 10 divergence tests:

* fires when numpy and ONNX disagree (cell-exact case)
* fires when numpy and ONNX disagree (tolerance case)
* clean when both match (cell-exact)
* clean when both match (tolerance)
* silent-pass when [onnx-runtime] extra missing (mock)
* silent-pass when reference missing
* silent-pass when probe grid missing
* fires runtime-error diagnostic when numpy_reference throws
* fires runtime-error diagnostic when InferenceSession.run throws
* multi-probe: one finding per diverging probe
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")
ort = pytest.importorskip("onnxruntime")
np = pytest.importorskip("numpy")


def _vi(name: str, dtype, shape):
    return onnx.helper.make_tensor_value_info(name, dtype, shape)


def _save_relu_float_model(path: Path) -> None:
    """Identity-Relu model with [1,4] FLOAT input/output."""
    a = _vi("a", onnx.TensorProto.FLOAT, [1, 4])
    c = _vi("c", onnx.TensorProto.FLOAT, [1, 4])
    m = onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("Relu", ["a"], ["c"])],
            "r",
            inputs=[a],
            outputs=[c],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )
    onnx.save(m, str(path))


def _save_identity_int64_model(path: Path) -> None:
    """Identity model on [1,4] INT64. Useful for the cell-exact mode
    (integer dtype triggers np.array_equal)."""
    a = _vi("a", onnx.TensorProto.INT64, [1, 4])
    c = _vi("c", onnx.TensorProto.INT64, [1, 4])
    m = onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("Identity", ["a"], ["c"])],
            "i",
            inputs=[a],
            outputs=[c],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )
    onnx.save(m, str(path))


def _write_task(path: Path, train_inputs: list) -> None:
    obj = {
        "train": [{"input": grid, "output": grid} for grid in train_inputs],
        "test": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def _write_build(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def _load_proto(path: Path):
    return onnx.load(str(path))


def test_numpy_divergence_fires_on_cell_exact_disagreement(
    tmp_path: Path,
) -> None:
    """Integer dtype output triggers np.array_equal (cell-exact);
    a wrong reference fires with category-shape summary naming
    'cell-exact'."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "ident.onnx"
    _save_identity_int64_model(onnx_path)
    _write_build(
        tmp_path / "ident_build.py",
        "import numpy as np\n"
        "def numpy_reference(grid):\n"
        "    return np.array(grid, dtype=np.int64) * 2  # WRONG\n",
    )
    _write_task(tmp_path / "ident.json", [[[1, 2, 3, 4]]])
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert len(findings) == 1
    f = findings[0]
    assert f.probe_index == 0
    assert "cell-exact" in f.divergence_summary
    assert "differ" in f.divergence_summary


def test_numpy_divergence_fires_on_tolerance_disagreement(
    tmp_path: Path,
) -> None:
    """Float output uses np.allclose; a numerically-different
    reference fires with the np.allclose tolerance summary."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "relu.onnx"
    _save_relu_float_model(onnx_path)
    _write_build(
        tmp_path / "relu_build.py",
        "import numpy as np\n"
        "def numpy_reference(grid):\n"
        "    return np.maximum(np.array(grid, dtype=np.float32), 0) + 0.5\n",
    )
    _write_task(tmp_path / "relu.json", [[[-1.0, 2.0, -3.0, 4.0]]])
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert len(findings) == 1
    assert "np.allclose" in findings[0].divergence_summary
    assert "max abs diff" in findings[0].divergence_summary


def test_numpy_divergence_clean_when_cell_exact_matches(
    tmp_path: Path,
) -> None:
    """Identity model on int64, identity reference: cell-exact
    agree; no findings."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "ident.onnx"
    _save_identity_int64_model(onnx_path)
    _write_build(
        tmp_path / "ident_build.py",
        "import numpy as np\n"
        "def numpy_reference(grid):\n"
        "    return np.array(grid, dtype=np.int64)\n",
    )
    _write_task(tmp_path / "ident.json", [[[1, 2, 3, 4]]])
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert findings == []


def test_numpy_divergence_clean_when_tolerance_matches(
    tmp_path: Path,
) -> None:
    """Float Relu vs np.maximum reference: agree within tolerance;
    no findings."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "relu.onnx"
    _save_relu_float_model(onnx_path)
    _write_build(
        tmp_path / "relu_build.py",
        "import numpy as np\n"
        "def numpy_reference(grid):\n"
        "    return np.maximum(np.array(grid, dtype=np.float32), 0)\n",
    )
    _write_task(tmp_path / "relu.json", [[[-1.0, 2.0, -3.0, 4.0]]])
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert findings == []


def test_numpy_divergence_silent_pass_when_onnxruntime_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Decision 6 (a): when onnxruntime is not importable (the
    [onnx-runtime] extra is not installed), the check
    silent-passes."""
    onnx_path = tmp_path / "relu.onnx"
    _save_relu_float_model(onnx_path)
    _write_build(
        tmp_path / "relu_build.py",
        "def numpy_reference(grid):\n    return grid\n",
    )
    _write_task(tmp_path / "relu.json", [[[1.0]]])

    # Force ImportError on onnxruntime by removing it from sys.modules
    # and inserting None to block re-import.
    monkeypatch.setitem(sys.modules, "onnxruntime", None)
    import importlib

    import furqan_lint.onnx_adapter.numpy_divergence as nd

    importlib.reload(nd)
    try:
        findings = list(nd.check_numpy_divergence(_load_proto(onnx_path), onnx_path))
        assert findings == []
    finally:
        # Restore real onnxruntime for subsequent tests.
        try:
            import onnxruntime as _real_ort

            monkeypatch.setitem(sys.modules, "onnxruntime", _real_ort)
        except ImportError:
            monkeypatch.delitem(sys.modules, "onnxruntime", raising=False)
        importlib.reload(nd)


def test_numpy_divergence_silent_pass_when_reference_missing(
    tmp_path: Path,
) -> None:
    """Decision 6 (b): no sibling _build.py = silent-pass, even if
    a task file exists."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "relu.onnx"
    _save_relu_float_model(onnx_path)
    _write_task(tmp_path / "relu.json", [[[1.0]]])
    # No _build.py
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert findings == []


def test_numpy_divergence_silent_pass_when_probe_grid_missing(
    tmp_path: Path,
) -> None:
    """Decision 6 (c): no sibling .json task file = silent-pass,
    even if a reference exists."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "relu.onnx"
    _save_relu_float_model(onnx_path)
    _write_build(
        tmp_path / "relu_build.py",
        "def numpy_reference(grid):\n    return grid\n",
    )
    # No .json
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert findings == []


def test_numpy_divergence_fires_when_numpy_reference_raises(
    tmp_path: Path,
) -> None:
    """When the numpy_reference function raises an exception, the
    check fires with a runtime-error diagnostic naming the
    probe_index and the exception type."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "relu.onnx"
    _save_relu_float_model(onnx_path)
    _write_build(
        tmp_path / "relu_build.py",
        "def numpy_reference(grid):\n" "    raise RuntimeError('reference broken')\n",
    )
    _write_task(tmp_path / "relu.json", [[[1.0]]])
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert len(findings) == 1
    assert findings[0].probe_index == 0
    assert "RuntimeError" in findings[0].diagnosis
    assert "reference broken" in findings[0].diagnosis


def test_numpy_divergence_fires_when_onnx_inference_raises(
    tmp_path: Path,
) -> None:
    """When InferenceSession.run raises (e.g., wrong input shape
    that adaptation cannot recover), fires with a runtime-error
    diagnostic on the onnx side."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "relu.onnx"
    _save_relu_float_model(onnx_path)
    # Reference accepts whatever; ONNX expects [1,4] FLOAT, we feed [1,5].
    _write_build(
        tmp_path / "relu_build.py",
        "import numpy as np\n"
        "def numpy_reference(grid):\n"
        "    return np.maximum(np.array(grid, dtype=np.float32), 0)\n",
    )
    _write_task(tmp_path / "relu.json", [[[1.0, 2.0, 3.0, 4.0, 5.0]]])
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert findings, "expected at least one finding for the size mismatch"
    f = findings[0]
    # Runtime-error diagnostic on onnx side.
    assert f.probe_index == 0
    assert "ONNX inference raised" in f.diagnosis or ("differ" in f.divergence_summary)


def test_numpy_divergence_multi_probe_one_finding_per_diverging(
    tmp_path: Path,
) -> None:
    """Multi-example task: reference disagrees with model on probe 1
    only; exactly one finding emitted with probe_index=1."""
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "ident.onnx"
    _save_identity_int64_model(onnx_path)
    # Reference returns input unchanged for probe 0/2 but doubled for
    # probe 1. Identity ONNX returns input unchanged. Disagreement on 1.
    _write_build(
        tmp_path / "ident_build.py",
        "import numpy as np\n"
        "_calls = [0]\n"
        "def numpy_reference(grid):\n"
        "    arr = np.array(grid, dtype=np.int64)\n"
        "    i = _calls[0]\n"
        "    _calls[0] += 1\n"
        "    if i == 1:\n"
        "        return arr * 2\n"
        "    return arr\n",
    )
    _write_task(
        tmp_path / "ident.json",
        [[[1, 2, 3, 4]], [[5, 6, 7, 8]], [[9, 0, 1, 2]]],
    )
    findings = list(check_numpy_divergence(_load_proto(onnx_path), onnx_path))
    assert len(findings) == 1
    assert findings[0].probe_index == 1


def test_cli_numpy_divergence_body_prints(tmp_path: Path) -> None:
    """Round-34 HIGH-1 regression test: the CLI's
    ``_check_onnx_file`` printer must include the diagnosis
    body for ``NumpyDivergenceDiagnostic`` findings.

    Pre-v0.9.3.1 the printer's isinstance tuple filtered the
    fourth diagnostic family out, producing
    ``MARAD <path>\n  1 violation(s):\n`` with no body.
    The substrate-side check_numpy_divergence emits a full
    diagnostic; the CLI surface dropped it. v0.9.3.1
    extends the isinstance tuple to include
    NumpyDivergenceDiagnostic so the body prints.

    The test runs the CLI end-to-end via subprocess on a
    fixture that triggers a divergence finding, then asserts
    the diagnosis prose appears in stdout. Per §3.5 of the
    v0.9.3.1 prompt, the test does NOT assert that
    ``minimal_fix`` prints (that gap is closed by v0.9.4
    Part 5b alongside the structural CLI-integration gate).
    """
    import re
    import subprocess
    import sys

    onnx_path = tmp_path / "dummy.onnx"
    _save_relu_float_model(onnx_path)

    # Disagreeing reference: returns 2x the input where ONNX Relu
    # would return max(input, 0). Triggers the tolerance-mode
    # divergence path.
    (tmp_path / "dummy_build.py").write_text(
        "import numpy as np\n"
        "def numpy_reference(grid):\n"
        "    return np.array(grid, dtype=np.float32) * 2.0\n",
        encoding="utf-8",
    )
    import json

    (tmp_path / "dummy.json").write_text(
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

    result = subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(onnx_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    # Exit 1: at least one MARAD fired.
    assert result.returncode == 1, (
        f"expected exit 1 (MARAD); got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    # Headline line is present.
    assert "MARAD" in result.stdout
    assert "1 violation(s):" in result.stdout

    # The diagnostic family tag and body prose are present.
    assert (
        "numpy_divergence" in result.stdout
    ), f"expected '[numpy_divergence]' tag in stdout; got:\n{result.stdout}"
    assert (
        "disagree" in result.stdout or "reference" in result.stdout
    ), f"expected diagnosis prose in stdout; got:\n{result.stdout}"

    # Negative assertion: the bug shape was an empty body after
    # the violations count. Confirm we are NOT in that state.
    bug_shape = re.compile(r"1 violation\(s\):\s*\n\s*$")
    assert not bug_shape.search(result.stdout), (
        f"CLI output still matches the round-34 HIGH-1 bug shape "
        f"(empty body after violations count):\n{result.stdout!r}"
    )
