"""Runner-integration tests for the v0.9.3 signature.

Two tests:

* ``test_check_onnx_module_runs_all_four_checkers``: the
  three-arg call returns four-checker output (the new tag
  ``"numpy_divergence"`` is registered alongside the v0.9.0 /
  v0.9.1 / v0.9.2 tags).
* ``test_check_onnx_module_fail_fast_typerror_on_two_arg_call``:
  calling ``check_onnx_module(module, model_proto)`` (missing
  the new ``model_path``) raises ``TypeError`` per round-30
  fail-fast / round-33 HIGH-1 closure. The existing v0.9.1 pin
  on the one-arg call ``check_onnx_module(module)`` continues
  to pass through v0.9.3.
"""

from __future__ import annotations

from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")

from tests.fixtures.onnx.builders import (  # noqa: E402
    make_relu_model,
    make_unreachable_output_model,
)


def test_check_onnx_module_runs_all_four_checkers(tmp_path: Path) -> None:
    """The three-arg ``check_onnx_module(module, model_proto, model_path)``
    runs D24-onnx, opset-compliance, D11-onnx, and numpy_divergence.

    For this test we use ``make_unreachable_output_model`` (D24
    fires) and a ``model_path`` pointing at a location with no
    NeuroGolf sidecar (numpy_divergence silent-passes per
    Decision 6 condition (b)/(c)). The diagnostic-tag list
    contains ``"all_paths_emit"`` and may also contain other
    tags depending on the model state.
    """
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    model = make_unreachable_output_model()
    module = to_onnx_module(model)
    diags = check_onnx_module(module, model, tmp_path / "no_sidecar.onnx")
    names = {n for n, _ in diags}
    assert "all_paths_emit" in names


def test_check_onnx_module_fail_fast_typerror_on_two_arg_call() -> None:
    """Round-33 HIGH-1: ``check_onnx_module(module, model_proto)``
    (missing the new ``model_path`` parameter) raises ``TypeError``.
    The fail-fast discipline catches pre-v0.9.3 call sites that
    were not updated when the signature evolved.

    The existing v0.9.1 pin on the one-arg call also continues
    to raise ``TypeError`` (one missing argument vs two missing
    arguments; both raise).
    """
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    model = make_relu_model()
    module = to_onnx_module(model)
    with pytest.raises(TypeError):
        check_onnx_module(module, model)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        check_onnx_module(module)  # type: ignore[call-arg]
