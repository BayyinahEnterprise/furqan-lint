"""Tests for Phase G11.0 T05: public-surface extraction.

Pin:

* Three public names produce three entries.
* Underscore-prefixed names are excluded.
* Entries are ASCII-sorted by name.
* __all__ semantics honored (statically declared list only).
* Dynamic __all__ raises DynamicAllError.
"""

from __future__ import annotations

from pathlib import Path

import pytest

rfc8785 = pytest.importorskip("rfc8785")

from furqan_lint.additive import DynamicAllError  # noqa: E402
from furqan_lint.gate11.surface_extraction import (  # noqa: E402
    extract_public_surface,
)


def _write(tmp_path: Path, src: str) -> Path:
    p = tmp_path / "m.py"
    p.write_text(src, encoding="utf-8")
    return p


def test_three_public_names_three_entries(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        "def alpha(): ...\n" "class Beta: ...\n" "GAMMA: int = 3\n" "def _private(): ...\n",
    )
    entries = extract_public_surface(p)
    names = [e["name"] for e in entries]
    assert names == ["Beta", "GAMMA", "alpha"]
    kinds = {e["name"]: e["kind"] for e in entries}
    assert kinds == {"Beta": "class", "GAMMA": "constant", "alpha": "function"}


def test_underscore_prefixed_excluded(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        "def _hidden(): ...\n"
        "class _Private: ...\n"
        "_INTERNAL: int = 1\n"
        "def visible(): ...\n",
    )
    entries = extract_public_surface(p)
    names = [e["name"] for e in entries]
    assert names == ["visible"]


def test_ascii_sorted_order(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        "def zeta(): ...\n" "def alpha(): ...\n" "def mu(): ...\n",
    )
    entries = extract_public_surface(p)
    assert [e["name"] for e in entries] == ["alpha", "mu", "zeta"]


def test_all_statically_declared(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        "__all__ = ['alpha']\n" "def alpha(): ...\n" "def beta(): ...\n",  # not exported
    )
    entries = extract_public_surface(p)
    names = [e["name"] for e in entries]
    assert names == ["alpha"]


def test_dynamic_all_raises_dynamic_all_error(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        "_NAMES = ['alpha']\n" "__all__ = list(_NAMES)\n" "def alpha(): ...\n",
    )
    with pytest.raises(DynamicAllError):
        extract_public_surface(p)


def test_signature_fingerprints_present_and_unique(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        "def f(x: int) -> int: return x\n" "def g(x: str) -> str: return x\n",
    )
    entries = extract_public_surface(p)
    fps = {e["signature_fingerprint"] for e in entries}
    assert len(fps) == 2
    for e in entries:
        assert e["signature_fingerprint"].startswith("sha256:")
        assert len(e["signature_fingerprint"]) == len("sha256:") + 64


def test_constant_with_annotation(tmp_path: Path) -> None:
    p = _write(tmp_path, "MAX_RETRIES: int = 3\n")
    entries = extract_public_surface(p)
    assert entries[0]["name"] == "MAX_RETRIES"
    assert entries[0]["kind"] == "constant"
