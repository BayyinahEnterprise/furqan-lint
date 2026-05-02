"""Additive-only API checker for Python modules.

Phase 2 ships this as a Python-native checker rather than wrapping
Furqan's :func:`check_additive`. The Furqan checker compares
:class:`AdditiveOnlyModuleDecl` blocks with explicit
:class:`VersionLiteral` and :class:`ExportDecl` nodes, which Python
does not have. The Python equivalent is the module's public surface,
defined as:

* if ``__all__`` is set (list or tuple of string literals): exactly
  those names;
* otherwise: every top-level name that does not start with an
  underscore (functions, classes, simple module-level assignments).

The contract is one-directional: removing a public name fires a
:class:`Marad`; adding one is silent. Renames are detected as a
remove-and-add pair (the removed name fires; the added name is
ignored). Phase 3 may add a rename catalog so the user can declare a
rename explicitly the way Furqan's ``major_version_bump`` block does.
"""

from __future__ import annotations

import ast

from furqan.errors.marad import Marad
from furqan.parser.ast_nodes import SourceSpan


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def check_additive_api(
    current_source: str,
    previous_source: str,
    filename: str = "<module>",
) -> list[Marad]:
    """Compare two versions of a module's public API.

    Returns one :class:`Marad` per public name that was present in
    ``previous_source`` and absent in ``current_source``. The
    diagnostics are emitted in sorted name order so callers (and
    tests) get a stable sequence.
    """
    current_names = _extract_public_names(current_source)
    previous_names = _extract_public_names(previous_source)

    removed = previous_names - current_names
    diagnostics: list[Marad] = []
    for name in sorted(removed):
        diagnostics.append(
            Marad(
                primitive="additive_only",
                diagnosis=(
                    f"Public name '{name}' was present in the "
                    f"previous version but is absent in the current "
                    f"version. Removing a public name breaks the "
                    f"additive-only contract: you can add to a "
                    f"module's public interface but never remove or "
                    f"rename."
                ),
                location=SourceSpan(file=filename, line=1, column=0),
                minimal_fix=(
                    f"Restore '{name}' in the current version, or "
                    f"add a compatibility alias: {name} = <new_name>"
                ),
                regression_check=(
                    f"After restoring '{name}', re-run "
                    f"`furqan-lint diff <old> <new>` and confirm "
                    f"PASS."
                ),
            )
        )
    return diagnostics


# ---------------------------------------------------------------------------
# Public-surface extraction
# ---------------------------------------------------------------------------

def _extract_public_names(source: str) -> set[str]:
    """Return the set of public names exposed by ``source``.

    Looks for an ``__all__`` assignment first; if present, returns
    exactly the names it lists. Otherwise returns every top-level
    function, class, or simple-assignment target whose name does not
    start with an underscore.
    """
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "__all__"
                ):
                    return _extract_all_list(node.value)

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and not target.id.startswith("_")
                ):
                    names.add(target.id)
    return names


def _extract_all_list(node: ast.expr) -> set[str]:
    """Extract string-literal names from ``__all__ = [...]`` or
    ``__all__ = (...)``. Non-string-literal entries are silently
    skipped: dynamic ``__all__`` construction is out of scope."""
    names: set[str] = set()
    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                names.add(elt.value)
    return names
