"""Full-pipeline correctness tests for the Rust adapter (v0.7.0).

10 integration tests: spawn ``furqan-lint check <fixture>`` for
each Rust fixture and assert the verdict (PASS / MARAD with
specific diagnostic / PARSE ERROR). Mirrors the Python adapter's
tests/test_correctness.py shape exactly.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def _rust_extras_present() -> bool:
    try:
        importlib.import_module("tree_sitter")
        importlib.import_module("tree_sitter_rust")
    except ImportError:
        return False
    return True


_REASON = "tree_sitter / tree_sitter_rust not installed"
pytestmark_rust = pytest.mark.skipif(not _rust_extras_present(), reason=_REASON)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "rust"


def _run_check(fixture_relpath: str) -> subprocess.CompletedProcess[str]:
    """Run ``furqan-lint check <fixture>`` and capture stdout."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "furqan_lint.cli",
            "check",
            str(FIXTURES / fixture_relpath),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


# ---------------------------------------------------------------------------
# clean/ fixtures: PASS
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_simple_returning_fn_is_pass() -> None:
    result = _run_check("clean/simple_returning_fn.rs")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    assert "R3, D24, D11" in result.stdout


@pytestmark_rust
def test_implicit_return_block_is_pass() -> None:
    """Validator R1 case: tail expression with no semicolon is a
    valid implicit return; D24 must not fire."""
    result = _run_check("clean/implicit_return_block.rs")
    assert result.returncode == 0, result.stdout
    assert "PASS" in result.stdout


@pytestmark_rust
def test_match_all_arms_return_is_pass() -> None:
    """Match where every arm returns satisfies D24."""
    result = _run_check("clean/match_all_arms_return.rs")
    assert result.returncode == 0, result.stdout
    assert "PASS" in result.stdout


@pytestmark_rust
def test_method_in_impl_block_is_pass() -> None:
    """Methods inside impl blocks are discovered and pass D24."""
    result = _run_check("clean/method_in_impl_block.rs")
    assert result.returncode == 0, result.stdout
    assert "PASS" in result.stdout


@pytestmark_rust
def test_async_fn_returns_result_is_pass() -> None:
    """async fn is treated identically to sync fn for D24/D11."""
    result = _run_check("clean/async_fn_returns_result.rs")
    assert result.returncode == 0, result.stdout
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# failing/ fixtures: MARAD
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_missing_return_path_fires_d24() -> None:
    """if-without-else with a side-effect tail fires D24 P1."""
    result = _run_check("failing/missing_return_path.rs")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "all_paths_return" in result.stdout
    assert "function 'classify'" in result.stdout


@pytestmark_rust
def test_d11_optional_collapse_fires_d11() -> None:
    """Caller silently narrows an Option-returning helper; D11 fires."""
    result = _run_check("failing/d11_optional_collapse.rs")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "status_coverage" in result.stdout
    assert "function 'find_age'" in result.stdout
    assert "i32 | None" in result.stdout


@pytestmark_rust
def test_match_missing_arm_return_fires_d24() -> None:
    """Match where one arm body is side-effect-only fires D24."""
    result = _run_check("failing/match_missing_arm_return.rs")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "function 'route'" in result.stdout


# ---------------------------------------------------------------------------
# documented_limits/ fixtures: pin current behaviour
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_closure_with_annotated_return_is_silent_pass() -> None:
    """closure_expression is skipped in Phase 1 even with explicit
    return-type annotation. The outer function PASSes because the
    closure body is not analysed."""
    result = _run_check("documented_limits/closure_with_annotated_return.rs")
    assert result.returncode == 0
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Phase 2 (v0.7.1): R3 (zero-return) integration tests
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_r3_fires_on_empty_body() -> None:
    """Empty body with non-unit return type fires R3 (zero-return).
    ALSO asserts EXACTLY ONE diagnostic, exercising the R3-D24
    suppression path (without it, both R3 and D24 would fire and
    the assertion would catch two)."""
    result = _run_check("failing/r3_empty_body_returns_T.rs")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout
    assert "1 violation(s)" in result.stdout, (
        f"expected EXACTLY ONE diagnostic (R3 suppresses D24); " f"got:\n{result.stdout}"
    )


@pytestmark_rust
def test_r3_fires_on_panic_with_semicolon() -> None:
    """``panic!();`` body fires R3. Pins exact diagnostic prose +
    the function name + the declared return type per §3.5
    source-fidelity requirement."""
    result = _run_check("failing/r3_panic_only_body.rs")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout
    assert "i32" in result.stdout
    assert "but its body contains no `return` statement" in result.stdout


@pytestmark_rust
def test_r3_fires_on_todo_with_semicolon() -> None:
    """``todo!();`` body fires R3. Same structural pattern as
    panic-with-semi, different macro identity, same verdict."""
    result = _run_check("failing/r3_todo_only_body.rs")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout


@pytestmark_rust
def test_r3_fires_on_unimplemented_with_semicolon() -> None:
    """``unimplemented!();`` body fires R3. Pinned to keep the
    structural rule (not a hardcoded macro list) the load-bearing
    decision point."""
    result = _run_check("failing/r3_unimplemented_only_body.rs")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout


@pytestmark_rust
def test_r3_fires_on_unreachable_with_semicolon() -> None:
    """``unreachable!();`` body fires R3."""
    result = _run_check("failing/r3_unreachable_only_body.rs")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout


@pytestmark_rust
def test_r3_fires_on_unrelated_macro_with_semicolon() -> None:
    """``eprintln!("x");`` body fires R3. Locks the design that
    R3 is grammar-and-macro-agnostic: the structural pattern
    (zero ReturnStmt + non-None return type) is what matters,
    not whether the macro name is panic-like.

    Without this fixture's pinning test, a future contributor
    might add a PANIC_MACROS = {"panic", "todo", ...} allowlist,
    which would narrow the checker incorrectly."""
    result = _run_check("failing/r3_macro_only_body_with_unrelated_macro.rs")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout


@pytestmark_rust
def test_r3_silent_on_panic_as_tail_expression() -> None:
    """Documented limit: ``panic!()`` (no semicolon) used as a
    tail expression does NOT fire R3 because the translator
    synthesizes a ReturnStmt for any tail expression. The
    fixture file pins the panic case as the canonical example;
    test_r3_silent_on_diverging_macros_as_tail_expression below
    parametrizes over the full diverging-macro family (panic,
    todo, unimplemented, unreachable) to lock the structural rule
    that R3 is grammar-and-macro-agnostic."""
    result = _run_check("documented_limits/r3_panic_as_tail_expression.rs")
    assert result.returncode == 0
    assert "PASS" in result.stdout


@pytestmark_rust
@pytest.mark.parametrize(
    "macro_invocation",
    [
        'panic!("never returns")',
        'todo!("not yet implemented")',
        "unimplemented!()",
        "unreachable!()",
    ],
)
def test_r3_silent_on_diverging_macros_as_tail_expression(tmp_path, macro_invocation: str) -> None:
    """Round-17 MEDIUM 4: macro_invocation_body.rs and
    r3_panic_as_tail_expression.rs pinned the same underlying
    limit under different labels. v0.7.3 retired
    macro_invocation_body and consolidated the cases into this
    parametrized test that exercises the full diverging-macro
    family. The structural rule R3 enforces (zero-ReturnStmt +
    annotated return type, where the translator's tail-expression
    synthesis produces statements=1 for the no-semicolon case)
    is macro-identity-agnostic; this test pins that the rule
    silences uniformly across the four canonical diverging
    macros."""
    rust_source = f"fn f() -> i32 {{ {macro_invocation} }}\n"
    fixture = tmp_path / "diverging_macro.rs"
    fixture.write_text(rust_source)
    result = subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(fixture)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"R3 unexpectedly fired on `{macro_invocation}` as tail "
        f"expression. The structural rule should silence uniformly "
        f"across diverging macros, NOT fire on a hardcoded macro "
        f"name allowlist.\nstdout:\n{result.stdout}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Phase 3 (v0.7.2): Result-aware D11
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_d11_fires_on_result_collapse() -> None:
    """A function declaring a concrete return type but calling a
    Result-returning helper without propagating the union must
    fire D11. v0.7.1 D11 only fired on Option-returning helpers;
    v0.7.2 widens the producer predicate to recognise Result
    via _is_result_type."""
    result = _run_check("failing/result_collapse.rs")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "status_coverage" in result.stdout
    assert "function 'parse_age'" in result.stdout
    assert "parse_helper" in result.stdout


@pytestmark_rust
def test_d11_clean_when_result_propagated() -> None:
    """A function that calls a Result-returning helper and
    propagates the union via its own Result return type does NOT
    fire D11. The honesty discipline is satisfied: the may-fail
    contract is preserved up the call stack."""
    result = _run_check("clean/result_propagated.rs")
    assert result.returncode == 0
    assert "PASS" in result.stdout


@pytestmark_rust
def test_result_predicate_does_not_match_option() -> None:
    """_is_result_type must not fire on Option<T>; that is
    _is_optional_union's domain. The two predicates partition
    the may-fail-producer space cleanly."""
    import tempfile
    from pathlib import Path

    from furqan_lint.runner import (
        _is_may_fail_producer,
        _is_optional_union,
        _is_result_type,
    )
    from furqan_lint.rust_adapter import parse_file

    with tempfile.NamedTemporaryFile(suffix=".rs", delete=False) as fp:
        fp.write(b"fn f() -> Option<i32> { Some(0) }\n")
        path = Path(fp.name)
    module = parse_file(path)
    rt = module.functions[0].return_type
    assert _is_optional_union(rt) is True
    assert _is_result_type(rt) is False
    # _is_may_fail_producer fires on either; sanity check the union
    assert _is_may_fail_producer(rt) is True


def test_rust_extract_omits_impl_methods() -> None:
    """v0.8.3 documented limit: extract_public_names omits
    methods inside ``impl Type { ... }`` blocks.

    The extractor walks only top-level CST root children; impl
    methods live one level deeper. Asymmetric with goast as of
    v0.8.2 (which emits qualified method names like
    ``Counter.increment``); Rust impl-method collection is
    registered as a v0.8.4 candidate.

    Pin: ``frozenset({"Counter"})`` only -- the two impl
    methods (``increment``, ``get``) are silently omitted. The
    pin asserts the empirical behavior; a future v0.8.4 change
    that adds impl-method collection MUST flip this assertion
    deliberately, with the matching CHANGELOG ``### Limitations
    retired`` entry.
    """
    if not _rust_extras_present():
        pytest.skip(_REASON)
    from furqan_lint.rust_adapter import extract_public_names

    fixture = FIXTURES / "documented_limits" / "impl_methods_omitted.rs"
    names = extract_public_names(fixture)
    assert names == frozenset({"Counter"}), f"Expected only 'Counter', got: {sorted(names)}"


def test_trait_object_return_documented_limit() -> None:
    """Backfill (v0.8.3): the v0.7.0 fixture
    ``trait_object_return.rs`` had a header comment and a
    documented_limits/README entry but no pinning test. The
    four-place-completeness gate (introduced in v0.8.3 commit
    5) enforces the test-presence requirement; the backfill
    happens here so the gate self-test passes against the
    v0.8.2 substrate.

    Verdict: PASS. The fixture parses cleanly and produces no
    diagnostics; the limit is that the trait-object payload
    is not modeled (a future trait-dispatch checker would
    need to revisit), not that any current checker fires
    on the file.
    """
    result = _run_check("documented_limits/trait_object_return.rs")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_lifetime_param_return_documented_limit() -> None:
    """Backfill (v0.8.3): the v0.7.0 fixture
    ``lifetime_param_return.rs`` had a header comment and a
    documented_limits/README entry but no pinning test. Same
    rationale as test_trait_object_return_documented_limit.

    Verdict: PASS. Lifetimes are stripped during translation;
    D24's path-coverage logic is unaffected.
    """
    result = _run_check("documented_limits/lifetime_param_return.rs")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
