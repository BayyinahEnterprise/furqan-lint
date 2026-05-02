"""Run structural checkers on a translated Python ``Module``.

Three checkers cross the language boundary cleanly:

* **D24 (all-paths-return).** No adaptation needed. Every typed Python
  function should reach a ``return`` on every control-flow path; the
  Furqan checker reads ``fn.return_type`` and walks ``fn.statements``.
* **D11 (status-coverage).** As of v0.4.1, D11 uses the upstream
  ``producer_predicate`` keyword-only parameter on
  ``check_status_coverage`` (available since furqan v0.11.0) instead
  of monkey-patching ``status_coverage._is_integrity_incomplete_union``.
  The adapter helper :func:`_is_optional_union` is passed as the
  predicate so the check sees ``Optional[X]`` (translated to
  ``UnionType(X, None)``) as the Python equivalent of Furqan's
  ``Integrity | Incomplete`` producer pattern. Closes the full
  lifecycle of a round-1 audit finding (v0.1.0 monkey-patch via
  context manager -> v0.3.0 added threading lock for safety ->
  v0.4.1 upstream ``producer_predicate=`` keyword retires the
  patch entirely).
* **return_none_mismatch.** Python-native checker that closes Phase 1
  Gap 1: a function declaring a non-Optional return type that returns
  None on some path is a type mismatch, not a satisfied D24 path.
"""

from __future__ import annotations

from furqan.checker.all_paths_return import check_all_paths_return
from furqan.checker.status_coverage import check_status_coverage
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
    Passed to ``check_status_coverage`` via the ``producer_predicate``
    keyword (furqan>=0.11.0).
    """
    if not isinstance(rt, UnionType):
        return False
    names = {rt.left.base, rt.right.base}
    return "None" in names


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

    for d in check_status_coverage(
        module, producer_predicate=_is_optional_union
    ):
        diagnostics.append(("status_coverage", d))

    for d in check_return_none(module):
        diagnostics.append(("return_none_mismatch", d))

    return diagnostics
