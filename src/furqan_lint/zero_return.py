"""R3: ring-close check for declared producers (Python semantics).

A function that declares a non-``None`` return type but contains zero
``return`` statements anywhere in its body is reported as
``zero_return_path``. mypy reports the same case as "Missing return
statement"; this checker brings furqan-lint to parity for that class.

Skipped (does not fire R3):

- Functions annotated ``-> None``. The implicit ``None`` return is
  the declared type.
- Functions annotated ``-> Optional[T]``, ``-> T | None``, or any
  ``Union`` containing ``None`` (implicit ``None`` is a valid return
  for Optional). Annotation analysis delegates to
  ``adapter._is_optional``, ``adapter._is_pipe_union_with_none``,
  ``adapter._is_union_with_none``, and ``adapter._is_all_none_union``.
  These encode the v0.3.x degenerate-form fixes (Optional[None],
  Union[None, None], etc.) that took six audit rounds to harden;
  R3 does not re-derive them.
- Functions with no return annotation at all. R3 has no contract
  for an unannotated function.
- Functions whose body raises unconditionally (``raise`` is the
  terminal value, not a ``return``). Conservative: only the
  canonical "function body is exactly one Raise" or "all paths
  end in Raise" shapes are recognized.
- Functions whose body is the canonical infinite loop ``while True:``
  with no ``break`` (provably non-returning; reaching the end of
  the body is unreachable). Non-canonical loops (``while 1:``,
  ``itertools.count()``) are NOT recognized in v0.6.0.
- Functions decorated with any of the names in
  ``_SKIP_DECORATORS`` (e.g., ``@abstractmethod``, ``@overload``).
  Decorator resolution in v0.6.0 is name-only; aliased imports
  (``from abc import abstractmethod as abstract``) are NOT yet
  resolved. v0.6.1 will add symbol-table-backed resolution.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from furqan_lint.adapter import (
    _is_all_none_union,
    _is_optional,
    _is_pipe_union_with_none,
    _is_union_with_none,
)

# Decorator skip-list. Name-only resolution; v0.6.1 will resolve
# aliased imports through the symbol table.
_SKIP_DECORATORS: frozenset[str] = frozenset(
    {
        "abstractmethod",
        "overload",
        "typing.overload",
        "abc.abstractmethod",
    }
)


@dataclass(frozen=True)
class ZeroReturnDiagnostic:
    """A function that declared a non-None return type but contains
    zero ``return`` statements (R3, ring-close)."""

    function_name: str
    lineno: int
    col_offset: int
    declared_return: str

    @property
    def diagnosis(self) -> str:
        return (
            f"function '{self.function_name}' declares "
            f"-> {self.declared_return} but contains no "
            f"`return` statement (R3, ring-close)."
        )


def check_zero_return(tree: ast.Module) -> list[ZeroReturnDiagnostic]:
    """Walk every top-level and nested function/method in ``tree`` and
    emit a diagnostic for each that satisfies the R3 firing condition.

    Methods of classes are walked. Lambdas are not (they cannot have
    a return-type annotation in Python syntax). Nested function
    definitions are walked independently of their enclosing function.
    """
    diagnostics: list[ZeroReturnDiagnostic] = []
    for fn in _iter_function_defs(tree):
        diagnostics.extend(_check_function(fn))
    return diagnostics


# ---------------------------------------------------------------------------
# Walking
# ---------------------------------------------------------------------------


def _iter_function_defs(
    tree: ast.AST,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Yield every ``FunctionDef`` and ``AsyncFunctionDef`` reachable
    from ``tree``, including methods of classes and inner functions."""
    out: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            out.append(node)
    return out


# ---------------------------------------------------------------------------
# Per-function check
# ---------------------------------------------------------------------------


def _check_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ZeroReturnDiagnostic]:
    """Return a single-element list if ``node`` satisfies R3's
    firing condition, else an empty list.

    Returns a list (rather than ``ZeroReturnDiagnostic | None``) so
    that the caller can ``.extend(...)`` without a None-narrowing
    step that D11 status-coverage would flag as silently dropping
    the Incomplete arm.
    """
    # 1. No return-type annotation: skip.
    if node.returns is None:
        return []

    # 2. Annotation allows None (Optional/Union-with-None/None): skip.
    if _annotation_allows_none(node.returns):
        return []

    # 3. Decorator on the skip-list: skip.
    if _has_skip_decorator(node):
        return []

    # 4. Body is provably non-returning (raise-only or while True
    #    with no break): skip.
    if _body_is_non_returning(node.body):
        return []

    # 5. Has at least one return statement (excluding nested
    #    function/lambda bodies): not R3's case (D24 territory).
    if _has_any_return(node.body):
        return []

    # All checks passed - fire R3.
    return [
        ZeroReturnDiagnostic(
            function_name=node.name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            declared_return=_render_annotation(node.returns),
        )
    ]


# ---------------------------------------------------------------------------
# Annotation analysis (delegates to adapter helpers)
# ---------------------------------------------------------------------------


def _annotation_allows_none(ann: ast.expr) -> bool:
    """True iff ``ann`` is a type annotation that includes ``None``.

    Delegates to the adapter helpers that encode the v0.3.x
    degenerate-form fixes. R3 does not re-derive them.
    """
    if _is_none_literal(ann):
        return True
    if _is_optional(ann):
        return True
    if _is_pipe_union_with_none(ann):
        return True
    if _is_union_with_none(ann):
        return True
    return bool(_is_all_none_union(ann))


def _is_none_literal(node: ast.expr) -> bool:
    """True iff ``node`` is the bare ``None`` literal."""
    if isinstance(node, ast.Constant) and node.value is None:
        return True
    return isinstance(node, ast.Name) and node.id == "None"


def _render_annotation(ann: ast.expr) -> str:
    """Best-effort rendering of an annotation for diagnostic prose.

    Falls back to ``ast.dump`` if ``ast.unparse`` is unavailable
    (Python < 3.9, but the project requires 3.10+ so unparse is
    always present).
    """
    try:
        return ast.unparse(ann)
    except AttributeError:  # pragma: no cover  - 3.10+ guaranteed
        return ast.dump(ann)


# ---------------------------------------------------------------------------
# Decorator skip-list
# ---------------------------------------------------------------------------


def _has_skip_decorator(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """True iff any decorator on ``node`` matches a name in
    ``_SKIP_DECORATORS``.

    Recognizes ``@abstractmethod``, ``@overload``,
    ``@typing.overload``, ``@abc.abstractmethod``. Does NOT recognize
    aliased imports (``from abc import abstractmethod as abstract``).
    Pinned as v0.6.1 regression target.
    """
    return any(_decorator_matches_skip_list(dec) for dec in node.decorator_list)


def _decorator_matches_skip_list(dec: ast.expr) -> bool:
    """True iff the decorator reduces to a dotted name in
    ``_SKIP_DECORATORS``.

    Recognizes:
    - ``@abstractmethod``                      -> ``"abstractmethod"``
    - ``@abc.abstractmethod``                  -> ``"abc.abstractmethod"``
    - ``@abstractmethod()`` (called)           -> ``"abstractmethod"``
    - ``@functools.cache(maxsize=128)``        -> ``"functools.cache"``

    Returns ``False`` for shapes that don't reduce to a dotted name
    (e.g., ``@(lambda f: f)``). Returns ``bool`` rather than
    ``str | None`` so that ``_has_skip_decorator``'s consumer-side
    discipline (D11) is honestly propagated.
    """
    target = dec.func if isinstance(dec, ast.Call) else dec
    if isinstance(target, ast.Name):
        return target.id in _SKIP_DECORATORS
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
        return f"{target.value.id}.{target.attr}" in _SKIP_DECORATORS
    return False


# ---------------------------------------------------------------------------
# Non-returning body detection (raise-only, while True)
# ---------------------------------------------------------------------------


def _body_is_non_returning(body: list[ast.stmt]) -> bool:
    """True iff the body is provably non-returning.

    Two recognized shapes:
    1. Every statement on every path is or ends in ``Raise``. The
       most common form is a body that consists of nothing but a
       single ``Raise`` statement. Conservative: branching bodies
       where every branch ends in ``Raise`` are also recognized.
    2. The body is exactly one ``while True:`` (or ``while 1:`` is
       NOT recognized in v0.6.0; canonical form only) with no
       ``break`` reachable from the loop body.

    Conservative: any other shape is treated as potentially returning.
    Non-canonical infinite loops, raises hidden inside ``try/except``
    that swallows them, etc. are NOT recognized. False positives
    here are bug reports.
    """
    if not body:
        return False

    # Shape 1: all-raise terminal-statement check.
    if _all_paths_terminate_in_raise(body):
        return True

    # Shape 2: body is exactly one canonical `while True:` with no break.
    return (
        len(body) == 1
        and isinstance(body[0], ast.While)
        and _is_constant_true(body[0].test)
        and not _contains_break(body[0].body)
    )


def _all_paths_terminate_in_raise(body: list[ast.stmt]) -> bool:
    """True iff the body's last statement is ``Raise``, or is an
    ``If`` whose body and else_body both terminate in ``Raise``
    recursively. Conservative.
    """
    if not body:
        return False
    last = body[-1]
    if isinstance(last, ast.Raise):
        return True
    if isinstance(last, ast.If):
        return _all_paths_terminate_in_raise(last.body) and _all_paths_terminate_in_raise(
            last.orelse
        )
    return False


def _is_constant_true(node: ast.expr) -> bool:
    """True iff ``node`` is the literal ``True``. Does NOT recognize
    ``1``, ``"truthy"``, or any other truthy-but-not-True expression.
    """
    return isinstance(node, ast.Constant) and node.value is True


def _contains_break(body: list[ast.stmt]) -> bool:
    """True iff ``body`` (or any nested control-flow construct
    inside it) contains a ``Break``. Conservative: a ``Break`` inside
    a nested ``while`` or ``for`` loop is still counted, even though
    it would only break the inner loop. v0.6.0 prefers false-positive
    suppression over precise loop-scope tracking.
    """
    for node in body:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Break):
                return True
    return False


# ---------------------------------------------------------------------------
# Return-counting (excluding nested function/lambda bodies)
# ---------------------------------------------------------------------------


def _has_any_return(body: list[ast.stmt]) -> bool:
    """True iff the body contains any ``Return`` statement that
    belongs to the function being checked.

    Returns inside nested ``FunctionDef``, ``AsyncFunctionDef``, or
    ``Lambda`` bodies do NOT count - those are independent function
    scopes.
    """
    return any(_node_contains_own_return(node) for node in body)


def _node_contains_own_return(node: ast.AST) -> bool:
    """Recursive walker that returns True if ``node`` (or any of its
    nested children, EXCEPT inside another function/lambda body)
    contains a ``Return``.
    """
    if isinstance(node, ast.Return):
        return True
    # Stop descending into nested function/lambda scopes.
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
        return False
    return any(_node_contains_own_return(child) for child in ast.iter_child_nodes(node))
