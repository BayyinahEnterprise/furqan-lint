# furqan-lint

[![CI](https://github.com/BayyinahEnterprise/furqan-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/BayyinahEnterprise/furqan-lint/actions/workflows/ci.yml)

Structural-honesty checks for Python, powered by [Furqan](https://tryfurqan.com).

`furqan-lint` translates Python source into the Furqan AST and runs the
subset of Furqan checkers whose semantics carry across language boundaries
into idiomatic Python. Four checks ship today:

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

Requires Python 3.10+ and `furqan>=0.11.0`. Furqan is not yet on PyPI; install it from GitHub:

```bash
pip install "git+https://github.com/BayyinahEnterprise/furqan-programming-language.git@v0.11.1"
pip install furqan-lint
```

### Rust support (opt-in)

As of v0.7.0, furqan-lint can lint `.rs` files. Rust support is
behind an opt-in extra so the Python-only install path is unchanged:

```bash
pip install "furqan-lint[rust]"
```

This pulls in `tree-sitter` and `tree-sitter-rust` (PyPI ships
ARM64 and x86_64 wheels for both; no source build required).

As of v0.7.2, `.rs` files run three checkers: R3 (ring-close,
zero-return on annotated functions, via upstream
`furqan.checker.check_ring_close`), D24 (all-paths-return), and
D11 (status-coverage). The D11 producer predicate recognises
both `Option<T>` and `Result<T, E>` returns; a caller that calls
a may-fail helper without propagating the union is flagged.

The planned analogue of `return_none_mismatch` was dropped per
the v0.7.2 prompt-grounding self-check, which empirically
demonstrated that the firing condition is unreachable on any
compilable Rust source (`rustc` rejects `fn f() -> i32 { None }`
at compile time before furqan-lint sees the file). Trait objects,
lifetimes, macro expansion, closure return-type checks, and
Cargo workspace traversal remain out of scope.

Edition is read from the nearest ancestor `Cargo.toml`'s
`[package].edition` field (one of "2018", "2021", "2024"); if
no Cargo.toml is found or the field is malformed, edition
defaults to "2021". The current implementation does not branch on edition.

## Usage

```bash
furqan-lint check path/to/file.py
furqan-lint check path/to/directory/
furqan-lint diff old_version.py new_version.py
furqan-lint version
```

## CI Integration

Two ways to wire furqan-lint into your workflow.

### GitHub Action

Three lines in your workflow file run the structural checks on every
push or pull request:

```yaml
# .github/workflows/furqan-lint.yml
name: Furqan Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: BayyinahEnterprise/furqan-lint@v0.4.0
        with:
          path: src/
```

Inputs (all optional):
- `path` -- file or directory to check. Default: `.`
- `python-version` -- Python version to use. Default: `3.12`
- `furqan-lint-version` -- pinned version to install. Default: install
  latest from `main`.

### Pre-Commit Hook

Run the same checks locally on every `git commit` against staged
Python files:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/BayyinahEnterprise/furqan-lint
    rev: v0.4.0
    hooks:
      - id: furqan-lint
```

Then `pre-commit install`. Failures block the commit.

## Using with Other Tools

furqan-lint is complementary to ruff and mypy. Each catches a
different class of issue:

| Tool | Catches | Overlap with furqan-lint |
|------|---------|--------------------------|
| **ruff** | Style, unused imports, complexity, common bug patterns, formatting (replaces black + isort + flake8 + pyupgrade) | None |
| **mypy** | Type errors, some missing returns | Partial overlap on D24 and return-none. mypy does NOT catch Optional collapse (D11) or API-breaking changes (additive-only). |
| **furqan-lint** | Missing return paths, Optional collapse, return-None mismatch, API-breaking changes, zero-return functions | See mypy column |

### Recommended `.pre-commit-config.yaml` for Your Project

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy

  - repo: https://github.com/BayyinahEnterprise/furqan-lint
    rev: v0.5.0
    hooks:
      - id: furqan-lint
```

Then `pre-commit install`. Run order: ruff (lint + format) -> mypy
(types) -> furqan-lint (structural honesty). Each layer catches what
the previous layers do not.

### Contributing to furqan-lint

```bash
git clone https://github.com/BayyinahEnterprise/furqan-lint.git
cd furqan-lint
pip install -e ".[dev]"
pre-commit install

# Run all tools manually
ruff check .
ruff format --check .
mypy
pytest -q

# Run by test category
pytest -m unit         # fast, in-process, no subprocess
pytest -m integration  # CLI and pipeline tests
pytest -m "not slow"   # skip slow tests
pytest -m "not network" # skip network-dependent tests
```

The `furqan-lint check src/` self-check runs as part of pre-commit;
the tool that catches drift in other people's code must not have
drift in its own.

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

## Closed in v0.4.1

- **D11 monkey-patch retired.** The producer-predicate hack went
  through three lifecycle stages: a stopgap monkey-patch in v0.1.0
  on `status_coverage._is_integrity_incomplete_union`, a scoped
  context manager in v0.3.0, and a `threading.Lock` for safety in
  v0.3.0. v0.4.1 retires the patch entirely by passing the
  Python-Optional predicate via the upstream `producer_predicate=`
  keyword on `check_status_coverage`, available since
  `furqan>=0.11.0`. Closes the full lifecycle of a round-1 audit
  finding.
- **Pre-commit hook installability.** The hook now declares
  `furqan` as an `additional_dependency` via git URL, so
  `pre-commit install` can resolve the dependency that PyPI does
  not yet host.

## Closed in v0.3.5

Two corrective fixes promoting documented limitations to fixes:

- **Exception-driven fall-through.** `try`/`except` bodies are now
  modelled as maybe-runs (the success path = `try.body + orelse`
  becomes the body of a synthetic `IfStmt`; handlers chain into the
  `else_body`). D24 now correctly flags the false-negative case
  where a function's only return path is inside a `try` block whose
  except handler falls through (the canonical mypy "Missing return
  statement" shape). Documented as a known limit since v0.3.1.
- **PEP 604 `None | None`.** Now translates to bare
  `TypePath("None")`, the same shape `Optional[None]` (v0.3.4) and
  `Union[None]` (v0.3.3) produce. All three optional-spelling paths
  are now structurally identical for the all-None case. Documented
  as a v0.4.0 candidate in v0.3.4.

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
### Rust adapter (current as of v0.7.3)

Each Rust limit has a fixture in
`tests/fixtures/rust/documented_limits/` and a pinning test in
`tests/test_rust_correctness.py`.

- **Macro-invocation bodies.** A function whose body is a single
  macro invocation (`todo!()`, `unimplemented!()`, etc.) is treated
  as opaque. The current implementation cannot see through macro expansion. The
  Python adapter's R3 catches the analogous Python case
  (`def f() -> int: pass`); the Rust analogue is deferred to
  v0.7.1. Pinned as `tests/fixtures/rust/documented_limits/macro_invocation_body.rs`.
- **Trait-object return types.** Functions returning `Box<dyn Trait>`
  are translated to a `TypePath` that ignores the trait-object
  payload. Trait-object polymorphism is out of scope; a future
  a future checker would be the right place to revisit. Pinned as
  `tests/fixtures/rust/documented_limits/trait_object_return.rs`.
- **Lifetime-affected return types.** Functions with explicit
  lifetime parameters (`fn f<'a>(...) -> &'a str`) have their
  lifetimes stripped during translation; the return type is
  treated as `-> &'a str` literally (no lifetime semantics).
  D24's path-coverage logic is unaffected; a future borrow-pattern
  checker would need lifetime preservation. Pinned as
  `tests/fixtures/rust/documented_limits/lifetime_param_return.rs`.
- **Closures with annotated return types.** `closure_expression`
  nodes are skipped for D24, D11, AND R3 in v0.7.1. The outer
  function is checked normally; the closure body is opaque.
  A future phase may revisit when there is a concrete user-reported
  false negative. Pinned as
  `tests/fixtures/rust/documented_limits/closure_with_annotated_return.rs`.
- **`panic!()` (or any diverging macro) used as a tail expression
  with no `;`.** The translator synthesizes a `ReturnStmt(opaque)`
  for any tail expression per the v0.7.0 R1 rule, so R3 (zero-return)
  does not fire on `fn f() -> i32 { panic!() }`. Adding a fix
  would require either a hardcoded diverging-macro allowlist
  (brittle) or cross-file type inference of the macro's expansion
  type (out of scope). A future phase may revisit if the Rust ecosystem
  standardizes a `#[diverging]` attribute. Pinned as
  `tests/fixtures/rust/documented_limits/r3_panic_as_tail_expression.rs`.

## License

Apache-2.0.
