"""Tests for the Python ``ast`` -> Furqan AST adapter.

The adapter is the load-bearing translation layer. Every test here
exercises one shape of Python source and asserts the corresponding
Furqan AST shape. The checkers themselves are tested end-to-end in
``test_checks.py``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from furqan.parser.ast_nodes import (
    BismillahBlock,
    CallRef,
    CompoundTypeDef,
    FunctionDef,
    IdentExpr,
    IfStmt,
    Module,
    ParamDecl,
    ReturnStmt,
    TypePath,
    UnionType,
)

from furqan_lint.adapter import translate_file, translate_source


# ---------------------------------------------------------------------------
# Function shape
# ---------------------------------------------------------------------------

def test_simple_function_translates_to_function_def(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "simple_function.py")
    assert isinstance(module, Module)
    assert len(module.functions) == 1
    fn = module.functions[0]
    assert isinstance(fn, FunctionDef)
    assert fn.name == "greet"


def test_function_params_translate_to_param_decls(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "simple_function.py")
    fn = module.functions[0]
    assert len(fn.params) == 1
    p = fn.params[0]
    assert isinstance(p, ParamDecl)
    assert p.name == "name"
    assert p.type_path.base == "str"


def test_return_annotation_translates_to_type_path(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "simple_function.py")
    fn = module.functions[0]
    assert isinstance(fn.return_type, TypePath)
    assert fn.return_type.base == "str"


# ---------------------------------------------------------------------------
# Optional / union return types
# ---------------------------------------------------------------------------

def test_optional_annotation_translates_to_union_type() -> None:
    src = (
        "from typing import Optional\n"
        "def f(x: int) -> Optional[str]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    assert isinstance(fn.return_type, UnionType)
    assert fn.return_type.left.base == "str"
    assert fn.return_type.right.base == "None"


def test_pipe_union_none_translates_to_union_type() -> None:
    src = (
        "def f(x: int) -> str | None:\n"
        "    return None\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    assert isinstance(fn.return_type, UnionType)
    assert fn.return_type.left.base == "str"
    assert fn.return_type.right.base == "None"


# ---------------------------------------------------------------------------
# Statement structure
# ---------------------------------------------------------------------------

def test_if_statement_translates_to_if_stmt() -> None:
    src = (
        "def f(x: int) -> int:\n"
        "    if x:\n"
        "        return 1\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    assert len(fn.statements) == 1
    assert isinstance(fn.statements[0], IfStmt)


def test_if_else_translates_with_else_body() -> None:
    src = (
        "def f(x: int) -> int:\n"
        "    if x:\n"
        "        return 1\n"
    "    else:\n"
        "        return 2\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    if_stmt = fn.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert len(if_stmt.body) == 1
    assert len(if_stmt.else_body) == 1


def test_return_stmt_translates() -> None:
    src = (
        "def f() -> int:\n"
        "    return 42\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    assert len(fn.statements) == 1
    assert isinstance(fn.statements[0], ReturnStmt)


def test_bare_return_translates_to_none_marker() -> None:
    src = (
        "def f() -> None:\n"
        "    return\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    ret = fn.statements[0]
    assert isinstance(ret, ReturnStmt)
    assert isinstance(ret.value, IdentExpr)
    assert ret.value.name == "__none__"


# ---------------------------------------------------------------------------
# Call extraction
# ---------------------------------------------------------------------------

def test_call_extracted_as_call_ref() -> None:
    src = (
        "def f() -> int:\n"
        "    return helper()\n"
        "def helper() -> int:\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    f = next(fn for fn in module.functions if fn.name == "f")
    assert any(isinstance(c, CallRef) and c.path == ("helper",) for c in f.calls)


def test_method_call_extracted_by_attr_name() -> None:
    src = (
        "def f(obj) -> int:\n"
        "    return obj.compute()\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    assert any(c.path == ("compute",) for c in fn.calls)


# ---------------------------------------------------------------------------
# Class translation
# ---------------------------------------------------------------------------

def test_class_translates_to_compound_type_def() -> None:
    src = (
        "class Doc:\n"
        "    def render(self) -> str:\n"
        "        return ''\n"
    )
    module = translate_source(src, "<test>")
    assert len(module.compound_types) == 1
    ct = module.compound_types[0]
    assert isinstance(ct, CompoundTypeDef)
    assert ct.name == "Doc"


# ---------------------------------------------------------------------------
# Module-level translation
# ---------------------------------------------------------------------------

def test_module_has_synthetic_bismillah() -> None:
    module = translate_source("def f() -> int:\n    return 1\n", "<test>")
    assert isinstance(module.bismillah, BismillahBlock)
    assert module.bismillah.alias_used == "bismillah"


def test_module_name_from_filename() -> None:
    module = translate_source("def f() -> int:\n    return 1\n", "/a/b/foo.py")
    assert module.bismillah.name == "foo"


def test_nested_if_translates_recursively() -> None:
    src = (
        "def f(x: int, y: int) -> int:\n"
        "    if x:\n"
        "        if y:\n"
        "            return 1\n"
        "        return 2\n"
        "    return 3\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    outer = fn.statements[0]
    assert isinstance(outer, IfStmt)
    inner = outer.body[0]
    assert isinstance(inner, IfStmt)


def test_async_function_treated_as_regular() -> None:
    src = (
        "async def f() -> int:\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    assert len(module.functions) == 1
    assert module.functions[0].name == "f"


def test_no_return_annotation_gives_none_return_type() -> None:
    src = (
        "def f():\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    assert module.functions[0].return_type is None


def test_unannotated_param_gives_any_type() -> None:
    src = (
        "def f(x) -> int:\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    fn = module.functions[0]
    assert fn.params[0].type_path.base == "Any"


def test_only_top_level_functions_collected() -> None:
    """Defect 1 fix: ``ast.walk`` would re-collect inner functions.
    The adapter iterates ``tree.body`` only."""
    src = (
        "def outer() -> int:\n"
        "    def inner() -> int:\n"
        "        return 1\n"
        "    return inner()\n"
    )
    module = translate_source(src, "<test>")
    names = [fn.name for fn in module.functions]
    assert names == ["outer"]


def test_class_methods_also_collected_as_functions() -> None:
    src = (
        "class C:\n"
        "    def a(self) -> int:\n"
        "        return 1\n"
        "    def b(self) -> int:\n"
        "        return 2\n"
    )
    module = translate_source(src, "<test>")
    method_names = sorted(fn.name for fn in module.functions)
    assert method_names == ["a", "b"]
