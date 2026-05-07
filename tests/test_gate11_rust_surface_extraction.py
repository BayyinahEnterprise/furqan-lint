"""Tests for Rust public-surface extraction.

Pins the documented limits (impl-block methods omitted,
``pub(crate)`` excluded, items inside non-``pub`` modules
excluded) per amended_4 T02.
"""

# ruff: noqa: E402, SIM115, RUF005

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_rust")
pytest.importorskip("rfc8785")

from furqan_lint.gate11.rust_surface_extraction import (
    DynamicRustSurfaceError,
    extract_public_surface_rust,
)


def _write_rust(src: str) -> Path:
    fh = tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False)
    fh.write(src)
    fh.close()
    return Path(fh.name)


def test_pub_fn_extracted():
    p = _write_rust("pub fn add(a: i32, b: i32) -> i32 { a + b }")
    try:
        entries = extract_public_surface_rust(p)
        assert len(entries) == 1
        assert entries[0]["name"] == "add"
        assert entries[0]["kind"] == "function"
    finally:
        p.unlink()


def test_pub_struct_extracted():
    p = _write_rust("pub struct Point { pub x: i32, y: i32 }")
    try:
        entries = extract_public_surface_rust(p)
        assert len(entries) == 1
        assert entries[0]["name"] == "Point"
        assert entries[0]["kind"] == "struct"
    finally:
        p.unlink()


def test_pub_enum_extracted():
    p = _write_rust("pub enum Color { Red, Green, Blue }")
    try:
        entries = extract_public_surface_rust(p)
        assert len(entries) == 1
        assert entries[0]["kind"] == "enum"
    finally:
        p.unlink()


def test_pub_trait_extracted():
    """Phase G11.1 ADDS trait extraction (legacy
    extract_public_names omits trait_item per locked decision 3
    in v0.8.2; G11.1 includes it because traits are part of the
    crate's externally-visible API surface).
    """
    p = _write_rust("pub trait Shape { fn area(&self) -> f64; }")
    try:
        entries = extract_public_surface_rust(p)
        assert len(entries) == 1
        assert entries[0]["kind"] == "trait"
        assert entries[0]["name"] == "Shape"
    finally:
        p.unlink()


def test_pub_crate_NOT_extracted():
    """Documented limit: ``pub(crate)`` is not external API."""
    p = _write_rust("pub(crate) fn internal() {}")
    try:
        entries = extract_public_surface_rust(p)
        assert entries == []
    finally:
        p.unlink()


def test_pub_super_NOT_extracted():
    p = _write_rust("pub(super) fn parent_only() {}")
    try:
        entries = extract_public_surface_rust(p)
        assert entries == []
    finally:
        p.unlink()


def test_private_NOT_extracted():
    p = _write_rust("fn private() {}")
    try:
        entries = extract_public_surface_rust(p)
        assert entries == []
    finally:
        p.unlink()


def test_impl_methods_NOT_extracted():
    """Documented limit (consistent with existing
    extract_public_names): impl-block methods are out of scope.
    Improvement is a v1.5 horizon item.
    """
    src = """
pub struct S {}
impl S {
    pub fn method(&self) {}
}
"""
    p = _write_rust(src)
    try:
        entries = extract_public_surface_rust(p)
        # Only the struct surfaces; the impl-block method does not.
        names = [e["name"] for e in entries]
        assert "S" in names
        assert "method" not in names
    finally:
        p.unlink()


def test_pub_const_extracted():
    p = _write_rust("pub const MAX: i32 = 100;")
    try:
        entries = extract_public_surface_rust(p)
        assert entries[0]["name"] == "MAX"
        assert entries[0]["kind"] == "constant"
    finally:
        p.unlink()


def test_pub_static_extracted():
    p = _write_rust('pub static NAME: &str = "x";')
    try:
        entries = extract_public_surface_rust(p)
        assert entries[0]["name"] == "NAME"
        assert entries[0]["kind"] == "constant"
    finally:
        p.unlink()


def test_pub_type_alias_extracted():
    p = _write_rust("pub type Result2<T> = Result<T, String>;")
    try:
        entries = extract_public_surface_rust(p)
        assert entries[0]["name"] == "Result2"
        assert entries[0]["kind"] == "type_alias"
    finally:
        p.unlink()


def test_ascii_sorted_order():
    """Output is ASCII-sorted regardless of source order."""
    src = """
pub fn zebra() {}
pub fn alpha() {}
pub fn middle() {}
"""
    p = _write_rust(src)
    try:
        entries = extract_public_surface_rust(p)
        names = [e["name"] for e in entries]
        assert names == sorted(names)
    finally:
        p.unlink()


def test_pub_use_glob_raises_indeterminate():
    """``pub use foo::*`` cannot be statically resolved; raises
    DynamicRustSurfaceError so the verifier can mark the
    manifest CASM-V-INDETERMINATE per Phase G11.A Invariant 6
    step 8.
    """
    p = _write_rust("pub use crate::foo::*;")
    try:
        with pytest.raises(DynamicRustSurfaceError):
            extract_public_surface_rust(p)
    finally:
        p.unlink()
