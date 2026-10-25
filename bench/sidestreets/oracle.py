"""Execution oracle: run a generated function on every decision path.

Every ``nxt()`` and ``p()`` call consumes one decision bit. The oracle
enumerates decision sequences depth-first (replay with a prefix,
default 0 beyond it, then branch on each defaulted position), so every
path with at most ``MAX_DECISIONS`` decisions is executed. That bound
is the oracle's declared horizon; paths beyond it are not observed.

Outcomes per path: ``returned`` (value), ``raised`` (exception type),
``diverged`` (budget exhausted).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

MAX_DECISIONS = 12
MAX_RUNS = 4096
STEP_BUDGET = 64
LINE_BUDGET = 2000  # bounds loops that never consume a decision (while True: pass)


class _Budget(Exception):
    pass


@dataclass
class Truth:
    returns_none: bool = False  # some path returns None
    producer_none: bool = False  # ...and that None disappears when p() never returns None
    none_crash: bool = False  # some path raises TypeError/AttributeError (None misuse)
    producer_crash: bool = False  # ...and that crash disappears when p() never returns None
    invalid: bool = False  # NameError / UnboundLocalError / SyntaxError: not a valid specimen
    runs: int = 0
    truncated: bool = False  # hit MAX_RUNS or MAX_DECISIONS somewhere
    witness: list[int] | None = field(default=None)  # decisions of a None-returning path


def run(source: str, fname: str = "f") -> Truth:  # noqa: PLR0915  (one replay loop, kept whole)
    truth = Truth()
    try:
        code = compile(source, "<specimen>", "exec")
    except SyntaxError:
        truth.invalid = True
        return truth

    state: dict = {"bits": [], "i": 0, "steps": 0, "kinds": [], "force_p": False}

    def take(kind: str) -> int:
        state["steps"] += 1
        if state["steps"] > STEP_BUDGET:
            raise _Budget
        i = state["i"]
        state["i"] += 1
        state["kinds"].append(kind)
        bits = state["bits"]
        bit = bits[i] if i < len(bits) else 0
        if kind == "p" and state["force_p"]:
            return 0
        return bit

    ns: dict = {}
    exec(code, ns)
    ns["nxt"] = lambda: bool(take("nxt"))
    ns["p"] = lambda: None if take("p") else 1

    def counterfactual(prefix: list[int]) -> bool:
        """Same decisions, but every p() returns 1. True when the None
        result goes away, i.e. the None came from the producer."""
        state.update(bits=prefix, i=0, steps=0, kinds=[], force_p=True)
        try:
            return call(fn) is not None
        except BaseException:
            return True  # the None path no longer returns None
        finally:
            state["force_p"] = False

    ns["print"] = lambda *a, **k: None
    fn = ns[fname]
    code_obj = fn.__code__
    lines = {"n": 0}

    def tracer(frame, event, arg):
        if frame.f_code is not code_obj:
            return None

        def local(frame, event, arg):
            if event == "line":
                lines["n"] += 1
                if lines["n"] > LINE_BUDGET:
                    raise _Budget
            return local

        return local

    def call(f):
        lines["n"] = 0
        sys.settrace(tracer)
        try:
            return f()
        finally:
            sys.settrace(None)

    stack: list[list[int]] = [[]]
    while stack:
        if truth.runs >= MAX_RUNS:
            truth.truncated = True
            break
        prefix = stack.pop()
        state.update(bits=prefix, i=0, steps=0, kinds=[])
        truth.runs += 1
        consumed = 0
        try:
            value = call(fn)
            consumed = state["i"]
            if value is None:
                truth.returns_none = True
                if counterfactual(list(prefix)) and not truth.producer_none:
                    truth.producer_none = True
                    truth.witness = list(prefix)
        except _Budget:
            pass
        except (NameError, UnboundLocalError):
            truth.invalid = True
            return truth
        except (TypeError, AttributeError):
            truth.none_crash = True
            consumed = state["i"]
            if not truth.producer_crash and _crash_gone(state, fn, list(prefix)):
                truth.producer_crash = True
        except (ValueError, KeyError, SystemExit):
            pass
        if not consumed:  # exception paths: the counterfactual never ran
            consumed = state["i"]
        if consumed > MAX_DECISIONS:
            truth.truncated = True
            consumed = MAX_DECISIONS
        for j in range(len(prefix), consumed):
            stack.append(_branch(prefix, j))
    return truth


def _branch(prefix: list[int], j: int) -> list[int]:
    """Decision sequence equal to the defaulted run up to position j, then 1."""
    return prefix + [0] * (j - len(prefix)) + [1]


def _crash_gone(state: dict, fn, prefix: list[int]) -> bool:
    """Same decisions with every p() returning 1: does the crash vanish?"""
    state.update(bits=prefix, i=0, steps=0, kinds=[], force_p=True)
    try:
        fn()
        return True
    except (TypeError, AttributeError):
        return False
    except BaseException:
        return True
    finally:
        state["force_p"] = False
