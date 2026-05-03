"""Rust adapter: parse .rs files into a Furqan ``Module`` for D24 + D11.

Phase 1 (v0.7.0). Opt-in via the ``[rust]`` extra:

    pip install furqan-lint[rust]

The package is importable without the extra (the CLI does not import
this module unless asked to lint a ``.rs`` file), so the
Python-only install path remains unaffected. tree-sitter is imported
lazily inside ``parse_file``; importing this package alone does not
trigger a ``tree_sitter`` import.

Public surface
==============

* ``parse_file(path)`` -> ``Module``: parse a Rust source file and
  return the translated Furqan ``Module``.
* ``RustParseError``: raised when the Rust source contains a syntax
  error or missing tokens; the CLI converts this to exit code 2.

Everything else (the parser singleton, the translator internals,
the edition resolver) is intentionally not exported. v0.7.x can
expand the surface using the ``__all__``-snapshot additive-only
discipline pinned by ``tests/test_rust_public_surface_additive.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from furqan.parser.ast_nodes import Module

from furqan_lint.rust_adapter.translator import RustParseError

__all__ = ("RustParseError", "parse_file")


def parse_file(path: Path) -> Module:
    """Parse ``path`` as Rust source and return a Furqan ``Module``.

    Lazy-imports ``furqan_lint.rust_adapter.parser`` and
    ``furqan_lint.rust_adapter.translator`` so that the broader
    ``furqan_lint`` package can be imported without the
    ``tree_sitter`` runtime dependency. If tree-sitter or
    tree-sitter-rust is missing, the underlying ``parser._get_parser``
    raises ``ImportError`` and the CLI converts that to a
    user-facing install hint.

    Raises ``RustParseError`` if the source contains a syntax error
    (recoverable parse errors and missing tokens are both caught
    via ``tree.root_node.has_error``).
    """
    from furqan_lint.rust_adapter.edition import edition_for
    from furqan_lint.rust_adapter.parser import parse_file as _parse_file
    from furqan_lint.rust_adapter.translator import translate_tree

    tree = _parse_file(path)
    edition = edition_for(path)
    return translate_tree(tree, path.read_bytes(), path, edition=edition)
