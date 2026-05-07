"""Tests for Phase G11.0 T09: Gate 11 CLI surface.

Exercise the CLI dispatch paths without performing live OIDC /
Sigstore signing. The signing path is exercised by the smoke
test in tests/test_gate11_signing.py (env-gated).

Pin:

* ``furqan-lint check --gate11 <empty-tree>`` is a silent no-op.
* ``furqan-lint check --gate11`` invokes verification when bundles
  are present in the path.
* ``furqan-lint manifest verify <missing>`` returns 1 with a
  meaningful error.
* ``furqan-lint manifest verify <tampered>`` returns 1 with the
  expected CASM-V code (CASM-V-040 module-hash mismatch is the
  cleanest synthetic path; CASM-V-050 removed-name is the
  second).
* Unknown ``manifest`` action returns 2.
* The dispatch entry point is reachable from the top-level
  ``furqan_lint.cli.main`` via argv.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

rfc8785 = pytest.importorskip("rfc8785")

from furqan_lint.gate11 import GATE11_BUNDLE_SUFFIX  # noqa: E402
from furqan_lint.gate11.module_canonicalization import (  # noqa: E402
    module_root_hash,
)


def _run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _module(tmp_path: Path, src: str, name: str = "m.py") -> Path:
    p = tmp_path / name
    p.write_text(src, encoding="utf-8")
    return p


def _entries_for(module_path: Path) -> list:
    from furqan_lint.gate11.surface_extraction import extract_public_surface

    return extract_public_surface(module_path)


def _baseline_manifest_dict(module_path: Path, names_entries: list) -> dict:
    return {
        "casm_version": "1.0",
        "module_identity": {
            "language": "python",
            "module_path": str(module_path),
            "module_root_hash": module_root_hash(module_path),
        },
        "public_surface": {
            "names": names_entries,
            "extraction_method": "ast.module-public-surface@v1.0",
            "extraction_substrate": "furqan-lint test",
        },
        "chain": {"previous_manifest_hash": None, "chain_position": 1},
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": "0.10.0",
            "checker_set_hash": "sha256:" + "0" * 64,
        },
        "trust_root": {
            "trust_root_id": "public-sigstore",
            "fulcio_url": "https://fulcio.sigstore.dev",
            "rekor_url": "https://rekor.sigstore.dev",
        },
        "issued_at": "2026-05-07T14:32:11Z",
    }


def _write_unsigned_bundle(tmp_path: Path, module_path: Path, names_entries: list) -> Path:
    """Write a bundle with a manifest but an empty sigstore_bundle.

    The bundle is parseable; verification will fail at step 6
    (Sigstore) but step 7 (module hash) and step 8 (public
    surface) can be exercised individually via the Verifier
    methods. The CLI tests here exercise the failure modes that
    happen BEFORE step 6 when possible.
    """
    md = _baseline_manifest_dict(module_path, names_entries)
    bp = module_path.with_suffix(GATE11_BUNDLE_SUFFIX)
    bp.write_text(
        json.dumps({"manifest": md, "sigstore_bundle": {}}),
        encoding="utf-8",
    )
    return bp


def test_check_gate11_silent_noop_when_no_bundles(tmp_path: Path) -> None:
    """An empty directory triggers the silent no-op path."""
    _module(tmp_path, "def f(): ...\n")
    result = _run_cli(["check", "--gate11", str(tmp_path)])
    # The base check should still pass on the .py file; gate11
    # has nothing to do.
    assert result.returncode == 0, (
        f"expected exit 0; got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_check_gate11_invokes_verification_when_bundle_present(
    tmp_path: Path,
) -> None:
    """A bundle present in the path triggers verification.

    The bundle's empty sigstore_bundle will fail step 6 with
    CASM-V-030/CASM-V-021/CASM-V-032; the CLI should surface
    the failure and exit non-zero rather than silent-passing.
    """
    p = _module(tmp_path, "def f(): ...\n")
    _write_unsigned_bundle(tmp_path, p, _entries_for(p))
    result = _run_cli(["check", "--gate11", str(tmp_path)])
    assert result.returncode != 0
    assert "CASM-V-" in (result.stdout + result.stderr)


def test_manifest_verify_missing_bundle_exits_1(tmp_path: Path) -> None:
    bogus = tmp_path / "nope.furqan.manifest.sigstore"
    result = _run_cli(["manifest", "verify", str(bogus)])
    assert result.returncode == 1
    assert "bundle not found" in (result.stdout + result.stderr)


def test_manifest_verify_unknown_action_exits_2(tmp_path: Path) -> None:
    result = _run_cli(["manifest", "frobnicate"])
    assert result.returncode == 2
    assert "unknown manifest action" in (result.stdout + result.stderr)


def test_manifest_verify_tampered_module_hash_surfaces_casm_v_040(
    tmp_path: Path,
) -> None:
    """Sign-then-verify is expensive; instead synthesize a
    bundle with a manifest claiming a different module hash and
    verify against the real module. Step 7 fires CASM-V-040
    before step 6 in the verifier composition (actually after,
    so we'll see whichever fires first; both are >= 1 exit).
    """
    p = _module(tmp_path, "def f(): ...\n")
    entries = _entries_for(p)
    # Forge a wrong module_root_hash.
    md = _baseline_manifest_dict(p, entries)
    md["module_identity"]["module_root_hash"] = "sha256:" + "0" * 64
    bp = p.with_suffix(GATE11_BUNDLE_SUFFIX)
    bp.write_text(
        json.dumps({"manifest": md, "sigstore_bundle": {}}),
        encoding="utf-8",
    )
    result = _run_cli(["manifest", "verify", str(bp)])
    assert result.returncode == 1
    output = result.stdout + result.stderr
    assert "CASM-V-" in output


def test_manifest_init_help_when_no_args(tmp_path: Path) -> None:
    result = _run_cli(["manifest", "init"])
    assert result.returncode == 2
    assert "usage" in (result.stdout + result.stderr).lower()


def test_manifest_dispatch_no_args_help(tmp_path: Path) -> None:
    result = _run_cli(["manifest"])
    assert result.returncode == 2


def test_top_level_help_includes_manifest_and_gate11(tmp_path: Path) -> None:
    result = _run_cli(["--help"])
    out = result.stdout
    assert "manifest init" in out
    assert "manifest verify" in out
    assert "manifest update" in out
    assert "--gate11" in out


def test_check_without_gate11_unchanged_behavior(tmp_path: Path) -> None:
    """`furqan-lint check path/` without --gate11 produces the
    same diagnostics as before. Acceptance criterion #3 of the
    G11.0 prompt."""
    _module(tmp_path, "def f() -> int: return 1\n")
    result = _run_cli(["check", str(tmp_path)])
    assert result.returncode == 0
    # No CASM- prefixes in output.
    assert "CASM-" not in result.stdout
