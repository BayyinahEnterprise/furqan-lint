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
    assert "Rust Phase 2: R3 + D24 + D11" in result.stdout


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
def test_macro_invocation_body_is_silent_pass() -> None:
    """Phase 1 cannot see through macro expansion; a function whose
    body is a macro invocation passes silently. The Rust analogue
    of R3 is deferred to v0.7.1; this test pins the current limit
    so a future fix transitions intentionally."""
    result = _run_check("documented_limits/macro_invocation_body.rs")
    assert result.returncode == 0
    assert "PASS" in result.stdout


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
    """Documented limit (v0.7.1): ``panic!()`` (no semicolon) used
    as a tail expression does NOT fire R3 because the translator
    synthesizes a ReturnStmt for any tail expression. Phase 3 may
    revisit if the Rust ecosystem standardizes a #[diverging]
    attribute on macros."""
    result = _run_check("documented_limits/r3_panic_as_tail_expression.rs")
    assert result.returncode == 0
    assert "PASS" in result.stdout
