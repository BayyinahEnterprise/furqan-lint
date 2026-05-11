"""Phase G11.4 (Tasdiq al-Bayan / v0.14.0) T05 ONNX honest asymmetry pins.

POSITIVE asymmetry tests: ONNX behaves differently from
source-code substrates where structurally appropriate. Each pin
asserts the documented limit from an-Naziat T06 + T07 +
docs/onnx-attestation-boundary.md is mechanically enforced rather
than only documented.

Per Tasdiq al-Bayan T05 spec: 4 ONNX asymmetry pins. +4 tests
per T00 step 4.1 working hypothesis.

These tests pair with TestOnnxAsymmetry in
tests/test_gate11_cross_substrate_corpus.py (which verifies the
NEGATIVE asymmetry: ONNX-specific CASM-V codes 070/071 fire only
on ONNX). T05 here verifies the POSITIVE asymmetry: ONNX
attestation boundary excludes specific artifact classes, and the
exclusion is mechanically enforced via schema-shape constraints.

Per F-TAB-2 closure (T01 absorption): the four documented limits
align with the canonical CASM-V-070/071 substrate per
an-Naziat T01 + T06 + T07 ship, not the dispatch prompt's stale
033/034 references.
"""

# ruff: noqa: E402

from __future__ import annotations

import dataclasses
import inspect

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.manifest_schema import (
    OnnxIdentitySection,
    ValueInfoSummary,
)
from furqan_lint.gate11.onnx_signature_canonicalization import (
    canonicalize_bytes,
)


def test_onnx_attestation_substrate_is_binary() -> None:
    """T05 Pin 1 (POSITIVE asymmetry): ONNX attestation operates on
    ModelProto-derived structure (graph topology + opset_imports +
    ir_version + ValueInfo entries), NOT on source-code bytes
    (since ONNX has no source-code form -- it is binary protobuf).

    Mechanical enforcement: the gate11 attestation surface for ONNX
    is the JCS-canonical form of OnnxIdentitySection (graph
    topology layer), NOT initializer-tensor-bytes / value_info
    intermediate-bytes / sidecar-bytes. The substrate-of-record is
    the dataclass schema: only opset_imports, ir_version, inputs,
    outputs are fields (Limit 3 mechanical pin at
    tests/test_gate11_onnx_limits.py).
    """
    # The canonical bytes are JCS-shaped (JSON), not protobuf-bytes:
    section = OnnxIdentitySection(
        opset_imports=(("", 18),),
        ir_version=9,
        inputs=(ValueInfoSummary(name="x", dtype="FLOAT", shape=(1, 4)),),
        outputs=(ValueInfoSummary(name="y", dtype="FLOAT", shape=(1, 4)),),
    )
    canonical = canonicalize_bytes(section)
    # Substrate-attestation: canonical-bytes form starts with the
    # JCS opening brace (JSON), proving the attestation surface is
    # structured-graph-topology, not raw ModelProto protobuf
    # bytes (which would start with protobuf field-tag bytes like
    # \x08 / \x0a / \x12).
    assert canonical.startswith(b"{"), (
        "T05 Pin 1 violation: ONNX canonical bytes are not "
        "JCS-shaped; attestation surface is operating on raw "
        "protobuf rather than graph topology"
    )
    # And the canonical bytes do NOT include initializer (weight)
    # data. The OnnxIdentitySection schema has no initializer
    # field; weights are out of attestation surface per
    # docs/onnx-attestation-boundary.md Class B (Outside attestation
    # but under integrity):
    section_fields = {f.name for f in dataclasses.fields(OnnxIdentitySection)}
    assert "initializer" not in section_fields
    assert "weights" not in section_fields


def test_onnx_dim_param_partial_concreteness() -> None:
    """T05 Pin 2 (POSITIVE asymmetry): ONNX manifests preserve
    symbolic dimensions as strings (dim_param) and concrete
    dimensions as integers (dim_value) faithfully. A shape of
    (1, 10, 'H', 64) round-trips with 'H' preserved as string
    and the integers preserved as integers.

    Mechanical enforcement: rule 10 of onnx_signature_canonicalization
    (symbolic-vs-concrete dim preservation). Drift between manifest
    and substrate ModelProto raises CASM-V-071 at verification time
    per substrate-actual v0.13.0 T01 allocation.

    No equivalent concept in source-code substrates: Python /
    Rust / Go canonicalization operates on type expressions
    (rules 1-5 / 6-8), not on graph shape. The dim_param
    partial-concreteness asymmetry is honestly distinct.
    """
    vi_partial = ValueInfoSummary(
        name="input_tensor",
        dtype="FLOAT",
        shape=(1, 10, "H", 64),
    )
    section = OnnxIdentitySection(
        opset_imports=(("", 18),),
        ir_version=9,
        inputs=(vi_partial,),
        outputs=(),
    )
    canonical = canonicalize_bytes(section)

    # Symbolic dim 'H' appears as JSON string in canonical bytes:
    assert b'"H"' in canonical, (
        "T05 Pin 2 violation: symbolic dim 'H' not preserved as "
        "string in canonical bytes; rule 10 mechanical-enforcement "
        "broken"
    )
    # Concrete dims appear as JSON integers (no quotes):
    assert b"1," in canonical or b"[1," in canonical
    assert b"10," in canonical or b",10," in canonical
    assert b"64" in canonical
    # The concrete integers must NOT be coerced to JSON strings:
    assert b'"1"' not in canonical
    assert b'"10"' not in canonical
    assert b'"64"' not in canonical


def test_onnx_intermediates_excluded_from_attestation() -> None:
    """T05 Pin 3 (POSITIVE asymmetry): the ONNX attestation surface
    covers graph.input + graph.output ONLY; internal node outputs
    (graph.value_info entries that are not graph boundaries) are
    NOT part of the attestation surface.

    Mechanical enforcement: the OnnxIdentitySection schema has
    fields only for opset_imports / ir_version / inputs / outputs
    (Limit 3 pin at tests/test_gate11_onnx_limits.py). A future
    change to add an 'intermediates' or 'value_info' field would
    have to update the dataclass + canonicalization + verification
    paths -- a Naskh Discipline event with CHANGELOG entry.

    Substrate-attestation: two ONNX models that differ ONLY in
    internal graph.value_info entries produce the SAME canonical
    OnnxIdentitySection bytes (since the attestation operates on
    inputs/outputs only).
    """
    # Construct two sections that are identical at inputs/outputs
    # but conceptually differ at the (omitted) intermediate layer.
    # Since OnnxIdentitySection has no intermediates field, both
    # sections are byte-identical at the canonical-bytes layer --
    # this IS the structural enforcement.
    section_v1 = OnnxIdentitySection(
        opset_imports=(("", 18),),
        ir_version=9,
        inputs=(ValueInfoSummary(name="x", dtype="FLOAT", shape=(1, 4)),),
        outputs=(ValueInfoSummary(name="y", dtype="FLOAT", shape=(1, 4)),),
    )
    section_v2 = OnnxIdentitySection(
        opset_imports=(("", 18),),
        ir_version=9,
        inputs=(ValueInfoSummary(name="x", dtype="FLOAT", shape=(1, 4)),),
        outputs=(ValueInfoSummary(name="y", dtype="FLOAT", shape=(1, 4)),),
    )
    assert canonicalize_bytes(section_v1) == canonicalize_bytes(section_v2), (
        "T05 Pin 3 violation: identical input/output sections "
        "produce divergent canonical bytes (impossible per rule 9 "
        "sort + rule 10 dim preservation; would indicate a "
        "regression in OnnxIdentitySection schema layer)"
    )
    # And the schema cannot accept an 'intermediates' field:
    section_fields = {f.name for f in dataclasses.fields(OnnxIdentitySection)}
    assert "intermediates" not in section_fields
    assert "value_info" not in section_fields, (
        "T05 Pin 3 violation: 'value_info' field present in "
        "OnnxIdentitySection -- would expose internal node outputs "
        "to the attestation surface, breaking the public-surface "
        "definition for ONNX (graph.input + graph.output ONLY)"
    )


def test_onnx_neurogolf_sidecar_attestation_boundary() -> None:
    """T05 Pin 4 (POSITIVE asymmetry): NeuroGolf-convention
    sidecars (numpy_reference, probe-grid YAML, score-validity
    thresholds, model_card) are NOT part of the gate11 attestation
    surface for ONNX. A modified sidecar does NOT invalidate the
    model's gate11 attestation; sidecars are regeneratable metadata
    per docs/onnx-attestation-boundary.md Class C (Outside
    attestation entirely).

    Mechanical enforcement: OnnxIdentitySection has no sidecar-
    related fields (Limit 4 pin at tests/test_gate11_onnx_limits.py).
    A NeuroGolf sidecar lives outside the dataclass and outside
    the canonical-bytes form; the substrate-of-record is the
    schema absence.
    """
    section_fields = {f.name for f in dataclasses.fields(OnnxIdentitySection)}
    sidecar_field_names = {
        "numpy_reference",
        "probe_grid",
        "score_validity",
        "sidecar",
        "sidecars",
        "metadata",
        "model_card",
        "training_metadata",
        "neurogolf_sidecar",
    }
    overlap = section_fields & sidecar_field_names
    assert not overlap, (
        "T05 Pin 4 violation: NeuroGolf sidecar boundary breached; "
        f"OnnxIdentitySection has sidecar-related fields {overlap!r} "
        "which would force sidecar artifacts into the attestation "
        "surface, breaking the regeneratable-metadata convention "
        "documented in docs/onnx-attestation-boundary.md Class C"
    )
    # And cross-reference: the boundary doc names this asymmetry
    # explicitly:
    from pathlib import Path

    boundary_doc = (
        Path(__file__).parent.parent
        / "docs"
        / "onnx-attestation-boundary.md"
    )
    if boundary_doc.exists():
        content = boundary_doc.read_text(encoding="utf-8")
        # The doc names "NeuroGolf" (Class C section + decision
        # flowchart):
        assert "NeuroGolf" in content, (
            "docs/onnx-attestation-boundary.md does not name "
            "NeuroGolf sidecar convention; T07 (an-Naziat) "
            "documentation regression"
        )
