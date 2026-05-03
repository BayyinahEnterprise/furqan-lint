# Documented limitations

Each fixture in this directory pins a known false negative or false
positive that the current release has chosen not to fix yet. The
`Remaining limitations` section of the project README explains the
user-visible contract; the fixtures here pin the current behaviour
so a future fix is detected as a deliberate improvement rather than
a silent regression.

The discipline is borrowed from Bayyinah's `tests/fixtures/`
adversarial gauntlet directories: every claim the documentation
makes about behaviour has a fixture asserting that behaviour, so
the documentation cannot drift away from the code.

The four-place pattern: every documented limit must appear in
(1) the README's `Remaining limitations` section, (2) a fixture
in this directory with a substantive header docstring, (3) a
pinning test in `tests/test_documented_limits.py` that asserts
the *current* behaviour, and (4) a CHANGELOG entry under
`### Limitations introduced` for the version that named it. When
all four are aligned, the limitation is deliberate; when they
drift, a v0.6.1-style corrective is required.

## Inventory

- **`try_body_only_returns_in_block.py`.** Originally pinned the
  v0.3.x stronger-form limit "try body raises, except falls
  through, mypy flags this, furqan-lint does not". The limit was
  retired in v0.6.0 by R3 (zero-return), which catches the case
  because the function has no return statement on any path. The
  fixture is retained as a regression target: the test in
  `tests/test_documented_limits.py` now asserts R3 fires (rather
  than asserting silent PASS).
- **`aliased_optional_import.py`.** `from typing import Optional as
  MyOpt; -> MyOpt[X]` is treated as a non-Optional return type.
  The function returns None and fires a false-positive
  `return_none_mismatch`. The proper fix needs symbol-table
  tracking on the `return_none` checker (parse imports, build
  alias map, resolve before matching). v0.6.1 added alias
  resolution to R3's decorator skip-list; extending the pattern
  to `return_none`'s Optional/Union recognition is registered as
  a follow-up. README registers this under "Aliased Optional /
  Union imports."
- **`aliased_union_import.py`.** Symmetric form for `Union`: a
  `from somelib import Union; -> Union[X, None]` (or `from typing
  import Union as U; -> U[X, None]`) bypasses the bare-name and
  `typing.` / `t.` matchers in the `return_none` checker, so a
  function that returns `None` may PASS silently. Same fix shape
  as the `Optional` case.
- **`local_class_in_function.py`.** A class defined inside a
  function or method body has its methods silently dropped. The
  v0.3.2 fix added recursive descent through nested top-level
  classes (`Outer.Inner.method` is now collected); the same
  descent does NOT extend through `FunctionDef` bodies into local
  `ClassDef` children, regardless of whether the `FunctionDef` is
  at module scope or inside another `ClassDef`. The argument for
  keeping it: a local class is a private implementation detail
  used as a closure-like return value, not part of the module's
  public contract. README registers this under "Local classes
  inside any function or method body."

## How to retire a fixture

When a future version closes one of these limitations:

1. Delete the fixture (or move it to `tests/fixtures/clean/` /
   `tests/fixtures/failing/` depending on whether the new behaviour
   makes it pass or fail substantively). If the fixture demonstrates
   a case the new version now catches, retain it as a regression
   target and invert the test assertion instead of moving it.
2. Remove the corresponding entry from the README's `Remaining
   limitations` section.
3. Update the test in `tests/test_documented_limits.py` to remove
   the now-stale assertion (or invert it, per step 1).
4. Add a CHANGELOG entry under `### Fixed` (or `### Limitations
   retired`) naming the limitation that closed.

## Retired in v0.3.5

- `try_body_no_exception_modeling.py` removed: the
  "Exception-driven fall-through" limitation it pinned was closed
  by v0.3.5's try/except modeling fix. `try_body_only_returns_in_block.py`
  was preserved at the time because it pinned a different limit
  (D24's skip-on-zero-returns rule for ring-close R3 territory).
- `redundant_pipe_none.py` removed: the v0.3.4 "PEP 604 redundant
  None" pinning was promoted to a structural fix in v0.3.5. The
  PEP 604 pipe path now produces `TypePath("None")` for `None | None`,
  matching the `Optional[None]` (v0.3.4) and `Union[None]` (v0.3.3)
  paths.

## Retired in v0.6.0

- `zero_return_function.py` moved to `tests/fixtures/failing/`:
  the v0.4.x "Zero-return functions" limitation was closed by R3
  (ring-close), which now fires on every zero-return shape D24
  cannot reach.
- `try_body_only_returns_in_block.py` retained as a regression
  target, but the limit it pinned was retired: R3 catches the
  try-body-only-raise case because the function has no return
  statement on any path. The pinning test was inverted from
  "asserts silent PASS" to "asserts R3 fires".

## Retired in v0.6.1

- `aliased_abstractmethod.py` removed: the v0.6.0 "Aliased
  decorator imports for R3 skip-list" limitation was closed by
  symbol-table-backed alias resolution in `zero_return.py`. The
  alias case is now covered by `tests/test_round11_alias_resolution.py`
  (positive cases plus negative-control regression checks).
