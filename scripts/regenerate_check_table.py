"""Phase G11.0 / T12 / F1 closure: regenerate the README structural-checks table.

The README's "structural checks ship today" prose plus per-check
bullet list is auto-derived from the checker registry. The
generator emits the block delimited by:

    <!-- FURQAN_LINT_CHECKS_AUTO_BEGIN -->
    ... auto-generated content ...
    <!-- FURQAN_LINT_CHECKS_AUTO_END -->

A pre-commit hook compares the generator's output against the
README's current content and fails on drift. Editing the table
by hand causes the hook to fail; the contributor's resolution is
to re-run the generator.

The prose count ("Four checks ship today") is derived from the
table length so the count and the table cannot drift apart.

Checker registry source of truth:

* Python adapter: the four Python-language checks documented
  here (D24, D11, return_none_mismatch, additive_only). These
  ship in the v0.3.x core checker pipeline.
* Rust adapter (opt-in [rust]): R3 + D24 + D11.
* Go adapter (opt-in [go]): D24 + D11.
* ONNX adapter (opt-in [onnx]/[onnx-runtime]/[onnx-profile]):
  D24-onnx + opset_compliance + D11-onnx + numpy_divergence +
  score_validity.

The generator emits the Python core list first (the README's
historical structure), followed by an "Optional adapters" subsection
naming the adapter-specific checks.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
BEGIN = "<!-- FURQAN_LINT_CHECKS_AUTO_BEGIN -->"
END = "<!-- FURQAN_LINT_CHECKS_AUTO_END -->"

# Python core checks. Source of truth: keep this in sync with the
# four checkers wired in src/furqan_lint/runner.py and the diff
# path's `additive_only` checker. This is the "checker registry"
# the F1 closure references; the generator owns it.
PYTHON_CHECKS = [
    {
        "id": "D24",
        "title": "all-paths-return",
        "summary": (
            "every control-flow path through a typed function reaches a " "return statement."
        ),
    },
    {
        "id": "D11",
        "title": "status-coverage",
        "summary": (
            "when a function returns ``Optional[X]``, every caller either "
            "propagates the optionality or explicitly handles ``None``. "
            "A caller that silently collapses ``Optional[X]`` into a "
            "non-optional return type is the structural equivalent of "
            "dropping the ``Incomplete`` arm of Furqan's "
            "``Integrity | Incomplete`` union."
        ),
    },
    {
        "id": "return_none_mismatch",
        "title": "",
        "summary": (
            "a function declaring ``-> str`` (or any non-Optional type) "
            "that returns ``None`` on some path is flagged as a type "
            "mismatch. Closes the D24 return-None blind spot."
        ),
    },
    {
        "id": "additive_only",
        "title": "",
        "summary": (
            "invoked via ``furqan-lint diff old.py new.py``, compares two "
            "versions of a module's public surface and fires on any "
            "removed name. Adding a public name is silent."
        ),
    },
]


def _number_word(n: int) -> str:
    words = {
        1: "One",
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
        6: "Six",
        7: "Seven",
        8: "Eight",
    }
    return words.get(n, str(n))


def render_block() -> str:
    """Produce the auto-derived prose block.

    The block contains a count-prose line ("Four checks ship today")
    derived from len(PYTHON_CHECKS), followed by the per-check
    bullet list. The wrapper sentinels are added by the caller.
    """
    n = len(PYTHON_CHECKS)
    lines = [
        f"{_number_word(n)} core Python checks ship today:",
        "",
    ]
    for c in PYTHON_CHECKS:
        if c["title"]:
            lines.append(f"- **{c['id']} ({c['title']})** {c['summary']}")
        else:
            lines.append(f"- **{c['id']}** {c['summary']}")
    lines.append("")
    lines.append(
        "Adapter-specific checks ship under the optional extras "
        "documented below: ``[rust]`` adds R3 + D24 + D11; ``[go]`` "
        "adds D24 + D11; ``[onnx]`` adds D24-onnx + opset_compliance + "
        "D11-onnx; ``[onnx-runtime]`` adds numpy_divergence; "
        "``[onnx-profile]`` adds score_validity ADVISORY; ``[gate11]`` "
        "adds the Sigstore-CASM Gate 11 verifier (v0.10.0+; an "
        "additive-only contract on the public surface, "
        "cryptographically witnessed via Sigstore Rekor)."
    )
    return "\n".join(lines)


def render_with_sentinels() -> str:
    """Produce the block wrapped in the BEGIN/END sentinels."""
    return f"{BEGIN}\n{render_block()}\n{END}"


def update_readme() -> None:
    """Replace the README's auto-block in place; create it if absent.

    On first run (no sentinels in README), the generator looks for
    the legacy "Four checks ship today" prose and replaces that
    span with the wrapped auto-block. Subsequent runs just update
    the content between the sentinels.
    """
    text = README.read_text(encoding="utf-8")
    new_block = render_with_sentinels()
    if BEGIN in text and END in text:
        prefix, _, rest = text.partition(BEGIN)
        _, _, suffix = rest.partition(END)
        text = prefix + new_block + suffix
    else:
        # Replace the legacy hand-written block. The legacy block
        # starts with "Four checks ship today:" and runs through the
        # `additive_only` bullet's closing line.
        legacy_start = "into idiomatic Python. Four checks ship today:"
        legacy_end_marker = "  removed name. Adding a public name is silent."
        if legacy_start in text and legacy_end_marker in text:
            i = text.index(legacy_start) + len("into idiomatic Python. ")
            j = text.index(legacy_end_marker) + len(legacy_end_marker)
            text = text[:i] + new_block + text[j:]
        else:
            raise SystemExit(
                "could not locate the README check table; expected "
                "either the BEGIN/END sentinels or the legacy "
                "'Four checks ship today' prose"
            )
    README.write_text(text, encoding="utf-8")


def check_no_drift() -> int:
    """Pre-commit-shaped check: returns 0 if the README matches
    the generator's output, 1 otherwise."""
    text = README.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print(
            "README does not contain the FURQAN_LINT_CHECKS_AUTO sentinels. "
            "Run scripts/regenerate_check_table.py to install them.",
            file=sys.stderr,
        )
        return 1
    prefix, _, rest = text.partition(BEGIN)
    actual_inner, _, suffix = rest.partition(END)
    expected = "\n" + render_block() + "\n"
    if actual_inner != expected:
        print(
            "README structural-check block is out of date with the "
            "generator. Run scripts/regenerate_check_table.py and "
            "commit the result.",
            file=sys.stderr,
        )
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=("Regenerate or check the README structural-checks block " "(F1 closure).")
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the README is out of date with the generator",
    )
    args = parser.parse_args()
    if args.check:
        return check_no_drift()
    update_readme()
    print(f"updated {README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
