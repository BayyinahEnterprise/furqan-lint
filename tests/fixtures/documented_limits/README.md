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

- **`try_body_no_exception_modeling.py`.** A function whose only
  return is inside a `try` block. v0.3.1 splices the `try` body
  unconditionally, so the function is reported PASS even though an
  exception in the body would prevent reaching the return.
  Asymmetric with the `match` cases (which wrap as maybe-runs).
  README registers this under "Exception-driven fall-through."
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
- **`redundant_pipe_none.py`.** `int | None | None` and
  `None | None` are accepted today (mypy / pyright collapse the
  redundant arm; the matcher arrives at the right answer for
  incidental reasons) but not structurally defended the way the
  `Union[None]` path is in v0.3.3 and the `Optional[None]` path
  is in v0.3.4. The intermediate AST is a binary `UnionType`
  whose arms may both be `None` after inner extraction; this
  shape would break the day someone refactors the pipe path to
  require distinct arms. README registers this under "Redundant
  `None` arms in PEP 604 unions."
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
