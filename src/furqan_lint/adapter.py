"""Translate a Python ``ast.Module`` into a Furqan ``Module``.

The adapter is structural, not semantic. It carries shape across the
language boundary so Furqan's structural-honesty checkers can run on
Python source without modification. Two translation contracts:

1. The Python module yields one Furqan ``Module`` with a synthetic
   ``BismillahBlock``. The Bismillah is a placeholder; D24 and D11 do
   not introspect it. Phase 2 may derive its fields from a
   ``__furqan_serves__`` module variable.
2. Every Python expression collapses to one of two opaque
   ``IdentExpr`` markers: ``__none__`` (the literal ``None``) or
   ``__opaque__`` (everything else). D24 only inspects whether a
   ``ReturnStmt`` exists on a path; D11 only inspects call sites and
   declared return types. Neither needs real expression structure.
"""

from __future__ import annotations

import ast
from pathlib import Path

from furqan.parser.ast_nodes import (
    BismillahBlock,
    CallRef,
    CompoundTypeDef,
    FieldDecl,
    FunctionDef,
    IdentExpr,
    IfStmt,
    LayerBlock,
    Module,
    ParamDecl,
    ReturnStmt,
    SourceSpan,
    TypePath,
    UnionType,
)


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def translate_file(path: Path) -> Module:
    """Parse a Python file at ``path`` and return a Furqan ``Module``."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    return _translate_module(tree, str(path))


def translate_source(source: str, filename: str = "<string>") -> Module:
    """Parse a Python source string and return a Furqan ``Module``."""
    tree = ast.parse(source, filename=filename)
    return _translate_module(tree, filename)


# ---------------------------------------------------------------------------
# Module translation
# ---------------------------------------------------------------------------

def _translate_module(tree: ast.Module, filename: str) -> Module:
    """Translate an ``ast.Module`` into a Furqan ``Module``.

    DEFECT 1 FIX: iterate ``tree.body`` only, not ``ast.walk``. Walking
    the whole tree would re-collect class methods as top-level
    functions and double-count nested function definitions. Methods
    are gathered explicitly inside the ``ClassDef`` branch below.
    """
    functions: list[FunctionDef] = []
    compound_types: list[CompoundTypeDef] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(_translate_function(node, filename))
        elif isinstance(node, ast.ClassDef):
            compound_types.append(_translate_class(node, filename))
            # Class methods become top-level functions in the Furqan
            # Module. CompoundTypeDef has no methods field in the
            # AST, so this is the only place to put them.
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(_translate_function(child, filename))

    module_name = Path(filename).stem
    sp = _span(filename, 1, 0)

    bismillah = BismillahBlock(
        name=module_name,
        authority=("python_module",),
        serves=(("structural_honesty",),),
        scope=(module_name,),
        not_scope=(),
        span=sp,
        alias_used="bismillah",
    )

    return Module(
        bismillah=bismillah,
        functions=tuple(functions),
        source_path=filename,
        compound_types=tuple(compound_types),
    )


# ---------------------------------------------------------------------------
# Class translation
# ---------------------------------------------------------------------------

def _translate_class(node: ast.ClassDef, filename: str) -> CompoundTypeDef:
    """Translate a Python class to a ``CompoundTypeDef``.

    Phase 1 does not separate zahir from batin. Both layers are empty
    ``LayerBlock`` shells. The class name is captured so a future
    ring-close R1 type-resolution pass can find it.
    """
    sp = _span(filename, node.lineno, node.col_offset)
    return CompoundTypeDef(
        name=node.name,
        zahir=LayerBlock(
            layer="zahir",
            fields=(),
            span=sp,
            alias_used="zahir",
        ),
        batin=LayerBlock(
            layer="batin",
            fields=(),
            span=sp,
            alias_used="batin",
        ),
        span=sp,
    )


# ---------------------------------------------------------------------------
# Function translation
# ---------------------------------------------------------------------------

def _translate_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    filename: str,
) -> FunctionDef:
    params: list[ParamDecl] = []
    for arg in node.args.args:
        type_path = _translate_annotation(arg.annotation, filename)
        params.append(
            ParamDecl(
                name=arg.arg,
                type_path=type_path,
                span=_span(filename, arg.lineno, arg.col_offset),
            )
        )

    return_type = None
    if node.returns is not None:
        return_type = _translate_return_annotation(node.returns, filename)

    statements = _translate_body(node.body, filename)
    calls = _extract_calls(node, filename)

    return FunctionDef(
        name=node.name,
        calls=tuple(calls),
        span=_span(filename, node.lineno, node.col_offset),
        params=tuple(params),
        return_type=return_type,
        accesses=(),
        statements=tuple(statements),
    )


# ---------------------------------------------------------------------------
# Type annotation translation
# ---------------------------------------------------------------------------

def _translate_annotation(
    node: ast.expr | None,
    filename: str,
) -> TypePath:
    """Translate a parameter type annotation to a ``TypePath``.

    Untyped parameters get the sentinel ``Any``. The checkers that
    look at parameter types (none in Phase 1) can pattern-match on
    ``Any`` to skip them.
    """
    if node is None:
        return TypePath(
            base="Any",
            layer=None,
            span=_span(filename, 0, 0),
            layer_alias_used=None,
        )
    return TypePath(
        base=_annotation_name(node),
        layer=None,
        span=_span(filename, node.lineno, node.col_offset),
        layer_alias_used=None,
    )


def _translate_return_annotation(
    node: ast.expr,
    filename: str,
) -> TypePath | UnionType:
    """Translate a return-type annotation, mapping ``Optional[X]`` and
    ``X | None`` to a Furqan ``UnionType``."""
    sp = _span(filename, node.lineno, node.col_offset)

    if _is_optional(node):
        inner = _extract_optional_inner(node)
        return UnionType(
            left=TypePath(
                base=_annotation_name(inner),
                layer=None,
                span=sp,
                layer_alias_used=None,
            ),
            right=TypePath(
                base="None",
                layer=None,
                span=sp,
                layer_alias_used=None,
            ),
            span=sp,
        )

    if _is_pipe_union_with_none(node):
        inner = _extract_pipe_union_inner(node)
        return UnionType(
            left=TypePath(
                base=_annotation_name(inner),
                layer=None,
                span=sp,
                layer_alias_used=None,
            ),
            right=TypePath(
                base="None",
                layer=None,
                span=sp,
                layer_alias_used=None,
            ),
            span=sp,
        )

    return TypePath(
        base=_annotation_name(node),
        layer=None,
        span=sp,
        layer_alias_used=None,
    )


def _is_optional(node: ast.expr) -> bool:
    """True iff ``node`` is ``Optional[X]`` or ``typing.Optional[X]``."""
    if isinstance(node, ast.Subscript):
        if isinstance(node.value, ast.Name) and node.value.id == "Optional":
            return True
        if isinstance(node.value, ast.Attribute) and node.value.attr == "Optional":
            return True
    return False


def _extract_optional_inner(node: ast.Subscript) -> ast.expr:
    """Extract ``X`` from ``Optional[X]``."""
    return node.slice


def _is_pipe_union_with_none(node: ast.expr) -> bool:
    """True iff ``node`` is ``X | None`` (PEP 604 form)."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        if isinstance(node.right, ast.Constant) and node.right.value is None:
            return True
        if isinstance(node.right, ast.Name) and node.right.id == "None":
            return True
    return False


def _extract_pipe_union_inner(node: ast.BinOp) -> ast.expr:
    """Extract ``X`` from ``X | None``."""
    return node.left


def _annotation_name(node: ast.expr) -> str:
    """Best-effort short name for any annotation expression."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Subscript):
        return _annotation_name(node.value)
    return "Unknown"


# ---------------------------------------------------------------------------
# Body and expression translation
# ---------------------------------------------------------------------------

def _translate_body(
    body: list[ast.stmt],
    filename: str,
) -> list:
    """Extract ``ReturnStmt`` and ``IfStmt`` only.

    Every other statement type (assignments, expressions, loops, ...)
    is silently skipped. The two checkers wired in Phase 1 only
    inspect returns and conditional branching.
    """
    result: list = []
    for node in body:
        if isinstance(node, ast.Return):
            result.append(
                ReturnStmt(
                    value=_translate_expression(node.value, filename),
                    span=_span(filename, node.lineno, node.col_offset),
                )
            )
        elif isinstance(node, ast.If):
            result.append(
                IfStmt(
                    condition=_translate_expression(node.test, filename),
                    body=tuple(_translate_body(node.body, filename)),
                    span=_span(filename, node.lineno, node.col_offset),
                    else_body=tuple(_translate_body(node.orelse, filename)),
                )
            )
    return result


def _extract_calls(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    filename: str,
) -> list[CallRef]:
    """Collect call references inside a function body.

    Phase 1 gap: ``ast.walk`` recurses into nested function bodies, so
    a call inside a closure is attributed to the enclosing function.
    Documented in Section 8 of the implementation prompt.
    """
    calls: list[CallRef] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = _call_name(child)
            if name:
                calls.append(
                    CallRef(
                        path=(name,),
                        span=_span(filename, child.lineno, child.col_offset),
                    )
                )
    return calls


def _call_name(node: ast.Call) -> str | None:
    """Return the simple name of the callable at a call site, or
    ``None`` if it cannot be reduced to a bare identifier."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _translate_expression(
    node: ast.expr | None,
    filename: str,
) -> IdentExpr:
    """Collapse every Python expression to one of two opaque markers.

    ``__none__`` marks the literal ``None`` (so a future D22 pass can
    distinguish ``return None`` from ``return value``). ``__opaque__``
    marks every other expression. Phase 1 does no type inference;
    D22 (return-type match) will treat these as uncheckable, which is
    correct.

    KNOWN PHASE 1 GAP: D24 treats ``return None`` as a satisfied
    return path even when the declared return type is non-Optional.
    This is a type mismatch, not a missing return. Phase 2 with D22
    closes this gap.
    """
    sp_zero = _span(filename, 0, 0)
    if node is None:
        return IdentExpr(name="__none__", span=sp_zero)
    if isinstance(node, ast.Constant) and node.value is None:
        return IdentExpr(
            name="__none__",
            span=_span(filename, node.lineno, node.col_offset),
        )
    return IdentExpr(
        name="__opaque__",
        span=_span(filename, node.lineno, node.col_offset),
    )


def _span(filename: str, line: int, col: int) -> SourceSpan:
    return SourceSpan(file=filename, line=line, column=col)
