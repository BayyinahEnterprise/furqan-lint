"""Unit tests for the Rust adapter translator (v0.7.0 Phase 1).

13 tests covering: empty / panic-only body skip, if/else / match /
loop translation, implicit-return tail expression detection, ?-op,
Result and Option translation, async fn, has_error refusal (ERROR
node + missing token), edition resolution, lazy import, and
function discovery (free / impl / mod / nested).
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _rust_extras_present() -> bool:
    try:
        importlib.import_module("tree_sitter")
        importlib.import_module("tree_sitter_rust")
    except ImportError:
        return False
    return True


_REASON = "tree_sitter / tree_sitter_rust not installed"
pytestmark_rust = pytest.mark.skipif(not _rust_extras_present(), reason=_REASON)


# ---------------------------------------------------------------------------
# Lazy-import gate
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cli_imports_without_tree_sitter_loaded() -> None:
    """Importing furqan_lint.cli must not transitively import
    tree_sitter. If it does, the Python-only install path would
    crash on a fresh venv even when the user is only linting .py
    files."""
    # Freshly remove cli + rust_adapter from sys.modules to force
    # a clean import.
    for name in list(sys.modules):
        if name.startswith("furqan_lint.cli") or name.startswith("furqan_lint.rust_adapter"):
            del sys.modules[name]
    if "tree_sitter" in sys.modules:
        del sys.modules["tree_sitter"]

    importlib.import_module("furqan_lint.cli")

    assert "tree_sitter" not in sys.modules, (
        "Importing furqan_lint.cli triggered a tree_sitter import. "
        "The Python-only install path must remain free of tree_sitter."
    )


# ---------------------------------------------------------------------------
# Function discovery
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_function_discovery_finds_free_impl_mod_and_nested_functions() -> None:
    """All four function shapes (free, impl method, mod-nested,
    nested fn-in-fn) must be discovered by the recursive walk."""
    from furqan_lint.rust_adapter import parse_file

    src = b"""
fn free_fn() -> i32 { 1 }

mod inner {
    pub fn mod_fn() -> i32 { 2 }
}

struct S;
impl S {
    fn impl_fn(&self) -> i32 { 3 }
}

fn outer_with_nested() -> i32 {
    fn nested_fn() -> i32 { 4 }
    nested_fn()
}
"""
    tmp = Path("/tmp/_test_discovery.rs")
    tmp.write_bytes(src)
    module = parse_file(tmp)
    names = sorted(fn.name for fn in module.functions)
    assert names == ["free_fn", "impl_fn", "mod_fn", "nested_fn", "outer_with_nested"]


@pytestmark_rust
def test_function_discovery_skips_function_signature_item() -> None:
    """``function_signature_item`` (trait declarations with no body)
    must NOT appear as functions in the translated module."""
    from furqan_lint.rust_adapter import parse_file

    src = b"""
trait T {
    fn declared(&self) -> i32;
    fn declared_with_default(&self) -> i32 { 42 }
}
"""
    tmp = Path("/tmp/_test_sig_skip.rs")
    tmp.write_bytes(src)
    module = parse_file(tmp)
    names = sorted(fn.name for fn in module.functions)
    assert names == ["declared_with_default"]


@pytestmark_rust
def test_function_discovery_skips_closure_expression() -> None:
    """``closure_expression`` is skipped per Phase 1 prompt 3.4."""
    from furqan_lint.rust_adapter import parse_file

    src = b"""
fn outer() -> i32 {
    let _f = |x: i32| -> i32 { x + 1 };
    7
}
"""
    tmp = Path("/tmp/_test_closure_skip.rs")
    tmp.write_bytes(src)
    module = parse_file(tmp)
    names = [fn.name for fn in module.functions]
    assert names == ["outer"]


# ---------------------------------------------------------------------------
# Body translation
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_implicit_return_detection_via_positional_walk() -> None:
    """Validator R1: ``fn f() -> i32 { 42 }`` must produce a
    FunctionDef whose statements contain a ReturnStmt. Detection is
    positional (last named child has no trailing ';'), not via a
    field_name lookup, so this works across tree-sitter-rust 0.23
    and 0.24."""
    from furqan.parser.ast_nodes import ReturnStmt

    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_implicit.rs")
    tmp.write_bytes(b"fn f() -> i32 { 42 }\n")
    module = parse_file(tmp)
    fn = module.functions[0]
    assert any(isinstance(s, ReturnStmt) for s in fn.statements)


@pytestmark_rust
def test_explicit_return_statement_translates_to_return_stmt() -> None:
    """``return X;`` produces a ReturnStmt."""
    from furqan.parser.ast_nodes import ReturnStmt

    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_explicit.rs")
    tmp.write_bytes(b"fn f() -> i32 { return 42; }\n")
    module = parse_file(tmp)
    fn = module.functions[0]
    assert any(isinstance(s, ReturnStmt) for s in fn.statements)


@pytestmark_rust
def test_match_with_returning_arms_satisfies_d24() -> None:
    """A match where every arm body is a return-or-implicit-return
    must satisfy D24."""
    from furqan.checker.all_paths_return import check_all_paths_return

    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_match_returns.rs")
    tmp.write_bytes(b"fn f(x: i32) -> i32 { match x { 0 => 0, _ => 1 } }\n")
    module = parse_file(tmp)
    diagnostics = list(check_all_paths_return(module))
    assert diagnostics == [], f"D24 fired unexpectedly: {diagnostics}"


@pytestmark_rust
def test_question_mark_operator_is_opaque_for_d24() -> None:
    """The ? operator is opaque for D24: it does not contribute a
    return-on-Err that D24 should rely on; a function using ?
    still needs a final return."""
    from furqan.checker.all_paths_return import check_all_paths_return

    from furqan_lint.rust_adapter import parse_file

    src = b"""
fn helper() -> Result<i32, std::io::Error> { Ok(1) }
fn caller() -> Result<i32, std::io::Error> {
    let v = helper()?;
    Ok(v)
}
"""
    tmp = Path("/tmp/_test_question.rs")
    tmp.write_bytes(src)
    module = parse_file(tmp)
    diagnostics = list(check_all_paths_return(module))
    assert diagnostics == [], f"D24 fired unexpectedly: {diagnostics}"


# ---------------------------------------------------------------------------
# Return type translation
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_result_translates_to_union_type() -> None:
    """``Result<T, E>`` produces a UnionType(TypePath(T), TypePath(E))."""
    from furqan.parser.ast_nodes import UnionType

    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_result_union.rs")
    tmp.write_bytes(b"fn f() -> Result<i32, std::io::Error> { Ok(1) }\n")
    module = parse_file(tmp)
    fn = module.functions[0]
    assert isinstance(fn.return_type, UnionType)
    assert fn.return_type.left.base == "i32"
    assert "Error" in fn.return_type.right.base


@pytestmark_rust
def test_option_translates_to_union_with_none_arm() -> None:
    """``Option<T>`` produces a UnionType(TypePath(T), TypePath('None'))
    so the existing producer_predicate fires on Option-collapse."""
    from furqan.parser.ast_nodes import UnionType

    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_option_union.rs")
    tmp.write_bytes(b"fn f() -> Option<i32> { Some(1) }\n")
    module = parse_file(tmp)
    fn = module.functions[0]
    assert isinstance(fn.return_type, UnionType)
    assert fn.return_type.left.base == "i32"
    assert fn.return_type.right.base == "None"


@pytestmark_rust
def test_async_fn_translates_identically_to_sync() -> None:
    """``async fn`` is irrelevant to D24/D11; the translator treats
    it identically to a non-async function."""
    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_async.rs")
    tmp.write_bytes(b"async fn fetch(id: u64) -> i32 { 42 }\n")
    module = parse_file(tmp)
    assert len(module.functions) == 1
    assert module.functions[0].name == "fetch"


# ---------------------------------------------------------------------------
# Parse error refusal
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_has_error_refusal_on_explicit_error_node() -> None:
    """A source with a syntax error must raise RustParseError."""
    from furqan_lint.rust_adapter import RustParseError, parse_file

    tmp = Path("/tmp/_test_error_node.rs")
    tmp.write_bytes(b"fn f(x: i32) -> i32 { let !! ;; }\n")
    with pytest.raises(RustParseError):
        parse_file(tmp)


@pytestmark_rust
def test_has_error_refusal_on_missing_brace() -> None:
    """A source missing a closing brace must raise RustParseError;
    the detection mechanism is tree.root_node.has_error which
    catches both ERROR nodes and is_missing markers (a manual walk
    for type=='ERROR' would miss the missing-brace case)."""
    from furqan_lint.rust_adapter import RustParseError, parse_file

    tmp = Path("/tmp/_test_missing_brace.rs")
    tmp.write_bytes(b"fn f() -> i32 { 42\n")  # missing closing }
    with pytest.raises(RustParseError):
        parse_file(tmp)


# ---------------------------------------------------------------------------
# Edition resolution
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_edition_defaults_to_2021_when_no_cargo_toml(tmp_path: Path) -> None:
    """If no Cargo.toml is found, edition defaults to '2021'."""
    from furqan_lint.rust_adapter.edition import edition_for

    rs = tmp_path / "stray.rs"
    rs.write_text("fn f() -> i32 { 1 }\n")
    assert edition_for(rs) == "2021"


@pytestmark_rust
def test_edition_read_from_cargo_toml(tmp_path: Path) -> None:
    """The nearest Cargo.toml's [package].edition is used when valid."""
    from furqan_lint.rust_adapter.edition import edition_for

    (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"\nedition = "2018"\n')
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    rs = src_dir / "lib.rs"
    rs.write_text("fn f() -> i32 { 1 }\n")
    assert edition_for(rs) == "2018"


# ---------------------------------------------------------------------------
# Phase 2 (v0.7.1): R3 IR-shape pins
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_empty_body_translates_to_zero_statements() -> None:
    """``fn f() -> i32 {}`` must produce a FunctionDef with
    ``statements=()``. Locks the IR shape that R3 relies on (zero
    ReturnStmt + non-None return type)."""
    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_empty.rs")
    tmp.write_bytes(b"fn f() -> i32 {}\n")
    module = parse_file(tmp)
    fn = module.functions[0]
    assert len(fn.statements) == 0


@pytestmark_rust
def test_panic_with_semicolon_translates_to_zero_statements() -> None:
    """``fn f() -> i32 { panic!(); }`` must produce a FunctionDef
    with ``statements=()``: the macro-with-semicolon is an
    expression_statement that the translator drops. The IR shape
    is identical to the empty-body case."""
    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_panic_semi.rs")
    tmp.write_bytes(b"fn f() -> i32 { panic!(); }\n")
    module = parse_file(tmp)
    fn = module.functions[0]
    assert len(fn.statements) == 0


@pytestmark_rust
def test_panic_as_tail_expression_synthesises_one_return_stmt() -> None:
    """``fn f() -> i32 { panic!() }`` (no semicolon) must produce
    a FunctionDef with exactly one ReturnStmt: the translator
    synthesizes a ReturnStmt for any tail expression per the v0.7.0
    R1 rule. This is the IR shape that prevents R3 from firing on
    the panic-as-tail-expression case (documented limit)."""
    from furqan.parser.ast_nodes import ReturnStmt

    from furqan_lint.rust_adapter import parse_file

    tmp = Path("/tmp/_test_panic_tail.rs")
    tmp.write_bytes(b"fn f() -> i32 { panic!() }\n")
    module = parse_file(tmp)
    fn = module.functions[0]
    assert len(fn.statements) == 1
    assert isinstance(fn.statements[0], ReturnStmt)


# ---------------------------------------------------------------------------
# Phase 2 (v0.7.1): runner discriminator
# ---------------------------------------------------------------------------


@pytestmark_rust
def test_is_r3_shaped_recognises_only_r3() -> None:
    """``_is_r3_shaped`` must return True for R3-shaped diagnoses
    (containing 'but its body') and False for R1-shaped diagnoses
    (containing 'no compound type with that name'). Pinned so a
    future upstream prose drift breaks the test, not the user."""
    from unittest.mock import MagicMock

    from furqan_lint.rust_adapter.runner import _is_r3_shaped

    r3_diag = MagicMock()
    r3_diag.diagnosis = (
        "function 'f' declares return type i32 but its body contains "
        "no `return` statement (recursing into any nested if-blocks)."
    )
    r1_diag = MagicMock()
    r1_diag.diagnosis = (
        "the return type of function 'f' references type 'i32', but "
        "no compound type with that name is declared in this module."
    )
    assert _is_r3_shaped(r3_diag) is True
    assert _is_r3_shaped(r1_diag) is False
