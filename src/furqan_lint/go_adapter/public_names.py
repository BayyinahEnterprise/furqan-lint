"""Public-name extraction for Go source files.

Used by the additive-only diff path (CLI ``furqan-lint diff
old.go new.go``). Mirrors ``furqan_lint.additive._extract_public_names``
in shape -- returns a frozenset of names exposed by a single
file -- but reads from the goast binary's ``public_names`` JSON
field rather than from a Python AST walk.

Symmetric with the future ``rust_adapter.public_names`` module
(deferred to v0.8.2 per locked decision 2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def extract_public_names(path: Path | str) -> frozenset[str]:
    """Extract uppercase-initial Go identifiers from ``path``.

    The goast binary emits ``public_names`` as an ordered list of
    every identifier whose first rune is uppercase, regardless of
    declaration kind: top-level functions, type names, var/const
    names, AND method names (without receiver-type qualification
    -- see the documented limit pinned by
    ``method_conflation_v1.go`` / ``method_conflation_v2.go``;
    fixed in v0.8.2 by emitting qualified method names).

    Returns a frozenset so the caller can pass it directly to
    :func:`furqan_lint.additive.compare_name_sets` without
    additional conversion. The frozenset collapse is also where
    the method-name conflation false-negative manifests: two
    distinct ``Foo`` methods on different receivers become one
    ``Foo`` entry in the set, and removing one method while the
    other remains is invisible to the diff.

    Raises whatever the underlying ``parse_file`` raises:
    :class:`furqan_lint.go_adapter.GoExtrasNotInstalled` when the
    bundled goast binary is absent (and no
    ``FURQAN_LINT_GOAST_BIN`` env override is set), or
    :class:`furqan_lint.go_adapter.GoParseError` when goast
    cannot parse the source file (the CLI maps both to user-
    facing exit codes).
    """
    from furqan_lint.go_adapter import parse_file

    data: dict[str, Any] = parse_file(path)
    return frozenset(data.get("public_names", []))
