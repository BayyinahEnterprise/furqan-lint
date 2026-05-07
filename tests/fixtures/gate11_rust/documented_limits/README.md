# Phase G11.1 (as-Saffat) Rust Sigstore-CASM documented limits

Each fixture in this directory pins a current furqan-lint Rust
adapter behaviour that holds in v1.0 of the Sigstore-CASM
substrate. If a future improvement changes the adapter's
behaviour, the pinning test in
``tests/test_gate11_rust_documented_limits.py`` will fail and
force the change to surface as either a Naskh Discipline
schema/invariant update OR an explicit retirement of the
documented limit per framework section 10.2 retirement
procedure.

## Fixture inventory

- ``lifetime_stripped_from_signature``: lifetimes are stripped
  during canonicalization; ``f<'a>(s: &'a str)`` and
  ``f<'b>(s: &'b str)`` produce identical fingerprints. v1.5
  horizon: lifetime-aware canonical types.
- ``impl_methods_omitted_from_surface``: impl-block methods
  are not part of the v1.0 public-surface fingerprint
  (consistent with the existing
  ``furqan_lint.rust_adapter.extract_public_names`` documented
  limit). v1.5 horizon: method-level signing.
- ``trait_object_literal_text``: ``Box<dyn Trait>`` is signed
  as literal text; semantic equivalence under bound rewrites
  is not detected. v1.5 horizon: trait-bound-aware canonical
  form.
- ``macro_call_signed_pre_expansion``: macros are signed at
  the source level, NOT after expansion. v2 horizon: requires
  sigstore-rs FFI for rustc macro-expansion infrastructure.
- ``pub_crate_excluded``: ``pub(crate)`` and ``pub(super)``
  items are not part of the external API surface and are
  skipped during extraction. This is the locked decision and
  is NOT a v1.5 horizon item.

The four-place-completeness gate
(``tests/test_four_place_completeness_gate.py``) requires that
every fixture in this directory is referenced by:

  (a) CHANGELOG.md by exact filename stem (v0.11.0 entry).
  (b) This README.md inventory.
  (c) ``tests/test_gate11_rust_documented_limits.py`` pinning
      test.
  (d) The fixture file itself.
