"""ONNX-specific verification gates (3 of v0.9.0's 17 gates):

* ``test_gate_8c_onnx_containment``: static AST scan of
  ``src/furqan_lint/`` confirms ``import onnx`` and
  ``from onnx ...`` appear only in files under
  ``src/furqan_lint/onnx_adapter/``. Round-24 finding m5
  closure: the assertion is exact-AST, not a naive grep, so
  comments and docstring mentions of "onnx" do not false-fire.
* ``test_gate_9c_onnx_missing_extras``: simulates the
  ``[onnx]`` extra missing from the install. The CLI raises
  ``OnnxExtrasNotInstalled`` (subclass of ``ImportError``)
  with the install hint as its message.
* ``test_gate_changelog_math_v0_9_0``: pre-flight check that
  the v0.9.0 release commit (when it lands) will write a
  CHANGELOG ``### Tests`` block whose stated total matches the
  empirical ``pytest --collect-only`` count.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src" / "furqan_lint"


def _walks_python_source_files(root: Path):
    """Yield every ``.py`` file under ``root`` (excluding caches)."""
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


def test_gate_8c_onnx_containment() -> None:
    """``import onnx`` / ``from onnx ...`` appear only in files
    under ``src/furqan_lint/onnx_adapter/``.

    Implementation: AST-walk every ``.py`` file under
    ``src/furqan_lint/``; flag ``Import``/``ImportFrom`` nodes
    whose module is ``onnx`` (or a submodule) AND whose source
    file is NOT under ``src/furqan_lint/onnx_adapter/``.

    Round-24 finding m5 closure: the assertion uses ``ast``,
    not a naive grep, so prose mentions of ``onnx`` in
    comments or docstrings do not false-fire.
    """
    onnx_adapter_dir = SRC_ROOT / "onnx_adapter"
    violations: list[tuple[Path, int, str]] = []

    for source_file in _walks_python_source_files(SRC_ROOT):
        if onnx_adapter_dir in source_file.parents:
            continue  # the adapter is the one place onnx may be imported.
        try:
            tree = ast.parse(source_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "onnx" or alias.name.startswith("onnx."):
                        violations.append((source_file, node.lineno, f"import {alias.name}"))
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None and (
                    node.module == "onnx" or node.module.startswith("onnx.")
                ):
                    violations.append((source_file, node.lineno, f"from {node.module} import ..."))

    assert not violations, (
        f"onnx imports leaked outside src/furqan_lint/onnx_adapter/: "
        f"{[(str(p.relative_to(REPO_ROOT)), ln, kind) for p, ln, kind in violations]}"
    )


def test_gate_9c_onnx_missing_extras(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the [onnx] extra is missing, parse_model raises
    ``OnnxExtrasNotInstalled`` (subclass of ``ImportError``)
    with the canonical install hint."""
    from furqan_lint.onnx_adapter import OnnxExtrasNotInstalled

    # Force the lazy ``import onnx`` inside parser to fail.
    monkeypatch.setitem(sys.modules, "onnx", None)
    import importlib

    import furqan_lint.onnx_adapter.parser as parser_mod

    importlib.reload(parser_mod)
    try:
        with pytest.raises(OnnxExtrasNotInstalled) as exc:
            parser_mod.parse_model("ignored.onnx")
        assert "pip install furqan-lint[onnx]" in str(exc.value)
        assert isinstance(exc.value, ImportError)
    finally:
        # Restore the real onnx for downstream tests in the same session.
        try:
            import onnx as _real_onnx

            monkeypatch.setitem(sys.modules, "onnx", _real_onnx)
        except ImportError:
            monkeypatch.delitem(sys.modules, "onnx", raising=False)
        importlib.reload(parser_mod)


def test_gate_changelog_math_v0_9_0() -> None:
    """Pre-flight check for the v0.9.0 release commit (commit 7).

    Asserts that the CHANGELOG either still carries the
    placeholder (commits 2-6 in flight) OR that the populated
    v0.9.0 entry's stated total matches ``pytest --collect-only``.
    During commits 2-6 the latest entry's header is
    ``## [0.9.0] - <DATE>`` and the ### Tests block contains
    ``-> <TBD>`` markers; the gate skips. After commit 7 the
    placeholder is replaced with empirical values; the gate
    asserts equality.
    """
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    entry_match = re.search(r"^## \[([^\]]+)\]", changelog, re.MULTILINE)
    assert entry_match, "CHANGELOG missing a top-level version entry"
    latest_version = entry_match.group(1)
    if latest_version != "0.9.0":
        pytest.skip(f"latest CHANGELOG entry is {latest_version}, not 0.9.0")

    # Find the v0.9.0 entry text.
    start = entry_match.start()
    next_entry = re.search(r"^## \[", changelog[start + 1 :], re.MULTILINE)
    end = (start + 1 + next_entry.start()) if next_entry else len(changelog)
    block = changelog[start:end]

    # In-flight markers ONLY in the entry header (## [v] - <DATE>)
    # or the canonical "-> <TBD>" arithmetic. Backtick-quoted prose
    # references to the literal strings (release bodies that
    # describe the placeholder mechanism) do NOT count; mirrors
    # tests/test_changelog_math_gate.py lines 54-82.
    if re.search(r"^## \[[^\]]+\] - <DATE>", block, re.MULTILINE):
        pytest.skip("v0.9.0 CHANGELOG entry still has <DATE> in header")
    if re.search(r"->\s*<TBD>", block):
        pytest.skip("v0.9.0 CHANGELOG entry still has -> <TBD> in Tests block")
    if re.search(r"Net delta:\s*<TBD>", block):
        pytest.skip("v0.9.0 CHANGELOG entry still has Net delta: <TBD>")

    # Populated form: parse the canonical "Test count: X (...) -> Y (...). Net delta: +Z" sentence.
    m = re.search(
        r"Test count:\s*(\d+)\s*\([^)]+\)\s*->\s*(\d+)\s*\([^)]+\)\.\s*" r"Net delta:\s*\+(\d+)",
        block,
        re.IGNORECASE | re.DOTALL,
    )
    assert m, (
        f"v0.9.0 CHANGELOG entry missing the canonical 'Test count: X -> Y. "
        f"Net delta: +Z' sentence; block:\n{block}"
    )
    stated_y = int(m.group(2))

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    count_match = re.search(r"(\d+)\s+tests?\s+collected", result.stdout)
    assert count_match, f"could not parse pytest --collect-only output:\n{result.stdout}"
    empirical = int(count_match.group(1))
    assert stated_y == empirical, (
        f"v0.9.0 CHANGELOG states {stated_y} tests; pytest collected "
        f"{empirical}. Reconcile before tagging."
    )
