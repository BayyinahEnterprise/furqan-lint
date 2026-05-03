"""Round-10 R3 (ring-close, zero-return) tests.

12 tests covering the firing matrix:

  failing/  - 5 tests asserting R3 fires (one per fixture)
  clean/    - 6 tests asserting R3 stays silent on legitimate
              zero-return shapes
  unit      - 1 test against ``check_zero_return`` directly to
              pin the API shape independent of CLI plumbing.

The companion documented-limit pin (aliased-abstractmethod)
lives in ``tests/test_documented_limits.py`` per the
four-place documentation pattern.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def _run_check(fixture_relpath: str) -> subprocess.CompletedProcess[str]:
    """Run ``furqan-lint check`` on a fixture and capture stdout."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "furqan_lint.cli",
            "check",
            str(FIXTURES / fixture_relpath),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


# ---------------------------------------------------------------------------
# failing/ fixtures: R3 must fire on each
# ---------------------------------------------------------------------------


def test_r3_fires_on_bare_zero_return_function() -> None:
    """The minimal R3 case: ``def f(x: int) -> str: pass``."""
    result = _run_check("failing/zero_return_function.py")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout
    assert "-> str" in result.stdout


def test_r3_fires_on_branching_zero_return() -> None:
    """Branching body, no returns: D24 cannot catch this (D24
    requires >=1 return present), R3 must."""
    result = _run_check("failing/zero_return_with_branches.py")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout


def test_r3_fires_on_async_function() -> None:
    """``AsyncFunctionDef`` is walked the same as ``FunctionDef``."""
    result = _run_check("failing/zero_return_async.py")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'fetch'" in result.stdout


def test_r3_fires_on_method_inside_class() -> None:
    """R3 walks methods inside ``ClassDef`` bodies."""
    result = _run_check("failing/zero_return_method.py")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'process'" in result.stdout


def test_r3_fires_on_outer_skips_optional_helper() -> None:
    """Sibling functions: outer (-> int, zero returns) fires R3;
    helper (-> Optional[int], zero returns) does not."""
    result = _run_check("failing/zero_return_optional_propagation.py")
    assert result.returncode == 1
    assert "zero_return_path" in result.stdout
    assert "function 'outer'" in result.stdout
    assert "function 'helper'" not in result.stdout


# ---------------------------------------------------------------------------
# clean/ fixtures: R3 must stay silent
# ---------------------------------------------------------------------------


def test_r3_silent_on_none_annotated() -> None:
    """``-> None`` is the implicit return type; R3 does not fire."""
    result = _run_check("clean/zero_return_none_annotated.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_r3_silent_on_unannotated() -> None:
    """No return annotation: R3 has no contract to enforce."""
    result = _run_check("clean/zero_return_unannotated.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_r3_silent_on_optional_and_pipe_none_annotations() -> None:
    """``Optional[int]`` and ``int | None`` both permit implicit
    None; R3 delegates to the adapter helpers and skips both."""
    for fixture in (
        "clean/zero_return_optional_annotated.py",
        "clean/zero_return_pipe_none.py",
    ):
        result = _run_check(fixture)
        assert result.returncode == 0, f"{fixture} did not PASS:\n{result.stdout}"
        assert "PASS" in result.stdout


def test_r3_silent_on_raise_only_body() -> None:
    """A function whose body is a single ``raise`` provably never
    returns; R3 skips."""
    result = _run_check("clean/raise_only_function.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_r3_silent_on_while_true_no_break() -> None:
    """Canonical infinite loop: ``while True:`` with no ``break``;
    the function provably never returns. R3 skips."""
    result = _run_check("clean/while_true_no_break.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_r3_silent_on_decorator_skip_list() -> None:
    """``@abstractmethod`` and ``@overload`` (and their dotted
    forms ``@abc.abstractmethod`` / ``@typing.overload``) skip R3."""
    for fixture in (
        "clean/abstractmethod_decorated.py",
        "clean/overload_decorated.py",
    ):
        result = _run_check(fixture)
        assert result.returncode == 0, f"{fixture} did not PASS:\n{result.stdout}"
        assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Direct API: pin ``check_zero_return`` shape independent of CLI
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_check_zero_return_returns_diagnostic_with_function_name() -> None:
    """``check_zero_return`` returns a list of
    ``ZeroReturnDiagnostic`` with a ``function_name`` matching the
    bare offender. Pins the API shape so callers
    (CLI, future plugins) can rely on it."""
    from furqan_lint.zero_return import ZeroReturnDiagnostic, check_zero_return

    source = "def offender(x: int) -> int:\n    pass\n"
    tree = ast.parse(source, filename="<test>")
    diags = check_zero_return(tree)
    assert len(diags) == 1
    diag = diags[0]
    assert isinstance(diag, ZeroReturnDiagnostic)
    assert diag.function_name == "offender"
    assert diag.declared_return == "int"
    assert "no `return` statement" in diag.diagnosis
