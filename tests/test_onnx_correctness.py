"""Tests for the ONNX checker pipeline.

Covers the five commit-3 tests:

* ``test_onnx_d24_fires_on_unreachable_output``
* ``test_onnx_d24_clean_when_all_outputs_reachable``
* ``test_onnx_opset_fires_on_future_op``
* ``test_onnx_opset_clean_when_all_ops_in_declared_opset``
* ``test_opset_registry_version_pinned``

The pin test (round-24 finding M2 closure) reads the resolved
``onnx.__version__`` and asserts it falls within the declared
``>=1.14,<1.19`` window. It also asserts deterministic schema
lookup behaviour for two retroactive-addition cases.
"""

from __future__ import annotations

import re

import pytest

onnx = pytest.importorskip("onnx")

from tests.fixtures.onnx.builders import (  # noqa: E402
    make_relu_model,
    make_two_output_model,
    make_unknown_op_model,
    make_unreachable_output_model,
)


def test_onnx_d24_fires_on_unreachable_output() -> None:
    """A model whose graph.output declares a tensor that no node
    produces fires an ``all_paths_emit`` finding."""
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    module = to_onnx_module(make_unreachable_output_model())
    findings = check_onnx_module(module)
    names = [n for n, d in findings]
    assert "all_paths_emit" in names, f"expected all_paths_emit; got {names}"
    diag = next(d for n, d in findings if n == "all_paths_emit")
    assert diag.output_name == "z"


def test_onnx_d24_clean_when_all_outputs_reachable() -> None:
    """A model where every declared output is produced by some
    node fires no ``all_paths_emit`` finding."""
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    module = to_onnx_module(make_two_output_model())
    findings = check_onnx_module(module)
    names = [n for n, d in findings]
    assert "all_paths_emit" not in names, f"expected no all_paths_emit findings; got {findings}"


def test_onnx_opset_fires_on_future_op() -> None:
    """A model with an op_type that does not exist in the declared
    opset fires an ``opset_compliance`` finding."""
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    module = to_onnx_module(make_unknown_op_model())
    findings = check_onnx_module(module)
    names = [n for n, d in findings]
    assert "opset_compliance" in names, f"expected opset_compliance; got {names}"
    diag = next(d for n, d in findings if n == "opset_compliance")
    assert diag.op_type == "XQyzNotARealOp"


def test_onnx_opset_clean_when_all_ops_in_declared_opset() -> None:
    """A model whose every node uses an op present in the declared
    opset fires no ``opset_compliance`` finding."""
    from furqan_lint.onnx_adapter.runner import check_onnx_module
    from furqan_lint.onnx_adapter.translator import to_onnx_module

    module = to_onnx_module(make_relu_model(opset_version=14))
    findings = check_onnx_module(module)
    names = [n for n, d in findings]
    assert "opset_compliance" not in names, f"expected no opset_compliance findings; got {findings}"


def test_opset_registry_version_pinned() -> None:
    """The installed onnx package version must fall within the
    declared >=1.14,<1.19 pin window (round-24 finding M2 / Decision 4).

    Also asserts that a canonical opset-14 op (Relu) and a
    canonical opset-13 op (Identity) are both deterministically
    resolvable at their introduction versions across the pin
    window. This is the four-place-completeness pinning test for
    the registry-pin documented limit (see fixture at
    tests/fixtures/onnx/documented_limits/registry_pin_window.py).
    """
    import onnx.defs as _defs

    version = str(onnx.__version__)
    m = re.match(r"^(\d+)\.(\d+)", version)
    assert m, f"could not parse onnx version: {version}"
    major, minor = int(m.group(1)), int(m.group(2))
    # >= 1.14 and < 1.19
    assert (major, minor) >= (1, 14), (
        f"onnx version {version} below the pinned lower bound 1.14; "
        f"the [onnx] extra in pyproject.toml requires >=1.14,<1.19."
    )
    assert (major, minor) < (1, 19), (
        f"onnx version {version} at or above the pinned upper bound 1.19; "
        f"the [onnx] extra in pyproject.toml requires <1.19 to keep the "
        f"op registry deterministic across package upgrades."
    )
    # Two known retroactive-addition cases handled deterministically.
    relu_schema = _defs.get_schema("Relu", max_inclusive_version=14)
    assert relu_schema is not None
    identity_schema = _defs.get_schema("Identity", max_inclusive_version=14)
    assert identity_schema is not None
