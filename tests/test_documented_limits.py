"""Pin v0.3.1's known limitations as tests.

Each test asserts the *current* behaviour of a documented limitation.
When a future version closes one of these, the test fails and the
fixer follows the procedure in
``tests/fixtures/documented_limits/README.md``: delete the fixture,
remove the README entry, drop the assertion here, add a CHANGELOG
entry under ``### Fixed``.

The discipline mirrors Bayyinah's adversarial gauntlet directories:
every claim the documentation makes about behaviour has a fixture
and a test asserting that behaviour, so the documentation cannot
silently drift away from the code.

These tests are NOT a statement that the current behaviour is
correct. They are a statement that the current behaviour is the
deliberate, documented behaviour, so any change to it (in either
direction) must be intentional.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "documented_limits"


def _run_check(fixture: str) -> subprocess.CompletedProcess:
    """Run ``furqan-lint check <fixture>`` and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "check", str(FIXTURES / fixture)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


# ---------------------------------------------------------------------------
# Exception-driven fall-through (try body spliced unconditionally)
# ---------------------------------------------------------------------------

def test_try_body_only_returns_in_block_is_passed() -> None:
    """``try: return 42; except ValueError: pass`` is reported PASS.

    Documented limitation: v0.3.1 splices the try body
    unconditionally so D24 sees the return as guaranteed coverage.
    An exception in the body would prevent the return from
    reaching, but D24 explicitly does not model exception flow.
    """
    result = _run_check("try_body_no_exception_modeling.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_try_body_raises_with_swallowing_handler_is_passed() -> None:
    """``try: raise; except: pass`` is reported PASS.

    Documented limitation: same as above, stronger form. The body
    unconditionally raises, the handler falls through, mypy flags
    this. v0.3.1 does not.
    """
    result = _run_check("try_body_only_returns_in_block.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Aliased Optional imports
# ---------------------------------------------------------------------------

def test_aliased_optional_import_fires_false_positive() -> None:
    """``from typing import Optional as MyOpt; -> MyOpt[X]`` is
    treated as non-Optional and a return-None inside fires
    return_none_mismatch as a false positive.

    Documented limitation: the matcher requires the bare ``Optional``
    name or the qualified ``typing.Optional`` / ``t.Optional`` forms.
    Alias resolution needs symbol-table tracking, deferred to a
    future phase.
    """
    result = _run_check("aliased_optional_import.py")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "return_none_mismatch" in result.stdout


# ---------------------------------------------------------------------------
# Local classes inside function bodies
# ---------------------------------------------------------------------------

def test_local_class_in_function_methods_not_collected() -> None:
    """A class defined inside a function body has its methods
    silently dropped, even though the v0.3.2 nested-class fix
    (Finding 3) collects methods of nested top-level classes.

    Documented limitation: a local class is a private
    implementation detail; D24 and ``return_none_mismatch`` exist
    to keep the public contract honest, so silent passes on
    locally-scoped classes are deliberate. If a future fixture
    demonstrates a real regression caused by this, extend the
    function walker to also descend into nested
    ``ClassDef``-inside-``FunctionDef``.
    """
    result = _run_check("local_class_in_function.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout
