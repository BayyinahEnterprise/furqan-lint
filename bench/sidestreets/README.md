# Side-street map

An exhaustive small-scope check of furqan-lint's D24 and D11 verdicts
against execution.

1. **Enumerate.** `grammar.py` builds every function body with at most N
   statements from a grammar of Python control flow (`if`, `for`,
   `while True`, `try` / `except` / `finally`, `with`, `return`,
   `raise`, `sys.exit`, `break`, `continue`, None guards, walrus,
   closures). Every condition reads a fresh decision bit from `nxt()`,
   and the Optional producer `p()` reads one too, so conditions are
   independent and every structural path is reachable.
2. **Execute.** `oracle.py` runs each function on every decision path
   (depth-first replay) and records the truth. For D24 the truth is
   whether some path falls through and returns None. For D11 it is
   whether a None *from `p()`* reaches the caller: a counterfactual
   rerun with `p()` never returning None separates the producer's None
   from a literal `None`, which is outside D11's question.
3. **Compare.** `verdict.py` runs furqan-lint (module API with the
   source tree, so R3 runs too). `run_map.py` writes every disagreement,
   with its source, to an append-only JSONL ledger.

## Declared horizon

* Programs with at most N statements (N is a parameter).
* At most 12 decisions per path, at most 4096 paths per program, and
  at most 2000 executed lines per run (bounds `while True` loops that
  never consume a decision). Programs that hit a bound are counted as
  `truncated`, never as agreeing.
* Beyond that horizon nothing is claimed.

## Run

    PYTHONPATH=src python -m sidestreets.run_map d11 --max-size 4 --out OUT   # from bench/

## Gate

`tests/test_side_street_map.py` runs the map inside the test suite:
D11 must have zero false negatives (size 3 always, size 4 under
`slow`), and every D24 false negative must be a documented limit.

## Evidence that it sees

On D11 up to 4 statements (17,053 programs) the map reports 1,768
false negatives for the first v1.0.1 cut (`83ec189`), 32 for `df7f99d`
(the class the external audit reported as F-01), and 0 from `f7c7282`
on. At 5 statements (423,099 programs) it reports 2 for `f7c7282`, the
exact leak the first independent review round found by hand (a guard's
`raise` caught by an enclosing `except`), and 0 for the release.
