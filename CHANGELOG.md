# Changelog

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
