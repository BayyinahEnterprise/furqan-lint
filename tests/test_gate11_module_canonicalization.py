"""Tests for Phase G11.0 T03: module canonicalization.

Pin:

* LF and CRLF inputs produce the same hash.
* BOM and no-BOM inputs produce the same hash.
* Different content produces different hashes.
* Non-UTF-8 source raises ModuleCanonicalizationError with
  code CASM-V-002.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from furqan_lint.gate11.module_canonicalization import (
    ModuleCanonicalizationError,
    canonicalize_module,
    module_root_hash,
)


def test_lf_vs_crlf_same_hash(tmp_path: Path) -> None:
    a = tmp_path / "lf.py"
    b = tmp_path / "crlf.py"
    a.write_bytes(b"def f():\n    return 1\n")
    b.write_bytes(b"def f():\r\n    return 1\r\n")
    assert module_root_hash(a) == module_root_hash(b)


def test_bom_vs_no_bom_same_hash(tmp_path: Path) -> None:
    base = b"def f():\n    return 1\n"
    a = tmp_path / "no_bom.py"
    b = tmp_path / "with_bom.py"
    a.write_bytes(base)
    b.write_bytes(b"\xef\xbb\xbf" + base)
    assert module_root_hash(a) == module_root_hash(b)


def test_different_content_different_hash(tmp_path: Path) -> None:
    a = tmp_path / "a.py"
    b = tmp_path / "b.py"
    a.write_bytes(b"def f():\n    return 1\n")
    b.write_bytes(b"def f():\n    return 2\n")
    assert module_root_hash(a) != module_root_hash(b)


def test_canonicalize_returns_bytes_with_lf(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_bytes(b"a\r\nb\r\nc\n")
    out = canonicalize_module(p)
    assert out == b"a\nb\nc\n"
    # BOM-stripped, CRLF-normalized.
    p2 = tmp_path / "m2.py"
    p2.write_bytes(b"\xef\xbb\xbf" + b"x\r\n")
    assert canonicalize_module(p2) == b"x\n"


def test_non_utf8_raises_casm_v_002(tmp_path: Path) -> None:
    p = tmp_path / "bad.py"
    # Latin-1 byte 0xff is not valid UTF-8 leading byte.
    p.write_bytes(b"# header\nx = '\xff'\n")
    with pytest.raises(ModuleCanonicalizationError) as exc:
        canonicalize_module(p)
    assert exc.value.code == "CASM-V-002"
    assert "UTF-8" in str(exc.value)


def test_hash_format_is_sha256_prefixed(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_bytes(b"x = 1\n")
    h = module_root_hash(p)
    assert h.startswith("sha256:")
    assert len(h) == len("sha256:") + 64
    int(h[len("sha256:") :], 16)  # parses as hex


def test_old_mac_cr_endings_normalize(tmp_path: Path) -> None:
    """Legacy CR-only line endings normalize to LF."""
    a = tmp_path / "lf.py"
    b = tmp_path / "cr.py"
    a.write_bytes(b"a\nb\nc\n")
    b.write_bytes(b"a\rb\rc\r")
    assert module_root_hash(a) == module_root_hash(b)
