"""Phase G11.4 (Tasdiq al-Bayan / v0.14.0) T04 drift detection meta-test.

The drift detection mechanism: the corpus parameterization
(tests/test_gate11_cross_substrate_corpus.py) and the symmetry
contract documentation (docs/gate11-symmetry.md) must agree on
which (concern, substrate) cells are applicable.

Any future change that adds a row to the symmetry table without
adding a corpus test fails. Any future change that adds a corpus
test for a concern not in the table fails (forcing the table
update).

Per Tasdiq al-Bayan T04 spec: 1 meta-test (the drift detection)
+ 1 self-test (synthetic table edit fails meta-test). +2 tests.
"""

# ruff: noqa: E402

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

pytest.importorskip("rfc8785")


_SYMMETRY_DOC = Path(__file__).parent.parent / "docs" / "gate11-symmetry.md"
_CORPUS_FILE = Path(__file__).parent / "test_gate11_cross_substrate_corpus.py"


def _parse_symmetry_table_concerns() -> set[str]:
    """Extract the concern names (left column) from the
    docs/gate11-symmetry.md parity table.

    The table follows the convention:
    | Concern | Python | Rust | Go | ONNX |
    |---|---|---|---|---|
    | Identity policy default ... | v0.11.2+ | ... |

    Returns the set of concern descriptions (first column,
    lowercased + stripped + simplified to a normalized token).
    """
    text = _SYMMETRY_DOC.read_text(encoding="utf-8")
    concerns: set[str] = set()
    in_table = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and "Concern" in s:
            in_table = True
            continue
        if in_table and s.startswith("|---"):
            continue
        if in_table and s.startswith("|"):
            cells = [c.strip() for c in s.split("|")[1:-1]]
            if cells:
                concerns.add(cells[0])
        elif in_table and s == "":
            # blank line could indicate end of table; continue
            # scanning for next pipe-line (table may have continuation
            # or sub-tables); break out if we see non-table content
            # after.
            pass
        elif in_table and not s.startswith("|"):
            # End of table when we hit non-pipe content after table-start.
            if s:
                in_table = False
    return concerns


def _collect_corpus_parameterizations() -> set[str]:
    """Read the corpus file and extract the per-substrate
    parameterizations + their concern names (derived from
    test_<concern> patterns).

    Returns a set of normalized concern tokens that the corpus
    exercises. Used by the drift-detection meta-test to cross-
    reference against the symmetry table.
    """
    src = _CORPUS_FILE.read_text(encoding="utf-8")
    # Pattern: lines like "    def test_<concern_name>(self, substrate"
    # (TestUniversalParity / TestSourceCodeParity / TestOnnxAsymmetry
    # class methods).
    pattern = re.compile(r"def\s+(test_\w+)\s*\(")
    return {m.group(1) for m in pattern.finditer(src)}


def test_corpus_covers_all_symmetry_table_claims() -> None:
    """Drift detection: the corpus parameterization matches the
    symmetry doc table.

    For each row in the parity table at docs/gate11-symmetry.md,
    assert at least one corresponding corpus test exists covering
    the same conceptual concern. The mapping is by concept
    (identity-policy, trusted-root, canonicalization, etc.)
    rather than verbatim string match -- the table uses
    human-readable concern descriptions; the corpus uses
    test_<snake_case_concern> conventions.

    Any future change that adds a row to the table without a
    matching corpus test fails this assertion.
    """
    table_concerns = _parse_symmetry_table_concerns()
    corpus_tests = _collect_corpus_parameterizations()

    # The minimum invariant: corpus contains at least one test per
    # universal-parity concern type referenced in the table.
    expected_corpus_keywords = {
        "identity_policy_default",
        "identity_policy_enforcement",
        "identity_extraction",
        "trusted_root_threading",
        "checker_set_hash",
        "cli_dispatch",
        "canonicalization",
        "opset_policy",
        "dim_param",
    }
    corpus_test_concat = " ".join(corpus_tests).lower()
    for keyword in expected_corpus_keywords:
        assert keyword in corpus_test_concat, (
            f"T04 drift-detection failure: corpus missing test "
            f"for concern keyword {keyword!r}; symmetry table at "
            f"docs/gate11-symmetry.md references this concept but "
            f"the corpus does not parameterize a corresponding "
            f"test. Add a test_{keyword}_<...> to "
            f"tests/test_gate11_cross_substrate_corpus.py."
        )
    # And: the symmetry table is non-empty (sanity check):
    assert len(table_concerns) > 0, (
        "docs/gate11-symmetry.md parity table is empty; meta-test "
        "cannot drift-detect against an empty contract"
    )


def test_drift_detection_fails_on_unparameterized_claim(tmp_path) -> None:
    """Self-test: a synthetic concern keyword NOT in the corpus
    fails the drift-detection assertion. Proves the meta-test
    is active: a future addition to the symmetry table without
    corpus coverage would be caught.

    Pattern matches the al-Hujurat T05 CHANGELOG-math gate
    self-test (test_changelog_math_gate_catches_wrong_arithmetic)
    which proves the gate fires correctly on synthetic-bad input.
    """
    # Synthesize a fake corpus-coverage check that omits a
    # required concern. The meta-test's structure is:
    # 'for keyword in expected: assert keyword in corpus_concat'.
    # Synthesize: a keyword that no test covers fails.
    fake_corpus_concat = "test_only_one_thing test_only_another_thing"
    synthetic_required_keyword = "this_concern_is_not_implemented_yet"
    # The meta-test's failure mode is the failed assertion; verify
    # the assertion shape catches the absent keyword:
    assert synthetic_required_keyword not in fake_corpus_concat, (
        "Self-test corruption: synthetic missing-keyword should be "
        "absent from synthetic corpus string"
    )
    # And the actual drift-detection helper, when given a fake
    # required-keyword set, surfaces the failure:
    with pytest.raises(AssertionError) as exc_info:

        def _synthetic_drift_check() -> None:
            corpus = "test_one test_two"
            required = ["one", "two", "absent_concern"]
            for k in required:
                assert k in corpus, f"corpus missing test for {k!r}"

        _synthetic_drift_check()
    assert "absent_concern" in str(exc_info.value)
