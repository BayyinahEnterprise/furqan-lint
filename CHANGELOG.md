# Changelog

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
