"""End-to-end checker tests.

Each test runs the full pipeline (translate -> run checks) on a fixture
or inline source and asserts the expected diagnostic shape.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from furqan.errors.marad import Advisory, Marad

from furqan_lint.adapter import translate_file, translate_source
from furqan_lint.runner import check_python_module


def _marads(diagnostics: list) -> list:
    return [d for _, d in diagnostics if isinstance(d, Marad)]


def _by_checker(diagnostics: list, name: str) -> list:
    return [d for n, d in diagnostics if n == name]


# ---------------------------------------------------------------------------
# D24 - all-paths-return
# ---------------------------------------------------------------------------

def test_simple_function_passes_d24(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "simple_function.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []


def test_if_else_both_return_passes_d24(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "if_else_both_return.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []


def test_missing_return_path_fires_d24(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "missing_return_path.py")
    diags = check_python_module(module)
    d24 = _by_checker(diags, "all_paths_return")
    assert len(d24) == 1
    assert isinstance(d24[0], Marad)


def test_nested_missing_return_fires_d24(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "nested_missing_return.py")
    diags = check_python_module(module)
    d24 = _by_checker(diags, "all_paths_return")
    assert len(d24) == 1


def test_function_without_return_type_skipped_d24() -> None:
    """D24 has no contract on functions without a declared return type."""
    src = (
        "def f(x):\n"
        "    if x:\n"
        "        return 1\n"
    )
    module = translate_source(src, "<test>")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []


def test_return_none_satisfies_d24_path_coverage() -> None:
    """``return None`` is a return statement and therefore still
    satisfies D24's path coverage. The type mismatch is caught by
    the v0.2.0 ``return_none_mismatch`` checker, not by D24. This
    test pins both halves of that contract: D24 stays silent;
    return_none_mismatch fires."""
    src = (
        "def f(x: int) -> str:\n"
        "    if x:\n"
        "        return 'yes'\n"
        "    return None\n"
    )
    module = translate_source(src, "<test>")
    diags = check_python_module(module)
    assert _by_checker(diags, "all_paths_return") == []
    assert len(_by_checker(diags, "return_none_mismatch")) == 1


# ---------------------------------------------------------------------------
# D11 - status-coverage
# ---------------------------------------------------------------------------

def test_optional_propagated_passes_d11(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "optional_propagated.py")
    diags = check_python_module(module)
    assert _by_checker(diags, "status_coverage") == []


def test_status_collapse_fires_d11(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "status_collapse.py")
    diags = check_python_module(module)
    s = _by_checker(diags, "status_coverage")
    assert len(s) >= 1
    assert any(isinstance(d, Marad) for d in s)


def test_multiple_collapses_fire_per_call_site(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "multiple_collapses.py")
    diags = check_python_module(module)
    s = _by_checker(diags, "status_coverage")
    marads = [d for d in s if isinstance(d, Marad)]
    assert len(marads) == 2


def test_function_calling_non_optional_passes_d11() -> None:
    src = (
        "def helper() -> int:\n"
        "    return 1\n"
        "def caller() -> int:\n"
        "    return helper()\n"
    )
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


def test_cli_check_clean_file_returns_0(clean_dir: Path) -> None:
    result = _run_cli("check", str(clean_dir / "simple_function.py"))
    assert result.returncode == 0


def test_cli_check_failing_file_returns_1(failing_dir: Path) -> None:
    result = _run_cli("check", str(failing_dir / "missing_return_path.py"))
    assert result.returncode == 1


def test_cli_check_directory_scans_all_py_files(clean_dir: Path) -> None:
    result = _run_cli("check", str(clean_dir))
    assert result.returncode == 0
    # Each clean fixture should have produced a PASS line.
    py_count = len(list(clean_dir.glob("*.py")))
    assert result.stdout.count("PASS") == py_count


def test_cli_directory_excludes_venv_and_pycache(tmp_path: Path) -> None:
    """A ``.venv`` directory under the scan target must not be walked."""
    (tmp_path / "good.py").write_text(
        "def f() -> int:\n    return 1\n", encoding="utf-8"
    )
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "broken.py").write_text(
        "def bad(x: int) -> int:\n    if x:\n        return 1\n",
        encoding="utf-8",
    )
    result = _run_cli("check", str(tmp_path))
    assert result.returncode == 0
    assert "broken.py" not in result.stdout


def test_cli_syntax_error_returns_2(tmp_path: Path) -> None:
    bad = tmp_path / "syntax_error.py"
    bad.write_text("def f(:\n", encoding="utf-8")
    result = _run_cli("check", str(bad))
    assert result.returncode == 2
    assert "SYNTAX ERROR" in result.stdout


def test_cli_version_prints_version() -> None:
    from furqan_lint import __version__

    result = _run_cli("version")
    assert result.returncode == 0
    assert __version__ in result.stdout
    assert "furqan-lint" in result.stdout


def test_cli_help_prints_usage() -> None:
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "Usage" in result.stdout


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_file_passes() -> None:
    module = translate_source("", "<empty>")
    diags = check_python_module(module)
    assert diags == []


def test_file_with_no_functions_passes() -> None:
    module = translate_source("X = 1\nY = 2\n", "<noop>")
    diags = check_python_module(module)
    assert diags == []


def test_class_methods_checked() -> None:
    """Methods are extracted as functions, so D24 runs on them too."""
    src = (
        "class C:\n"
        "    def bad(self, x: int) -> int:\n"
        "        if x:\n"
        "            return 1\n"
    )
    module = translate_source(src, "<cls>")
    diags = check_python_module(module)
    assert any(isinstance(d, Marad) for _, d in diags)
