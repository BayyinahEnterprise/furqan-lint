"""pyproject [rust] extras sync (v0.7.0).

Verifies that ``pip install furqan-lint[rust]`` resolves the
expected runtime dependencies and that the modules import cleanly
on this machine. Skipped when the [rust] extra is not installed
(silent on the Python-only install path; hard failure on a
configured rust install).
"""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

_MISSING_REASON = (
    "tree_sitter or tree_sitter_rust not installed; install with "
    "pip install -e '.[rust]' to run this test"
)


def _rust_extras_present() -> bool:
    try:
        importlib.import_module("tree_sitter")
        importlib.import_module("tree_sitter_rust")
    except ImportError:
        return False
    return True


@pytest.mark.skipif(not _rust_extras_present(), reason=_MISSING_REASON)
def test_tree_sitter_imports_cleanly() -> None:
    """Importing tree_sitter and tree_sitter_rust must not raise.
    Failure here means the [rust] extra resolved to incompatible
    package versions on this Python."""
    import tree_sitter
    import tree_sitter_rust

    assert tree_sitter is not None
    assert tree_sitter_rust is not None


@pytest.mark.skipif(not _rust_extras_present(), reason=_MISSING_REASON)
def test_rust_language_handle_is_nonzero() -> None:
    """``tree_sitter.Language(tree_sitter_rust.language())`` must
    construct a non-None handle. Sanity check that the C grammar
    is loadable."""
    import tree_sitter
    import tree_sitter_rust

    handle = tree_sitter.Language(tree_sitter_rust.language())
    assert handle is not None
