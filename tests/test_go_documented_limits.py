"""Pinning tests for the Go adapter's documented limits.

Each test asserts the current observable verdict so any
behavior change (in either direction) shows up as a test
failure rather than a silent semantic drift. The mirror of
``tests/test_documented_limits.py`` (Python) and
``tests/test_rust_correctness.py`` (Rust documented_limits
section).

The fixtures under ``tests/fixtures/go/documented_limits/``
each have a header comment describing what the limit is, when
it was introduced, and the resolution path. The
``tests/fixtures/go/documented_limits/README.md`` indexes them.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
LIMITS_DIR = REPO_ROOT / "tests" / "fixtures" / "go" / "documented_limits"


def _go_extras_present() -> bool:
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    pkg_root = Path(spec.origin).parent
    binary = pkg_root / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _go_extras_present(),
        reason="goast binary not built; install [go] extras",
    ),
]


def _run_check(fixture: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(fixture)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_multi_return_three_or_more_translates_to_opaque() -> None:
    """3+-element returns become TypePath('<multi-return>'); D24 PASSes."""
    fixture = LIMITS_DIR / "multi_return_three_or_more.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_two_element_non_error_tuple_is_opaque_typepath() -> None:
    """(int, string) returns are opaque TypePath, NOT a may-fail union."""
    fixture = LIMITS_DIR / "two_element_non_error_tuple.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_for_statement_body_is_opaque() -> None:
    """`for` body wraps as may-runs-0-or-N opaque IfStmt; trailing
    return makes the function PASS."""
    fixture = LIMITS_DIR / "for_statement_opaque.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_switch_statement_body_is_opaque() -> None:
    """`switch` body wraps as may-runs-0-or-N opaque IfStmt.
    The case-arm returns are invisible to D24, so a switch-only
    function PASSes regardless of arm coverage. The limit being
    pinned: D24 cannot reason about return coverage inside
    switch bodies, so it neither correctly recognizes exhaustive
    switches nor fires on partial ones. Resolution path: a
    future phase may extend if a concrete user-reported false
    positive or false negative warrants it.
    """
    fixture = LIMITS_DIR / "switch_statement_opaque.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_select_statement_body_is_opaque() -> None:
    """`select` body wraps as may-runs-0-or-N opaque IfStmt."""
    fixture = LIMITS_DIR / "select_statement_opaque.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_defer_statement_is_opaque() -> None:
    """`defer` is opaque; the trailing return is what guarantees coverage."""
    fixture = LIMITS_DIR / "defer_statement_opaque.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_interface_method_dispatch_is_opaque() -> None:
    """Interface method dispatch is not specially modeled; the call
    appears with the bare method name and the function PASSes D24."""
    fixture = LIMITS_DIR / "interface_method_dispatch.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_generic_type_parameters_are_discarded() -> None:
    """Generic type parameters in signatures are syntactically
    allowed; the function PASSes D24."""
    fixture = LIMITS_DIR / "generic_type_parameters.go"
    result = _run_check(fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
