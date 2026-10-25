"""End-to-end checker tests.

Each test runs the full pipeline (translate -> run checks) on a fixture
or inline source and asserts the expected diagnostic shape.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest
from furqan.errors.marad import Marad

from furqan_lint.adapter import translate_file, translate_source
from furqan_lint.runner import check_python_module


def _marads(diagnostics: list) -> list:
    return [d for _, d in diagnostics if isinstance(d, Marad)]


def _by_checker(diagnostics: list, name: str) -> list:
    return [d for n, d in diagnostics if n == name]


# ---------------------------------------------------------------------------
# D24 - all-paths-return
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_simple_function_passes_d24(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "simple_function.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []


@pytest.mark.unit
def test_if_else_both_return_passes_d24(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "if_else_both_return.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []


@pytest.mark.unit
def test_missing_return_path_fires_d24(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "missing_return_path.py")
    diags = check_python_module(module)
    d24 = _by_checker(diags, "all_paths_return")
    assert len(d24) == 1
    assert isinstance(d24[0], Marad)


@pytest.mark.unit
def test_raise_terminal_paths_pass_d24(clean_dir: Path) -> None:
    """v1.0.1: ``raise`` / ``sys.exit`` / ``os._exit`` end a path;
    they are not a fall-through (raise-terminal false positive)."""
    module = translate_file(clean_dir / "raise_terminal_paths.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []


@pytest.mark.unit
def test_raise_branch_with_fall_through_still_fires_d24(failing_dir: Path) -> None:
    """v1.0.1 true-positive guard: a raising branch must not mask a
    sibling path that falls through."""
    module = translate_file(failing_dir / "raise_branch_with_fall_through.py")
    diags = check_python_module(module)
    d24 = _by_checker(diags, "all_paths_return")
    assert len(d24) == 1
    assert "classify" in str(d24[0])


@pytest.mark.unit
def test_zero_return_function_with_raise_is_not_double_reported() -> None:
    """v1.0.1: a function with no explicit ``return`` stays in R3's
    jurisdiction; modelling ``raise`` as terminal must not make D24
    report it as well."""
    source = "def f(x: int) -> int:\n" "    if x:\n" "        raise ValueError(x)\n"
    diags = check_python_module(translate_source(source), ast.parse(source))
    assert _by_checker(diags, "all_paths_return") == []
    assert len(_by_checker(diags, "zero_return_path")) == 1


@pytest.mark.unit
def test_nested_missing_return_fires_d24(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "nested_missing_return.py")
    diags = check_python_module(module)
    d24 = _by_checker(diags, "all_paths_return")
    assert len(d24) == 1


@pytest.mark.unit
def test_function_without_return_type_skipped_d24() -> None:
    """D24 has no contract on functions without a declared return type."""
    src = "def f(x):\n    if x:\n        return 1\n"
    module = translate_source(src, "<test>")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []


@pytest.mark.unit
def test_return_none_satisfies_d24_path_coverage() -> None:
    """``return None`` is a return statement and therefore still
    satisfies D24's path coverage. The type mismatch is caught by
    the v0.2.0 ``return_none_mismatch`` checker, not by D24. This
    test pins both halves of that contract: D24 stays silent;
    return_none_mismatch fires."""
    src = "def f(x: int) -> str:\n    if x:\n        return 'yes'\n    return None\n"
    module = translate_source(src, "<test>")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []
    assert len(_by_checker(diags, "return_none_mismatch")) == 1


# ---------------------------------------------------------------------------
# D11 - status-coverage
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_optional_propagated_passes_d11(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "optional_propagated.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "status_coverage") == []


@pytest.mark.unit
def test_optional_narrowed_at_call_site_passes_d11(clean_dir: Path) -> None:
    """v1.0.1: an explicitly handled None arm is not a status
    collapse (None-guard, ``or`` default, rebind, walrus, ``==``)."""
    module = translate_file(clean_dir / "optional_narrowed_at_call_site.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "status_coverage") == []
    assert _by_checker(diags, "all_paths_return") == []


@pytest.mark.unit
def test_optional_collapse_still_reported_d11(failing_dir: Path) -> None:
    """v1.0.1 true-positive guard: unhandled None arms still fire,
    one diagnostic per function. Includes the review-round shapes that
    resemble a guard but let None out (``break`` / ``continue`` out of
    a loop, ``return x`` in the None branch, ``or None``, rebinding to
    None, a closure read after the guard) and the v1.0.1 audit F-01
    shapes (a nested ``return x`` before the rebind or the raise)."""
    module = translate_file(failing_dir / "optional_collapse_still_reported.py")
    diags = check_python_module(module)
    s = _by_checker(diags, "status_coverage")
    expected = sorted(
        [
            "leaky",
            "late_guard",
            "ordered",
            "guard_without_exit",
            "has_letter_a",
            "in_alphabet",
            "break_leaks",
            "walrus_continue_leaks",
            "returns_the_none",
            "or_none_default",
            "rebinds_to_none",
            "closure_reads_after_guard",
            "nested_return_before_rebind",
            "nested_return_before_raise",
            "walrus_nested_return_before_raise",
        ]
    )
    named = sorted(name for name in expected if any(f"function '{name}'" in str(d) for d in s))
    assert named == expected
    assert len(s) == len(expected)


@pytest.mark.unit
def test_generators_and_procedures_have_no_return_contract(clean_dir: Path) -> None:
    """v1.0.1: generators and ``-> None`` procedures are translated
    without a value-return contract, so D24 and D11 stay silent."""
    module = translate_file(clean_dir / "generator_and_procedure_shapes.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []
    assert _by_checker(diags, "status_coverage") == []
    by_name = {fn.name: fn for fn in module.functions}
    for name in ("evens", "chained", "record"):
        assert by_name[name].return_type is None


@pytest.mark.unit
def test_procedure_calling_optional_producer_is_advisory_not_error() -> None:
    """v1.0.1: a ``-> None`` procedure that calls an Optional producer
    cannot collapse a status into its return value. D11 used to report
    an S1 error here; it now emits only its informational S2 advisory
    (exit 0), the shape upstream designed for effectful functions."""
    source = (
        "from typing import Optional\n"
        "def find_name(uid: int) -> Optional[str]:\n"
        "    return 'alice' if uid == 1 else None\n"
        "def log_name(uid: int) -> None:\n"
        "    name = find_name(uid)\n"
        "    print(name)\n"
    )
    s = _by_checker(check_python_module(translate_source(source)), "status_coverage")
    assert len(s) == 1
    assert not isinstance(s[0], Marad)
    assert "S2" in str(s[0])


@pytest.mark.unit
def test_status_collapse_fires_d11(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "status_collapse.py")
    diags = check_python_module(module)
    s = _by_checker(diags, "status_coverage")
    assert len(s) >= 1
    assert any(isinstance(d, Marad) for d in s)


@pytest.mark.unit
def test_multiple_collapses_fire_per_call_site(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "multiple_collapses.py")
    diags = check_python_module(module)
    s = _by_checker(diags, "status_coverage")
    marads = [d for d in s if isinstance(d, Marad)]
    assert len(marads) == 2


@pytest.mark.unit
def test_function_calling_non_optional_passes_d11() -> None:
    src = "def helper() -> int:\n    return 1\ndef caller() -> int:\n    return helper()\n"
    module = translate_source(src, "<test>")
    diags = check_python_module(module)
    assert _by_checker(diags, "status_coverage") == []


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


@pytest.mark.integration
def test_cli_check_clean_file_returns_0(clean_dir: Path) -> None:
    result = _run_cli("check", str(clean_dir / "simple_function.py"))
    assert result.returncode == 0


@pytest.mark.integration
def test_cli_check_failing_file_returns_1(failing_dir: Path) -> None:
    result = _run_cli("check", str(failing_dir / "missing_return_path.py"))
    assert result.returncode == 1


@pytest.mark.integration
def test_cli_check_directory_scans_all_py_files(clean_dir: Path) -> None:
    result = _run_cli("check", str(clean_dir))
    assert result.returncode == 0
    # Each clean fixture should have produced a PASS line.
    py_count = len(list(clean_dir.glob("*.py")))
    assert result.stdout.count("PASS") == py_count


@pytest.mark.integration
def test_cli_directory_excludes_venv_and_pycache(tmp_path: Path) -> None:
    """A ``.venv`` directory under the scan target must not be walked."""
    (tmp_path / "good.py").write_text("def f() -> int:\n    return 1\n", encoding="utf-8")
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "broken.py").write_text(
        "def bad(x: int) -> int:\n    if x:\n        return 1\n",
        encoding="utf-8",
    )
    result = _run_cli("check", str(tmp_path))
    assert result.returncode == 0
    assert "broken.py" not in result.stdout


@pytest.mark.integration
def test_cli_syntax_error_returns_2(tmp_path: Path) -> None:
    bad = tmp_path / "syntax_error.py"
    bad.write_text("def f(:\n", encoding="utf-8")
    result = _run_cli("check", str(bad))
    assert result.returncode == 2
    assert "SYNTAX ERROR" in result.stdout


@pytest.mark.integration
def test_cli_version_prints_version() -> None:
    from furqan_lint import __version__

    result = _run_cli("version")
    assert result.returncode == 0
    assert __version__ in result.stdout
    assert "furqan-lint" in result.stdout


@pytest.mark.integration
def test_cli_help_prints_usage() -> None:
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "Usage" in result.stdout


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_empty_file_passes() -> None:
    module = translate_source("", "<empty>")
    diags = check_python_module(module)
    assert diags == []


@pytest.mark.unit
def test_file_with_no_functions_passes() -> None:
    module = translate_source("X = 1\nY = 2\n", "<noop>")
    diags = check_python_module(module)
    assert diags == []


@pytest.mark.unit
def test_class_methods_checked() -> None:
    """Methods are extracted as functions, so D24 runs on them too."""
    src = "class C:\n    def bad(self, x: int) -> int:\n        if x:\n            return 1\n"
    module = translate_source(src, "<cls>")
    diags = check_python_module(module)
    assert any(isinstance(d, Marad) for _, d in diags)


@pytest.mark.unit
def test_audit_f01_nested_return_before_rebind_fires_d11_via_module_api() -> None:
    """v1.0.1 audit F-01 reproduction, verbatim, through the module API
    with the source tree supplied (all four checkers run). The None
    branch rebinds ``name`` only after a nested ``return name``, so the
    None escapes on the ``early`` path and D11 must report it."""
    source = (
        "from typing import Optional\n"
        "\n"
        "def find_name(uid: int) -> Optional[str]:\n"
        "    return None\n"
        "\n"
        "def leak(uid: int, early: bool) -> str:\n"
        "    name = find_name(uid)\n"
        "    if name is None:\n"
        "        if early:\n"
        "            return name\n"
        '        name = "fallback"\n'
        "    return name\n"
    )
    namespace: dict = {}
    exec(compile(source, "<f01>", "exec"), namespace)
    assert namespace["leak"](1, True) is None  # the leak is real
    diags = check_python_module(translate_source(source), ast.parse(source))
    s = _by_checker(diags, "status_coverage")
    assert len(s) == 1
    assert isinstance(s[0], Marad)
    assert "function 'leak'" in str(s[0])


@pytest.mark.integration
def test_audit_f01_guard_fixture_fires_through_cli(failing_dir: Path) -> None:
    """The F-01 guard cases fire through the real CLI entry point."""
    result = _run_cli("check", str(failing_dir / "optional_collapse_still_reported.py"))
    assert result.returncode == 1
    for name in (
        "nested_return_before_rebind",
        "nested_return_before_raise",
        "walrus_nested_return_before_raise",
    ):
        assert f"[status_coverage] function '{name}'" in result.stdout


@pytest.mark.unit
def test_every_python_fixture_compiles() -> None:
    """v1.0.1 audit F-02: every Python specimen the suite reasons about
    must be valid, compilable Python, not merely parseable. ``ast.parse``
    accepts some code that ``compile`` rejects (for example ``return``
    inside ``except*``), and a verdict on code that cannot run is not
    evidence about code that can."""
    fixtures = sorted((REPO_ROOT / "tests" / "fixtures").rglob("*.py"))
    assert fixtures
    for path in fixtures:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
