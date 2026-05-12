# Gate 11 self-attestation (v1.0+)

## Phase G12.0 (al-Basirah; canonical mushaf chain closing)

From v1.0 onward, furqan-lint signs its own releases with
gate11. The structural-honesty thesis closes on itself: the
tool that catches drift in others' code attests its own.

This document is normative for Relying Parties verifying
furqan-lint's own gate11 self-attestation. It is paired with
``docs/gate11-v1-self-attestation.md`` (the v1.0 prerequisite
scope document shipped at Tasdiq al-Bayan / v0.14.0) and
``SAFETY_INVARIANTS.md`` Invariant 6 step 8 ONNX-specific
extension + CASM-V-072 allocation.

## Verification by Relying Parties

```bash
pip install furqan-lint
furqan-lint manifest verify-self \
  --expected-identity "https://github.com/BayyinahEnterprise/furqan-lint/.github/workflows/release.yml@refs/tags/v1.0.0" \
  --expected-issuer "https://token.actions.githubusercontent.com"
```

The ``--expected-identity`` pattern MUST be configured for
production verification per the CASM-V-035 default refuse-
without-policy discipline (at-Tawbah T02). The pattern
should match the BayyinahEnterprise GitHub Actions release
workflow's Sigstore-OIDC signing identity (canonical
identity-rooted-in-release-yml convention) or the project
lead's personal signing identity per local-build
attestation.

For verifying a specific release (not the installed version):

```bash
furqan-lint manifest verify-self --version 1.0.0 \
  --expected-identity "<pattern>" \
  --expected-issuer "https://token.actions.githubusercontent.com"
```

## What is attested

The gate11 self-manifest covers:

* The Python checker source files in
  ``gate11/_pinned_checker_sources_self.py``
  ``PINNED_CHECKER_SOURCES_SELF`` tuple (Form A
  checker_set_hash per H-6 corrective at v0.11.2 at-Tawbah)
* The linter version + name + ``module_identity.language ==
  "python"`` (Python wheel substrate; dispatch routes via
  function-local ``_LANGUAGE_DISPATCH`` -> ``_verify_python``
  per al-Mursalat T04 + an-Naziat F-NA-3 closure)
* The signing identity (a Sigstore-issued certificate from
  the GitHub Actions ambient-OIDC flow at release time)
* The signing time (logged in Sigstore's Certificate
  Transparency log)

## What is NOT attested in v1.0

* The ``cmd/goast/main.go`` Go binary's structural integrity
  (the goast binary is shipped pre-compiled in the Python
  wheel; reproducible-build attestation is deferred per
  ``docs/gate11-symmetry.md`` self-attestation row "Go:
  DEFERRED" cell and per §5.1 step 4 failure mode #4 of the
  al-Basirah dispatch prompt; v1.x candidate for closure
  when Go ecosystem reproducible-build tooling matures)
* Initializer data, fixtures, or test files not in the
  pinned source list at
  ``_pinned_checker_sources_self.py``
* Documentation, CHANGELOG entries, or other non-source
  artifacts (the attestation surface is the checker code's
  integrity; non-source artifacts are out of scope)
* Rust source (furqan-lint does not ship Rust source; the
  Rust verifier substrate at ``gate11/rust_verification.py``
  IS in the pinned list, but no external Rust crate is
  shipped per the v0.11.0 Phase G11.1 charter)
* ONNX models (furqan-lint does not ship ONNX models)

## CASM-V-072 self-attestation-failure (substrate-actual)

Per F-BA-substrate-conflict-1 v1.0.0 closure (mirror of
F-TAB-2 v0.14.0 pattern): the substrate-actual CASM-V code
for self-attestation-failure is **CASM-V-072**, NOT the
prompt-cited 040 (which is in-use at v0.10.0+ baseline for
module_root_hash mismatch per Invariant 6 step 7).

Three sub-conditions surface CASM-V-072 with named
sub-condition in the error message:

* **(a) manifest-not-found**: the convention-based URL
  ``https://github.com/BayyinahEnterprise/furqan-lint/releases/download/v${VERSION}/self_manifest.json``
  returns 404 OR the network fetch fails. Remediation: verify
  the release was tagged and release.yml T06 step completed
  successfully (operator runbook at
  ``docs/release-checklist.md`` Self-attestation discovery
  section).

* **(b) checker-set-hash-drift**: the manifest's
  checker_set_hash claim does not match the computed sha256
  over the installed pinned source list. Remediation:
  investigate substrate divergence; this is a Naskh
  Discipline event requiring CHANGELOG entry per framework
  section 10.2 procedure.

* **(c) signature-verification-unexpected**: the underlying
  Sigstore verification fails with a mode not already
  covered by CASM-V-030..036 (typed identity-path errors
  pass through unchanged). Remediation: investigate
  Sigstore bundle integrity per the upstream Sigstore
  project guidance.

## Trust model

Self-attestation does not eliminate the need for external
trust. It locates the trust at the Sigstore Certificate
Transparency log layer: a Relying Party trusts that
Sigstore's CT log is honestly maintained and that the
project lead's (or BayyinahEnterprise organization's)
signing identity is correctly attested at that layer. The
recursion bottoms out at this trust anchor outside the
project.

Without the CT log, self-attestation would be aspirational;
with it, the recursion has a foundation. This is the
structural-honesty thesis applied to the chain itself:
trust is located explicitly at the external rung
(Sigstore CT) rather than at the linter-vendor layer.

## Cross-references

* ``docs/gate11-v1-self-attestation.md`` (Tasdiq al-Bayan T07
  scope reference) -- the v1.0 prerequisite-document shipped
  at v0.14.0; this document is the implementation reference
* ``docs/release-checklist.md`` Self-attestation discovery
  section (al-Basirah T04) -- operator runbook
* ``SAFETY_INVARIANTS.md`` Invariant 6 step 8 ONNX-specific
  extension + CASM-V-072 allocation (al-Basirah T01)
* ``docs/gate11-symmetry.md`` self-attestation row (al-Basirah
  T06) -- four-substrate parity table extension with honest
  asymmetries (Python v1.0+; Rust N/A; Go DEFERRED; ONNX N/A)
* ``CHANGELOG.md`` v1.0.0 entry -- canonical record of
  al-Basirah ship + canonical mushaf chain closing

La hawla wa la quwwata illa billah.
