"""Side-street map gate (v1.0.2).

Runs the exhaustive small-scope map in ``bench/sidestreets`` (see its
README) and holds furqan-lint to it:

* D11: zero false negatives. Every program in which a None from the
  Optional producer reaches the caller's return value must be reported.
* D24: every false negative must be the documented limit
  ``terminal_recognition_false_negatives`` (a ``raise`` swallowed by
  ``contextlib.suppress``).

A self-test proves the map can see: with a verdict that reports
nothing, the D11 leaks surface as false negatives.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

FULL_MAP = pytest.mark.skipif(
    os.environ.get("FURQAN_LINT_SIDE_STREET_MAP") != "1",
    reason="size-4 map (~90s) runs in the CI test-full job; set FURQAN_LINT_SIDE_STREET_MAP=1",
)

BENCH = Path(__file__).resolve().parents[1] / "bench"
sys.path.insert(0, str(BENCH))

from sidestreets import run_map  # noqa: E402


def _summary(records: list[dict]) -> str:
    return "\n\n".join(r["src"].split("def f() -> int:\n")[1] for r in records[:3])


@pytest.mark.unit
def test_d11_map_size_3_has_no_false_negatives() -> None:
    counts, records = run_map.run_serial("d11", 3)
    fn = [r for r in records if r["cls"] in ("FN", "crash_silent")]
    assert counts["agree"] > 0
    assert not fn, f"D11 misses {len(fn)} producer-None leaks, e.g.:\n" + _summary(fn)


@pytest.mark.slow
@FULL_MAP
def test_d11_map_size_4_has_no_false_negatives() -> None:
    counts, records = run_map.run_serial("d11", 4)
    fn = [r for r in records if r["cls"] in ("FN", "crash_silent")]
    assert sum(counts[k] for k in counts if k != "truncated") > 17000
    assert not fn, f"D11 misses {len(fn)} producer-None leaks, e.g.:\n" + _summary(fn)


@pytest.mark.slow
@FULL_MAP
def test_d24_map_size_4_false_negatives_are_documented() -> None:
    _, records = run_map.run_serial("d24", 4)
    fn = [r for r in records if r["cls"] == "FN"]
    undocumented = [r for r in fn if "contextlib.suppress" not in r["src"]]
    assert fn, "expected the documented suppress limit to appear"
    assert not undocumented, "undocumented D24 misses, e.g.:\n" + _summary(undocumented)


@pytest.mark.unit
def test_map_sees_leaks_when_the_linter_is_blind(monkeypatch: pytest.MonkeyPatch) -> None:
    """Self-test: replace furqan-lint's verdict with one that flags
    nothing; the oracle alone must then expose the D11 leaks."""
    from sidestreets import verdict

    monkeypatch.setattr(
        verdict,
        "verdict",
        lambda src, fname="f": dict.fromkeys(
            ("d24", "r3", "d11", "d11_note", "return_none"), False
        ),
    )
    _, records = run_map.run_serial("d11", 2)
    assert any(r["cls"] == "FN" for r in records)
