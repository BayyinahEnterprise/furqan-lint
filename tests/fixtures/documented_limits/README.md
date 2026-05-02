# Documented limitations

Each fixture in this directory pins a known false negative or false
positive that v0.3.x has chosen not to fix yet. The `Remaining
limitations` section of the project README explains the user-visible
contract; the fixtures here pin the current behaviour so a future
fix is detected as a deliberate improvement rather than a silent
regression.

The discipline is borrowed from Bayyinah's `tests/fixtures/`
adversarial gauntlet directories: every claim the documentation
makes about behaviour has a fixture asserting that behaviour, so
the documentation cannot drift away from the code.

## Inventory

- **`try_body_only_returns_in_block.py`.** Stronger form: the body
  raises before the return, the except handler falls through. mypy
  flags this; v0.3.1 does not.
- **`aliased_optional_import.py`.** `from typing import Optional as
  MyOpt; -> MyOpt[X]` is treated as a non-Optional return type.
  The function returns None and fires a false-positive
  `return_none_mismatch`. The proper fix needs symbol-table
  tracking (parse imports, build alias map). README registers
  this under "Aliased Optional / Union imports."
- **`aliased_union_import.py`.** Symmetric form for `Union`: a
  `from somelib import Union; -> Union[X, None]` (or `from typing
  import Union as U; -> U[X, None]`) bypasses the bare-name and
  `typing.` / `t.` matchers added in v0.3.2 Finding 1, so a
  function that returns `None` may PASS silently even though the
  `Union` head came from a non-`typing` module that has nothing to
  do with optionality. Same fix shape as the `Optional` case
  (symbol-table tracking). README registers this under "Aliased
  Optional / Union imports."
- **`local_class_in_function.py`.** A class defined inside a
  function or method body has its methods silently dropped. The
  v0.3.2 Finding 3 fix added recursive descent through nested
  top-level classes (`Outer.Inner.method` is now collected); the
  same descent does NOT extend through `FunctionDef` bodies into
  local `ClassDef` children, regardless of whether the
  `FunctionDef` is at module scope or inside another `ClassDef`.
  The argument for keeping it: a local class is a private
  implementation detail used as a closure-like return value, not
  part of the module's public contract. README registers this
  under "Local classes inside any function or method body."
- **`zero_return_function.py`.** A function declaring a return type
  with no `return` statement on any path is silently passed. D24
  skips functions with zero returns, deferring to ring-close R3
  (a separate Furqan checker furqan-lint does not yet run).
  mypy reports this as "Missing return statement"; callers who
  want this flagged should run mypy alongside furqan-lint.
  README registers this under "Zero-return functions."

## How to retire a fixture

When a future version closes one of these limitations:

1. Delete the fixture (or move it to `tests/fixtures/clean/` /
   `tests/fixtures/failing/` depending on whether the new behaviour
   makes it pass or fail substantively).
2. Remove the corresponding entry from the README's `Remaining
   limitations` section.
3. Update the test in `tests/test_documented_limits.py` to remove
   the now-stale assertion, leaving only fixtures that still
   represent open limitations.
4. Add a CHANGELOG entry under `### Fixed` naming the limitation
   that closed.


## Retired in v0.3.5

- ``try_body_no_exception_modeling.py`` removed: the
  "Exception-driven fall-through" limitation it pinned was closed
  by v0.3.5's try/except modeling fix. ``try_body_only_returns_in_block.py``
  is preserved because it pins a different limit (D24's skip-on-zero-returns
  rule for ring-close R3 territory), which is unaffected by the
  try/except modeling fix.
- ``redundant_pipe_none.py`` removed: the v0.3.4 "PEP 604 redundant
  None" pinning was promoted to a structural fix in v0.3.5. The
  PEP 604 pipe path now produces ``TypePath("None")`` for ``None | None``,
  matching the ``Optional[None]`` (v0.3.4) and ``Union[None]`` (v0.3.3)
  paths.
