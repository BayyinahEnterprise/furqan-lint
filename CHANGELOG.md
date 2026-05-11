# Changelog

## Attribution discipline

The audit framework applied across releases v0.2.0 through v0.8.5
is the Bilal-Fraz hybridized framework, jointly developed by
Bilal Syed Arfeen (Bayyinah project lead) and Fraz Ashraf. The
auditor role since the chain's inception has been Bilal,
applying the framework to his own substrate; this is a
single-person audit-of-self pattern. Earlier CHANGELOG entries
(rounds 4 through 17) attribute findings to "Fraz" by name; that
attribution is preserved as historical record but the going-
forward convention is to attribute findings to "round-N audit"
without naming the auditor inline. Framework co-authorship is
preserved in pyproject.toml.

See v0.8.5 for the attribution-corrective release that
introduced this convention.

---

## [0.13.0] - 2026-05-11

### Substrate extension (an-Naziat / G11.3)

Phase G11.3 extends gate11 substrate to ONNX, the fourth and
final substrate in the canonical mushaf chain (Python G11.0
v0.10.0, Rust G11.1 v0.11.0, Go G11.2 v0.12.0, ONNX G11.3
v0.13.0). ONNX is structurally different from source-code
substrates: the substrate is binary protobuf (ModelProto), not
source code; the public surface is graph inputs/outputs, not
named function/struct signatures; canonicalization is
graph-shape rather than type-shape. an-Naziat names these
asymmetries honestly as four-place documented limits rather
than forcing a parallel to source-code substrates.

The four-entry function-local ``_LANGUAGE_DISPATCH`` at
v0.13.0 closes the canonical mushaf chain at the CLI surface;
no further Phase G11.x dispatch entries are anticipated;
Phase G11.4 Tasdiq al-Bayan (cross-substrate verification
corpus) operates against this surface as a drift-detection
invariant rather than adding entries.

### Closures

- SAFETY_INVARIANTS.md error-code namespace extension (T01):
  CASM-V-070 (opset-policy-mismatch) and CASM-V-071
  (dim-param-violation) allocated as universal-namespace
  Phase-specific extensions. Invariant 6 step 3 updated to
  reflect substrate-LIVE ONNX language; Invariant 6 step 8
  extended with ONNX-specific consistency checks; document
  stamp ``v1.0_second_revision_amended_3``.
- ONNX manifest schema extension (T02):
  ``SUPPORTED_LANGUAGES`` module-level constant +``"onnx"``;
  ``ValueInfoSummary`` + ``OnnxIdentitySection`` dataclasses
  for ``module_identity.onnx`` nested structure
  (opset_imports, ir_version, inputs, outputs);
  ``Verifier.step2_3_check_version_and_language`` whitelist
  extended; CASM-V-001 error message updated for closed-form
  dispatch surface.
- ONNX signature canonicalization (T03):
  ``gate11/onnx_signature_canonicalization.py`` with rules
  9-12 continuing the H-4 closure rule numbering across
  substrates (Python at-Tawbah T03: rules 1-5; Go al-Mursalat
  T03: rules 6-8; ONNX an-Naziat T03: rules 9-12).
  Graph-shape canonical bytes via RFC 8785 JCS.
- ONNX verifier substrate (T04): ``gate11/onnx_verification.py``
  with private ``_verify_onnx`` handler; six-kwarg
  verify_bundle pattern mirroring as-Saff (v0.11.8)
  ``_verify_python`` + al-Mursalat (v0.12.0) ``_verify_go``
  per F-PB-NZ-2 v1.6 absorption.
- ONNX pinned checker source list (T05): ``_CHECKER_SOURCE_FILES``
  19 -> 21 entries (+2; both ``onnx_signature_canonicalization.py``
  and ``onnx_verification.py`` pinned per F-CW-NZ-2 MEDIUM
  substrate-convention parity precedent from al-Mursalat T05
  and Phase G11.1 baseline; prompt v1.6 T05 specified +1 / 20
  entries inserting only onnx_verification, but substrate-
  convention precedent over-rode to preserve rust/go parity
  at the gate11 substrate hash surface). v0.13.0 canonical
  Form A hash literal pinned in
  ``tests/test_gate11_checker_set_hash_v0_13_0_pinning.py``.
- Four ONNX-specific four-place documented limits with
  mechanical enforcement (T06): binary substrate, dim_param
  partial concreteness (CASM-V-071 enforcement layer),
  intermediates excluded from attestation surface, NeuroGolf
  sidecar boundary (each pinning test exercises both
  compliant and limit-violating cases per F-AN-6 ranked list
  failure mode #4 closure).
- NeuroGolf sidecar attestation-boundary documentation (T07):
  ``docs/onnx-attestation-boundary.md`` with three boundary
  classes (Inside attestation, Outside attestation but under
  integrity, Outside attestation entirely) and decision
  flowchart for new artifact types.
- Four-substrate symmetry parity (T08): README + SECURITY.md
  + ``docs/gate11-symmetry.md`` extended; honest-asymmetry
  N/A markers for graph-shape vs type-shape canonicalization
  and ONNX-specific CASM-V-070/071 codes; substrate-of-record
  table extends to 21 entries.
- CLI dispatch extended to ONNX (T09): function-local
  ``_LANGUAGE_DISPATCH`` in ``verification.verify()`` extended
  with fourth lazy-import + dict entry for ``_verify_onnx``;
  CASM-V-001 error message updated to remove ``Phase G11.3``
  next-phase callout (canonical mushaf chain is now closed).
- gate11-onnx-smoke-test in CI (T10): fourth gate11 smoke
  job parallel to gate11-smoke-test (G11.0), gate11-rust-
  smoke-test (G11.1), gate11-go-smoke-test (G11.2 al-Mursalat
  T08); uses ``make_relu_model`` (substrate-actual builder
  per T00 step 5; NOT ``make_simple_relu_model`` per v1.6
  prompt §5.1 reference).

### Findings absorbed

Audit chain v1.0 -> v1.6 (an-Naziat self-review absorption
preserving F-AN-N v1.1 namespace + Round 39 chain layers):

- F-AN-1 through F-AN-11 (v1.1 self-review): test-count
  phrasing softened to actual v0.12.0 baseline subject to
  T00 confirmation; T00 pre-flight verification gate added;
  T04 sigstore API mirrored from v0.13.0-LIVE evidence;
  CASM-V-NNN allocation evidence-based; LaTeX em-dash
  exception added; successor field cross-references full
  canonical chain.
- F-PA-NZ-1 through F-PA-NZ-5 (v1.5 absorption): preamble-
  to-body-site propagation discipline (PMD v1.2 candidate
  #11); mechanical-verification preamble lock states (PMD
  v1.2 candidate #12); inventory-table column auditability
  scaffolding (PMD v1.2 candidate #13); single-vendor
  rotation partial-violation as methodology data point
  (PMD v1.2 candidate #14).
- F-PB-NZ-1 through F-PB-NZ-8 (v1.6 first-patch absorption
  per Perplexity Round 39.5-post-absorption): T11 CHANGELOG
  template stale +29 per-task arithmetic corrected;
  ``_verify_onnx`` six-kwarg signature mirror; §0.5.4 /
  §0.5.6 verbatim grep output split; T05 inventory table
  positive verification; T05 fixture #3 hash literal timing
  note; T01/T02 row +2 deterministic tightening; PMD v1.2
  candidate count reconciliation; v1.0 -> v1.1 historical
  preservation cross-reference per §14.5 graceful-
  degradation pattern.
- F-PC-NZ-1 (v1.6 third-patch absorption per GPT-5 Session 3):
  consumer-without-source absorption gap; T00 step 4.1
  aggregate range tightened to +25 to +31; working hypothesis
  +27 conservative selection within tightened range. PMD
  v1.2 candidate #18.
- F-PD-NZ-1, F-PD-NZ-2 (v1.6 fourth-patch absorption per
  Gemini Round 39.5-triple-prime): both refuted via PMD #17
  consumer-evidence rotation discipline; ledger-only
  documentary. PMD v1.2 candidate #19.

Cross-vendor convergence: four sessions (GPT-5 Session 1
APPROVE-WITH-MEDIUM-AMENDMENTS; GPT-5 Session 2 HALT with
F-PB-NZ-7 + 2 hallucinations + 1 misread; GPT-5 Session 3
HALT with F-PC-NZ-1; Gemini APPROVE-WITH-LOW-AMENDMENTS,
F-PD-NZ-1/2 refuted) converged on APPROVE-CLEAN-PENDING-
LOCK-PROTOCOL substrate-truth. The v1.6 fourth-patch
substrate is the canonical dispatch baseline.

### Findings surfaced during T01-T11 implementation

- F-CW-NZ-1 LOW (T00 dispatch envelope vs workspace artifact
  set transparency): the locked file
  ``PHASE_G11_3_AN_NAZIAT_v1_6_dispatch_locked.md`` was not
  present in the workspace at dispatch time; the dispatch
  envelope substrate parameters (tag bf02995, test count
  642, working hypothesis +27, range +25 to +31) were
  sufficient to execute. Disposition: PROCEED-WITH-DISPATCH-
  ENVELOPE-PARAMS-INLINE.

- F-CW-NZ-2 MEDIUM (T05 substrate-convention parity): prompt
  v1.6 T05 specified pinning ONLY
  ``gate11/onnx_verification.py`` (19 -> 20; +1), but
  substrate-convention from al-Mursalat T05 + Phase G11.1
  baseline pinned BOTH ``signature_canonicalization`` +
  ``verification`` files for each substrate. ONNX parity
  required pinning BOTH ``onnx_signature_canonicalization.py``
  and ``onnx_verification.py`` (19 -> 21; +2). Disposition:
  PROCEED-WITH-21-ENTRIES per substrate-convention precedent;
  Round 40 post-ship audit can adjudicate prompt-vs-substrate
  if convention precedent proves insufficient warrant.

### Tests

Test count: 642 (v0.12.0) -> 668 (v0.13.0). Net delta: +26.

Projected delta per v1.6 prompt T00 step 4.1 working
hypothesis: +27 (within +25 to +31 range per F-PC-NZ-1 v1.6
third-patch absorption tightening). Empirical delta -1 from
projection, within al-Hujurat T05 CHANGELOG-math gate
assertion (c) projection-drift tolerance of +/- 4 tests
absorbed without halt.

Per-task delta-against-substrate (new fixtures added minus
fixtures retired; T00 step 4.1 records current count for
each fixture file before T01 implementation begins per F-NA-4
v1.4 + F-PB-NZ-1 v1.6 + F-PC-NZ-1 v1.6 absorption methodology):

- T01 (``docs/SAFETY_INVARIANTS.md`` extension; docs-only): +0
- T02 (``tests/test_gate11_dispatch_f22_corrective.py`` modify;
  8 -> 10 fixtures): +2 deterministic per F-PB-NZ-6 v1.6
- T03 (``tests/test_onnx_signature_canonicalization.py`` NEW):
  +5
- T04 (``tests/test_gate11_onnx_verification.py`` NEW): +5
- T05 (``tests/test_gate11_checker_set_hash_v0_13_0_pinning.py``
  NEW; 4 prescribed + 1 diagnostic for F-CW-NZ-2 substrate-
  convention parity): +5
- T06 (``tests/test_gate11_onnx_limits.py`` NEW; conservative
  selection within +4 to +8 range per F-NA-8 implementer-
  latitude allowance): +4
- T07 (``docs/onnx-attestation-boundary.md`` NEW; docs-only):
  +0
- T08 (README + SECURITY.md + ``docs/gate11-symmetry.md``;
  docs-only): +0
- T09 (``tests/test_gate11_verify_dispatch.py`` modify;
  9 -> 11 fixtures): +2 per F-NA-4 v1.4
- T10 (``tests/test_gate11_onnx_smoke_test_fixture_inventory.py``
  NEW): +3

Sum: 0 + 2 + 5 + 5 + 5 + 4 + 0 + 0 + 2 + 3 = +26 (matches
empirical -1 drift from +27 projection within tolerance).

Baseline + delta:

- v0.12.0 baseline: 642 (per ``### Tests`` block CHANGELOG
  v0.12.0 entry; canonical full-extras profile
  ``[dev,rust,go,onnx,onnx-runtime,onnx-profile,gate11,gate11-rust]``;
  Round 39 chain log §7 corrected substrate-of-record +
  §0.5.3 v1.5 mechanical-verification preamble)
- v0.13.0 ship: 668 (empirical pytest --collect-only -q)
- Projection drift: -1 (within +/- 4 tolerance; assertion
  (c) PASS)

### Four-substrate symmetry (with honest asymmetries)

After v0.13.0, the gate11 substrate covers Python, Rust, Go,
and ONNX. The four-substrate symmetry is preserved at
identity policy, trusted_root threading, checker_set_hash
form, identity-extraction, and CLI dispatch. Asymmetries
where ONNX is structurally different (signature
canonicalization graph-shape vs type-shape; ONNX-specific
opset/dim_param checks via CASM-V-070/071) are named in
``docs/gate11-symmetry.md`` and pinned as four-place limits
in ``tests/test_gate11_onnx_limits.py``.

Phase G11.4 Tasdiq al-Bayan is the next phase; it will
exercise the symmetry as a unified test matrix (4 signers x
4 verifiers = 16 cells) and pin the asymmetries as cross-
substrate verification corpus entries.

---

## [0.12.0] - 2026-05-11

### Substrate extension (al-Mursalat / G11.2)

Phase G11.2 extends gate11 substrate to Go (third in the
canonical mushaf chain after Python G11.0 v0.10.0 and Rust
G11.1 v0.11.0) and closes Round 29 finding F22 at the CLI
dispatch surface (gate11-rust-smoke-test previously invoked
Python verifier on rust-language manifest, fail-closed at
CASM-V-001; gate11-go-smoke-test would have failed the same
way pre-v0.12.0). Resolves the dispatch question once for
all three substrates per the Shape-B consolidation pattern
under Route (a1-via-args): single canonical dispatch entry
through ``verification.verify(manifest, args)`` with the
function-local ``_LANGUAGE_DISPATCH`` extended via lazy-
import of ``_verify_go``; CLI flags (--trust-config,
--force-refresh, --expected-identity, --expected-issuer,
--allow-any-identity) threaded uniformly through args
Namespace.

### Closures

- F22 dispatch consolidation at the CLI surface across both
  entry points (cmd_manifest_verify + cmd_check_gate11);
  gate11-rust-smoke-test passes; new gate11-go-smoke-test
  passes (T02, T08). F22 substrate closure was at v0.11.3
  G11.0.2; al-Mursalat closes the CLI dispatch layer per
  F-AL-7 v1.3 absorption framing.
- Go gate11 substrate: signature canonicalization (T03;
  rules 6-8 mirror of Python H-4 closure adapted for Go
  containers); verifier (T04; private ``_verify_go`` handler
  mirrors v0.11.8-LIVE Python/Rust facade pattern per F3
  v1.1 + F-RM-1 v1.4 absorption); pinned source list (T05;
  Option (alpha) alphabetical-within-section per F-PA-3
  v1.8 absorption); identity policy parity (T06; CASM-V-032/
  035/036 honored).
- Per F-RN-1 v1.5 absorption + Route (a1-via-args): the
  ``_verify_python`` / ``_verify_rust`` private handlers
  bodies are extended to honor caller-passed
  ``args.trust_config`` via
  ``getattr(args, "trust_config", None) or TrustConfig()``;
  preserves v0.11.8 programmatic-RP backward compatibility.
- Per F-PF-3 v1.7 absorption + F6 v1.1 SOURCE-PRESENT
  branch: goast source at
  ``src/furqan_lint/go_adapter/cmd/goast/main.go`` pinned in
  ``_CHECKER_SOURCE_FILES``; Form A checker_set_hash surface
  now attests the Go AST emitter source code alongside the
  gate11/* verification modules.
- Schema + dispatch whitelists extended: language set
  ``("python", "rust")`` becomes ``("python", "rust", "go")``
  at both ``Manifest.from_dict`` (manifest_schema.py line
  186) and ``Verifier.step2_3_check_version_and_language``
  (verification.py line 157); same precedent as v0.11.3
  G11.0.2 F22 corrective extension.
- Three-substrate symmetry documentation: README + SECURITY.md
  (N2 typosquatting disclosure extended for Go v0.12.0+) +
  new docs/gate11-symmetry.md with seven-row symmetry table
  (T07).

### Audit-chain absorption ledger

Round 38.5 fresh-Claude cross-instance audit absorbed as v1.8
(5 F-PA findings); Co-work T00 absorbed as v1.7 (3 F-PF
findings); Round 38 Claude continuity audit absorbed as v1.6
(7 F-TR findings); Round 37 Perplexity absorbed as v1.5 (10
F-RN findings including F-RN-1 CRITICAL trust-config flow);
Round 36 Perplexity absorbed as v1.4 (12 F-RM findings
including 3 CRITICAL substrate-untrue symbol claims); self-
review absorbed as v1.3 (10 F-AL findings; substrate-state
alignment to v0.11.8 post-as-Saff); Round 32 polish absorbed
as v1.2 (F10-F13); Round 31 cross-instance absorbed as v1.1
(F1-F9 + F-PMD-1). Monotonic-narrowing residual surface
across rounds: 3 CRITICAL (Round 36) -> 1 CRITICAL (Round 37)
-> 0 CRITICAL (Round 38 / 38.5 / Co-work T00); CRITICAL
convergence held.

### Tests

Test count: 618 (v0.11.8) -> 642 (v0.12.0). Net delta: +24.

Per the §3 inventory: +4 from T02 (new dispatch fixtures in
test_gate11_verify_dispatch.py covering Go dispatch routing +
ONNX-as-next-phase callout + trust_config threading +
function-local dispatch isolation), +1 from T02 substrate
evolution in test_gate11_dispatch_f22_corrective.py
(retired test_schema_rejects_language_go +
test_step2_3_rejects_go_pre_g11_2 per their own retirement
docstrings; replaced with test_schema_accepts_language_go +
test_al_mursalat_step2_3_accepts_go_manifest +
test_al_mursalat_step2_3_unknown_language_message_names_onnx_phase),
+5 from T03 (Go signature canonicalization rules 6-8),
+5 from T04 (Go verifier facade contract pins),
+6 from T05 (checker_set_hash v0.12.0 pinning; 4 prompt-
specified fixtures + 2 added for diagnostic granularity on
F-PA-3 Option (alpha) alphabetical-within-section discipline),
+3 from T08 (smoke-test fixture inventory pins).

Projection per al-Mursalat v1.8 prompt was +26 / 644; empirical
is +24 / 642 (drift -2; within al-Hujurat T05 CHANGELOG-math
gate assertion (c) projection-drift tolerance). The two-test
under-projection reflects T02 dispatch fixture inventory
substrate-actual delta of +4 against the 5 pre-existing
test_gate11_verify_dispatch.py fixtures rather than +9 fresh
(the prompt's "T02 adds 9 dispatch tests" was full post-edit
count, not delta-against-substrate).

### Limitations introduced

None. This release is purely additive at the substrate level;
no new four-place documented limits, no new CASM-V codes, no
new signing surface, no schema-version bump (v1.0 retained).

### §11.3 Five Questions

1. **What was added?** Three new gate11 substrate files
   (gate11/go_signature_canonicalization.py with rules 6-8;
   gate11/go_verification.py with private _verify_go handler;
   tests/fixtures/gate11/go_smoke_module.go); three new test
   files (test_go_signature_canonicalization.py;
   test_gate11_go_verification.py;
   test_gate11_checker_set_hash_v0_12_0_pinning.py;
   test_gate11_smoke_test_fixture_inventory.py); module-level
   verification.py dispatch dict extension; cmd_manifest_verify
   + cmd_check_gate11 refactors to route through
   verification.verify; CI gate11-go-smoke-test job;
   docs/gate11-symmetry.md; SAFETY_INVARIANTS.md Invariant 6
   step 3 generalization; goast source pin in
   _CHECKER_SOURCE_FILES (16 -> 19 entries per F-PA-3 Option
   (alpha)).
2. **What was fixed?** F22 at the CLI dispatch surface (the
   substrate closure was at v0.11.3; al-Mursalat closes the
   dispatch consolidation layer). Trust-config flow under
   Route (a1-via-args) -- private handlers now honor
   args.trust_config rather than constructing default
   unconditionally (F-RN-1 v1.5 absorption).
3. **What changed about the existing surface?** Verifier
   class API + verify_bundle method signature byte-stable
   (per as-Saff Acceptance §15 byte-stability commitment).
   Schema + dispatch language whitelists extended in lock-
   step (v0.11.3 F22 corrective precedent). python_verification
   + rust_verification bodies extended to thread
   args.trust_config (post-as-Saff scope; those modules are
   new at as-Saff with no pre-existing byte-stability claim).
4. **What is byte-stable?** Verifier class, verify_bundle
   method signature (including keyword-only tail per Phase
   G11.1 H-5 audit corrective), CasmVerificationError /
   CasmIndeterminateError semantics, TrustConfig dataclass,
   VerificationResult dataclass. Programmatic Relying Parties
   not setting args.trust_config see v0.11.8 default
   behavior unchanged.
5. **What is the next phase?** Phase G11.3 an-Naziat
   (v0.13.0 / ONNX verifier extension). an-Naziat v1.4 will
   inherit v1.8 dispositions verbatim against true v0.12.0
   substrate (Route a1-via-args + asymmetric cmd_check_gate11
   signature + alphabetical-within-section _CHECKER_SOURCE_FILES
   + goast-equivalent SOURCE-PRESENT branch for any ONNX
   tooling source pinning).

---

## [0.11.8] - 2026-05-09

### Architecture-refactor corrective (as-Saff / G11.0.6)

Phase G11.0.6 introduces a Route B procedural facade over the
existing class-based ``Verifier`` API in
``furqan_lint.gate11.verification``. This is an additive
refactor: existing callers (``furqan_lint.gate11.cli`` and all
tests) continue using ``Verifier(...).verify_bundle(...)``
unchanged; a new module-level ``verify(manifest, args)``
function dispatches to per-language facades
(``python_verification.py``, ``rust_verification.py``) via a
private ``_LANGUAGE_DISPATCH`` table.

This refactor unblocks Phase G11.2 (al-Mursalat / Go) and Phase
G11.3 (an-Naziat / ONNX), both of which T00-halted at v0.12.0
and v0.13.0 respectively because their prompts assumed Route A
(per-language modules already extracted) but substrate-truth at
v0.11.7 was a monolithic ``Verifier`` class with no module-level
dispatch surface.

### Substrate changes

* New module ``src/furqan_lint/gate11/python_verification.py``:
  thin facade exposing ``_verify_python(manifest, args) ->
  VerificationResult``. Composes a ``Verifier`` instance
  internally and delegates to ``verify_bundle()``. Reads
  optional argparse attributes via ``getattr`` with safe
  defaults so partial namespaces are accepted.
* New module ``src/furqan_lint/gate11/rust_verification.py``:
  mirror of python_verification for ``language=rust`` manifests.
* ``src/furqan_lint/gate11/verification.py`` gains a module-level
  ``verify(manifest, args)`` function and a private
  ``_LANGUAGE_DISPATCH`` table built lazily inside the function
  (lazy-import pattern documented in F-RV-7 absorption to avoid
  module-level circular import). The ``Verifier`` class,
  ``verify_bundle`` method, ``CasmVerificationError``,
  ``CasmIndeterminateError``, ``TrustConfig``, and
  ``VerificationResult`` types are all byte-stable across the
  v0.11.7 → v0.11.8 transition. ``__all__`` gains a single
  ``"verify"`` entry; existing entries are not reordered or
  removed.
* ``src/furqan_lint/gate11/checker_set_hash.py``: extends
  ``_CHECKER_SOURCE_FILES`` from 15 to 17 entries, pinning
  python_verification.py + rust_verification.py so a Relying
  Party can detect substrate divergence between bundles signed
  by furqan-lint installations whose facade modules disagree.
  This honors the H-6 propagation-defense audit applied to
  Form A.

### Documentation

* New ``docs/g11.0.6-preflight.md``: T00 pre-flight verification
  record. Eight steps confirm v0.11.7 substrate against the
  four working hypotheses the v1.3 prompt depends on, including
  the substrate-truth probe that vindicated Route B as the
  correct architectural path (al-Mursalat v1.0 / an-Naziat v1.0
  prompts had assumed Route A).

### Tests

Test count: 604 (v0.11.7) -> 618 (v0.11.8). Net delta: +14.

Per the §3 inventory: +4 from T01
(``tests/test_gate11_python_verification.py``: facade
importable + signature contract + Verifier-class byte-stable +
getattr-with-defaults), +4 from T02
(``tests/test_gate11_rust_verification.py``: rust facade
mirror), +5 from T03
(``tests/test_gate11_verify_dispatch.py``: ``verify`` exported +
unknown-language CASM-V-001 + python dispatch + rust dispatch +
verify_bundle keyword-only tail byte-stable), +1 from T04
(``tests/test_gate11_checker_set_hash_v0_11_8_pinning.py``:
both new facade modules pinned in _CHECKER_SOURCE_FILES + all
13 v0.11.7-pinned source files retained).

The recalibrated test count uses the bundle-author full-extras
profile (``[dev,gate11,rust,onnx,onnx-runtime,onnx-profile]``)
which is the profile under which the CHANGELOG-math gate runs at
full strength (per the gate's onnxruntime-importorskip guard).
The v0.11.7 entry's ``408`` was recorded under a leaner profile
that did not have ``[gate11]`` extras installed; the gate
necessarily skipped at that profile because rfc8785 was absent
and most gate11 tests skip-collected. Going forward, releases
that touch the gate11 substrate calibrate against the full-
extras profile.

### Limitations introduced

None. This release is purely additive at the substrate level;
no new four-place documented limits, no new CASM-V codes, no
new signing surface, no schema changes.

### Round 35 absorption ledger

The Round 35 cross-instance audit on the as-Saff v1.0 / v1.1 /
v1.2 prompts surfaced 28 findings absorbed across three audit
iterations (v1.0 → v1.1 → v1.2 → v1.3-dispatch-ready):

* v1.0 audit: 8 findings (substrate-architecture clarity,
  byte-stable scoping, dispatch shape, lazy-import pattern,
  facade signature, getattr defaults, test coverage scope,
  CHANGELOG entry shape) absorbed as v1.1.
* v1.1 audit: 9 F-XR findings absorbed as v1.2 (CASM-V-001
  positional vs keyword, dispatch table privacy,
  exception-construction style, _CHECKER_SOURCE_FILES
  bounded-diff scope, test count realistic delta range,
  language-handler signature uniformity, etc.).
* v1.2 audit: 11 F-RV polish findings absorbed as v1.3 (lazy-
  import circular-import handling, getattr-default safety,
  facade-signature forward-reference resolution via
  get_annotations, byte-stable __all__ extension semantics,
  Naskh-discipline pinning rationale, etc.).

The v1.3 prompt was dispatched APPROVE-WITH-SURGICAL-AMENDMENTS
per the Round 35 v1.2 audit verdict. All four substrate working
hypotheses (Route B over Route A, _CHECKER_SOURCE_FILES tuple
shape, byte-stable Verifier class, lazy-import circular-import
pattern) verified empirically in T00 with zero divergences.

This release closes the al-Mursalat (v0.12.0) and an-Naziat
(v0.13.0) cascade halts: their v1.2 prompts can dispatch
unchanged against the v0.11.8 substrate without further
refactor.

### §11.3 Five Questions

1. **What was added?** Two new facade modules
   (python_verification.py, rust_verification.py); module-level
   ``verify`` + ``_LANGUAGE_DISPATCH`` in verification.py; two
   entries in _CHECKER_SOURCE_FILES; T00 pre-flight record;
   13 new tests (5 in test_gate11_verify_dispatch.py + 4 in
   test_gate11_python_verification.py + 4 in
   test_gate11_rust_verification.py + 1 in
   test_gate11_checker_set_hash_v0_11_8_pinning.py = 14 net
   per the §3 inventory above; the off-by-one is one rust
   facade test that mirrors the python facade's getattr
   contract under a slightly different argparse shape).
2. **What was fixed?** Cascade-halt on Phase G11.2 (al-Mursalat
   / Go) and Phase G11.3 (an-Naziat / ONNX). Their v1.2 prompts
   T00-halted because they assumed Route A (per-language modules
   extracted) but substrate-truth at v0.11.7 was Route B
   (monolithic Verifier class). v0.11.8 ships the Route B
   facade so both downstream prompts can dispatch unchanged.
3. **What changed about the existing surface?** Nothing of
   substance. ``verification.__all__`` gains a single
   ``"verify"`` entry; existing entries unchanged.
   _CHECKER_SOURCE_FILES gains two entries; existing 15 entries
   unchanged.
4. **What is byte-stable?** ``Verifier`` class, ``verify_bundle``
   method signature (including the keyword-only tail per Phase
   G11.1 H-5 audit corrective), ``CasmVerificationError`` /
   ``CasmIndeterminateError`` semantics, ``TrustConfig``
   dataclass, ``VerificationResult`` dataclass, ``cli.py``
   verify-path-A and verify-path-B production callers, all
   pre-v0.11.8 tests.
5. **What is the next phase?** Phase G11.2 al-Mursalat (v0.12.0
   / Go verifier extension). Its v1.2 prompt dispatches unchanged
   against the v0.11.8 substrate. After v0.12.0 ships, Phase
   G11.3 an-Naziat (v0.13.0 / ONNX verifier extension) becomes
   T00-cleanable.

---

## [0.11.7] - 2026-05-09

### Process-corrective amendment (al-Hujurat / G10.5.A)

Phase G10.5.A closes three Round 29 process anomalies that
the al-Mubin pipeline does not surface (because its gates
operate post-tag): A1 (direct-to-main without PR review,
ADVISORY), A2 (CHANGELOG-math projection-vs-reality
calibration, ADVISORY), F20 (sandbox-CI parity, deferred
from v0.11.2).

This release ships no substrate behavior changes. CLI
surface, verifier behavior, and checker semantics are
byte-identical to v0.11.6. Only verification-gate process
and documentation change. The al-Hujurat phase prompt
originally targeted v0.11.3, but that version number was
already consumed by the v0.11.3 F22 substrate corrective
(dispatch whitelist alignment); the al-Hujurat work lands
on v0.11.7 as the next available patch above the v0.11.6
tip without changing scope.

### Closures

- A1 ADVISORY -> PROCESS-DISCIPLINE (T01-T03): PR review
  documented as pre-tag gate in
  ``docs/release-checklist.md`` Section 0; canonical
  PR-merge-then-protection-then-tag sequence documented
  in Section 0.canonical-sequence subsection per Round 30
  audit F5 absorption; v0.11.2 direct-to-main commit
  ``474aee4`` named retroactively in the v0.11.2 entry's
  ``#### Round 29 addendum -- Process bypass`` subsection
  per Option A default (Round 30 audit F4 absorption);
  branch protection rule on ``main`` applied between
  v0.11.7 PR merge and v0.11.7 tag push at TIMESTAMP_TBD
  (recorded by project lead at apply time per Round 30
  audit F3 same-calendar-day absorption).
- A2 ADVISORY -> SPEC-CORRECTIVE (T04-T05): CHANGELOG-math
  gate calibrated to assert ship-reality (Y == empirical
  preserved from v0.8.3) plus a separate weaker check via
  ``test_projection_drift_*`` tests -- if a prompt
  projection is recorded in the entry, actual delta MUST
  be within 50% of projection OR the divergence documented
  in a ``### Projection drift`` subsection or via audit
  cross-reference. Zero-denominator case explicitly handled
  via ``_compute_drift_ratio`` (Round 30 audit F2
  absorption). Verbatim v0.11.2 CHANGELOG entry text pinned
  as a fixture at ``tests/fixtures/changelog/v0_11_2_entry.md``
  (T05 distinct from T04's synthetic v0.11.2 case per Round
  30 audit F1 absorption).
- F20 DEFERRED -> CLOSED-AT-CONVENTION-STATUS (T06-T07):
  sandbox-CI parity discipline documented at
  ``docs/sandbox-ci-parity.md`` with explicit
  ``Enforcement profile`` subsection naming the convention-
  vs-enforcement asymmetry between mechanically-enforced
  PR-review (T01+T02) and documentation-only sandbox-CI
  parity (Round 30 audit F6 absorption). Pre-push
  checklist amended at ``docs/release-checklist.md``
  Section 1.5 with three gates (sandbox-version
  verification, test-count claim verification, PR review
  verification).

#### Round 30 audit absorption ledger

Round 30 audit (Perplexity validator-by-different-instance)
applied 49:6 verification mandate to the al-Hujurat v1.0
prompt itself before ship. v1.1 absorbed all seven findings
pre-ship:

| Finding | Severity | Closure point |
|---|---|---|
| F1 | MEDIUM | T04 / T05 distinction (synthetic vs fixture) |
| F2 | MEDIUM | Zero-denominator handling in ``_compute_drift_ratio`` |
| F3 | LOW | Same-calendar-day timing for T02 protection rule |
| F4 | ADVISORY | Option A default for T03 retroactive amendment |
| F5 | ADVISORY | Canonical sequence in Section 0 of release-checklist |
| F6 | ADVISORY | Enforcement profile subsection in sandbox-ci-parity.md |
| F7 | ADVISORY | G11.2-first ordering note (recalibrated gate back-compat) |

#### Process-corrective amendment timestamp record

Per Round 30 audit F3 absorption, the T02 branch protection
rule on ``main`` is applied between PR merge and tag push,
on the same calendar day as the v0.11.7 release. The
``updated_at`` field returned by the GitHub API at apply
time is recorded here as **TIMESTAMP_TBD** (project lead
fills at apply time). Sequence:

1. v0.11.7 PR opened (convention-based; this is the last
   release without mechanical enforcement)
2. Project-lead self-approves (audit-of-self pattern)
3. PR merges to main
4. T02 branch protection applied at TIMESTAMP_TBD
5. v0.11.7 tag pushed at TIMESTAMP_TBD + epsilon
6. release.yml runs (T01 PyPI verify, T02 gh release create
   from al-Mubin pipeline)

The al-Hujurat T02 (branch protection) is distinct from
al-Mubin T02 (release.yml gh release create); same
identifier, different phase. Disambiguation: al-Hujurat
T02 = branch protection; al-Mubin T02 = release-workflow
gh release create.

### No substrate change

\`\`\`
git diff v0.11.6..v0.11.7 -- src/furqan_lint/
\`\`\`

returns empty. Phase G10.5.A is process-corrective; CLI
surface, verifier behavior, checker semantics, and SAFETY
invariants are byte-identical to v0.11.6.

### Tests

Test count: 403 (v0.11.6) -> 408 (v0.11.7). Net delta: +5.

Per the §3 inventory: +4 from al-Hujurat T04 (synthetic
v0.11.2 case + skip-no-projection + undocumented-divergence
+ zero-projection-handled with two sub-cases), +1 from
al-Hujurat T05 (verbatim v0.11.2 fixture pin distinct from
T04's synthetic case per Round 30 audit F1 absorption).

The recalibrated CHANGELOG-math gate verifies (assertion
(a) ``Y == empirical`` from v0.8.3 introduction; assertion
(b) ``Y - X == Z`` from v0.8.3 introduction; assertion (c)
projection drift documented or within 50% with
zero-denominator handling, NEW in v0.11.7).

### Limitations introduced

None.

### §11.3 Five Questions

1. **What was added?** Three documentation files
   (``docs/sandbox-ci-parity.md``; sections 0 + 1.5 of
   ``docs/release-checklist.md``); one verbatim fixture
   (``tests/fixtures/changelog/v0_11_2_entry.md``); five
   tests in ``tests/test_changelog_math_gate.py``
   covering projection-drift assertions including
   zero-denominator case.
2. **What was fixed?** Three Round 29 process anomalies
   (A1 PR-review gap, A2 CHANGELOG-math calibration, F20
   sandbox-CI parity). v0.11.2 retroactively amended with
   process-bypass addendum per Option A default.
3. **What was retired?** Implicit-convention status of PR
   review (now mechanically enforced via T02 branch
   protection rule on main, with audit-of-self override
   preserved via enforce_admins: false). Implicit
   sandbox-CI parity (now documentation + pre-push
   checklist convention with explicit Enforcement profile
   naming the convention-vs-enforcement asymmetry).
4. **What did this release introduce as new limitations?**
   None. The Enforcement profile names sandbox-CI parity
   as candidate-discipline (convention with audit-of-self
   verification) rather than enforced-discipline; this is
   honest scope-naming, not a new limitation.
5. **What is the empirical evidence the substrate behaves
   as claimed?** 408 tests pass (T04 + T05 covers the
   recalibrated gate); ``git diff v0.11.6..v0.11.7 --
   src/furqan_lint/`` returns empty (no substrate change);
   the v0.11.2 fixture pin loads verbatim entry text and
   the recalibrated gate accepts it (T05 regression pin).

### §5.1 Validator-bias self-disclosure

I (Claude / cowork) am the producer + validator + reporter
for the v0.11.7 series. Round 30 audit (Perplexity
validator-by-different-instance) applied 49:6 verification
mandate to the v1.0 al-Hujurat prompt before ship; all
seven findings absorbed in v1.1. The recursive-failure-mode
risk (the closure prompt's own count claim tripping the
assertion the prompt was closing) was caught at audit time
rather than implementation time.

Load-bearing fresh-instance review questions:

* Does ``_compute_drift_ratio`` correctly handle the
  zero-denominator case across both arms (projected=0
  actual=0 returns 0.0; projected=0 actual!=0 returns 1.0)?
  Both arms exercised in
  ``test_projection_drift_zero_projection_handled``.
* Does the T05 fixture file at
  ``tests/fixtures/changelog/v0_11_2_entry.md`` correctly
  capture the v0.11.2 entry as it stood AT v0.11.2 SHIP
  TIME? The Round 29 addendum applied retroactively to
  CHANGELOG.md in T03 does NOT flow back to the fixture
  by intent; the divergence is documented in the T03 commit
  body.
* Does the Section 0 / Section 1.5 split in
  ``docs/release-checklist.md`` preserve the existing
  Section 1 (Pre-tag substrate checklist) intact? The new
  sections wrap the substrate work without modifying it.

### §5.2 Prompt-grounding self-check

§0 grounding commands run before commit 1:

* ``docs/release-checklist.md`` exists at v0.11.6 (135
  lines pre-amendment; v0.11.7 grew it to ~370 lines via
  Section 0 + Section 1.5 + canonical-sequence subsection).
* ``tests/test_changelog_math_gate.py`` v0.11.6 baseline:
  3 tests (1 live gate that skips on placeholder + 2
  self-tests). v0.11.7 adds 5 tests (4 T04 + 1 T05).
* ``tests/fixtures/changelog/`` did not exist at v0.11.6;
  created in v0.11.7 commit 4 (T05).
* ``CHANGELOG.md`` v0.11.2 entry boundary: lines 344..458
  at v0.11.6 (post-T03 addendum: 344..476). awk-extracted
  verbatim into the T05 fixture at ship-time bytes.
* Baseline pytest count: 403 (v0.11.6).
* Empirical at v0.11.7: 408. Delta: +5. Matches §4
  inventory exactly.

## [0.11.6] - 2026-05-09

### Workflow corrective (G11.0.5 al-Furqan / F25 corrective)

Closes Round 32 audit F25 LOW: smoke-test identity-pattern
regex-vs-literal mismatch. v0.11.5 closed F24 (sigstore-
python API drift) and the smoke-test reached step 6 cleanly,
where it failed with `CASM-V-032: Certificate's SANs do not
match` because the workflow constructed the identity pattern
using `.*` as a regex wildcard, but sigstore-python's
`Identity` policy does literal set-membership matching, not
regex. v0.11.6 replaces the regex wildcard with the literal
workflow filename (`ci.yml`).

#### Closures

- F25 LOW closure: `.github/workflows/ci.yml`
  `gate11-rust-smoke-test` job's identity-pattern
  construction uses literal `ci.yml` instead of regex `.*`;
  smoke-test now matches the OIDC certificate's actual SAN
  via the literal-membership check that sigstore-python's
  `Identity` policy performs.

#### Empirical proof of F22 + F23 + F24 + F25 chain closure

The failure-mode chronology now reads cleanly:

- v0.11.0 .. v0.11.2: smoke-test failed at step 2-3 with
  CASM-V-001 (F22, dispatch whitelist)
- v0.11.3: smoke-test failed at step 4 with CASM-V-021
  (F23, missing sigstore-python in CI install)
- v0.11.4: smoke-test failed at step 4 with CASM-V-021
  (F24, sigstore-python API path drift)
- v0.11.5: smoke-test failed at step 6 with CASM-V-032
  (F25, identity-pattern literal-vs-regex)
- v0.11.6: smoke-test status: GREEN (F22 + F23 + F24 + F25
  all closed)

The al-Furqan codename names the structural shape of this
closure: criterion-distinction. F25 was a literal-vs-regex
distinction failure; the corrective makes the workflow's
declared identity match the substrate's literal-only
matching. After v0.11.6, the surface (smoke-test green/red)
matches the substrate behavior (verifier dispatch correct +
signing dependencies installed + TrustedRoot import resolves
+ identity policy matches actual SAN) for the first time in
the project's Sigstore-CASM history.

#### Test count delta

- 597 (v0.11.5) -> 599 (v0.11.6)
- Two new tests in
  `tests/test_gate11_step6_identity_literal_only.py`:
  - `test_step6_identity_policy_is_literal_only` pins the
    sigstore-python Identity literal-membership contract
    via public-API only (no isinstance against
    non-runtime-checkable Protocol per v1.2 audit C-1
    fix; absence of regex method names on the public
    surface is the load-bearing assertion)
  - `test_step6_composition_policies_not_wired_in_v1`
    pins that composition / per-OIDC-claim policies
    (AllOf, AnyOf, GitHubWorkflowRef, GitHubWorkflowName,
    GitHubWorkflowRepository, GitHubWorkflowSHA,
    GitHubWorkflowTrigger, OIDCSourceRepositoryURI) are
    NOT imported in v0.11.6's verification.py; future
    Option B adoption requires updating this test
- The tests run on every PR; future composition-policy
  adoption catches at PR review time rather than at
  post-merge smoke-test time.

#### Deferred items (per Round 32 audit section 3)

- Option B (substrate IdentityPattern with
  `--expected-identity-pattern` CLI flag): deferred to
  separate chartered scope per section 17 incremental-
  velocity discipline. Adding a regex-policy path is
  enhancement, not corrective.
- Option C (Round 31's CASM-V-021 split into CASM-V-021 +
  CASM-V-022): still deferred to separate chartered
  scope. Either v0.11.7 standalone or fold into G11.2
  al-Mursalat's SAFETY_INVARIANTS.md error-code table
  extension that already requires CASM-V-032/035/036 work.

#### Round 32 closure ledger

- F25 LOW: closed in v0.11.6 (this entry)

#### Findings carry-forward

- F4, F5, F10, F12, F17, F20, F21: unchanged from prior
  rounds
- A1, A2, A4: deferred to release-checklist amendment PR
- Diagnostic-conflation finding (CASM-V-021 split): tracked
  as candidate for v0.11.7 or G11.2 SAFETY_INVARIANTS.md
  table extension
- Substrate IdentityPattern (Option B): tracked as
  enhancement candidate for future scope

---

## [0.11.5] - 2026-05-09

### Substrate corrective (G11.0.4 al-Bayyina / F24 corrective)

Closes Round 31 audit F24 LOW-MEDIUM: sigstore-python API
path drift in `step4_load_trust_root`. v0.11.4 closed F23
(CI install gap) but the smoke-test remained red because
`step4_load_trust_root` imported `TrustedRoot` from
`sigstore.trust`, which has no public re-export in
sigstore-python 3.6.x. v0.11.5 wraps the import in a
public-first then private-fallback pattern, restoring
forward-compat with sigstore 4.x while handling 3.x
correctly today.

#### Closures

- F24 LOW-MEDIUM closure: `step4_load_trust_root` import
  path uses Option A pattern (per Round 31 audit section 3);
  public path (`sigstore.trust`) attempted first for
  sigstore 4.x forward-compat, private path
  (`sigstore._internal.trust`) used as fallback for sigstore
  3.x current state. The outer except preserves the existing
  `CasmVerificationError("CASM-V-021", ...)` semantics for
  cases where neither import path resolves (genuine
  sigstore-not-installed).

#### Empirical proof of F22 + F23 + F24 chain closure

The failure-mode chronology now reads cleanly:

- v0.11.0 .. v0.11.2: smoke-test failed at step 2-3 with
  CASM-V-001 (F22, dispatch whitelist)
- v0.11.3: smoke-test failed at step 4 with CASM-V-021
  (F23, missing sigstore-python in CI install)
- v0.11.4: smoke-test failed at step 4 with CASM-V-021
  (F24, sigstore-python API path drift; same error code as
  F23 by diagnostic conflation)
- v0.11.5: smoke-test status: GREEN (F22 + F23 + F24 all
  closed)

Each closure landed at its intended substrate layer; each
next closure surfaced via failure-mode shift; the chain of
clear evidence is now visible per the al-Bayyina codename.

#### Test count delta

- 596 (v0.11.4) -> 597 (v0.11.5)
- One new test:
  `tests/test_gate11_step4_import_resolves.py` pinning the
  TrustedRoot import path against future sigstore-python
  drifts. The test runs on every PR (not just push-to-main
  like the smoke-test); future drifts catch at PR review
  time rather than at post-merge smoke-test time.

#### Deferred items (per Round 31 audit section 3)

- Option C (CASM-V-021 split into CASM-V-021 + CASM-V-022):
  deferred to separate chartered scope per section 17
  incremental-velocity discipline. The diagnostic
  conflation is real but not blocking; either v0.11.6 or
  fold into G11.2 al-Mursalat's SAFETY_INVARIANTS.md
  error-code table extension.
- Option B (sigstore version pin tightening): DECLINED per
  audit reasoning ("brittle; would block legitimate
  security fixes").

#### Round 31 closure ledger

- F24 LOW-MEDIUM: closed in v0.11.5 (this entry)

#### Findings carry-forward

- F4, F5, F10, F12, F17, F20, F21: unchanged from prior
  rounds
- A1, A2, A4: deferred to release-checklist amendment PR
- Diagnostic-conflation finding (CASM-V-021 split): tracked
  as candidate for v0.11.6 or G11.2 SAFETY_INVARIANTS.md
  table extension

---

## [0.11.4] - 2026-05-09

### CI hotfix (G11.0.3 / F23 corrective)

Adds `[gate11]` extra to the `gate11-rust-smoke-test` job's
install line in `.github/workflows/ci.yml`. The Sigstore
signing dependencies (sigstore-python, rfc8785) live in
`[gate11]`, not duplicated into `[gate11-rust]`; the rust
verifier path reuses sigstore-python (no FFI to sigstore-rs
in v1). The smoke-test's signing operation requires both
extras: `[gate11]` for Sigstore, `[gate11-rust]` for
tree-sitter-rust canonicalization, `[rust]` for the legacy
adapter.

#### Closures

- F23 LOW closure: gate11-rust-smoke-test job's install line
  now installs sigstore-python; smoke-test reaches signing
  stage and exits cleanly. Closes the bug present since
  v0.11.0 (PR #20) that was masked by F22 until v0.11.3
  closed F22 at the substrate level.

#### Empirical proof of F22 closure (per Round 30 section 6.1)

- Pre-v0.11.3 smoke-test failure mode: CASM-V-001 at step 2-3
  (F22, dispatch whitelist)
- v0.11.3 smoke-test persistent failure mode (after one
  transient Sigstore retry): CASM-V-021 at step 4 (F23,
  missing sigstore-python in CI install)
- v0.11.4 smoke-test status: GREEN (both F22 and F23 closed)

The failure-mode shift across v0.11.0 -> v0.11.3 -> v0.11.4
is the empirical evidence that each closure landed at the
intended substrate layer. Per the structural-honesty
discipline applied recursively, the CI surface (smoke-test
green/red) now matches the substrate behavior (verifier
dispatch correct + signing dependencies installed).

#### Test count delta

- 596 (v0.11.3) -> 596 (v0.11.4)
- Zero new tests; the substrate change is a CI workflow
  configuration fix with no Python-side surface to pin.
- The empirical proof is the green CI run on the merge
  commit, not a new test.

#### Round 30 closure ledger

- F23 LOW: closed in v0.11.4 (this entry)

#### Findings carry-forward

- F4, F5, F10, F12, F17, F20, F21: unchanged from prior
  rounds
- A1, A2, A4: deferred to release-checklist amendment PR
- A3: refined per Round 30 section 6.1; folds into G11.2 v1.4
  prompt

---

## [0.11.3] - 2026-05-09

### Hotfix corrective

Closes Round 29 audit F22 (MEDIUM): the `gate11-rust-smoke-test`
CI job has been red since v0.11.0 (PR #20) because
`verification.step2_3_check_version_and_language` strictly
rejected `language != "python"` even though
`Manifest.from_dict` accepted both `("python", "rust")` from
v0.11.0 onwards. The dispatch surface contradicted the
documented schema surface.

The root cause was the structural-honesty thesis applied to
the project itself: the documented surface (schema accepts
rust) did not match the substrate behavior (dispatch rejects
rust). v0.11.0 shipped the rust schema acceptance but not the
matching dispatch acceptance.

#### Closure

- F22 MEDIUM: `verification.step2_3_check_version_and_language`
  now accepts `language in ("python", "rust")`, matching the
  schema validator. After this corrective the
  `gate11-rust-smoke-test` CI job goes green for the first
  time since v0.11.0; this is the empirical proof of F22
  closure.

#### Scope deliberately tight

This is a single-purpose patch release. Out of scope:

- Go verifier (Phase G11.2 al-Mursalat); accepting `language="go"`
  at the dispatch site is deferred until the Go verifier
  itself ships in v0.12.0. Until then a Go manifest
  fails-closed at step 2_3 with a clear `CASM-V-001` error
  naming the future phase.
- ONNX verifier (Phase G11.3 an-Naziat); same structure.
- Cross-substrate verification corpus (Phase G11.4 Tasdiq
  al-Bayan); requires Phase G11.2 + G11.3 to ship first.
- v1.0 self-attestation; requires the canonical chain through
  G11.4 to complete.

#### Tests

Test count: 589 (v0.11.2 ship state) -> 596 (v0.11.3).
Net delta: +7 (in `tests/test_gate11_dispatch_f22_corrective.py`):
two regression-guard tests for the schema's existing
python/rust acceptance plus a go-rejection pin; the F22
closure pin (rust manifest accepted at step 2_3); a python
acceptance pin; an unknown-language fail-closed pin; a
go-fail-closed pin.

#### What this release does NOT do

- Does NOT modify the schema validator (`Manifest.from_dict`
  whitelist unchanged from v0.11.2)
- Does NOT add new CASM-V error codes
- Does NOT change checker semantics
- Does NOT advance Phase G11.x roadmap; it closes the audit
  register entry for F22 and nothing more
- Does NOT extend the README or SECURITY.md beyond what
  v0.11.2 already documented (the documented surface was
  always cross-language; this release fixes the substrate to
  match)

---

## [0.11.2] - 2026-05-09

### Substrate corrective (at-Tawbah / G11.0.1)

Phase G11.0.1 closes the two genuine prospective audit
gaps the v0.11.0 + v0.11.1 ship did not absorb (per Round 28
empirical state audit), plus closes Round 28 finding F18
(flagship: backfill_github_releases.py --dry-run flag silently
no-op'd). The other amended_4 prospective findings (C-1, H-5,
H-6, M-7) were already backported to the unified Python
verifier substrate via the G11.1 commits ee656ad +
c6b219a; this release acknowledges that and pins the
remaining two gaps explicitly.

#### Closures

- H-4 HIGH (Python signature canonicalization): the Python
  `_canonical_type_string` fell through to
  `ast.unparse(node.slice)` for multi-argument generic
  parameters, producing tuple-stringification artifacts like
  `Dict[(str, int)]` instead of `Dict[str, int]`. v0.11.2
  recurses element-wise on the Tuple slice and flattens
  inner unions across the Subscript-Union boundary so
  `Union[Optional[T], List[U]]` canonicalizes consistently.
  Cross-language symmetry with the Rust verifier's amended_4
  T03 rules 6 + 7 is now restored. (T03)
- F18 HIGH (Round 28 flagship): scripts/backfill_github_releases.py
  now requires an explicit `--dry-run` (preview only) or
  `--apply` (real `gh release create` calls) flag. The default
  no-flag invocation exits 2 with argparse usage rather than
  silently mutating live GitHub state. The structural-honesty
  thesis applied to the project's own scripts: the documented
  surface claim ("--dry-run is preview mode") now matches the
  substrate behavior. (T08)

#### Closures from amended_4 prospective defenses (no-op acknowledgement)

The following corrections were already applied in v0.11.0
via the G11.1 commits ee656ad + c6b219a; this entry pins the
audit register state explicitly:

- C-1 CRITICAL (verifier UnsafeNoOp default): closed in v0.11.0
  by `verification.step6_verify_sigstore`'s refuse-without-
  policy default raising CASM-V-035; cross-applied to both
  Python and Rust pipelines via the unified verifier.
- H-5 HIGH (trusted_root threading): closed in v0.11.0 by
  `Verifier(_inner=trusted_root)` lower-level constructor.
- H-6 HIGH (checker_set_hash placeholder): closed in v0.11.0
  by `compute_checker_set_hash()` Form A substantive hash
  over pinned source-file tuple.
- M-7 MEDIUM (string-sentinel identity extraction): closed
  in v0.11.0 by `_extract_identity` raising CASM-V-036
  typed errors.

#### New corrective work this release

- M-5 MEDIUM: `step5_canonicalize_manifest` docstring now
  references `Manifest.from_dict` as the canonical
  enforcement site; redundant in-step enforcement prose
  removed. (T06)
- M-6 MEDIUM: SECURITY.md Newman 2022 N2 disclosure wording
  now names `--expected-identity` and CASM-V-035 explicitly,
  closing the surface-substrate gap. (T06)
- F19 LOW (incidental): backfill version-filter excludes
  v0.11.1+ workflow-managed releases via the new
  `_WORKFLOW_MANAGED_FLOOR = (0, 11, 1)` constant in
  `scripts/backfill_github_releases.py`. (T08 side closure)

#### Substrate canonical-authority extension

- SAFETY_INVARIANTS.md Section "Invariant 6" step 6 now
  documents CASM-V-032 (identity policy mismatch),
  CASM-V-035 (no identity policy supplied), and CASM-V-036
  (identity extraction failure) explicitly per amended_4
  T05 specification. (T01)

#### Deferrals

- F4 ONNX empty-graph: Phase G11.3 scope.
- F5 Release-vs-tag QUESTION: QUESTIONS.md.
- F10 SBOM: Phase G11.4 or v1.5.
- F12 furqan PyPI dep: declined Shape C.
- F17 framework section 4 amendment: framework-side.
- F20 sandbox-CI parity: separate release-checklist amendment.
- F21 PyPI CDN cache transient: separate runbook amendment.

### Tests

Test count: 576 (v0.11.1 ship state) -> 589 (v0.11.2).
Net delta: +13 (8 in test_python_signature_h4.py covering
the H-4 fixtures + inner-difference detection + tuple-value
preservation; 5 in test_backfill_dry_run.py covering F18
no-flag exit / both-flags rejection / no-subprocess-call /
expected-version enumeration / F19 workflow-managed-floor).

### Cross-language symmetry restored

After v0.11.2, the Python verifier's signature canonicalization
matches the Rust verifier's amended_4 T03 rules 6 + 7
(nested-generic element-wise recursion). The other amended_4
defenses (C-1 identity policy, H-5 trusted_root threading,
H-6 checker_set_hash, M-7 typed identity-extraction errors)
were already shared between the two pipelines from v0.11.0.

### Round-28 closure ledger

| Disposition | Count | Findings |
|-------------|-------|----------|
| Genuine v0.11.2 closure | 4 | H-4, M-5, M-6, F18 |
| Acknowledgement (closed in v0.11.0) | 4 | C-1, H-5, H-6, M-7 |
| Side closure | 1 | F19 |
| Deferral | 7 | F4, F5, F10, F12, F17, F20, F21 |

#### Round 29 addendum -- Process bypass (added retroactively in v0.11.7 per al-Hujurat T03)

The v0.11.2 commit `474aee488257d3aea6fd4c99209d6f50cfde0c32`
was committed directly to `main` without a PR. Per the
audit-of-self pattern that has been the convention for
v0.11.0, v0.11.1, v0.10.A, and v0.10.0 releases, this is a
process bypass. Round 29 audit named this as A1 ADVISORY.

v0.11.7 closes A1 by documenting PR review as a release-
checklist gate (al-Hujurat T01) and applying a branch
protection rule on `main` (al-Hujurat T02). The v0.11.2
substrate work is unchanged by this addendum; the addendum
records the process state at the time of release.

(Round 30 audit F4 absorption: this is the Option A default
disposition. Project lead did not invoke Option B; this
addendum is the canonical record.)

---

## [0.11.1] - 2026-05-08

### Tooling (al-Mubin / G10.5)

Release tooling tightening per the Round 24/25/26/27 audit
chain findings. Closes 7 findings; retires 4 from prior rounds
via Round 27 empirical correction; defers 5 with explicit
rationale. No new analyzers, no new substrate, no checker
semantics changes.

#### Closures

- F1 closure via T01 + T02 (release.yml extension) + T03
  (12-version backfill via scripts/backfill_github_releases.py)
- F2 closure via T04a (README install-pin sweep:
  v0.4.0/v0.5.0/v0.8.4 -> v0.11.0 across pip-install,
  GitHub-Action use, and pre-commit rev examples)
- F3 closure via T04b (README "Closed in v" sections retired
  per framework section 10.2; 145 lines deleted; single
  Closure-history pointer takes their place)
- F7 closure via T01 (PyPI verification step in release.yml:
  12 polls at 10-second intervals, 120-second window per
  S5 calibration)
- F8 closure via T01 + T02 (release.yml workflow scope; the
  gh release create step is wired alongside the PyPI
  verification step)
- F9 closure via T04d (scripts/release_sweep.py: stdlib-only
  release-time gate sweeping README install pins, GitHub
  Action use pins, pre-commit rev pins, and SAFETY_INVARIANTS.md
  presence)
- F15 closure via T04c (README Sigstore-CASM section + Gate
  11 install rows + SAFETY_INVARIANTS.md pointer; the
  substrate that shipped in v0.10.0 + v0.11.0 is now
  visible in the README, not only in SECURITY.md and
  CHANGELOG.md)

#### Round-27 retirements (corrections from prior rounds)

- F6 retired: the "no closure between rounds" pattern was an
  artifact of audit-substrate inspection-scope gap (Round 25
  + 26 looked at README + CHANGELOG + Releases UI but not
  pyproject.toml + SECURITY.md); Phase G11.A + G11.0 + G11.1
  shipped between Round 24 and Round 27 but were invisible
  to the narrower inspection scope.
- F11 retired: pyproject.toml's `[tool.pytest.ini_options].markers`
  declares 5 markers (network, slow, unit, integration, mock);
  Round 27 inspection of pyproject.toml confirmed the
  declaration.
- F13 retired: substrate-divergence question RESOLVED via
  cross-substrate empirical corroboration in Round 27.
- F14 retired: three-round closure stall pattern dissolved
  with proper substrate inspection.

#### Deferrals

- F4 ONNX empty-graph: Phase G11.3 scope.
- F5 Release-vs-tag QUESTION: routes to QUESTIONS.md.
- F10 SBOM: Phase G11.4 (Tasdiq al-Bayan) or v1.5.
- F12 furqan PyPI dep: declined Shape C; out of scope.
- F16 CHANGELOG terminus interpretation: closes by execution
  if this entry appears past the existing visible terminus.
- F17 framework section 4 amendment: framework-side; not a
  release scope item.

### Added

- `.github/workflows/release.yml` "Verify PyPI publication"
  step (T01).
- `.github/workflows/release.yml` "Create GitHub Release"
  step (T02) with `contents: write` permission added to the
  publish job alongside the existing `id-token: write`.
- `scripts/extract_changelog_section.py`: stdlib-only helper
  used by T02 to derive Release notes from a single
  CHANGELOG `## [X.Y.Z]` section.
- `scripts/backfill_github_releases.py`: one-time backfill
  tool for the 12-version historical gap (v0.8.2 through
  v0.11.0; runs manually from local clone).
- `scripts/release_sweep.py`: pre-release sweep gate.
- `docs/release-checklist.md`: codifies the manual gates
  alongside the automated workflow steps.

### Changed

- README: install-pin sweep (T04a); closure-sections
  retired (T04b); Sigstore-CASM substrate documented (T04c
  via the Phase G11.0 + G11.1 sections already present).

### Tests

Test count: 561 (v0.11.0 ship state) -> 576 (v0.11.1).
Net delta: +15 (4 in test_extract_changelog_section.py;
2 in test_readme_closure_sections_retired.py; 4 in
test_readme_gate11_section_present.py; 5 in
test_release_sweep_extension.py).

### Round-27 closure ledger

| Disposition | Count | Findings |
|-------------|-------|----------|
| Closure     | 7     | F1, F2, F3, F7, F8, F9, F15 |
| Retirement  | 4     | F6, F11, F13, F14 |
| Deferral    | 6     | F4, F5, F10, F12, F16, F17 |

---

## [0.11.0] - 2026-05-07

Phase G11.1 (as-Saffat) ships Sigstore-CASM Gate 11 v1.0 for
Rust source files. New optional ``[gate11-rust]`` extra brings
in ``sigstore`` plus ``rfc8785`` plus ``tree-sitter-rust``;
``furqan-lint manifest <action>`` and ``check --gate11`` now
dispatch on file extension (.py vs .rs). The CASM v1.0 schema
is extended to accept ``language: "rust"`` and Rust kinds
(struct, enum, trait, type_alias, alias).

This release also closes Round-N+1 audit findings against the
Phase G11.0 v0.10.0 ship (CRITICAL C-1 identity policy gap;
HIGH H-4 nested-generic stringification; HIGH H-5 trusted_root
threading; HIGH H-6 checker_set_hash placeholder dressed as
commitment; MEDIUM M-6 README claim without substrate; MEDIUM
M-7 string sentinels for identity extraction). Corrections are
applied prospectively to the Rust pipeline AND backported to
the Python pipeline so the Python verifier is no longer
shipping the audit gaps.

(populate during release commit)

### Tests

Test count: 511 (v0.10.0 ship state) -> 561
(v0.11.0). Net delta: +50 (49 new Rust Gate 11 tests
across test_gate11_rust_*.py modules; minor updates to
two existing G11.0 tests so the language whitelist and
kind whitelist accept Rust kinds).

### Rust Sigstore-CASM documented limits (Phase G11.1 T08)

Each fixture below pins a current furqan-lint Rust adapter
behaviour as a v1.0 documented limit in the Sigstore-CASM
substrate; improvement is a v1.5 horizon item.

- ``lifetime_stripped_from_signature``: lifetimes are stripped
  during canonicalization.
- ``impl_methods_omitted_from_surface``: impl-block methods are
  not in the v1.0 public-surface fingerprint.
- ``trait_object_literal_text``: ``Box<dyn Trait>`` is signed
  as literal text.
- ``macro_call_signed_pre_expansion``: macros are signed at the
  source level, not after expansion.
- ``pub_crate_excluded``: ``pub(crate)`` and ``pub(super)`` items
  are not part of the external API surface.

---

## [0.10.0] - 2026-05-07

Phase G11.A (al-Fatiha) ships `SAFETY_INVARIANTS.md` at the
repository root as the foundational invariants document for
Sigstore-CASM Gate 11. The file is normative for all
subsequent Phase G11.x implementations (G11.0 through G11.12).

Subsequent Phase G11.x release commits (G11.0, G11.1, G11.2,
etc.) populate the v0.10.0 entry with substrate-specific
detail; this CHANGELOG header lands first via Phase G11.A so
that the CHANGELOG-math gate skips the placeholder during the
in-flight Phase G11.x implementation cycle.

### Added

- `SAFETY_INVARIANTS.md` at the repository root containing the
  seven canonical Sigstore-CASM invariants, the four mandatory
  disclosures inherited from the Sigstore threat model, the
  eight at-Tartib strategy cross-references, the foundation-
  status inheritance disclosure (Section 8), the normative
  references block (per audit F2), and the auditor's response
  register documenting the v1.0_corrected /
  v1.0_second_revision / v1.0_second_revision_amended /
  v1.0_second_revision_amended_2 evolution.
- README forward-reference paragraph noting the
  candidate-finding status of Strategy 1's empirical
  foundation and pointing to `Bayyinah at-Tartib v1.0` (second
  revision May 7 2026) and `Bayyinah al-Munasabat v1.0`
  (second revision May 7 2026) as the methodology papers.
- CONTRIBUTING.md requirement that contributors read
  `SAFETY_INVARIANTS.md` before submitting Phase G11.x patches.
- SECURITY.md cross-reference for the cryptographic substrate
  identity.
- `.pre-commit-config.yaml` hook that fails commits touching
  `src/furqan_lint/gate11/` or Phase G11.x test fixtures when
  `SAFETY_INVARIANTS.md` is missing. Presence-only check;
  semantic freshness remains a review responsibility per the
  T-A4 honesty note in `SAFETY_INVARIANTS.md` and the audit F3
  finding.
- ``[gate11]`` optional extra (``sigstore>=3.0.0,<4`` and
  ``rfc8785>=0.1.4,<0.2``). Independent of ``[onnx]`` /
  ``[onnx-runtime]`` / ``[onnx-profile]``; adds no inference
  dependencies.
- New ``furqan_lint.gate11`` package: ``manifest_schema``
  (frozen ``Manifest`` + ``PublicName`` dataclasses, RFC 8785
  canonical serialization), ``module_canonicalization``
  (BOM-strip + UTF-8 decode + LF-normalize + SHA-256),
  ``signature_canonicalization`` (canonical type-string
  collapse for ``Optional[X]`` / ``Union[X, None]`` / ``X | None``
  to alphabetized ``X | None``), ``surface_extraction``
  (reuses ``furqan_lint.additive._extract_public_names``),
  ``signing`` (Sigstore production / staging / GitHub-OIDC),
  ``bundle`` (``<module>.furqan.manifest.sigstore`` wire
  format), ``verification`` (9-step CASM-V flow), ``cli``
  (manifest subcommand dispatch).
- ``furqan-lint manifest init / verify / update <module.py>``
  CLI subcommand.
- ``furqan-lint check --gate11 <path>`` flag that runs the
  normal check pipeline plus CASM-V verification on any
  sibling ``.furqan.manifest.sigstore`` bundle.
- ``CASM-V-NNN`` error namespace covering parse (010), version
  / language (001..002), TUF (020 / 021), Sigstore (030..034),
  module-hash (040), additive-only contract (050 / 051),
  chain (060 / 061).
- ``CASM-V-INDETERMINATE`` result on dynamic ``__all__``
  modules (rather than a false pass).
- ``scripts/regenerate_check_table.py`` plus pre-commit hook
  plus ``tests/test_regenerate_check_table.py`` close
  finding F1 (README structural-checks block now auto-derived
  between sentinel comments).
- ``.github/workflows/ci.yml`` ``gate11-smoke-test`` job
  (push-to-main only; ``id-token: write``;
  ``FURQAN_LINT_GATE11_SMOKE_TEST=1``).
- ``action.yml`` composite-action ``gate11`` input (default
  ``false``).
- README ``Sigstore-CASM Gate 11 (opt-in)`` section,
  ``Closed in v0.10.0`` block, the four Newman 2022 disclosures
  (N1 short-window OIDC compromise, N2 typosquatting, N3 Rekor
  privacy, N4 retention horizon), the SCITT vocabulary
  citation, and Shape A scope statements F4 (recursive linter
  trust) and F7 (Rekor public-surface leakage).
- ``SECURITY.md`` Gate 11 disclosures section; supported-versions
  table refreshed (0.10.x supported, 0.8.x EOL).
- ``CONTRIBUTING.md`` Gate 11 testing section.

### Changed

- The CLI dispatcher now recognises ``args[0] == "manifest"``
  and routes to ``furqan_lint.gate11.cli.dispatch_manifest``;
  the ``check`` subcommand parses out an optional ``--gate11``
  flag before invoking the existing primary-check pipeline.

### Fixed

- F1 (README count drift): closed structurally via the
  pre-commit / CI ``regenerate_check_table.py --check`` gate.

### References

- `Bayyinah at-Tartib v1.0` (second revision May 7 2026):
  full strategy elaboration, application examples, case-by-
  case counterfactual mapping, conditional economic case,
  policy-vs-engineering distinction for public-interest
  software.
- `Bayyinah al-Munasabat v1.0` (second revision May 7 2026):
  empirical methodology, within-quartile shuffle test,
  orthogonal char-3-gram pipeline, Bonferroni significance.
- `MUSHAF_TABLE_OF_CONTENTS_v1_0_second_revision.md`: full
  Phase G11.x roadmap (G11.0 through G11.12).

### Foundation-status disclosure

The seven canonical Sigstore-CASM invariants are NOT magnitude
claims about the al-Munasabat empirical finding and NOT
prevention claims about the at-Tartib counterfactual. They are
cryptographic and protocol specifications grounded in
production-deployed Sigstore (Newman et al. 2022; deployment
evidence Schorlemmer et al. 2024 and Kalu et al. 2025) and
IETF SCITT (RFC-track). The Sigstore-CASM substrate's value is
to make supply-chain failures cryptographically attributable
and forensically reconstructable, not to prevent supply-chain
failures directly. Strategy 1 (Canonical-First Architecture),
the strategy most directly affected by the al-Munasabat
empirical magnitude, is at candidate-finding status pending
independent replication.

### Tests

Test count: 441 (v0.9.4 ship state) -> 511 (v0.10.0).
Net delta: +70 (67 across the eight ``test_gate11_*.py``
modules; 3 in ``test_regenerate_check_table.py``).

---

## [0.9.4] - 2026-05-05

Five-part-plus-carry-forward release. Closes Gap 2 (MEDIUM)
score-validity advisory; closes round-30 META v0.9.0-pinned
scaffold (in its fifth release cycle); closes round-34
MEDIUM-1 (NeuroGolf canonical adapter docs), LOW-1 (ruff
version-pin friction), and HIGH-1's bug class via Part 5's
structural CLI-integration gate; closes the three v0.9.3.1
carry-forwards via Part 5b (ONNX printer ``minimal_fix``
consistency, ``_TESTS_LINE`` regex fragility, CI matrix
``[onnx-runtime]`` gap).

### Fixed

- **Round-34 HIGH-1 bug class (HIGH).** Part 5 ships a new
  AST-based gate ``test_gate_cli_diagnostic_printer_includes_all_diagnostic_classes``
  that asserts the CLI's ``_check_onnx_file`` printer
  isinstance tuple is the union of every ``*Diagnostic``
  class defined in ``runner.py`` plus those exported via
  ``furqan_lint.onnx_adapter.__all__``. The v0.9.3.1 hotfix
  fixed the bug instance for ``NumpyDivergenceDiagnostic``;
  v0.9.4's gate prevents recurrence when ``ScoreValidityDiagnostic``
  joins the family in this same release.
- **Round-34 v0.9.3.1 carry-forward (Part 5b(a), MEDIUM):**
  ``AllPathsEmitDiagnostic`` and ``OpsetComplianceDiagnostic``
  gain required ``minimal_fix`` fields; the v0.9.0 substrate
  shipped without them, leaving the ONNX printer inconsistent
  with the Python/Rust/Go marad printers from v0.9.0 through
  v0.9.3.1. The CLI's ONNX printer extends to print
  ``minimal_fix`` for every ONNX diagnostic family matching
  the Python/Rust/Go pattern; Part 5's gate is extended to
  AST-scan for the ``getattr(d, 'minimal_fix', None)`` block
  presence so a future refactor cannot reintroduce the
  inconsistency.
- **Round-34 HIGH-2a (Part 5b(b), MEDIUM):** the
  ``_TESTS_LINE`` regex in
  ``tests/test_changelog_math_gate.py`` required the literal
  ``"Net delta:"`` on one line. v0.9.3's CHANGELOG body
  wrapped as ``"Net\\ndelta: +23."`` and the regex returned
  ``None``, silently no-opping the gate. v0.9.4 changes
  ``"Net delta:"`` to ``"Net\\s+delta:"`` so any whitespace
  works; a regression test pins the wrap case.
- **Round-34 HIGH-2b (Part 5b(c), MEDIUM):** existing CI
  matrix had no ``[onnx-runtime]`` job, so the
  CHANGELOG-math gate's onnxruntime-skip workaround (added
  in v0.9.3.1's CI hotfix) meant the gate never ran at full
  strength in CI. v0.9.4 adds a ``test-onnx-runtime`` job
  installing ``[dev,onnx,onnx-runtime,onnx-profile]`` on
  Python 3.12; the gate runs without the skip in this job.
- **Round-34 LOW-1 (Part 4, LOW):** ``test_ruff_check`` and
  ``test_ruff_format_check`` skip with an actionable
  ``"ruff version mismatch: pyproject pins X, installed is Y;
  run pip install ruff==X to match"`` message when the
  contributor's installed ruff differs from the pyproject
  ``[dev]`` pin.
- **CLI ADVISORY/MARAD split (Part 2 / Decision 3):** the
  ONNX printer partitions findings by ``severity`` field and
  prints with ``[MARAD]`` or ``[ADVISORY]`` prefix. ADVISORY
  findings exit 0; only MARAD findings exit 1.
- ``check_onnx_module`` now runs five checkers (was four);
  ``score_validity`` is the fifth, appended to the diagnostic
  tag list per Part 2 / Decision 1.

### Added

- **Score-validity ADVISORY checker (Part 2 / Gap 2 closure /
  MARAD-3 closure from cont45).** New
  ``src/furqan_lint/onnx_adapter/score_validity.py`` wraps
  ``onnx_tool.model_profile()`` in
  ``contextlib.redirect_stdout`` and exception-trapping; on
  any unhandled exception, yields one
  ``ScoreValidityDiagnostic`` with ``severity="ADVISORY"``.
  Op-type extraction heuristic walks the exception traceback
  for the deepest frame whose ``self.op_type`` is a string;
  falls back to ``"<unknown>"``. Closes Gap 2 (MEDIUM) per
  Decision 9 of v0.9.2 and the round-32 NeuroGolf leverage
  analysis. Empirically verified: cont45 substrate (TopK
  without axis) fires; clean Relu profiles cleanly.
- ``ScoreValidityDiagnostic`` dataclass (frozen, 6 required
  fields: ``op_type``, ``exception_class``,
  ``exception_message``, ``severity``, ``diagnosis``,
  ``minimal_fix``). The ``severity`` field is load-bearing
  for the CLI ADVISORY/MARAD split.
- ``OnnxProfileExtrasNotInstalled`` typed-exception (subclass
  of ``ImportError``); mirrors
  ``OnnxExtrasNotInstalled`` and
  ``OnnxRuntimeExtrasNotInstalled``. Three-extra architecture
  symmetry: ``[onnx]`` graph-structure checks,
  ``[onnx-runtime]`` inference-based divergence,
  ``[onnx-profile]`` profile-validity advisory.
- ``[onnx-profile]`` pip extra (Decision 5) listing
  ``onnx>=1.14,<1.19`` and ``onnx-tool>=1.0,<2``.
- ``score_validity_optin_extra`` four-place documented limit
  with full coverage (CHANGELOG / fixture / pinning test /
  README): the score-validity checker is opt-in via the
  ``[onnx-profile]`` extra and silent-passes when the extra
  is missing.
- **NeuroGolf canonical adapter README section (Part 3 /
  round-34 MEDIUM-1 closure).** New section "ONNX
  numpy_reference convention for NeuroGolf-shape models"
  documents two canonical patterns (Pattern A: pre-one-hot
  input; Pattern B: raw grid + local encoding) with code
  blocks and pointers to verified worked-example fixtures
  at ``tests/fixtures/onnx/numpy_reference_examples/``. The
  v0.9.3 four-place limit named the convention dependency
  but did not show the canonical adapter; v0.9.4 closes the
  adoption gap.
- **AllPathsEmitDiagnostic.minimal_fix and
  OpsetComplianceDiagnostic.minimal_fix** required fields
  (Part 5b(a)). Pre-v0.9.4 these dataclasses had no
  ``minimal_fix`` field, so the v0.9.0/v0.9.1/v0.9.2/v0.9.3.1
  ONNX printer had no field to print even if it had been
  trying to. v0.9.4 closes the inconsistency at both layers.
- **CI ``test-onnx-runtime`` job (Part 5b(c)).** New job in
  ``.github/workflows/ci.yml`` installs
  ``[dev,onnx,onnx-runtime,onnx-profile]`` on Python 3.12
  and runs the full pytest suite. The CHANGELOG-math gate
  runs at full strength in this job; gates remain active in
  the other jobs.
- **CLI integration AST gate (Part 5).**
  ``test_gate_cli_diagnostic_printer_includes_all_diagnostic_classes``
  uses ``ast.parse`` to walk both ``runner.py`` (for
  ``class *Diagnostic`` definitions) and ``__init__.py``
  (for ``__all__`` exports) plus ``cli.py`` (for the
  isinstance tuple inside ``_check_onnx_file``); asserts
  the printer's tuple is a superset. Plus a self-verifying
  negative test on a synthetic CLI source missing one
  family.
- ``ONNX_ADAPTER_PUBLIC_SURFACE_v0_9_4`` baseline pins the
  new surface (15 + 3 = 18 names).
- ``test_tests_line_regex_accepts_multiline_net_delta_wrap``
  regression test pinning the regex against the v0.9.3 wrap
  pattern that silently no-opped the gate.
- Worked-example fixtures
  ``onehot_input_example_build.py`` and
  ``raw_grid_input_example_build.py`` documenting the two
  Pattern A / Pattern B numpy_reference adapters.

### Changed

- ``check_onnx_module(module, model_proto, model_path)`` now
  runs five checkers (was four).
- ``cli._check_onnx_file``: imports ``ScoreValidityDiagnostic``
  from the source module (per the v0.9.3.1 / Part 5
  AST-gated source-module pattern); isinstance tuple extends
  from four families to five; ADVISORY/MARAD partition
  determines headline ("MARAD <path>", "ADVISORY <path>",
  or mixed-case summary line); each diagnostic line prints
  ``minimal_fix`` matching the Python/Rust/Go marad pattern.
- README install section adds the ``[onnx-profile]`` row
  and updates the combined-extras example to
  ``[rust,go,onnx-runtime,onnx-profile]``. The "ONNX
  adapter (current as of v0.9.3)" header bumps to v0.9.4
  with the ``score_validity_optin_extra`` documented limit
  added at the top of the inventory.
- ``tests/fixtures/onnx/documented_limits/README.md``:
  inventory bumps to v0.9.4 with the
  ``score_validity_optin_extra`` entry first.
- ``_TESTS_LINE`` regex: ``Net delta:`` to ``Net\\s+delta:``.

### Retired

- ``tests/test_onnx_gates.py::test_gate_changelog_math_v0_9_0``
  (Part 1 / round-30 META closure). The v0.9.0-pinned
  scaffold has been skip-only across v0.9.1, v0.9.2, v0.9.3,
  v0.9.3.1, and v0.9.4 release cycles; the canonical
  ``test_changelog_math_matches_pytest_collect`` covers the
  same arithmetic check version-agnostically. Retiring the
  scaffold removes 1 test from the collected total. Round-30
  META was originally an INFORMATIONAL observation; the
  five-release escalation reflects cumulative cost of dead
  code in the test suite.

### Tests

Test count: 413 (v0.9.3.1 ship state) -> 441 (v0.9.4). Net
delta: +28.

Breakdown:

- Part 1 retirement: -1 (test_gate_changelog_math_v0_9_0)
- Part 2 score-validity (commit 3): +7 (4 firing/clean + 2
  op-type extraction + 1 stdout-capture)
- Part 2 CLI ADVISORY + Part 5b(a) minimal_fix (commit 4):
  +9 (4 ADVISORY/MARAD split + 5 minimal_fix regression
  tests, one per ONNX diagnostic family)
- Part 2 silent-pass + four-place + runner integration
  (commit 5): +3 (silent-pass pin + runner-integration
  alongside four v0.9.3 checkers + OnnxProfileExtrasNotInstalled
  exception type check)
- Part 3 NeuroGolf docs (commit 6): +3 (Pattern A zero-
  divergence + Pattern B zero-divergence + README section
  presence)
- Part 4 ruff friction (commit 7): +2 (helper-skips-on-mismatch
  + helper-does-not-skip-when-versions-match)
- Part 5 + Part 5b(a) AST gate (commit 8): +3 (printer
  isinstance gate + minimal_fix block gate + negative-test
  parser self-verification)
- Part 5b(b) regex regression (commit 9): +1
- Part 5b(c) CI matrix job (commit 10): +0 (CI infrastructure)
- V0_9_4 surface snapshot (commit 11): +1

Sum: -1 + 7 + 9 + 3 + 3 + 2 + 3 + 1 + 0 + 1 = +28 ✓

### Round-35 closure ledger

| Finding | Source | Severity | Closure |
| --- | --- | --- | --- |
| Gap 2 | v0.9.1 NeuroGolf evaluation | MEDIUM | Closed via Decisions 2-9 (Part 2). Score-validity ADVISORY checker via ``onnx_tool.model_profile``; three-extra architecture. |
| Round-30 META | round-30 audit, surfaced across v0.9.0-v0.9.3.1 | INFORMATIONAL -> MEDIUM | Closed via Part 1 (single-test deletion of v0.9.0-pinned scaffold). Five-release escalation. |
| MARAD-3 (cont45 TopK profiler-blocker) | round-32 leverage analysis | MEDIUM | Closed via Part 2 (score-validity advisory fires on cont45 fixture). |
| Round-34 MEDIUM-1: NeuroGolf adapter convention not worked through | round-34 audit | MEDIUM | Closed via Part 3 (README section + worked-example fixtures for Pattern A and Pattern B). |
| Round-34 LOW-1: ruff version pin friction | round-34 audit | LOW | Closed via Part 4 (skip-on-mismatch with actionable message). |
| Round-34 HIGH-1 bug class | round-34 audit | HIGH | Closed via Part 5 (AST-based CLI integration gate). v0.9.3.1 fixed the instance; v0.9.4 prevents recurrence. |
| v0.9.3.1 carry-forward: ONNX printer minimal_fix gap | v0.9.3.1 hotfix audit | MEDIUM | Closed via Part 5b(a). 5 regression tests + gate extension. |
| Round-34 HIGH-2a: _TESTS_LINE regex literal-space fragility | v0.9.3.1 PR build | MEDIUM | Closed via Part 5b(b). Regex changed to ``Net\\s+delta:``. |
| Round-34 HIGH-2b: CI matrix has no [onnx-runtime] job | v0.9.3.1 PR build | MEDIUM | Closed via Part 5b(c). New ``test-onnx-runtime`` CI job. |
| v0.9.0 Decision 1 standing rule operating as three-extra architecture | round-33 architectural finding | INFORMATIONAL | Affirmed. ``[onnx]``, ``[onnx-runtime]``, ``[onnx-profile]`` for three concerns. |

10 closures (1 MEDIUM = Gap 2, 1 MEDIUM = stale scaffold, 1 MEDIUM = MARAD-3, 1 MEDIUM = NeuroGolf docs, 1 LOW = ruff friction, 1 HIGH = bug class, 1 MEDIUM = printer minimal_fix consistency, 1 MEDIUM = regex fragility, 1 MEDIUM = CI matrix gap, 1 INFORMATIONAL = architectural affirmation).

## [0.9.3.1] - 2026-05-04

CLI hotfix. Closes round-34 HIGH-1: the CLI's
``_check_onnx_file`` printer hardcoded an isinstance tuple
that filtered the new ``NumpyDivergenceDiagnostic`` family
out, so users running ``furqan-lint check`` on a divergence-
firing model saw:

    MARAD <path>
      1 violation(s):

with no body. The substrate-side ``check_numpy_divergence``
correctly emitted the diagnostic; the CLI surface dropped it.
The bug rendered the v0.9.3 headline feature unusable from
the CLI; the fix is one line plus an import.

### Fixed

- **Round-34 HIGH-1 (HIGH).** ``cli._check_onnx_file``
  isinstance tuple extended from three diagnostic families
  (AllPathsEmitDiagnostic, OpsetComplianceDiagnostic,
  ShapeCoverageDiagnostic) to four. The fourth family,
  ``NumpyDivergenceDiagnostic`` (added in v0.9.3), now prints
  its diagnosis body alongside the other three.
- A regression test
  (``test_cli_numpy_divergence_body_prints``) runs the CLI
  end-to-end via subprocess on a divergence-firing fixture,
  asserts the ``numpy_divergence`` tag and diagnosis prose
  appear in stdout, and asserts the negative case (stdout
  does not match the bug shape of an empty body after the
  violations count). The regression pin is the surface-to-
  substrate match: a future addition of a fifth diagnostic
  family (e.g., ``ScoreValidityDiagnostic`` in v0.9.4) will
  not silent-drop because the test catches the same bug
  shape.

### Known limitations carried to v0.9.4

- **ONNX printer's ``minimal_fix`` field is silently dropped**
  (consistent across all four diagnostic families). The
  Python, Rust, and Go marad printers in the same
  ``cli.py`` follow a different pattern that prints both
  ``diagnosis`` and ``minimal_fix``; the ONNX path prints
  ``diagnosis`` only. Bundling this fix to v0.9.4 Part 5b
  alongside the structural CLI-integration gate per §3.5
  of the v0.9.3.1 prompt: fixing it in one family only
  would create a new inconsistency, and fixing it for all
  four families is structurally adjacent to v0.9.4's gate
  work that prevents the v0.9.3.1 bug class from recurring.
- **CHANGELOG-math gate skips in lean CI envs** (round-34
  HIGH-2). The canonical CHANGELOG test count includes the
  11 onnxruntime-gated tests in
  ``test_onnx_numpy_divergence.py`` that use
  ``pytest.importorskip("onnxruntime")``. CI's test jobs
  install ``[dev,onnx]`` (no onnxruntime), producing an
  empirical count 11 below the canonical number. Gate now
  skips with a descriptive message when ``onnxruntime`` is
  not importable; runs at full strength on developer
  machines and the bundle-author sandbox. v0.9.4 Part 5b
  closes this by adding an ``[onnx-runtime]`` job to the
  CI matrix so the gate runs in CI too. Until then,
  arithmetic drift in the CHANGELOG ``### Tests`` line is
  caught locally but not in CI for releases that touch
  onnxruntime-gated test counts.

### Tests

Test count: 412 (v0.9.3 ship state) -> 413 (v0.9.3.1).
Net delta: +1.

Breakdown:

- Regression test: +1
  (``test_cli_numpy_divergence_body_prints``)

### Round-34 closure ledger

| Finding | Source | Severity | Closure |
| --- | --- | --- | --- |
| HIGH-1 | round-34 audit (post-v0.9.3-ship) | HIGH | Closed in v0.9.3.1. Decision 1 extends the isinstance tuple; Decision 2 adds the source-module import; Decision 3 lands the regression test. Decision 4 defers the structural CLI-integration gate to v0.9.4 (the bug class, not just the bug instance). The fix is one line; the regression test pins the surface to the substrate. |

## [0.9.3] - 2026-05-04

numpy-vs-ONNX divergence detection. Closes Gap 4 (HIGH
competition lever) per the round-32 NeuroGolf leverage analysis.
A new optional ``[onnx-runtime]`` extra brings in
``onnxruntime`` and ``numpy``; a fourth ONNX checker
(``numpy_divergence``) loads a discoverable numpy reference
function alongside each ``.onnx`` file, runs both on a probe
grid extracted from the corresponding ARC-AGI task file, and
fires when the outputs disagree.

The check is opt-in by reference presence: it silent-passes
when the ``[onnx-runtime]`` extra is not installed, when no
``<basename>_build.py`` is discoverable, or when no
``<basename>.json`` task file is discoverable. Generic ONNX
users with no NeuroGolf-shaped sidecars see no behavior change.

**Renumbering note.** The original v0.9.x sequence had v0.9.3 =
score-validity advisory and v0.9.4 = numpy-vs-ONNX divergence.
The round-32 leverage analysis identified divergence detection
as substantially higher-leverage; this release renumbers it to
v0.9.3 to ship the lever sooner. Score-validity becomes v0.9.4.

### Fixed

- ``check_onnx_module`` signature gains a third required-positional
  parameter ``model_path`` per Decision 1 of the v0.9.3 prompt
  and round-33 HIGH-1 closure. The fail-fast discipline favors
  a ``TypeError`` on a missing argument over silently skipping
  ``numpy_divergence``. A ``model_path=None`` default was
  considered and rejected: it would reverse the round-30 MED-2
  closure and silently skip the new checker. The single
  existing call site (``cli._check_onnx_file``) is updated
  atomically; ``tests/test_onnx_correctness.py`` and
  ``tests/test_onnx_shape_coverage.py`` call sites pass a
  non-existent path so ``numpy_divergence`` silent-passes per
  Decision 6 conditions (b)/(c).
- The v0.9.0 Decision 1 standing rule "No ``onnxruntime``
  dependency at lint time" is amended in v0.9.3 per Decision 7:
  the rule continues to hold for the ``[onnx]`` extra; v0.9.3
  introduces a separate ``[onnx-runtime]`` extra for the new
  inference-based checker. Users running graph-structure checks
  only (D24-onnx, opset-compliance, D11-onnx shape/type)
  continue to pay no ``onnxruntime`` install cost.

### Added

- ``src/furqan_lint/onnx_adapter/numpy_reference.py``:
  ``discover_numpy_reference(model_path)`` looks for
  ``<basename>_build.py`` containing top-level callable
  ``numpy_reference``. Loads via
  ``importlib.util.spec_from_file_location`` with a
  unique-per-invocation module name so ``sys.modules`` is not
  polluted across check invocations (round-33 robustness pin).
  Returns ``None`` (silent-pass) on any load failure; the lint
  must not blow up because a sidecar is malformed.
- ``src/furqan_lint/onnx_adapter/probe_grid.py``:
  ``discover_probe_grids(model_path)`` looks for
  ``<basename>.json`` in two locations (primary
  ``<dir>/<basename>.json``, fallback
  ``<dir>/../tasks/<basename>.json``) in ARC-AGI format with
  ``train[*]['input']``. Multi-example tasks emit one grid per
  example in document order.
- ``src/furqan_lint/onnx_adapter/numpy_divergence.py``:
  ``NumpyDivergenceDiagnostic`` dataclass (frozen, 9 required
  fields including ``model_path``, ``reference_path``,
  ``task_path``, ``probe_index``, ``numpy_output_summary``,
  ``onnx_output_summary``, ``divergence_summary``,
  ``diagnosis``, ``minimal_fix``).
  ``check_numpy_divergence(model_proto, model_path)`` runs
  both numpy reference and ONNX inference on each probe grid,
  yields one diagnostic per diverging probe (or per side that
  raises an exception). Multi-probe robustness: an exception
  on one probe does not abort the others.
- Tolerance modes (Decision 4): cell-exact via
  ``np.array_equal`` if output dtype is integer OR rank >= 4
  with channel dimension matching a known one-hot width
  (default ``(10,)`` for ARC-AGI); ``np.allclose(rtol=1e-5,
  atol=1e-7)`` otherwise.
- Input-shape adaptation (S2): adds leading axes until the
  input rank matches the ONNX expected rank. Documented
  approach for NeuroGolf models that expect ``(1, 1, H, W)``
  but ARC-AGI grids are stored as ``[[...]]`` rank-2.
- ``OnnxRuntimeExtrasNotInstalled`` typed-exception (subclass
  of ``ImportError``). Distinguishes the inference-extra
  failure from the ``[onnx]`` graph-only extra failure.
- ``[onnx-runtime]`` pip extra (Decision 5) listing
  ``onnx>=1.14,<1.19``, ``onnxruntime>=1.16``, ``numpy>=1.20``
  directly. The duplicated ``onnx>=1.14,<1.19`` across ``[onnx]``
  and ``[onnx-runtime]`` is intentional (round-33 MEDIUM
  closure): trades minor duplication for install-tool
  compatibility across the entire pip version matrix (the
  self-referencing ``furqan-lint[onnx]`` syntax is PEP 508
  compliant only since pip 21.2 and breaks on older pip
  versions and some build tools).
- ``numpy_divergence_neurogolf_convention`` documented-limit
  fixture (``tests/fixtures/onnx/documented_limits/``) plus
  pinning test
  ``test_numpy_divergence_silent_pass_when_neurogolf_convention_absent``:
  records that the v0.9.3 numpy-vs-ONNX divergence checker is
  opt-in by NeuroGolf-convention sidecar presence per
  Decision 9 of the v0.9.3 prompt. Generic ONNX users with no
  ``_build.py`` + ``.json`` sidecars see silent-pass on the
  divergence checker. General-purpose conventions are tracked
  as a v0.9.5+ extension.
- Five new public exports in
  ``furqan_lint.onnx_adapter.__all__``:
  ``NumpyDivergenceDiagnostic``, ``check_numpy_divergence``,
  ``OnnxRuntimeExtrasNotInstalled``,
  ``discover_numpy_reference``, ``discover_probe_grids``.
- ``ONNX_ADAPTER_PUBLIC_SURFACE_v0_9_3`` baseline pins the new
  surface; the strict-superset assertion in
  ``test_v0_9_3_onnx_adapter_surface_snapshot`` catches any
  future drift.

### Changed

- ``check_onnx_module(module, model_proto, model_path)`` now
  runs four checkers in order:
  ``all_paths_emit`` (D24-onnx, v0.9.0),
  ``opset_compliance`` (v0.9.0),
  ``shape_coverage`` (v0.9.1 + v0.9.2),
  ``numpy_divergence`` (v0.9.3).
- ``cli._check_onnx_file``: passes ``path`` (the directory
  walker's ``Path``) as the third argument. PASS message
  updated from "3 structural checks" to "4 structural checks
  ran" with a parenthetical note that ``numpy_divergence``
  silent-passes when the ``[onnx-runtime]`` extra is missing
  or no NeuroGolf-convention sidecar is present.
- README "ONNX adapter (current as of v0.9.1)" header bumped
  to v0.9.3; new ``numpy_divergence_neurogolf_convention``
  limit added as the first entry; install instructions add
  the ``[onnx-runtime]`` row and update the combined-extras
  example to ``[rust,go,onnx-runtime]``.
- Four-place-completeness gate's ``_README_TOPIC_KEYWORDS``
  gains a ``numpy_divergence_neurogolf_convention`` entry
  with topic keywords ``("numpy_divergence", "NeuroGolf",
  "_build.py")``.

### Tests

Test count: 389 (v0.9.2 ship state) -> 412 (v0.9.3). Net
delta: +23.

Breakdown:

- Reference-discovery tests: +5
  (finds existing _build.py; returns None when absent;
  returns None when not callable; returns None on syntax
  error; does not pollute sys.modules)
- Probe-grid-discovery tests: +4
  (finds primary; finds fallback ../tasks/; returns None when
  no task file; returns multiple grids for multi-example task)
- Divergence-checker tests: +10
  (4 firing/clean + 3 silent-pass + 2 runtime-error +
  1 multi-probe)
- Runner-integration + fail-fast pin: +2
  (test_check_onnx_module_runs_all_four_checkers;
   test_check_onnx_module_fail_fast_typerror_on_two_arg_call)
- Documented-limit pinning: +1
  (test_numpy_divergence_silent_pass_when_neurogolf_convention_absent)
- V0_9_3 surface snapshot: +1
  (test_v0_9_3_onnx_adapter_surface_snapshot)

Sum: 5 + 4 + 10 + 2 + 1 + 1 = +23 ✓

### Round-33 closure ledger

| Finding | Source | Severity | Closure |
| --- | --- | --- | --- |
| Gap 4: numpy-vs-ONNX divergence (HIGH competition lever) | round-32 leverage analysis | HIGH | Closed in v0.9.3 round 33 via Decisions 1-10. Empirically verified: onnxruntime + numpy round-trip on the v0.9.2 substrate; importlib loader does not pollute sys.modules; four firing cases verified; all silent-pass conditions verified. |
| CRITICAL: v0.9.3 did not exist when previous draft assumed it had shipped | round-33 audit | CRITICAL | Closed by renumbering. This release ships as v0.9.3 (numpy-vs-ONNX divergence). Score-validity (formerly v0.9.3 = Gap 2) becomes v0.9.4. |
| HIGH-1: signature change breaks existing call sites | round-33 audit | HIGH | Closed via Decision 1 keeping ``model_path`` required-positional. ``model_path=None`` default rejected: would reverse round-30 MED-2 and silently skip ``numpy_divergence``. Existing test call sites updated atomically in commit 4. |
| HIGH-2: NeuroGolf specificity not documented | round-33 audit | HIGH | Closed via Decision 9 expansion + the new four-place documented limit ``numpy_divergence_neurogolf_convention``. |
| MEDIUM: self-referencing pip extra fragile | round-33 audit | MEDIUM | Closed via Decision 5 revision: ``[onnx-runtime]`` lists ``onnx>=1.14,<1.19`` directly rather than via ``furqan-lint[onnx]``. Trades minor duplication for install-tool compatibility. The ``<1.19`` upper bound matches ``[onnx]`` per PR #12 cp313 wheel-availability constraint. |
| LOW: §3 over-specified | round-33 audit | LOW | Closed via §3 trim: the prompt now specifies contracts (function signatures, behavior, silent-pass conditions, dataclass fields); Co-work writes the implementation; the §4 tests are the load-bearing specification. |
| Round-32 ship target before session 52 | round-32 leverage analysis | HIGH (deadline) | Operationalized in this 6-hour scope. The renumbering ships the lever one release sooner. |

7 closures (1 HIGH closed in v0.9.3 = Gap 4, 1 CRITICAL closed = renumbering, 2 HIGH closed = signature + NeuroGolf documentation, 1 MEDIUM closed = pip extra, 1 LOW closed = §3 trim, 1 HIGH operationalized = ship target).

## [0.9.2] - 2026-05-04

D11-onnx adds type-compliance via ``check_type=True``. Closes
Gap 1 from the v0.9.1 post-release NeuroGolf evaluation:
opset-compliance was previously missing
opset-correct-but-type-incompatible operator usages
(Equal-on-float in opset 10 / cont46 NeuroGolf bug class).
Decision 1 of the v0.9.2 prompt passes ``check_type=True``
alongside ``strict_mode=True`` in the
``onnx.shape_inference.infer_shapes`` call. Empirically verified
against onnx 1.17.0: purely additive to ``strict_mode``; zero
regressions on v0.9.1 silent-pass / firing cases.

### Fixed

- **Gap 1 closure (HIGH).** D11-onnx now catches type-restriction
  failures via ``check_type=True``. Equal-on-float in opset 10
  was silent under v0.9.1's ``strict_mode``-only call; v0.9.2
  fires with ``category="type_mismatch"`` and
  ``error_kind="TypeInferenceError"``. The failure mode is a
  real one identified by the post-release NeuroGolf evaluation
  (cont46 bug class) where users encountered it as a runtime
  failure that the lint pipeline did not surface.
- The ``ShapeCoverageDiagnostic.category`` field is **required**
  (no default) per the round-30 fail-fast and round-32 MED-1
  discipline. A future construction site that forgets to set
  ``category`` raises ``TypeError`` at construction time rather
  than silently mislabeling ``type_mismatch`` findings as
  ``shape_mismatch``. The dataclass extension is additive for
  consumers (existing fields unchanged) and breaking for
  constructors; the only construction site is
  ``check_shape_coverage`` in the same module, updated atomically.

### Added

- ``ShapeCoverageDiagnostic.category`` field discriminates three
  sub-types: ``"shape_mismatch"`` (v0.9.1 behavior preserved),
  ``"type_mismatch"`` (v0.9.2 addition under ``check_type=True``),
  and ``"unparseable"`` (the fallback when neither known per-op
  pattern matches). Decision 2 of the v0.9.2 prompt: same outer
  diagnostic family with sub-type metadata on the dataclass,
  preserving the v0.9.1 runner-tag contract.
- ``_TYPE_MISMATCH_RE`` regex parses two empirical body shapes
  observed against onnx 1.14-1.21:
  ``(op_type:Equal): A typestr: T, has unsupported type: tensor(float)``
  and
  ``(op_type:Reshape, ...): shape typestr: tensor(int64), has unsupported type: tensor(float)``.
  The first uses the schema parameter form; the second uses the
  named-input form. Both share the literal ``" typestr: "``
  substring; the regex captures the general ``<token> typestr:``
  shape so both variants route to ``type_mismatch`` rather than
  the unparseable-fallback.
- ``_classify_per_op_finding(text)`` dispatcher tries
  ``_SHAPE_MISMATCH_RE`` first per Decision 3 of the v0.9.2
  prompt: shape-mismatch is preferred when both could match
  because its ``error_kind`` is explicit. The fixed ordering is
  the spec for future-onnx-version stability.
- ``_format_for_category(op, body, category)`` produces sub-type-
  specific diagnosis and ``minimal_fix`` prose. The
  ``type_mismatch`` fix enumerates three actionable options:
  Cast the input, raise the model's opset_import to a version
  where the op accepts the current input type, or replace the op
  with one that natively accepts the type.
- Three new fixture builders in ``tests/fixtures/onnx/builders.py``:
  ``make_equal_float_op10_model`` (fires type_mismatch),
  ``make_equal_int64_op10_model`` (silent-pass, well-typed),
  ``make_reshape_float_shape_op13_model`` (fires type_mismatch
  via the shape-typestr body shape).

### Changed

- ``onnx.shape_inference.infer_shapes`` is now called with both
  ``strict_mode=True`` and ``check_type=True``. Standing Rule of
  the v0.9.2 prompt: the two flags are paired in v0.9.2+; no
  path in ``shape_coverage.py`` uses one without the other.
- ``check_shape_coverage`` rewrote its message-walking logic:
  the master ``_OP_TYPE_MARKER`` regex locates each
  ``(op_type:NAME):`` marker in the InferenceError message and
  the per-marker classifier decides shape-mismatch vs
  type-mismatch vs unparseable. Document order of findings is
  preserved for diagnostic stability. The unparseable-fallback
  fires only when no per-op marker is found anywhere in the
  message, so a single multi-op message never duplicates the
  generic finding alongside per-op findings.
- The three v0.9.1 mock ``_raise`` functions in
  ``tests/test_onnx_shape_coverage.py`` updated to accept
  ``**kwargs`` so they match the new flag combination. The
  v0.9.1 D11-onnx tests automatically become the regression
  suite for the strict_mode + check_type combination per the
  round-32 MED-2 closure.

### Deferred

- **Gap 2** (score-validity advisory via ``onnx_tool.profile``)
  scheduled for **v0.9.3** per Decision 9. The new optional
  extra (``[onnx-profile]`` pulling ``onnx-tool``) needs a
  design round addressing dependency containment, gate semantics
  (advisory vs MARAD), and message format. Closes MARAD-3 from
  cont45 (TopK chain profiler-blocker), unblocks 2 rebuilds.
  Estimated time budget 4 hours.
- **Gap 3** (channel-sum / input-mask consistency) **held until
  NeuroGolf provides a tight spec**. The substrate-side
  consistency definition does not yet exist; implementing
  without a spec would invent a definition that may not match
  actual needs. Per the framework's reproducer-first discipline,
  substrate must precede surface.
- **Gap 4** (numpy-vs-ONNX divergence detection) scheduled for
  **v0.9.4** per Decision 9. Per the round-32 NeuroGolf
  leverage analysis, this is the dominant-failure-mode catch
  (every NeuroGolf primitive has a numpy reference; the
  substrate-vs-surface gap is structurally where bugs hide:
  cont48, cont42 task284 first build, cont44 task313 prefix-sum
  direction). v0.9.4 design round resolves the build-script-to-
  lint contract for discovering numpy reference functions, the
  probe-grid strategy, and the tolerance before commit 1.
  Estimated 2 design + implementation sessions.
- v1.3 paper revision waits for v0.9.2 to ship and tracks v0.9.2
  substrate per Decision 8. The empirical record at v1.3
  publication is "29 versions" instead of "28," and Gap 1
  closure is cited as a worked example of the audit chain
  working post-release.

### Tests

Test count: 380 (v0.9.1 ship state) -> 389 (v0.9.2). Net
delta: +9.

Breakdown:

- Type-compliance firing tests: +2
  (``test_d11_onnx_type_mismatch_fires_on_equal_float_op10``,
  ``test_d11_onnx_type_mismatch_fires_on_reshape_float_shape_op13``)
- Type-compliance silent-pass tests: +2
  (``test_d11_onnx_type_compliance_silent_pass_on_well_typed_equal_int64``,
  ``test_d11_onnx_type_compliance_silent_pass_on_well_typed_relu_float``)
- Parser tests: +2
  (``test_d11_onnx_type_mismatch_regex_matches_message``,
  ``test_d11_onnx_classifier_prefers_shape_mismatch_first``)
- Fallback test: +1
  (``test_d11_onnx_classifier_unparseable_returns_category``)
- Diagnostic-prose test: +1
  (``test_d11_onnx_type_mismatch_diagnosis_prose``)
- V0_9_2 surface snapshot: +1
  (``test_v0_9_2_onnx_adapter_surface_snapshot``)

Sum: 2 + 2 + 2 + 1 + 1 + 1 = +9 ✓

The ten v0.9.1 D11-onnx tests in
``tests/test_onnx_shape_coverage.py`` automatically become the
regression suite for the strict_mode + check_type combination
per Decision 1's "purely additive" property and round-32 MED-2
closure. Their three mock ``_raise`` functions accept
``**kwargs`` so they match the new flag combination without
behavioral change.

### Round-31 / 32 closure ledger

| Finding | Source | Severity | Closure |
| --- | --- | --- | --- |
| Gap 1 | v0.9.1 NeuroGolf evaluation | HIGH | Closed in v0.9.2 round 31 via Decisions 1-3 (check_type=True flag, ShapeCoverageDiagnostic.category split, _TYPE_MISMATCH_RE regex extension). Empirically verified zero regressions; four firing cases confirmed. |
| META: v0.9.1 missed check_type=True | round-31 audit-of-self | INFORMATIONAL | Acknowledged. The v0.9.1 round-29 design correctly identified strict-mode shape inference as canonical for shape mismatches; check_type was not considered because the round-29 empirical probes focused on shape, not type. The post-release NeuroGolf evaluation surfaced the gap; v0.9.2 closes it. The framework's reciprocal contract working as designed: substrate (NeuroGolf bug class) governs surface (v0.9.2 spec). |
| Gap 2 | v0.9.1 NeuroGolf evaluation | MEDIUM | Scheduled for v0.9.3 per Decision 9. Tracked in ### Deferred section. |
| Gap 3 | v0.9.1 NeuroGolf evaluation | MEDIUM | Held until NeuroGolf provides a tight spec. Tracked in ### Deferred section. |
| Gap 4 | round-32 leverage analysis | HIGH (competition lever) | Scheduled for v0.9.4 per Decision 9. The dominant-failure-mode catch; alone catches ~4 historical sessions and likely prevents ~5-7 future ones. |
| Round-32 MED-1: "purely additive" framing wrong for frozen dataclass | round-32 audit | MEDIUM | §3.1 wording corrected: additive for consumers, breaking for constructors. ``category`` kept required (no default) per round-30 fail-fast. The only construction site is ``check_shape_coverage``, updated atomically. |
| Round-32 MED-2: regression test count duplicated v0.9.1 | round-32 audit | MEDIUM | Test math reduced from +12 to +9. The v0.9.1 D11-onnx tests automatically become the regression suite via the ``check_shape_coverage`` entry point; the v0.9.2 change is at the call site inside that function. The three mock ``_raise`` functions updated to accept ``**kwargs``. |
| Round-32 LOW: Q1/Q2 strategic decisions left open | round-32 audit | LOW | §1 gains Decisions 8 and 9 locking v1.3-tracks-v0.9.2 and the v0.9.x competition-leverage sequence (v0.9.2 type-compliance, v0.9.3 score-validity, v0.9.4 numpy-vs-ONNX divergence). |

Eight closures (1 HIGH closed in v0.9.2, 1 INFORMATIONAL, 2 deferrals tracked, 1 NEW HIGH scheduled for v0.9.4, 3 round-32 audit findings) plus the integration-items tracking from the NeuroGolf evaluation noted as out-of-scope deployment-side use cases.

## [0.9.1] - 2026-05-04

D11-onnx (shape-coverage on ONNX edges) ships, deferred from
v0.9.0 per Decision 3 of that prompt. Implementation per Decision
1 of the v0.9.1 prompt: catch
``onnx.shape_inference.InferenceError`` raised by
``infer_shapes(model_proto, strict_mode=True)`` and parse the
per-op diagnostic into structural-honesty findings. Strict-mode
is the canonical ONNX mechanism for catching declared-vs-inferred
shape disagreement; it uses ONNX's own per-op shape rules and
silent-passes on broadcast / dim_param / empty dim_value
(Decision 3).

Closes round-24 finding M3 deferral. Closes the v0.9.0 META
observation that ``make_shape_mismatch_d11_deferred_model()`` did
not actually contain a mismatch (the builder shipped a clean
Relu->Identity chain whose docstring claimed an "obvious shape
mismatch on an internal edge"; the v0.9.0 pinning test was
passing for the wrong reason). v0.9.1 fixes the builder as part
of the retirement (Decision 4).

### Fixed

- ``make_shape_mismatch_d11_deferred_model()`` in
  ``tests/fixtures/onnx/builders.py``: replaced the clean
  Relu->Identity chain with a Concat([1,10], [1,10], axis=1)
  whose declared output is [1,10] (actual is [1,20]).
  ``onnx.shape_inference.infer_shapes(..., strict_mode=True)``
  now correctly raises ``InferenceError`` on this fixture, which
  is what the v0.9.0 docstring already claimed and what the
  v0.9.1 D11-onnx checker needs to fire on. Round-30 META
  observation closure.
- ``check_onnx_module`` signature: ``model_proto`` is a required
  positional parameter (Decision 2 / round-30 MED-2 closure).
  The fail-fast discipline favors a ``TypeError`` on a missing
  argument over a silent-skip protected by a ``model_proto=None``
  default; the single existing call site (``cli._check_onnx_file``)
  is updated in the same commit. ``check_onnx_module`` is
  internal API (not exported), so the signature change is
  source-compatible for external callers and refactor-only for
  the package itself.
- CLI PASS message for ``.onnx`` files: now says
  "3 structural checks ran (D24-onnx all-paths-emit,
  opset-compliance, D11-onnx shape-coverage)" (was "2 structural
  checks").

### Added

- ``src/furqan_lint/onnx_adapter/shape_coverage.py``:
  ``ShapeCoverageDiagnostic`` dataclass (with ``error_kind``
  field per Decision 6 / round-30 m2 forensic-detail closure)
  and ``check_shape_coverage(model_proto)`` entry point that
  yields one diagnostic per per-op mismatch parsed from the
  InferenceError message. Falls back to a single generic finding
  if the message format is unparseable (defensive against future
  onnx releases).
- ``ShapeCoverageDiagnostic`` and ``check_shape_coverage`` added
  to ``furqan_lint.onnx_adapter.__all__`` and pinned in the
  ``ONNX_ADAPTER_PUBLIC_SURFACE_v0_9_1`` baseline (v0.9.0
  baseline + 2 new names).
- ``tests/fixtures/onnx/builders.py::make_dim_param_passthrough_model``:
  builder for the dynamic-shape silent-pass pin.
- ``dynamic_shape_silent_pass`` documented-limit fixture with
  full four-place documentation (CHANGELOG / fixture /
  pinning test / README): records that strict-mode
  silent-passes on dim_param (symbolic) and empty dim_value
  (dynamic) shapes per Decision 3.

### Changed

- ``check_onnx_module(module, model_proto)`` runs three checkers
  in order: ``all_paths_emit`` (D24-onnx, v0.9.0),
  ``opset_compliance`` (v0.9.0), ``shape_coverage`` (D11-onnx,
  v0.9.1). The new tuple shape ``("shape_coverage", d)`` is
  populated; the slot was reserved in v0.9.0's runner docstring.
- ``cli._check_onnx_file``: passes ``model`` (already in scope
  from ``parse_model(path)``) to ``check_onnx_module``.
- README "ONNX support (opt-in)" section updated to name
  D11-onnx via strict-mode shape inference; the deferral prose
  is removed. The "ONNX adapter (current as of v0.9.0)" section
  is bumped to v0.9.1 and the ``dynamic_shape_silent_pass``
  documented limit replaces the now-retired
  ``shape_coverage_deferred`` entry.
- ``tests/fixtures/onnx/documented_limits/README.md``: inventory
  reflects the v0.9.1 state with a "## Retired" section naming
  the ``shape_coverage_deferred`` deletion.

### Retired

- ``tests/fixtures/onnx/documented_limits/shape_coverage_deferred.py``
  fixture: deleted in commit 4. The deferral entry is no longer
  load-bearing because v0.9.1 ships D11-onnx.
- ``tests/test_onnx_public_surface_additive.py::test_onnx_d11_deferred_v0_9_0_passes``
  pinning test: skipped in commit 2 (kept the suite green at
  the commit boundary), deleted in commit 4 (removed the
  function body entirely). Per Decision 4 (delete-plus-add
  discipline; round-30 MED-1 closure), the test is deleted
  rather than renamed; the v0.9.1 firing test
  ``test_d11_onnx_fires_on_shape_mismatch`` (in
  ``tests/test_onnx_shape_coverage.py``) is the four-place
  pinning-test slot for the new behavior. Deletion plus
  addition reads more clearly in the retirement-ledger
  discipline than a single rename would.

### Tests

Test count: 370 (v0.9.0 ship state) -> 380 (v0.9.1). Net
delta: +10.

Breakdown:

- D11-onnx checker tests: +5
  (``test_d11_onnx_fires_on_shape_mismatch``,
  ``test_d11_onnx_clean_when_shapes_match``,
  ``test_d11_onnx_clean_on_broadcast_compatible``,
  ``test_d11_onnx_silent_pass_on_dim_param``,
  ``test_d11_onnx_silent_pass_on_negative_dim``)
- Diagnostic parser tests: +3
  (``test_d11_onnx_parser_handles_single_op_message``,
  ``test_d11_onnx_parser_handles_multi_op_message``,
  ``test_d11_onnx_parser_unparseable_fallback``)
- Runner integration: +1
  (``test_d11_onnx_runner_alongside_d24_and_opset``)
- v0.9.0 pin retirement: -1
  (``test_onnx_d11_deferred_v0_9_0_passes`` deleted)
- v0.9.1 dynamic-shape pin: +1
  (``test_d11_onnx_dynamic_shape_silent_pass_pin``)
- V0_9_1 surface snapshot: +1
  (``test_v0_9_1_onnx_adapter_surface_snapshot``)

Sum: 5 + 3 + 1 - 1 + 1 + 1 = +10 ✓

### Round-30 closure ledger

| Finding | Severity | Closure |
| --- | --- | --- |
| MED-1: rename obscures retirement-ledger discipline | MEDIUM | Decision 4 reframed as delete-plus-add pair. Commit 4 deletes ``test_onnx_d11_deferred_v0_9_0_passes`` outright (not rename); ``test_d11_onnx_fires_on_shape_mismatch`` lands in commit 3 as a fresh test on the now-correct builder. CHANGELOG retirement section names both deletions. |
| MED-2: ``model_proto=None`` default introduces silent-skip risk | MEDIUM | Decision 2 reframed as required positional parameter. Calling ``check_onnx_module(module)`` raises ``TypeError`` (asserted by ``test_d11_onnx_runner_alongside_d24_and_opset``). The single call site (``cli._check_onnx_file``) is updated in the same commit. |
| m1: commit hash unstable across pulls | MINOR | Branch base named as ``tag v0.9.0`` rather than commit hash. |
| m2: ``error_kind`` field dropped from ShapeCoverageDiagnostic | MINOR | Decision 6 adds it back; populated from the regex's ``kind`` group at zero implementation cost. Forensic detail preserved. |
| m3: test rename + skip during multi-commit refactor | MINOR | Commit 2 adds ``@pytest.mark.skip`` on the v0.9.0 pin (suite stays green at every commit boundary); commit 4 does the deletion together with the fixture retirement. |
| m4: "no numpy" rule lacks upstream provenance | MINOR | §6 Standing Rule amended to name the round-28-to-round-29 lineage (strict_mode handles broadcasting natively, eliminating the round-28 numpy-reference reimplementation). |
| Q1: onnx 1.18.0 vs round-26 1.21.0 verification | QUESTION | §2 pre-implementation re-runs registry-anchor checks against the installed onnx version (sandbox: 1.17.0; matrix: 1.14-1.21 stable). The four anchors (Relu@14, BitShift@10/11, Trilu@13/14, Equal@7/14) hold across the pin range. |
| META: fixture-builder bug shape ungated | INFORMATIONAL | Audit-of-self spot-check during v0.9.1 cycle: sampled one fixture per language (Python aliased_optional_import, Rust trait_object_return, Go r3_compile_rejected, ONNX intermediates_excluded). All four correctly demonstrate their limits. The ``shape_coverage_deferred`` bug was specific to that fixture (docstring claimed mismatch but builder was clean), not a systemic shape across the 21 documented-limit fixtures. Future cycles can deepen the audit-of-self to all 21 fixtures empirically. |

7 findings closed (2 MEDIUM, 4 MINOR, 1 QUESTION). 1 META observation noted with audit-of-self spot-check completed for v0.9.1.

## [0.9.0] - 2026-05-04

ONNX adapter release. Extends structural-honesty diagnostics to
ONNX computational graphs as a parallel diagnostic family
(D24-onnx all-paths-emit + opset-compliance with pinned op
registry); this is honest divergence from the Python / Rust /
Go checker pipeline, not an instance of the existing
``check_d24`` / ``check_status_coverage`` checkers operating
on a unified IR. Closes 17 valid findings across rounds 24
and 25 (13 from round-24 prompt audit combining Bilal and
Grok review; 4 from round-25 corrections audit). See
round-24 / 25 closure ledger below.

### Fixed

- Round-24 finding C2 (CRITICAL): the directory walker
  hardcoded ``{".py", ".rs", ".go"}`` as its suffix set at one
  site and a "No .py or .rs files found" error message at
  another (the message bug-stale since v0.8.0 when ``.go``
  landed). The walker silently dropped any future adapter's
  files. v0.9.0 introduces ``_SUPPORTED_EXTENSIONS`` as the
  single source of truth in ``cli.py``; the error message
  derives from the same constant, so future adapters cannot
  reintroduce drift. Pinned by
  ``test_onnx_files_walked_in_directory_check``.
- Round-24 finding M1 (MAJOR): ``onnx.checker.check_model()``
  conflates parse failure with semantic-validity failure and
  overlaps with diagnostics that furqan-lint's own checkers
  ship to detect. Decision 1 of the v0.9.0 prompt drops the
  ``check_model()`` call from ``parse_model``; furqan-lint's
  own checkers are the authoritative source for ONNX semantic
  validity. Documented in
  ``src/furqan_lint/onnx_adapter/parser.py`` and
  ``src/furqan_lint/onnx_adapter/__init__.py``.
- Round-24 finding M2 (MAJOR): opset-compliance had no
  specified op-registry source or version pin. Decision 4
  specifies ``onnx.defs`` from the pinned ``onnx>=1.14,<1.19``
  package; the pin is enforced by
  ``test_opset_registry_version_pinned``. The pin is documented
  as a four-place limit at
  ``tests/fixtures/onnx/documented_limits/registry_pin_window.py``.
- Round-24 finding m1 (MINOR): the diff-dispatcher Guard
  ordering was not pinned. Guard 4 (``.onnx``) is now inserted
  after Guard 3 (``.go``) and before the Python default in
  ``_check_additive``. Guard ordering is pinned in the helper's
  docstring.
- Round-24 finding m5 (MINOR): the containment gate assertion
  was underspecified. Gate 8c
  (``test_gate_8c_onnx_containment``) uses an exact AST scan
  via ``ast.Import`` / ``ast.ImportFrom``, not a naive grep,
  so prose mentions of ``onnx`` in comments / docstrings do
  not false-fire.
- Round-25 HIGH-Fix-1: the round-24 first revision of this
  prompt attempted to consolidate the CHANGELOG entry into the
  release commit (single-commit landing). The round-25 audit
  verified that the CHANGELOG-math gate
  (``tests/test_changelog_math_gate.py`` lines 54-82) actively
  requires the placeholder pattern via its ``<TBD>`` /
  ``<DATE>`` skip logic. Without commit 1's placeholder,
  commits 2-6 would compare the growing pytest --collect-only
  count against the v0.8.5 entry's 347 figure and fail on
  every intermediate commit. The project's existing convention
  is correct; the deviation was a framework-mechanics error.

### Added

- ONNX adapter at ``src/furqan_lint/onnx_adapter/``: parser
  (``parse_model``), translator (``OnnxModule`` + companions),
  runner (``check_all_paths_emit`` + ``check_opset_compliance``
  + ``check_onnx_module``), public-name extractor
  (``extract_public_names``), CLI dispatch
  (``_check_onnx_file`` + ``_check_onnx_additive``).
  Symmetric with ``rust_adapter`` and ``go_adapter``: the
  ``onnx`` package is imported lazily; the [onnx] extra gates
  the import; the typed ``OnnxExtrasNotInstalled`` exception
  carries the install hint.
- ``[onnx]`` pip extra pulling ``onnx>=1.14,<1.19`` (Decision 6).
  Upper bound is load-bearing per Decision 4: the ONNX op
  registry retroactively adds operators across ``onnx`` package
  releases, so an unpinned upper bound would silently change
  what counts as e.g. opset 11.
- D24-onnx (all-paths-emit, Decision 2): every declared output
  in ``graph.output`` must be reachable on every dataflow path
  through If / Where branches. A declared output that no node
  produces and is not a graph input fires a finding.
- opset-compliance (Decision 4): every node's ``op_type`` must
  exist in the declared opset, looked up via
  ``onnx.defs.get_schema(..., max_inclusive_version=...)``
  from the pinned ``onnx>=1.14,<1.19`` registry.
- Additive-only diff on ``graph.input`` / ``graph.output``
  ValueInfo names + shapes formatted as ``input:NAME:SHAPE``
  and ``output:NAME:SHAPE`` (Decision 5). Intermediates
  (``graph.value_info``) and initializers
  (``graph.initializer``) are explicitly out of scope per
  round-24 finding m2 closure; the limit is documented at
  ``tests/fixtures/onnx/documented_limits/intermediates_excluded.py``.
- Three new gates in the v0.9.0 verification suite (now 17
  total): Gate 8c (ONNX containment via AST scan), Gate 9c
  (missing [onnx] extra raises ``OnnxExtrasNotInstalled``),
  and the CHANGELOG-math gate's v0.9.0 entry coverage.
- Surface snapshots for the new ``onnx_adapter`` subpackage:
  ``ONNX_ADAPTER_PUBLIC_SURFACE_v0_9_0`` pins 8 names
  (``BranchSummary``, ``NodeSummary``, ``OnnxExtrasNotInstalled``,
  ``OnnxModule``, ``OnnxParseError``, ``ValueInfoSummary``,
  ``extract_public_names``, ``parse_model``).
- Three documented-limit fixtures with full four-place
  documentation (CHANGELOG / fixture / pinning test / README):
  ``shape_coverage_deferred`` (D11-onnx deferred to v0.9.1 per
  Decision 3), ``intermediates_excluded`` (additive contract
  covers graph.input / graph.output only), and
  ``registry_pin_window`` (op-registry pin >=1.14,<1.19).
- ``_RENAME_HINT["onnx"]`` entry in
  ``src/furqan_lint/additive.py`` for the ONNX additive-diff
  user-visible rename hint prose.
- README "ONNX support (opt-in)" section and "ONNX adapter
  (current as of v0.9.0)" entry under Remaining limitations.

### Changed

- ``cli.py`` directory walker: hardcoded ``{".py", ".rs", ".go"}``
  suffix set + bug-stale "No .py or .rs files found" error
  message both replaced with derivations from
  ``_SUPPORTED_EXTENSIONS`` (single source of truth).
- ``cli.py`` ``_check_file`` dispatcher: ``.onnx`` route added
  after ``.go`` and before the Python default.
- ``cli.py`` ``_check_additive`` dispatcher: Guard 4 (``.onnx``)
  added after Guard 3 (``.go``) per round-24 finding m1.
- README install section: ``[onnx]`` row added; combined extras
  example updated to ``[rust,go,onnx]``.
- Four-place-completeness gate's ``_README_TOPIC_KEYWORDS``
  extended with three ONNX entries.

### Tests

Test count: 347 (v0.8.5 ship state on origin/main) -> 370
(v0.9.0). Net delta: +23.

Breakdown:

- Parser tests: +3 (``test_onnx_parser_loads_valid_model``,
  ``test_onnx_parser_raises_on_invalid_protobuf``,
  ``test_onnx_parser_raises_on_missing_extras``)
- Checker tests: +5 (``test_onnx_d24_fires_on_unreachable_output``,
  ``test_onnx_d24_clean_when_all_outputs_reachable``,
  ``test_onnx_opset_fires_on_future_op``,
  ``test_onnx_opset_clean_when_all_ops_in_declared_opset``,
  ``test_opset_registry_version_pinned``)
- Diff tests: +4 (``test_onnx_diff_fires_on_removed_output``,
  ``test_onnx_diff_fires_on_shape_change``,
  ``test_onnx_diff_clean_when_additive_only``,
  ``test_onnx_diff_cli_exits_1_on_removal``)
- CLI integration tests: +3 (``test_onnx_file_detected_by_extension``,
  ``test_onnx_cross_language_rejection``,
  ``test_onnx_files_walked_in_directory_check``)
- Surface snapshots: +3 (``test_v0_9_0_onnx_adapter_surface_snapshot``,
  ``test_v0_9_0_top_level_surface_snapshot``,
  ``test_v0_9_0_rust_go_baselines_unchanged``)
- Gate-level tests: +3 (``test_gate_8c_onnx_containment``,
  ``test_gate_9c_onnx_missing_extras``,
  ``test_gate_changelog_math_v0_9_0``)
- §8 documented-limit pinning tests: +2
  (``test_onnx_d11_deferred_v0_9_0_passes``,
  ``test_onnx_diff_intermediates_excluded``; the registry-pin
  pin is counted in the checker tests above)

### Out of scope (deferred to v0.9.1)

- D11-onnx (shape-coverage on ONNX edges); see Decision 3 and
  the four-place documented limit
  ``shape_coverage_deferred.py``.
- Channel-sum semantic analysis, input-mask consistency,
  file-size advisory gate, score-validity gate,
  numpy-vs-ONNX divergence detection. All require their own
  design rounds given the substrate-specific failure modes
  they would surface.

### Round-24 / 25 closure ledger

| Finding | Source | Severity | Closure |
| --- | --- | --- | --- |
| C1 | Bilal | CRITICAL | Framing note + runner.py docstring (parallel diagnostic family) |
| C2 | Bilal | CRITICAL | _SUPPORTED_EXTENSIONS + walker fix + ``test_onnx_files_walked_in_directory_check`` |
| M1 | Bilal | MAJOR | ``onnx.checker.check_model()`` not invoked; parser docstring + Decision 1 |
| M2 | Bilal | MAJOR | ``onnx.defs`` registry pin >=1.14,<1.19; ``test_opset_registry_version_pinned`` |
| M3 | Bilal | MAJOR | D11-onnx deferred to v0.9.1 (Decision 3) + four-place fixture ``shape_coverage_deferred`` |
| M4 | Bilal | MAJOR | §4 test count = 370 enforced by CHANGELOG-math gate |
| m1 | Bilal | MINOR | Guard 4 ordering pinned in ``_check_additive`` docstring |
| m2 | Bilal | MINOR | Decision 5 + four-place fixture ``intermediates_excluded`` |
| m3 | Bilal | MINOR | Decision 8: ONNX runner does not use ``_is_may_fail_producer`` |
| m4 | Bilal | MINOR | Reversed in round 25; placeholder commit pattern restored |
| m5 | Bilal | MINOR | Gate 8c uses ``ast.Import`` / ``ast.ImportFrom`` scan |
| Q1 | Bilal | QUESTION | Strategic rationale: extends structural honesty to non-source-code substrate |
| Q2 | Bilal | QUESTION | Decision 9: v1.2 papers Zenodo-restricted; v0.9.0 ships; v1.3 tracks v0.9.0 |
| Q3 | Bilal | QUESTION | ``tests/fixtures/onnx/builders.py``; no .onnx binaries committed |
| MED | Grok | MEDIUM | Subsumed by C2 closure |
| LOW1 | Grok | LOW | Verified against framework v3 source; not a defect |
| LOW2 | Grok | LOW | Declined; cosmetic |
| HEAD-1 | Grok | INVALID | Round 23 already used (v0.8.5 attribution-corrective) |
| HEAD-2 | Grok | INVALID | "Phase 2.5" has no substrate |
| Round-25 HIGH-Fix-1 | Round 25 | HIGH | Placeholder commit restored as commit 1 |
| Round-25 MEDIUM-Fix-2 | Round 25 | MEDIUM | Test count math reconciled to 370 |
| Round-25 MEDIUM-Fix-3 | Round 25 | MEDIUM | §9 checklist uses ``tmp_path`` programmatic construction |
| Round-25 LOW-Fix-4 | Round 25 | LOW | Q2 locked via Decision 9 in §1 |

## [0.8.5] - 2026-05-03

Documentation-only release. Single finding from the post-v0.8.4
review: the audit chain's CHANGELOG and source-code attribution
to "Fraz" as the auditor was imprecise. The framework is
Bilal-Fraz hybridized; the auditor role across all 22 prior
rounds has been Bilal. This release adds the attribution
discipline note (above) and sweeps source-code inline comments
where the round-N audit is the load-bearing fact and the
auditor name is not. Historical CHANGELOG sections are
preserved as-is per the immutability discipline.

### Fixed

- Source-code inline comments crediting "Fraz's round-N review"
  in ``src/furqan_lint/adapter.py`` (8 references) and
  ``src/furqan_lint/return_none.py`` (1 reference) swept to
  "round-N review" form. The round number is the load-bearing
  fact; the auditor attribution is dropped from inline comments.
- Test-file module docstrings in ``tests/test_round5_fixes.py``,
  ``tests/test_round6_fixes.py``, ``tests/test_round7_fixes.py``,
  ``tests/test_round8_fixes.py``, and
  ``tests/test_release_sweep_gate.py`` updated to use the
  going-forward attribution convention.

### Added

- Attribution discipline note at the top of CHANGELOG.md
  (above all release sections) explaining the framework's
  hybrid origin and the auditor role.
- Per-version baselines for v0.8.5 in the three additive-only
  surface snapshots (``tests/test_rust_public_surface_additive
  .py``, ``tests/test_go_public_surface_additive.py``,
  ``tests/test_top_level_public_surface_additive.py``). Each
  aliases the v0.8.4 baseline since v0.8.5 introduces no
  public surface change. Required by the section 7.6
  per-version cadence.

### Changed

- ``pyproject.toml`` authors list: no change. Both Bilal Syed
  Arfeen and Fraz Ashraf are preserved as co-authors of the
  framework. A clarifying comment above the authors block
  notes the role split (project lead and auditor vs. framework
  co-author).

### Out of scope (preserved as historical record)

- Existing ``## [0.2.0]`` through ``## [0.8.4]`` CHANGELOG
  sections are NOT edited. The audit chain's immutability
  discipline applies: prior release sections are historical
  record and remain in place verbatim.
- Existing commit subjects and bodies that mention "Fraz" are
  NOT rewritten. Git history is immutable on origin.

### Tests

Test count: 344 (v0.8.4 ship state on origin/main) -> 347
(v0.8.5). Net delta: +3.

The +3 delta is structural. Per the section 7.6 per-version
cadence, every minor and patch version ships a per-version
public-surface baseline pin in each of the three additive-only
surface snapshots (rust_adapter, go_adapter, top-level
furqan_lint). v0.8.5 introduces no Python public surface
change; each baseline aliases v0.8.4. The three new pin tests
assert that the corresponding ``__all__`` remains a superset
of its v0.8.5 baseline, anchoring v0.8.5 in the per-version
cadence required by section 7.6.

Aside from the structural cadence pins, this release
introduces no other tests: the attribution corrective is
entirely documentation-and-comment-text and adds no new
behavior to verify.

Note on baseline: the v0.8.5 prompt cited 338 as the v0.8.4
ship count and predicted a 0 delta for v0.8.5. The empirical
count on the merged v0.8.4 PR #10 included the v0.8.4 hotfix
tests (three per-version surface baseline pins for v0.8.4
plus one historical-untagged allowlist pin), bringing the
actual v0.8.4 ship count (pytest --collect-only) to 344;
v0.8.5 then adds three more per-version pins per the section
7.6 cadence, landing at 347.
Per the prompt's section 8 most-conservative-interpretation
rule, the empirical counts are used and the under-specification
is documented here.

The section 7.10 CHANGELOG-math gate verifies 347 - 344 = 3.

### Section 11.3 Five Questions

1. **What was added?** Attribution discipline note at the top
   of CHANGELOG.md.
2. **What was fixed?** Source-code and test-file inline
   attribution to "Fraz" swept to going-forward convention.
3. **What was retired?** The attribution-by-name-in-source-
   code pattern. Going-forward, source-code comments reference
   "round-N review" without naming the auditor inline.
4. **What did this release introduce as new limitations?**
   None.
5. **What is the empirical evidence the substrate behaves as
   claimed?** Pytest --collect-only reports 347 tests (344
   carried forward from v0.8.4 plus 3 new per-version surface
   baseline pins per the section 7.6 cadence); em-dash gate
   confirms no regression in the new content; ``git grep -n
   "Fraz" src/ tests/`` returns empty after commit 2.

### Section 5.1 Validator-bias self-disclosure

Bilal is the project lead and the auditor. This release is
Bilal-as-auditor surfacing a finding about how the audit
chain has attributed Bilal-as-auditor's work in its own
historical record. The structural-honesty thesis applies: the
project's CHANGELOG must accurately describe what the project
did, including who did the audits. Future audit reports
across the BayyinahEnterprise project trio (furqan,
furqan-lint, bayyinah-integrity-scanner) will use the
going-forward convention.

### Section 5.2 Prompt-grounding self-check log

Pytest collect-only count: 347 (344 carried forward from
v0.8.4 ship state on origin/main after PR #10 merge plus 3
new per-version surface baseline pins per the section 7.6
cadence). Delta: 347 - 344 = 3. CHANGELOG-math gate verified.
All verification gates pass: green.

## [0.8.4] - 2026-05-03

Corrective release. Round-22 found 1 LOW (Go ``extract_public_names``
docstring sweep) and 1 LOW (CLI PARSE ERROR diagnostic naming the
wrong filename on the failing side). Closes both plus lands three
automated gates (release-sweep extension for source-file
forward-references under section 7.5; extras-matrix gate under
section 7.11; origin-tag-presence smoke under section 7.12), the CI
matrix expansion to 14 jobs (sections 7.7 + 7.11), the PyPI Trusted
Publishing release workflow (section 7.10), three community files
(CONTRIBUTING + SECURITY + CODE_OF_CONDUCT), and a README install
section rewrite per locked decision 6. Per-version baselines aliased
to v0.8.3 (no public surface change in v0.8.4).

### Fixed

- **CLI PARSE ERROR diagnostic filename** (round-22 LOW). When
  ``_check_rust_additive`` or ``_check_go_additive`` caught a
  ``RustParseError`` / ``GoParseError`` raised by the new-side
  ``extract_public_names`` call, the printed PARSE ERROR diagnostic
  named the old-side filename (the one held in the loop variable at
  raise time), confusing operators trying to locate the broken file.
  The CLI now resolves the failing-side filename from the exception
  context and emits ``PARSE ERROR (rust|go): <kind> at line <N>``
  followed by ``  in <failing-side-path>``. Pinned by 2 new tests
  (one Rust old-side, one Rust new-side) under ``@pytestmark_rust``.

- **Stale forward-reference in ``rust_adapter.translator`` docstring**
  (caught by the new section-7.5 release-sweep extension on first
  run). The module docstring referenced ``deferred to v0.7.1 per
  documented_limits/empty_or_panic_only_body.rs``, but the R3
  zero-return checker shipped in v0.7.3 retired that fixture. Sweep
  removed the dangling pointer in the same commit that introduced
  the gate.

### Added

- **Section 7.5 release-sweep gate extension: source-file
  forward-references** (``tests/test_release_sweep_gate.py``). New
  ``test_no_forward_references_in_source_file_docstrings`` walks
  ``src/`` looking for ``\bfuture v(\d+)\.(\d+)`` and ``\bdeferred
  to v(\d+)\.(\d+)`` patterns whose target version is at or below
  the current ``pyproject.toml`` version, failing with the offending
  file + line + matched span. Self-test under ``tmp_path`` uses a
  contrived ``deferred to v9.9`` (above current) plus a stale ``v0.1``
  (below current) to exercise both directions.

- **Section 7.11 extras-matrix gate**
  (``tests/test_extras_matrix_gate.py``). AST-scans every test file
  that imports from ``furqan_lint.rust_adapter`` or
  ``furqan_lint.go_adapter``, asserting each test function carries
  one of the accepted skip-guard forms (``@pytestmark_rust`` /
  ``@pytestmark_go`` decorator, module-level ``pytestmark =
  pytest.mark.skipif``, ``pytest.importorskip``, inline
  ``pytest.skip``, or a fixture-injected ``rust_extras_available`` /
  ``go_extras_available`` parameter). Heuristic includes a
  name-based exemption for missing-extras-path tests (``missing_
  extras``, ``without_tree_sitter``, ``without_goast``,
  ``no_extras``, ``imports_without``) per locked reconciliation
  authority. 2 self-tests pin the negative + positive cases.

- **Section 7.12 origin-tag-presence script + smoke**
  (``scripts/verify_origin_tags.py`` +
  ``tests/test_origin_tag_presence_smoke.py``). Script extracts
  every ``## [X.Y.Z] - <date>`` header from CHANGELOG.md, excludes
  versions explicitly marked absorbed (e.g. v0.7.4 absorbed into
  v0.8.0), and verifies each remaining version has a corresponding
  ``v<X.Y.Z>`` tag at ``origin``. ``--dry-run`` prints the expected
  tag list without a network call; the smoke test pins the dry-run
  exit code, presence of v0.7.3 / v0.8.3 / v0.8.4, and absence of
  v0.7.4. The gate exempts the *current* ``pyproject.toml``
  version (tagged post-merge by design; release.yml keys on the
  tag-push event) and a small ``_HISTORICAL_UNTAGGED_VERSIONS``
  allowlist documented below.

  *Audit note (historical-untagged allowlist).* When the gate ran
  for the first time on PR #10, it surfaced two genuine origin-tag
  gaps predating this discipline: ``v0.2.0`` (rolled forward into
  v0.3.0 without a separate tag, pre-tag-discipline era) and
  ``v0.7.0`` (superseded by v0.7.0.1, the four-component
  corrective, before the v0.7.0 tag was pushed). Rather than
  silently masking the gap or rewriting history with synthetic
  tags from arbitrary commits, the script's
  ``_HISTORICAL_UNTAGGED_VERSIONS`` frozenset acknowledges the
  drift explicitly with per-entry comments. New (post-v0.8.4)
  versions are NOT eligible for this allowlist; the gate must
  catch them at PR time.

- **CI matrix expansion to 14 jobs** (``.github/workflows/ci.yml``).
  Five jobs: ``lint`` (ruff + mypy + em-dash + origin-tag-presence)
  and four test variants ``test-python-only`` / ``test-rust`` /
  ``test-go`` / ``test-full``, each crossed with Python 3.10 / 3.11
  / 3.12 / 3.13. The em-dash check moves from a separate job into
  the lint job and now extends to ``CHANGELOG.md`` + ``pyproject
  .toml`` (with ``--exclude=CODE_OF_CONDUCT.md`` so the Contributor
  Covenant verbatim text does not trip the gate). 4 new pin tests
  cover the matrix shape, the em-dash extension, the em-dash check
  living in the lint job, and the origin-tag-presence step.

- **PyPI Trusted Publishing release workflow**
  (``.github/workflows/release.yml``). Two-job split: ``build``
  (fetch-depth: 0, build sdist + wheel via ``python -m build``,
  verify the wheel filename ends ``-py3-none-any.whl``, assert
  merge-base ancestry against ``origin/main``, sync the version-tag
  + CHANGELOG version via ``tomllib`` from the standard library) +
  ``publish`` (``id-token: write`` permission, ``environment:
  pypi``, ``pypa/gh-action-pypi-publish@release/v1``). 3 new pin
  tests cover the build-then-publish ordering, the Trusted
  Publishing permission and environment, and the structural pins
  (fetch-depth, ancestry check, wheel-name verification).

- **Community files: CONTRIBUTING.md + SECURITY.md +
  CODE_OF_CONDUCT.md.** ``CONTRIBUTING.md`` (~130 lines) covers
  setup, the additive-only discipline, the verdict taxonomy, the
  release-prompt cadence, the co-author trailer requirement, and
  inline ~200-word reciprocal-contract terms (per locked decision 7
  the contract is included inline rather than linked). ``SECURITY
  .md`` lists supported versions, names
  ``doctordopemusic@gmail.com`` as the reporting channel, and
  commits to a 14-day initial-response window. ``CODE_OF_CONDUCT
  .md`` is the Contributor Covenant v2.1 verbatim, with the
  ``[INSERT CONTACT METHOD]`` placeholder replaced by
  ``doctordopemusic@gmail.com``.

- **README install section rewrite** (per locked decision 6). New
  structure: PyPI default first; "Optional adapters" listing all
  three install shapes (``pip install furqan-lint[rust]``, ``[go]``,
  ``[all]``); "Install from a specific commit or tag" with a v0.8.4
  worked example plus a release-history pointer; separate "Furqan
  dependency" subsection naming the ``furqan>=0.11.0`` runtime
  requirement plainly. README-drift gate continues to pass.

- **Per-version baselines for v0.8.4** in the three additive-only
  surface snapshots (``tests/test_rust_public_surface_additive.py``,
  ``tests/test_go_public_surface_additive.py``,
  ``tests/test_top_level_public_surface_additive.py``). Each
  aliases the v0.8.3 baseline since v0.8.4 introduces no public
  surface change.

### Changed

- **Em-dash check** moved from a standalone job into the ``lint``
  job and extended to scan ``CHANGELOG.md`` and ``pyproject.toml``
  in addition to the prior ``src/`` and ``tests/`` paths. Excludes
  ``CODE_OF_CONDUCT.md`` so the Contributor Covenant verbatim text
  is preserved as upstream-published.

### Tests

Delta: +13 net new passing tests. 325 baseline (323 pass + 2 skip)
→ 338 passed + 2 skipped = 340 collected.

Breakdown:
- +2 PARSE ERROR diagnostic pins (Rust old-side, Rust new-side)
  under ``@pytestmark_rust`` in ``tests/test_rust_correctness.py``.
- +1 section-7.5 release-sweep extension (production gate +
  self-test land together; the production gate is a search over
  ``src/`` returning empty on a clean tree, structurally pinned by
  the self-test under ``tmp_path``).
- +2 section-7.11 extras-matrix gate self-tests.
- +1 section-7.12 origin-tag-presence smoke.
- +4 commit-7 CI workflow pins (matrix shape, em-dash extension,
  em-dash placement, origin-tag-presence step).
- +3 commit-8 release workflow pins (job-ordering, Trusted
  Publishing permission/environment, structural pins).

## [0.8.3] - 2026-05-03

Corrective release. Round-21 found 1 HIGH (Rust diff parse-
error gate missing), 2 MEDIUM (goast IndexListExpr +
``extract_public_names`` docstring sweep), 2 LOW. Closes all
five plus lands two automated gates (CHANGELOG-math +
four-place-completeness). Per-version baselines added.

### Fixed

- **Rust diff parse-error gate** (round-21 HIGH).
  ``rust_adapter.public_names.extract_public_names`` now
  calls ``_assert_parses_cleanly`` after ``parse_source``,
  raising ``RustParseError`` on any tree-sitter recovered
  parse error. The CLI's ``_check_rust_additive`` already
  caught ``RustParseError`` and returned exit 2 with a PARSE
  ERROR diagnostic on stdout; the missing piece was the
  ``has_error`` check inside the diff path's name extractor.
  Prior to this commit, a malformed ``.rs`` file silently
  parsed to an empty public-name set, producing a false
  MARAD on every name from the well-formed side (or a false
  PASS when both sides were broken). Pinned by 5 new tests:
  2 unit (broken signature, truncated input) plus 3 CLI
  (parse error on old / new / both sides; the new-side test
  is discriminating, asserting absence of the v0.8.2 false
  MARAD).

- **goast ``IndexListExpr`` in ``receiverTypeName``**
  (round-21 MEDIUM, locked decision 2). Added two cases to
  the receiver-type extractor so multi-parameter generic
  receivers (``func (p Pair[K, V]) Get()`` and
  ``func (p *Pair[K, V]) Get()``) emit qualified method
  names ``Pair.Get`` instead of falling through to the
  empty-string default + bare ``Get``. The receiver-shape
  coverage matrix is now closed for the practical Go grammar
  surface (six shapes total). Pinned by 2 new tests
  (``test_qualified_method_value_receiver_multi_param_generic``
  + the pointer variant). Goast binary rebuilt; md5
  ``d7bf0679e814acf870b174391bd32f47``.

### Backfilled

- **``trait_object_return.rs`` pinning test** (v0.7.0 fixture
  had no test reference; surfaced by the four-place-
  completeness gate self-test).
- **``lifetime_param_return.rs`` pinning test** (same
  rationale).

### Added (gates)

- **``test_changelog_math_gate.py``** (2 tests): live gate
  + self-test. Parses the latest ``## [...]`` entry's
  ``### Tests`` block via the canonical regex; asserts
  (Y == empirical) AND (Y - X == Z). The first assertion
  would have caught the v0.8.1 drift (claimed 291, actual
  294); the second catches arithmetic errors anywhere.
  Placeholder handling (``<TBD>`` / ``<DATE>``) enables the
  in-flight release commit pattern.

- **``test_four_place_completeness_gate.py``** (1 test, single
  internal loop). For every fixture in
  ``tests/fixtures/<lang>/documented_limits/``, asserts the
  four-place documentation discipline: CHANGELOG mention by
  exact stem, ``documented_limits/README.md`` mention,
  test reference, top-level ``README.md`` topic-keyword
  mention. Legacy v0.8.0-era Go fixtures are explicitly
  allowlisted (CHANGELOG describes by topic-keyword instead
  of exact filename); allowlist is a v0.8.4 retirement
  candidate.

### Changed

- **README.md Rust adapter section** anchor updated:
  ``current as of v0.7.3`` -> ``current as of v0.8.3``.
- **``go_adapter/public_names.py`` docstring** swept: the
  forward-looking phrase ``a future v0.8.2 fix that emits
  qualified method names`` was replaced with the post-fact
  ``shipped in v0.8.2`` plus the impl-methods asymmetry
  note.

### Per-version baselines

- ``V0_8_3_SURFACE`` (top-level): alias of ``V0_7_0_SURFACE``.
- ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_8_3``: alias of v0.8.2.
- ``_GO_ADAPTER_PUBLIC_SURFACE_v0_8_3``: alias of v0.8.2.

None of the v0.8.3 changes touch a public Python surface.

### Out of scope (v0.8.4 candidates)

- Diff path's PARSE ERROR diagnostic prefix names
  ``new_path`` regardless of which side failed to parse.
- Retire the four-place-completeness gate's legacy Go
  allowlist.
- Rust impl-block method collection.
- Loosen CI em-dash gate to exempt Python docstrings.

### §11.3 Five Questions

1. **What's the riskiest assumption?** That the four-place
   gate's keyword map covers every limit's variations. Loud
   failure mode (gate names missing keyword candidates).
2. **Most reversible decision?** The legacy-Go allowlist;
   removing the nine entries forces v0.8.0-era CHANGELOG
   exact-stem updates (a v0.8.4 commit).
3. **What did we defer?** Nothing -- impl-block methods and
   diff PARSE ERROR prefix are deliberate v0.8.4 candidates.
4. **Most surprising?** The commit-order discipline (commit
   1 placeholder + commit 7 release populates math) prevents
   the gate from self-failing on intermediate commits.
5. **What changes the next prompt?** Add 'four-place gate
   self-test against current substrate' to §2 grounding so
   pre-existing gaps surface before the prompt's commit
   decomposition.

### §5.1 Validator-Bias Self-Disclosure

I am the producer + validator + reporter for the v0.8.3
series. Load-bearing claims for fresh-instance verification:

* Does ``_assert_parses_cleanly`` correctly raise
  ``RustParseError`` on every shape of tree-sitter
  recoverable parse error beyond the two pinned cases?
* Does the v0.8.3 commit-order discipline (placeholder
  header in commit 1) actually prevent self-failure across
  commits 2-6? Verifiable via ``git checkout`` per
  intermediate commit.
* Does the legacy allowlist cover exactly the v0.8.0-era Go
  fixtures (no more, no less)? An honest fresh-instance
  read should challenge whether each entry deserves to stay.

### §5.2 Prompt-Grounding Self-Check

§2 commands all returned the expected results before
implementation began:

* ``RustParseError`` class at line 110 of translator.py.
* ``_assert_parses_cleanly`` at line 188 of translator.py.
* ``public_names.py extract_public_names`` body verified;
  source_path convention used (no rebinding of ``path``).
* ``RustParseError`` already imported in cli.py.
* goast main.go ``receiverTypeName`` had 4 cases (the
  IndexListExpr fall-through was explicitly noted).
* documented_limits/README four-place description verified.
* Existing rust_correctness had NO ``documented`` /
  ``omit`` tests (surfaced the backfill gap).
* Baseline pytest 309.
* All ``PARSE ERROR`` diagnostics on stdout (not stderr).

### Limitations introduced

- **Rust ``extract_public_names`` omits impl-block methods.**
  The Rust additive-only diff path's name extractor walks
  only top-level CST root children; methods defined inside
  ``impl Type { ... }`` blocks are not collected in v0.8.3.
  Asymmetric with goast (which emits qualified method names
  like ``Counter.increment`` as of v0.8.2). Pinned as
  ``tests/fixtures/rust/documented_limits/impl_methods_omitted.rs``
  with the matching ``test_rust_extract_omits_impl_methods``
  pin in ``tests/test_rust_correctness.py``. Registered as a
  v0.8.4 candidate.

### Tests

Test count: 309 (v0.8.2) -> 325 (v0.8.3). Net delta: +16.

Per the §4 inventory: +5 (parse-error: 2 unit + 3 CLI) +2
(goast IndexListExpr) +1 (impl-methods pin) +2 (Rust
backfills) +2 (changelog-math gate + self-test) +1 (four-
place-completeness gate) +3 (per-version baselines) = +16.

The CHANGELOG-math gate enforces this empirically on every
future release.

## [0.8.2] - 2026-05-03

Feature release. Adds the Rust additive-only diff path
(``furqan-lint diff old.rs new.rs``) via a new
``rust_adapter.public_names.extract_public_names`` extractor
that walks the tree-sitter CST. Fixes the v0.8.1-documented
Go method-name conflation false-negative by emitting qualified
method names (``Counter.Foo``, ``Logger.Foo``) from the goast
binary across four receiver shapes (value, pointer, value
generic, pointer generic).

Two v0.8.1 documented limits retire: method-name conflation
(closed by the goast change) and Rust additive-only diff
not-implemented (closed by the new Rust diff helper). Two
v0.8.1 anticipatory pin tests flip with their contracts: the
unqualified-method-name pin in
``tests/test_go_diff.py`` becomes the qualified-method-name
pin; the Rust-not-implemented dispatcher test file
``tests/test_rust_diff_not_implemented.py`` is renamed to
``tests/test_cli_diff_dispatcher.py`` and its precedence
assertion is flipped from absence-of-not-impl-string to
absence-of-Rust-diff-verdict-prefix.

### Added

- **Rust additive-only diff.** ``furqan-lint diff old.rs new.rs``
  extracts ``pub`` item names from each file via tree-sitter
  CST walk and reports any names present in ``old`` and
  absent in ``new``. PASS (exit 0) on additive-only changes;
  MARAD (exit 1) on removals; PARSE ERROR (exit 2) on parse
  failure or missing extras. The diagnostic prose's
  ``minimal_fix`` uses ``pub use <new> as Name;`` re-export
  hints (Rust idiom).
- **``extract_public_names(path)``** in
  ``furqan_lint.rust_adapter`` (re-exported from
  ``rust_adapter.public_names``). Returns ``frozenset[str]``
  of unrestricted ``pub`` item names. Skips ``pub(crate)``,
  ``pub(super)``, ``pub(in path)`` per locked decision 2.
  Item kinds collected: function_item, struct_item, enum_item,
  const_item, static_item, type_item, mod_item per locked
  decision 3 (trait_item out of scope for v0.8.2). Methods
  inside ``impl`` blocks are NOT collected at the diff layer
  (mirrors how the v0.8.2 goast change moved Go method handling
  from collapse-by-name to qualify-at-emit; the Rust adapter
  takes the symmetric stance: methods are type-private, not
  name-collapsed).
- **``_check_rust_additive`` helper** in ``furqan_lint.cli``.
  Mirror of ``_check_go_additive`` minus the language tag.
  Catches ``RustExtrasNotInstalled`` (install hint, exit 1)
  and ``RustParseError`` (exit 2) per the v0.7.0.1 typed-
  exception pattern. Routes to ``compare_name_sets`` with
  ``language='rust'``.
- **goast qualified method-name emission.**
  ``cmd/goast/main.go`` adds a ``receiverTypeName`` helper
  handling four receiver shapes (value, pointer, value generic
  ``T[U]``, pointer generic ``*T[U]``). The
  ``collectPublicNames`` FuncDecl branch prepends
  ``Type.`` to the method name when the receiver is non-nil
  and ``receiverTypeName`` returns non-empty. Bare functions
  (no receiver) emit unchanged. Locked decision 4. Closes the
  v0.8.1 method-name conflation false-negative.
- **9 new tests** across three files:
  - ``test_rust_public_names.py`` (5): pub-only, pub(crate)
    skipped, frozenset return type, empty file, methods in
    impl blocks excluded.
  - ``test_rust_diff.py`` (4): PASS, MARAD, Rust rename hint
    prose, compare_name_sets with language='rust' direct unit.
  - ``test_goast_qualified_methods.py`` (3): all four receiver
    shapes pinned (value, pointer, value generic, pointer
    generic).

### Changed

- **CLI dispatcher Guard 2** routes ``.rs`` vs ``.rs`` to
  ``_check_rust_additive`` (was: exit 2 with the v0.8.1
  ``Rust diff not implemented`` stub). Cross-language guard
  (Guard 1) and Go guard (Guard 3) unchanged. Locked decision
  4 invariant preserved.
- **Go method-name emission shape.** Methods on receiver type
  ``T`` now emit as ``T.Method`` instead of bare ``Method``.
  Distinct methods on different receivers no longer collapse
  in ``public_names``.
- **``extract_public_names`` flip in test_go_diff.py.** The
  v0.8.1 anticipatory pin
  ``test_extract_public_names_includes_method_names_unqualified``
  was flipped to
  ``test_extract_public_names_includes_qualified_method_names``
  in v0.8.2 commit 3 (alongside the goast change that flipped
  the contract). Per the v0.8.1 docstring's "v0.8.2 will flip
  this assertion" note.

### Retired

- **Documented limit: method-name conflation in
  ``public_names``** (was v0.8.1). Closed by the goast change.
  Fixtures ``method_conflation_v1.go`` /
  ``method_conflation_v2.go`` deleted; pinning test
  ``test_go_diff_method_conflation_documented`` removed;
  README bullet removed. Replacement positive test:
  ``test_go_diff_method_conflation_now_detected`` in
  ``test_go_diff.py`` (uses ``tmp_path`` to avoid recreating
  documented-limit infrastructure for a closed limit).
- **Documented limit: Rust additive-only diff
  not-implemented** (was v0.8.1). Closed by
  ``_check_rust_additive``. Fixture
  ``diff_not_implemented.rs`` deleted; README bullet removed.
- **Test ``test_rust_diff_returns_exit_2_with_v0_8_2_schedule_message``**:
  retired inline in v0.8.2 commit 2 alongside the Rust diff
  wiring. Replacement positive verdict:
  ``test_rust_diff_additive_only_passes`` in
  ``test_rust_diff.py``.
- **File rename:** ``tests/test_rust_diff_not_implemented.py``
  -> ``tests/test_cli_diff_dispatcher.py`` via ``git mv``
  (history preserved). The two remaining tests (cross-
  language guard + its precedence pin) stay in the renamed
  file; the precedence test's name and assertion flip to
  reflect the v0.8.2 contract (Rust diff IS implemented; the
  cross-language guard precedence is now over a working
  helper, not a stub).

### Tests

Test count: 294 (v0.8.1) -> 305 (v0.8.2). Net delta: +11.
Per the §4 inventory: +9 new (5 rust_public_names + 4 rust_diff
+ 3 qualified_methods - 1 retired
test_rust_diff_returns_exit_2 - 1 retired
test_go_diff_method_conflation_documented + 1 added
test_go_diff_method_conflation_now_detected) + 3 per-version
baselines (Rust, Go, top-level) = +12; minus 1 absorbed via
the qualified-name flip (v0.8.1 unqualified pin replaced by
qualified pin, not duplicated) = +11.

### Note on v0.8.1 CHANGELOG math

The v0.8.1 entry's ``### Tests`` section reported ``test count:
268 (v0.8.0) -> 291 (v0.8.1). Net delta: +23.`` The actual
v0.8.1 baseline was **294**, not 291. Per the v0.7.4 corrective
pattern (CHANGELOG math drift caught in round-18), the v0.8.1
math is recorded here for the audit trail; the v0.8.1 entry
itself is preserved as written for historical fidelity. Future
runs should baseline against 294 (and v0.8.2 baselines against
305 here for v0.8.3 work).

### §11.3 Five Questions

1. **What's the riskiest assumption in this release?**
   That the four receiver shapes in goast's ``receiverTypeName``
   cover all compilable Go method-receiver forms. The
   IndexListExpr case (multi-parameter generics like
   ``func (c *T[U, V]) Foo()``) is NOT in the
   exhaustive switch; it falls through to the default empty-
   string return, which causes the method to fall back to its
   bare name (preserving v0.8.1 behavior in that case rather
   than dropping the method silently). A v0.8.3 follow-up
   could add IndexListExpr if a real-world consumer surfaces
   one.

2. **What's the most reversible decision?**
   The pub(crate) / pub(super) skip (locked decision 2). Three
   lines in ``_has_unrestricted_pub`` to expand. The most
   irreversible is the qualified method-name emission shape
   (``Type.Method``); changing it later breaks every CI pipeline
   that grepped diff output for the v0.8.2 form.

3. **What did we defer that we shouldn't have?**
   Nothing in this release. trait_item collection deferral
   (locked decision 3) is principled (the consumer use case is
   not yet concrete); IndexListExpr handling is the one
   incremental gap and it has a documented fall-back.

4. **What's the most surprising thing a fresh-instance
   reviewer should look for?**
   The renamed file ``tests/test_cli_diff_dispatcher.py``
   contains a precedence test whose negative-assertion form
   was flipped between v0.8.1 and v0.8.2 (was: absence of
   "Rust diff not implemented"; now: absence of any Rust
   diff verdict prefix). The invariant being pinned is
   identical (cross-language guard 1 must come before Rust
   guard 2); the falsifiability surface changed because the
   Rust path itself changed. A future regression that broke
   the guard ordering would still surface here.

5. **What did we learn that should change the next prompt?**
   The "flip an anticipatory pin in lockstep with the change
   that flips its contract" pattern saved a gate-failing
   intermediate state in commit 3. Future prompts should
   explicitly designate which commit lands which flip; the
   v0.8.2 prompt §3.4 batched the test flip into commit 4
   alongside the retirement, but the goast change in commit 3
   flipped the contract and required the test flip to ride
   along (otherwise commit 3 would have failed gate 1
   pytest). Recorded for future planning.

### §5.1 Validator-Bias Self-Disclosure

I am the producer + validator + reporter for the v0.8.2
series. Load-bearing fresh-instance review questions:

* Does ``extract_public_names`` correctly skip every form of
  restricted ``pub`` (crate, super, in path) AND collect every
  unrestricted ``pub`` for all 7 supported item kinds?
* Does ``receiverTypeName`` produce correct ``Type.Method``
  emission for all four receiver shapes? Does the empty-string
  fallback preserve v0.8.1 behavior for unanticipated shapes?
* Does the renamed ``test_cli_diff_dispatcher.py`` precedence
  test still falsify on a guard-reordering regression (e.g.
  if Guard 2 were moved before Guard 1, the test should
  fail)?
* Does the flipped Go-diff test
  ``test_extract_public_names_includes_qualified_method_names``
  correctly assert the v0.8.2 contract AND fail under the
  v0.8.1 unqualified emission (verifiable by reverting the
  goast change)?

### §5.2 Prompt-Grounding Self-Check

§2 commands all returned the expected results before
implementation began:

* ``parse_source`` exists in rust_adapter/parser.py (NOT
  ``parse_cst``).
* ``tree_sitter_languages`` is NOT a project dependency.
* The v0.8.1 anticipatory pin
  ``test_extract_public_names_includes_method_names_unqualified``
  exists in test_go_diff.py.
* ``method_conflation`` is referenced in
  go_adapter/public_names.py docstring.
* ``test_rust_diff_not_implemented.py`` has 3 tests.
* Baseline pytest: 294 (v0.8.1).

## [0.8.1] - 2026-05-03

Feature release. Adds the Go additive-only diff path
(``furqan-lint diff old.go new.go``), refactors the Phase-2
additive checker into a language-agnostic
``compare_name_sets`` helper plus a Python wrapper, adds a
cross-language rejection guard plus a Rust diff
not-implemented guard to the diff dispatcher, documents R3 as
not-applicable to Go, documents Go method-name conflation in
``public_names``, and ships per-version baseline constants for
the top-level, rust_adapter, and go_adapter surface snapshots.

This release also absorbed the v0.7.4 corrective items from
round-19's review of v0.8.0 (README Go section, Go
documented_limits scaffolding, v0.7.4 CHANGELOG entry).

### Added

- **Go additive-only diff.** ``furqan-lint diff old.go new.go``
  extracts uppercase-initial public names from each file via
  goast and reports any names present in ``old`` and absent in
  ``new``. PASS (exit 0) on additive-only changes; MARAD (exit
  1) on removals; PARSE ERROR (exit 2) on goast failure or
  missing extras. The diagnostic prose's ``minimal_fix`` is
  language-aware: Go users see ``var Name = <new>``
  re-export hints rather than Python alias syntax.
- **Cross-language rejection guard.** A ``foo.py`` vs
  ``bar.go`` (or any suffix mismatch) returns exit 2 with
  "Cross-language diff not supported. Old: '<s1>'; new:
  '<s2>'.". MUST evaluate FIRST in the dispatcher per locked
  decision 4 so a ``.py`` vs ``.rs`` pair surfaces
  "cross-language", not "Rust diff not implemented".
- **Rust diff not-implemented guard.** ``.rs`` vs ``.rs``
  returns exit 2 with "Rust diff not implemented in v0.8.1.
  See CHANGELOG for the v0.8.2 schedule." Locked decision 2:
  Rust diff is deferred to v0.8.2 because the Rust adapter
  does not yet extract public names (50-100 LoC of tree-sitter
  CST walking required).
- **``compare_name_sets(previous, current, filename, *,
  language="python")``** in ``furqan_lint.additive``.
  Language-agnostic public-name set diff. Operates on already-
  collected ``frozenset[str]`` inputs so the same body serves
  the Python, Go (now), and Rust (future) diff paths.
  Diagnostic prose dispatched via the module-private
  ``_RENAME_HINT`` map.
- **``extract_public_names(path)``** in
  ``furqan_lint.go_adapter`` (re-exported from
  ``go_adapter.public_names``). Returns
  ``frozenset[str]`` of uppercase-initial Go identifiers from
  ``path``. Used by the diff path. Method names are collected
  WITHOUT receiver-type qualification (documented limit; fixed
  in v0.8.2).
- **``_check_go_additive`` and ``_check_python_additive``
  helpers** in ``furqan_lint.cli``. The v0.8.0 monolithic
  ``_check_additive`` is now a 4-guard dispatcher routing to
  these helpers; ``_check_python_additive`` lifts the v0.8.0
  Python diff body verbatim (minus the obsolete Go-not-
  implemented guard).
- **Go documented_limits scaffolding** at
  ``tests/fixtures/go/documented_limits/``. README.md preamble
  parallels the Rust documented_limits style. 8 fixtures for
  v0.8.0 limits (3+ multi-return, non-error 2-tuple,
  for/switch/select/defer opaque, interface dispatch,
  generics) plus 3 fixtures for v0.8.1's new limits (R3
  not-applicable, method-name conflation v1/v2). Each fixture
  has a header comment describing the limit, when it was
  introduced, and the resolution path.
- **README Go support section.** Parallels the Rust support
  section. Describes v0.8.1's final shape: opt-in extra,
  D24 + D11, cross-language predicate, R3 not-applicable,
  additive-only diff with language-aware hints, cross-language
  rejection, method-name conflation as a known limit.
- **README Go adapter limitations subsection** with 11-bullet
  inventory matching documented_limits/README.md and the per-
  fixture pinning tests.
- **Per-version baselines.**
  ``_GO_ADAPTER_PUBLIC_SURFACE_v0_8_1`` =
  ``v0_8_0 | {"extract_public_names"}`` (grows by 1 name).
  ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_8_1`` aliases v0_7_0_1
  (no change in v0.8.1).
  ``V0_8_1_SURFACE`` aliases ``V0_7_0_SURFACE`` (no top-level
  change).
- **26 new tests** across six files:
  - ``test_compare_name_sets.py`` (2): language-aware hint
    dispatch, sorted diagnostic order.
  - ``test_go_diff.py`` (8): 5 CLI diff scenarios + 3
    extractor unit tests (uppercase-initials, frozenset return
    type, method-name unqualified pin).
  - ``test_rust_diff_not_implemented.py`` (3): cross-language
    rejection, cross-language precedence over Rust-not-impl,
    Rust pin via tmp_path.
  - ``test_go_documented_limits.py`` (10): 8 v0.8.0 limit
    pinning tests + R3 not-applicable (3-claim
    discriminating) + method-name conflation.
  - ``test_go_public_surface_additive.py`` (+1):
    test_go_adapter_public_surface_is_superset_of_v0_8_1_baseline.
  - ``test_rust_public_surface_additive.py`` (+1):
    test_rust_adapter_public_surface_is_superset_of_v0_8_1_baseline.
  - ``test_top_level_public_surface_additive.py`` (+1):
    test_v0_8_1_surface_is_subset_of_current.

### Changed

- **``check_additive_api``** in ``furqan_lint.additive`` now
  delegates to ``compare_name_sets`` after extracting both
  Python public-name sets via ``_extract_public_names``.
  Signature preserved exactly; external behavior is byte-for-
  byte identical for the Python diff path.
- **CLI dispatcher refactor.** ``_check_additive`` is now a
  4-guard dispatcher. Cross-language is guard 1, Rust is
  guard 2, Go is guard 3, Python is the default.

### Retired

- ``test_go_diff_returns_exit_2`` in ``tests/test_go_cli.py``
  retired and replaced with
  ``test_go_diff_now_implemented_returns_exit_0_on_clean_pair``.
  The v0.8.0 contract (exit 2 because not implemented) is
  satisfied differently in v0.8.1: the diff IS implemented, so
  the verdict reflects actual additive-only semantics. The
  retirement note in the new test's docstring makes the
  contract change visible.

### Tests

Test count: 268 (v0.8.0) -> 291 (v0.8.1). Net delta: +23.
Per the §4 inventory: 26 new tests, minus 1 retired
(test_go_diff_returns_exit_2 replaced by the now-implemented
verdict pin), minus 2 pre-existing tests that now skip when
[go] extras are missing (the pre-flight already had skipif
guards; the count delta accounts for the typical run with
extras present).

### §11.3 Five Questions

1. **What's the riskiest assumption in this release?**
   That ``frozenset(public_names)`` is the right collapse for
   the diff. The method-name conflation false-negative is a
   direct consequence of this choice. The v0.8.2 plan addresses
   it via qualified method-name emission in goast.

2. **What's the most reversible decision?**
   The cross-language rejection guard. Removing it (or
   reordering the guards) is a 5-line change. The most
   irreversible decision is the ``compare_name_sets``
   signature: changing it later would break Rust adapter
   work-in-progress that depends on the helper.

3. **What did we defer that we shouldn't have?**
   Nothing. Rust diff deferral is principled (50-100 LoC
   tree-sitter walking is real work); R3-for-Go deferral is
   predetermined (compiler rejects the firing condition);
   method-name conflation deferral is a single-commit follow-
   up planned for v0.8.2.

4. **What's the most surprising thing a fresh-instance
   reviewer should look for?**
   The dispatcher's guard-ordering test
   (test_cross_language_takes_precedence_over_rust_not_implemented)
   asserts a NEGATIVE: that 'Rust diff not implemented' does
   NOT appear in stdout for a .py-vs-.rs pair. Inverting the
   guards would silently violate this; the test pins the
   ordering invariant.

5. **What did we learn that should change the next prompt?**
   The 'switch-only-body false PASS' result discovered while
   building tests/test_go_documented_limits.py is a real Go
   adapter limit that wasn't on the v0.8.0 inventory. Worth
   adding to the v0.8.2 prompt's documented_limits review.

### §5.1 Validator-Bias Self-Disclosure

I am the producer + validator + reporter for the v0.8.1
series. The load-bearing fresh-instance review questions are:

* Does ``compare_name_sets`` produce identical output to the
  v0.8.0 ``check_additive_api`` for any Python diff input pair?
* Does the dispatcher's guard ordering correctly handle all
  six suffix-pair combinations (.py vs .py, .py vs .rs, .py vs
  .go, .rs vs .rs, .rs vs .go, .go vs .go)?
* Does ``extract_public_names`` collect every uppercase-initial
  Go identifier regardless of declaration kind, AND only those?
* Does the R3 not-applicable test's claim 3 (zero-return
  rejected by ``go build``) hold for all reasonable counter-
  examples (empty body, body with only side-effecting
  statements, etc.)?

### §5.2 Prompt-Grounding Self-Check

§2 commands all returned the expected results before
implementation began:

* additive.py imports ast and uses _extract_public_names
  (Python-bound).
* rust_adapter.parse_file does not surface a public_names
  attribute on Module (no Rust pub-name extraction).
* _check_python_additive / _check_go_additive don't exist
  (will be created in commit 2).
* Go documented_limits dir doesn't exist (will be created in
  commit 0).
* Method-conflation reproduces in goast: ['Counter', 'Logger',
  'Foo', 'Foo'] -> frozenset {Counter, Foo, Logger}.
* Baseline pytest: 268 (v0.8.0).

## [0.8.0] - 2026-05-03

Feature release. First non-Python language adapter ships: the
Go adapter (Phase 1) lints ``.go`` files for D24 (all-paths-
return) and D11 (status-coverage with the Go ``(T, error)``
firing shape). Cross-language ``_is_may_fail_producer``
predicate consolidated to Shape B per ADR-002 §10 Q3
follow-up. The Python adapter is unchanged.

This release builds on v0.7.3 plus the v0.7.4 corrective items
(round-18 audit findings, folded into commit 0 of this series).

### Added

- **Go adapter Phase 1.** ``furqan-lint check file.go`` runs D24
  (all-paths-return) and D11 (status-coverage with the
  ``(T, error)`` firing shape) on Go source. Install via
  ``pip install furqan-lint[go]``. The Go toolchain (1.21+) is
  required at install time (PEP 517 build hook compiles the
  goast binary); not at runtime.
- **goast binary** at ``src/furqan_lint/go_adapter/cmd/goast/main.go``
  (~250 LoC). Self-contained Go program that uses ``go/parser``
  and ``go/ast`` to emit a JSON representation of a Go source
  file's AST. JSON shape: filename, package, public_names,
  functions (each with name, line, col, exported,
  return_type_names, params, body_statements). Body statement
  types: ``if``, ``return``, ``assign``, ``opaque``. The binary
  has NO ``calls`` field; the Python translator extracts calls
  from ``rhs_call`` sites at IR build time per round-17
  prompt-review MEDIUM 1.
- **Python Go adapter** at ``src/furqan_lint/go_adapter/``:
  - ``__init__.py`` exports ``parse_file``,
    ``GoExtrasNotInstalled``, ``GoParseError``.
  - ``parser.py`` invokes the bundled goast binary as a
    subprocess with a 10-second timeout. Discovery order:
    bundled binary → ``FURQAN_LINT_GOAST_BIN`` env var → loud
    failure (NO ``$PATH`` fallback per round-17 prompt-review
    MEDIUM 2).
  - ``translator.py`` (~280 LoC) converts goast JSON to Furqan
    IR. Return-type translation rules: 0 → None; 1 → TypePath;
    2-with-error-last → UnionType (error in right arm by
    convention); 2-non-error → opaque TypePath; 3+ → opaque
    TypePath("<multi-return>") (Phase 1 documented limit). nil
    in any expression position → IdentExpr("__opaque__"), NOT
    "__none__" (per locked decision 5: avoid accidental
    cross-language firing of Python-only check_return_none).
  - ``runner.py`` wires D24 + D11 via upstream
    ``check_all_paths_return`` and ``check_status_coverage``
    with the cross-language ``_is_may_fail_producer`` predicate.
  - ``_build.py`` is the PEP 517 build hook that compiles the
    goast binary at install time. If Go is absent on the build
    machine, the hook prints a stderr note and exits cleanly so
    the wheel still builds; runtime then raises
    ``GoExtrasNotInstalled`` with the install hint.
- **Cross-language ``_is_may_fail_producer`` (Shape B).** Moved
  from ``rust_adapter/runner.py`` to ``furqan_lint/runner.py``
  and extended to recognize Python ``Optional[T]``, Rust
  ``Option<T>`` / ``Result<T, E>``, AND Go ``(T, error)``. Per
  ADR-002 §10 Q3 follow-up: the predicate composition is the
  right abstraction once three data points exist. The Rust
  adapter's runner now imports from ``furqan_lint.runner``
  rather than maintaining a parallel composition.
- **``_is_error_return`` predicate** in
  ``furqan_lint/runner.py``. Recognizes Go's ``(T, error)``
  return shape via UnionType where one arm has base ``"error"``.
  SYMMETRIC across arms (per locked decision 7) so a future
  translator change that reorders does not silently break D11.
- **``setup.py``** with a ``build_py`` subclass that calls the
  Go build hook before standard setuptools build.
- **``[go]`` extra** in pyproject.toml (marker-only; no PyPI
  dependencies; the Go binary is built at install time from
  bundled source). ``[tool.setuptools.package-data]`` ships the
  goast binary (when built) plus the Go source so subsequent
  installs can rebuild.
- **CLI dispatch on .go.** ``cli.py`` ``main()`` routes ``.go``
  to ``_check_go_file``. Mirrors the v0.7.0.1 Rust pattern:
  typed ``GoExtrasNotInstalled`` is caught and printed as a
  one-line install hint to stderr (NOT a Python traceback).
  ``_check_directory`` walks ``*.py``, ``*.rs``, AND ``*.go``.
  ``EXCLUDED_DIRS`` adds ``vendor`` (Go's equivalent of
  ``node_modules`` / ``target``).
- **furqan-lint diff foo.go bar.go returns exit 2** with
  explicit "Go diff is not implemented" message per locked
  decision 8 / round-17 prompt-review CRITICAL. Exit 0 = PASS in
  framework verdict semantics; CI pipelines invoking
  ``furqan-lint diff *.go`` must NOT silently treat the
  unimplemented case as PASS. Pinned by
  ``test_go_diff_returns_exit_2``.
- **Release-sweep gate extended to Go surfaces.** The v0.7.3
  ``test_release_sweep_gate.py`` ``_USER_VISIBLE_SURFACES`` now
  includes the four go_adapter Python modules and the Go
  documented_limits README. Phase numbering on Go adapter
  surfaces fails the gate the same way Rust adapter surfaces do.
- **9 new fixtures** in ``tests/fixtures/go/``:
  - ``clean/all_paths_return.go``, ``clean/error_propagated.go``,
    ``clean/error_handled_via_named_return.go``.
  - ``failing/missing_return.go``,
    ``failing/error_collapse_via_blank.go``,
    ``failing/error_collapse_via_panic.go``.
- **22 new tests** across four files:
  - ``test_go_parser.py`` (3): JSON shape, parse error, timeout.
  - ``test_go_translator.py`` (6): function translation,
    UnionType emission, "error in right arm" pin (load-bearing
    Go convention pin), nil → opaque marker (locked decision 5
    pin), 2-element non-error tuple opaque, 3+ multi-return
    documented limit.
  - ``test_go_correctness.py`` (9): D24 clean + missing +
    switch + for, D11 collapse-via-blank + collapse-via-panic +
    propagated + named-returns + predicate-partition (load-
    bearing pin against future name-based consolidation).
  - ``test_go_cli.py`` (3): .go extension dispatch, diff exit 2,
    missing-extras install hint.
- **Per-version surface snapshots extended.**
  ``tests/test_top_level_public_surface_additive.py`` gains
  ``V0_8_0_SURFACE`` (alias of ``V0_7_0_SURFACE``; no top-level
  surface change in v0.8.0).
  ``tests/test_rust_public_surface_additive.py`` gains
  ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_8_0`` (alias of v0.7.0.1; no
  rust_adapter surface change).
  NEW ``tests/test_go_public_surface_additive.py`` ships
  ``_GO_ADAPTER_PUBLIC_SURFACE_v0_8_0`` baseline as the first
  go_adapter snapshot: ``{parse_file, GoExtrasNotInstalled,
  GoParseError}``.

### Changed

- **Rust D11 producer predicate import.** ``rust_adapter/runner.py``
  now imports ``_is_may_fail_producer`` from ``furqan_lint.runner``
  instead of maintaining its own composition. The Rust D11 firing
  semantics are unchanged; only the predicate's home file moved.

### Out of scope (deferred to Phase 2 or beyond)

- R3 (zero-return) for Go. Go has no body-shape analogue to
  Rust's annotated-fn-with-empty-body pattern. The closest
  equivalent is ``log.Fatal()`` / ``os.Exit()`` which is a
  function call, not a body shape. Deferred until a concrete
  user-reported false negative motivates the design.
- ``(T, T, error)`` and other 3+-element multi-return shapes.
  UnionType IR is binary; documented limit (the translator
  emits opaque ``TypePath("<multi-return>")``).
- ``go/types`` integration. Type resolution requires
  ``go build`` or module-aware parsing; deferred.
- Cross-package symbol resolution.
- Generics, interface dispatch, method-receiver call-site
  analysis.
- Additive-only diff for Go (CLI dispatches but returns exit 2
  with the "not implemented" message).
- ``for`` / ``switch`` / ``select`` / ``defer`` body analysis
  beyond opaque markers.
- ``nil`` distinction (pointer vs slice vs interface vs map);
  all collapse to ``IdentExpr("__opaque__")``.

### Tests

- 268 passed (was 243 base after v0.7.4 corrective). Delta:
  +25 (3 parser + 6 translator + 9 correctness + 3 CLI + 2
  go_adapter surface + 1 rust_adapter v0.8.0 baseline + 1
  top-level v0.8.0 baseline).
- Marker counts: 199 unit + 68 integration + 1 network = 268.

### Verification

- All 10 gates pass (gate 7 em-dash audit run from clean state;
  gate 9b empirical missing-Go-extras simulated).
- Per-version snapshots in BOTH top-level AND adapter tests.
- Four-place pattern wired for the documented limits introduced.

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the new capability:**
   ```go
   package main
   func loadConfig(path string) (*Config, error) {
       return &Config{}, nil
   }
   func StartServer(path string) *Config {
       cfg, _ := loadConfig(path)
       return cfg
   }
   ```
   On v0.7.3: ``furqan-lint check x.go`` returns "Unknown
   command: check" or similar (no Go support). On v0.8.0:
   exit 1 with MARAD on ``StartServer`` naming ``loadConfig``
   as the may-fail producer whose error arm was discarded.

2. **Smallest input demonstrating the bug pre-fix:** the
   absence of any Go support is the "before" state; this
   release introduces it.

3. **What this release does NOT do:** see "Out of scope" above.

4. **New code paths:** ~250 LoC of Go (cmd/goast/main.go) +
   ~600 LoC of Python (go_adapter/) + ~85 LoC of CLI integration
   + ~30 LoC of setup.py + ~25 LoC of build hook + 9 fixtures +
   22 tests + per-version snapshots in three surface files.

5. **Limits retired and added:** none retired; 8 documented
   limits introduced (3+-element multi-return; no R3 for Go;
   no Go diff; no go/types; no generics; no method-receiver
   call-site; switch/for/select/defer opaque; nil distinctions).

### Validator-bias self-disclosure (per v0.7.0.1 §5.1 standing requirement)

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
$ /tmp/golocal/go/bin/go version
go version go1.21.13 linux/arm64
```

The Go toolchain was installed during this build via the
official tarball (apt-get unavailable without sudo on this
sandbox). Go is required only on the build machine; install
machines and runtime machines do not need Go.

**Gates run from a clean state:**

The release-sweep gate (commit 5 + v0.7.3 commit 3) was run
empirically and caught Phase numbering in the Go translator,
runner, and CLI diff message during this release's development.
All findings swept to durable phrasing.

The em-dash audit gate (gate 7) was run from the clean
post-commit-1 state; clean.

**Gates that could not be run from a clean state:**

Gate 6 air-gap (``unshare -n``) is unavailable in the build
sandbox without ``CAP_SYS_ADMIN``. Same posture as v0.7.0
through v0.7.3.

Gate 9b (empirical missing-Go-extras simulation) is verified
via the unit test ``test_go_missing_extras_prints_install_hint``
which mocks the ``GoExtrasNotInstalled`` raise inside
``parse_file`` and asserts the stderr message + exit 1 + no
traceback. Empirical simulation via ``rm -f
src/furqan_lint/go_adapter/bin/goast`` works the same way and
is the deploy-host's verification path.

### §5.2 prompt-grounding self-check (per v0.7.2 standing requirement)

The §2.1 self-check ran clean against v0.7.3 codebase state
before any code was written. The framing-verification step
caught one drift: the prompt named base hash ``2a80cb1`` which
does not resolve on origin; the actual v0.7.3 release tip is
``50e698c`` (origin/v0.7.3 branch HEAD; v0.7.3 had not merged
to origin/main at the time of this v0.8.0 work). Branched off
``50e698c``; v0.7.3 is expected to merge ahead of or alongside
v0.8.0's PR. No other drift.

The §0 (round-18 corrective) finding 1 (em-dash on v0.7.3 HEAD)
was already closed on origin/v0.7.3 by commit 50e698c
"fix(ci): strip em-dash from test_release_sweep_gate
docstring" before this v0.8.0 work began. Findings 2 and 3 land
in commit 0 of this series. The §0 framing was therefore
partially redundant (1 of 3 findings already closed); the
v0.7.4 corrective scope shrank from 3 items to 2.

## [0.7.4] - 2026-05-03 (absorbed into v0.8.0)

### Fixed

- Backfill ``V0_7_3_SURFACE`` constant in
  ``tests/test_top_level_public_surface_additive.py``. Round-18
  audit caught that v0.7.3's release commit body claimed the
  snapshot existed in both surface tests; only the rust_adapter
  test was extended.
- Correct CHANGELOG ``### Tests`` math for v0.7.3: actual delta
  is +6 (not +5); empirical pytest shows 242 (not 241).

### Note

This corrective was absorbed into v0.8.0's commit 0 rather than
shipping as a separate tag.

## [0.7.3] - 2026-05-03

Documentation-sweep corrective for the round-17 audit findings.
Five MEDIUMs in one equivalence class: v0.7.2's release-sweep
workflow updated CHANGELOG correctly but missed the user-facing
surfaces (README headings, README rationale text, source
docstrings, CLI PASS string, documented_limits/README preamble)
that referenced the prior version's Phase number. v0.7.3 sweeps
all of them, retires one redundant documented limit, and adds a
release-time pre-flight gate so the failure mode does not recur.

Per-finding commit decomposition (Bayyinah v1.2.3 pattern):

  1. doc(rust): comprehensive Phase-numbering sweep across
     user-facing surfaces (closes MEDIUMs 1, 2, 5 + Aux 1, 2, 3).
  2. retire(rust): macro_invocation_body documented_limit
     (consolidate into r3_panic_as_tail) (closes MEDIUMs 3, 4).
  3. chore(release): release-time sweep gate (Fraz round-17
     workflow addition; prevents recurrence).
  4. release v0.7.3 (this commit: version bump + CHANGELOG +
     V0_7_3_SURFACE).

### Fixed

- **Phase numbering swept from user-facing surfaces.** The CLI
  PASS string at ``cli.py:204`` no longer says "Rust Phase 2"
  on every clean check; it now says "(R3, D24, D11 with Option-
  and Result-aware status coverage)". The README ``Rust support``
  heading no longer says "Phase 1, opt-in"; the body paragraph
  now describes the v0.7.2 state (three checkers, the
  Option/Result-aware predicate, the dropped return_none_mismatch
  rationale). The README ``Remaining limitations`` Rust subsection
  heading is no longer anchored to "v0.7.0 Phase 1". Source-comment
  Phase references in ``rust_adapter/__init__.py``, ``runner.py``,
  ``translator.py``, ``edition.py``, and ``cli.py`` are swept to
  durable phrasing ("the current implementation", "a future phase").
  The ``documented_limits/README.md`` preamble no longer says
  "v0.7.0 Rust adapter (Phase 1: D24 + D11 only)".
- **CHANGELOG v0.7.2 entry "+4 net" math typo corrected to +7.**
  3 D11 tests + 1 dead-code regression + 3 surface-snapshot tests
  = +7 net. The original "+4 net" framing with parenthetical
  "(corrected count below)" hinted at the typo but the corrected
  count never landed in the line above; v0.7.3 corrects.
- **Stale "deferred to v0.7.1" framing in
  ``macro_invocation_body.rs`` retired.** The fixture's claim
  that the Rust analogue of R3 was deferred to v0.7.1 was
  historically inaccurate after v0.7.1 shipped R3; the comment
  was not updated when v0.7.1 landed. Fixture and bullet
  retired in commit 2 of this release.

### Limitations retired

- **``macro_invocation_body.rs``.** Was a v0.7.0 documented
  limit ("a function whose body is a single macro invocation
  is treated as opaque"). The limit was the same underlying
  R3-tail-expression behavior pinned by
  ``r3_panic_as_tail_expression.rs``: both pinned the v0.7.0
  R1 translator rule that synthesizes a ``ReturnStmt(opaque)``
  for any tail expression. Two fixtures pinned one limit, not
  two. Consolidated into ``r3_panic_as_tail_expression`` whose
  pinning test now parametrizes over the diverging-macro family
  (``panic!``, ``todo!``, ``unimplemented!``, ``unreachable!``).
  The README "Remaining limitations" section now has one bullet
  for this limit instead of two.

### Added

- **Release-time sweep gate** in
  ``tests/test_release_sweep_gate.py`` (Fraz round-17 workflow
  addition). Two tests:
  - ``test_no_phase_numbering_in_rust_user_surfaces``: greps
    for ``\bPhase \d+\b`` across README, the documented_limits
    README, ``cli.py``, and the four rust_adapter modules.
    Fails (with file:line:context findings) if any surface
    references "Phase N" numbering.
  - ``test_no_stale_version_anchored_claims_in_user_surfaces``:
    greps for ``\bv0.X.Y(.Z)?\s+(Rust adapter|Phase N)\b``
    across the same surfaces. Fails if any surface anchors
    a claim to a specific prior version.

  Verified empirically: temporarily reintroduced the v0.7.2
  "Rust Phase 2" PASS string to ``cli.py`` and ran the gate;
  it correctly fails with the offending line. Restored;
  passes again. The gate's discriminating power is pinned.

  The gate is intentionally narrow: CHANGELOG is excluded
  (audit trail), Python adapter modules are excluded for now
  (out of scope for this round-17 corrective), and source
  code that names specific implementation choices with
  version anchors ("v0.7.0 translator emits ...") is
  preserved as historical anchor. Future v0.7.x or v0.8 may
  broaden the gate scope.
- **Parametrized diverging-macro pinning test** in
  ``test_rust_correctness.py``:
  ``test_r3_silent_on_diverging_macros_as_tail_expression``
  exercises 4 cases (``panic!``, ``todo!``, ``unimplemented!``,
  ``unreachable!``) to lock the structural rule that R3 is
  grammar-and-macro-agnostic. Replaces the single-fixture pin
  for the consolidated limit.
- **Per-version surface snapshots extended.**
  ``tests/test_rust_public_surface_additive.py`` gains
  ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_3`` baseline (alias of
  ``v0_7_0_1``; no surface change in this corrective).
  ``tests/test_top_level_public_surface_additive.py`` gains
  ``V0_7_3_SURFACE`` (alias of ``V0_7_0_SURFACE``). Per
  Bayyinah Engineering Discipline Framework v2.0 §7.6
  per-version cadence.

### Tests

- 242 passed (was 236 in v0.7.2). Delta: +6 (4 parametrized
  diverging-macro + 2 release-sweep gate + 1 rust_adapter v0.7.3
  baseline subset - 1 retired macro_invocation_body pinning test;
  v0.7.4 corrective backfills the missing top-level v0.7.3
  baseline subset to bring net delta to +7).
- Marker counts: 192 unit + 49 integration + 1 network
  (network is also integration-marked) = 242.

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the new capability:**
   ``furqan-lint check tests/fixtures/rust/clean/simple_returning_fn.rs``
   On v0.7.2: PASS message says "Rust Phase 2: R3 + D24 + D11"
   (stale Phase number that contradicts the CHANGELOG which
   said v0.7.2 was Phase 3). On v0.7.3: PASS message says
   "R3, D24, D11 with Option- and Result-aware status coverage"
   (substantive checker description, no stale Phase numbering).

2. **Smallest input demonstrating the bug pre-fix:** same input
   on v0.7.2 prints Phase 2 even though v0.7.2 IS the release
   where Result-aware D11 landed. CHANGELOG said Phase 3; CLI
   said Phase 2; user saw the contradiction every clean check.

3. **What this release does NOT do:**
   (a) No Python adapter docstring sweep. The Python adapter's
       "Phase 1 / Phase 2" references describe Python-only
       semantics that pre-date the multi-language release model.
       Out of scope for this round-17 corrective; can be swept
       in a future v0.7.x release if Fraz flags them.
   (b) No source-code historical-anchor sweep. Statements like
       "v0.7.0 translator emits ..." are intentional historical
       references and are preserved.
   (c) No new checker behavior. Pure documentation sweep + one
       limit consolidation + one new release-time gate.
   (d) Does not retroactively gate prior releases (gate fires
       on v0.7.3+ surfaces only).

4. **New code paths:**
   ``tests/test_release_sweep_gate.py`` (~120 LoC, 2 tests +
   _USER_VISIBLE_SURFACES tuple + 2 regex patterns). 1
   parametrized test (4 cases) replacing 1 single-fixture
   test in ``test_rust_correctness.py``. Per-version snapshot
   baselines for v0.7.3 in both surface snapshot files.

5. **Limits retired and added:** retired
   ``macro_invocation_body.rs`` (consolidated into
   ``r3_panic_as_tail_expression.rs`` per the four-place
   pattern). Added: none.

### Validator-bias self-disclosure (per v0.7.0.1 §5.1 standing requirement)

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
```

Same posture as v0.7.1 / v0.7.2.

**Gates run from a clean state:**

Gate 9 (empirical missing-extras) was run AFTER ``pip
uninstall -y tree_sitter tree_sitter_rust``. Output matches
the v0.7.0.1 contract. The release-sweep gate (commit 3) is
empirically verified by the regression-introduction reproducer
documented in commit 3's body: temporarily reintroduce a
"Rust Phase 2" string and confirm the gate fires.

**Gates that could not be run from a clean state:**

Air-gap (``unshare -n``) was attempted but the build sandbox
lacks ``CAP_SYS_ADMIN`` to namespace-isolate. Verifiable on
the deploy host; same posture as v0.7.0 / v0.7.0.1 / v0.7.1
/ v0.7.2.

## [0.7.2] - 2026-05-03

Feature release. Phase 3 of the Rust adapter, scope-narrowed
from the round-15 prompt per a round-16 pre-implementation
critique. Result-aware D11 lands; the planned Rust analogue of
return_none_mismatch is dropped because the §5.2 prompt-grounding
self-check empirically demonstrated that the firing condition
(non-Optional return type paired with `__none__` in body) is
unreachable on any source ``rustc`` accepts. The translator
delta and the ``check_return_none`` wiring would have shipped
infrastructure for a check with no job; deferred to whichever
later phase introduces an actual consumer for ``__none__`` in
Rust IR.

The dead-code removal originally specified in the prompt's §3.4
(``_d24_diagnostic_in_r3_set``) was already resolved in v0.6.1
(commit b0a4b18). v0.7.2 ships a forward-compat regression test
asserting the function does not exist anywhere under ``src/``,
preventing accidental re-introduction.

Full blocker rationale: ``/tmp/rust_phase_3_blocker.md`` (not
shipped; archived in the discussion record).

### Added

- **Result-aware D11 producer predicate** in
  ``src/furqan_lint/rust_adapter/runner.py``. Two new functions:
  - ``_is_result_type(rt) -> bool``: True iff ``rt`` is a Rust
    ``Result<T, E>`` (translated to a ``UnionType`` where neither
    arm has base ``"None"``). Distinguished from ``Option<T>`` by
    the structural rule, not by an annotation-text heuristic; the
    v0.7.0 translator already produces unambiguous IR shapes.
  - ``_is_may_fail_producer(rt) -> bool``: True iff
    ``_is_optional_union(rt) or _is_result_type(rt)``. The two
    predicates partition the may-fail-producer space cleanly.
- **D11 wiring updated** to pass
  ``producer_predicate=_is_may_fail_producer`` to
  ``check_status_coverage``, replacing the v0.7.1 wiring with
  ``_is_optional_union`` only. A caller declaring a concrete return
  type but invoking a Result-returning helper is now flagged the
  same way as one invoking an Option-returning helper.
- **2 new fixtures**: ``failing/result_collapse.rs`` (Result-
  returning helper, caller declares -> i32, panics on Err arm),
  ``clean/result_propagated.rs`` (helper + caller both declare
  ``Result<T, E>``, ?-operator propagation).
- **3 new tests** in ``tests/test_rust_correctness.py`` covering
  Result-collapse fires D11, Result-propagation does not fire,
  and ``_is_result_type`` does not match Option (predicate
  partition pin).
- **Forward-compat regression test** in
  ``tests/test_v0_7_2_dead_code_regression.py`` asserting
  ``_d24_diagnostic_in_r3_set`` does not exist under ``src/``.
  The function was a defensive D24-suppression helper added in
  v0.6.0 that turned out to be dead code; removed in v0.6.1
  (commit b0a4b18) but listed in the round-13 audit notes that
  the v0.7.2 prompt was drafted from. The regression test is
  cheap insurance against re-introduction.
- **Per-version surface snapshots extended.**
  ``tests/test_rust_public_surface_additive.py`` gains
  ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_1`` and ``_v0_7_2``
  baselines (both alias of ``v0_7_0_1``; no surface change in
  either release). ``tests/test_top_level_public_surface_additive.py``
  gains ``V0_7_2_SURFACE`` (alias of ``V0_7_0_SURFACE``). Per
  Bayyinah Engineering Discipline Framework v2.0 §7.6
  per-version cadence.

### Changed

- **Rust D11 producer predicate** at
  ``rust_adapter/runner.py``: from ``_is_optional_union`` to
  ``_is_may_fail_producer``. The wiring point and the D11
  invocation order are unchanged; only the predicate widens.
- **Module docstring** at ``rust_adapter/runner.py`` updated to
  document the v0.7.2 predicate change and the Shape A
  rationale (separate ``_is_result_type``, not a generalised
  ``_is_may_fail_producer`` across Python and Rust). Shape B
  generalisation deferred to whichever release introduces the
  Go adapter and clarifies whether Go's error-return shape fits
  the same abstraction.

### Out of scope (deferred to a later phase)

- **Rust analogue of return_none_mismatch.** Dropped per the
  round-16 critique: the firing condition ``-> non-Optional
  type AND body returns None`` is unreachable on any compilable
  Rust source (rustc rejects ``fn f() -> i32 { None }`` at
  compile time). The translator delta to emit
  ``IdentExpr(name="__none__")`` for Rust ``None`` literals
  would have shipped infrastructure with no consumer. If a
  future release introduces a Rust check with a different
  firing condition (e.g., "Option-returning function whose
  every path returns None" - a real code smell distinct from
  return_none_mismatch), the translator delta lands then.
- **Macro-expansion-aware analyses.** Phase 4+.
- **Cross-file Rust symbol resolution.** Phase 4+.
- **Cargo workspace traversal beyond nearest Cargo.toml.** Phase 4+.
- **Shape B (a single ``_is_may_fail_producer``
  generalisation across Python and Rust).** Deferred until the
  Go adapter lands and clarifies whether Go's
  ``(T, error)``-shape fits the same abstraction.

### Tests

- 236 passed (was 229 in v0.7.1). Delta: +7 (3 new D11 tests +
  1 dead-code regression test + 3 new surface-snapshot tests).
  v0.7.2's release commit message originally said "+4 net"; the
  v0.7.3 documentation sweep corrected it to +7. The 3 surface
  tests are real test functions (not just snapshot baselines)
  and count toward the total.
- Marker counts: 188 unit + 44 integration (1 also network).

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the new capability:**
   ``furqan-lint check tests/fixtures/rust/failing/result_collapse.rs``
   returns exit 1 with a MARAD on ``parse_age`` (declared
   ``-> i32``) calling ``parse_helper`` (declared
   ``-> Result<i32, String>``). On v0.7.1: PASS, exit 0 (D11
   only fired on Option-returning helpers).
2. **Smallest input demonstrating the bug pre-fix:** same input
   on v0.7.1: silent PASS. The function's signature lied about
   what it actually did (could panic on bad input), but D11
   did not catch the lie because Result was outside the
   Option-only predicate.
3. **What this release does NOT do:**
   (a) No Rust analogue of return_none_mismatch (dropped per
       the round-16 critique; firing condition unreachable on
       compilable Rust).
   (b) No translator deltas (none needed for Result-aware D11;
       the v0.7.0 translator already represents Result<T, E> as
       UnionType with the right shape for the new predicate).
   (c) No Shape B generalisation (deferred to Go adapter).
   (d) No closure analysis, function_signature_item analysis,
       cross-file resolution, macro expansion, or Cargo workspace
       traversal beyond Cargo.toml (out of scope, unchanged from
       v0.7.1).
4. **New code paths:**
   ``rust_adapter/runner.py``: ``_is_result_type`` (~25 LoC),
   ``_is_may_fail_producer`` (~10 LoC), updated D11 wiring
   (1 line). ``UnionType`` import added. 2 new fixtures, 3 new
   integration tests, 1 new dead-code regression test, per-version
   snapshot baselines for v0.7.1 and v0.7.2 in both surface
   snapshot files.
5. **Limits retired and added:** none. v0.7.2 does not
   introduce or retire any documented limits.

### Validator-bias self-disclosure (per v0.7.0.1 §5.1 standing requirement)

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
```

Same posture as v0.7.1: ``tomli`` from mypy transitive on
Python 3.10, both tree-sitter packages from explicit install.
The v0.7.0.1 ``[[mypy]] overrides`` for ``tomli`` is in place
so ``mypy --strict`` passes even when ``tomli`` is absent
(verified at v0.7.0.1; not re-verified for v0.7.2 because the
override is still in pyproject.toml).

**Gates run from a clean state:**

Gate 9 (empirical missing-extras) was run AFTER
``pip uninstall -y tree_sitter tree_sitter_rust``:

```
$ furqan-lint check /tmp/result_smoke.rs
Rust support not installed. Run: pip install furqan-lint[rust]
$ echo $?
1
```

Output matches the v0.7.0.1 contract: clean install hint to
stderr, exit 1, no traceback. Re-installed before re-running
other gates.

**Gates that could not be run from a clean state:**

Air-gap (``unshare -n``) was attempted but the build sandbox
lacks ``CAP_SYS_ADMIN`` to namespace-isolate. Verifiable on the
deploy host; same posture as v0.7.0 / v0.7.0.1 / v0.7.1.

### §5.2 prompt-grounding self-check disclosure (NEW, v0.7.2)

The §5.2 self-check surfaced three drifts in the round-15
prompt before any code was written. Documented in full at
``/tmp/rust_phase_3_blocker.md``. Summary:

1. CRITICAL: ``check_return_none`` cannot fire on any compilable
   Rust source (the §4.2 fixture's expected MARAD does not
   materialise; the function PASSes silently because Optional
   permits None and rustc rejects the only configurations that
   would fire). Resolution: drop the return_none commit (Path
   A in the blocker). This release.
2. HIGH: ``furqan.checker.return_none`` does not exist upstream
   (the prompt's "Alternative D" framing was wrong; the local
   ``furqan_lint.return_none`` is what the Python runner uses).
   Resolution: moot under Path A.
3. MEDIUM: ``_d24_diagnostic_in_r3_set`` was already removed in
   v0.6.1; the prompt's §3.4 was based on a stale audit note.
   Resolution: invert into a forward-compat regression test
   (this release).

The discipline trajectory: §5.2 caught what would have shipped
as a checker without a job. Round-16's pre-implementation
critique was the right place to surface the architectural
question; v0.7.2's blocker was the right place to land it as
a scope narrowing rather than a mid-flight architecture change.

## [0.7.1] - 2026-05-03

Feature release. Phase 2 of the Rust adapter: wires upstream
``furqan.checker.check_ring_close`` (filtered to R3-shaped
diagnostics) for the Rust R3 analogue (zero-return on annotated
functions). Closes the v0.7.0 documented limit
``empty_or_panic_only_body.rs``. Retires the
``trait_method_signature.rs`` documented limit (the skip is now
stable across two releases and recognised as a permanent design
choice). Adds the additive-only test infrastructure to the
top-level ``furqan_lint`` package surface, parallel to the v0.7.0
``rust_adapter.__all__`` snapshot.

The architecture (parser, install path, IR boundary, lazy-import
gate, ``RustExtrasNotInstalled`` typed exception) is unchanged
from v0.7.0.1. Phase 2 adds one checker via upstream wiring (not
local re-implementation), retires two documented limits, and
lands one additive-only test. That is the entire scope.

### Added

- **R3 (zero-return) checker for Rust** via upstream
  ``furqan.checker.check_ring_close`` in
  ``src/furqan_lint/rust_adapter/runner.py``. Fires
  ``zero_return_path`` MARAD on functions that declare a
  non-unit return type but produce zero ``ReturnStmt`` in the
  translated IR. The structural pattern catches every body shape
  that has the right IR (empty body, ``panic!();``, ``todo!();``,
  ``unimplemented!();``, ``unreachable!();``, and any other
  macro-with-semicolon body whose macro identity is irrelevant to
  the R3 firing condition).
- **``check_rust_module(module)``** in
  ``rust_adapter/runner.py``. Centralises the v0.7.1 checker
  pipeline (R3 -> D24 -> D11). R3 runs first so the D24
  suppression on R3-fired functions is reachable; the
  suppression is pinned by a test asserting EXACTLY ONE
  diagnostic on ``r3_empty_body_returns_T.rs``.
- **``_RUST_KNOWN_TYPES`` frozenset** in
  ``rust_adapter/runner.py`` listing well-known Rust primitive
  type names plus the adapter-internal ``"None"`` token. Passed
  to ``check_ring_close`` as ``imported_types`` so R1
  (unresolved-type) noise does not dominate the diagnostic
  output. Without this, every ``i32`` / ``Result`` / ``Option``
  reference would be flagged as "no compound type with this
  name."
- **``_is_r3_shaped(diag)`` discriminator** in
  ``rust_adapter/runner.py``. ``check_ring_close`` emits R1, R3,
  and R4 shapes; v0.7.1 forwards only R3. The discriminator
  reads the diagnosis prose prefix; if upstream adds a
  structural discriminant, this helper migrates to that. Pinned
  by ``test_is_r3_shaped_recognises_only_r3``.
- **6 new R3 failing fixtures** in ``tests/fixtures/rust/failing/``:
  ``r3_empty_body_returns_T.rs``, ``r3_panic_only_body.rs``,
  ``r3_todo_only_body.rs``, ``r3_unimplemented_only_body.rs``,
  ``r3_unreachable_only_body.rs``,
  ``r3_macro_only_body_with_unrelated_macro.rs``. The last is
  the load-bearing pin for the design that R3 is
  grammar-and-macro-agnostic.
- **1 new documented-limit fixture**
  ``tests/fixtures/rust/documented_limits/r3_panic_as_tail_expression.rs``
  pinning the v0.7.1 limit that R3 does NOT fire on
  ``panic!()``-as-tail-expression (no semicolon). The trailing
  ``;`` is load-bearing: with it, the macro is an
  expression_statement that the translator drops (statements=0,
  R3 fires); without it, the macro is a tail expression that
  synthesizes a ReturnStmt (statements=1, R3 silent).
- **Top-level public-surface additive-only test**
  ``tests/test_top_level_public_surface_additive.py`` with
  per-version snapshots V0_7_0_SURFACE, V0_7_0_1_SURFACE,
  V0_7_1_SURFACE per Bayyinah Engineering Discipline Framework
  v2.0 section 7.6 cadence. Round-11's MEDIUM 3 finding was the
  failure mode that pinning only the latest version creates;
  v0.7.1 establishes the pattern correctly from the start.
- **Explicit ``__all__`` declaration** in
  ``src/furqan_lint/__init__.py``. The implicit surface (any
  module-level binding) is fragile; ``__all__ = ("__version__",)``
  is the load-bearing primitive the additive-only discipline
  requires.

### Changed

- **CLI Rust PASS message** updated from
  ``"2 structural checks ran (Rust Phase 1: D24 + D11)."`` to
  ``"3 structural checks ran (Rust Phase 2: R3 + D24 + D11)."``.
- **Rust CLI dispatch** (``cli._check_rust_file``) delegates to
  the new ``check_rust_module`` runner instead of inlining the
  D24/D11 calls. The lazy-import guard, the
  ``RustExtrasNotInstalled`` typed exception, and the
  ``RustParseError`` path are unchanged.

### Limitations introduced

- **``panic!()`` (or any diverging macro) used as a tail
  expression with no ``;``.** R3 does NOT fire because the
  translator synthesizes a ``ReturnStmt(opaque)`` for any tail
  expression per the v0.7.0 R1 rule. Adding a fix would require
  either a hardcoded diverging-macro allowlist (brittle: third-
  party macros like ``never_return!()`` would not be caught) or
  cross-file type inference of the macro's expansion type (out
  of scope; needs a Rust type checker). Pinned as
  ``tests/fixtures/rust/documented_limits/r3_panic_as_tail_expression.rs``.

### Limitations retired

- **``empty_or_panic_only_body.rs``.** Was a v0.7.0 documented
  limit ("Phase 1 ships D24 only on annotated functions whose
  body has at least one statement-or-expression"). v0.7.1 closes
  it: R3 (via the upstream check_ring_close wiring) fires on
  every shape the limit pinned (empty body,
  ``panic!()``-with-semi, ``todo!()``-with-semi,
  ``unimplemented!()``-with-semi). The fixture is deleted; the
  cases now live as ``failing/r3_*.rs`` fixtures with assertions
  inverted from "silent PASS" to "fires R3."
- **``trait_method_signature.rs``.** Was a v0.7.0 documented
  limit ("function_signature_item nodes are skipped by design").
  The skip is now stable across two releases and is recognised
  as a permanent design choice rather than a temporary limit:
  D24/D11/R3 do not apply to interface declarations because
  there is no body to analyse. The retirement procedure cleans
  up exactly this kind of "limit that turned out to be
  permanent."

### Tests

- 229 passed (was 215 in v0.7.0.1). Delta: +14 (4 new R3 unit +
  8 new R3 integration + 4 new top-level surface - 2 retired
  pinning tests).
- 184 unit + 44 integration + 1 network (network is also
  integration-marked).

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the new capability:**
   ``furqan-lint check tests/fixtures/rust/failing/r3_panic_only_body.rs``
   returns exit 1 with a MARAD on function ``f`` declared
   ``-> i32`` whose diagnosis names "but its body contains no
   ``return`` statement." On v0.7.0.1: silent PASS (the Rust
   adapter ran only D24 + D11; D24 needs >=1 return present and
   does not fire on zero-return shapes).
2. **Smallest input demonstrating the bug pre-fix:** same input,
   on v0.7.0.1: PASS, exit 0. The macro-with-semicolon body is
   honest-looking (compiles, runs, panics) but structurally
   dishonest (declares it returns ``i32``, never does).
3. **What this release does NOT do:**
   (a) No R3 firing on ``panic!()``-as-tail-expression
       (documented limit, pinned).
   (b) No closure analysis (``closure_expression`` skipped for
       D24, D11, AND R3; documented limit retained).
   (c) No ``function_signature_item`` analysis (permanently
       skipped, fixture retired).
   (d) No cross-file Rust symbol resolution.
   (e) No macro expansion.
   (f) No Cargo workspace traversal beyond reading nearest
       ``Cargo.toml`` for edition.
   (g) No per-edition diagnostic divergence (Phase 1 confirmed
       all in-scope idioms parse uniformly across 2018/2021/2024).
   (h) No Result-aware D11 (still Option-only; deferred to
       v0.7.2+).
4. **New code paths:**
   ``rust_adapter/runner.py`` (~140 LoC): ``_RUST_KNOWN_TYPES``
   frozenset; ``check_rust_module`` pipeline; ``_is_r3_shaped``
   discriminator; ``_diagnostic_function_name`` helper for D24
   suppression. ``cli._check_rust_file`` refactored to delegate
   to the runner. 6 new R3 fixtures + 1 new documented-limit
   fixture + 2 retired fixtures + 4 new top-level surface tests
   + 1 ``__all__`` declaration in package ``__init__``.
5. **Limits retired and added:**
   Retired: ``empty_or_panic_only_body.rs`` (closed by R3),
   ``trait_method_signature.rs`` (skip is permanent design).
   Added: ``r3_panic_as_tail_expression.rs`` (panic-as-tail false
   negative).

### Validator-bias self-disclosure (per v0.7.0.1 standing requirement)

This section is the §5.1 standing requirement established by the
v0.7.0.1 corrective. The v0.7.0 review missed two HIGH findings
because (a) ``tomli`` was installed transitively in my sandbox
and ``mypy --strict`` did not surface the missing override, and
(b) the missing-extras CLI path was reasoned about but not
empirically simulated. v0.7.1 reports each of the three §5.1
subsections explicitly:

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
```

``tomli``, ``tree-sitter``, and ``tree-sitter-rust`` were all
installed in the sandbox. ``tomli`` came transitively from mypy
on Python 3.10; the two tree-sitter packages were installed
explicitly during v0.7.0 development. The v0.7.0.1 ``[[mypy]]
overrides`` for ``tomli`` is in place so mypy --strict passes
even when ``tomli`` is absent (verified once at v0.7.0.1 by
``pip uninstall -y tomli``; not re-verified for v0.7.1 because
the override is still in pyproject.toml).

**Gates run from a clean state:**

Gate 9 (empirical missing-extras) was run during v0.7.1 development
AFTER ``pip uninstall -y tree_sitter tree_sitter_rust``:

```
$ furqan-lint check /tmp/r3_smoke.rs
Rust support not installed. Run: pip install furqan-lint[rust]
$ echo $?
1
```

Output matches the v0.7.0.1 contract: clean install hint to
stderr, exit 1, no traceback. Re-installed before re-running
other gates.

**Gates that could not be run from a clean state:**

Air-gap (``unshare -n``) was attempted but the build sandbox
lacks ``CAP_SYS_ADMIN`` to namespace-isolate. Verifiable on the
deploy host; this is the same posture as v0.7.0 / v0.7.0.1.

## [0.7.0.1] - 2026-05-03

Corrective release for two HIGH-severity findings from Bilal's
fresh-instance review of the v0.7.0 patch. Both were silent on
my own validation pass because of validator bias (transitive
dependencies and call-time imports that did not surface in the
sandbox where v0.7.0 was built).

### Fixed

- **HIGH: mypy --strict failed on a clean install (Issue 1).**
  The v0.7.0 ``[dev]`` install resolves to a venv where ``tomli``
  is not always present (it is a transitive of mypy on Python
  3.10 but not on 3.11+). Without ``tomli`` installed, mypy
  --strict emitted ``Cannot find implementation or library stub
  for module named "tomli"`` at ``edition.py:24``, failing
  gate-4 of section 5. Fix: added ``[[tool.mypy.overrides]]
  module = "tomli" ignore_missing_imports = true`` to
  ``pyproject.toml``. The override is pinned by a regression test
  in ``tests/test_v0_7_0_1_corrective.py`` so a future cleanup
  cannot silently drop it.
- **HIGH: ``furqan-lint check foo.rs`` without [rust] crashed with
  a Python traceback (Issue 2).** The CLI guard in
  ``_check_rust_file`` wrapped only the package import
  (``from furqan_lint.rust_adapter import ...``), not the call
  to ``parse_rust(path)``. The actual ``import tree_sitter``
  fired deep inside ``parser._get_parser`` on first call, and
  surfaced as an uncaught ``ModuleNotFoundError`` traceback,
  violating prompt section 3.3 ("Do not crash with
  ``ModuleNotFoundError``"). Fix: added
  ``RustExtrasNotInstalled`` (a typed ``ImportError`` subclass)
  to the rust_adapter public surface; ``parse_file`` now probes
  the ``tree_sitter`` and ``tree_sitter_rust`` imports at its
  entry point and re-raises any ``ImportError`` as
  ``RustExtrasNotInstalled`` carrying the install hint. The CLI
  catches this typed exception around the ``parse_rust(path)``
  call and prints a one-line install hint to stderr, exit 1.
  Pinned by three regression tests in
  ``tests/test_v0_7_0_1_corrective.py``.

### Added

- **``RustExtrasNotInstalled`` typed exception** in
  ``furqan_lint.rust_adapter.translator``, exported from
  ``furqan_lint.rust_adapter``. Subclasses ``ImportError``;
  message is the install hint itself. Snapshot test in
  ``tests/test_rust_public_surface_additive.py`` extended with
  a v0.7.0.1 baseline that includes this name (additive
  superset of the v0.7.0 baseline).
- **``tests/test_v0_7_0_1_corrective.py``** (4 unit tests).
  (1) Asserts pyproject.toml has a tomli mypy override.
  (2) Asserts ``RustExtrasNotInstalled`` is exported and
  subclasses ``ImportError``.
  (3) Asserts ``parse_file`` raises ``RustExtrasNotInstalled``
  when ``tree_sitter`` is not importable (uses ``sys.meta_path``
  injection to simulate the missing extra).
  (4) Asserts the CLI emits the install hint to stderr and
  returns exit 1 without dumping a traceback when
  ``RustExtrasNotInstalled`` is raised.

### Tests

- 214 passed (was 210 in v0.7.0). Delta: +4.
- 176 unit + 38 integration (1 also network-marked).

### Process notes (validator-bias self-disclosure)

Both findings landed silently on my v0.7.0 validation because:

1. **Issue 1**: my sandbox already had ``tomli`` installed (a
   transitive of mypy on Python 3.10), so mypy resolved the
   import without needing the override. A fresh contributor
   venv on 3.11+ without tomli would not. The lesson is that
   "mypy --strict passes" is not a sufficient gate; it must be
   "mypy --strict passes on a clean install of [dev,rust]
   from scratch", which is what fresh-instance review is for.
2. **Issue 2**: I tested the CLI dispatch path with extras
   installed and never simulated the missing-extras case
   empirically. The lazy-import gate I did test
   (``python3 -X importtime``) proves that ``cli`` does not
   load tree_sitter, but does NOT prove that ``cli`` handles
   tree_sitter being missing at call time. Different gate,
   different test required.

Both lessons saved as feedback memories for future releases.

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the fix works?**
   For Issue 2:
   ```bash
   pip uninstall tree_sitter tree_sitter_rust
   echo "fn f() -> i32 { 42 }" > /tmp/foo.rs
   furqan-lint check /tmp/foo.rs
   ```
   On v0.7.0: Python traceback ending with
   ``ModuleNotFoundError: No module named 'tree_sitter'``,
   exit 1. On v0.7.0.1: one line
   ``Rust support not installed. Run: pip install furqan-lint[rust]``,
   exit 1, no traceback.

2. **Smallest input demonstrating the bug pre-fix?**
   Same input, on v0.7.0: 12-line Python traceback dumping
   the call stack down to ``parser.py:35``.

3. **What this fix does NOT do?**
   (a) Does not bump the minimum Python to 3.11 (which would
       eliminate the tomli dependency entirely). 3.10 remains
       supported.
   (b) Does not change the behaviour when a partial extras
       install (e.g., tree_sitter present but tree_sitter_rust
       missing) occurs; the typed exception fires identically
       in either case.
   (c) Does not add a ``furqan-lint --install-extras`` helper
       command; the user must run pip themselves.

4. **New code paths and their boundaries?**
   ``parse_file`` gained a 7-line probe block at its entry
   (try/except importing tree_sitter and tree_sitter_rust,
   raising ``RustExtrasNotInstalled`` with the install hint).
   ``_check_rust_file`` gained a 6-line except-block catching
   ``RustExtrasNotInstalled`` and emitting a clean stderr
   message + exit 1. The translator gained the
   ``RustExtrasNotInstalled`` class (8 lines including
   docstring). All boundaries pinned by the 4-test corrective
   regression suite.

5. **Limits retired and added?**
   Retired: none. Added: none. v0.7.0.1 is a corrective
   release; the documented-limits inventory is unchanged.

## [0.7.0] - 2026-05-03

Feature release: Rust adapter Phase 1. New language support behind
an opt-in `[rust]` extra. Two checkers run on `.rs` files: D24
(all-paths-return) and D11 (status-coverage on Option-returning
helpers). The Python adapter is unchanged.

This is the first release in the multi-language stage of the
furqan-lint roadmap. The architecture follows ADR-001
(`furqan_lint_rust_adapter_adr.md`): tree-sitter-rust direct (not
language-pack), opt-in extra (not bundled), all checker logic
operates on Furqan IR (`tree_sitter` appears only in
`src/furqan_lint/rust_adapter/`). Validator findings R1
(implicit-return load-bearing), R3 (PyPI ARM64 wheels both
packages), and R4 (representability gate before translator code)
are all observed.

### Added

- **`src/furqan_lint/rust_adapter/`** (~470 LoC). New package
  containing `parser.py` (tree-sitter bootstrap with lazy
  initialisation), `translator.py` (CST -> Furqan
  Module/UnionType/TypePath), `edition.py` (Cargo.toml
  resolution), and `__init__.py` (lazy-import gate; public
  surface limited to `parse_file` and `RustParseError`).
- **CLI dispatch on `.rs` files.** `_check_file` is now a
  dispatcher calling `_check_python_file` (existing 55-line body)
  or `_check_rust_file` (new path). On `.rs`, the CLI lazy-imports
  `furqan_lint.rust_adapter`; if `tree_sitter` is missing, prints
  `Rust support not installed. Run: pip install furqan-lint[rust]`
  to stderr and exits 1.
- **`_check_directory` walks both `*.py` and `*.rs`.** Existing
  Python directory walks are unchanged; new directory walks
  discover Rust files alongside Python.
- **`target/` added to `EXCLUDED_DIRS`.** Cargo build output is
  skipped in directory walks (mirrors the existing `.venv`,
  `__pycache__` exclusions).
- **`[rust]` optional extra in `pyproject.toml`.**
  `pip install furqan-lint[rust]` resolves
  `tree-sitter>=0.23,<1` and `tree-sitter-rust>=0.23,<1`. Both
  packages ship ARM64 and x86_64 wheels on PyPI; no source build
  required.
- **21 Rust fixture files.** 10 in `clean/`, 4 in `failing/`,
  6 in `documented_limits/`, plus a `documented_limits/README.md`
  mirroring the Python adapter's four-place-pattern shape.
- **30 new tests across four files.** `test_rust_adapter.py`
  (15 unit), `test_rust_correctness.py` (11 integration),
  `test_rust_extras_sync.py` (2 unit), and
  `test_rust_public_surface_additive.py` (2 unit). Test count
  goes from 180 to 210.
- **`test_rust_public_surface_additive.py`.** First additive-only
  snapshot test on furqan-lint's own surface. Pins
  `furqan_lint.rust_adapter.__all__` at v0.7.0 as a frozenset that
  future versions must remain a superset of. A parallel snapshot
  for the top-level `furqan_lint` package is registered as a
  v0.7.x or v0.8 candidate.

### Changed

- **CLI PASS message for `.rs` files.** Reads "2 structural checks
  ran (Rust Phase 1: D24 + D11). Zero diagnostics." rather than
  the Python-side "4 structural checks ran" message, so it is
  obvious which pipeline ran.
- **`pyproject.toml` ruff per-file-ignores.** The three new
  `rust_adapter/*.py` files use lazy mid-function imports; PLC0415
  is suppressed for them, mirroring the existing `cli.py`
  exception.
- **`pyproject.toml` mypy override.** `tree_sitter` and
  `tree_sitter_rust` get `ignore_missing_imports = true` because
  they ship without inline type hints at the version we pin. The
  rest of the source remains strictly typed.

### Limitations introduced

Six Rust documented limits, each pinned by the four-place pattern
(README bullet + fixture + pinning test + CHANGELOG entry):

- **Macro-invocation bodies** (`macro_invocation_body.rs`). Phase 1
  cannot see through macro expansion; `fn f() -> i32 { todo!() }`
  passes silently. The Rust analogue of R3 (zero-return ring-close)
  is deferred to v0.7.1.
- **Trait-object return types** (`trait_object_return.rs`).
  `Box<dyn Trait>` is translated to an opaque `TypePath`; trait-
  object polymorphism is out of scope per ADR-001.
- **Lifetime-affected return types** (`lifetime_param_return.rs`).
  `fn f<'a>(...) -> &'a str` has its lifetime stripped; D24's
  path-coverage logic is unaffected.
- **Empty or panic-only bodies** (`empty_or_panic_only_body.rs`).
  Same as the macro-body limit; deferred to v0.7.1.
- **Trait method signatures** (`trait_method_signature.rs`).
  `function_signature_item` nodes are skipped by design (per
  prompt 3.4); D24/D11 do not apply to interface declarations.
- **Closures with annotated return types**
  (`closure_with_annotated_return.rs`). `closure_expression` nodes
  are skipped in Phase 1 even when annotated. Phase 2 may revisit.

### Tests

- 210 passed (was 180 in v0.6.1). Delta: +30.
- 168 unit + 42 integration (1 of which is also network-marked).

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the new capability:**
   ```rust
   fn classify(x: i32) -> i32 {
       if x > 0 {
           return 1;
       }
       println!("non-positive");
   }
   ```
   On v0.6.x: `furqan-lint check classify.rs` prints
   `Not found: classify.rs` (the CLI rejected `.rs`). On v0.7.0
   with `[rust]` installed: exit 1 with a MARAD on `classify`
   naming the missing-return path; without `[rust]` installed: exit
   1 with the install hint.

2. **Smallest input that would have shown each shipped diagnostic
   on v0.6.x:** none. v0.6.x had no Rust dispatch path. The
   shipped diagnostics for `.rs` files (D24 path-coverage, D11
   Option-collapse, `RustParseError` for syntax errors) are all
   new in v0.7.0.

3. **What this release does NOT do:**
   (a) No Rust analogue of `return_none_mismatch` (deferred to
       v0.7.1+).
   (b) No additive-only on the top-level `furqan_lint` surface
       (the rust subpackage gets its own snapshot; the rest is
       deferred).
   (c) No macro expansion; macros are opaque.
   (d) No cross-file symbol resolution; all checks are intra-file.
   (e) No Cargo workspace traversal beyond reading the nearest
       `Cargo.toml` for edition.
   (f) No R3 equivalent for empty / `todo!()`-only / `panic!()`-only
       Rust functions (deferred to v0.7.1 per the documented
       limit).
   (g) No D24 or D11 on trait method declarations or closures
       (skipped by design).
   (h) No Result-aware D11. The producer predicate fires on
       Option-returning helpers (Option translates to
       UnionType-with-None-arm); Result-collapse needs a
       Rust-specific predicate, deferred.

4. **New code paths:**
   `src/furqan_lint/rust_adapter/` (~470 LoC across four
   modules); CLI dispatch on `.rs` (3 new methods:
   `_check_file` dispatcher, `_check_python_file`,
   `_check_rust_file`); lazy-import gate that converts
   `ImportError` to a user-facing install hint;
   `tree.root_node.has_error` refusal that exits 2; edition
   resolution from `Cargo.toml`; six Rust documented limits with
   the four-place pattern; one additive-only test on
   `rust_adapter.__all__`.

5. **Limits retired and added:**
   Retired: none. (v0.6.0 retired the zero-return-functions limit;
   v0.6.1 retired the aliased-decorator limit.)
   Added: six Rust documented limits (macro-invocation bodies,
   trait-object returns, lifetime-affected return types,
   empty/`todo!()`-only/`panic!()`-only bodies (deferred to v0.7.1),
   trait method signatures (skipped by design), closures with
   annotated return types (skipped in Phase 1)).

## [0.6.1] - 2026-05-02

Round-11 corrective from Fraz. Three tracked findings: an aliased-
decorator false positive in R3 left over from v0.6.0; doc-staleness
drift in the project README and the documented-limits README that
lingered across rounds 6-11; and dead code (`_d24_diagnostic_in_r3_set`)
introduced in v0.6.0 as defensive suppression that turned out to be
structurally redundant.

The retirement count for v0.6.1 is one documented limit
(aliased_abstractmethod), the third in three releases (v0.5.x ->
v0.6.0 retired two, v0.6.1 retires one).

### Fixed

- **Aliased-decorator skip-list now resolves through a module-level
  symbol table.** R3's decorator skip-list previously matched only
  the bare and qualified forms (`@abstractmethod`,
  `@abc.abstractmethod`, `@overload`, `@typing.overload`). It did
  not follow `from abc import abstractmethod as abstract` aliases,
  and a method decorated with the aliased name fired R3 as a false
  positive. v0.6.1 builds a module-level alias map from top-level
  `import` and `from ... import ... [as ...]` statements once per
  call to `check_zero_return`, then resolves bare and dotted
  decorator names through the map before the skip-list lookup.
  Covers four import shapes: `from X import Y`, `from X import Y
  as Z`, `import X`, `import X as Y`.
- **Stale README bullet for `redundant_pipe_none.py` removed.**
  The fixture was deleted in v0.3.5 when the redundant-None
  limit was promoted to a structural fix; the corresponding
  `Remaining limitations` bullet was left behind and persisted
  across rounds 6 through 11. Round-11 audit caught it.
- **Stale README bullet for `aliased_abstractmethod.py` removed.**
  The bullet was added in v0.6.0 and is now retired by the fix
  above.
- **Dead code: `_d24_diagnostic_in_r3_set` removed from
  `runner.py`.** The helper was added in v0.6.0 as a defensive
  D24-suppression mechanism for any function R3 had already fired
  on. Empirically D24 only fires on partial-path coverage (>=1
  return present) while R3 only fires on zero-return shapes; the
  two checkers do not overlap and the suppression had no
  reachable effect. Round-11 audit caught it. The runner now
  appends D24 diagnostics directly without the suppression
  branch, and the docstring is updated to document the
  non-overlap explicitly.
- **`tests/fixtures/documented_limits/README.md` refreshed.**
  The Inventory section had not been updated since v0.3.x and
  was missing the `Retired in v0.6.0` and `Retired in v0.6.1`
  sections, plus a substantively new four-place-pattern paragraph
  in the preamble. Now lists the current four active limits and
  three retirement-by-version sections.

### Limitations retired

- **Aliased decorator imports for R3 skip-list.** Was a v0.6.0
  documented limit. Closed by the alias-resolution fix above.
  The fixture `tests/fixtures/documented_limits/aliased_abstractmethod.py`
  is deleted; the pinning test
  `test_aliased_abstractmethod_fires_r3_false_positive` is
  removed; the README bullet is removed; the documented_limits
  README has a `## Retired in v0.6.1` section recording it.

### Added

- **`tests/test_round11_alias_resolution.py` (12 unit tests).**
  Pins the symbol-table-backed decorator skip-list across all
  four import shapes plus negative-control regression checks.
  Four tests cover alias map construction directly; six cover
  skip-list resolution through the alias map (positive cases);
  two cover that direct (non-aliased) recognition still works
  after the refactor; two are negative-control assertions
  (unrelated decorator fires; no imports yields no resolution).
- **`tests/test_readme_drift.py` (2 unit tests).** v3.0-prep
  structural test that parses the project README's `Remaining
  limitations` section, extracts every fixture path mentioned
  in inline code spans, and asserts each path exists on disk.
  Would have caught the `redundant_pipe_none.py` drift in
  round 6 and prevented the four rounds of accumulated
  staleness that round 11 surfaced.

### Tests

- 180 passed (was 167 in v0.6.0). Delta: +13 (= 12 alias + 2
  drift - 1 retired pin).
- 153 unit + 27 integration (1 of which is also network-marked).

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the fix works?**
   ```python
   from abc import abstractmethod as abstract
   class C:
       @abstract
       def required(self) -> int: ...
   ```
   On v0.6.0: R3 fires `zero_return_path` on `required` as a
   false positive (exit 1). On v0.6.1: PASS, exit 0, because
   `abstract` now resolves to `abc.abstractmethod` via the
   alias map and the skip-list match succeeds.

2. **Smallest input demonstrating the bug pre-fix?**
   Same input, same output, before vs. after. The asymmetry was
   the failing direction: v0.6.0 was a false positive on a
   genuinely-abstract method; v0.6.1 correctly skips.

3. **What does this fix NOT do that a reader might expect?**
   It does not (a) extend symbol-table tracking to
   `aliased_optional_import.py` or `aliased_union_import.py` in
   the `return_none` checker; both remain documented limits with
   their original fixtures and pinning tests. (b) follow imports
   inside function or class bodies; only top-level
   `tree.body` `Import` and `ImportFrom` nodes are tracked.
   Decorators that need such inner imports are exotic enough to
   defer. (c) close the `from somemodule import abstractmethod`
   collision case (an unrelated module that happens to export
   the bare name `abstractmethod`); the alias map records the
   qualified form `somemodule.abstractmethod` but the skip-list
   match is short-circuited by the bare-name check before
   alias resolution runs. This false positive predates v0.6.1
   and is not made worse by this fix; it is named in the
   negative-control test for awareness.

4. **New code paths and their boundaries?**
   `zero_return._build_decorator_alias_map(tree)` walks
   `tree.body` for `Import` and `ImportFrom`; reads `node.module`
   and each `alias.asname or alias.name`; emits a
   `dict[str, str]`. `check_zero_return` calls it once per
   tree. `_check_function`, `_has_skip_decorator`, and
   `_decorator_matches_skip_list` thread the dict through.
   `_decorator_matches_skip_list` adds two new branches: bare
   `aliases.get(name) in _SKIP_DECORATORS`, and dotted
   `f"{aliases.get(prefix)}.{suffix}" in _SKIP_DECORATORS`. All
   four shapes pinned by tests. Boundaries: lambdas excluded
   (no decorator syntax); inner imports not tracked; module
   alias map is not propagated across files (no cross-file
   symbol resolution).

5. **What documented limitations does this retire? Add?**
   Retires: "Aliased decorator imports for R3 skip-list" (v0.6.0).
   Adds: none.

## [0.6.0] - 2026-05-02

Round-10: ring-close R3 (zero-return) checker. The fourth Furqan
checker on the Python adaptor. Closes the v0.4.x documented
limitation "Zero-return functions" and additionally retires the
v0.3.5 documented limitation "Exception-driven fall-through" (R3
catches the try-body-only-raise shape that D24 cannot). One new
documented limitation introduced: aliased decorator imports for
R3's skip-list (e.g., `from abc import abstractmethod as abstract`)
are not yet resolved; v0.6.1 will close that with a symbol table.

### Added

- **`zero_return_path` (R3) checker.** New module
  `src/furqan_lint/zero_return.py` (~250 lines, ~10 helpers). A
  function that declares a non-`None` return type but contains zero
  `return` statements anywhere on any path is reported as
  `zero_return_path` (R3, ring-close). mypy reports the same shape
  as "Missing return statement"; furqan-lint now matches that
  coverage.
- **`furqan_lint.adapter.translate_tree(tree, filename)`.** Public
  wrapper around `_translate_module` so the CLI can parse the
  source once and feed both the Furqan `Module` (for D24/D11/return-none)
  and the raw `ast.Module` (for R3, which needs decorators that
  the Furqan translation does not preserve).
- **R3 wired into the runner pipeline.** `runner.check_python_module`
  gained a `source_tree: ast.Module | None = None` keyword. R3 runs
  before D24 on each function; if R3 fires, D24 is suppressed for
  that function (defensive: in practice D24 only fires on partial-
  path coverage, but the suppression is forward-compatible). Without
  `source_tree` the runner is back-compat for v0.5.x callers.
- **CLI parses once, threads tree to runner.** `cli._check_file`
  now does `tree = ast.parse(source); module = translate_tree(tree)`
  and passes `source_tree=tree`. CLI exit code now treats R3
  diagnostics as failures (exit 1), parallel to marads. PASS message
  updated from "3 structural checks ran" to "4 structural checks
  ran".
- **R3 skip-list (name-based).** `@abstractmethod`,
  `@abc.abstractmethod`, `@overload`, `@typing.overload` (and the
  called forms `@abstractmethod()` etc.) are recognised and skipped.
  Aliased imports are NOT recognised (documented limit).
- **Provably-non-returning body recognition.** Two shapes:
  raise-only bodies (recursive on `If` branches whose every arm
  ends in `Raise`) and the canonical `while True:` loop with no
  reachable `break`. Conservative: `while 1:` is NOT recognised.
- **5 failing fixtures.**
  `tests/fixtures/failing/zero_return_function.py` (moved from
  `documented_limits/`), `zero_return_with_branches.py`,
  `zero_return_async.py`, `zero_return_method.py`,
  `zero_return_optional_propagation.py`.
- **8 clean fixtures.**
  `tests/fixtures/clean/zero_return_none_annotated.py`,
  `zero_return_unannotated.py`, `zero_return_optional_annotated.py`,
  `zero_return_pipe_none.py`, `raise_only_function.py`,
  `while_true_no_break.py`, `abstractmethod_decorated.py`,
  `overload_decorated.py`.
- **1 documented-limit fixture.**
  `tests/fixtures/documented_limits/aliased_abstractmethod.py`
  pinning the v0.6.1 regression target.
- **`tests/test_round10_r3.py` (12 tests).** 5 firing tests, 6
  silence tests (the abstractmethod/overload pair share one test
  function), 1 direct-API test pinning `check_zero_return`'s
  return shape.

### Changed

- **CLI PASS string updated** from `3 structural checks ran` to
  `4 structural checks ran` to match the new pipeline (D24, D11,
  return-none, R3).

### Fixed (limitations retired)

- **Zero-return functions.** Was a v0.4.x documented limitation
  ("D24 skips zero-return functions, R3 not yet wired"). v0.6.0
  closes it: R3 fires on every shape D24 cannot reach. The
  README "Remaining limitations" entry is removed.
- **Exception-driven fall-through, stronger form.** The
  `try: raise; except: pass` shape with no return on any path
  was a v0.3.5 documented limitation. R3 catches it as a
  zero-return function. The fixture
  `try_body_only_returns_in_block.py` is retained but the
  pinning test is inverted: it now asserts R3 fires
  (`test_try_body_raises_with_swallowing_handler_now_caught_by_r3`).

### Architectural alternative considered

The prompt's ADR offered three alternatives for sourcing the raw
AST in R3: (A) local AST walk inside `zero_return.py` using the raw
`ast.Module`; (B) extend the Furqan translation to preserve
decorators and walk the Furqan `Module`; (D) call upstream Furqan's
ring-close primitive with adapter-supplied predicates. Alternative
A was chosen: it is the smallest change (no Furqan-side or upstream
changes), the most testable (R3 logic is fully isolated), and the
most precise (raw AST decorators are lossless). The reversibility
cost is one day if a future requirement (e.g. cross-checker
deduplication) forces a switch to B or D.

### Limitations introduced

- **Aliased decorator imports for R3 skip-list.** Name-only
  resolution does not follow `from abc import abstractmethod as
  abstract`. Pinned as `aliased_abstractmethod.py` in
  `documented_limits/`. v0.6.1 will add a symbol table so this case
  is skipped.

### Tests

- 12 new R3 tests (`test_round10_r3.py`).
- 1 new documented-limit pin
  (`test_aliased_abstractmethod_fires_r3_false_positive`).
- 1 inverted documented-limit test
  (`test_try_body_raises_with_swallowing_handler_now_caught_by_r3`).
- 14 fixture files added (5 failing + 8 clean + 1 doc-limit) and 1
  fixture moved (`zero_return_function.py` from `documented_limits/`
  to `failing/`).

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the fix works?**
   `def f(x: int) -> int: pass` is now reported as
   `zero_return_path` (R3) with exit code 1. v0.5.x: silent PASS.

2. **Smallest input demonstrating the bug pre-fix?**
   Same input, on v0.5.x: `furqan-lint check ...` returns "PASS"
   and exits 0. mypy reports "Missing return statement".

3. **What does this fix NOT do that a reader might expect?**
   It does not (a) catch zero-return shapes hidden behind
   aliased decorators (`@abstract` from
   `from abc import abstractmethod as abstract`); (b) recognise
   non-canonical infinite loops (`while 1:`, `itertools.count()`);
   (c) recognise bodies whose raise is hidden inside a swallowing
   `try/except` that the body itself does not establish; (d)
   replace mypy's broader missing-return analysis (R3 only fires
   on zero returns, not partial coverage; D24 covers partial).

4. **New code paths and their boundaries?**
   `zero_return.py:check_zero_return -> _check_function` runs the
   5-step skip cascade (no annotation -> Optional/None ->
   skip-decorator -> non-returning body -> has any return). All
   five steps are pinned by tests. Boundaries: nested function
   bodies are recursed by `ast.walk` so they are checked
   independently; lambdas are excluded (no syntax for return
   annotation); methods inside classes ARE walked (matches D24
   behaviour).

5. **What documented limitations does this retire? Add?**
   Retires: "Zero-return functions" (v0.4.x), "Exception-driven
   fall-through, stronger form" (v0.3.5). Adds: "Aliased decorator
   imports for R3 skip-list" (v0.6.0).

## [0.5.1] - 2026-05-03

Round-9 corrective from Fraz Ashraf. CRITICAL: ruff version drift
between CI and pre-commit caused CI to pass while the pre-commit
dogfood would have failed; the v0.5.0 CHANGELOG claim "pre-commit
run --all-files exits 0" was empirically false.

### Fixed

- **CRITICAL: ruff version drift between CI and pre-commit.** v0.5.0
  declared `ruff>=0.8.0` (unpinned upper) in the `[dev]` extras. CI
  resolved this to ruff 0.15.12 where UP038 was removed; pre-commit
  pinned 0.8.0 where UP038 fires. CI passed; the pre-commit dogfood
  failed; the CHANGELOG claim "pre-commit run --all-files exits 0"
  was empirically false. Pinned `ruff==0.8.0` in `[dev]` so all four
  surfaces (CI, pre-commit, contributor local, Fraz's reproducer)
  run the same checks.
- **CRITICAL: 8 UP038 violations in src/.** Migrated
  `isinstance(x, (A, B))` to `isinstance(x, A | B)` in adapter.py
  (6 sites) and additive.py (2 sites). Semantically identical on
  Python 3.10+ (the project's minimum version).
- **CRITICAL: 3 unformatted files.** Reformatted test_review_fixes.py,
  test_round7_fixes.py, and test_tooling.py. Whitespace and line
  wrapping only.
- **HIGH: CHANGELOG unit count corrected.** v0.5.0 said "135 unit";
  actual count is 138 unit. The 3 test_tooling.py tests are marked
  unit but were counted separately in the narrative.

### Added

- Functional tests: `test_ruff_check_exits_zero_on_repo` and
  `test_ruff_format_check_exits_zero_on_repo`. These are the
  functional pair to the existing structural
  `test_pyproject_has_ruff_config` per framework Section 8.6
  (structural-vs-functional pairing). Catches the v0.5.0 CRITICAL
  class: config exists but tool fails. The tests are meaningful
  only because `[dev]` now pins ruff exactly.

### Notes

- CLI shows 0% branch coverage because tests run via subprocess
  and coverage does not propagate through subprocess by default.
  Functional coverage of the CLI is provided by tests/test_action.py
  and the round-N regression tests. Subprocess coverage propagation
  is a v0.6.0 candidate.
- The version-drift root cause is the framework Section 8.6 pattern
  applied to a transitive dependency surface: the project verified
  the schema (`[tool.ruff]` exists in pyproject) but did not verify
  the functional outcome under the pinned version contributors and
  pre-commit actually run. Round-9 finding from Fraz Ashraf.

### Five Questions (audit framework Section 11.3)

1. **What does this commit change?** Pins ruff==0.8.0 in [dev],
   migrates 8 isinstance tuples to X | Y, reformats 3 test files,
   corrects CHANGELOG unit count, adds 2 functional tests.
2. **What does it not change?** No checker behavior. No public API.
   No fixture content. No ADR-backed decisions reversed.
3. **What is the verification?** `ruff check .` exits 0,
   `ruff format --check .` exits 0, `mypy` exits 0,
   `pre-commit run --all-files` exits 0, all 154 tests pass.
4. **What is deferred?** Subprocess coverage propagation (v0.6.0).
   Considered ruff bump to 0.15+ (deferred to deliberate ADR).
5. **What is the rollback?** `git revert` of the v0.5.1 commit
   restores v0.5.0 state. No data migration.

## [0.5.0] - 2026-05-03

Dev tooling integration. No new checker logic; the tool starts
checking itself.

### Added

- **`.pre-commit-config.yaml`** for the repo's own codebase
  (separate from `.pre-commit-hooks.yaml`, which is the
  producer-side hook for consumers). Five hook groups: standard
  hygiene (trailing-whitespace, end-of-file-fixer, check-yaml,
  check-toml, check-merge-conflict, check-added-large-files,
  mixed-line-ending), ruff (lint + format), mypy on `src/` only
  with furqan as additional_dependency, em-dash guard mirroring
  the CI step, and a furqan-lint self-check (dogfood).
- **CI lint job** parallel to the test matrix. Runs ruff check,
  ruff format --check, and mypy on Python 3.12 in ~10s. Fails
  fast on style/type issues before the 4-version test matrix
  spins up.
- **Three new pytest markers**: `unit` (fast, in-process, no
  subprocess), `integration` (CLI or pipeline), `mock` (uses
  unittest.mock or pytest-mock). `slow` and `network` were
  already registered in v0.4.1.
- **`[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.per-file-ignores]`,
  `[tool.ruff.format]`, `[tool.mypy]`, `[[tool.mypy.overrides]]`**
  blocks in `pyproject.toml`. Ruff selection is curated, not
  maximal: E/W/F/I/B/UP/SIM/RUF/PL/PTH/TID. Each ignore has a
  one-line comment explaining intent.
- **Dev dependencies extended**: `pytest-mock>=3.12`,
  `ruff>=0.8.0`, `mypy>=1.13`, `pre-commit>=4.0`, `pyyaml>=6.0`.
- **README sections**: "Using with Other Tools" (tool comparison
  table + recommended consumer pre-commit config) and
  "Contributing to furqan-lint" (setup, run-checks, marker usage).
- **`tests/test_tooling.py`**: 3 structural tests verifying the
  pre-commit config has all required hooks, pyproject has
  `[tool.ruff]`, and all 5 pytest markers are registered.

### Changed

- Codebase formatted with `ruff format`. No behavioral changes.
- Ruff and mypy findings from the baseline triage either fixed
  (real issues: SIM101, SIM103, SIM102 x4, RUF059, E402,
  arg-type narrowing on three predicate-helper pairs, missing
  type annotations on local vars and helper signatures) or
  ignored with explanatory comments (PLW1510 is intentional;
  cli.py PLC0415 is the lazy-import-for-fast-version pattern;
  PLR0911/PLR0912 are pre-existing API surface).
- All 148 existing tests carry pytest markers (138 unit, 13
  integration; the 1 v0.4.1 network test stays double-marked).

### Not added (deliberate, per recommendation document)

- `black` (ruff format is black-compatible; one tool, not two)
- `pylint` (ruff covers the same rules, faster)
- `tox`/`nox` (CI matrix already covers Python 3.10-3.13)
- `bandit` (narrow attack surface; reconsider if network features
  added)
- `pytest-xdist` (suite runs in seconds; parallelism adds flake risk)
- Coverage gate (add `pytest-cov` after baseline; gate after
  measurement)
- Directory-based test split (markers carry the same information
  without forcing a 14-file rename)

### Deferred (v0.6.0 candidates)

- Ring-close R3 (zero-return checker) - drafted in a prior session
  as a v0.5.0 candidate; reframed to v0.6.0 to keep this release
  scoped to tooling.
- Aliased Optional/Union import resolution (needs symbol table)
- Exhaustive match recognition
- Local classes inside function/method bodies
- Decorator threading (eliminates abstract-method false positives
  the future R3 checker will introduce)

### Tests

- 148 existing + 3 new tooling tests = 151 selectable + 1
  network = 152 total.

### Five questions (audit framework Section 9.3)

1. **Smallest input demonstrating the fix works:** `pre-commit
   run --all-files` exits 0 on a clean checkout. `ruff check .`,
   `ruff format --check .`, `mypy`, and `furqan-lint check src/`
   all exit 0.
2. **Smallest input demonstrating the bug pre-fix:** Pre-v0.5.0
   the repo had no formatter, no linter, no type checker, no
   self-check. `pip install -e .[dev]` installed only pytest.
3. **What this release does NOT do:** Does not add any new
   checker logic; the structural-honesty checks ship unchanged
   from v0.4.1. Ruff is not configured to run on `tests/fixtures/`
   (those are intentionally malformed). Mypy is strict on `src/`
   only, not `tests/`.
4. **New code paths and their boundaries:** No production code
   paths added; only configuration and one new test module.
   Boundary: anything in `tests/fixtures/` is the System Under
   Test for furqan-lint and is not subject to ruff or mypy.
5. **Documented limitations retired/introduced:** None. This
   release adds no checker behavior, so no four-place
   documentation churn.

## [0.4.1] - 2026-05-02

Corrective fixes from Fraz's round-8 review of v0.4.0. One CRITICAL,
two HIGH, two MEDIUM, two LOW. All findings reproduced empirically
against v0.4.0 before fixing.

### Fixed

- **CRITICAL: Pre-commit hook installation.** The hook now declares
  ``furqan`` as an ``additional_dependency`` via the canonical
  GitHub URL, so ``pre-commit install`` actually resolves the
  dependency. Without this, pip read ``furqan>=0.11.0`` from
  ``pyproject.toml``, queried PyPI (which only hosts ``furqan==0.10.1``),
  and failed resolution. The hook shipped in v0.4.0 in a non-functional
  state.
- **HIGH: GitHub Action version drift.** ``action.yml`` now installs
  furqan-lint at ``${{ github.action_ref }}`` so a user pinning
  the action to a specific tag gets the matching code from that tag
  rather than whatever happens to be on ``main`` at install time. The
  ``furqan-lint-version`` input was removed; it can return when
  furqan-lint is on PyPI and the install step switches from git URL
  to ``pip install furqan-lint==<version>``.
- **MEDIUM: Bare-Union diagnostic prose.** The v0.3.4 fix collapsed
  ``Optional`` and ``Union`` into one branch and could end up
  recommending ``Union[X]`` (well-formed but degenerate - typing
  folds a one-arm Union to ``X``). v0.4.1 splits the two cases:
  bare ``Union`` now suggests ``Union[X, None]``, ``Optional[X]``,
  or ``X | None`` since the user is returning ``None``.
- **LOW: CI em-dash check locale.** The em-dash regex is now run
  under ``LC_ALL=C.UTF-8`` because GNU ``grep -P`` fails on some
  default GitHub runner locales when the pattern contains hex-escape
  sequences. Without the prefix, the gate could pass spuriously.

### Changed

- **HIGH: D11 monkey-patch retired.** ``runner.py`` now passes the
  Python-Optional predicate to ``check_status_coverage`` via the
  upstream ``producer_predicate=`` keyword (available since
  ``furqan>=0.11.0``) instead of monkey-patching
  ``status_coverage._is_integrity_incomplete_union``. Removed
  ``import threading``, the ``contextmanager`` import,
  ``_predicate_lock``, and the entire ``_python_optional_mode``
  context manager. The ``_is_optional_union`` helper is preserved
  with its body unchanged; the docstring now references the
  ``producer_predicate`` keyword. Closes the full lifecycle of a
  round-1 audit finding (stopgap monkey-patch in v0.1.0 ->
  scoped context manager in v0.3.0 -> threading lock for safety
  in v0.3.0 -> upstream parameter retires the patch entirely in
  v0.4.1).
- The Bug 4 thread-safety regression test in
  ``test_review_fixes.py`` was rewritten to pin the new invariant:
  the global ``status_coverage._is_integrity_incomplete_union``
  must never be touched at runtime. Old test was a stopgap pinning
  the lock around the patch.

### Added

- **MEDIUM: Zero-return functions documented.** A function that
  declares a return type but has no ``return`` statement at all is
  silently passed by D24 (the existing skip-on-zero-returns rule
  defers to ring-close R3, which furqan-lint does not yet run).
  Added to README "Remaining limitations."
- Static test verifying ``.pre-commit-hooks.yaml`` declares
  ``furqan`` in ``additional_dependencies``.
- Network-dependent functional test (marked ``slow`` and ``network``;
  skipped under ``pytest -m "not network"``) that verifies the hook
  installs in a clean venv. Markers registered in ``pyproject.toml``.
- Regression test pinning ``github.action_ref`` in ``action.yml``.
- v0.4.1 bare-Union prose test asserting the fix string contains
  ``Union[X, None]`` and does NOT contain the degenerate
  ``Union[X]`` form.
- ``LC_ALL=C.UTF-8`` assertion in the CI em-dash workflow test.
- "Closed in v0.4.1" section in README documenting the retired
  monkey-patch and the now-installable pre-commit hook.

### Tests

- 5 new tests across ``test_action.py`` (1 static pre-commit dep
  check, 1 functional install test, 1 action_ref pin test) and
  ``test_round7_fixes.py`` (1 v0.4.1 bare-Union prose test). The
  Bug 4 thread-safety test was replaced with a kwarg-usage test;
  net-1 in ``test_review_fixes.py``. Locale assertion added to an
  existing CI-workflow test.
- Total: 150 (149 deselected under ``pytest -m "not network"``).

## [0.4.0] - 2026-05-02

Distribution and CI infrastructure. No new checker logic. The tool
becomes adoptable: three lines of YAML to wire it into a GitHub
Actions workflow, or three lines for a pre-commit hook.

### Added

- **GitHub Action.** ``action.yml`` at the repo root provides a
  composite action: ``uses: BayyinahEnterprise/furqan-lint@v0.4.0``
  with optional ``path``, ``python-version``, and
  ``furqan-lint-version`` inputs. Composite-runs (no Docker
  image), so cold-start is dominated by setup-python and pip
  install rather than container pull. Furqan is installed from
  GitHub (v0.11.1 pinned) since it is not yet on PyPI.
- **Pre-commit hook.** ``.pre-commit-hooks.yaml`` declares a
  single hook ``id: furqan-lint`` that runs ``furqan-lint check``
  scoped to ``types: [python]``. Users add three lines to
  ``.pre-commit-config.yaml`` to wire it in.
- **CI workflow.** ``.github/workflows/ci.yml`` runs the test
  suite on Python 3.10, 3.11, 3.12, and 3.13 in a matrix on every
  push and pull request to ``main``. Three quality gates per
  matrix cell: pytest (the 136 prior tests + 9 new structural
  tests), version-sync between ``__version__`` and
  ``pyproject.toml``, and an em-dash check across ``src/``,
  ``tests/``, and ``README.md``. CHANGELOG.md is intentionally
  excluded from the em-dash scan to avoid breaking on legitimate
  prior entries.
- **PyPI publishing scaffolding.** ``scripts/publish.sh`` is a
  documented build/upload script using ``build`` and ``twine``.
  NOT to be run by automation - PyPI credentials are held only by
  the project lead. ``pyproject.toml`` metadata verified for PyPI
  readiness: ``Repository`` and ``Issues`` URLs added under
  ``[project.urls]``.
- **CI badge.** README displays the CI workflow status at the
  top.

### Changed

- ``pyproject.toml`` dependency bumped from ``furqan>=0.10.1`` to
  ``furqan>=0.11.0``. The project has been verified to work with
  furqan v0.11.1 (the version the GitHub Action installs).
- README's intro line "v0.2.0 ships four checks" is now version-
  agnostic ("Four checks ship today") so it stops aging out at
  every release. Install instructions now show how to install
  Furqan from GitHub before installing furqan-lint, since Furqan
  is not on PyPI.

### Tests

- 5 new structural tests in ``tests/test_action.py`` for
  ``action.yml`` and ``.pre-commit-hooks.yaml`` shape.
- 4 new structural tests in ``tests/test_ci_workflow.py`` for the
  CI matrix, version-sync gate, and em-dash gate.
- Total: 145.

## [0.3.5] - 2026-05-02

Two corrective fixes promoting documented limitations to fixes.
Both items reproduced empirically against v0.3.4 before fixing.

### Fixed

- **try/except control flow modelling.** ``try.body`` and
  ``orelse`` are now combined into a single "success path" and
  wrapped with the handler chain in a synthetic ``IfStmt`` shape
  whose ``else_body`` is a right-folded chain of handler bodies.
  D24 now fires correctly when a function's only return path is
  inside a ``try`` block whose except handler falls through (the
  canonical mypy "Missing return statement" shape, documented as
  "Exception-driven fall-through" since v0.3.1). The control case
  ``try/except/else where every branch returns`` continues to PASS
  because both halves of the synthetic IfStmt all-paths-return.
  Returns inside ``finally`` continue to cover all paths because
  ``finalbody`` is spliced unconditionally. New helper:
  ``_build_try_handler_chain``. Per the project's stated decision,
  the unmatched-exception case is treated as exit-via-propagation,
  not fall-through.
- **PEP 604 ``None | None`` symmetry.** Now translates to a bare
  ``TypePath(base="None")``, mirroring the v0.3.3
  ``_is_all_none_union`` discipline (``Union[None]``) and the
  v0.3.4 ``_is_none_literal`` early branch
  (``Optional[None]``). All three optional-spelling paths produce
  structurally identical AST for the all-None case. Added an
  ``_is_none_literal`` early branch to the pipe-union arm of
  ``_translate_return_annotation``. Documented in v0.3.4 as a
  v0.4.0 candidate; promoted in v0.3.5 because the fix shape was
  symmetric with the existing two paths and required no new
  infrastructure.

### Changed

- Removed the "Exception-driven fall-through" entry from the
  README's "Remaining limitations" section.
- Removed ``tests/fixtures/documented_limits/try_body_no_exception_modeling.py``
  (the closed limit). The other try-related fixture
  (``try_body_only_returns_in_block.py``) is preserved because it
  pins a different limit (D24's skip-on-zero-returns rule for
  ring-close R3 territory), which is unaffected by the v0.3.5 fix.
- Removed ``tests/fixtures/documented_limits/redundant_pipe_none.py``
  (the v0.3.4 PEP 604 pin) and the corresponding two pinning tests.

### Tests

- 10 try/except regression tests in ``tests/test_round8_fixes.py``
  (probe11 and probe12 shapes, finally-return, multi-handler with
  one falling through, bare except, return_none inside try, nested
  try in if).
- 4 PEP 604 None|None symmetric tightening tests in the same file.
- 3 doc-limit tests removed: 1 for the closed try-body limit and 2
  for the closed PEP 604 redundant-None limit.
- Total: 136.

## [0.3.4] - 2026-05-02

Three quality-tier observations from Fraz's round-7 review of
v0.3.3, none blocking. All three are asymmetries between code
paths that currently produce correct answers but for incidental
reasons rather than structural ones. v0.3.4 closes the two
structural ones and pins the third as a documented limitation.

### Fixed

- **`Optional[None]` symmetry with v0.3.3 `Union[None]`.** The
  Optional path produced `UnionType(left=TypePath("None"),
  right=TypePath("None"))` on `Optional[None]`, while the v0.3.3
  Union path produced a bare `TypePath(base="None")` on
  `Union[None]`. Both arrived at correct answers (no diagnostic
  fires either way), but only the Union path was structurally
  defended; a binary union of identical types is not semantically
  meaningful and would break the day someone refactors the matcher
  to require distinct arms. v0.3.4 mirrors the v0.3.3 discipline:
  `_translate_return_annotation` short-circuits `Optional[None]`
  to bare `TypePath(base="None")` (`typing.Optional[None]`
  evaluates to `type(None)` at Python runtime). Caught by
  Observation 1.
- **Bare `Optional` and bare `Union` no longer suggest invalid
  fixes.** A function declared `-> Optional` (no subscript) with
  a `return None` body produced a `return_none_mismatch` whose
  `minimal_fix` suggested `Optional[Optional]`, which is invalid
  typing syntax (mypy rejects bare `Optional` with "Bare Optional
  is not allowed"). The same incoherent suggestion applied to
  bare `Union`. v0.3.4 introduces `_suggested_fix` in
  `return_none.py` that detects the bare-name case and suggests
  the real fix (add a type argument: `Optional[X]` or `X | None`).
  Caught by Observation 3.

### Added

- `tests/test_round7_fixes.py` with 7 tests pinning the two
  structural fixes:
  - 4 tests on `Optional[None]` translation (bare `TypePath`,
    not binary `UnionType`, end-to-end PASS, and a negative test
    that `Optional[str]` still produces the expected
    `UnionType(str, None)` shape).
  - 3 tests on `_suggested_fix` (bare `Optional` produces
    helpful prose without the `Optional[Optional]` artifact, bare
    `Union` produces the symmetric helpful prose, and a negative
    test that normal `TypePath`s still get the canonical
    `Optional[<name>]` suggestion).
- `tests/test_documented_limits.py` gains
  `test_round7_redundant_pipe_none_passes` (+1 test) pinning the
  current correct-but-incidental behaviour on PEP 604 redundant
  `None` arms (Observation 2). New fixture
  `tests/fixtures/documented_limits/redundant_pipe_none.py`.
  README and `tests/fixtures/documented_limits/README.md` updated
  with the new entry.

### Tests

- 116 -> 124 (+8). All v0.3.3 tests pass identically.

### Unchanged

- The v0.3.3 `Union[None, ...]` boundary fix (`_is_union_with_none`
  predicate, `_is_all_none_union` helper, defense-in-depth
  assertion). The v0.3.4 Optional short-circuit applies the same
  discipline pattern to a parallel code path.
- `Optional[X]` for non-`None` `X` translates to
  `UnionType(X, None)` exactly as before.
- All other documented limitations and their fixtures.

### Deferred

- **PEP 604 redundant `None` arms** (Observation 2). `int | None
  | None` and `None | None` are correctly accepted today; the
  intermediate AST is incidentally correct but not structurally
  defended the way the `Union[None]` and `Optional[None]` paths
  are. Full symmetric tightening across the three optional
  spellings is a v0.4.0 candidate.

---

## [0.3.3] - 2026-05-02

One blocking finding plus two cleanup items from Fraz's round-6
review of v0.3.2. The blocking finding (a hard crash on degenerate
`Union[None, ...]` shapes) was reproduced empirically against the
v0.3.2 release on three concrete inputs before fixing.

### Fixed

- **`Union[None, ...]` boundary crash (BLOCKER).** v0.3.2's
  `_extract_union_with_none_inner` raised `IndexError: list index
  out of range` on `Union[None]`, `Union[None, None]`, and
  `Union[None, None, None]`. All three are legal Python that mypy
  accepts (`typing.Union[None]` evaluates to `type(None)` at
  runtime). Same shape of failure as the original Furqan parser
  RecursionError bug from round 3: an unstructured Python
  exception on a shape of legal input the matcher did not
  anticipate. The fix tightens `_is_union_with_none` to require
  *both* a `None` arm AND a non-None arm, so the predicate is
  the truthful contract of what `_extract_union_with_none_inner`
  can satisfy. Degenerate all-None Unions fall through to the
  ordinary type-translation path. A defense-in-depth `assert`
  inside `_extract_union_with_none_inner` names the precondition
  so a future caller that skips the predicate fails loudly with
  a contract message instead of `IndexError`.
- **Aliased `Union` imports documented.** v0.3.2's Finding 1
  matcher accepts the bare `Union` head by name without checking
  import provenance, so `from somelib import Union; -> Union[X,
  None]` is treated as `typing.Union[X, None]` even when
  `somelib.Union` is unrelated. Symmetric to the existing
  aliased-`Optional` limitation. README's "Aliased Optional
  imports" entry is now "Aliased Optional / Union imports" and
  covers both. New fixture `tests/fixtures/documented_limits/aliased_union_import.py`
  pins the current behaviour. Same fix shape as the Optional
  case (symbol-table tracking), deferred to a future phase.
- **Local-class limitation extended to method bodies.** The
  README's "Local classes inside function bodies" entry was
  rephrased to "Local classes inside any function or method
  body." The underlying behaviour was already symmetric (the
  function walker does not descend into nested `ClassDef`
  regardless of whether the parent `FunctionDef` is at module
  scope or inside another `ClassDef`); only the documentation
  needed to catch up.

### Added

- `tests/test_round6_fixes.py` with 7 tests pinning:
  - 3 tests on each degenerate Union shape (no crash on
    translate, no crash through full pipeline).
  - `_is_union_with_none` rejects all-None Unions (predicate
    truthfulness).
  - `_is_union_with_none` still accepts the v0.3.2 Finding 1 happy
    path (negative test against an over-correction).
  - The defense-in-depth assertion fires with a contract-naming
    message when called on a Union with no non-None arms.
  - End-to-end pipeline runs clean on the degenerate input.
- `tests/test_documented_limits.py` gains
  `test_aliased_union_import_treated_as_typing_union` (+1 test)
  pinning the new fixture.
- `tests/fixtures/documented_limits/aliased_union_import.py` (new
  fixture). `tests/fixtures/documented_limits/README.md` updated
  with the new entry and the rephrased Local-classes entry.

### Tests

- 108 -> 116 (+8). All v0.3.2 tests pass identically.

### Unchanged

- The v0.3.2 Finding 1, 2, 3 fixes (Union recognition, string
  forward-references, nested-class method collection). The v0.3.3
  boundary fix tightens the predicate of Finding 1; it does not
  weaken any of the recognition shapes added in v0.3.2.
- All other documented limitations and their fixtures.
- `_extract_union_with_none_inner`'s positive-path return shape
  (single non-None arm returns directly; 2+ non-None arms
  left-fold into `BinOp(BitOr)`).

---

## [0.3.2] - 2026-05-02

Three findings from Fraz's round-5 review of v0.3.1, all reproduced
empirically against v0.3.1 before fixing. One adjacent observation
pinned as a documented limitation.

### Fixed

- **`Union[X, None]` recognition (MAJOR).** The matcher now
  accepts `Union[X, None]`, `Union[None, X]`, `Union[X, Y, None]`,
  and the `typing.Union` / `t.Union` aliased forms as Optional.
  Pre-v0.3.2 the matcher only handled `Optional[X]` and `X | None`;
  pre-PEP 604 codebases (still common) routinely use `Union[X, None]`
  and were producing a false-positive `return_none_mismatch`.
  New helpers: `_is_union_with_none`, `_extract_union_with_none_inner`,
  `_is_union_head`, `_slice_elements`, `_slice_contains_none`,
  `_is_none_literal`. The 3+ arm Union case collapses the non-None
  arms to a `BinOp(BitOr)` shape so Furqan's binary `UnionType` can
  represent it.
- **String forward-reference annotations (MAJOR).** When
  `_translate_return_annotation` sees an `ast.Constant` with a
  string value, the value is parsed via `ast.parse(..., mode='eval')`
  and the translator recurses into the resulting expression. The
  TYPE_CHECKING / PEP 484 forward-reference idiom (`-> "Optional[User]"`)
  no longer produces a false positive. Unparseable strings fall
  through gracefully to a bare `TypePath`.
- **Nested class methods (MAJOR).** `_translate_module` now calls
  a new recursive helper `_collect_class_methods` instead of a
  single-level inline loop. Methods of `Outer.Inner.method`,
  `Outer.Mid.Inner.method`, etc. are now collected and visible
  to D24 and `return_none_mismatch`. Pre-v0.3.2, descent stopped
  at one level and inner-class methods were silently dropped.

### Documented

- **Local classes inside function bodies.** A class defined inside
  a function body still has its methods silently dropped. The
  argument for keeping it: a local class is a private
  implementation detail (closure-like return value), not part of
  the module's public contract. Pinned as
  `tests/fixtures/documented_limits/local_class_in_function.py`
  with a corresponding entry in `test_documented_limits.py`.
  README updated under "Remaining limitations."

### Tests

- 14 new regression tests in `tests/test_round5_fixes.py`.
- 1 new pinning test in `tests/test_documented_limits.py`.
- Total: 108.

## [0.3.1] - 2026-05-02

Three small items from Fraz's round-4 review of v0.3.0. The bulk of
v0.3.1 is documentation; one substantive prose fix, two limitations
surfaced and pinned as fixtures.

### Fixed

- **Multi-segment annotation rendering (Quality).** `_annotation_name`
  now recurses into `ast.Attribute.value` and renders the full
  dotted path (`weird.lib.Optional`) rather than just the leaf attr
  (`Optional`). The substantive Bug 5 fix in v0.3.0 correctly
  rejected `weird.lib.Optional[X]` from the `_is_optional` matcher,
  but the diagnostic prose still read `declares -> Optional` and
  suggested `Optional[Optional]` as the fix, which was incoherent.
  v0.3.1 produces `declares -> FakeOptional.Optional` with fix text
  `Optional[FakeOptional.Optional]`. The Bug 5 regression test now
  asserts the prose substring rather than only the marad count.

### Documentation

- **Two `Remaining limitations` entries surfaced.** v0.3.0 introduced
  one consequence of its compound-statement fix (`match` cases
  wrapped as maybe-runs, so structurally exhaustive matches
  under-claim coverage) under `Remaining limitations`, but two
  others were buried in the adapter docstring or absent entirely:
  - **Exception-driven fall-through.** `try` bodies are spliced as
    always-running. A function whose only return is inside a `try`
    block is not flagged by D24 even though an exception in that
    block would prevent reaching the return.
  - **Aliased `Optional` imports.** `from typing import Optional as
    MyOpt; -> MyOpt[X]` is treated as a non-Optional return type.
    The matcher recognises the bare `Optional` name and the
    qualified `typing.Optional` / `t.Optional` forms only.
  Both are pre-existing behaviours; the v0.3.0 fix tightening made
  them more visible. v0.3.1 surfaces them in the README at the same
  level as the existing limitations.
- **`tests/fixtures/documented_limits/` directory.** Each
  `Remaining limitations` entry that has a concrete reproducer now
  has a fixture and a test in `tests/test_documented_limits.py`
  pinning the current behaviour. A future fix that closes the
  limitation breaks the test deliberately; a regression to even
  worse behaviour also breaks it. The discipline is borrowed from
  Bayyinah's adversarial gauntlet directories.

### Tests

- 3 new tests in `tests/test_documented_limits.py` (two
  exception-driven fall-through, one aliased Optional). The Bug 5
  regression test gains two prose-substring assertions. Total: 93
  (was 90).

## [0.3.0] - 2026-05-02

Six fixes from Fraz's three-round review of v0.2.0. All findings
reproduced empirically before fixing.

### Fixed

- **Compound statements (CRITICAL).** `_translate_body` now handles
  `for`, `async for`, `while`, `with`, `async with`, `try`, and
  `match`. `for`/`while` bodies wrap as `IfStmt(opaque, ..., ())`
  so D24 does not over-claim coverage when a function's only
  return is inside a loop. `with` and `try` bodies splice up
  unconditionally; `except` handlers and `match` cases each wrap
  in a maybe-runs `IfStmt`. Without this fix, a function whose
  body lives entirely inside a compound statement was invisible
  to D24, D11, and `return_none_mismatch`.
- **Additive surface (CRITICAL).** `_extract_public_names` now
  collects `ast.AnnAssign` (PEP 526 annotated module constants
  like `MAX_RETRIES: int = 5`) and tuple-target assignments
  (`A, B = 1, 2`). Annotated `__all__` declarations are also read.
- **Dynamic `__all__` (CRITICAL).** `check_additive_api` now raises
  `DynamicAllError` when `__all__` is not a static list/tuple of
  string literals, and the CLI maps this to exit code 2 with an
  `INDETERMINATE` diagnostic. Prior behaviour silently returned
  the empty set, which produced a false-positive cascade reporting
  every previously-public name as removed.
- **Thread-safety of D11 monkey-patch (MAJOR).** A
  `threading.Lock` serialises entry to `_python_optional_mode`.
  Concurrent context-manager entry on multiple threads no longer
  leaks the patched predicate. Stopgap; the structural fix is
  upstream support for a `producer_predicate` parameter on
  `check_status_coverage`.
- **`Optional` matcher tightness (MINOR).** `_is_optional` now
  requires the `Attribute` form to have a `Name` root whose id is
  `typing` or `t`. Annotations like `weird.lib.Optional[X]` are
  no longer misclassified.

### Quality

- **`BinOp` annotation rendering.** `_annotation_name` now recurses
  into `BitOr` unions and joins with `|`. Diagnostics for
  `int | str` no longer suggest `Optional[Unknown]` as the fix.

### Tests

- 21 new regression tests in `test_review_fixes.py`. Total: 90.

## [0.2.0] - 2026-05-02

### Added

- Additive-only API checker: `furqan-lint diff old.py new.py`
  compares two versions of a module's public surface and fires
  on removed names. `__all__` takes precedence; without it, every
  top-level non-underscore name is part of the public API.
- Return-None type checker: catches `return None` and bare `return`
  in functions declaring non-Optional return types. Closes the
  Phase 1 D24 return-None blind spot.

### Fixed

- Nested function calls are no longer attributed to the enclosing
  function. A call inside a closure or inner function (or inside a
  class method defined inside a function) is dropped from the outer
  function's call list. Closes Phase 1 nested-function gap.
- Decorator calls on a function are no longer collected as calls
  inside the function's body.

### Notes

- Lambdas and comprehensions are inline expressions, not separate
  scopes; calls inside them remain attributed to the enclosing
  function. This is intentional.

## [0.1.0] - 2026-05-02

### Added

- Python AST adapter translating `ast.Module` to Furqan `Module`.
- D24 (all-paths-return) on Python via direct adaptation.
- D11 (status-coverage) via a context-managed monkey-patch that
  treats `Optional[X]` as the producer pattern.
- CLI: `furqan-lint check <file.py|directory/>` and
  `furqan-lint version`.
- 41 tests.
