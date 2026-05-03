# Rust documented limitations

Each fixture in this directory pins a known false negative or false
positive of the v0.7.0 Rust adapter (Phase 1: D24 + D11 only). The
project README's `Remaining limitations` section explains the
user-visible contract; the fixtures here pin the current behaviour
so a future fix is detected as a deliberate improvement rather
than a silent regression.

The discipline mirrors the Python adapter's
`tests/fixtures/documented_limits/`: every claim the documentation
makes about behaviour has a fixture asserting that behaviour.

The four-place pattern: every documented limit must appear in
(1) the README's `Remaining limitations` section, (2) a fixture
in this directory with a substantive header docstring, (3) a
pinning test in `tests/test_rust_correctness.py` that asserts the
*current* (limited) behaviour, and (4) a CHANGELOG entry under
`### Limitations introduced` for the version that named it.

## Inventory

- **`macro_invocation_body.rs`.** A function whose body is a single
  macro invocation (`todo!()`, `unimplemented!()`, etc.) is treated
  as opaque. Phase 1 cannot see through macro expansion. The
  Python adapter's R3 catches the analogous Python case
  (`def f() -> int: pass`); the Rust analogue is deferred to
  v0.7.1.
- **`trait_object_return.rs`.** A function returning
  `Box<dyn Trait>` is translated to a `TypePath` that ignores the
  trait-object payload. Trait-object polymorphism is out of scope
  per ADR-001's deferred-features list; the fixture parses cleanly
  and does not currently fire a marad, but a future Phase 2
  checker that reasons about trait dispatch would be the right
  place to revisit.
- **`lifetime_param_return.rs`.** Functions with explicit lifetime
  parameters (`fn f<'a>(...) -> &'a str`) have their lifetimes
  stripped during translation; the return type is treated as
  `-> str`. D24's path-coverage logic is unaffected; a future
  borrow-pattern checker would need lifetime preservation.
- **`empty_or_panic_only_body.rs`.** Functions with empty bodies
  or bodies containing only `panic!()` / `todo!()` /
  `unimplemented!()` are PASS in v0.7.0. The Rust analogue of
  Python's R3 (zero-return ring-close) is deferred to v0.7.1.
- **`trait_method_signature.rs`.** `function_signature_item` nodes
  (trait method declarations with no body) are skipped by design
  per prompt §3.4. D24/D11 do not apply to interface declarations.
  This is a deliberate skip, not an oversight; pinned so that a
  future change to walk `function_signature_item` is intentional.
- **`closure_with_annotated_return.rs`.** `closure_expression`
  nodes are skipped in Phase 1 even when the closure has an
  explicit `-> T` annotation. The outer function is checked
  normally; the closure body is opaque. Phase 2 may revisit.

## How to retire a fixture

When a future version closes one of these limitations:

1. Delete the fixture (or move it to `tests/fixtures/rust/clean/`
   or `tests/fixtures/rust/failing/` depending on whether the new
   behaviour makes it pass or fail substantively). If the fixture
   demonstrates a case the new version now catches, retain it as
   a regression target and invert the test assertion instead of
   moving it.
2. Remove the corresponding entry from the README's
   `Remaining limitations` section.
3. Update the test in `tests/test_rust_correctness.py` to remove
   the now-stale assertion (or invert it, per step 1).
4. Add a CHANGELOG entry under `### Fixed` (or `### Limitations
   retired`) naming the limitation that closed.
