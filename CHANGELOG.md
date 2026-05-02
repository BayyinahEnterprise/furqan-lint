# Changelog

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
