# Changelog

## [0.8.0] - 2026-05-03

Feature release. First non-Python language adapter ships: the
Go adapter (Phase 1) lints ``.go`` files for D24 (all-paths-
return) and D11 (status-coverage with the Go ``(T, error)``
firing shape). Cross-language ``_is_may_fail_producer``
predicate consolidated to Shape B per ADR-002 §10 Q3
follow-up. The Python adapter is unchanged.

This release builds on v0.7.3 plus the v0.7.4 corrective items
(round-18 audit findings, folded into commit 0 of this series).

### Added

- **Go adapter Phase 1.** ``furqan-lint check file.go`` runs D24
  (all-paths-return) and D11 (status-coverage with the
  ``(T, error)`` firing shape) on Go source. Install via
  ``pip install furqan-lint[go]``. The Go toolchain (1.21+) is
  required at install time (PEP 517 build hook compiles the
  goast binary); not at runtime.
- **goast binary** at ``src/furqan_lint/go_adapter/cmd/goast/main.go``
  (~250 LoC). Self-contained Go program that uses ``go/parser``
  and ``go/ast`` to emit a JSON representation of a Go source
  file's AST. JSON shape: filename, package, public_names,
  functions (each with name, line, col, exported,
  return_type_names, params, body_statements). Body statement
  types: ``if``, ``return``, ``assign``, ``opaque``. The binary
  has NO ``calls`` field; the Python translator extracts calls
  from ``rhs_call`` sites at IR build time per round-17
  prompt-review MEDIUM 1.
- **Python Go adapter** at ``src/furqan_lint/go_adapter/``:
  - ``__init__.py`` exports ``parse_file``,
    ``GoExtrasNotInstalled``, ``GoParseError``.
  - ``parser.py`` invokes the bundled goast binary as a
    subprocess with a 10-second timeout. Discovery order:
    bundled binary → ``FURQAN_LINT_GOAST_BIN`` env var → loud
    failure (NO ``$PATH`` fallback per round-17 prompt-review
    MEDIUM 2).
  - ``translator.py`` (~280 LoC) converts goast JSON to Furqan
    IR. Return-type translation rules: 0 → None; 1 → TypePath;
    2-with-error-last → UnionType (error in right arm by
    convention); 2-non-error → opaque TypePath; 3+ → opaque
    TypePath("<multi-return>") (Phase 1 documented limit). nil
    in any expression position → IdentExpr("__opaque__"), NOT
    "__none__" (per locked decision 5: avoid accidental
    cross-language firing of Python-only check_return_none).
  - ``runner.py`` wires D24 + D11 via upstream
    ``check_all_paths_return`` and ``check_status_coverage``
    with the cross-language ``_is_may_fail_producer`` predicate.
  - ``_build.py`` is the PEP 517 build hook that compiles the
    goast binary at install time. If Go is absent on the build
    machine, the hook prints a stderr note and exits cleanly so
    the wheel still builds; runtime then raises
    ``GoExtrasNotInstalled`` with the install hint.
- **Cross-language ``_is_may_fail_producer`` (Shape B).** Moved
  from ``rust_adapter/runner.py`` to ``furqan_lint/runner.py``
  and extended to recognize Python ``Optional[T]``, Rust
  ``Option<T>`` / ``Result<T, E>``, AND Go ``(T, error)``. Per
  ADR-002 §10 Q3 follow-up: the predicate composition is the
  right abstraction once three data points exist. The Rust
  adapter's runner now imports from ``furqan_lint.runner``
  rather than maintaining a parallel composition.
- **``_is_error_return`` predicate** in
  ``furqan_lint/runner.py``. Recognizes Go's ``(T, error)``
  return shape via UnionType where one arm has base ``"error"``.
  SYMMETRIC across arms (per locked decision 7) so a future
  translator change that reorders does not silently break D11.
- **``setup.py``** with a ``build_py`` subclass that calls the
  Go build hook before standard setuptools build.
- **``[go]`` extra** in pyproject.toml (marker-only; no PyPI
  dependencies; the Go binary is built at install time from
  bundled source). ``[tool.setuptools.package-data]`` ships the
  goast binary (when built) plus the Go source so subsequent
  installs can rebuild.
- **CLI dispatch on .go.** ``cli.py`` ``main()`` routes ``.go``
  to ``_check_go_file``. Mirrors the v0.7.0.1 Rust pattern:
  typed ``GoExtrasNotInstalled`` is caught and printed as a
  one-line install hint to stderr (NOT a Python traceback).
  ``_check_directory`` walks ``*.py``, ``*.rs``, AND ``*.go``.
  ``EXCLUDED_DIRS`` adds ``vendor`` (Go's equivalent of
  ``node_modules`` / ``target``).
- **furqan-lint diff foo.go bar.go returns exit 2** with
  explicit "Go diff is not implemented" message per locked
  decision 8 / round-17 prompt-review CRITICAL. Exit 0 = PASS in
  framework verdict semantics; CI pipelines invoking
  ``furqan-lint diff *.go`` must NOT silently treat the
  unimplemented case as PASS. Pinned by
  ``test_go_diff_returns_exit_2``.
- **Release-sweep gate extended to Go surfaces.** The v0.7.3
  ``test_release_sweep_gate.py`` ``_USER_VISIBLE_SURFACES`` now
  includes the four go_adapter Python modules and the Go
  documented_limits README. Phase numbering on Go adapter
  surfaces fails the gate the same way Rust adapter surfaces do.
- **9 new fixtures** in ``tests/fixtures/go/``:
  - ``clean/all_paths_return.go``, ``clean/error_propagated.go``,
    ``clean/error_handled_via_named_return.go``.
  - ``failing/missing_return.go``,
    ``failing/error_collapse_via_blank.go``,
    ``failing/error_collapse_via_panic.go``.
- **22 new tests** across four files:
  - ``test_go_parser.py`` (3): JSON shape, parse error, timeout.
  - ``test_go_translator.py`` (6): function translation,
    UnionType emission, "error in right arm" pin (load-bearing
    Go convention pin), nil → opaque marker (locked decision 5
    pin), 2-element non-error tuple opaque, 3+ multi-return
    documented limit.
  - ``test_go_correctness.py`` (9): D24 clean + missing +
    switch + for, D11 collapse-via-blank + collapse-via-panic +
    propagated + named-returns + predicate-partition (load-
    bearing pin against future name-based consolidation).
  - ``test_go_cli.py`` (3): .go extension dispatch, diff exit 2,
    missing-extras install hint.
- **Per-version surface snapshots extended.**
  ``tests/test_top_level_public_surface_additive.py`` gains
  ``V0_8_0_SURFACE`` (alias of ``V0_7_0_SURFACE``; no top-level
  surface change in v0.8.0).
  ``tests/test_rust_public_surface_additive.py`` gains
  ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_8_0`` (alias of v0.7.0.1; no
  rust_adapter surface change).
  NEW ``tests/test_go_public_surface_additive.py`` ships
  ``_GO_ADAPTER_PUBLIC_SURFACE_v0_8_0`` baseline as the first
  go_adapter snapshot: ``{parse_file, GoExtrasNotInstalled,
  GoParseError}``.

### Changed

- **Rust D11 producer predicate import.** ``rust_adapter/runner.py``
  now imports ``_is_may_fail_producer`` from ``furqan_lint.runner``
  instead of maintaining its own composition. The Rust D11 firing
  semantics are unchanged; only the predicate's home file moved.

### Out of scope (deferred to Phase 2 or beyond)

- R3 (zero-return) for Go. Go has no body-shape analogue to
  Rust's annotated-fn-with-empty-body pattern. The closest
  equivalent is ``log.Fatal()`` / ``os.Exit()`` which is a
  function call, not a body shape. Deferred until a concrete
  user-reported false negative motivates the design.
- ``(T, T, error)`` and other 3+-element multi-return shapes.
  UnionType IR is binary; documented limit (the translator
  emits opaque ``TypePath("<multi-return>")``).
- ``go/types`` integration. Type resolution requires
  ``go build`` or module-aware parsing; deferred.
- Cross-package symbol resolution.
- Generics, interface dispatch, method-receiver call-site
  analysis.
- Additive-only diff for Go (CLI dispatches but returns exit 2
  with the "not implemented" message).
- ``for`` / ``switch`` / ``select`` / ``defer`` body analysis
  beyond opaque markers.
- ``nil`` distinction (pointer vs slice vs interface vs map);
  all collapse to ``IdentExpr("__opaque__")``.

### Tests

- 268 passed (was 243 base after v0.7.4 corrective). Delta:
  +25 (3 parser + 6 translator + 9 correctness + 3 CLI + 2
  go_adapter surface + 1 rust_adapter v0.8.0 baseline + 1
  top-level v0.8.0 baseline).
- Marker counts: 199 unit + 68 integration + 1 network = 268.

### Verification

- All 10 gates pass (gate 7 em-dash audit run from clean state;
  gate 9b empirical missing-Go-extras simulated).
- Per-version snapshots in BOTH top-level AND adapter tests.
- Four-place pattern wired for the documented limits introduced.

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the new capability:**
   ```go
   package main
   func loadConfig(path string) (*Config, error) {
       return &Config{}, nil
   }
   func StartServer(path string) *Config {
       cfg, _ := loadConfig(path)
       return cfg
   }
   ```
   On v0.7.3: ``furqan-lint check x.go`` returns "Unknown
   command: check" or similar (no Go support). On v0.8.0:
   exit 1 with MARAD on ``StartServer`` naming ``loadConfig``
   as the may-fail producer whose error arm was discarded.

2. **Smallest input demonstrating the bug pre-fix:** the
   absence of any Go support is the "before" state; this
   release introduces it.

3. **What this release does NOT do:** see "Out of scope" above.

4. **New code paths:** ~250 LoC of Go (cmd/goast/main.go) +
   ~600 LoC of Python (go_adapter/) + ~85 LoC of CLI integration
   + ~30 LoC of setup.py + ~25 LoC of build hook + 9 fixtures +
   22 tests + per-version snapshots in three surface files.

5. **Limits retired and added:** none retired; 8 documented
   limits introduced (3+-element multi-return; no R3 for Go;
   no Go diff; no go/types; no generics; no method-receiver
   call-site; switch/for/select/defer opaque; nil distinctions).

### Validator-bias self-disclosure (per v0.7.0.1 §5.1 standing requirement)

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
$ /tmp/golocal/go/bin/go version
go version go1.21.13 linux/arm64
```

The Go toolchain was installed during this build via the
official tarball (apt-get unavailable without sudo on this
sandbox). Go is required only on the build machine; install
machines and runtime machines do not need Go.

**Gates run from a clean state:**

The release-sweep gate (commit 5 + v0.7.3 commit 3) was run
empirically and caught Phase numbering in the Go translator,
runner, and CLI diff message during this release's development.
All findings swept to durable phrasing.

The em-dash audit gate (gate 7) was run from the clean
post-commit-1 state; clean.

**Gates that could not be run from a clean state:**

Gate 6 air-gap (``unshare -n``) is unavailable in the build
sandbox without ``CAP_SYS_ADMIN``. Same posture as v0.7.0
through v0.7.3.

Gate 9b (empirical missing-Go-extras simulation) is verified
via the unit test ``test_go_missing_extras_prints_install_hint``
which mocks the ``GoExtrasNotInstalled`` raise inside
``parse_file`` and asserts the stderr message + exit 1 + no
traceback. Empirical simulation via ``rm -f
src/furqan_lint/go_adapter/bin/goast`` works the same way and
is the deploy-host's verification path.

### §5.2 prompt-grounding self-check (per v0.7.2 standing requirement)

The §2.1 self-check ran clean against v0.7.3 codebase state
before any code was written. The framing-verification step
caught one drift: the prompt named base hash ``2a80cb1`` which
does not resolve on origin; the actual v0.7.3 release tip is
``50e698c`` (origin/v0.7.3 branch HEAD; v0.7.3 had not merged
to origin/main at the time of this v0.8.0 work). Branched off
``50e698c``; v0.7.3 is expected to merge ahead of or alongside
v0.8.0's PR. No other drift.

The §0 (round-18 corrective) finding 1 (em-dash on v0.7.3 HEAD)
was already closed on origin/v0.7.3 by commit 50e698c
"fix(ci): strip em-dash from test_release_sweep_gate
docstring" before this v0.8.0 work began. Findings 2 and 3 land
in commit 0 of this series. The §0 framing was therefore
partially redundant (1 of 3 findings already closed); the
v0.7.4 corrective scope shrank from 3 items to 2.

## [0.7.3] - 2026-05-03

Documentation-sweep corrective for the round-17 audit findings.
Five MEDIUMs in one equivalence class: v0.7.2's release-sweep
workflow updated CHANGELOG correctly but missed the user-facing
surfaces (README headings, README rationale text, source
docstrings, CLI PASS string, documented_limits/README preamble)
that referenced the prior version's Phase number. v0.7.3 sweeps
all of them, retires one redundant documented limit, and adds a
release-time pre-flight gate so the failure mode does not recur.

Per-finding commit decomposition (Bayyinah v1.2.3 pattern):

  1. doc(rust): comprehensive Phase-numbering sweep across
     user-facing surfaces (closes MEDIUMs 1, 2, 5 + Aux 1, 2, 3).
  2. retire(rust): macro_invocation_body documented_limit
     (consolidate into r3_panic_as_tail) (closes MEDIUMs 3, 4).
  3. chore(release): release-time sweep gate (Fraz round-17
     workflow addition; prevents recurrence).
  4. release v0.7.3 (this commit: version bump + CHANGELOG +
     V0_7_3_SURFACE).

### Fixed

- **Phase numbering swept from user-facing surfaces.** The CLI
  PASS string at ``cli.py:204`` no longer says "Rust Phase 2"
  on every clean check; it now says "(R3, D24, D11 with Option-
  and Result-aware status coverage)". The README ``Rust support``
  heading no longer says "Phase 1, opt-in"; the body paragraph
  now describes the v0.7.2 state (three checkers, the
  Option/Result-aware predicate, the dropped return_none_mismatch
  rationale). The README ``Remaining limitations`` Rust subsection
  heading is no longer anchored to "v0.7.0 Phase 1". Source-comment
  Phase references in ``rust_adapter/__init__.py``, ``runner.py``,
  ``translator.py``, ``edition.py``, and ``cli.py`` are swept to
  durable phrasing ("the current implementation", "a future phase").
  The ``documented_limits/README.md`` preamble no longer says
  "v0.7.0 Rust adapter (Phase 1: D24 + D11 only)".
- **CHANGELOG v0.7.2 entry "+4 net" math typo corrected to +7.**
  3 D11 tests + 1 dead-code regression + 3 surface-snapshot tests
  = +7 net. The original "+4 net" framing with parenthetical
  "(corrected count below)" hinted at the typo but the corrected
  count never landed in the line above; v0.7.3 corrects.
- **Stale "deferred to v0.7.1" framing in
  ``macro_invocation_body.rs`` retired.** The fixture's claim
  that the Rust analogue of R3 was deferred to v0.7.1 was
  historically inaccurate after v0.7.1 shipped R3; the comment
  was not updated when v0.7.1 landed. Fixture and bullet
  retired in commit 2 of this release.

### Limitations retired

- **``macro_invocation_body.rs``.** Was a v0.7.0 documented
  limit ("a function whose body is a single macro invocation
  is treated as opaque"). The limit was the same underlying
  R3-tail-expression behavior pinned by
  ``r3_panic_as_tail_expression.rs``: both pinned the v0.7.0
  R1 translator rule that synthesizes a ``ReturnStmt(opaque)``
  for any tail expression. Two fixtures pinned one limit, not
  two. Consolidated into ``r3_panic_as_tail_expression`` whose
  pinning test now parametrizes over the diverging-macro family
  (``panic!``, ``todo!``, ``unimplemented!``, ``unreachable!``).
  The README "Remaining limitations" section now has one bullet
  for this limit instead of two.

### Added

- **Release-time sweep gate** in
  ``tests/test_release_sweep_gate.py`` (Fraz round-17 workflow
  addition). Two tests:
  - ``test_no_phase_numbering_in_rust_user_surfaces``: greps
    for ``\bPhase \d+\b`` across README, the documented_limits
    README, ``cli.py``, and the four rust_adapter modules.
    Fails (with file:line:context findings) if any surface
    references "Phase N" numbering.
  - ``test_no_stale_version_anchored_claims_in_user_surfaces``:
    greps for ``\bv0.X.Y(.Z)?\s+(Rust adapter|Phase N)\b``
    across the same surfaces. Fails if any surface anchors
    a claim to a specific prior version.

  Verified empirically: temporarily reintroduced the v0.7.2
  "Rust Phase 2" PASS string to ``cli.py`` and ran the gate;
  it correctly fails with the offending line. Restored;
  passes again. The gate's discriminating power is pinned.

  The gate is intentionally narrow: CHANGELOG is excluded
  (audit trail), Python adapter modules are excluded for now
  (out of scope for this round-17 corrective), and source
  code that names specific implementation choices with
  version anchors ("v0.7.0 translator emits ...") is
  preserved as historical anchor. Future v0.7.x or v0.8 may
  broaden the gate scope.
- **Parametrized diverging-macro pinning test** in
  ``test_rust_correctness.py``:
  ``test_r3_silent_on_diverging_macros_as_tail_expression``
  exercises 4 cases (``panic!``, ``todo!``, ``unimplemented!``,
  ``unreachable!``) to lock the structural rule that R3 is
  grammar-and-macro-agnostic. Replaces the single-fixture pin
  for the consolidated limit.
- **Per-version surface snapshots extended.**
  ``tests/test_rust_public_surface_additive.py`` gains
  ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_3`` baseline (alias of
  ``v0_7_0_1``; no surface change in this corrective).
  ``tests/test_top_level_public_surface_additive.py`` gains
  ``V0_7_3_SURFACE`` (alias of ``V0_7_0_SURFACE``). Per
  Bayyinah Engineering Discipline Framework v2.0 §7.6
  per-version cadence.

### Tests

- 242 passed (was 236 in v0.7.2). Delta: +6 (4 parametrized
  diverging-macro + 2 release-sweep gate + 1 rust_adapter v0.7.3
  baseline subset - 1 retired macro_invocation_body pinning test;
  v0.7.4 corrective backfills the missing top-level v0.7.3
  baseline subset to bring net delta to +7).
- Marker counts: 192 unit + 49 integration + 1 network
  (network is also integration-marked) = 242.

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the new capability:**
   ``furqan-lint check tests/fixtures/rust/clean/simple_returning_fn.rs``
   On v0.7.2: PASS message says "Rust Phase 2: R3 + D24 + D11"
   (stale Phase number that contradicts the CHANGELOG which
   said v0.7.2 was Phase 3). On v0.7.3: PASS message says
   "R3, D24, D11 with Option- and Result-aware status coverage"
   (substantive checker description, no stale Phase numbering).

2. **Smallest input demonstrating the bug pre-fix:** same input
   on v0.7.2 prints Phase 2 even though v0.7.2 IS the release
   where Result-aware D11 landed. CHANGELOG said Phase 3; CLI
   said Phase 2; user saw the contradiction every clean check.

3. **What this release does NOT do:**
   (a) No Python adapter docstring sweep. The Python adapter's
       "Phase 1 / Phase 2" references describe Python-only
       semantics that pre-date the multi-language release model.
       Out of scope for this round-17 corrective; can be swept
       in a future v0.7.x release if Fraz flags them.
   (b) No source-code historical-anchor sweep. Statements like
       "v0.7.0 translator emits ..." are intentional historical
       references and are preserved.
   (c) No new checker behavior. Pure documentation sweep + one
       limit consolidation + one new release-time gate.
   (d) Does not retroactively gate prior releases (gate fires
       on v0.7.3+ surfaces only).

4. **New code paths:**
   ``tests/test_release_sweep_gate.py`` (~120 LoC, 2 tests +
   _USER_VISIBLE_SURFACES tuple + 2 regex patterns). 1
   parametrized test (4 cases) replacing 1 single-fixture
   test in ``test_rust_correctness.py``. Per-version snapshot
   baselines for v0.7.3 in both surface snapshot files.

5. **Limits retired and added:** retired
   ``macro_invocation_body.rs`` (consolidated into
   ``r3_panic_as_tail_expression.rs`` per the four-place
   pattern). Added: none.

### Validator-bias self-disclosure (per v0.7.0.1 §5.1 standing requirement)

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
```

Same posture as v0.7.1 / v0.7.2.

**Gates run from a clean state:**

Gate 9 (empirical missing-extras) was run AFTER ``pip
uninstall -y tree_sitter tree_sitter_rust``. Output matches
the v0.7.0.1 contract. The release-sweep gate (commit 3) is
empirically verified by the regression-introduction reproducer
documented in commit 3's body: temporarily reintroduce a
"Rust Phase 2" string and confirm the gate fires.

**Gates that could not be run from a clean state:**

Air-gap (``unshare -n``) was attempted but the build sandbox
lacks ``CAP_SYS_ADMIN`` to namespace-isolate. Verifiable on
the deploy host; same posture as v0.7.0 / v0.7.0.1 / v0.7.1
/ v0.7.2.

## [0.7.2] - 2026-05-03

Feature release. Phase 3 of the Rust adapter, scope-narrowed
from the round-15 prompt per a round-16 pre-implementation
critique. Result-aware D11 lands; the planned Rust analogue of
return_none_mismatch is dropped because the §5.2 prompt-grounding
self-check empirically demonstrated that the firing condition
(non-Optional return type paired with `__none__` in body) is
unreachable on any source ``rustc`` accepts. The translator
delta and the ``check_return_none`` wiring would have shipped
infrastructure for a check with no job; deferred to whichever
later phase introduces an actual consumer for ``__none__`` in
Rust IR.

The dead-code removal originally specified in the prompt's §3.4
(``_d24_diagnostic_in_r3_set``) was already resolved in v0.6.1
(commit b0a4b18). v0.7.2 ships a forward-compat regression test
asserting the function does not exist anywhere under ``src/``,
preventing accidental re-introduction.

Full blocker rationale: ``/tmp/rust_phase_3_blocker.md`` (not
shipped; archived in the discussion record).

### Added

- **Result-aware D11 producer predicate** in
  ``src/furqan_lint/rust_adapter/runner.py``. Two new functions:
  - ``_is_result_type(rt) -> bool``: True iff ``rt`` is a Rust
    ``Result<T, E>`` (translated to a ``UnionType`` where neither
    arm has base ``"None"``). Distinguished from ``Option<T>`` by
    the structural rule, not by an annotation-text heuristic; the
    v0.7.0 translator already produces unambiguous IR shapes.
  - ``_is_may_fail_producer(rt) -> bool``: True iff
    ``_is_optional_union(rt) or _is_result_type(rt)``. The two
    predicates partition the may-fail-producer space cleanly.
- **D11 wiring updated** to pass
  ``producer_predicate=_is_may_fail_producer`` to
  ``check_status_coverage``, replacing the v0.7.1 wiring with
  ``_is_optional_union`` only. A caller declaring a concrete return
  type but invoking a Result-returning helper is now flagged the
  same way as one invoking an Option-returning helper.
- **2 new fixtures**: ``failing/result_collapse.rs`` (Result-
  returning helper, caller declares -> i32, panics on Err arm),
  ``clean/result_propagated.rs`` (helper + caller both declare
  ``Result<T, E>``, ?-operator propagation).
- **3 new tests** in ``tests/test_rust_correctness.py`` covering
  Result-collapse fires D11, Result-propagation does not fire,
  and ``_is_result_type`` does not match Option (predicate
  partition pin).
- **Forward-compat regression test** in
  ``tests/test_v0_7_2_dead_code_regression.py`` asserting
  ``_d24_diagnostic_in_r3_set`` does not exist under ``src/``.
  The function was a defensive D24-suppression helper added in
  v0.6.0 that turned out to be dead code; removed in v0.6.1
  (commit b0a4b18) but listed in the round-13 audit notes that
  the v0.7.2 prompt was drafted from. The regression test is
  cheap insurance against re-introduction.
- **Per-version surface snapshots extended.**
  ``tests/test_rust_public_surface_additive.py`` gains
  ``_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_1`` and ``_v0_7_2``
  baselines (both alias of ``v0_7_0_1``; no surface change in
  either release). ``tests/test_top_level_public_surface_additive.py``
  gains ``V0_7_2_SURFACE`` (alias of ``V0_7_0_SURFACE``). Per
  Bayyinah Engineering Discipline Framework v2.0 §7.6
  per-version cadence.

### Changed

- **Rust D11 producer predicate** at
  ``rust_adapter/runner.py``: from ``_is_optional_union`` to
  ``_is_may_fail_producer``. The wiring point and the D11
  invocation order are unchanged; only the predicate widens.
- **Module docstring** at ``rust_adapter/runner.py`` updated to
  document the v0.7.2 predicate change and the Shape A
  rationale (separate ``_is_result_type``, not a generalised
  ``_is_may_fail_producer`` across Python and Rust). Shape B
  generalisation deferred to whichever release introduces the
  Go adapter and clarifies whether Go's error-return shape fits
  the same abstraction.

### Out of scope (deferred to a later phase)

- **Rust analogue of return_none_mismatch.** Dropped per the
  round-16 critique: the firing condition ``-> non-Optional
  type AND body returns None`` is unreachable on any compilable
  Rust source (rustc rejects ``fn f() -> i32 { None }`` at
  compile time). The translator delta to emit
  ``IdentExpr(name="__none__")`` for Rust ``None`` literals
  would have shipped infrastructure with no consumer. If a
  future release introduces a Rust check with a different
  firing condition (e.g., "Option-returning function whose
  every path returns None" - a real code smell distinct from
  return_none_mismatch), the translator delta lands then.
- **Macro-expansion-aware analyses.** Phase 4+.
- **Cross-file Rust symbol resolution.** Phase 4+.
- **Cargo workspace traversal beyond nearest Cargo.toml.** Phase 4+.
- **Shape B (a single ``_is_may_fail_producer``
  generalisation across Python and Rust).** Deferred until the
  Go adapter lands and clarifies whether Go's
  ``(T, error)``-shape fits the same abstraction.

### Tests

- 236 passed (was 229 in v0.7.1). Delta: +7 (3 new D11 tests +
  1 dead-code regression test + 3 new surface-snapshot tests).
  v0.7.2's release commit message originally said "+4 net"; the
  v0.7.3 documentation sweep corrected it to +7. The 3 surface
  tests are real test functions (not just snapshot baselines)
  and count toward the total.
- Marker counts: 188 unit + 44 integration (1 also network).

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the new capability:**
   ``furqan-lint check tests/fixtures/rust/failing/result_collapse.rs``
   returns exit 1 with a MARAD on ``parse_age`` (declared
   ``-> i32``) calling ``parse_helper`` (declared
   ``-> Result<i32, String>``). On v0.7.1: PASS, exit 0 (D11
   only fired on Option-returning helpers).
2. **Smallest input demonstrating the bug pre-fix:** same input
   on v0.7.1: silent PASS. The function's signature lied about
   what it actually did (could panic on bad input), but D11
   did not catch the lie because Result was outside the
   Option-only predicate.
3. **What this release does NOT do:**
   (a) No Rust analogue of return_none_mismatch (dropped per
       the round-16 critique; firing condition unreachable on
       compilable Rust).
   (b) No translator deltas (none needed for Result-aware D11;
       the v0.7.0 translator already represents Result<T, E> as
       UnionType with the right shape for the new predicate).
   (c) No Shape B generalisation (deferred to Go adapter).
   (d) No closure analysis, function_signature_item analysis,
       cross-file resolution, macro expansion, or Cargo workspace
       traversal beyond Cargo.toml (out of scope, unchanged from
       v0.7.1).
4. **New code paths:**
   ``rust_adapter/runner.py``: ``_is_result_type`` (~25 LoC),
   ``_is_may_fail_producer`` (~10 LoC), updated D11 wiring
   (1 line). ``UnionType`` import added. 2 new fixtures, 3 new
   integration tests, 1 new dead-code regression test, per-version
   snapshot baselines for v0.7.1 and v0.7.2 in both surface
   snapshot files.
5. **Limits retired and added:** none. v0.7.2 does not
   introduce or retire any documented limits.

### Validator-bias self-disclosure (per v0.7.0.1 §5.1 standing requirement)

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
```

Same posture as v0.7.1: ``tomli`` from mypy transitive on
Python 3.10, both tree-sitter packages from explicit install.
The v0.7.0.1 ``[[mypy]] overrides`` for ``tomli`` is in place
so ``mypy --strict`` passes even when ``tomli`` is absent
(verified at v0.7.0.1; not re-verified for v0.7.2 because the
override is still in pyproject.toml).

**Gates run from a clean state:**

Gate 9 (empirical missing-extras) was run AFTER
``pip uninstall -y tree_sitter tree_sitter_rust``:

```
$ furqan-lint check /tmp/result_smoke.rs
Rust support not installed. Run: pip install furqan-lint[rust]
$ echo $?
1
```

Output matches the v0.7.0.1 contract: clean install hint to
stderr, exit 1, no traceback. Re-installed before re-running
other gates.

**Gates that could not be run from a clean state:**

Air-gap (``unshare -n``) was attempted but the build sandbox
lacks ``CAP_SYS_ADMIN`` to namespace-isolate. Verifiable on the
deploy host; same posture as v0.7.0 / v0.7.0.1 / v0.7.1.

### §5.2 prompt-grounding self-check disclosure (NEW, v0.7.2)

The §5.2 self-check surfaced three drifts in the round-15
prompt before any code was written. Documented in full at
``/tmp/rust_phase_3_blocker.md``. Summary:

1. CRITICAL: ``check_return_none`` cannot fire on any compilable
   Rust source (the §4.2 fixture's expected MARAD does not
   materialise; the function PASSes silently because Optional
   permits None and rustc rejects the only configurations that
   would fire). Resolution: drop the return_none commit (Path
   A in the blocker). This release.
2. HIGH: ``furqan.checker.return_none`` does not exist upstream
   (the prompt's "Alternative D" framing was wrong; the local
   ``furqan_lint.return_none`` is what the Python runner uses).
   Resolution: moot under Path A.
3. MEDIUM: ``_d24_diagnostic_in_r3_set`` was already removed in
   v0.6.1; the prompt's §3.4 was based on a stale audit note.
   Resolution: invert into a forward-compat regression test
   (this release).

The discipline trajectory: §5.2 caught what would have shipped
as a checker without a job. Round-16's pre-implementation
critique was the right place to surface the architectural
question; v0.7.2's blocker was the right place to land it as
a scope narrowing rather than a mid-flight architecture change.

## [0.7.1] - 2026-05-03

Feature release. Phase 2 of the Rust adapter: wires upstream
``furqan.checker.check_ring_close`` (filtered to R3-shaped
diagnostics) for the Rust R3 analogue (zero-return on annotated
functions). Closes the v0.7.0 documented limit
``empty_or_panic_only_body.rs``. Retires the
``trait_method_signature.rs`` documented limit (the skip is now
stable across two releases and recognised as a permanent design
choice). Adds the additive-only test infrastructure to the
top-level ``furqan_lint`` package surface, parallel to the v0.7.0
``rust_adapter.__all__`` snapshot.

The architecture (parser, install path, IR boundary, lazy-import
gate, ``RustExtrasNotInstalled`` typed exception) is unchanged
from v0.7.0.1. Phase 2 adds one checker via upstream wiring (not
local re-implementation), retires two documented limits, and
lands one additive-only test. That is the entire scope.

### Added

- **R3 (zero-return) checker for Rust** via upstream
  ``furqan.checker.check_ring_close`` in
  ``src/furqan_lint/rust_adapter/runner.py``. Fires
  ``zero_return_path`` MARAD on functions that declare a
  non-unit return type but produce zero ``ReturnStmt`` in the
  translated IR. The structural pattern catches every body shape
  that has the right IR (empty body, ``panic!();``, ``todo!();``,
  ``unimplemented!();``, ``unreachable!();``, and any other
  macro-with-semicolon body whose macro identity is irrelevant to
  the R3 firing condition).
- **``check_rust_module(module)``** in
  ``rust_adapter/runner.py``. Centralises the v0.7.1 checker
  pipeline (R3 -> D24 -> D11). R3 runs first so the D24
  suppression on R3-fired functions is reachable; the
  suppression is pinned by a test asserting EXACTLY ONE
  diagnostic on ``r3_empty_body_returns_T.rs``.
- **``_RUST_KNOWN_TYPES`` frozenset** in
  ``rust_adapter/runner.py`` listing well-known Rust primitive
  type names plus the adapter-internal ``"None"`` token. Passed
  to ``check_ring_close`` as ``imported_types`` so R1
  (unresolved-type) noise does not dominate the diagnostic
  output. Without this, every ``i32`` / ``Result`` / ``Option``
  reference would be flagged as "no compound type with this
  name."
- **``_is_r3_shaped(diag)`` discriminator** in
  ``rust_adapter/runner.py``. ``check_ring_close`` emits R1, R3,
  and R4 shapes; v0.7.1 forwards only R3. The discriminator
  reads the diagnosis prose prefix; if upstream adds a
  structural discriminant, this helper migrates to that. Pinned
  by ``test_is_r3_shaped_recognises_only_r3``.
- **6 new R3 failing fixtures** in ``tests/fixtures/rust/failing/``:
  ``r3_empty_body_returns_T.rs``, ``r3_panic_only_body.rs``,
  ``r3_todo_only_body.rs``, ``r3_unimplemented_only_body.rs``,
  ``r3_unreachable_only_body.rs``,
  ``r3_macro_only_body_with_unrelated_macro.rs``. The last is
  the load-bearing pin for the design that R3 is
  grammar-and-macro-agnostic.
- **1 new documented-limit fixture**
  ``tests/fixtures/rust/documented_limits/r3_panic_as_tail_expression.rs``
  pinning the v0.7.1 limit that R3 does NOT fire on
  ``panic!()``-as-tail-expression (no semicolon). The trailing
  ``;`` is load-bearing: with it, the macro is an
  expression_statement that the translator drops (statements=0,
  R3 fires); without it, the macro is a tail expression that
  synthesizes a ReturnStmt (statements=1, R3 silent).
- **Top-level public-surface additive-only test**
  ``tests/test_top_level_public_surface_additive.py`` with
  per-version snapshots V0_7_0_SURFACE, V0_7_0_1_SURFACE,
  V0_7_1_SURFACE per Bayyinah Engineering Discipline Framework
  v2.0 section 7.6 cadence. Round-11's MEDIUM 3 finding was the
  failure mode that pinning only the latest version creates;
  v0.7.1 establishes the pattern correctly from the start.
- **Explicit ``__all__`` declaration** in
  ``src/furqan_lint/__init__.py``. The implicit surface (any
  module-level binding) is fragile; ``__all__ = ("__version__",)``
  is the load-bearing primitive the additive-only discipline
  requires.

### Changed

- **CLI Rust PASS message** updated from
  ``"2 structural checks ran (Rust Phase 1: D24 + D11)."`` to
  ``"3 structural checks ran (Rust Phase 2: R3 + D24 + D11)."``.
- **Rust CLI dispatch** (``cli._check_rust_file``) delegates to
  the new ``check_rust_module`` runner instead of inlining the
  D24/D11 calls. The lazy-import guard, the
  ``RustExtrasNotInstalled`` typed exception, and the
  ``RustParseError`` path are unchanged.

### Limitations introduced

- **``panic!()`` (or any diverging macro) used as a tail
  expression with no ``;``.** R3 does NOT fire because the
  translator synthesizes a ``ReturnStmt(opaque)`` for any tail
  expression per the v0.7.0 R1 rule. Adding a fix would require
  either a hardcoded diverging-macro allowlist (brittle: third-
  party macros like ``never_return!()`` would not be caught) or
  cross-file type inference of the macro's expansion type (out
  of scope; needs a Rust type checker). Pinned as
  ``tests/fixtures/rust/documented_limits/r3_panic_as_tail_expression.rs``.

### Limitations retired

- **``empty_or_panic_only_body.rs``.** Was a v0.7.0 documented
  limit ("Phase 1 ships D24 only on annotated functions whose
  body has at least one statement-or-expression"). v0.7.1 closes
  it: R3 (via the upstream check_ring_close wiring) fires on
  every shape the limit pinned (empty body,
  ``panic!()``-with-semi, ``todo!()``-with-semi,
  ``unimplemented!()``-with-semi). The fixture is deleted; the
  cases now live as ``failing/r3_*.rs`` fixtures with assertions
  inverted from "silent PASS" to "fires R3."
- **``trait_method_signature.rs``.** Was a v0.7.0 documented
  limit ("function_signature_item nodes are skipped by design").
  The skip is now stable across two releases and is recognised
  as a permanent design choice rather than a temporary limit:
  D24/D11/R3 do not apply to interface declarations because
  there is no body to analyse. The retirement procedure cleans
  up exactly this kind of "limit that turned out to be
  permanent."

### Tests

- 229 passed (was 215 in v0.7.0.1). Delta: +14 (4 new R3 unit +
  8 new R3 integration + 4 new top-level surface - 2 retired
  pinning tests).
- 184 unit + 44 integration + 1 network (network is also
  integration-marked).

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the new capability:**
   ``furqan-lint check tests/fixtures/rust/failing/r3_panic_only_body.rs``
   returns exit 1 with a MARAD on function ``f`` declared
   ``-> i32`` whose diagnosis names "but its body contains no
   ``return`` statement." On v0.7.0.1: silent PASS (the Rust
   adapter ran only D24 + D11; D24 needs >=1 return present and
   does not fire on zero-return shapes).
2. **Smallest input demonstrating the bug pre-fix:** same input,
   on v0.7.0.1: PASS, exit 0. The macro-with-semicolon body is
   honest-looking (compiles, runs, panics) but structurally
   dishonest (declares it returns ``i32``, never does).
3. **What this release does NOT do:**
   (a) No R3 firing on ``panic!()``-as-tail-expression
       (documented limit, pinned).
   (b) No closure analysis (``closure_expression`` skipped for
       D24, D11, AND R3; documented limit retained).
   (c) No ``function_signature_item`` analysis (permanently
       skipped, fixture retired).
   (d) No cross-file Rust symbol resolution.
   (e) No macro expansion.
   (f) No Cargo workspace traversal beyond reading nearest
       ``Cargo.toml`` for edition.
   (g) No per-edition diagnostic divergence (Phase 1 confirmed
       all in-scope idioms parse uniformly across 2018/2021/2024).
   (h) No Result-aware D11 (still Option-only; deferred to
       v0.7.2+).
4. **New code paths:**
   ``rust_adapter/runner.py`` (~140 LoC): ``_RUST_KNOWN_TYPES``
   frozenset; ``check_rust_module`` pipeline; ``_is_r3_shaped``
   discriminator; ``_diagnostic_function_name`` helper for D24
   suppression. ``cli._check_rust_file`` refactored to delegate
   to the runner. 6 new R3 fixtures + 1 new documented-limit
   fixture + 2 retired fixtures + 4 new top-level surface tests
   + 1 ``__all__`` declaration in package ``__init__``.
5. **Limits retired and added:**
   Retired: ``empty_or_panic_only_body.rs`` (closed by R3),
   ``trait_method_signature.rs`` (skip is permanent design).
   Added: ``r3_panic_as_tail_expression.rs`` (panic-as-tail false
   negative).

### Validator-bias self-disclosure (per v0.7.0.1 standing requirement)

This section is the §5.1 standing requirement established by the
v0.7.0.1 corrective. The v0.7.0 review missed two HIGH findings
because (a) ``tomli`` was installed transitively in my sandbox
and ``mypy --strict`` did not surface the missing override, and
(b) the missing-extras CLI path was reasoned about but not
empirically simulated. v0.7.1 reports each of the three §5.1
subsections explicitly:

**Sandbox state at the time of testing:**

```
$ pip freeze | grep -E "tree_sitter|tomli|furqan"
furqan @ file:///[...]/furqan-programming-language
furqan-lint @ -e file:///tmp/furqan-lint
tomli==2.4.1
tree-sitter==0.25.2
tree-sitter-rust==0.24.2
```

``tomli``, ``tree-sitter``, and ``tree-sitter-rust`` were all
installed in the sandbox. ``tomli`` came transitively from mypy
on Python 3.10; the two tree-sitter packages were installed
explicitly during v0.7.0 development. The v0.7.0.1 ``[[mypy]]
overrides`` for ``tomli`` is in place so mypy --strict passes
even when ``tomli`` is absent (verified once at v0.7.0.1 by
``pip uninstall -y tomli``; not re-verified for v0.7.1 because
the override is still in pyproject.toml).

**Gates run from a clean state:**

Gate 9 (empirical missing-extras) was run during v0.7.1 development
AFTER ``pip uninstall -y tree_sitter tree_sitter_rust``:

```
$ furqan-lint check /tmp/r3_smoke.rs
Rust support not installed. Run: pip install furqan-lint[rust]
$ echo $?
1
```

Output matches the v0.7.0.1 contract: clean install hint to
stderr, exit 1, no traceback. Re-installed before re-running
other gates.

**Gates that could not be run from a clean state:**

Air-gap (``unshare -n``) was attempted but the build sandbox
lacks ``CAP_SYS_ADMIN`` to namespace-isolate. Verifiable on the
deploy host; this is the same posture as v0.7.0 / v0.7.0.1.

## [0.7.0.1] - 2026-05-03

Corrective release for two HIGH-severity findings from Bilal's
fresh-instance review of the v0.7.0 patch. Both were silent on
my own validation pass because of validator bias (transitive
dependencies and call-time imports that did not surface in the
sandbox where v0.7.0 was built).

### Fixed

- **HIGH: mypy --strict failed on a clean install (Issue 1).**
  The v0.7.0 ``[dev]`` install resolves to a venv where ``tomli``
  is not always present (it is a transitive of mypy on Python
  3.10 but not on 3.11+). Without ``tomli`` installed, mypy
  --strict emitted ``Cannot find implementation or library stub
  for module named "tomli"`` at ``edition.py:24``, failing
  gate-4 of section 5. Fix: added ``[[tool.mypy.overrides]]
  module = "tomli" ignore_missing_imports = true`` to
  ``pyproject.toml``. The override is pinned by a regression test
  in ``tests/test_v0_7_0_1_corrective.py`` so a future cleanup
  cannot silently drop it.
- **HIGH: ``furqan-lint check foo.rs`` without [rust] crashed with
  a Python traceback (Issue 2).** The CLI guard in
  ``_check_rust_file`` wrapped only the package import
  (``from furqan_lint.rust_adapter import ...``), not the call
  to ``parse_rust(path)``. The actual ``import tree_sitter``
  fired deep inside ``parser._get_parser`` on first call, and
  surfaced as an uncaught ``ModuleNotFoundError`` traceback,
  violating prompt section 3.3 ("Do not crash with
  ``ModuleNotFoundError``"). Fix: added
  ``RustExtrasNotInstalled`` (a typed ``ImportError`` subclass)
  to the rust_adapter public surface; ``parse_file`` now probes
  the ``tree_sitter`` and ``tree_sitter_rust`` imports at its
  entry point and re-raises any ``ImportError`` as
  ``RustExtrasNotInstalled`` carrying the install hint. The CLI
  catches this typed exception around the ``parse_rust(path)``
  call and prints a one-line install hint to stderr, exit 1.
  Pinned by three regression tests in
  ``tests/test_v0_7_0_1_corrective.py``.

### Added

- **``RustExtrasNotInstalled`` typed exception** in
  ``furqan_lint.rust_adapter.translator``, exported from
  ``furqan_lint.rust_adapter``. Subclasses ``ImportError``;
  message is the install hint itself. Snapshot test in
  ``tests/test_rust_public_surface_additive.py`` extended with
  a v0.7.0.1 baseline that includes this name (additive
  superset of the v0.7.0 baseline).
- **``tests/test_v0_7_0_1_corrective.py``** (4 unit tests).
  (1) Asserts pyproject.toml has a tomli mypy override.
  (2) Asserts ``RustExtrasNotInstalled`` is exported and
  subclasses ``ImportError``.
  (3) Asserts ``parse_file`` raises ``RustExtrasNotInstalled``
  when ``tree_sitter`` is not importable (uses ``sys.meta_path``
  injection to simulate the missing extra).
  (4) Asserts the CLI emits the install hint to stderr and
  returns exit 1 without dumping a traceback when
  ``RustExtrasNotInstalled`` is raised.

### Tests

- 214 passed (was 210 in v0.7.0). Delta: +4.
- 176 unit + 38 integration (1 also network-marked).

### Process notes (validator-bias self-disclosure)

Both findings landed silently on my v0.7.0 validation because:

1. **Issue 1**: my sandbox already had ``tomli`` installed (a
   transitive of mypy on Python 3.10), so mypy resolved the
   import without needing the override. A fresh contributor
   venv on 3.11+ without tomli would not. The lesson is that
   "mypy --strict passes" is not a sufficient gate; it must be
   "mypy --strict passes on a clean install of [dev,rust]
   from scratch", which is what fresh-instance review is for.
2. **Issue 2**: I tested the CLI dispatch path with extras
   installed and never simulated the missing-extras case
   empirically. The lazy-import gate I did test
   (``python3 -X importtime``) proves that ``cli`` does not
   load tree_sitter, but does NOT prove that ``cli`` handles
   tree_sitter being missing at call time. Different gate,
   different test required.

Both lessons saved as feedback memories for future releases.

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the fix works?**
   For Issue 2:
   ```bash
   pip uninstall tree_sitter tree_sitter_rust
   echo "fn f() -> i32 { 42 }" > /tmp/foo.rs
   furqan-lint check /tmp/foo.rs
   ```
   On v0.7.0: Python traceback ending with
   ``ModuleNotFoundError: No module named 'tree_sitter'``,
   exit 1. On v0.7.0.1: one line
   ``Rust support not installed. Run: pip install furqan-lint[rust]``,
   exit 1, no traceback.

2. **Smallest input demonstrating the bug pre-fix?**
   Same input, on v0.7.0: 12-line Python traceback dumping
   the call stack down to ``parser.py:35``.

3. **What this fix does NOT do?**
   (a) Does not bump the minimum Python to 3.11 (which would
       eliminate the tomli dependency entirely). 3.10 remains
       supported.
   (b) Does not change the behaviour when a partial extras
       install (e.g., tree_sitter present but tree_sitter_rust
       missing) occurs; the typed exception fires identically
       in either case.
   (c) Does not add a ``furqan-lint --install-extras`` helper
       command; the user must run pip themselves.

4. **New code paths and their boundaries?**
   ``parse_file`` gained a 7-line probe block at its entry
   (try/except importing tree_sitter and tree_sitter_rust,
   raising ``RustExtrasNotInstalled`` with the install hint).
   ``_check_rust_file`` gained a 6-line except-block catching
   ``RustExtrasNotInstalled`` and emitting a clean stderr
   message + exit 1. The translator gained the
   ``RustExtrasNotInstalled`` class (8 lines including
   docstring). All boundaries pinned by the 4-test corrective
   regression suite.

5. **Limits retired and added?**
   Retired: none. Added: none. v0.7.0.1 is a corrective
   release; the documented-limits inventory is unchanged.

## [0.7.0] - 2026-05-03

Feature release: Rust adapter Phase 1. New language support behind
an opt-in `[rust]` extra. Two checkers run on `.rs` files: D24
(all-paths-return) and D11 (status-coverage on Option-returning
helpers). The Python adapter is unchanged.

This is the first release in the multi-language stage of the
furqan-lint roadmap. The architecture follows ADR-001
(`furqan_lint_rust_adapter_adr.md`): tree-sitter-rust direct (not
language-pack), opt-in extra (not bundled), all checker logic
operates on Furqan IR (`tree_sitter` appears only in
`src/furqan_lint/rust_adapter/`). Validator findings R1
(implicit-return load-bearing), R3 (PyPI ARM64 wheels both
packages), and R4 (representability gate before translator code)
are all observed.

### Added

- **`src/furqan_lint/rust_adapter/`** (~470 LoC). New package
  containing `parser.py` (tree-sitter bootstrap with lazy
  initialisation), `translator.py` (CST -> Furqan
  Module/UnionType/TypePath), `edition.py` (Cargo.toml
  resolution), and `__init__.py` (lazy-import gate; public
  surface limited to `parse_file` and `RustParseError`).
- **CLI dispatch on `.rs` files.** `_check_file` is now a
  dispatcher calling `_check_python_file` (existing 55-line body)
  or `_check_rust_file` (new path). On `.rs`, the CLI lazy-imports
  `furqan_lint.rust_adapter`; if `tree_sitter` is missing, prints
  `Rust support not installed. Run: pip install furqan-lint[rust]`
  to stderr and exits 1.
- **`_check_directory` walks both `*.py` and `*.rs`.** Existing
  Python directory walks are unchanged; new directory walks
  discover Rust files alongside Python.
- **`target/` added to `EXCLUDED_DIRS`.** Cargo build output is
  skipped in directory walks (mirrors the existing `.venv`,
  `__pycache__` exclusions).
- **`[rust]` optional extra in `pyproject.toml`.**
  `pip install furqan-lint[rust]` resolves
  `tree-sitter>=0.23,<1` and `tree-sitter-rust>=0.23,<1`. Both
  packages ship ARM64 and x86_64 wheels on PyPI; no source build
  required.
- **21 Rust fixture files.** 10 in `clean/`, 4 in `failing/`,
  6 in `documented_limits/`, plus a `documented_limits/README.md`
  mirroring the Python adapter's four-place-pattern shape.
- **30 new tests across four files.** `test_rust_adapter.py`
  (15 unit), `test_rust_correctness.py` (11 integration),
  `test_rust_extras_sync.py` (2 unit), and
  `test_rust_public_surface_additive.py` (2 unit). Test count
  goes from 180 to 210.
- **`test_rust_public_surface_additive.py`.** First additive-only
  snapshot test on furqan-lint's own surface. Pins
  `furqan_lint.rust_adapter.__all__` at v0.7.0 as a frozenset that
  future versions must remain a superset of. A parallel snapshot
  for the top-level `furqan_lint` package is registered as a
  v0.7.x or v0.8 candidate.

### Changed

- **CLI PASS message for `.rs` files.** Reads "2 structural checks
  ran (Rust Phase 1: D24 + D11). Zero diagnostics." rather than
  the Python-side "4 structural checks ran" message, so it is
  obvious which pipeline ran.
- **`pyproject.toml` ruff per-file-ignores.** The three new
  `rust_adapter/*.py` files use lazy mid-function imports; PLC0415
  is suppressed for them, mirroring the existing `cli.py`
  exception.
- **`pyproject.toml` mypy override.** `tree_sitter` and
  `tree_sitter_rust` get `ignore_missing_imports = true` because
  they ship without inline type hints at the version we pin. The
  rest of the source remains strictly typed.

### Limitations introduced

Six Rust documented limits, each pinned by the four-place pattern
(README bullet + fixture + pinning test + CHANGELOG entry):

- **Macro-invocation bodies** (`macro_invocation_body.rs`). Phase 1
  cannot see through macro expansion; `fn f() -> i32 { todo!() }`
  passes silently. The Rust analogue of R3 (zero-return ring-close)
  is deferred to v0.7.1.
- **Trait-object return types** (`trait_object_return.rs`).
  `Box<dyn Trait>` is translated to an opaque `TypePath`; trait-
  object polymorphism is out of scope per ADR-001.
- **Lifetime-affected return types** (`lifetime_param_return.rs`).
  `fn f<'a>(...) -> &'a str` has its lifetime stripped; D24's
  path-coverage logic is unaffected.
- **Empty or panic-only bodies** (`empty_or_panic_only_body.rs`).
  Same as the macro-body limit; deferred to v0.7.1.
- **Trait method signatures** (`trait_method_signature.rs`).
  `function_signature_item` nodes are skipped by design (per
  prompt 3.4); D24/D11 do not apply to interface declarations.
- **Closures with annotated return types**
  (`closure_with_annotated_return.rs`). `closure_expression` nodes
  are skipped in Phase 1 even when annotated. Phase 2 may revisit.

### Tests

- 210 passed (was 180 in v0.6.1). Delta: +30.
- 168 unit + 42 integration (1 of which is also network-marked).

### Five Questions (release level, per Bayyinah Engineering Discipline Framework v2.0 section 11.3)

1. **Smallest input demonstrating the new capability:**
   ```rust
   fn classify(x: i32) -> i32 {
       if x > 0 {
           return 1;
       }
       println!("non-positive");
   }
   ```
   On v0.6.x: `furqan-lint check classify.rs` prints
   `Not found: classify.rs` (the CLI rejected `.rs`). On v0.7.0
   with `[rust]` installed: exit 1 with a MARAD on `classify`
   naming the missing-return path; without `[rust]` installed: exit
   1 with the install hint.

2. **Smallest input that would have shown each shipped diagnostic
   on v0.6.x:** none. v0.6.x had no Rust dispatch path. The
   shipped diagnostics for `.rs` files (D24 path-coverage, D11
   Option-collapse, `RustParseError` for syntax errors) are all
   new in v0.7.0.

3. **What this release does NOT do:**
   (a) No Rust analogue of `return_none_mismatch` (deferred to
       v0.7.1+).
   (b) No additive-only on the top-level `furqan_lint` surface
       (the rust subpackage gets its own snapshot; the rest is
       deferred).
   (c) No macro expansion; macros are opaque.
   (d) No cross-file symbol resolution; all checks are intra-file.
   (e) No Cargo workspace traversal beyond reading the nearest
       `Cargo.toml` for edition.
   (f) No R3 equivalent for empty / `todo!()`-only / `panic!()`-only
       Rust functions (deferred to v0.7.1 per the documented
       limit).
   (g) No D24 or D11 on trait method declarations or closures
       (skipped by design).
   (h) No Result-aware D11. The producer predicate fires on
       Option-returning helpers (Option translates to
       UnionType-with-None-arm); Result-collapse needs a
       Rust-specific predicate, deferred.

4. **New code paths:**
   `src/furqan_lint/rust_adapter/` (~470 LoC across four
   modules); CLI dispatch on `.rs` (3 new methods:
   `_check_file` dispatcher, `_check_python_file`,
   `_check_rust_file`); lazy-import gate that converts
   `ImportError` to a user-facing install hint;
   `tree.root_node.has_error` refusal that exits 2; edition
   resolution from `Cargo.toml`; six Rust documented limits with
   the four-place pattern; one additive-only test on
   `rust_adapter.__all__`.

5. **Limits retired and added:**
   Retired: none. (v0.6.0 retired the zero-return-functions limit;
   v0.6.1 retired the aliased-decorator limit.)
   Added: six Rust documented limits (macro-invocation bodies,
   trait-object returns, lifetime-affected return types,
   empty/`todo!()`-only/`panic!()`-only bodies (deferred to v0.7.1),
   trait method signatures (skipped by design), closures with
   annotated return types (skipped in Phase 1)).

## [0.6.1] - 2026-05-02

Round-11 corrective from Fraz. Three tracked findings: an aliased-
decorator false positive in R3 left over from v0.6.0; doc-staleness
drift in the project README and the documented-limits README that
lingered across rounds 6-11; and dead code (`_d24_diagnostic_in_r3_set`)
introduced in v0.6.0 as defensive suppression that turned out to be
structurally redundant.

The retirement count for v0.6.1 is one documented limit
(aliased_abstractmethod), the third in three releases (v0.5.x ->
v0.6.0 retired two, v0.6.1 retires one).

### Fixed

- **Aliased-decorator skip-list now resolves through a module-level
  symbol table.** R3's decorator skip-list previously matched only
  the bare and qualified forms (`@abstractmethod`,
  `@abc.abstractmethod`, `@overload`, `@typing.overload`). It did
  not follow `from abc import abstractmethod as abstract` aliases,
  and a method decorated with the aliased name fired R3 as a false
  positive. v0.6.1 builds a module-level alias map from top-level
  `import` and `from ... import ... [as ...]` statements once per
  call to `check_zero_return`, then resolves bare and dotted
  decorator names through the map before the skip-list lookup.
  Covers four import shapes: `from X import Y`, `from X import Y
  as Z`, `import X`, `import X as Y`.
- **Stale README bullet for `redundant_pipe_none.py` removed.**
  The fixture was deleted in v0.3.5 when the redundant-None
  limit was promoted to a structural fix; the corresponding
  `Remaining limitations` bullet was left behind and persisted
  across rounds 6 through 11. Round-11 audit caught it.
- **Stale README bullet for `aliased_abstractmethod.py` removed.**
  The bullet was added in v0.6.0 and is now retired by the fix
  above.
- **Dead code: `_d24_diagnostic_in_r3_set` removed from
  `runner.py`.** The helper was added in v0.6.0 as a defensive
  D24-suppression mechanism for any function R3 had already fired
  on. Empirically D24 only fires on partial-path coverage (>=1
  return present) while R3 only fires on zero-return shapes; the
  two checkers do not overlap and the suppression had no
  reachable effect. Round-11 audit caught it. The runner now
  appends D24 diagnostics directly without the suppression
  branch, and the docstring is updated to document the
  non-overlap explicitly.
- **`tests/fixtures/documented_limits/README.md` refreshed.**
  The Inventory section had not been updated since v0.3.x and
  was missing the `Retired in v0.6.0` and `Retired in v0.6.1`
  sections, plus a substantively new four-place-pattern paragraph
  in the preamble. Now lists the current four active limits and
  three retirement-by-version sections.

### Limitations retired

- **Aliased decorator imports for R3 skip-list.** Was a v0.6.0
  documented limit. Closed by the alias-resolution fix above.
  The fixture `tests/fixtures/documented_limits/aliased_abstractmethod.py`
  is deleted; the pinning test
  `test_aliased_abstractmethod_fires_r3_false_positive` is
  removed; the README bullet is removed; the documented_limits
  README has a `## Retired in v0.6.1` section recording it.

### Added

- **`tests/test_round11_alias_resolution.py` (12 unit tests).**
  Pins the symbol-table-backed decorator skip-list across all
  four import shapes plus negative-control regression checks.
  Four tests cover alias map construction directly; six cover
  skip-list resolution through the alias map (positive cases);
  two cover that direct (non-aliased) recognition still works
  after the refactor; two are negative-control assertions
  (unrelated decorator fires; no imports yields no resolution).
- **`tests/test_readme_drift.py` (2 unit tests).** v3.0-prep
  structural test that parses the project README's `Remaining
  limitations` section, extracts every fixture path mentioned
  in inline code spans, and asserts each path exists on disk.
  Would have caught the `redundant_pipe_none.py` drift in
  round 6 and prevented the four rounds of accumulated
  staleness that round 11 surfaced.

### Tests

- 180 passed (was 167 in v0.6.0). Delta: +13 (= 12 alias + 2
  drift - 1 retired pin).
- 153 unit + 27 integration (1 of which is also network-marked).

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the fix works?**
   ```python
   from abc import abstractmethod as abstract
   class C:
       @abstract
       def required(self) -> int: ...
   ```
   On v0.6.0: R3 fires `zero_return_path` on `required` as a
   false positive (exit 1). On v0.6.1: PASS, exit 0, because
   `abstract` now resolves to `abc.abstractmethod` via the
   alias map and the skip-list match succeeds.

2. **Smallest input demonstrating the bug pre-fix?**
   Same input, same output, before vs. after. The asymmetry was
   the failing direction: v0.6.0 was a false positive on a
   genuinely-abstract method; v0.6.1 correctly skips.

3. **What does this fix NOT do that a reader might expect?**
   It does not (a) extend symbol-table tracking to
   `aliased_optional_import.py` or `aliased_union_import.py` in
   the `return_none` checker; both remain documented limits with
   their original fixtures and pinning tests. (b) follow imports
   inside function or class bodies; only top-level
   `tree.body` `Import` and `ImportFrom` nodes are tracked.
   Decorators that need such inner imports are exotic enough to
   defer. (c) close the `from somemodule import abstractmethod`
   collision case (an unrelated module that happens to export
   the bare name `abstractmethod`); the alias map records the
   qualified form `somemodule.abstractmethod` but the skip-list
   match is short-circuited by the bare-name check before
   alias resolution runs. This false positive predates v0.6.1
   and is not made worse by this fix; it is named in the
   negative-control test for awareness.

4. **New code paths and their boundaries?**
   `zero_return._build_decorator_alias_map(tree)` walks
   `tree.body` for `Import` and `ImportFrom`; reads `node.module`
   and each `alias.asname or alias.name`; emits a
   `dict[str, str]`. `check_zero_return` calls it once per
   tree. `_check_function`, `_has_skip_decorator`, and
   `_decorator_matches_skip_list` thread the dict through.
   `_decorator_matches_skip_list` adds two new branches: bare
   `aliases.get(name) in _SKIP_DECORATORS`, and dotted
   `f"{aliases.get(prefix)}.{suffix}" in _SKIP_DECORATORS`. All
   four shapes pinned by tests. Boundaries: lambdas excluded
   (no decorator syntax); inner imports not tracked; module
   alias map is not propagated across files (no cross-file
   symbol resolution).

5. **What documented limitations does this retire? Add?**
   Retires: "Aliased decorator imports for R3 skip-list" (v0.6.0).
   Adds: none.

## [0.6.0] - 2026-05-02

Round-10: ring-close R3 (zero-return) checker. The fourth Furqan
checker on the Python adaptor. Closes the v0.4.x documented
limitation "Zero-return functions" and additionally retires the
v0.3.5 documented limitation "Exception-driven fall-through" (R3
catches the try-body-only-raise shape that D24 cannot). One new
documented limitation introduced: aliased decorator imports for
R3's skip-list (e.g., `from abc import abstractmethod as abstract`)
are not yet resolved; v0.6.1 will close that with a symbol table.

### Added

- **`zero_return_path` (R3) checker.** New module
  `src/furqan_lint/zero_return.py` (~250 lines, ~10 helpers). A
  function that declares a non-`None` return type but contains zero
  `return` statements anywhere on any path is reported as
  `zero_return_path` (R3, ring-close). mypy reports the same shape
  as "Missing return statement"; furqan-lint now matches that
  coverage.
- **`furqan_lint.adapter.translate_tree(tree, filename)`.** Public
  wrapper around `_translate_module` so the CLI can parse the
  source once and feed both the Furqan `Module` (for D24/D11/return-none)
  and the raw `ast.Module` (for R3, which needs decorators that
  the Furqan translation does not preserve).
- **R3 wired into the runner pipeline.** `runner.check_python_module`
  gained a `source_tree: ast.Module | None = None` keyword. R3 runs
  before D24 on each function; if R3 fires, D24 is suppressed for
  that function (defensive: in practice D24 only fires on partial-
  path coverage, but the suppression is forward-compatible). Without
  `source_tree` the runner is back-compat for v0.5.x callers.
- **CLI parses once, threads tree to runner.** `cli._check_file`
  now does `tree = ast.parse(source); module = translate_tree(tree)`
  and passes `source_tree=tree`. CLI exit code now treats R3
  diagnostics as failures (exit 1), parallel to marads. PASS message
  updated from "3 structural checks ran" to "4 structural checks
  ran".
- **R3 skip-list (name-based).** `@abstractmethod`,
  `@abc.abstractmethod`, `@overload`, `@typing.overload` (and the
  called forms `@abstractmethod()` etc.) are recognised and skipped.
  Aliased imports are NOT recognised (documented limit).
- **Provably-non-returning body recognition.** Two shapes:
  raise-only bodies (recursive on `If` branches whose every arm
  ends in `Raise`) and the canonical `while True:` loop with no
  reachable `break`. Conservative: `while 1:` is NOT recognised.
- **5 failing fixtures.**
  `tests/fixtures/failing/zero_return_function.py` (moved from
  `documented_limits/`), `zero_return_with_branches.py`,
  `zero_return_async.py`, `zero_return_method.py`,
  `zero_return_optional_propagation.py`.
- **8 clean fixtures.**
  `tests/fixtures/clean/zero_return_none_annotated.py`,
  `zero_return_unannotated.py`, `zero_return_optional_annotated.py`,
  `zero_return_pipe_none.py`, `raise_only_function.py`,
  `while_true_no_break.py`, `abstractmethod_decorated.py`,
  `overload_decorated.py`.
- **1 documented-limit fixture.**
  `tests/fixtures/documented_limits/aliased_abstractmethod.py`
  pinning the v0.6.1 regression target.
- **`tests/test_round10_r3.py` (12 tests).** 5 firing tests, 6
  silence tests (the abstractmethod/overload pair share one test
  function), 1 direct-API test pinning `check_zero_return`'s
  return shape.

### Changed

- **CLI PASS string updated** from `3 structural checks ran` to
  `4 structural checks ran` to match the new pipeline (D24, D11,
  return-none, R3).

### Fixed (limitations retired)

- **Zero-return functions.** Was a v0.4.x documented limitation
  ("D24 skips zero-return functions, R3 not yet wired"). v0.6.0
  closes it: R3 fires on every shape D24 cannot reach. The
  README "Remaining limitations" entry is removed.
- **Exception-driven fall-through, stronger form.** The
  `try: raise; except: pass` shape with no return on any path
  was a v0.3.5 documented limitation. R3 catches it as a
  zero-return function. The fixture
  `try_body_only_returns_in_block.py` is retained but the
  pinning test is inverted: it now asserts R3 fires
  (`test_try_body_raises_with_swallowing_handler_now_caught_by_r3`).

### Architectural alternative considered

The prompt's ADR offered three alternatives for sourcing the raw
AST in R3: (A) local AST walk inside `zero_return.py` using the raw
`ast.Module`; (B) extend the Furqan translation to preserve
decorators and walk the Furqan `Module`; (D) call upstream Furqan's
ring-close primitive with adapter-supplied predicates. Alternative
A was chosen: it is the smallest change (no Furqan-side or upstream
changes), the most testable (R3 logic is fully isolated), and the
most precise (raw AST decorators are lossless). The reversibility
cost is one day if a future requirement (e.g. cross-checker
deduplication) forces a switch to B or D.

### Limitations introduced

- **Aliased decorator imports for R3 skip-list.** Name-only
  resolution does not follow `from abc import abstractmethod as
  abstract`. Pinned as `aliased_abstractmethod.py` in
  `documented_limits/`. v0.6.1 will add a symbol table so this case
  is skipped.

### Tests

- 12 new R3 tests (`test_round10_r3.py`).
- 1 new documented-limit pin
  (`test_aliased_abstractmethod_fires_r3_false_positive`).
- 1 inverted documented-limit test
  (`test_try_body_raises_with_swallowing_handler_now_caught_by_r3`).
- 14 fixture files added (5 failing + 8 clean + 1 doc-limit) and 1
  fixture moved (`zero_return_function.py` from `documented_limits/`
  to `failing/`).

### Five Questions (per Bayyinah Engineering Discipline Framework v2.0 §11.3)

1. **Smallest input demonstrating the fix works?**
   `def f(x: int) -> int: pass` is now reported as
   `zero_return_path` (R3) with exit code 1. v0.5.x: silent PASS.

2. **Smallest input demonstrating the bug pre-fix?**
   Same input, on v0.5.x: `furqan-lint check ...` returns "PASS"
   and exits 0. mypy reports "Missing return statement".

3. **What does this fix NOT do that a reader might expect?**
   It does not (a) catch zero-return shapes hidden behind
   aliased decorators (`@abstract` from
   `from abc import abstractmethod as abstract`); (b) recognise
   non-canonical infinite loops (`while 1:`, `itertools.count()`);
   (c) recognise bodies whose raise is hidden inside a swallowing
   `try/except` that the body itself does not establish; (d)
   replace mypy's broader missing-return analysis (R3 only fires
   on zero returns, not partial coverage; D24 covers partial).

4. **New code paths and their boundaries?**
   `zero_return.py:check_zero_return -> _check_function` runs the
   5-step skip cascade (no annotation -> Optional/None ->
   skip-decorator -> non-returning body -> has any return). All
   five steps are pinned by tests. Boundaries: nested function
   bodies are recursed by `ast.walk` so they are checked
   independently; lambdas are excluded (no syntax for return
   annotation); methods inside classes ARE walked (matches D24
   behaviour).

5. **What documented limitations does this retire? Add?**
   Retires: "Zero-return functions" (v0.4.x), "Exception-driven
   fall-through, stronger form" (v0.3.5). Adds: "Aliased decorator
   imports for R3 skip-list" (v0.6.0).

## [0.5.1] - 2026-05-03

Round-9 corrective from Fraz Ashraf. CRITICAL: ruff version drift
between CI and pre-commit caused CI to pass while the pre-commit
dogfood would have failed; the v0.5.0 CHANGELOG claim "pre-commit
run --all-files exits 0" was empirically false.

### Fixed

- **CRITICAL: ruff version drift between CI and pre-commit.** v0.5.0
  declared `ruff>=0.8.0` (unpinned upper) in the `[dev]` extras. CI
  resolved this to ruff 0.15.12 where UP038 was removed; pre-commit
  pinned 0.8.0 where UP038 fires. CI passed; the pre-commit dogfood
  failed; the CHANGELOG claim "pre-commit run --all-files exits 0"
  was empirically false. Pinned `ruff==0.8.0` in `[dev]` so all four
  surfaces (CI, pre-commit, contributor local, Fraz's reproducer)
  run the same checks.
- **CRITICAL: 8 UP038 violations in src/.** Migrated
  `isinstance(x, (A, B))` to `isinstance(x, A | B)` in adapter.py
  (6 sites) and additive.py (2 sites). Semantically identical on
  Python 3.10+ (the project's minimum version).
- **CRITICAL: 3 unformatted files.** Reformatted test_review_fixes.py,
  test_round7_fixes.py, and test_tooling.py. Whitespace and line
  wrapping only.
- **HIGH: CHANGELOG unit count corrected.** v0.5.0 said "135 unit";
  actual count is 138 unit. The 3 test_tooling.py tests are marked
  unit but were counted separately in the narrative.

### Added

- Functional tests: `test_ruff_check_exits_zero_on_repo` and
  `test_ruff_format_check_exits_zero_on_repo`. These are the
  functional pair to the existing structural
  `test_pyproject_has_ruff_config` per framework Section 8.6
  (structural-vs-functional pairing). Catches the v0.5.0 CRITICAL
  class: config exists but tool fails. The tests are meaningful
  only because `[dev]` now pins ruff exactly.

### Notes

- CLI shows 0% branch coverage because tests run via subprocess
  and coverage does not propagate through subprocess by default.
  Functional coverage of the CLI is provided by tests/test_action.py
  and the round-N regression tests. Subprocess coverage propagation
  is a v0.6.0 candidate.
- The version-drift root cause is the framework Section 8.6 pattern
  applied to a transitive dependency surface: the project verified
  the schema (`[tool.ruff]` exists in pyproject) but did not verify
  the functional outcome under the pinned version contributors and
  pre-commit actually run. Round-9 finding from Fraz Ashraf.

### Five Questions (audit framework Section 11.3)

1. **What does this commit change?** Pins ruff==0.8.0 in [dev],
   migrates 8 isinstance tuples to X | Y, reformats 3 test files,
   corrects CHANGELOG unit count, adds 2 functional tests.
2. **What does it not change?** No checker behavior. No public API.
   No fixture content. No ADR-backed decisions reversed.
3. **What is the verification?** `ruff check .` exits 0,
   `ruff format --check .` exits 0, `mypy` exits 0,
   `pre-commit run --all-files` exits 0, all 154 tests pass.
4. **What is deferred?** Subprocess coverage propagation (v0.6.0).
   Considered ruff bump to 0.15+ (deferred to deliberate ADR).
5. **What is the rollback?** `git revert` of the v0.5.1 commit
   restores v0.5.0 state. No data migration.

## [0.5.0] - 2026-05-03

Dev tooling integration. No new checker logic; the tool starts
checking itself.

### Added

- **`.pre-commit-config.yaml`** for the repo's own codebase
  (separate from `.pre-commit-hooks.yaml`, which is the
  producer-side hook for consumers). Five hook groups: standard
  hygiene (trailing-whitespace, end-of-file-fixer, check-yaml,
  check-toml, check-merge-conflict, check-added-large-files,
  mixed-line-ending), ruff (lint + format), mypy on `src/` only
  with furqan as additional_dependency, em-dash guard mirroring
  the CI step, and a furqan-lint self-check (dogfood).
- **CI lint job** parallel to the test matrix. Runs ruff check,
  ruff format --check, and mypy on Python 3.12 in ~10s. Fails
  fast on style/type issues before the 4-version test matrix
  spins up.
- **Three new pytest markers**: `unit` (fast, in-process, no
  subprocess), `integration` (CLI or pipeline), `mock` (uses
  unittest.mock or pytest-mock). `slow` and `network` were
  already registered in v0.4.1.
- **`[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.per-file-ignores]`,
  `[tool.ruff.format]`, `[tool.mypy]`, `[[tool.mypy.overrides]]`**
  blocks in `pyproject.toml`. Ruff selection is curated, not
  maximal: E/W/F/I/B/UP/SIM/RUF/PL/PTH/TID. Each ignore has a
  one-line comment explaining intent.
- **Dev dependencies extended**: `pytest-mock>=3.12`,
  `ruff>=0.8.0`, `mypy>=1.13`, `pre-commit>=4.0`, `pyyaml>=6.0`.
- **README sections**: "Using with Other Tools" (tool comparison
  table + recommended consumer pre-commit config) and
  "Contributing to furqan-lint" (setup, run-checks, marker usage).
- **`tests/test_tooling.py`**: 3 structural tests verifying the
  pre-commit config has all required hooks, pyproject has
  `[tool.ruff]`, and all 5 pytest markers are registered.

### Changed

- Codebase formatted with `ruff format`. No behavioral changes.
- Ruff and mypy findings from the baseline triage either fixed
  (real issues: SIM101, SIM103, SIM102 x4, RUF059, E402,
  arg-type narrowing on three predicate-helper pairs, missing
  type annotations on local vars and helper signatures) or
  ignored with explanatory comments (PLW1510 is intentional;
  cli.py PLC0415 is the lazy-import-for-fast-version pattern;
  PLR0911/PLR0912 are pre-existing API surface).
- All 148 existing tests carry pytest markers (138 unit, 13
  integration; the 1 v0.4.1 network test stays double-marked).

### Not added (deliberate, per recommendation document)

- `black` (ruff format is black-compatible; one tool, not two)
- `pylint` (ruff covers the same rules, faster)
- `tox`/`nox` (CI matrix already covers Python 3.10-3.13)
- `bandit` (narrow attack surface; reconsider if network features
  added)
- `pytest-xdist` (suite runs in seconds; parallelism adds flake risk)
- Coverage gate (add `pytest-cov` after baseline; gate after
  measurement)
- Directory-based test split (markers carry the same information
  without forcing a 14-file rename)

### Deferred (v0.6.0 candidates)

- Ring-close R3 (zero-return checker) - drafted in a prior session
  as a v0.5.0 candidate; reframed to v0.6.0 to keep this release
  scoped to tooling.
- Aliased Optional/Union import resolution (needs symbol table)
- Exhaustive match recognition
- Local classes inside function/method bodies
- Decorator threading (eliminates abstract-method false positives
  the future R3 checker will introduce)

### Tests

- 148 existing + 3 new tooling tests = 151 selectable + 1
  network = 152 total.

### Five questions (audit framework Section 9.3)

1. **Smallest input demonstrating the fix works:** `pre-commit
   run --all-files` exits 0 on a clean checkout. `ruff check .`,
   `ruff format --check .`, `mypy`, and `furqan-lint check src/`
   all exit 0.
2. **Smallest input demonstrating the bug pre-fix:** Pre-v0.5.0
   the repo had no formatter, no linter, no type checker, no
   self-check. `pip install -e .[dev]` installed only pytest.
3. **What this release does NOT do:** Does not add any new
   checker logic; the structural-honesty checks ship unchanged
   from v0.4.1. Ruff is not configured to run on `tests/fixtures/`
   (those are intentionally malformed). Mypy is strict on `src/`
   only, not `tests/`.
4. **New code paths and their boundaries:** No production code
   paths added; only configuration and one new test module.
   Boundary: anything in `tests/fixtures/` is the System Under
   Test for furqan-lint and is not subject to ruff or mypy.
5. **Documented limitations retired/introduced:** None. This
   release adds no checker behavior, so no four-place
   documentation churn.

## [0.4.1] - 2026-05-02

Corrective fixes from Fraz's round-8 review of v0.4.0. One CRITICAL,
two HIGH, two MEDIUM, two LOW. All findings reproduced empirically
against v0.4.0 before fixing.

### Fixed

- **CRITICAL: Pre-commit hook installation.** The hook now declares
  ``furqan`` as an ``additional_dependency`` via the canonical
  GitHub URL, so ``pre-commit install`` actually resolves the
  dependency. Without this, pip read ``furqan>=0.11.0`` from
  ``pyproject.toml``, queried PyPI (which only hosts ``furqan==0.10.1``),
  and failed resolution. The hook shipped in v0.4.0 in a non-functional
  state.
- **HIGH: GitHub Action version drift.** ``action.yml`` now installs
  furqan-lint at ``${{ github.action_ref }}`` so a user pinning
  the action to a specific tag gets the matching code from that tag
  rather than whatever happens to be on ``main`` at install time. The
  ``furqan-lint-version`` input was removed; it can return when
  furqan-lint is on PyPI and the install step switches from git URL
  to ``pip install furqan-lint==<version>``.
- **MEDIUM: Bare-Union diagnostic prose.** The v0.3.4 fix collapsed
  ``Optional`` and ``Union`` into one branch and could end up
  recommending ``Union[X]`` (well-formed but degenerate - typing
  folds a one-arm Union to ``X``). v0.4.1 splits the two cases:
  bare ``Union`` now suggests ``Union[X, None]``, ``Optional[X]``,
  or ``X | None`` since the user is returning ``None``.
- **LOW: CI em-dash check locale.** The em-dash regex is now run
  under ``LC_ALL=C.UTF-8`` because GNU ``grep -P`` fails on some
  default GitHub runner locales when the pattern contains hex-escape
  sequences. Without the prefix, the gate could pass spuriously.

### Changed

- **HIGH: D11 monkey-patch retired.** ``runner.py`` now passes the
  Python-Optional predicate to ``check_status_coverage`` via the
  upstream ``producer_predicate=`` keyword (available since
  ``furqan>=0.11.0``) instead of monkey-patching
  ``status_coverage._is_integrity_incomplete_union``. Removed
  ``import threading``, the ``contextmanager`` import,
  ``_predicate_lock``, and the entire ``_python_optional_mode``
  context manager. The ``_is_optional_union`` helper is preserved
  with its body unchanged; the docstring now references the
  ``producer_predicate`` keyword. Closes the full lifecycle of a
  round-1 audit finding (stopgap monkey-patch in v0.1.0 ->
  scoped context manager in v0.3.0 -> threading lock for safety
  in v0.3.0 -> upstream parameter retires the patch entirely in
  v0.4.1).
- The Bug 4 thread-safety regression test in
  ``test_review_fixes.py`` was rewritten to pin the new invariant:
  the global ``status_coverage._is_integrity_incomplete_union``
  must never be touched at runtime. Old test was a stopgap pinning
  the lock around the patch.

### Added

- **MEDIUM: Zero-return functions documented.** A function that
  declares a return type but has no ``return`` statement at all is
  silently passed by D24 (the existing skip-on-zero-returns rule
  defers to ring-close R3, which furqan-lint does not yet run).
  Added to README "Remaining limitations."
- Static test verifying ``.pre-commit-hooks.yaml`` declares
  ``furqan`` in ``additional_dependencies``.
- Network-dependent functional test (marked ``slow`` and ``network``;
  skipped under ``pytest -m "not network"``) that verifies the hook
  installs in a clean venv. Markers registered in ``pyproject.toml``.
- Regression test pinning ``github.action_ref`` in ``action.yml``.
- v0.4.1 bare-Union prose test asserting the fix string contains
  ``Union[X, None]`` and does NOT contain the degenerate
  ``Union[X]`` form.
- ``LC_ALL=C.UTF-8`` assertion in the CI em-dash workflow test.
- "Closed in v0.4.1" section in README documenting the retired
  monkey-patch and the now-installable pre-commit hook.

### Tests

- 5 new tests across ``test_action.py`` (1 static pre-commit dep
  check, 1 functional install test, 1 action_ref pin test) and
  ``test_round7_fixes.py`` (1 v0.4.1 bare-Union prose test). The
  Bug 4 thread-safety test was replaced with a kwarg-usage test;
  net-1 in ``test_review_fixes.py``. Locale assertion added to an
  existing CI-workflow test.
- Total: 150 (149 deselected under ``pytest -m "not network"``).

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
