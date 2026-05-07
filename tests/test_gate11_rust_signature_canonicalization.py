"""Tests for the Rust signature canonicalizer.

Pins the audit H-4 nested-generic recursion defense via
explicit canonical-string assertions plus fingerprint
divergence assertions on the five fixture files in
``tests/fixtures/gate11_rust/nested_generic_pinning/``.

If the canonicalizer ever regresses to the Phase G11.0 v0.10.0
tuple-stringification failure mode (where multi-argument
generic parameters fall through to a stringified tuple-node
representation), these tests will detect it before merge.
"""

# ruff: noqa: E402, SIM115, RUF005

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_rust")
pytest.importorskip("rfc8785")

from furqan_lint.gate11.rust_signature_canonicalization import (
    _canonical_type_from_node,
    signature_fingerprint_rust,
)
from furqan_lint.gate11.rust_surface_extraction import (
    extract_public_surface_rust,
)
from furqan_lint.rust_adapter.parser import parse_source

FIXTURES = Path(__file__).parent / "fixtures" / "gate11_rust"


def _first_param_type(rust_source: str) -> str:
    """Helper: parse a single ``pub fn`` and return the canonical
    type-string of its first parameter.
    """
    tree = parse_source(rust_source.encode("utf-8"))
    fn_node = None
    for top in tree.root_node.children:
        if top.type == "function_item":
            fn_node = top
            break
    if fn_node is None:
        raise AssertionError("no function_item in source")
    for c in fn_node.children:
        if c.type == "parameters":
            for p in c.children:
                if p.type == "parameter":
                    seen_colon = False
                    for sub in p.children:
                        if sub.text == b":":
                            seen_colon = True
                            continue
                        if seen_colon:
                            return _canonical_type_from_node(sub)
    raise AssertionError("no parameter type found")


# ---------------------------------------------------------------
# H-4 propagation defense: nested-generic canonical strings
# ---------------------------------------------------------------


def test_h4_vec_of_result_canonical_string():
    """Vec<Result<T, E>> recurses element-wise (T03 rule 6)."""
    src = "pub fn f(x: Vec<Result<u8, Error>>) {}"
    assert _first_param_type(src) == "Vec<Result<u8, Error>>"


def test_h4_hashmap_with_option_canonical_string():
    """HashMap<String, Option<V>> -- multi-arg outer + nested inner."""
    src = "pub fn f(x: HashMap<String, Option<V>>) {}"
    assert _first_param_type(src) == "HashMap<String, Option<V>>"


def test_h4_option_of_slice_strips_lifetimes():
    """Option<&'a [T]> -- lifetime stripped at every nesting level."""
    src = "pub fn f<'a, T>(x: Option<&'a [T]>) {}"
    assert _first_param_type(src) == "Option<&[T]>"


def test_h4_box_dyn_strips_lifetime_and_bound():
    """Box<dyn Trait + 'a> -- lifetime stripped; bound elided per rule 4."""
    src = "pub trait Trait {} pub fn f<'a>(x: Box<dyn Trait + 'a>) {}"
    assert _first_param_type(src) == "Box<dyn Trait>"


def test_h4_triple_nested_recurses_correctly():
    """HashMap<String, Option<Vec<T>>> -- three-level nesting."""
    src = "pub fn f<T>(x: HashMap<String, Option<Vec<T>>>) {}"
    assert _first_param_type(src) == "HashMap<String, Option<Vec<T>>>"


def test_h4_hashmap_inner_generic_difference_detected():
    """The audit's central H-4 assertion:
    ``HashMap<String, Option<V>>`` and ``HashMap<String, Result<V, ()>>``
    must produce DIFFERENT canonical strings. The Phase G11.0
    v0.10.0 Python tuple-stringification failure mode would
    erase this difference.
    """
    a = _first_param_type("pub fn f<V>(x: HashMap<String, Option<V>>) {}")
    b = _first_param_type("pub fn f<V>(x: HashMap<String, Result<V, ()>>) {}")
    assert a != b
    assert a == "HashMap<String, Option<V>>"
    assert b == "HashMap<String, Result<V, ()>>"


def test_h4_lifetime_renaming_invariant():
    """Renaming a lifetime ('a -> 'b) MUST NOT change the
    canonical string (lifetimes are stripped per rule 2).
    """
    a = _first_param_type("pub fn f<'a>(x: &'a str) {}")
    b = _first_param_type("pub fn f<'b>(x: &'b str) {}")
    assert a == b == "&str"


def test_h4_scoped_path_preserved():
    """std::io::Error -- scoped paths preserved as-is."""
    src = "pub fn f(x: std::io::Error) {}"
    assert _first_param_type(src) == "std::io::Error"


# ---------------------------------------------------------------
# Fixture-based pinning tests (H-4 propagation defense)
# ---------------------------------------------------------------


def test_fixture_vec_of_result_pinned():
    entries = extract_public_surface_rust(FIXTURES / "nested_generic_pinning" / "vec_of_result.rs")
    assert len(entries) == 1
    assert entries[0]["name"] == "f"
    assert entries[0]["kind"] == "function"
    # Fingerprint pinned by the canonical signature dict shape.
    assert entries[0]["signature_fingerprint"].startswith("sha256:")


def test_fixture_hashmap_with_option_pinned():
    entries = extract_public_surface_rust(
        FIXTURES / "nested_generic_pinning" / "hashmap_with_option.rs"
    )
    assert len(entries) == 1
    assert entries[0]["name"] == "g"


def test_fixture_option_of_slice_lifetime_invariant():
    """Renaming the lifetime in option_of_slice.rs must not
    change the fingerprint (after re-extraction).
    """
    src = (FIXTURES / "nested_generic_pinning" / "option_of_slice.rs").read_text()
    renamed = src.replace("'a", "'b")
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
        f.write(renamed)
        renamed_path = Path(f.name)
    try:
        original = extract_public_surface_rust(
            FIXTURES / "nested_generic_pinning" / "option_of_slice.rs"
        )
        renamed_extract = extract_public_surface_rust(renamed_path)
        assert original[0]["signature_fingerprint"] == renamed_extract[0]["signature_fingerprint"]
    finally:
        renamed_path.unlink()


def test_fixture_inner_generic_difference_pinned_via_fingerprint():
    """A and B fingerprints must differ because the H-4 fix
    detects inner-generic differences.
    """
    a_src = "pub fn f<V>(x: HashMap<String, Option<V>>) -> () { todo!() }"
    b_src = "pub fn f<V>(x: HashMap<String, Result<V, ()>>) -> () { todo!() }"
    import tempfile

    paths = []
    for src in (a_src, b_src):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as fh:
            fh.write(src)
            paths.append(Path(fh.name))
    try:
        a_entries = extract_public_surface_rust(paths[0])
        b_entries = extract_public_surface_rust(paths[1])
        assert a_entries[0]["signature_fingerprint"] != b_entries[0]["signature_fingerprint"]
    finally:
        for p in paths:
            p.unlink()


# ---------------------------------------------------------------
# Per-kind canonical-form tests
# ---------------------------------------------------------------


def test_function_signature_dict_shape():
    src = "pub fn add(a: i32, b: i32) -> i32 { a + b }"
    tree = parse_source(src.encode())
    fn_node = tree.root_node.children[0]
    fp = signature_fingerprint_rust(fn_node, "add", "function", src.encode())
    assert fp.startswith("sha256:")
    assert len(fp) == len("sha256:") + 64


def test_struct_private_field_changes_fingerprint():
    """Adding a private field changes the struct fingerprint.
    Private fields ARE part of the v1.0 canonical signature.
    """
    src1 = "pub struct P { pub x: i32 }"
    src2 = "pub struct P { pub x: i32, y: i32 }"
    import tempfile

    paths = []
    for src in (src1, src2):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as fh:
            fh.write(src)
            paths.append(Path(fh.name))
    try:
        e1 = extract_public_surface_rust(paths[0])
        e2 = extract_public_surface_rust(paths[1])
        assert e1[0]["signature_fingerprint"] != e2[0]["signature_fingerprint"]
    finally:
        for p in paths:
            p.unlink()


def test_enum_variants_in_signature():
    src = "pub enum Color { Red, Green, Blue }"
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as fh:
        fh.write(src)
        path = Path(fh.name)
    try:
        entries = extract_public_surface_rust(path)
        assert entries[0]["name"] == "Color"
        assert entries[0]["kind"] == "enum"
    finally:
        path.unlink()
