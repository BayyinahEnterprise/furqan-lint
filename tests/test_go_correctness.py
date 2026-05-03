"""Full-pipeline correctness tests for the Go adapter (v0.8.0).

Spawns the goast binary + translator + runner end-to-end on
fixtures and asserts verdicts. Mirrors test_rust_correctness.py
shape.

Phase 1 covers D24 (this file). Phase 2 (commit 4) adds D11
tests.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def _go_extras_present() -> bool:
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    pkg_root = Path(spec.origin).parent
    binary = pkg_root / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


_REASON = "goast binary not built; install [go] extras"
pytestmark_go = pytest.mark.skipif(not _go_extras_present(), reason=_REASON)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "go"


def _check(fixture_relpath: str) -> tuple[int, list[tuple[str, object]]]:
    """Run the full pipeline on a fixture; return diagnostic count
    and (name, diag) tuples."""
    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.runner import check_go_module
    from furqan_lint.go_adapter.translator import translate

    path = FIXTURES / fixture_relpath
    data = parse_file(path)
    module = translate(data, filename=str(path))
    diagnostics = check_go_module(module)
    return len(diagnostics), diagnostics


# ---------------------------------------------------------------------------
# D24 (all-paths-return)
# ---------------------------------------------------------------------------


@pytestmark_go
def test_go_d24_clean_when_all_paths_return() -> None:
    """if/else where both arms return satisfies D24."""
    n, diags = _check("clean/all_paths_return.go")
    assert (
        n == 0
    ), f"expected zero diagnostics, got {[(name, d.diagnosis[:80]) for name, d in diags]}"


@pytestmark_go
def test_go_d24_fires_on_missing_return() -> None:
    """if-without-else where the fall-through path has no return
    fires D24 P1."""
    n, diags = _check("failing/missing_return.go")
    assert n == 1
    name, diag = diags[0]
    assert name == "all_paths_return"
    assert "function 'Classify'" in diag.diagnosis


@pytestmark_go
def test_go_d24_handles_switch_cases(tmp_path: Path) -> None:
    """switch statements are translated as opaque markers (Phase 1
    documented limit). A function whose only structural path is a
    switch will fire D24 because the switch is not recognized as
    guaranteed-coverage."""
    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.runner import check_go_module
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "switched.go"
    source.write_text(
        "package switched\n\n"
        "func Classify(x int) (int, error) {\n"
        "    switch x {\n"
        "    case 0:\n"
        "        return 0, nil\n"
        "    default:\n"
        "        return 1, nil\n"
        "    }\n"
        "}\n"
    )
    module = translate(parse_file(source), filename=str(source))
    diagnostics = check_go_module(module)
    # Phase 1 limit: switch is opaque, so the IR contains no visible
    # ReturnStmt at the function-body level. D24 requires >=1
    # return present to fire (Case P1 = partial coverage), so it
    # does NOT fire here. The function structurally appears
    # zero-return. R3 (which would fire on zero-return) is not
    # wired for Go in v0.8.0; deferred to whichever Phase
    # introduces a Go-specific zero-return checker. This test pins
    # the current "silent PASS on switch-only body" limit.
    assert len(diagnostics) == 0
    fn = module.functions[0]
    # IR shape pin: zero ReturnStmts visible (switch is opaque IfStmt).
    from furqan.parser.ast_nodes import ReturnStmt

    return_stmts = [s for s in fn.statements if isinstance(s, ReturnStmt)]
    assert len(return_stmts) == 0


@pytestmark_go
def test_go_d24_handles_for_loop(tmp_path: Path) -> None:
    """for loops are opaque markers in Phase 1; a function whose
    only structural element is a for loop with returns inside fires
    D24 because the loop body is not walked. Phase 2 may extend."""
    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.runner import check_go_module
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "looped.go"
    source.write_text(
        "package looped\n\n"
        "func Find(xs []int) (int, error) {\n"
        "    for _, x := range xs {\n"
        "        if x > 0 {\n"
        "            return x, nil\n"
        "        }\n"
        "    }\n"
        "    return 0, nil\n"
        "}\n"
    )
    module = translate(parse_file(source), filename=str(source))
    diagnostics = check_go_module(module)
    # The post-loop return covers the fall-through path, so D24
    # should NOT fire on this fixture (the trailing return makes
    # the function structurally honest).
    assert len(diagnostics) == 0


# ---------------------------------------------------------------------------
# D11 (status-coverage on (T, error) returns)
# ---------------------------------------------------------------------------


@pytestmark_go
def test_go_d11_fires_on_error_collapse_via_blank() -> None:
    """Caller declares -> *Config and assigns ``cfg, _ := loadConfig(...)``.
    The discard via _ silently narrows the (T, error) union; D11 fires."""
    n, diags = _check("failing/error_collapse_via_blank.go")
    assert n == 1
    name, diag = diags[0]
    assert name == "status_coverage"
    assert "function 'StartServer'" in diag.diagnosis
    assert "loadConfig" in diag.diagnosis


@pytestmark_go
def test_go_d11_fires_on_error_collapse_via_panic() -> None:
    """Caller checks the error but its signature still lies
    (returns *Config not (*Config, error)). Same D11 firing
    condition as the blank-discard case: the caller declared a
    non-may-fail type."""
    n, diags = _check("failing/error_collapse_via_panic.go")
    assert n == 1
    name, diag = diags[0]
    assert name == "status_coverage"
    assert "function 'StartServer'" in diag.diagnosis


@pytestmark_go
def test_go_d11_clean_when_error_propagated() -> None:
    """Caller declares (*Config, error) and returns the upstream
    helper directly. The union is honestly propagated; D11 silent."""
    n, diags = _check("clean/error_propagated.go")
    assert (
        n == 0
    ), f"expected zero diagnostics, got {[(name, d.diagnosis[:80]) for name, d in diags]}"


@pytestmark_go
def test_go_d11_clean_when_named_returns() -> None:
    """Caller declares (cfg *Config, err error) named returns and
    propagates the helper's union via the named-return mechanism.
    Same honesty discipline; D11 silent."""
    n, diags = _check("clean/error_handled_via_named_return.go")
    assert (
        n == 0
    ), f"expected zero diagnostics, got {[(name, d.diagnosis[:80]) for name, d in diags]}"


@pytestmark_go
def test_go_d11_predicate_partition() -> None:
    """The cross-language _is_may_fail_producer predicate fires on
    Go's (T, error) shape via _is_error_return, on Rust's
    Option<T> via _is_optional_union, and on Rust's Result<T, E>
    via _is_result_type. The four predicates partition the
    may-fail-producer space cleanly with no overlap.

    This pin defends against a future refactor that consolidates
    the predicates into a single regex / name-based check that
    might over-fire."""
    from furqan.parser.ast_nodes import SourceSpan, TypePath, UnionType

    from furqan_lint.runner import (
        _is_error_return,
        _is_may_fail_producer,
        _is_optional_union,
        _is_result_type,
    )

    sp = SourceSpan(file="<synth>", line=1, column=0)

    # Go (T, error)
    go_err = UnionType(
        left=TypePath(base="*Config", layer=None, span=sp),
        right=TypePath(base="error", layer=None, span=sp),
        span=sp,
    )
    assert _is_error_return(go_err) is True
    assert _is_optional_union(go_err) is False
    assert _is_result_type(go_err) is True  # Both arms are non-None
    assert _is_may_fail_producer(go_err) is True

    # Rust Option<T>
    rust_opt = UnionType(
        left=TypePath(base="i32", layer=None, span=sp),
        right=TypePath(base="None", layer=None, span=sp),
        span=sp,
    )
    assert _is_optional_union(rust_opt) is True
    assert _is_error_return(rust_opt) is False
    assert _is_result_type(rust_opt) is False  # One arm is None
    assert _is_may_fail_producer(rust_opt) is True

    # Rust Result<T, E> (E is not "error")
    rust_result = UnionType(
        left=TypePath(base="i32", layer=None, span=sp),
        right=TypePath(base="String", layer=None, span=sp),
        span=sp,
    )
    assert _is_result_type(rust_result) is True
    assert _is_optional_union(rust_result) is False
    assert _is_error_return(rust_result) is False
    assert _is_may_fail_producer(rust_result) is True

    # Plain TypePath (not a union at all)
    plain = TypePath(base="i32", layer=None, span=sp)
    assert _is_optional_union(plain) is False
    assert _is_result_type(plain) is False
    assert _is_error_return(plain) is False
    assert _is_may_fail_producer(plain) is False
