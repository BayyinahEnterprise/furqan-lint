"""Tests for D11-onnx type-compliance via check_type=True.

Covers the v0.9.2 commit-2 tests:

* ``test_d11_onnx_type_mismatch_fires_on_equal_float_op10`` -
  the Gap 1 closure firing test (Equal-on-float in opset 10
  fires under check_type=True; was silent under v0.9.1's
  strict_mode-only call).
* ``test_d11_onnx_type_mismatch_fires_on_reshape_float_shape_op13`` -
  a second non-Equal op-type-restriction case (Reshape's
  shape input must be int64).
* ``test_d11_onnx_type_compliance_silent_pass_on_well_typed_equal_int64`` -
  Equal-on-int64 at opset 10 is well-typed and silent-passes.
* ``test_d11_onnx_type_compliance_silent_pass_on_well_typed_relu_float`` -
  Relu-on-float at opset 14 is well-typed and silent-passes.
* ``test_d11_onnx_type_mismatch_regex_matches_message`` -
  the new ``_TYPE_MISMATCH_RE`` matches both empirical body
  shapes (``A typestr:`` and ``shape typestr:``).
* ``test_d11_onnx_classifier_prefers_shape_mismatch_first`` -
  ``_classify_per_op_finding`` tries shape-mismatch first per
  Decision 3 of the v0.9.2 prompt; a message that could in
  principle match either regex routes to ``shape_mismatch``.
* ``test_d11_onnx_classifier_unparseable_returns_category`` -
  the unparseable-fallback branch sets ``category="unparseable"``.
* ``test_d11_onnx_type_mismatch_diagnosis_prose`` -
  the type-mismatch ``diagnosis`` and ``minimal_fix`` prose
  names the upgrade-opset / Cast / type-replacement options.
"""

from __future__ import annotations

import pytest

onnx = pytest.importorskip("onnx")
shape_inference = pytest.importorskip("onnx.shape_inference")

from tests.fixtures.onnx.builders import (  # noqa: E402
    make_equal_float_op10_model,
    make_equal_int64_op10_model,
    make_relu_model,
    make_reshape_float_shape_op13_model,
)


def test_d11_onnx_type_mismatch_fires_on_equal_float_op10() -> None:
    """Gap 1 closure: Equal-on-float in opset 10 was silent under
    v0.9.1's strict_mode-only call. v0.9.2 adds ``check_type=True``
    and the checker fires with ``category="type_mismatch"`` and
    error_kind ``TypeInferenceError``.

    The post-release NeuroGolf evaluation surfaced this gap (the
    cont46 bug class). v0.9.2 closes it.
    """
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    findings = list(check_shape_coverage(make_equal_float_op10_model()))
    assert findings, "expected a type_mismatch finding"
    assert any(d.op_type == "Equal" for d in findings)
    diag = next(d for d in findings if d.op_type == "Equal")
    assert diag.category == "type_mismatch"
    assert diag.error_kind == "TypeInferenceError"
    assert "tensor(float)" in diag.message


def test_d11_onnx_type_mismatch_fires_on_reshape_float_shape_op13() -> None:
    """Reshape at opset 13 requires its second input to be int64;
    passing float fires the type-restriction rule. The second
    non-Equal type-mismatch fixture per §4 of the v0.9.2 prompt.
    """
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    findings = list(check_shape_coverage(make_reshape_float_shape_op13_model()))
    assert findings
    diag = next(d for d in findings if d.op_type == "Reshape")
    assert diag.category == "type_mismatch"
    assert diag.error_kind == "TypeInferenceError"
    assert "shape typestr" in diag.message


def test_d11_onnx_type_compliance_silent_pass_on_well_typed_equal_int64() -> None:
    """Equal-on-int64 at opset 10 is well-typed under check_type;
    silent-passes."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    findings = list(check_shape_coverage(make_equal_int64_op10_model()))
    assert findings == [], f"expected silent-pass on well-typed Equal-int64; got {findings}"


def test_d11_onnx_type_compliance_silent_pass_on_well_typed_relu_float() -> None:
    """Relu-on-float at opset 14 is well-typed under check_type;
    silent-passes. Verifies that adding check_type=True does not
    introduce regressions on v0.9.1's clean fixtures."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    findings = list(check_shape_coverage(make_relu_model(opset_version=14)))
    assert findings == []


def test_d11_onnx_type_mismatch_regex_matches_message() -> None:
    """``_TYPE_MISMATCH_RE`` matches both empirical body shapes:
    ``A typestr:`` (schema parameter form, e.g., Equal) and
    ``shape typestr:`` (named input form, e.g., Reshape).
    """
    from furqan_lint.onnx_adapter.shape_coverage import (
        _TYPE_MISMATCH_RE,
    )

    msg_a = "(op_type:Equal): A typestr: T, has unsupported type: tensor(float)"
    m = _TYPE_MISMATCH_RE.match(msg_a)
    assert m is not None
    assert m.group("op") == "Equal"
    assert m.group("body").startswith("A typestr:")

    msg_shape = (
        "(op_type:Reshape, node name: r): shape typestr: tensor(int64), "
        "has unsupported type: tensor(float)"
    )
    m = _TYPE_MISMATCH_RE.match(msg_shape)
    assert m is not None
    assert m.group("op") == "Reshape"
    assert m.group("body").startswith("shape typestr:")


def test_d11_onnx_classifier_prefers_shape_mismatch_first() -> None:
    """``_classify_per_op_finding`` tries the shape-mismatch regex
    first per Decision 3 of the v0.9.2 prompt. A message with both
    a ``[KIND]`` prefix and ``typestr:`` text routes to shape-mismatch.
    """
    from furqan_lint.onnx_adapter.shape_coverage import (
        _classify_per_op_finding,
    )

    line = (
        "(op_type:Concat): [ShapeInferenceError] Inferred shape "
        "and existing shape differ in dimension 1: (20) vs (10)"
    )
    parsed = _classify_per_op_finding(line)
    assert parsed is not None
    op, kind, body, category = parsed
    assert op == "Concat"
    assert kind == "ShapeInferenceError"
    assert category == "shape_mismatch"


def test_d11_onnx_classifier_unparseable_returns_category() -> None:
    """When the InferenceError message has no recognisable per-op
    pattern, the unparseable-fallback branch emits one finding with
    ``category="unparseable"`` so downstream consumers can switch
    on the field cleanly."""
    from unittest.mock import patch

    from furqan_lint.onnx_adapter.shape_coverage import (
        check_shape_coverage,
    )

    fake_message = (
        "Some future onnx release reformatted everything and the "
        "regex misses every per-op marker."
    )

    def _raise(model_proto, strict_mode=True, **kwargs):
        raise onnx.shape_inference.InferenceError(fake_message)

    with patch.object(onnx.shape_inference, "infer_shapes", _raise):
        findings = list(check_shape_coverage(make_relu_model()))

    assert len(findings) == 1
    assert findings[0].category == "unparseable"
    assert findings[0].op_type == "<unknown>"


def test_d11_onnx_type_mismatch_diagnosis_prose() -> None:
    """The ``type_mismatch`` diagnosis names the failure mode and
    the ``minimal_fix`` enumerates the three actionable options
    (Cast / upgrade-opset / replace-op) per Decision 2 of the
    v0.9.2 prompt."""
    from furqan_lint.onnx_adapter.shape_coverage import (
        _format_for_category,
    )

    body = "A typestr: T, has unsupported type: tensor(float)"
    diagnosis, fix = _format_for_category("Equal", body, "type_mismatch")
    # Diagnosis: names the op and the failure mode.
    assert "Equal" in diagnosis
    assert "type-compliance" in diagnosis
    assert "opset" in diagnosis
    # Minimal fix: enumerates the three options.
    assert "Cast" in fix
    assert "opset" in fix
    assert "replace" in fix
