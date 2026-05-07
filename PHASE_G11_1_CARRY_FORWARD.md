# Phase G11.1 (as-Saffat) carry-forward

Date: 2026-05-07
Phase: G11.1 (Sigstore-CASM Gate 11 Rust extension)
Substrate baseline: BayyinahEnterprise/furqan-lint at the
`v0.10.0` ship (commit `8a2f0fc`)
Branch: `phase-g11-1-as-saffat`
Tag (assigned at release): `v0.11.0`
Anchor: Surah as-Saffat 37:1-3

## Status

Shipped: Sigstore-CASM Gate 11 v1.0 Rust extension. Closes
audit findings C-1, H-4, H-5, H-6, M-6, M-7 prospectively for
the Rust pipeline AND backports the corrections to the Python
pipeline so the v0.10.0 audit gaps do not persist beyond v0.11.0.

## Deliverable

- New `[gate11-rust]` optional extra (sigstore-python +
  rfc8785 + tree-sitter-rust).
- New `furqan_lint.gate11.rust_surface_extraction` module
  (T02): walks tree-sitter-rust CST top-level items; emits
  ASCII-sorted CASM v1.0 `public_surface.names` entries for
  function / struct / enum / trait / type_alias / constant /
  alias kinds.
- New `furqan_lint.gate11.rust_signature_canonicalization`
  module (T03): per-kind canonical signatures hashed via
  SHA-256 over rfc8785-canonical bytes. The H-4 propagation
  defense (rules 6 + 7: nested generics MUST recurse element-
  wise; multi-argument generic parameters MUST be iterated as
  AST nodes, never stringified).
- New `furqan_lint.gate11.rust_manifest` module (T04):
  `build_manifest_rust(...)` constructs a CASM v1.0 manifest
  with `language: "rust"`, `extraction_method:
  "tree-sitter.rust-public-surface@v1.0"`, and the
  audit-corrective `checker_set_hash` discipline (Form A
  substantive default; Form B `placeholder:sha256:` opt-in).
- New `furqan_lint.gate11.checker_set_hash` module (T04.1):
  the substantive hash computation over the pinned checker
  source-file tuple. Backports to the Python manifest builder
  in the same commit so the v0.10.0 H-6 finding is closed for
  Python.
- Verifier corrections in `furqan_lint.gate11.verification`
  (T05.2/3/4): `step6_verify_sigstore` grows
  `expected_identity` / `expected_issuer` /
  `allow_any_identity` kwargs; refuse-without-policy default
  raises `CASM-V-035`; `trusted_root` argument is consumed via
  `Verifier(_inner=trusted_root)`; `_extract_identity` raises
  typed `CASM-V-036` rather than returning string sentinels.
- CLI dispatch on `.rs` vs `.py` (T05.1) in
  `furqan_lint.gate11.cli`. Bundle filename preserves source
  extension (`foo.rs` -> `foo.rs.furqan.manifest.sigstore`).
- Top-level `furqan-lint check --gate11` extends the flag
  surface with `--expected-identity`, `--expected-issuer`,
  `--allow-any-identity`, `--force-refresh`.
- Three new CASM-V error codes (T05 + amended_4): CASM-V-032
  (identity policy mismatch), CASM-V-035 (no identity policy
  supplied), CASM-V-036 (identity extraction failure).
- New CI job `gate11-rust-smoke-test` (T06): push-to-main only,
  `id-token: write`, end-to-end OIDC sign + verify on a
  fixture .rs module via the GitHub Actions ambient identity.
- Documentation updates (T07): README "Sigstore-CASM Gate 11
  (Rust extension)" subsection covering install, CLI surface,
  identity-policy enforcement, documented limits; "Closed in
  v0.11.0" section enumerating C-1, H-4, H-5, H-6, M-6, M-7
  closures; SECURITY.md identity-policy paragraph;
  CONTRIBUTING.md gate11_rust testing section.
- Five documented-limits fixtures and pinning tests (T08):
  lifetime_stripped_from_signature, impl_methods_omitted_from_surface,
  trait_object_literal_text, macro_call_signed_pre_expansion,
  pub_crate_excluded.

Test count: 502 (v0.10.0 ship state) -> v0.11.0 ship state.
Tests added: 5 (T08 documented-limits) + 7 (T05 CLI) + 9 (T04
manifest) + 15 (T03 canonicalization) + 13 (T02 surface) = 49
new Rust tests, plus updates to two existing G11.0 tests.
ruff check + ruff format + mypy all clean.

## Findings closed in v0.11.0

| Finding | Severity | Surface | Closure |
|---------|----------|---------|---------|
| C-1 | CRITICAL | Identity policy gap (verifier accepted any signature) | T05.2 refuse-without-policy default; CASM-V-035; --expected-identity flag; backported to Python |
| H-4 | HIGH | Nested-generic tuple-stringification (Python H-4 failure mode) | T03 rules 6 + 7 element-wise recursion; five nested-generic pinning fixtures |
| H-5 | HIGH | trusted_root argument discarded by verifier | T05.3 Verifier(_inner=trusted_root) lower-level constructor |
| H-6 | HIGH | checker_set_hash placeholder dressed as commitment | T04.1 Form A substantive hash by default; Form B placeholder: prefix; backported to Python |
| M-6 | MEDIUM | README claim without substrate (typosquatting pinning) | T07 README documents --expected-identity flag explicitly |
| M-7 | MEDIUM | String sentinels for identity extraction | T05.4 typed CASM-V-036 errors |

## Findings deferred to a later phase

- **Method-level Rust signing**: impl-block methods are not in
  the v1.0 public-surface fingerprint. Closure path: v1.5
  horizon, requires extending the surface-extraction algorithm
  to walk impl blocks.
- **Lifetime-aware canonical types**: lifetimes are stripped
  during fingerprinting so semantic equivalence under lifetime
  rename is preserved. Closure path: v1.5 horizon if a downstream
  consumer requires lifetime-aware fingerprints.
- **Trait-object semantic equivalence**: `Box<dyn Trait + 'a>`
  is fingerprinted as `Box<dyn Trait>`; bound differences beyond
  the first identifier are erased. Closure path: v1.5 horizon
  with a separate trait-bound-aware canonical form.
- **Macro-expansion-aware signing**: macros are signed at the
  source level. Closure path: v2 horizon (requires sigstore-rs
  FFI to leverage rustc's macro-expansion infrastructure).
- **sigstore-rs-implemented signing**: v1 reuses sigstore-python.
  Closure path: v1.5 horizon, FFI bridge to sigstore-rs for
  Rust-native bundles.

## Carry-forward to subsequent phases

- **Phase G11.2 (al-Mursalat, Go)**: reuse the audit-corrective
  substrate landed here. The `checker_set_hash` discipline,
  `Identity` policy CLI surface, and `_extract_identity` typed
  errors are universal. Phase G11.2 ships
  `goast.go-public-surface@v1.0` extraction method and
  language="go" schema acceptance.
- **Phase G11.3 (an-Naziat, ONNX)**: same substrate reuse.
  ONNX's "module source" is the protobuf-serialized model
  bytes; module canonicalization rules apply directly.
- **Phase G11.4 (Tasdiq al-Bayan, Cross-Verification)**: builds
  the cross-substrate test corpus consuming the .rs bundles
  produced by this phase. The Phase G11.4 corpus MUST exercise
  CASM-V-032, CASM-V-035, CASM-V-036, plus all v0.10.0 codes.
- **Phase G11.0.1 corrective release scope**: the Python
  pipeline's audit findings (C-1, H-5, H-6, M-7) are closed
  in this v0.11.0 ship via backport. A follow-up corrective
  release prompt is not strictly necessary; the audit
  register entries can close against v0.11.0.

## Substrate verification

- `pytest --collect-only -q` -> 549 tests collected (502
  v0.10.0 baseline + 49 Rust + minor updates).
- `pytest -q` -> all-green (skips include the existing live-
  OIDC smoke gate plus the new gate11-rust-smoke-test which
  needs FURQAN_LINT_GATE11_SMOKE_TEST=1).
- `ruff check .` and `ruff format --check .` clean.
- `mypy src/furqan_lint` clean.
- Em-dash sweep clean.

## Round-numbering check

Phase G11.1 follows G11.A (al-Fatiha, foundational invariants)
and G11.0 (Kiraman Katibin, Python). Precedes G11.2
(al-Mursalat, Go), G11.3 (an-Naziat, ONNX), G11.4 (Tasdiq
al-Bayan, Cross-Verification), and Phases G11.5 through G11.12
on the v1.5+ horizon.

End of Phase G11.1 carry-forward.
