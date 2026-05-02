# furqan-lint

Structural-honesty checks for Python, powered by [Furqan](https://tryfurqan.com).

`furqan-lint` translates Python source into the Furqan AST and runs the
subset of Furqan checkers whose semantics carry across language boundaries
into idiomatic Python. v0.2.0 ships four checks:

- **D24 (all-paths-return)** every control-flow path through a typed
  function reaches a return statement.
- **D11 (status-coverage)** when a function returns `Optional[X]`, every
  caller either propagates the optionality or explicitly handles `None`.
  A caller that silently collapses `Optional[X]` into a non-optional return
  type is the structural equivalent of dropping the `Incomplete` arm of
  Furqan's `Integrity | Incomplete` union.
- **return_none_mismatch** a function declaring `-> str` (or any
  non-Optional type) that returns `None` on some path is flagged as a
  type mismatch. Closes the D24 return-None blind spot.
- **additive_only** invoked via `furqan-lint diff old.py new.py`,
  compares two versions of a module's public surface and fires on any
  removed name. Adding a public name is silent.

## Install

```bash
pip install furqan-lint
```

Requires Python 3.10+ and `furqan>=0.10.1`.

## Usage

```bash
furqan-lint check path/to/file.py
furqan-lint check path/to/directory/
furqan-lint diff old_version.py new_version.py
furqan-lint version
```

## Example

```python
# example.py
from typing import Optional

def find_record(id: int) -> Optional[dict]:
    if id <= 0:
        return None
    return {"id": id}

def get_name(id: int) -> str:
    record = find_record(id)
    if record is not None:
        return record["name"]
    # Missing else: falls through with no return
```

```
$ furqan-lint check example.py

MARAD  example.py
  3 violation(s):
    [all_paths_return] Function 'get_name' at line 8 declares
    -> str but not every control-flow path reaches a return
    statement.

    [status_coverage] Function 'get_name' at line 8 calls
    'find_record' (returns Optional[dict]) but declares -> str.
    The Optional is silently collapsed.

    [return_none_mismatch] Function 'get_name' at line 8
    declares -> str but returns None on at least one path.
```

## Closed in v0.3.2

Three findings from a round-5 review of v0.3.1, all reproduced
empirically and fixed:

- **`Union[X, None]` recognition.** `Union[X, None]`,
  `Union[None, X]`, `Union[X, Y, None]`, and the `typing.Union` /
  `t.Union` aliased forms are now treated as Optional. Older
  codebases (pre-PEP 604) routinely use `Union[X, None]` and were
  producing false-positive `return_none_mismatch` diagnostics.
- **String forward-reference annotations.** PEP 484 string
  annotations like `-> "Optional[User]"` (the canonical
  `TYPE_CHECKING` idiom for breaking circular imports) are now
  parsed and recursed into. Pre-v0.3.2 the literal string was
  treated as a bare type name.
- **Nested class methods.** Methods of `Outer.Inner.method`,
  `Outer.Mid.Inner.method`, etc. are now collected via recursive
  descent through nested `ClassDef` bodies. Pre-v0.3.2 the descent
  stopped at one level and inner-class methods were silently
  dropped, producing false-negative D24 and `return_none_mismatch`
  on a common Python idiom.

## Closed in v0.3.0

Six findings from a three-round review of v0.2.0, all reproduced
empirically and fixed:

- **Compound-statement blind spot.** `for`, `while`, `with`, `try`,
  and `match` bodies are now translated, so `return None` inside
  any of them is caught by `return_none_mismatch`. Loop and
  `except` bodies wrap as maybe-runs ifs so D24 doesn't
  over-claim coverage.
- **Additive surface gaps.** `MAX_RETRIES: int = 5` and `A, B = 1, 2`
  are now visible to the additive checker. Annotated `__all__`
  declarations are also read.
- **Dynamic `__all__` cascade.** A non-static `__all__` now raises
  `DynamicAllError` and the CLI exits 2 with an `INDETERMINATE`
  result, rather than silently treating the surface as empty.
- **D11 thread-safety.** A `threading.Lock` serialises concurrent
  entry to the monkey-patched-predicate context manager.
- **`Optional` over-match.** `weird.lib.Optional[X]` is no longer
  treated as `typing.Optional[X]`.
- **`int | str` rendering.** Diagnostic prose for non-Optional
  unions no longer says `Optional[Unknown]`.

## Closed in v0.2.0

- **D24 return-None blind spot.** A function declaring a non-Optional
  return type that returns `None` is now caught by the
  `return_none_mismatch` checker.
- **Nested-function call attribution.** Calls inside closures, inner
  functions, and methods of inner classes are no longer attributed to
  the enclosing function.
- **Decorator call attribution.** Decorators are no longer collected
  as calls inside the decorated function's body.

## Remaining limitations

Each limitation here has a fixture in `tests/fixtures/documented_limits/`
and a test in `tests/test_documented_limits.py` pinning the current
behaviour, so any change (in either direction) is intentional rather
than silent.

- **D11 monkey-patch.** The Optional detection still swaps
  `status_coverage._is_integrity_incomplete_union` inside a context
  manager (now lock-serialised, but still process-global). The
  structural fix is upstream support for a `producer_predicate`
  parameter on `check_status_coverage`. `contextvars.ContextVar`
  is the per-context-isolated alternative if upstream cooperates.
- **`self.method()` calls.** The adapter resolves `self.foo()` to the
  bare method name `foo`, the same as a plain `foo()` call. This is
  not a bug today but will need revisiting if the adapter ever stores
  qualified call paths.
- **Checker coverage.** Only four of Furqan's ten checkers run on
  Python. The rest depend on Python-specific conventions (scope
  declarations, layer annotations, calibration bounds, dependency
  mapping) that standard Python does not provide.
- **Return-type expression inference.** `return_none_mismatch` only
  catches the `None` literal. A `-> int` function returning `"hello"`
  is not caught.
- **Exhaustive `match` recognition.** Each case body wraps as a
  maybe-runs `IfStmt`, so D24 cannot recognise a structurally
  exhaustive `match` (with a `case _:` arm) as guaranteed coverage.
  Future work could splice the catch-all case into the prior
  `IfStmt`'s `else_body`.
- **Exception-driven fall-through.** `try` bodies are spliced as
  always-running. A function whose only return is inside a `try`
  block is not flagged by D24 even though an exception in that block
  would prevent reaching the return. mypy and similar type-checkers
  do model this; furqan-lint does not yet. The conservative fix
  (wrap `try.body` as maybe-runs only when there are exception
  handlers that don't all return) requires richer translation;
  v0.3.1 documents the limitation and pins it as a fixture rather
  than introducing a half-measure.
- **Aliased `Optional` / `Union` imports.** `from typing import
  Optional as MyOpt; -> MyOpt[X]` is treated as a non-Optional return
  type. The same gap applies to `Union`: `from typing import Union as
  U; -> U[X, None]` and `from somelib import Union; -> Union[X, None]`
  both bypass the bare-name and `typing.` / `t.` matchers. The matcher
  recognises the bare `Optional` / `Union` names and the qualified
  `typing.` / `t.` forms only; arbitrary aliases and same-named imports
  from non-`typing` modules need symbol-table tracking (parse imports,
  build alias map, resolve before matching), which is deferred to a
  future phase. Workaround: use the bare or qualified form, or rename
  the import to `import typing as t`.
- **Local classes inside any function or method body.** A class
  defined inside a function body or a method body has its methods
  silently dropped. The v0.3.2 nested-class fix added recursive
  descent through top-level `ClassDef` -> `ClassDef` (so
  `Outer.Inner.method` is collected); it does NOT extend through
  `FunctionDef` -> `ClassDef` regardless of whether the
  `FunctionDef` is at module scope or inside another `ClassDef`. The
  argument for the asymmetry: a local class is a private
  implementation detail (often a closure-like return value), not
  part of the module's public contract that D24 and
  `return_none_mismatch` exist to enforce. If a real-world
  regression demonstrates otherwise, extend the function walker to
  descend into local `ClassDef` bodies and call
  `_collect_class_methods`.

## License

Apache-2.0.
