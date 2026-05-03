"""Unit tests for furqan_lint.rust_adapter.public_names.extract_public_names.

Pins the v0.8.2 contract: the function returns exactly the
``pub`` item names declared at the file's top level, skipping
``pub(crate)`` / ``pub(super)`` / ``pub(in path)`` qualifiers
(per locked decision 2).

Tests are unit-marked and skipped when the [rust] extras are
not installed (mirrors test_rust_correctness.py shape).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _rust_extras_present() -> bool:
    return (
        importlib.util.find_spec("tree_sitter") is not None
        and importlib.util.find_spec("tree_sitter_rust") is not None
    )


pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(
        not _rust_extras_present(),
        reason="tree_sitter / tree_sitter_rust not installed; install [rust] extras",
    ),
]


def test_extract_public_names_collects_pub_items(tmp_path: Path) -> None:
    """All seven supported item kinds with bare ``pub`` are
    collected; non-pub items are excluded."""
    from furqan_lint.rust_adapter import extract_public_names

    src = tmp_path / "lib.rs"
    src.write_text(
        "pub fn public_fn() {}\n"
        "fn private_fn() {}\n"
        "pub struct PublicStruct {}\n"
        "struct PrivateStruct {}\n"
        "pub enum PublicEnum { A }\n"
        "pub const PUBLIC_CONST: i32 = 1;\n"
        "pub static PUBLIC_STATIC: i32 = 2;\n"
        "pub type PublicAlias = i32;\n"
        "pub mod public_mod {}\n"
    )
    names = extract_public_names(src)
    assert names == frozenset(
        {
            "public_fn",
            "PublicStruct",
            "PublicEnum",
            "PUBLIC_CONST",
            "PUBLIC_STATIC",
            "PublicAlias",
            "public_mod",
        }
    )
    assert "private_fn" not in names
    assert "PrivateStruct" not in names


def test_extract_public_names_skips_pub_crate(tmp_path: Path) -> None:
    """Crate-private items (``pub(crate)``) are NOT part of the
    external API surface; they must be skipped per locked
    decision 2."""
    from furqan_lint.rust_adapter import extract_public_names

    src = tmp_path / "lib.rs"
    src.write_text(
        "pub fn truly_public() {}\n"
        "pub(crate) fn crate_private() {}\n"
        "pub(super) fn super_private() {}\n"
        "pub(in crate::module) fn path_restricted() {}\n"
    )
    names = extract_public_names(src)
    assert names == frozenset({"truly_public"})


def test_extract_public_names_returns_frozenset(tmp_path: Path) -> None:
    """The return type is frozenset (not set or list) so the
    caller can pass it directly to compare_name_sets and so the
    value is hashable / safely shareable."""
    from furqan_lint.rust_adapter import extract_public_names

    src = tmp_path / "lib.rs"
    src.write_text("pub fn foo() {}\n")
    names = extract_public_names(src)
    assert isinstance(names, frozenset)


def test_extract_public_names_handles_empty_file(tmp_path: Path) -> None:
    """An empty Rust file or one with only comments returns an
    empty frozenset (not an error)."""
    from furqan_lint.rust_adapter import extract_public_names

    src = tmp_path / "lib.rs"
    src.write_text("// just a comment\n")
    assert extract_public_names(src) == frozenset()


def test_extract_public_names_skips_methods_in_impl(tmp_path: Path) -> None:
    """Methods inside ``impl Type { ... }`` blocks are NOT
    collected at the top-level diff layer (they are private to
    the type per the v0.8.2 design; mirrors goast's pre-v0.8.2
    bare-method handling but inverted -- the diff treats methods
    as type-private rather than collapsing them by name).

    The struct itself IS collected, but the impl methods are
    not. This is the load-bearing pin against a future change
    that recurses into impl bodies.
    """
    from furqan_lint.rust_adapter import extract_public_names

    src = tmp_path / "lib.rs"
    src.write_text(
        "pub struct Counter {}\n"
        "\n"
        "impl Counter {\n"
        "    pub fn new() -> Counter { Counter {} }\n"
        "    pub fn increment(&mut self) {}\n"
        "}\n"
    )
    names = extract_public_names(src)
    assert names == frozenset({"Counter"})
    assert "new" not in names
    assert "increment" not in names
