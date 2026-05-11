"""Phase G11.3 (an-Naziat / v0.13.0) T03 tests for ONNX signature canonicalization.

Exercises rules 9-12 of the cross-substrate H-4 closure rule
numbering at the ONNX-graph layer:

* Rule 9: ValueInfo entries sorted by name (deterministic
  ordering regardless of declaration order)
* Rule 10: symbolic dim_param preserved as string; concrete
  dim_value preserved as int
* Rule 11: opset_imports sorted by domain ascending, version
  descending
* Rule 12: ir_version preserved as integer (not string)

Per F-NA-4 v1.4 absorption + F-PB-NZ-1 v1.6 absorption:
delta-against-substrate convention treats this NEW file as
contributing +5 fixtures (T00 step 4.1 pinning table T03 row).
"""

# ruff: noqa: E402

from __future__ import annotations

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.manifest_schema import (
    CasmSchemaError,
    OnnxIdentitySection,
    ValueInfoSummary,
)
from furqan_lint.gate11.onnx_signature_canonicalization import (
    canonicalize,
    canonicalize_bytes,
)


def _make_section(
    *,
    opset_imports: tuple[tuple[str, int], ...] = (("", 18),),
    ir_version: int = 9,
    inputs: tuple[ValueInfoSummary, ...] = (),
    outputs: tuple[ValueInfoSummary, ...] = (),
) -> OnnxIdentitySection:
    """Build a minimal OnnxIdentitySection for tests."""
    return OnnxIdentitySection(
        opset_imports=opset_imports,
        ir_version=ir_version,
        inputs=inputs,
        outputs=outputs,
    )


def test_canonicalization_stable_across_value_info_reorder() -> None:
    """Rule 9: ValueInfo entries sorted by name before
    serialization. Two semantically-equivalent
    OnnxIdentitySection objects with inputs in different
    declaration order produce byte-identical canonical bytes.

    Closes the cross-substrate H-4 equivalent (failure mode #1
    of §5.1 step 4: substrate-attestation-non-determinism via
    proto declaration order)."""
    vi_a = ValueInfoSummary(name="alpha", dtype="FLOAT", shape=(1, 3))
    vi_b = ValueInfoSummary(name="beta", dtype="FLOAT", shape=(1, 3))
    vi_c = ValueInfoSummary(name="gamma", dtype="FLOAT", shape=(1, 3))

    section_declared_order_1 = _make_section(inputs=(vi_a, vi_b, vi_c))
    section_declared_order_2 = _make_section(inputs=(vi_c, vi_a, vi_b))
    section_declared_order_3 = _make_section(inputs=(vi_b, vi_c, vi_a))

    bytes_1 = canonicalize_bytes(section_declared_order_1)
    bytes_2 = canonicalize_bytes(section_declared_order_2)
    bytes_3 = canonicalize_bytes(section_declared_order_3)

    assert bytes_1 == bytes_2 == bytes_3, (
        "Rule 9 violation: canonical bytes diverge for "
        "semantically-equivalent inputs in different "
        "declaration order"
    )


def test_canonicalization_preserves_dim_param_as_string() -> None:
    """Rule 10: symbolic dimensions (dim_param) preserved as
    strings; concrete dimensions (dim_value) preserved as
    integers. A graph with mixed symbolic/concrete shape
    ``(batch_size, 3, 224, 224)`` canonicalizes with
    'batch_size' as string and the rest as ints.

    Closes failure mode #3 of §5.1 step 4 (symbolic-vs-
    concrete-dim divergence)."""
    vi = ValueInfoSummary(
        name="input_tensor",
        dtype="FLOAT",
        shape=("batch_size", 3, 224, 224),
    )
    section = _make_section(inputs=(vi,))
    canonical = canonicalize(section)

    assert len(canonical["inputs"]) == 1
    canonical_shape = canonical["inputs"][0]["shape"]
    assert canonical_shape[0] == "batch_size"  # symbolic preserved as str
    assert canonical_shape[1] == 3
    assert canonical_shape[2] == 224
    assert canonical_shape[3] == 224
    assert isinstance(canonical_shape[0], str)
    for i in (1, 2, 3):
        assert isinstance(canonical_shape[i], int)
    # And concrete ints must NOT be coerced to strings (the
    # symmetric failure mode):
    assert canonical_shape[1] != "3"


def test_canonicalization_sorts_opset_imports() -> None:
    """Rule 11: opset_imports sorted by domain ascending, then
    by version descending. Multiple opset_imports for the same
    domain place the highest version first (binding-version
    discipline).

    Tests both inter-domain sorting and intra-domain version
    ordering."""
    section = _make_section(
        opset_imports=(
            ("custom.ai", 5),
            ("", 18),
            ("custom.ai", 12),
            ("", 17),  # lower version of default domain
        ),
    )
    canonical = canonicalize(section)
    opsets = canonical["opset_imports"]
    # Domain '' (default) sorts first lexicographically, with
    # version 18 (highest) preceding version 17 within domain.
    # Domain 'custom.ai' sorts second, with version 12 preceding
    # version 5.
    assert opsets == [
        {"domain": "", "version": 18},
        {"domain": "", "version": 17},
        {"domain": "custom.ai", "version": 12},
        {"domain": "custom.ai", "version": 5},
    ]


def test_canonicalization_preserves_ir_version_as_integer() -> None:
    """Rule 12: ir_version preserved as integer (not string).
    The canonical bytes contain '9' as a JSON number, not
    '"9"' as a JSON string."""
    section = _make_section(ir_version=9)
    canonical = canonicalize(section)
    assert canonical["ir_version"] == 9
    assert isinstance(canonical["ir_version"], int)
    # And the RFC 8785 bytes show the integer form, not string:
    bytes_out = canonicalize_bytes(section)
    assert b'"ir_version":9' in bytes_out
    assert b'"ir_version":"9"' not in bytes_out


def test_canonicalization_rejects_malformed_inputs() -> None:
    """Strict-mode canonicalization: malformed inputs raise
    CasmSchemaError(CASM-V-001) rather than producing a
    silent sentinel string. This pattern matches the
    per-language canonicalizers (Python at-Tawbah T03;
    Go al-Mursalat T03; ONNX an-Naziat T03)."""
    # Wrong type at the top level:
    with pytest.raises(CasmSchemaError) as exc_info:
        canonicalize("not_a_section")  # type: ignore[arg-type]
    assert exc_info.value.code == "CASM-V-001"

    # Bad shape element type:
    bad_shape_vi = ValueInfoSummary(
        name="bad", dtype="FLOAT", shape=(3.14,),  # type: ignore[arg-type]
    )
    with pytest.raises(CasmSchemaError) as exc_info:
        canonicalize(_make_section(inputs=(bad_shape_vi,)))
    assert exc_info.value.code == "CASM-V-001"

    # Empty symbolic dim_param string:
    empty_param_vi = ValueInfoSummary(
        name="bad", dtype="FLOAT", shape=("",),
    )
    with pytest.raises(CasmSchemaError) as exc_info:
        canonicalize(_make_section(inputs=(empty_param_vi,)))
    assert exc_info.value.code == "CASM-V-001"

    # bool is subclass of int but explicitly rejected (rule 10
    # type discipline):
    bool_shape_vi = ValueInfoSummary(
        name="bad", dtype="FLOAT", shape=(True,),  # type: ignore[arg-type]
    )
    with pytest.raises(CasmSchemaError) as exc_info:
        canonicalize(_make_section(inputs=(bool_shape_vi,)))
    assert exc_info.value.code == "CASM-V-001"
