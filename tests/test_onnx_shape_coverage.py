"""Tests for D11-onnx shape-coverage via strict-mode shape inference.

Covers the v0.9.1 commit-3 checker tests:

* ``test_d11_onnx_fires_on_shape_mismatch`` (firing test on the
  fixed builder; replaces the deleted v0.9.0 pin
  ``test_onnx_d11_deferred_v0_9_0_passes`` per Decision 4 of the
  v0.9.1 prompt)
* ``test_d11_onnx_clean_when_shapes_match``
* ``test_d11_onnx_clean_on_broadcast_compatible``
* ``test_d11_onnx_silent_pass_on_dim_param``
* ``test_d11_onnx_silent_pass_on_negative_dim``
* ``test_d11_onnx_parser_handles_multi_op_message``
* ``test_d11_onnx_parser_unparseable_fallback``
* ``test_d11_onnx_runner_alongside_d24_and_opset``

The dynamic-shape deferral pin
(``test_d11_onnx_dynamic_shape_silent_pass_pin``) lands in
commit 4 alongside the dynamic-shape documented-limit fixture.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

onnx = pytest.importorskip("onnx")
shape_inference = pytest.importorskip("onnx.shape_inference")

from tests.fixtures.onnx.builders import (  # noqa: E402
    make_relu_model,
    make_shape_mismatch_d11_deferred_model,
)


def _vi(name: str, dims, elem_type=None):
    """Local convenience for building TypeProto ValueInfo."""
    if elem_type is None:
        elem_type = onnx.TensorProto.FLOAT
    return onnx.helper.make_tensor_value_info(name, elem_type, list(dims))


def _model(nodes, inputs, outputs, opset=14):
    return onnx.helper.make_model(
        onnx.helper.make_graph(nodes, "t", inputs=inputs, outputs=outputs),
        opset_imports=[onnx.helper.make_opsetid("", opset)],
        ir_version=8,
    )


def test_d11_onnx_fires_on_shape_mismatch() -> None:
    """The v0.9.1 firing test on the now-correct builder.

    ``make_shape_mismatch_d11_deferred_model()`` produces a
    Concat([1,10], [1,10], axis=1) with declared output [1,10].
    Strict-mode raises InferenceError; the checker yields one
    ``shape_coverage`` diagnostic naming the Concat op.

    This test replaces the deleted v0.9.0 pinning test
    ``test_onnx_d11_deferred_v0_9_0_passes`` per Decision 4 of
    the v0.9.1 prompt (delete-plus-add discipline; round-30
    finding MED-1 closure).
    """
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    model = make_shape_mismatch_d11_deferred_model()
    findings = list(check_shape_coverage(model))
    assert findings, "expected at least one shape_coverage finding"
    assert any(
        d.op_type == "Concat" for d in findings
    ), f"expected a Concat finding; got {[(d.op_type, d.message) for d in findings]}"
    # The error_kind should be ShapeInferenceError (Decision 6 / round-30 m2).
    diag = next(d for d in findings if d.op_type == "Concat")
    assert "ShapeInferenceError" in diag.error_kind
    # The diagnosis should name the op.
    assert "Concat" in diag.diagnosis


def test_d11_onnx_clean_when_shapes_match() -> None:
    """A well-formed model (Relu of [1,4] producing [1,4]) yields
    no shape_coverage findings."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    findings = list(check_shape_coverage(make_relu_model()))
    assert findings == [], f"expected no findings on clean model; got {findings}"


def test_d11_onnx_clean_on_broadcast_compatible() -> None:
    """Add of [1,10] and [5,10] is broadcast-compatible per ONNX
    semantics; declared output [5,10] is correct. Strict-mode
    silent-passes; the checker yields no findings."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    model = _model(
        [onnx.helper.make_node("Add", ["a", "b"], ["c"])],
        inputs=[_vi("a", [1, 10]), _vi("b", [5, 10])],
        outputs=[_vi("c", [5, 10])],
    )
    findings = list(check_shape_coverage(model))
    assert findings == []


def test_d11_onnx_silent_pass_on_dim_param() -> None:
    """A model with symbolic dim_param shapes (e.g., 'batch') is
    silent-passed by strict-mode; the checker yields no
    findings. Decision 3 of the v0.9.1 prompt."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    model = _model(
        [onnx.helper.make_node("Relu", ["x"], ["y"])],
        inputs=[_vi("x", ["batch", 10])],
        outputs=[_vi("y", ["batch", 10])],
    )
    findings = list(check_shape_coverage(model))
    assert findings == []


def test_d11_onnx_silent_pass_on_negative_dim() -> None:
    """A model with empty dim (None / dynamic, modeled as
    ``-1`` or unset) is silent-passed by strict-mode."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    # ``None`` here produces an unset dim_value/dim_param (dynamic dim).
    model = _model(
        [onnx.helper.make_node("Relu", ["x"], ["y"])],
        inputs=[_vi("x", [None, 10])],
        outputs=[_vi("y", [None, 10])],
    )
    findings = list(check_shape_coverage(model))
    assert findings == []


def test_d11_onnx_parser_handles_single_op_message() -> None:
    """A single per-op `(op_type:NAME): [KIND] body` line in the
    InferenceError message is captured as one finding. Establishes
    the regex's baseline (the 1-of-N case)."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        ShapeCoverageDiagnostic,
        check_shape_coverage,
    )

    fake_message = (
        "[ShapeInferenceError] Inference error(s):\n"
        " (op_type:Concat): [ShapeInferenceError] Inferred shape "
        "and existing shape differ in dimension 1: (20) vs (10)\n"
    )

    def _raise(model_proto, strict_mode=True, **kwargs):
        raise onnx.shape_inference.InferenceError(fake_message)

    with patch.object(onnx.shape_inference, "infer_shapes", _raise):
        findings = list(check_shape_coverage(make_relu_model()))

    assert len(findings) == 1
    diag = findings[0]
    assert isinstance(diag, ShapeCoverageDiagnostic)
    assert diag.op_type == "Concat"
    assert diag.error_kind == "ShapeInferenceError"
    assert "differ in dimension 1" in diag.message


def test_d11_onnx_parser_handles_multi_op_message() -> None:
    """When the InferenceError message contains multiple
    ``(op_type:NAME): [KIND] BODY`` lines, the regex captures
    one finding per line."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        ShapeCoverageDiagnostic,
        check_shape_coverage,
    )

    fake_message = (
        "[ShapeInferenceError] Inference error(s):\n"
        " (op_type:Concat): [ShapeInferenceError] Inferred shape "
        "and existing shape differ in dimension 1: (20) vs (10)\n"
        " (op_type:Add): [ShapeInferenceError] Incompatible "
        "dimensions\n"
    )

    def _raise(model_proto, strict_mode=True, **kwargs):
        raise onnx.shape_inference.InferenceError(fake_message)

    with patch.object(onnx.shape_inference, "infer_shapes", _raise):
        findings = list(check_shape_coverage(make_relu_model()))

    op_types = sorted(d.op_type for d in findings)
    assert op_types == ["Add", "Concat"], f"expected one finding per op; got {op_types}"
    for d in findings:
        assert isinstance(d, ShapeCoverageDiagnostic)
        assert d.error_kind == "ShapeInferenceError"


def test_d11_onnx_parser_unparseable_fallback() -> None:
    """When the InferenceError message has a format the regex
    cannot match, the checker emits one generic finding so the
    user still learns of the issue."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    fake_message = (
        "Some future onnx release reformatted this completely "
        "differently and the regex misses everything"
    )

    def _raise(model_proto, strict_mode=True, **kwargs):
        raise onnx.shape_inference.InferenceError(fake_message)

    with patch.object(onnx.shape_inference, "infer_shapes", _raise):
        findings = list(check_shape_coverage(make_relu_model()))

    assert len(findings) == 1
    assert findings[0].op_type == "<unknown>"
    assert findings[0].error_kind == "<unknown>"
    assert fake_message in findings[0].message


def test_d11_onnx_runner_alongside_d24_and_opset(tmp_path: Path) -> None:
    """``check_onnx_module`` runs all three checkers in order and
    requires both ``module`` and ``model_proto`` (Decision 2 of
    the v0.9.1 prompt; round-30 MED-2 closure). A module with
    a shape mismatch fires ``shape_coverage`` only (D24 and
    opset are clean for this fixture)."""
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    model = make_shape_mismatch_d11_deferred_model()
    module = to_onnx_module(model)
    diags = check_onnx_module(module, model)
    names = sorted({n for n, _ in diags})
    assert "shape_coverage" in names, f"expected shape_coverage in {names}"
    # And calling with one positional argument should fail-fast
    # per Decision 2 (TypeError, not silent-skip).
    with pytest.raises(TypeError):
        check_onnx_module(module)  # type: ignore[call-arg]


def test_d11_onnx_dynamic_shape_silent_pass_pin() -> None:
    """v0.9.1 documented-limit pin (four-place pattern):
    strict-mode shape inference silent-passes on dim_param.

    A passthrough model with a symbolic ``dim_param`` batch dim
    (``["batch", 10] -> Relu -> ["batch", 10]``) is accepted by
    strict_mode without raising; the checker yields no findings.
    The fixture documents this at
    ``tests/fixtures/onnx/documented_limits/dynamic_shape_silent_pass.py``.

    A future onnx release that changes the policy on dim_param
    handling will fail this test; that is the four-place gate's
    intended catch boundary.
    """
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )
    from tests.fixtures.onnx.builders import (
        make_dim_param_passthrough_model,
    )

    findings = list(check_shape_coverage(make_dim_param_passthrough_model()))
    assert findings == [], f"v0.9.1 strict_mode should silent-pass on dim_param; got {findings}"
