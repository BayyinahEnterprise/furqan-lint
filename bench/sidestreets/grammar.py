"""Exhaustive small-scope program enumerator for the side-street map.

Every function is built from a small grammar of Python control flow.
Each condition and loop count reads a fresh bit from ``nxt()``, so
conditions are independent: every structural path is reachable by some
input, and execution over all inputs equals the structural truth.

A statement is a tuple ``(kind, *children)``; ``render`` turns a block
(list of statements) into indented source lines.
"""

from __future__ import annotations

from collections.abc import Iterator
from functools import cache

Stmt = tuple
Block = tuple

TERMINAL = {"return", "raise", "exit", "break", "continue", "return_x", "return_zero"}


# --------------------------------------------------------------------- size-bounded core
#
# Scope is bounded by total statement count ``n`` (every statement,
# simple or compound, counts 1). All programs with n <= N are
# enumerated, which covers every nesting depth up to N - 1. Pruning:
# no statement follows a terminal one in the same block (dead code),
# and ``pass`` only appears as a block's sole statement.


def _grammar(leaves_fn, one_child, two_child, loop_one, loop_two, guard_kinds=()):
    @cache
    def stmts(n: int, in_loop: bool) -> tuple[Stmt, ...]:
        if n < 1:
            return ()
        out: list[Stmt] = list(leaves_fn(in_loop)) if n == 1 else []
        m = n - 1
        for b in blocks(m, in_loop):
            out += [(k, b) for k in one_child]
            out += [("guard", g, b) for g in guard_kinds]
        for b in blocks(m, True):
            out += [(k, b) for k in loop_one]
        for i in range(1, m):
            for b1 in blocks(i, in_loop):
                for b2 in blocks(m - i, in_loop):
                    out += [(k, b1, b2) for k in two_child]
            if loop_two:
                for b1 in blocks(i, True):
                    for b2 in blocks(m - i, in_loop):
                        out += [(k, b1, b2) for k in loop_two]
        return tuple(out)

    @cache
    def blocks(n: int, in_loop: bool) -> tuple[Block, ...]:
        out: list[Block] = [(s,) for s in stmts(n, in_loop)]
        for i in range(1, n):
            for a in stmts(i, in_loop):
                if a[0] in TERMINAL or a[0].startswith("return") or a[0] == "pass":
                    continue
                for rest in blocks(n - i, in_loop):
                    if rest[0][0] == "pass":
                        continue
                    out.append((a, *rest))
        return tuple(out)

    return stmts, blocks


# --------------------------------------------------------------------- D24 grammar


def d24_leaves(in_loop: bool) -> list[Stmt]:
    leaves: list[Stmt] = [("return",), ("raise",), ("pass",), ("exit",)]
    if in_loop:
        leaves += [("break",), ("continue",)]
    return leaves


d24_stmts, d24_blocks = _grammar(
    d24_leaves,
    one_child=("if", "with_suppress"),
    two_child=("ifelse", "try_except", "try_finally"),
    loop_one=("while_true", "for"),
    loop_two=("for_else",),
)


def d24_functions(max_size: int) -> Iterator[Block]:
    """Every top-level body with at most ``max_size`` statements,
    smallest first, so the first witness of a disagreement is minimal."""
    for n in range(1, max_size + 1):
        yield from d24_blocks(n, False)


def _size(node) -> int:
    if isinstance(node, tuple):
        return 1 + sum(_size(c) for c in node if isinstance(c, tuple))
    return 0


# --------------------------------------------------------------------- D11 grammar


def d11_leaves(in_loop: bool) -> list[Stmt]:
    leaves: list[Stmt] = [
        ("bind",),  # x = p()
        ("rebind_zero",),  # x = 0
        ("rebind_none",),  # x = None
        ("return_x",),  # return x
        ("return_zero",),  # return 0
        ("return_use",),  # return x + 0   (crashes on None)
        ("return_or_zero",),  # return p() or 0
        ("return_or_none",),  # return p() or None
        ("return_eq",),  # return p() == 1
        ("return_lambda",),  # return (lambda: x)()
        ("raise",),
        ("use",),  # print(x)
    ]
    if in_loop:
        leaves += [("break",), ("continue",)]
    return leaves


GUARDS = ("is_none", "not_x", "is_not_none", "truthy", "walrus_is_none", "walrus_is_not_none")

d11_stmts, d11_blocks = _grammar(
    d11_leaves,
    one_child=("if",),
    two_child=("try_except",),
    loop_one=("for",),
    loop_two=(),
    guard_kinds=GUARDS,
)


def d11_functions(max_size: int) -> Iterator[Block]:
    for n in range(1, max_size + 1):
        for body in d11_blocks(n, False):
            if body[0][0] == "bind" or _starts_with_walrus(body[0]):
                yield body  # x bound first, else UnboundLocal noise


def _starts_with_walrus(s: Stmt) -> bool:
    return s[0] == "guard" and s[1].startswith("walrus")


# --------------------------------------------------------------------- render

_SIMPLE = {
    "return": "return 0",
    "raise": "raise ValueError()",
    "pass": "pass",
    "exit": "sys.exit()",
    "break": "break",
    "continue": "continue",
    "bind": "x = p()",
    "rebind_zero": "x = 0",
    "rebind_none": "x = None",
    "return_x": "return x",
    "return_zero": "return 0",
    "return_use": "return x + 0",
    "return_or_zero": "return p() or 0",
    "return_or_none": "return p() or None",
    "return_eq": "return p() == 1",
    "return_lambda": "return (lambda: x)()",
    "use": "print(x)",
}

_GUARD_TEST = {
    "is_none": "x is None",
    "not_x": "not x",
    "is_not_none": "x is not None",
    "truthy": "x",
    "walrus_is_none": "(x := p()) is None",
    "walrus_is_not_none": "(x := p()) is not None",
}


def render(block: Block, indent: int = 1) -> list[str]:
    pad = "    " * indent
    lines: list[str] = []
    for s in block:
        k = s[0]
        if k in _SIMPLE:
            lines.append(pad + _SIMPLE[k])
        elif k == "if":
            lines += [pad + "if nxt():", *render(s[1], indent + 1)]
        elif k == "ifelse":
            lines += [pad + "if nxt():", *render(s[1], indent + 1), pad + "else:"]
            lines += render(s[2], indent + 1)
        elif k == "with_suppress":
            lines += [pad + "with contextlib.suppress(ValueError):", *render(s[1], indent + 1)]
        elif k == "try_except":
            lines += [pad + "try:", *render(s[1], indent + 1), pad + "except ValueError:"]
            lines += render(s[2], indent + 1)
        elif k == "try_finally":
            lines += [pad + "try:", *render(s[1], indent + 1), pad + "finally:"]
            lines += render(s[2], indent + 1)
        elif k == "while_true":
            lines += [pad + "while True:", *render(s[1], indent + 1)]
        elif k == "for":
            lines += [pad + "for _ in range(2 if nxt() else 0):", *render(s[1], indent + 1)]
        elif k == "for_else":
            lines += [pad + "for _ in range(2 if nxt() else 0):", *render(s[1], indent + 1)]
            lines += [pad + "else:", *render(s[2], indent + 1)]
        elif k == "guard":
            lines += [pad + f"if {_GUARD_TEST[s[1]]}:", *render(s[2], indent + 1)]
        else:  # pragma: no cover
            raise ValueError(k)
    return lines


D24_HEADER = """import contextlib
import sys


def nxt() -> bool:
    return True


"""

D11_HEADER = """from typing import Optional


def nxt() -> bool:
    return True


def p() -> Optional[int]:
    return 1


"""


def d24_source(body: Block) -> str:
    return D24_HEADER + "def f() -> int:\n" + "\n".join(render(body)) + "\n"


def d11_source(body: Block) -> str:
    # A trailing ``return 0`` removes fall-through, so any None that
    # reaches the caller came from p(), which is D11's question.
    return D11_HEADER + "def f() -> int:\n" + "\n".join(render(body)) + "\n    return 0\n"


def signature(block: Block) -> str:
    """Shape skeleton used to group disagreements."""

    def sig(s: Stmt) -> str:
        if s[0] == "guard":
            return f"guard[{s[1]}]({','.join(sig(c) for c in s[2])})"
        kids = [c for c in s[1:] if isinstance(c, tuple)]
        if not kids:
            return s[0]
        return s[0] + "(" + "|".join(",".join(sig(c) for c in k) for k in kids) + ")"

    return ";".join(sig(s) for s in block)
