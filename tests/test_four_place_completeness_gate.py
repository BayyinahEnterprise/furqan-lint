"""Four-place-completeness gate (v0.8.3 round-21 corrective).

For every fixture in ``tests/fixtures/<lang>/documented_limits/``,
asserts the four-place documentation discipline:

  (a) CHANGELOG.md mentions the fixture by stem (substring).
  (b) The fixture's ``documented_limits/README.md`` mentions
      the fixture by stem.
  (c) At least one ``tests/test_*.py`` references the fixture
      by stem.
  (d) The top-level README.md adapter limitations section
      mentions the topic (keyword matching, since the README
      describes by topic rather than by exact filename).

The gate is a single test with an internal loop (per locked
decision 5) so a fresh-instance reviewer reading the test
sees the discipline expressed in one place rather than per-
fixture parametrize entries.

Legacy Go fixtures (v0.8.0-era) are CHANGELOG-described by
topic-keyword rather than by exact filename. They are
explicitly allowlisted in
``_LEGACY_FIXTURES_NO_CHANGELOG_BY_FILENAME`` -- the four-
place discipline is preserved via narrative description but
not by exact-stem search. The allowlist is a v0.8.4
candidate for retirement; new fixtures (v0.8.3+) MUST
reference themselves in CHANGELOG by exact stem.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.unit

# v0.8.0-era Go fixtures: CHANGELOG describes by topic-keyword
# (e.g. "for_statement_opaque" appears in the inventory but
# CHANGELOG narrative says "for/range bodies wrap as may-runs"
# without naming the fixture file). New fixtures (v0.8.3+) must
# reference themselves by exact stem in CHANGELOG; this
# allowlist is a v0.8.4 retirement candidate.
_LEGACY_FIXTURES_NO_CHANGELOG_BY_FILENAME: frozenset[str] = frozenset(
    {
        "defer_statement_opaque",
        "for_statement_opaque",
        "generic_type_parameters",
        "interface_method_dispatch",
        "multi_return_three_or_more",
        "r3_compile_rejected",
        "select_statement_opaque",
        "switch_statement_opaque",
        "two_element_non_error_tuple",
    }
)

# Top-level README adapter-limitations sections describe limits
# by TOPIC keyword rather than by exact fixture filename. For
# each fixture stem, we map to the topic keywords that should
# appear in the top-level README. None means the fixture is
# adapter-internal (no top-level README mention required).
_README_TOPIC_KEYWORDS: dict[str, tuple[str, ...] | None] = {
    # Rust documented_limits.
    "trait_object_return": ("trait-object", "trait object", "trait_object"),
    "lifetime_param_return": ("lifetime", "Lifetime"),
    "closure_with_annotated_return": ("closure", "Closure"),
    "r3_panic_as_tail_expression": ("panic!", "diverging"),
    "impl_methods_omitted": ("impl-block", "impl_methods", "impl-method"),
    # Go documented_limits (legacy + v0.8.1 additions).
    "multi_return_three_or_more": ("multi-return", "3+", "multi_return"),
    "two_element_non_error_tuple": ("non-error", "non_error", "2-element"),
    "for_statement_opaque": ("for", "range"),
    "switch_statement_opaque": ("switch",),
    "select_statement_opaque": ("select",),
    "defer_statement_opaque": ("defer",),
    "interface_method_dispatch": ("Interface method dispatch", "interface dispatch"),
    "generic_type_parameters": ("Generic type parameters", "generic type"),
    "r3_compile_rejected": ("R3 not-applicable", "R3 not_applicable", "compiler rejects"),
    # ONNX documented_limits (v0.9.0).
    "dynamic_shape_silent_pass": ("dim_param", "dynamic shape", "strict_mode"),
    "intermediates_excluded": ("intermediates", "graph.value_info", "intermediate tensor"),
    "registry_pin_window": ("onnx>=1.14", "op registry", "op-registry"),
}


def _list_documented_limit_fixtures() -> list[Path]:
    """Return all fixture files in any
    ``tests/fixtures/<lang>/documented_limits/`` directory,
    excluding README.md."""
    fixtures: list[Path] = []
    for limits_dir in (REPO_ROOT / "tests" / "fixtures").rglob("documented_limits"):
        if not limits_dir.is_dir():
            continue
        for f in sorted(limits_dir.iterdir()):
            if f.is_file() and f.name != "README.md":
                fixtures.append(f)
    return fixtures


def _changelog_mentions_stem(stem: str) -> bool:
    text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    return stem in text


def _limits_readme_mentions_stem(fixture: Path) -> bool:
    readme = fixture.parent / "README.md"
    if not readme.is_file():
        return False
    return fixture.stem in readme.read_text(encoding="utf-8")


def _any_test_references_stem(stem: str) -> bool:
    tests_dir = REPO_ROOT / "tests"
    for test_file in tests_dir.glob("test_*.py"):
        if stem in test_file.read_text(encoding="utf-8"):
            return True
    return False


def _top_readme_mentions_topic(fixture_stem: str) -> bool:
    """Top-level README mentions the topic (keyword match).
    If the fixture has no registered keywords, the gate
    treats it as not-required-to-appear (returns True).
    """
    keywords = _README_TOPIC_KEYWORDS.get(fixture_stem)
    if keywords is None:
        return True
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    return any(kw in text for kw in keywords)


def test_four_place_completeness() -> None:
    """Every documented-limit fixture must have all four
    documentation places populated. Failures collected and
    reported in a single multi-line message.
    """
    failures: list[str] = []
    for fixture in _list_documented_limit_fixtures():
        stem = fixture.stem
        rel = fixture.relative_to(REPO_ROOT)

        # (a) CHANGELOG: skip if in legacy allowlist.
        if stem not in _LEGACY_FIXTURES_NO_CHANGELOG_BY_FILENAME:
            if not _changelog_mentions_stem(stem):
                failures.append(
                    f"{rel}: (a) CHANGELOG.md does not mention "
                    f"'{stem}' by exact stem. New fixtures (v0.8.3+) "
                    f"must reference themselves in CHANGELOG by "
                    f"exact filename."
                )

        # (b) documented_limits/README.md.
        if not _limits_readme_mentions_stem(fixture):
            failures.append(
                f"{rel}: (b) {fixture.parent.name}/README.md does "
                f"not mention '{stem}' in the inventory."
            )

        # (c) Test reference.
        if not _any_test_references_stem(stem):
            failures.append(
                f"{rel}: (c) no tests/test_*.py references the "
                f"fixture stem '{stem}'. Every documented-limit "
                f"fixture must have at least one pinning test."
            )

        # (d) Top-level README.
        if not _top_readme_mentions_topic(stem):
            keywords = _README_TOPIC_KEYWORDS.get(stem) or ()
            failures.append(
                f"{rel}: (d) top-level README.md adapter "
                f"limitations section does not mention any "
                f"keyword for '{stem}' (expected one of: "
                f"{', '.join(repr(k) for k in keywords)})."
            )

    if failures:
        report = "\n".join(f"  {f}" for f in failures)
        pytest.fail(
            f"Four-place documentation discipline incomplete on "
            f"{len(failures)} entries:\n{report}"
        )
