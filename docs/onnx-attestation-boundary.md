# ONNX attestation boundary

## Phase G11.3 (an-Naziat / v0.13.0)

This document is NORMATIVE for the gate11 ONNX substrate
(`language=onnx`) at v0.13.0 ship. It specifies where the
Sigstore-CASM gate11 attestation surface ends for ONNX
models, with three boundary classes and a decision flowchart
for new artifact types.

The document is paired with `SAFETY_INVARIANTS.md`
Invariant 6 (Verification flow universality) Step 8
extension; together they specify what the verifier checks at
step 8 of the 9-step verification flow for ONNX manifests.

## The three boundary classes

ONNX models in the BayyinahEnterprise NeuroGolf workflow are
accompanied by metadata artifacts (numpy_reference vectors,
probe-grid YAML files, score-validity threshold tables, etc.).
The gate11 attestation surface MUST distinguish three classes
of artifact:

### Class A: Inside attestation

The following are signed by the gate11 attestation and
verified at step 8 of the 9-step flow:

- `ModelProto.opset_imports` -- the opset version policy
  (binding-version semantics per
  `onnx_signature_canonicalization.py` rule 11)
- `ModelProto.ir_version` -- the ONNX IR version
- `ModelProto.graph.input` -- graph input ValueInfo entries
  (name, dtype, shape per ValueInfoSummary; symbolic-vs-
  concrete dim_param preserved per rule 10)
- `ModelProto.graph.output` -- graph output ValueInfo entries
  (same shape discipline)
- `ModelProto.graph.node[*]` topology -- node ordering,
  operator type, input/output edge names (the structural
  graph DAG; affects mathematical behavior)

Mathematical behavior is the load-bearing criterion: anything
whose change would silently alter the model's input-to-output
function MUST be inside attestation.

### Class B: Outside attestation, but under integrity

The following are subject to separate integrity tracking but
NOT part of the gate11 signature surface:

- `ModelProto.graph.initializer[*]` -- weight tensors
  (numerical values that change with retraining; integrity
  tracked via a separate `weights_root_hash` field if the
  application requires it, but NOT part of the gate11
  attestation per se)
- Application-level training metadata (epoch counts,
  optimizer state, training-set fingerprint)

The reason for the separation: retraining produces a new
weights tensor without changing the graph structure. A model
under continuous training would invalidate its attestation on
every epoch if weights were attested; the gate11 surface
operates at the structural-honesty layer, not at the
numerical-state layer.

### Class C: Outside attestation entirely

The following are metadata for structural-honesty checks and
can be regenerated without re-attesting the model:

- NeuroGolf `numpy_reference` vectors (reference outputs for
  probe-grid divergence checks; regeneratable from the model
  + probe grid; per the NeuroGolf canonical fixture
  convention at v0.9.x)
- NeuroGolf probe-grid YAML files (input fixtures used by
  D11-onnx / shape-coverage / numpy-divergence checkers)
- score-validity threshold tables (per-model classifier
  bounds for the score-validity checker; threshold values
  can be tuned without re-attesting the model)
- `model_card` / training documentation / README annotations
- Any artifact whose change does NOT affect mathematical
  behavior AND is not under integrity tracking

The reason for full exclusion: these artifacts support the
broader NeuroGolf workflow but are not load-bearing for the
gate11 structural-honesty contract. Including them would
fail-loud on probe-grid YAML edits (a common iteration
activity), inflating the false-positive rate at the
attestation layer.

## Decision flowchart

For a new artifact type X, decide its class via:

```text
                       New artifact X
                              |
              Does X change the mathematical
              behavior of model(input) -> output?
                              |
              ----------------+----------------
              |                                |
             YES                              NO
              |                                |
        Class A (INSIDE         Does the application require X
        attestation;            to be integrity-tracked alongside
        gate11 attests          the model (e.g., regulatory
        and verifies)           reproducibility for weights)?
                                                 |
                              -------------------+-------------------
                              |                                     |
                             YES                                   NO
                              |                                     |
                       Class B (separate                       Class C (OUTSIDE
                       integrity tracking;                     attestation
                       e.g., weights_root_hash)                entirely;
                                                               can change freely)
```

## Cross-references

- `SAFETY_INVARIANTS.md` Invariant 6 step 8 extension --
  the verification flow that consumes this boundary
  declaration
- `gate11/onnx_signature_canonicalization.py` rules 9-12 --
  the canonical-bytes form for the Class A surface
- `gate11/onnx_verification.py` -- the verifier facade
  enforcing the Class A signature surface
- `tests/test_gate11_onnx_limits.py` Limit 4
  (`test_limit_neurogolf_sidecar_not_in_onnx_section_schema`)
  -- the mechanical pin that schema-side rejects sidecar
  inclusion in OnnxIdentitySection

## Compatibility note

This document specifies the v0.13.0 ship boundary. Future
revisions (per Naskh Discipline, CHANGELOG-tracked) may
move artifacts between classes if the structural-honesty
contract requires it. For example, an artifact currently in
Class C (sidecar) could move to Class B (separate integrity)
if a regulated deployment requires reproducibility of probe-
grid YAML alongside the model. Moves between classes MUST be
CHANGELOG entries per Naskh Discipline; silent re-
classification is not permitted.

The Class A surface is closed-form: post-v0.13.0 ship, the
four fields (opset_imports, ir_version, inputs, outputs)
plus graph.node topology constitute the canonical gate11
attestation surface for ONNX. Adding fields requires a
v1.1 manifest schema bump (currently no plans;
`module_identity.onnx` was intentionally extensible as a
nested structure to absorb future fields without bumping
the top-level `casm_version`).
