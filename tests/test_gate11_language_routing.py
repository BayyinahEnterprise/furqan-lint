"""v1.0.1: Gate 11 language routing for Rust and Go.

The ``gate11-rust-smoke-test`` and ``gate11-go-smoke-test`` CI jobs
(push to ``main`` only) had been red since v0.11.x / v0.12.0:

* Verification step 8 extracted the live public surface with the
  Python extractor for every language, so verifying a Rust bundle
  failed with a Python ``SyntaxError`` on valid Rust.
* ``manifest init`` routed only ``.rs`` to a language builder; a
  ``.go`` module fell through to the Python builder and failed the
  same way, and no Go manifest builder existed. ``manifest update``
  routed nothing, so it failed on ``.rs`` and ``.go``.

These tests exercise the same paths without Sigstore (signing is
replaced by a stub payload; signature verification is covered by the
smoke-test jobs, which need ambient OIDC). Each test failed before the
fix with the error the CI jobs showed.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.bundle import Bundle  # noqa: E402
from furqan_lint.gate11.verification import (  # noqa: E402
    CasmVerificationError,
    Verifier,
)

RUST_SRC = "pub fn smoke(a: i32, b: i32) -> i32 { a + b }\n"
GO_SRC = (
    "package smoke\n\n"
    "func Smoke(a int, b int) (int, error) {\n    return a + b, nil\n}\n\n"
    "type Point struct {\n    X int\n}\n\n"
    "func helper() {}\n"
)


def _rust_extras_present() -> bool:
    return (
        importlib.util.find_spec("tree_sitter") is not None
        and importlib.util.find_spec("tree_sitter_rust") is not None
    )


def _go_extras_present() -> bool:
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    binary = Path(spec.origin).parent / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


needs_rust = pytest.mark.skipif(not _rust_extras_present(), reason="[gate11-rust] not installed")
needs_go = pytest.mark.skipif(not _go_extras_present(), reason="goast binary not built")


def _stub_signing(monkeypatch: pytest.MonkeyPatch) -> None:
    import furqan_lint.gate11.signing as signing

    monkeypatch.setattr(signing, "sign_manifest", lambda manifest: {"stub": True})


# --------------------------------------------------------------------- Rust


@needs_rust
def test_rust_step8_uses_rust_extractor(tmp_path: Path) -> None:
    """The CI failure: step 8 on a Rust bundle raised SyntaxError."""
    from furqan_lint.gate11.rust_manifest import build_manifest_rust

    src = tmp_path / "lib.rs"
    src.write_text(RUST_SRC)
    manifest = build_manifest_rust(src)
    Verifier().step8_compare_public_surface(manifest, src)  # must not raise


@needs_rust
def test_rust_step8_still_detects_signature_drift(tmp_path: Path) -> None:
    from furqan_lint.gate11.rust_manifest import build_manifest_rust

    src = tmp_path / "lib.rs"
    src.write_text(RUST_SRC)
    manifest = build_manifest_rust(src)
    src.write_text("pub fn smoke(a: i64, b: i32) -> i32 { 0 }\n")
    with pytest.raises(CasmVerificationError) as exc:
        Verifier().step8_compare_public_surface(manifest, src)
    assert exc.value.code == "CASM-V-051"


@needs_rust
def test_rust_manifest_update_routes_to_rust_builder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``manifest update`` on a .rs module built a Python manifest."""
    from furqan_lint.gate11.cli import cmd_manifest_init, cmd_manifest_update

    _stub_signing(monkeypatch)
    src = tmp_path / "lib.rs"
    src.write_text(RUST_SRC)
    assert cmd_manifest_init([str(src)]) == 0
    src.write_text(RUST_SRC + "pub fn extra() -> i32 { 1 }\n")
    assert cmd_manifest_update([str(src)]) == 0
    bundle = Bundle.read(tmp_path / "lib.rs.furqan.manifest.sigstore")
    assert bundle.manifest.module_identity["language"] == "rust"
    assert bundle.manifest.chain["chain_position"] == 2
    names = {e["name"] for e in bundle.manifest.public_surface["names"]}
    assert {"smoke", "extra"} <= names


# ----------------------------------------------------------------------- Go


@needs_go
def test_go_manifest_init_builds_go_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CI failure: ``manifest init smoke.go`` raised SyntaxError."""
    from furqan_lint.gate11.cli import cmd_manifest_init

    _stub_signing(monkeypatch)
    src = tmp_path / "smoke.go"
    src.write_text(GO_SRC)
    assert cmd_manifest_init([str(src)]) == 0
    bundle = Bundle.read(tmp_path / "smoke.go.furqan.manifest.sigstore")
    m = bundle.manifest
    assert m.module_identity["language"] == "go"
    assert m.public_surface["extraction_method"] == "goast.go-public-surface@v1.0"
    by_name = {e["name"]: e for e in m.public_surface["names"]}
    assert by_name["Smoke"]["kind"] == "function"
    assert by_name["Point"]["kind"] == "struct"
    assert "helper" not in by_name  # unexported
    Verifier().step8_compare_public_surface(m, src)  # must not raise


@needs_go
def test_go_step8_detects_signature_drift_and_removal(tmp_path: Path) -> None:
    from furqan_lint.gate11.go_verification import build_manifest_go

    src = tmp_path / "smoke.go"
    src.write_text(GO_SRC)
    manifest = build_manifest_go(src)
    src.write_text(GO_SRC.replace("a int, b int", "a int64, b int"))
    with pytest.raises(CasmVerificationError) as drift:
        Verifier().step8_compare_public_surface(manifest, src)
    assert drift.value.code == "CASM-V-051"
    src.write_text(GO_SRC.replace("type Point struct {\n    X int\n}\n", ""))
    with pytest.raises(CasmVerificationError) as removed:
        Verifier().step8_compare_public_surface(manifest, src)
    assert removed.value.code == "CASM-V-050"


@needs_go
def test_go_manifest_update_chains(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from furqan_lint.gate11.cli import cmd_manifest_init, cmd_manifest_update

    _stub_signing(monkeypatch)
    src = tmp_path / "smoke.go"
    src.write_text(GO_SRC)
    assert cmd_manifest_init([str(src)]) == 0
    src.write_text(GO_SRC + "\nfunc Extra() int { return 1 }\n")
    assert cmd_manifest_update([str(src)]) == 0
    m = Bundle.read(tmp_path / "smoke.go.furqan.manifest.sigstore").manifest
    assert m.module_identity["language"] == "go"
    assert m.chain["chain_position"] == 2
    assert m.chain["previous_manifest_hash"] is not None


@needs_go
def test_go_variadic_flag_is_part_of_the_fingerprint(tmp_path: Path) -> None:
    from furqan_lint.gate11.go_verification import extract_public_surface_go

    a = tmp_path / "a.go"
    b = tmp_path / "b.go"
    a.write_text("package p\n\nfunc F(xs ...int) int { return 0 }\n")
    b.write_text("package p\n\nfunc F(xs []int) int { return 0 }\n")
    fa = extract_public_surface_go(a)[0]["signature_fingerprint"]
    fb = extract_public_surface_go(b)[0]["signature_fingerprint"]
    assert fa != fb


@needs_go
def test_go_presence_only_names_get_schema_kinds(tmp_path: Path) -> None:
    from furqan_lint.gate11.go_verification import extract_public_surface_go

    src = tmp_path / "k.go"
    src.write_text(
        "package k\n\n"
        "type S struct{ X int }\n"
        "type I interface{ M() }\n"
        "type A = S\n"
        "type N int\n"
        "const C = 1\n"
        "var V = 2\n"
        "func (s S) Do() {}\n"
    )
    kinds = {e["name"]: e["kind"] for e in extract_public_surface_go(src)}
    assert kinds["S"] == "struct"
    assert kinds["I"] == "trait"
    assert kinds["A"] == "alias"
    assert kinds["N"] == "type_alias"
    assert kinds["C"] == "constant"
    assert kinds["V"] == "constant"


@needs_go
def test_go_methods_are_not_mistaken_for_top_level_functions(tmp_path: Path) -> None:
    """goast lists methods under their bare name; a method ``S.Do`` must
    not appear as a top-level function ``Do``."""
    from furqan_lint.gate11.go_verification import extract_public_surface_go

    src = tmp_path / "m.go"
    src.write_text("package m\n\ntype S struct{}\n\nfunc (s S) Do(x int) int { return x }\n")
    names = {e["name"]: e["kind"] for e in extract_public_surface_go(src)}
    assert "Do" not in names
    assert names["S.Do"] == "function"


@needs_go
def test_go_manifest_init_reports_unparseable_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """v1.0.2: the Go builder raises instead of returning None; the CLI
    still exits 1 with a message, not a traceback."""
    from furqan_lint.gate11.cli import cmd_manifest_init

    src = tmp_path / "broken.go"
    src.write_text("package broken\n\nfunc (\n")
    assert cmd_manifest_init([str(src)]) == 1
    assert "Go parse error" in capsys.readouterr().err
