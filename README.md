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

## License

Apache-2.0.
