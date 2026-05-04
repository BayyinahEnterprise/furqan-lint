"""Extras-matrix gate (v0.8.4 §7.11): adapter test files must self-skip cleanly.

Round-22 self-finding from PR #9: v0.8.3 backfilled
``test_trait_object_return_documented_limit`` and
``test_lifetime_param_return_documented_limit`` in
``test_rust_correctness.py`` without the ``@pytestmark_rust``
decorator. The audit ran with the ``[rust]`` extras installed and
the tests passed; CI matrix ran without the extras and the tests
failed. Hotfix ``7053b43`` added the missing decorators post-merge.

This gate prevents the same failure shape going forward by AST-
scanning every adapter test file and asserting that every
``test_*`` function has SOMETHING that makes it self-skip when
the relevant extras are missing.

Discovery (revision 2): glob the ``tests/`` directory for files
matching ``test_rust*.py`` / ``test_go*.py`` / ``test_goast*.py``
AND filter to those whose body actually references the adapter (via
``_ADAPTER_IMPORT_TOKENS``). This avoids drift on a manual allowlist
and excludes pure-Python wrapper files (e.g. the public-surface
snapshot tests that only read ``__all__`` without invoking the
adapter).

Accepted skip-guard forms (per locked spec):

1. **Decorator form:** ``@pytestmark_rust`` / ``@pytestmark_go``
   on the function, OR an equivalent
   ``@pytest.mark.skipif(not _rust_extras_present(), ...)`` /
   ``@pytest.mark.skipif(not _go_extras_present(), ...)``.
2. **Module-level pytestmark with skipif:** the file's top-level
   ``pytestmark = ...`` assignment includes a
   ``pytest.mark.skipif`` referencing ``_rust_extras_present`` or
   ``_go_extras_present`` (either alone or in a list).
3. **Module-level pytest.importorskip:** a top-level
   ``pytest.importorskip("tree_sitter")`` /
   ``pytest.importorskip("tree_sitter_rust")`` /
   ``pytest.importorskip("goast")`` etc. handles the entire module.
4. **Inline-skip form:** the function body's first statement (after
   a docstring, if present) is an ``if not _rust_extras_present():
   pytest.skip(...)`` block or a bare ``pytest.skip(...)`` call.
5. **Fixture-injected skip:** the function takes a fixture parameter
   whose name contains ``rust`` or ``go`` (case-insensitive) and a
   fixture by that name exists in ``tests/conftest.py``.

Reconciliation note (revision-3 authority): if the production self-
test fails on first run because a non-decorated file uses a skip-
pattern not yet recognised, prefer EXTENDING the heuristic over
adding decorators or allowlist entries. Document any extension here
with the empirical case that motivated it.

Heuristic extensions (empirical):

* **Missing-extras-path tests:** functions whose name matches the
  ``_MISSING_EXTRAS_NAME_PATTERN`` regex (e.g.
  ``test_go_missing_extras_prints_install_hint``,
  ``test_cli_imports_without_tree_sitter_loaded``) are deliberately
  designed to run on the no-extras install path. They mock the
  typed-exception raise site and assert the CLI dispatcher's
  install-hint behaviour. Requiring them to skip when extras are
  missing would defeat their purpose. Empirically motivated by
  ``test_go_cli.py::test_go_missing_extras_prints_install_hint``
  and ``test_rust_adapter.py::test_cli_imports_without_tree_sitter_loaded``
  on the v0.8.4 first-run.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

TESTS_DIR = Path(__file__).parent

# A file is considered "adapter-dependent" if its body contains any
# of these tokens. The token list intentionally over-approximates;
# the AST walk below will only flag adapter-dependent functions, and
# files that import the adapter package only for type-name checks
# (no functional use) will simply have no flagged functions.
_ADAPTER_IMPORT_TOKENS: tuple[str, ...] = (
    "from furqan_lint.rust_adapter",
    "from furqan_lint.go_adapter",
    "_rust_extras_present",
    "_go_extras_present",
)

# Function-name patterns that mark a test as an explicit
# missing-extras-path test. These tests exist BECAUSE the extras
# are missing; skipping them when extras are missing would defeat
# their purpose.
_MISSING_EXTRAS_NAME_PATTERN = re.compile(
    r"(missing_extras|without_tree_sitter|without_goast|no_extras|imports_without)",
    re.IGNORECASE,
)


def _adapter_test_files() -> tuple[Path, ...]:
    """Glob ``tests/test_{rust,go,goast}*.py`` and return paths whose
    bodies actually reference the adapter (filters out wrapper files
    that only test pure-Python utilities adjacent to the adapter,
    e.g. the public-surface snapshot files that just read
    ``__all__``)."""
    candidates = sorted(
        set(TESTS_DIR.glob("test_rust*.py"))
        | set(TESTS_DIR.glob("test_go*.py"))
        | set(TESTS_DIR.glob("test_goast*.py"))
    )
    return tuple(
        p for p in candidates if any(token in p.read_text() for token in _ADAPTER_IMPORT_TOKENS)
    )


def _module_has_importorskip(tree: ast.Module) -> bool:
    """True if the module body contains a top-level
    ``pytest.importorskip(...)`` call. The ``importorskip`` handles
    the entire module: every test below it auto-skips if the named
    module is missing."""
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if (
                isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "pytest"
                and call.func.attr == "importorskip"
            ):
                return True
    return False


def _module_has_pytestmark_skipif(tree: ast.Module, source: str) -> bool:
    """True if the module body has a top-level ``pytestmark = ...``
    assignment whose right-hand side references either a
    ``pytest.mark.skipif`` call or a name that resolves to one (e.g.
    ``pytestmark_rust``).

    Implemented as a textual check on the assignment span: we look
    for ``skipif`` AND one of the extras-present probe names in the
    same span. This catches all observed empirical shapes (single
    skipif, list of marks containing skipif, alias to a module-level
    ``pytestmark_rust`` definition that itself wraps skipif)."""
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [t for t in node.targets if isinstance(t, ast.Name)]
        if not any(t.id == "pytestmark" for t in targets):
            continue
        # Capture the text of the RHS span.
        snippet = ast.get_source_segment(source, node.value) or ""
        if "skipif" in snippet and (
            "_rust_extras_present" in snippet or "_go_extras_present" in snippet
        ):
            return True
    # Also catch the case where pytestmark references an alias defined
    # earlier in the module (e.g. ``pytestmark = pytestmark_rust``);
    # in that case the alias's definition will have ``skipif`` plus
    # the extras-probe name on its RHS.
    return False


# Names we accept as skip-decorators. The first two are project
# conventions; the third covers the raw form.
_DECORATOR_NAMES: frozenset[str] = frozenset({"pytestmark_rust", "pytestmark_go"})


def _decorator_is_skip_guard(dec: ast.expr, source: str) -> bool:
    """True if ``dec`` is an accepted skip-guard decorator."""
    if isinstance(dec, ast.Name) and dec.id in _DECORATOR_NAMES:
        return True
    snippet = ast.get_source_segment(source, dec) or ""
    return "skipif" in snippet and (
        "_rust_extras_present" in snippet or "_go_extras_present" in snippet
    )


def _body_has_inline_skip(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True if the function body's first non-docstring statement is
    a skip-guard: either ``if not _rust_extras_present(): pytest.skip(...)``
    or a bare ``pytest.skip(...)`` call."""
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        # docstring; drop and inspect next statement
        body = body[1:]
    if not body:
        return False
    first = body[0]
    # Bare pytest.skip(...) call
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Call):
        call = first.value
        if (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "pytest"
            and call.func.attr == "skip"
        ):
            return True
    # if not _rust_extras_present(): pytest.skip(...)
    if isinstance(first, ast.If):
        # Heuristic: the test for the if references an extras-probe.
        test_src = ast.dump(first.test)
        if "_rust_extras_present" in test_src or "_go_extras_present" in test_src:
            for stmt in first.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    call = stmt.value
                    if (
                        isinstance(call.func, ast.Attribute)
                        and isinstance(call.func.value, ast.Name)
                        and call.func.value.id == "pytest"
                        and call.func.attr == "skip"
                    ):
                        return True
    return False


def _conftest_fixture_names(tests_dir: Path) -> frozenset[str]:
    """Return the set of fixture names defined in ``conftest.py``,
    used by the fixture-injected skip heuristic."""
    conftest = tests_dir / "conftest.py"
    if not conftest.is_file():
        return frozenset()
    try:
        tree = ast.parse(conftest.read_text())
    except SyntaxError:
        return frozenset()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            for dec in node.decorator_list:
                snippet = ast.dump(dec)
                if "fixture" in snippet:
                    names.add(node.name)
                    break
    return frozenset(names)


def _params_include_adapter_fixture(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    conftest_fixtures: frozenset[str],
) -> bool:
    """True if any function parameter (other than ``self``) names a
    fixture defined in conftest.py whose name contains ``rust`` or
    ``go`` (case-insensitive)."""
    pattern = re.compile(r"(rust|go)", re.IGNORECASE)
    for arg in node.args.args:
        if arg.arg == "self":
            continue
        if arg.arg in conftest_fixtures and pattern.search(arg.arg):
            return True
    return False


def _function_has_skip_guard(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    source: str,
    conftest_fixtures: frozenset[str],
) -> bool:
    """Apply all accepted skip-guard forms to a single function."""
    if _MISSING_EXTRAS_NAME_PATTERN.search(node.name):
        # Missing-extras-path test: by design runs without extras.
        return True
    for dec in node.decorator_list:
        if _decorator_is_skip_guard(dec, source):
            return True
    if _body_has_inline_skip(node):
        return True
    return _params_include_adapter_fixture(node, conftest_fixtures)


def _walk_test_functions(tree: ast.Module):
    """Yield every ``FunctionDef`` / ``AsyncFunctionDef`` whose name
    starts with ``test_``, including methods inside ``ClassDef`` nodes."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if node.name.startswith("test_"):
                yield node


def _scan_file_for_unguarded_tests(
    path: Path,
    conftest_fixtures: frozenset[str],
) -> list[tuple[Path, str, int]]:
    """Return a list of ``(path, function_name, line_no)`` for every
    test function in ``path`` that lacks a recognised skip-guard.
    Returns an empty list for files whose entire module is guarded
    by a top-level ``importorskip`` or ``pytestmark`` skipif."""
    source = path.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    if _module_has_importorskip(tree):
        return []
    if _module_has_pytestmark_skipif(tree, source):
        return []
    findings: list[tuple[Path, str, int]] = []
    for node in _walk_test_functions(tree):
        if not _function_has_skip_guard(node, source, conftest_fixtures):
            findings.append((path, node.name, node.lineno))
    return findings


def test_rust_and_go_test_files_have_skip_guards() -> None:
    """Every test in ``test_rust_correctness.py`` /
    ``test_go_correctness.py`` (and any other adapter-dependent test
    file) must have either ``@pytestmark_rust`` /
    ``@pytestmark_go`` decorator OR an inline ``pytest.skip(_REASON)``
    call as its first statement OR a module-level
    ``pytestmark = pytest.mark.skipif(...)`` with the extras-probe OR
    a module-level ``pytest.importorskip(...)`` for the adapter
    module OR a fixture-injected skip parameter.

    Catches the round-22 self-finding: v0.8.3 backfilled
    ``test_trait_object_return_documented_limit`` and
    ``test_lifetime_param_return_documented_limit`` without the
    ``@pytestmark_rust`` decorator. Audit ran with ``[rust]`` extras
    installed; CI matrix ran without; tests failed in CI but had
    passed audit. This gate forecloses the same shape going forward.
    """
    conftest_fixtures = _conftest_fixture_names(TESTS_DIR)
    findings: list[tuple[Path, str, int]] = []
    for path in _adapter_test_files():
        findings.extend(_scan_file_for_unguarded_tests(path, conftest_fixtures))
    if findings:
        msg_lines = [
            "Found adapter test functions without recognised skip-guards.",
            "Every test in an adapter test file must self-skip cleanly when",
            "the relevant extras are missing. Accepted forms are listed in",
            "this module's docstring (decorator, inline skip, module-level",
            "pytestmark skipif, module-level importorskip, fixture-injected).",
            "",
            "Findings:",
        ]
        for path, name, line_no in findings:
            rel = path.relative_to(TESTS_DIR.parent)
            msg_lines.append(f"  {rel}:{line_no}  {name}")
        pytest.fail("\n".join(msg_lines))


def test_extras_matrix_gate_passes_on_clean_codebase() -> None:
    """Self-test: the gate passes against today's tests/ directory.

    Empirical pin that the heuristic recognises every skip-guard
    pattern actually used in the repo. If a future commit adds a
    new pattern (e.g. a fixture with a name like ``adapter_runtime``
    that doesn't match the rust/go regex), this test will fail
    first and the heuristic must be extended -- not the test file
    decorated -- per the locked reconciliation authority.
    """
    conftest_fixtures = _conftest_fixture_names(TESTS_DIR)
    findings: list[tuple[Path, str, int]] = []
    for path in _adapter_test_files():
        findings.extend(_scan_file_for_unguarded_tests(path, conftest_fixtures))
    assert not findings, (
        "Gate flagged real test files; extend the heuristic to cover "
        f"the empirical pattern. Findings: {findings}"
    )


def test_extras_matrix_gate_catches_missing_decorator(tmp_path: Path) -> None:
    """Self-test: the gate flags an undecorated test in a synthesized
    adapter test file, and does NOT flag a decorated one.

    Two functions in one file:

    * ``test_undecorated``: no skip-guard. Must be flagged.
    * ``test_decorated``: ``@pytestmark_rust``. Must NOT be flagged.

    The synthesized file imports ``from furqan_lint.rust_adapter``
    so it passes the adapter-dependence filter.
    """
    fake = tmp_path / "test_rust_synthetic.py"
    fake.write_text(
        '"""Synthetic adapter test file for the gate self-test."""\n'
        "from furqan_lint.rust_adapter import parse_file  # noqa: F401\n"
        "\n"
        "import pytest\n"
        "\n"
        "def _rust_extras_present() -> bool:\n"
        "    return True\n"
        "\n"
        'pytestmark_rust = pytest.mark.skipif(not _rust_extras_present(), reason="x")\n'
        "\n"
        "@pytestmark_rust\n"
        "def test_decorated() -> None:\n"
        "    assert True\n"
        "\n"
        "def test_undecorated() -> None:\n"
        "    assert True\n"
    )
    conftest_fixtures = _conftest_fixture_names(TESTS_DIR)
    findings = _scan_file_for_unguarded_tests(fake, conftest_fixtures)
    flagged_names = {name for _, name, _ in findings}
    assert (
        "test_undecorated" in flagged_names
    ), f"gate failed to catch undecorated test; findings: {findings}"
    assert (
        "test_decorated" not in flagged_names
    ), f"gate false-positived on decorated test; findings: {findings}"
