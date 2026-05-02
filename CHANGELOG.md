# Changelog

## [0.4.0] - 2026-05-02

Distribution and CI infrastructure. No new checker logic. The tool
becomes adoptable: three lines of YAML to wire it into a GitHub
Actions workflow, or three lines for a pre-commit hook.

### Added

- **GitHub Action.** ``action.yml`` at the repo root provides a
  composite action: ``uses: BayyinahEnterprise/furqan-lint@v0.4.0``
  with optional ``path``, ``python-version``, and
  ``furqan-lint-version`` inputs. Composite-runs (no Docker
  image), so cold-start is dominated by setup-python and pip
  install rather than container pull. Furqan is installed from
  GitHub (v0.11.1 pinned) since it is not yet on PyPI.
- **Pre-commit hook.** ``.pre-commit-hooks.yaml`` declares a
  single hook ``id: furqan-lint`` that runs ``furqan-lint check``
  scoped to ``types: [python]``. Users add three lines to
  ``.pre-commit-config.yaml`` to wire it in.
- **CI workflow.** ``.github/workflows/ci.yml`` runs the test
  suite on Python 3.10, 3.11, 3.12, and 3.13 in a matrix on every
  push and pull request to ``main``. Three quality gates per
  matrix cell: pytest (the 136 prior tests + 9 new structural
  tests), version-sync between ``__version__`` and
  ``pyproject.toml``, and an em-dash check across ``src/``,
  ``tests/``, and ``README.md``. CHANGELOG.md is intentionally
  excluded from the em-dash scan to avoid breaking on legitimate
  prior entries.
- **PyPI publishing scaffolding.** ``scripts/publish.sh`` is a
  documented build/upload script using ``build`` and ``twine``.
  NOT to be run by automation - PyPI credentials are held only by
  the project lead. ``pyproject.toml`` metadata verified for PyPI
  readiness: ``Repository`` and ``Issues`` URLs added under
  ``[project.urls]``.
- **CI badge.** README displays the CI workflow status at the
  top.

### Changed

- ``pyproject.toml`` dependency bumped from ``furqan>=0.10.1`` to
  ``furqan>=0.11.0``. The project has been verified to work with
  furqan v0.11.1 (the version the GitHub Action installs).
- README's intro line "v0.2.0 ships four checks" is now version-
  agnostic ("Four checks ship today") so it stops aging out at
  every release. Install instructions now show how to install
  Furqan from GitHub before installing furqan-lint, since Furqan
  is not on PyPI.

### Tests

- 5 new structural tests in ``tests/test_action.py`` for
  ``action.yml`` and ``.pre-commit-hooks.yaml`` shape.
- 4 new structural tests in ``tests/test_ci_workflow.py`` for the
  CI matrix, version-sync gate, and em-dash gate.
- Total: 145.

## [0.3.5] - 2026-05-02

Two corrective fixes promoting documented limitations to fixes.
Both items reproduced empirically against v0.3.4 before fixing.

### Fixed

- **try/except control flow modelling.** ``try.body`` and
  ``orelse`` are now combined into a single "success path" and
  wrapped with the handler chain in a synthetic ``IfStmt`` shape
  whose ``else_body`` is a right-folded chain of handler bodies.
  D24 now fires correctly when a function's only return path is
  inside a ``try`` block whose except handler falls through (the
  canonical mypy "Missing return statement" shape, documented as
  "Exception-driven fall-through" since v0.3.1). The control case
  ``try/except/else where every branch returns`` continues to PASS
  because both halves of the synthetic IfStmt all-paths-return.
  Returns inside ``finally`` continue to cover all paths because
  ``finalbody`` is spliced unconditionally. New helper:
  ``_build_try_handler_chain``. Per the project's stated decision,
  the unmatched-exception case is treated as exit-via-propagation,
  not fall-through.
- **PEP 604 ``None | None`` symmetry.** Now translates to a bare
  ``TypePath(base="None")``, mirroring the v0.3.3
  ``_is_all_none_union`` discipline (``Union[None]``) and the
  v0.3.4 ``_is_none_literal`` early branch
  (``Optional[None]``). All three optional-spelling paths produce
  structurally identical AST for the all-None case. Added an
  ``_is_none_literal`` early branch to the pipe-union arm of
  ``_translate_return_annotation``. Documented in v0.3.4 as a
  v0.4.0 candidate; promoted in v0.3.5 because the fix shape was
  symmetric with the existing two paths and required no new
  infrastructure.

### Changed

- Removed the "Exception-driven fall-through" entry from the
  README's "Remaining limitations" section.
- Removed ``tests/fixtures/documented_limits/try_body_no_exception_modeling.py``
  (the closed limit). The other try-related fixture
  (``try_body_only_returns_in_block.py``) is preserved because it
  pins a different limit (D24's skip-on-zero-returns rule for
  ring-close R3 territory), which is unaffected by the v0.3.5 fix.
- Removed ``tests/fixtures/documented_limits/redundant_pipe_none.py``
  (the v0.3.4 PEP 604 pin) and the corresponding two pinning tests.

### Tests

- 10 try/except regression tests in ``tests/test_round8_fixes.py``
  (probe11 and probe12 shapes, finally-return, multi-handler with
  one falling through, bare except, return_none inside try, nested
  try in if).
- 4 PEP 604 None|None symmetric tightening tests in the same file.
- 3 doc-limit tests removed: 1 for the closed try-body limit and 2
  for the closed PEP 604 redundant-None limit.
- Total: 136.

## [0.3.4] - 2026-05-02

Three quality-tier observations from Fraz's round-7 review of
v0.3.3, none blocking. All three are asymmetries between code
paths that currently produce correct answers but for incidental
reasons rather than structural ones. v0.3.4 closes the two
structural ones and pins the third as a documented limitation.

### Fixed

- **`Optional[None]` symmetry with v0.3.3 `Union[None]`.** The
  Optional path produced `UnionType(left=TypePath("None"),
  right=TypePath("None"))` on `Optional[None]`, while the v0.3.3
  Union path produced a bare `TypePath(base="None")` on
  `Union[None]`. Both arrived at correct answers (no diagnostic
  fires either way), but only the Union path was structurally
  defended; a binary union of identical types is not semantically
  meaningful and would break the day someone refactors the matcher
  to require distinct arms. v0.3.4 mirrors the v0.3.3 discipline:
  `_translate_return_annotation` short-circuits `Optional[None]`
  to bare `TypePath(base="None")` (`typing.Optional[None]`
  evaluates to `type(None)` at Python runtime). Caught by
  Observation 1.
- **Bare `Optional` and bare `Union` no longer suggest invalid
  fixes.** A function declared `-> Optional` (no subscript) with
  a `return None` body produced a `return_none_mismatch` whose
  `minimal_fix` suggested `Optional[Optional]`, which is invalid
  typing syntax (mypy rejects bare `Optional` with "Bare Optional
  is not allowed"). The same incoherent suggestion applied to
  bare `Union`. v0.3.4 introduces `_suggested_fix` in
  `return_none.py` that detects the bare-name case and suggests
  the real fix (add a type argument: `Optional[X]` or `X | None`).
  Caught by Observation 3.

### Added

- `tests/test_round7_fixes.py` with 7 tests pinning the two
  structural fixes:
  - 4 tests on `Optional[None]` translation (bare `TypePath`,
    not binary `UnionType`, end-to-end PASS, and a negative test
    that `Optional[str]` still produces the expected
    `UnionType(str, None)` shape).
  - 3 tests on `_suggested_fix` (bare `Optional` produces
    helpful prose without the `Optional[Optional]` artifact, bare
    `Union` produces the symmetric helpful prose, and a negative
    test that normal `TypePath`s still get the canonical
    `Optional[<name>]` suggestion).
- `tests/test_documented_limits.py` gains
  `test_round7_redundant_pipe_none_passes` (+1 test) pinning the
  current correct-but-incidental behaviour on PEP 604 redundant
  `None` arms (Observation 2). New fixture
  `tests/fixtures/documented_limits/redundant_pipe_none.py`.
  README and `tests/fixtures/documented_limits/README.md` updated
  with the new entry.

### Tests

- 116 -> 124 (+8). All v0.3.3 tests pass identically.

### Unchanged

- The v0.3.3 `Union[None, ...]` boundary fix (`_is_union_with_none`
  predicate, `_is_all_none_union` helper, defense-in-depth
  assertion). The v0.3.4 Optional short-circuit applies the same
  discipline pattern to a parallel code path.
- `Optional[X]` for non-`None` `X` translates to
  `UnionType(X, None)` exactly as before.
- All other documented limitations and their fixtures.

### Deferred

- **PEP 604 redundant `None` arms** (Observation 2). `int | None
  | None` and `None | None` are correctly accepted today; the
  intermediate AST is incidentally correct but not structurally
  defended the way the `Union[None]` and `Optional[None]` paths
  are. Full symmetric tightening across the three optional
  spellings is a v0.4.0 candidate.

---

## [0.3.3] - 2026-05-02

One blocking finding plus two cleanup items from Fraz's round-6
review of v0.3.2. The blocking finding (a hard crash on degenerate
`Union[None, ...]` shapes) was reproduced empirically against the
v0.3.2 release on three concrete inputs before fixing.

### Fixed

- **`Union[None, ...]` boundary crash (BLOCKER).** v0.3.2's
  `_extract_union_with_none_inner` raised `IndexError: list index
  out of range` on `Union[None]`, `Union[None, None]`, and
  `Union[None, None, None]`. All three are legal Python that mypy
  accepts (`typing.Union[None]` evaluates to `type(None)` at
  runtime). Same shape of failure as the original Furqan parser
  RecursionError bug from round 3: an unstructured Python
  exception on a shape of legal input the matcher did not
  anticipate. The fix tightens `_is_union_with_none` to require
  *both* a `None` arm AND a non-None arm, so the predicate is
  the truthful contract of what `_extract_union_with_none_inner`
  can satisfy. Degenerate all-None Unions fall through to the
  ordinary type-translation path. A defense-in-depth `assert`
  inside `_extract_union_with_none_inner` names the precondition
  so a future caller that skips the predicate fails loudly with
  a contract message instead of `IndexError`.
- **Aliased `Union` imports documented.** v0.3.2's Finding 1
  matcher accepts the bare `Union` head by name without checking
  import provenance, so `from somelib import Union; -> Union[X,
  None]` is treated as `typing.Union[X, None]` even when
  `somelib.Union` is unrelated. Symmetric to the existing
  aliased-`Optional` limitation. README's "Aliased Optional
  imports" entry is now "Aliased Optional / Union imports" and
  covers both. New fixture `tests/fixtures/documented_limits/aliased_union_import.py`
  pins the current behaviour. Same fix shape as the Optional
  case (symbol-table tracking), deferred to a future phase.
- **Local-class limitation extended to method bodies.** The
  README's "Local classes inside function bodies" entry was
  rephrased to "Local classes inside any function or method
  body." The underlying behaviour was already symmetric (the
  function walker does not descend into nested `ClassDef`
  regardless of whether the parent `FunctionDef` is at module
  scope or inside another `ClassDef`); only the documentation
  needed to catch up.

### Added

- `tests/test_round6_fixes.py` with 7 tests pinning:
  - 3 tests on each degenerate Union shape (no crash on
    translate, no crash through full pipeline).
  - `_is_union_with_none` rejects all-None Unions (predicate
    truthfulness).
  - `_is_union_with_none` still accepts the v0.3.2 Finding 1 happy
    path (negative test against an over-correction).
  - The defense-in-depth assertion fires with a contract-naming
    message when called on a Union with no non-None arms.
  - End-to-end pipeline runs clean on the degenerate input.
- `tests/test_documented_limits.py` gains
  `test_aliased_union_import_treated_as_typing_union` (+1 test)
  pinning the new fixture.
- `tests/fixtures/documented_limits/aliased_union_import.py` (new
  fixture). `tests/fixtures/documented_limits/README.md` updated
  with the new entry and the rephrased Local-classes entry.

### Tests

- 108 -> 116 (+8). All v0.3.2 tests pass identically.

### Unchanged

- The v0.3.2 Finding 1, 2, 3 fixes (Union recognition, string
  forward-references, nested-class method collection). The v0.3.3
  boundary fix tightens the predicate of Finding 1; it does not
  weaken any of the recognition shapes added in v0.3.2.
- All other documented limitations and their fixtures.
- `_extract_union_with_none_inner`'s positive-path return shape
  (single non-None arm returns directly; 2+ non-None arms
  left-fold into `BinOp(BitOr)`).

---

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
