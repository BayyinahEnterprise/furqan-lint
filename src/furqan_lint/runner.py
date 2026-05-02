"""Run structural checkers on a translated Python ``Module``.

Three checkers cross the language boundary cleanly as of v0.2.0:

* **D24 (all-paths-return).** No adaptation needed. Every typed Python
  function should reach a ``return`` on every control-flow path; the
  Furqan checker reads ``fn.return_type`` and walks ``fn.statements``.
* **D11 (status-coverage).** The Furqan check is hard-coded to
  recognise ``Integrity | Incomplete`` as the producer pattern. The
  Python equivalent is ``Optional[X]`` (i.e. ``X | None``). We
  monkey-patch the producer predicate inside a context manager so the
  check sees the Python pattern, then restore the original on exit.
  DEFECT 3 FIX: scoping via context manager prevents cross-
  contamination if Furqan's own test suite runs in the same process.
* **return_none_mismatch.** Python-native checker that closes Phase 1
  Gap 1: a function declaring a non-Optional return type that returns
  None on some path is a type mismatch, not a satisfied D24 path.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from furqan.checker import status_coverage
from furqan.checker.all_paths_return import check_all_paths_return
from furqan.parser.ast_nodes import Module, UnionType

from furqan_lint.return_none import check_return_none


# ---------------------------------------------------------------------------
# Producer predicate adaptation
# ---------------------------------------------------------------------------

def _is_optional_union(rt: object) -> bool:
    """True iff ``rt`` is a ``UnionType`` with one arm being ``None``.

    Treats ``Optional[X]`` (translated to ``UnionType(X, None)``) as
    the Python equivalent of Furqan's ``Integrity | Incomplete``
    producer pattern, for the purposes of D11's status-coverage walk.
    """
    if not isinstance(rt, UnionType):
        return False
    names = {rt.left.base, rt.right.base}
    return "None" in names


@contextmanager
def _python_optional_mode() -> Iterator[None]:
    """Temporarily patch ``status_coverage._is_integrity_incomplete_union``
    to the Python-aware predicate, restoring the original on exit.

    The patch is scoped so any subsequent call to ``check_status_coverage``
    that does not pass through this context manager (e.g. Furqan's own
    test suite running in the same process) sees the original behaviour.
    """
    original = status_coverage._is_integrity_incomplete_union
    status_coverage._is_integrity_incomplete_union = _is_optional_union
    try:
        yield
    finally:
        status_coverage._is_integrity_incomplete_union = original


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def check_python_module(module: Module) -> list[tuple[str, object]]:
    """Run all structural checks on a translated Python ``Module``.

    Returns a list of ``(checker_name, diagnostic)`` tuples. ``diagnostic``
    is either a :class:`furqan.errors.marad.Marad` (a violation) or a
    :class:`furqan.errors.marad.Advisory` (informational). The CLI
    separates these for display; programmatic consumers can filter by
    ``isinstance`` if they care about severity.
    """
    diagnostics: list[tuple[str, object]] = []

    for d in check_all_paths_return(module):
        diagnostics.append(("all_paths_return", d))

    with _python_optional_mode():
        for d in status_coverage.check_status_coverage(module):
            diagnostics.append(("status_coverage", d))

    for d in check_return_none(module):
        diagnostics.append(("return_none_mismatch", d))

    return diagnostics
