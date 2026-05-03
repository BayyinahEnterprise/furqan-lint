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
