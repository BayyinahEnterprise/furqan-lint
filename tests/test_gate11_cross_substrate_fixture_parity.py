"""Phase G11.4 (Tasdiq al-Bayan / v0.14.0) T03 fixture parity tests.

Exercises the build_cross_substrate_fixtures(concern_name) helper
that produces structurally-parallel fixtures across all four
gate11 substrates per Tasdiq al-Bayan T03 spec. The fixtures
share the same conceptual content (single public name; same
identity policy; same conceptual function: binary-add or
equivalent ONNX graph node).

Per F-NA-4 v1.4 absorption: delta-against-substrate convention
treats this NEW file as contributing +4 fixtures (T00 step 4.1
pinning table T03 row).

Per F-TAB-1 MEDIUM closure (pre-dispatch absorption): the
fixture root is tests/fixtures/gate11/cross_substrate/ matching
the existing tests/fixtures/gate11/ gate11-fixture-root
convention at v0.13.0.
"""

# ruff: noqa: E402

from __future__ import annotations

import json

import pytest

pytest.importorskip("rfc8785")

from tests.fixtures.gate11.cross_substrate._build import (
    build_cross_substrate_fixtures,
)

_EXPECTED_SUBSTRATES = {"python", "rust", "go", "onnx"}


def test_build_helper_produces_all_four_substrates(tmp_path, monkeypatch) -> None:
    """T03 closure: build_cross_substrate_fixtures(concern) returns
    a dict with keys for all four substrates. Mechanical enforcement
    of the four-substrate-parity claim at the fixture-construction
    layer."""
    fixtures = build_cross_substrate_fixtures("identity_policy_default")
    assert set(fixtures.keys()) == _EXPECTED_SUBSTRATES, (
        "T03 substrate-parity violation: fixture helper returned "
        f"keys {set(fixtures.keys())!r}; expected exactly "
        f"{_EXPECTED_SUBSTRATES!r}"
    )


def test_build_helper_produces_parallel_identity_files() -> None:
    """T03 closure: each concern directory contains a SHARED_IDENTITY
    file with the same identity string across all four substrates.
    The single identity file makes the parity claim mechanically
    enforceable: a Relying Party verifying any of the four
    substrate fixtures uses the same identity policy."""
    build_cross_substrate_fixtures("identity_policy_enforcement")
    from pathlib import Path

    identity_path = (
        Path(__file__).parent
        / "fixtures"
        / "gate11"
        / "cross_substrate"
        / "identity_policy_enforcement"
        / "SHARED_IDENTITY"
    )
    assert identity_path.exists(), (
        "T03 substrate-parity violation: SHARED_IDENTITY file " "missing from concern directory"
    )
    # The identity is the canonical BayyinahEnterprise GitHub
    # Actions OIDC SAN pattern (matches the smoke-test convention
    # at gate11-*-smoke-test CI jobs from prior phases):
    content = identity_path.read_text(encoding="utf-8")
    assert "BayyinahEnterprise" in content, (
        "T03 brand-canonical violation: identity does not name " "BayyinahEnterprise"
    )
    assert "furqan-lint" in content


def test_build_helper_produces_parallel_policy_files() -> None:
    """T03 closure: each concern directory contains a
    SHARED_POLICY.json file with valid JSON that includes
    expected_identity (the central policy enforcement field
    per C-1 closure across the chain) and expected_issuer
    (Sigstore ambient OIDC convention).
    """
    build_cross_substrate_fixtures("trusted_root_threading")
    from pathlib import Path

    policy_path = (
        Path(__file__).parent
        / "fixtures"
        / "gate11"
        / "cross_substrate"
        / "trusted_root_threading"
        / "SHARED_POLICY.json"
    )
    assert policy_path.exists()
    content = policy_path.read_text(encoding="utf-8")
    parsed = json.loads(content)
    assert "expected_identity" in parsed, (
        "T03 closure regression: SHARED_POLICY.json missing "
        "expected_identity field (CASM-V-032/035 enforcement "
        "layer regression)"
    )
    assert "expected_issuer" in parsed
    assert parsed["expected_issuer"].startswith("https://"), (
        "T03 policy convention violation: expected_issuer "
        "should be an HTTPS URL (ambient-OIDC convention)"
    )


def test_build_helper_concern_directory_structure_consistent() -> None:
    """T03 closure: building two different concern fixture sets
    produces the same directory file structure. Mechanical
    enforcement of structural parity across concerns: a future
    addition of a new concern automatically inherits the
    four-substrate parallel-fixture structure."""
    fixtures_a = build_cross_substrate_fixtures("force_refresh_plumbing")
    fixtures_b = build_cross_substrate_fixtures("checker_set_hash_form_a")

    # Both concerns return the same set of substrate keys:
    assert set(fixtures_a.keys()) == set(fixtures_b.keys())

    # Both concern directories have the same file-name structure:
    files_a = {p.name for p in fixtures_a["python"].parent.iterdir()}
    files_b = {p.name for p in fixtures_b["python"].parent.iterdir()}
    # Drop any optional ONNX file when onnx not installed (handled
    # lazily in the helper):
    common_files = files_a & files_b
    expected_files = {
        "python_module.py",
        "rust_crate.rs",
        "go_module.go",
        "SHARED_IDENTITY",
        "SHARED_POLICY.json",
    }
    assert expected_files.issubset(common_files), (
        f"T03 concern-directory structural-parity violation: "
        f"common files {common_files!r} missing expected "
        f"{expected_files!r}"
    )
