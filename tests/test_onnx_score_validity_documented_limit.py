"""Four-place pinning test for the v0.9.4 documented limit
``score_validity_optin_extra`` plus runner-integration check.

Three tests:

* Silent-pass when [onnx-profile] is mocked-absent (the
  four-place pin)
* Runner integration: score_validity runs alongside the four
  v0.9.3 checkers as the fifth diagnostic family
* OnnxProfileExtrasNotInstalled exception type is exported and
  is a subclass of ImportError
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")

from tests.fixtures.onnx.builders import make_relu_model  # noqa: E402


def test_score_validity_silent_pass_when_extra_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Decision 6 (a) of v0.9.4 prompt: when ``import onnx_tool``
    raises ImportError (the [onnx-profile] extra is not installed),
    the score-validity checker silent-passes with no diagnostic
    emitted. The four-place limit
    ``score_validity_optin_extra`` documents this behavior."""
    onnx_path = tmp_path / "relu.onnx"
    onnx.save(make_relu_model(), str(onnx_path))

    # Force ImportError on onnx_tool by inserting None into sys.modules.
    monkeypatch.setitem(sys.modules, "onnx_tool", None)
    import importlib

    import furqan_lint.onnx_adapter.score_validity as sv

    importlib.reload(sv)
    try:
        findings = list(sv.check_score_validity(None, onnx_path))
        assert findings == [], (
            "score_validity should silent-pass when [onnx-profile] "
            f"extra is missing; got {findings}"
        )
    finally:
        # Restore real onnx_tool for downstream tests.
        try:
            import onnx_tool as _real

            monkeypatch.setitem(sys.modules, "onnx_tool", _real)
        except ImportError:
            monkeypatch.delitem(sys.modules, "onnx_tool", raising=False)
        importlib.reload(sv)


def test_runner_integration_score_validity_alongside_four_v0_9_3_checkers(
    tmp_path: Path,
) -> None:
    """The runner emits ``("score_validity", d)`` tuples alongside
    the four v0.9.3 diagnostic families when score-validity
    fires. This test covers the runner-wiring contract for
    Part 2 / Decision 1: score_validity is the fifth family
    in the diagnostic-tag list."""
    pytest.importorskip("onnx_tool")
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    # TopK without axis fires score_validity (cont45 substrate).
    data = onnx.helper.make_tensor_value_info("data", onnx.TensorProto.FLOAT, [1, 100])
    k = onnx.helper.make_tensor_value_info("k", onnx.TensorProto.INT64, [1])
    values = onnx.helper.make_tensor_value_info("values", onnx.TensorProto.FLOAT, [1, 5])
    indices = onnx.helper.make_tensor_value_info("indices", onnx.TensorProto.INT64, [1, 5])
    model = onnx.helper.make_model(
        onnx.helper.make_graph(
            [onnx.helper.make_node("TopK", ["data", "k"], ["values", "indices"])],
            "t",
            inputs=[data, k],
            outputs=[values, indices],
        ),
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )
    onnx_path = tmp_path / "topk.onnx"
    onnx.save(model, str(onnx_path))

    module = to_onnx_module(model)
    diags = check_onnx_module(module, model, onnx_path)
    names = {n for n, _ in diags}
    # score_validity should be in the tag list (TopK fires the
    # profiler-coverage gap on onnx_tool 1.0.x).
    assert "score_validity" in names, f"expected score_validity in tags; got {names}"


def test_onnx_profile_extras_not_installed_exception_type_exists() -> None:
    """The OnnxProfileExtrasNotInstalled exception type is exported
    and is a subclass of ImportError (mirrors OnnxExtrasNotInstalled
    and OnnxRuntimeExtrasNotInstalled). v0.9.4 three-extra
    architecture symmetry."""
    from furqan_lint.onnx_adapter import OnnxProfileExtrasNotInstalled

    assert issubclass(OnnxProfileExtrasNotInstalled, ImportError)
