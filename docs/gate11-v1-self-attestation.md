# Gate 11 v1.0 self-attestation (successor to Tasdiq al-Bayan)

## Phase G11.5 (successor; out-of-v0.14.0 scope)

After Phase G11.4 Tasdiq al-Bayan ships (v0.14.0), the
foundation is in place for v1.0 self-attestation:
furqan-lint signs its own releases with gate11.

This document is normative for the scope of v1.0
self-attestation as a separate successor phase to v0.14.0. It
is **not** part of the v0.14.0 ship; it documents the boundary
between Tasdiq al-Bayan (corpus / verification infrastructure)
and v1.0 (self-attestation / signing surface).

## What v1.0 self-attestation means

v1.0 self-attestation is the structural-honesty thesis applied
to the project itself:

> The tool that catches drift in other people's code must not
> have drift in its own (v0.4.1+ self-check).
>
> The tool that attests other projects' supply-chain integrity
> must attest its own (v1.0+ self-attestation).

Concretely, v1.0+ each release of furqan-lint ships with a
gate11 manifest that:

  - Names the linter version, the four-substrate verifier
    surfaces (Python / Rust / Go / ONNX), the checker set hash
    for each substrate
  - Is signed via Sigstore with the project lead's identity
    (or the CI ambient OIDC identity per release.yml)
  - Is verifiable by any Relying Party using
    `furqan-lint manifest verify` against the released
    manifest

A Relying Party verifying furqan-lint's own attestation is
verifying using furqan-lint -- the verification surface and
the artifact-being-verified are the same code. This is the
structural-honesty thesis closing on itself.

## Why the corpus is the prerequisite

v1.0 self-attestation depends on four-substrate parity because
furqan-lint covers four substrates (Python, Rust, Go, ONNX)
and each substrate's verifier MUST behave consistently for a
Relying Party to rely on the attestation. The Tasdiq al-Bayan
corpus from v0.14.0
(`tests/test_gate11_cross_substrate_corpus.py`) verifies this
parity empirically. Without the corpus, parity is aspirational;
with the corpus, parity is mechanically enforced.

Specifically, v1.0 self-attestation relies on the corpus to
guarantee:

  1. **Identity-policy parity (CASM-V-032 / CASM-V-035)**:
     the four verifiers refuse-without-policy by default and
     enforce expected_identity identically. A Relying Party
     verifying furqan-lint's own release manifest can trust
     that the substrate's identity-policy semantics are
     consistent regardless of which substrate's signing
     surface produced the manifest.
  2. **Identity-extraction parity (CASM-V-036)**: H-5 closure
     across the chain (Phase G11.1 amended_4 + at-Tawbah
     backport + propagation through G11.2 + G11.3) ensures
     all four verifiers raise CASM-V-036 on identity-extraction
     TypeError rather than returning string sentinels.
  3. **trusted_root threading**: F-RN-1 v1.5 absorption pattern
     (getattr(args, 'trust_config', None) or TrustConfig())
     applies uniformly across all four `_verify_*` facades.
  4. **CLI dispatch four-entry closure**: function-local
     `_LANGUAGE_DISPATCH` inside `verification.verify()`
     covers all four substrates; no orphan dispatch entries.

The corpus mechanically verifies all four invariants on every
test run. v1.0 self-attestation builds on this verified
foundation.

## v1.0 scope (separate phase post-Tasdiq al-Bayan)

The v1.0 phase is **out of v0.14.0 scope**. v0.14.0 ships the
corpus; v1.0 ships the self-attestation. The v1.0 phase will:

  1. **Generate gate11 manifests for furqan-lint itself at
     release time** (one per substrate that furqan-lint ships
     code in: Python, plus the Go binary `goast` if
     reproducibly buildable).
  2. **Sign the manifests via Sigstore at release time**: the
     existing release.yml (al-Mubin v0.11.1 T01 PyPI verify +
     T02 gh release create) extends with T03 manifest sign +
     T04 manifest publish steps.
  3. **Document the self-attestation surface** in README and
     SECURITY.md (new sections; documented-limit shape for any
     residual disclosures).
  4. **Add a `furqan-lint manifest verify-self` subcommand**
     that downloads the release's manifest from the release
     artifact and verifies it using the locally-installed
     furqan-lint's gate11 verifier.

The v1.0 phase will be its own canonical mushaf chain entry
with its own Quranic anchor (to be chosen at v1.0 dispatch
time). Tasdiq al-Bayan is the prerequisite, not v1.0 itself.

## What v0.14.0 does NOT ship (and why that is correct)

v0.14.0 does NOT introduce v1.0 self-attestation. The
separation is principled per the framework's substrate-tight
discipline:

  - **Corpus and signing surface are different concerns**:
    the corpus is verification infrastructure (test code that
    runs in CI); the signing surface is production
    infrastructure (manifest generation + Sigstore signing at
    release time). Bundling them would violate the
    substrate-tight discipline (a regression in the corpus
    would block a release; a regression in signing would
    invalidate corpus tests).
  - **v1.0 self-attestation requires the corpus as a
    precondition**: shipping self-attestation before the
    parity corpus is in place would ship an attestation
    surface whose multi-substrate behavior was only
    aspirationally verified. Tasdiq al-Bayan provides the
    empirical-verification ground that v1.0 self-attestation
    will rely on.
  - **Two phases give two CHANGELOG entries**: separate
    delete-plus-add records for the corpus (v0.14.0) and the
    self-attestation surface (v1.0). A Relying Party reviewing
    the CHANGELOG can see the substrate-tight progression.

The v0.14.0 -> v1.0 transition is the structural-honesty
thesis closing on itself: the tool that attests other
projects' supply-chain integrity attests its own. Tasdiq
al-Bayan provides the verification surface v1.0 will rely on.

## Cross-references

- `tests/test_gate11_cross_substrate_corpus.py` -- the corpus
  v1.0 self-attestation depends on
- `tests/test_gate11_cross_substrate_drift_detection.py` --
  the drift-detection meta-test enforcing corpus-as-contract
- `docs/gate11-symmetry.md` -- the four-substrate parity table
  mechanically enforced by the corpus from v0.14.0+
- `docs/onnx-attestation-boundary.md` -- the attestation
  surface boundary for ONNX (Class A / B / C decision
  flowchart) that v1.0 self-attestation will inherit
- `SAFETY_INVARIANTS.md` Invariant 6 step 8 ONNX-specific
  extension -- the CASM-V-070 / CASM-V-071 enforcement layer
- `CHANGELOG.md` v0.14.0 entry -- the canonical record of
  Tasdiq al-Bayan ship + v1.0 prerequisite declaration

La hawla wa la quwwata illa billah.
