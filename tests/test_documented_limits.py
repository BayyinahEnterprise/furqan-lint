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

import pytest

pytestmark = pytest.mark.integration
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
# RETIRED in v0.6.0: R3 (zero-return) catches this case because the
# function 'f' has no return statement on any path. The fixture is
# kept as a regression target asserting R3 still catches it.
# ---------------------------------------------------------------------------


def test_try_body_raises_with_swallowing_handler_now_caught_by_r3() -> None:
    """``try: raise; except: pass`` (no return on any path) is now
    flagged by R3 (zero-return). v0.5.x and earlier: silent PASS.
    v0.6.0+: ring-close violation.

    Pinning the new behaviour as a regression target. If a future
    refactor accidentally regresses R3 to skip try-body shapes, this
    test will fail and the fix is to restore R3's coverage.
    """
    result = _run_check("try_body_only_returns_in_block.py")
    assert result.returncode == 1
    assert "MARAD" in result.stdout
    assert "zero_return_path" in result.stdout
    assert "function 'f'" in result.stdout


# ---------------------------------------------------------------------------
# Aliased Optional / Union imports
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


def test_aliased_union_import_treated_as_typing_union() -> None:
    """``Union[X, None]`` is treated as Optional regardless of which
    module the bare ``Union`` name was imported from. The matcher
    accepts the head by name and does not consult import provenance.

    Documented limitation (v0.3.3): symmetric form of the
    aliased-Optional limitation. The fixture imports ``Union`` from
    ``typing`` so it parses cleanly; the behaviour pinned here is
    that the matcher would treat ``somelib.Union[X, None]`` the
    same way (silent PASS) because it never looks at where the
    name came from. Same fix shape as the Optional case
    (symbol-table tracking).
    """
    result = _run_check("aliased_union_import.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


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


# ---------------------------------------------------------------------------
# Redundant None arms in PEP 604 unions (v0.3.4 / round-7 Observation 2)


# ---------------------------------------------------------------------------
# Optional stored in a container (v1.0.1)
# ---------------------------------------------------------------------------


def test_optional_stored_in_container_still_fires_d11() -> None:
    """D11 does not track values through containers: returning
    ``{"name": find_name(uid)}`` keeps the None arm but is still
    reported. Documented in README "Remaining limitations"."""
    result = _run_check("optional_stored_in_container.py")
    assert result.returncode == 1
    assert "status_coverage" in result.stdout
    assert "function 'describe'" in result.stdout


# ---------------------------------------------------------------------------
# Terminal calls D24 does not recognise (v1.0.1)
# ---------------------------------------------------------------------------


def test_exit_alias_not_terminal_still_fires_d24() -> None:
    """``from sys import exit``, a ``NoReturn`` helper, ``assert False``
    and bare ``quit()`` end the path at runtime, but D24 recognises only
    ``raise`` and the ``sys.exit`` / ``os._exit`` / ``os.abort``
    spellings, so all four are reported. Documented in README
    "Remaining limitations"."""
    result = _run_check("exit_alias_not_terminal.py")
    assert result.returncode == 1
    for name in ("aliased_exit", "via_noreturn_helper", "assert_false", "bare_quit"):
        assert f"[all_paths_return] function '{name}'" in result.stdout
    assert result.stdout.count("[all_paths_return]") == 4


# ---------------------------------------------------------------------------
# None handled away from the call site (v1.0.1)
# ---------------------------------------------------------------------------


def test_optional_guard_not_adjacent_still_fires_d11() -> None:
    """A None-guard that is not the statement right after the binding,
    ``assert x is not None`` (stripped by ``python -O``), and a None
    branch with a nested ``if`` before its exit (v1.0.1 audit F-01
    consequence), and a guard inside a ``try`` with handlers (its raise
    might be caught) are not seen as handling None, so D11 still
    reports all four. Documented in
    README "Remaining limitations"."""
    result = _run_check("optional_guard_not_adjacent.py")
    assert result.returncode == 1
    for name in ("guard_two_lines_down", "asserted", "branch_before_exit", "guard_inside_try"):
        assert f"[status_coverage] function '{name}'" in result.stdout
    assert result.stdout.count("[status_coverage]") == 4


# ---------------------------------------------------------------------------
# Terminal recognition is syntactic (v1.0.1)
# ---------------------------------------------------------------------------


def test_terminal_recognition_false_negatives_pass_silently() -> None:
    """A ``raise`` swallowed by ``contextlib.suppress`` and
    ``sys.exit()`` on a parameter named ``sys`` both count as ending
    the path, so D24 is silent on functions that can fall through.
    Documented in README "Remaining limitations"."""
    result = _run_check("terminal_recognition_false_negatives.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Raise shapes D24 still misreads (v1.0.1)
# ---------------------------------------------------------------------------


def test_raise_terminal_remaining_false_positives_still_fire_d24() -> None:
    """``for ... else: raise``, ``while True:`` ending in ``raise``, and
    ``try`` / ``finally`` with no ``except`` never fall through, yet
    D24 reports all three. Documented in README "Remaining
    limitations"."""
    result = _run_check("raise_terminal_remaining_false_positives.py")
    assert result.returncode == 1
    for name in ("search", "poll", "guarded"):
        assert f"[all_paths_return] function '{name}'" in result.stdout
    assert result.stdout.count("[all_paths_return]") == 3


@pytest.mark.skipif(sys.version_info < (3, 11), reason="except* needs Python 3.11")
def test_try_star_hides_missing_return_from_d24() -> None:
    """``try`` / ``except*`` is not translated, so a ``return`` inside
    its ``try`` body is invisible and D24 never runs on the function,
    even though a path falls through. Pre-existing; documented in
    README "Remaining limitations" next to the raise-terminal limits.

    v1.0.1 audit F-02: the specimen must be legal Python. ``return``,
    ``break`` and ``continue`` are forbidden inside an ``except*``
    handler, so the return sits in the ``try`` body and the handler
    only passes. The test compiles and runs the specimen first, so it
    pins behaviour on code that can actually execute."""
    import ast as _ast

    from furqan_lint.adapter import translate_source
    from furqan_lint.runner import check_python_module

    source = (
        "def f(x: int) -> int:\n"
        "    try:\n"
        "        if x:\n"
        "            return 1\n"
        "    except* ValueError:\n"
        "        pass\n"
    )
    namespace: dict = {}
    exec(compile(source, "<try-star>", "exec"), namespace)
    assert namespace["f"](0) is None  # the fall-through is real
    assert namespace["f"](1) == 1
    names = [n for n, _ in check_python_module(translate_source(source), _ast.parse(source))]
    assert "all_paths_return" not in names
    assert "zero_return_path" not in names


# ---------------------------------------------------------------------------
# ``-> None`` carries no value contract (v1.0.1)
# ---------------------------------------------------------------------------


def test_none_procedure_returning_value_passes_silently() -> None:
    """A ``-> None`` function that returns a value is not reported: no
    checker compares returned values with ``-> None``. Documented in
    README "Remaining limitations"."""
    result = _run_check("none_procedure_returning_value.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Comparisons are assumed to be bool (v1.0.1)
# ---------------------------------------------------------------------------


def test_comparison_assumed_bool_passes_silently() -> None:
    """An ``__eq__`` that returns its argument hands the producer's
    None back through ``==``; D11 assumes ``==`` yields a bool and is
    silent. Documented in README "Remaining limitations"."""
    result = _run_check("comparison_assumed_bool.py")
    assert result.returncode == 0
    assert "PASS" in result.stdout
