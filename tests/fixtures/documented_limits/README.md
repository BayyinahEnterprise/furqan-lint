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
- **`optional_stored_in_container.py`.** (v1.0.1) A call to an
  Optional producer whose result is placed straight into a container
  (`return {"name": find_name(uid)}`, typed `dict[str, str | None]`)
  keeps the None arm, yet D11 still reports it: D11 does not follow
  values through containers. furqan-lint's own
  `gate11/rust_signature_canonicalization._function_signature_dict`
  is this shape, and it is the one diagnostic left when furqan-lint
  checks its own `src/`. README registers this under "Optional
  stored in a container."
- **`exit_alias_not_terminal.py`.** (v1.0.1) D24 treats `raise`,
  `sys.exit(...)`, `os._exit(...)` and `os.abort()` as ending a path.
  `from sys import exit` aliases, bare `exit()` / `quit()`, calls to
  user functions annotated `NoReturn`, and `assert False` still look
  like a fall-through and are reported. The fix needs import alias tracking and `NoReturn`
  resolution. README registers this under "Terminal-call
  recognition."
- **`optional_guard_not_adjacent.py`.** (v1.0.1) D11 withholds a call
  only when None is handled at the call site or by a guard on the
  very next statement whose branch is straight-line up to its exit
  or rebind. A guard further down, a branch with a nested `if` before
  its exit (the price of the v1.0.1 audit F-01 correction), a guard
  inside a `try` with handlers or `finally` (its raise might be
  caught), and `assert x is not None` are not seen; the assert is left visible on
  purpose because `python -O` strips it. README registers this under "None handled
  away from the call site."
- **`terminal_recognition_false_negatives.py`.** (v1.0.1) Terminal
  recognition is syntactic: a `raise` inside `with
  contextlib.suppress(...)` and `sys.exit()` on a parameter named
  `sys` count as ending the path, so D24 is silent although the
  function can fall through. README registers this under "Terminal
  recognition is syntactic."
- **`raise_terminal_remaining_false_positives.py`.** (v1.0.1)
  `for ... else: raise`, `while True:` ending in `raise`, and `try` /
  `finally` with no `except` never fall through, yet D24 reports them.
  The `except*` blind spot is pinned inline in
  `tests/test_documented_limits.py`. README registers this under
  "Raise shapes D24 still misreads."
- **`none_procedure_returning_value.py`.** (v1.0.1) A `-> None`
  function that returns a value passes: `-> None` is translated
  without a return type and no checker compares values against it.
  README registers this under "`-> None` carries no value contract."
- **`comparison_assumed_bool.py`.** (v1.0.1) D11 withholds a producer
  call used as an `==` / `!=` / `is` / `is not` operand, assuming a bool
  result. An `__eq__` that returns its argument hands the None back and
  D11 is silent. README registers this under "Comparisons are assumed
  to be bool."
- **`guard_escapes_function_boundary.py`.** (v1.0.1) Nested function
  bodies are not checked by D11 or D24, a `nonlocal` rebind from a
  nested function is not followed, and a decorator that swallows the
  guard's `raise` is not seen. README registers this under "Checks
  stop at function boundaries."
- **`r3_conservative_completion.py`.** (v1.0.2) R3's completion
  analysis treats `with`, `for`, `except` handlers and nested-loop
  `break` as possibly completing, so functions that never return
  normally through those shapes are still reported. README registers
  this under "R3 completion is conservative."

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
