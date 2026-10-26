"""Side-street map: every small program, executed and linted.

    python -m sidestreets.run_map d11 --max-size 4 --out DIR

For each enumerated function: the execution oracle gives the truth,
furqan-lint gives its verdict, and every disagreement is written to an
append-only JSONL ledger with the source, so any finding replays.

D24 family: truth = "some path falls through" (every explicit return
is ``return 0``, so a None result can only be a fall-through).
Flagged = D24 or R3.
D11 family: truth = "some path returns a None that came from p()"
(a trailing ``return 0`` removes fall-through). Flagged = D11 S1.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from . import grammar, oracle, verdict


def judge(job: tuple[str, tuple]) -> dict:
    family, body = job
    src = grammar.d24_source(body) if family == "d24" else grammar.d11_source(body)
    truth = oracle.run(src)
    if truth.invalid:
        return {"cls": "invalid"}
    try:
        v = verdict.verdict(src)
    except Exception as exc:  # adapter crash is a finding in itself
        return {"cls": "LINT_CRASH", "src": src, "err": repr(exc)}
    if family == "d24":
        flagged = v["d24"] or v["r3"]
        if truth.returns_none and not flagged:
            cls = "FN"
        elif not truth.returns_none and flagged:
            cls = "FP_r3" if (v["r3"] and not v["d24"]) else "FP"
        else:
            cls = "agree"
    else:
        flagged = v["d11"]
        if truth.producer_none and not flagged:
            cls = "FN"
        elif truth.producer_none:
            cls = "agree"
        elif truth.returns_none:
            cls = "literal_none"  # a None not from p(): outside D11's question
        elif truth.producer_crash:
            cls = "crash_flagged" if flagged else "crash_silent"
        elif truth.none_crash:
            cls = "literal_none_crash"  # None misuse not from p()
        elif flagged:
            cls = "FP"
        else:
            cls = "agree"
    out = {"cls": cls, "truncated": truth.truncated, "runs": truth.runs}
    if cls not in ("agree",):
        out.update(src=src, sig=grammar.signature(body), witness=truth.witness, verdict=v)
    return out


def bodies(family: str, max_size: int) -> list[tuple]:
    gen = grammar.d24_functions(max_size) if family == "d24" else grammar.d11_functions(max_size)
    return list(gen)


def run_serial(family: str, max_size: int) -> tuple[Counter[str], list[dict]]:
    """Judge every program in-process. Returns class counts and the
    non-agreeing records (each with its source, so it replays)."""
    counts: Counter[str] = Counter()
    records: list[dict] = []
    for body in bodies(family, max_size):
        r = judge((family, body))
        counts[r["cls"]] += 1
        counts["truncated"] += bool(r.get("truncated"))
        if r["cls"] not in ("agree", "invalid"):
            records.append(r)
    return counts, records


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("family", choices=("d24", "d11"))
    ap.add_argument("--max-size", type=int, default=4)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=mp.cpu_count())
    args = ap.parse_args()

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    import furqan_lint.adapter as a

    progs = bodies(args.family, args.max_size)
    args.out.mkdir(parents=True, exist_ok=True)
    stem = f"{args.family}_n{args.max_size}_{commit}"
    ledger = args.out / f"{stem}.jsonl"
    counts: Counter[str] = Counter()
    truncated = 0
    t0 = time.time()
    with mp.Pool(args.jobs) as pool, ledger.open("w") as fh:
        for r in pool.imap(judge, ((args.family, b) for b in progs), chunksize=256):
            counts[r["cls"]] += 1
            truncated += bool(r.get("truncated"))
            if r["cls"] not in ("agree", "invalid"):
                fh.write(json.dumps(r) + "\n")
    summary = {
        "family": args.family,
        "max_size": args.max_size,
        "commit": commit,
        "adapter": a.__file__,
        "programs": len(progs),
        "counts": dict(counts),
        "truncated": truncated,
        "oracle_horizon": {"max_decisions": oracle.MAX_DECISIONS, "max_runs": oracle.MAX_RUNS},
        "seconds": round(time.time() - t0, 1),
    }
    (args.out / f"{stem}.summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
