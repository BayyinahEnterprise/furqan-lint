"""Phase G11.3 (an-Naziat / v0.13.0) T06 tests for four ONNX-specific four-place limits.

ONNX gate11 has four documented limits not present in the
source-code substrates (Python / Rust / Go). Each limit gets
four-place documentation per the al-Hujurat discipline:
CHANGELOG entry + pinning test + module docstring + README
mention. The pinning test exercises both compliant and
limit-violating cases per F-AN-6 ranked-list failure mode #4
closure ("the limit is mechanically enforced, not just
documented").

The four limits:

  1. **Binary substrate**: ONNX manifests attest ModelProto
     bytes, not source bytes. The Form A checker_set_hash
     semantics differ slightly: the 'checker code' pinning is
     the same as source-code gate11, but the 'substrate'
     pinning is the protobuf binary, not source.

  2. **dim_param partial concreteness**: ONNX manifests
     preserve symbolic dimensions as strings; verification
     enforces consistency between manifest and substrate. A
     manifest cannot promote a symbolic dim to concrete (or
     vice versa) without re-attestation. CASM-V-071 raised at
     verification time when this drifts.

  3. **Intermediates excluded from attestation surface**:
     attestation covers graph.input and graph.output, NOT
     internal node outputs that are not exposed at the graph
     boundary. This is the 'public surface' definition for
     ONNX.

  4. **NeuroGolf sidecar boundary**: numpy_reference and
     probe-grid sidecars are NOT under attestation; they are
     metadata that can be regenerated without re-attesting the
     model. The boundary is documented in
     docs/onnx-attestation-boundary.md (T07).

Per F-NA-4 v1.4 absorption + F-PB-NZ-1 v1.6 absorption:
delta-against-substrate convention treats this NEW file as
contributing +4 fixtures (T00 step 4.1 pinning table T06 row,
conservative selection within +4 to +8 range per F-NA-8
implementer-latitude allowance).
"""

# ruff: noqa: E402

from __future__ import annotations

import dataclasses

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.manifest_schema import (
    OnnxIdentitySection,
    ValueInfoSummary,
)
from furqan_lint.gate11.onnx_signature_canonicalization import (
    canonicalize_bytes,
)

# ---------------------------------------------------------------------------
# Limit 1: Binary substrate (ModelProto bytes, not source bytes)
# ---------------------------------------------------------------------------


def test_limit_binary_substrate_canonical_bytes_are_jcs_form() -> None:
    """Limit 1 closure: ONNX canonical bytes for the gate11
    attestation surface come from
    onnx_signature_canonicalization.canonicalize_bytes (which
    applies RFC 8785 / JCS over the OnnxIdentitySection
    dict), NOT from a source-bytes hash of the ModelProto's
    serialized protobuf form.

    The substrate-of-record for the gate11 attestation is the
    OnnxIdentitySection's canonical-bytes form, which is the
    abstraction the signature surface signs. The raw
    ModelProto bytes participate only at the
    module_root_hash step (step 7 of the 9-step flow); the
    public-surface attestation operates on the higher-level
    OnnxIdentitySection structure.

    Pinning test: the canonical-bytes output is JSON-shaped
    (starts with b'{'), not protobuf-shaped (which would
    start with field-tag bytes like b'\\x08').
    """
    vi = ValueInfoSummary(name="x", dtype="FLOAT", shape=(1, 3, 224, 224))
    section = OnnxIdentitySection(
        opset_imports=(("", 18),),
        ir_version=9,
        inputs=(vi,),
        outputs=(),
    )
    canonical = canonicalize_bytes(section)
    assert canonical.startswith(b"{"), (
        "Limit 1 violation: canonical bytes are not JSON-shaped; "
        "the gate11 attestation surface operates on the JCS form "
        "of OnnxIdentitySection, not raw ModelProto protobuf bytes"
    )
    # And the JSON form contains the field names we sign over:
    assert b'"opset_imports"' in canonical
    assert b'"ir_version"' in canonical
    assert b'"inputs"' in canonical
    assert b'"outputs"' in canonical


# ---------------------------------------------------------------------------
# Limit 2: dim_param partial concreteness (CASM-V-071 enforcement)
# ---------------------------------------------------------------------------


def test_limit_dim_param_promote_to_concrete_changes_canonical_bytes() -> None:
    """Limit 2 closure: promoting a symbolic dim to concrete
    (or vice versa) changes the canonical bytes. The
    mechanical CASM-V-071 enforcement happens via the
    canonicalization layer (rule 10): symbolic dims preserve
    as strings, concrete as integers, and the canonical JSON
    bytes reflect the type-tag faithfully.

    Substrate-attestation: a manifest with all-concrete dims
    for a model with symbolic dims produces a DIFFERENT
    canonical fingerprint, causing signature-verification to
    fail at step 6 of the 9-step flow with the underlying
    signature mismatch (and surfacing as CASM-V-071-class
    drift at the attestation layer per SAFETY_INVARIANTS.md
    Invariant 6 step 8 extension).
    """
    vi_symbolic = ValueInfoSummary(name="input", dtype="FLOAT", shape=("batch", 3, 224, 224))
    vi_concrete = ValueInfoSummary(name="input", dtype="FLOAT", shape=(1, 3, 224, 224))
    section_symbolic = OnnxIdentitySection(
        opset_imports=(("", 18),),
        ir_version=9,
        inputs=(vi_symbolic,),
        outputs=(),
    )
    section_concrete = dataclasses.replace(section_symbolic, inputs=(vi_concrete,))

    bytes_symbolic = canonicalize_bytes(section_symbolic)
    bytes_concrete = canonicalize_bytes(section_concrete)
    assert bytes_symbolic != bytes_concrete, (
        "Limit 2 violation: symbolic-vs-concrete dim swap did "
        "not change canonical bytes; CASM-V-071 mechanical "
        "enforcement layer broken (rule 10 of "
        "onnx_signature_canonicalization)"
    )
    # And specifically, symbolic appears as JSON string, concrete as int:
    assert b'"batch"' in bytes_symbolic
    assert b'"batch"' not in bytes_concrete
    assert b"[1,3,224,224]" in bytes_concrete


# ---------------------------------------------------------------------------
# Limit 3: Intermediates excluded from attestation surface
# ---------------------------------------------------------------------------


def test_limit_intermediates_excluded_only_inputs_outputs_in_section() -> None:
    """Limit 3 closure: the OnnxIdentitySection schema has
    fields only for ``inputs`` and ``outputs`` (graph
    boundary), with no field for ``intermediates`` (internal
    node outputs).

    Substrate-of-record: a developer adding an intermediate
    ValueInfo to the attestation surface would have to extend
    OnnxIdentitySection's dataclass fields; the schema
    surface mechanically prevents inclusion by absence of a
    field rather than by runtime rejection. This is the
    'public surface' definition for ONNX (graph.input +
    graph.output ONLY).
    """
    section_fields = {f.name for f in dataclasses.fields(OnnxIdentitySection)}
    assert section_fields == {
        "opset_imports",
        "ir_version",
        "inputs",
        "outputs",
    }, (
        "Limit 3 violation: OnnxIdentitySection schema includes "
        f"unexpected fields {section_fields - {'opset_imports', 'ir_version', 'inputs', 'outputs'}!r}; "
        "intermediates / internal-node outputs must NOT be part "
        "of the attestation surface"
    )
    # And specifically, no 'intermediates' / 'internal' field:
    assert "intermediates" not in section_fields
    assert "internal" not in section_fields


# ---------------------------------------------------------------------------
# Limit 4: NeuroGolf sidecar boundary (out of attestation)
# ---------------------------------------------------------------------------


def test_limit_neurogolf_sidecar_not_in_onnx_section_schema() -> None:
    """Limit 4 closure: NeuroGolf sidecar artifacts
    (numpy_reference, probe_grid YAML, score_validity
    thresholds) are NOT fields of OnnxIdentitySection. The
    sidecar boundary mechanically prevents inclusion at the
    schema level: a developer who wants to attest a sidecar
    must use a separate manifest (or extend the schema, which
    is a CHANGELOG-tracked Naskh Discipline event).

    Substrate-of-record: the OnnxIdentitySection has only the
    four ModelProto-derived fields (opset_imports,
    ir_version, inputs, outputs); no sidecar / metadata /
    numpy_reference / probe_grid field exists. The boundary
    is enforced by schema absence rather than by runtime
    reject.
    """
    section_fields = {f.name for f in dataclasses.fields(OnnxIdentitySection)}
    # No sidecar-related fields:
    sidecar_names = {
        "numpy_reference",
        "probe_grid",
        "score_validity",
        "sidecar",
        "sidecars",
        "metadata",
        "model_card",
        "training_metadata",
    }
    overlap = section_fields & sidecar_names
    assert not overlap, (
        "Limit 4 violation: OnnxIdentitySection includes sidecar-"
        f"related fields {overlap!r}; NeuroGolf sidecar boundary "
        "documented in docs/onnx-attestation-boundary.md (T07) "
        "requires sidecar artifacts remain OUTSIDE the gate11 "
        "attestation surface"
    )
