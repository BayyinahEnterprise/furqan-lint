# Rust documented limitations

Each fixture in this directory pins a known false negative or false
positive of the current Rust adapter (R3 + D24 + D11). The
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

- **`trait_object_return.rs`.** A function returning
  `Box<dyn Trait>` is translated to a `TypePath` that ignores the
  trait-object payload. Trait-object polymorphism is out of scope
  per ADR-001's deferred-features list; the fixture parses cleanly
  and does not currently fire a marad, but a future
  checker that reasons about trait dispatch would be the right
  place to revisit.
- **`lifetime_param_return.rs`.** Functions with explicit lifetime
  parameters (`fn f<'a>(...) -> &'a str`) have their lifetimes
  stripped during translation; the return type is treated as
  `-> str`. D24's path-coverage logic is unaffected; a future
  borrow-pattern checker would need lifetime preservation.
- **`closure_with_annotated_return.rs`.** `closure_expression`
  nodes are skipped for D24, D11, AND R3 (current as of v0.7.2).
  The outer function is checked normally; the closure body is
  opaque. A future phase may revisit when there is a concrete
  user-reported false negative.
- **`r3_panic_as_tail_expression.rs`.** `panic!()` (or any
  diverging macro) used as a tail expression with no trailing
  `;` does NOT fire R3 in v0.7.1, even though the function
  structurally produces no value. The tree-sitter-rust grammar
  treats the macro as a tail expression and the v0.7.0
  translator synthesizes a `ReturnStmt(opaque)` for any tail
  expression; R3 fires on zero `ReturnStmt`, so it does not
  fire here. Fixing this would require either a hardcoded
  diverging-macro allowlist (brittle) or cross-file type
  inference (out of scope). A future phase may revisit if the Rust
  ecosystem standardizes a `#[diverging]` attribute.

## Retired in v0.7.1

- `trait_method_signature.rs` removed: the skip of
  `function_signature_item` is now stable across two releases
  (v0.7.0 + v0.7.1) and is recognised as a permanent design
  choice rather than a temporary limit. D24/D11/R3 do not apply
  to trait method declarations because there is no body to
  analyse. The retirement procedure cleans up exactly this kind
  of "limit that turned out to be permanent."
- `empty_or_panic_only_body.rs` removed: closed by R3
  (zero-return). v0.7.1 wires upstream
  `furqan.checker.check_ring_close` (filtered to R3-shaped
  diagnostics) which catches every case the limit pinned. The
  fixture's structural pattern (annotated return type + empty
  or `;`-terminated macro-only body) translates to
  `statements=()`, which check_ring_close fires R3 on. The
  cases now live as `failing/r3_*.rs` fixtures with assertions
  inverted from "silent PASS" to "fires R3."

## Retired in v0.7.3

- `macro_invocation_body.rs` removed: the limit it pinned (a
  function whose body is a single macro invocation evaluates as
  opaque to R3) was the same underlying limit as
  `r3_panic_as_tail_expression.rs`. Both pinned the v0.7.0
  R1 translator behavior: tail expressions become synthesized
  opaque ReturnStmts, regardless of whether the tail expression
  is a diverging macro. The two fixtures pinned one limit, not
  two. Consolidated into `r3_panic_as_tail_expression.rs` whose
  pinning test now parametrizes over the diverging-macro family
  (panic, todo, unimplemented, unreachable). The README
  "Remaining limitations" section now has one bullet for this
  limit instead of two.

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
- **`impl_methods_omitted.rs`.** Methods inside `impl Type { ... }`
  blocks are intentionally not collected by
  `extract_public_names`. The extractor walks only top-level
  CST root children; impl methods live one level deeper.
  Asymmetric with goast as of v0.8.2 (which emits qualified
  method names). Pin lives in
  `tests/test_rust_correctness.py::test_rust_extract_omits_impl_methods`.
  Added in v0.8.3.
