"""Phase G12.0 (al-Basirah / v1.0.0) T02 tests for self-manifest generation.

Exercises gate11/self_manifest.py + gate11/_pinned_checker_sources_self.py.

Per F-NA-4 v1.4 absorption: delta-against-substrate convention
treats this NEW file as contributing +5 fixtures per T02 working
hypothesis.

Per F-BA-substrate-conflict-1 v1.0.0 closure: CASM-V code for
self-attestation-failure is CASM-V-072 (substrate-actual), NOT
the prompt-cited CASM-V-040 (which is in-use at v0.10.0+ baseline
for module_root_hash mismatch).
"""

# ruff: noqa: E402

from __future__ import annotations

import hashlib

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11._pinned_checker_sources_self import (
    PINNED_CHECKER_SOURCES_SELF,
)
from furqan_lint.gate11.manifest_schema import Manifest
from furqan_lint.gate11.self_manifest import (
    compute_self_checker_set_hash,
    generate_self_manifest,
)


def test_self_manifest_generation_produces_valid_schema() -> None:
    """T02 closure: generated self-manifest passes Manifest.from_dict
    schema validation. Mirror of test_schema_accepts_language_python
    pattern at the self-attestation surface."""
    manifest_dict = generate_self_manifest("1.0.0")
    # Should not raise:
    manifest = Manifest.from_dict(manifest_dict)
    assert manifest.module_identity["language"] == "python"
    assert manifest.casm_version == "1.0"


def test_self_manifest_checker_set_hash_form_a() -> None:
    """T02 closure: the checker_set_hash in the generated manifest
    matches sha256 of pinned-source-files concatenation. Form A
    discipline per H-6 propagation defense (mirror of
    test_v0_13_0_canonical_checker_set_hash_pinned for the
    self-attestation pinned list)."""
    manifest_dict = generate_self_manifest("1.0.0")
    actual_hash = manifest_dict["linter_substrate_attestation"]["checker_set_hash"]

    # Re-compute independently:
    expected = hashlib.sha256()
    for source_path in PINNED_CHECKER_SOURCES_SELF:
        expected.update(source_path.read_bytes())
    expected_hex = f"sha256:{expected.hexdigest()}"

    assert actual_hash == expected_hex, (
        "T02 Form A discipline violation: generate_self_manifest "
        "checker_set_hash does not match independently-computed "
        "sha256 over PINNED_CHECKER_SOURCES_SELF concatenation"
    )
    assert actual_hash == compute_self_checker_set_hash()


def test_self_manifest_public_surface_canonical_stable() -> None:
    """T02 closure: generating the self-manifest twice produces
    byte-identical canonical strings. Determinism is load-bearing
    for Sigstore signing (the bytes signed at release time MUST
    be the bytes a Relying Party verifies)."""
    manifest_1 = generate_self_manifest("1.0.0")
    manifest_2 = generate_self_manifest("1.0.0")
    # Compare via Manifest.to_canonical_bytes for byte-stable check:
    m1 = Manifest.from_dict(manifest_1)
    m2 = Manifest.from_dict(manifest_2)
    assert m1.to_canonical_bytes() == m2.to_canonical_bytes(), (
        "T02 determinism violation: two generations of self-manifest "
        "produce divergent canonical bytes (Sigstore signing would "
        "drift between release.yml T06 invocation and Relying-Party "
        "verify-self verification)"
    )


def test_self_manifest_includes_v1_0_self_attestation_modules() -> None:
    """T02 closure + §5.1 step 4 failure mode #3 closure: the pinned
    source list contains both _pinned_checker_sources_self.py and
    self_manifest.py.

    Mechanical enforcement: if a developer adds a new self-attestation
    module but forgets to update the pinned list, the manifest's
    checker_set_hash claim would not match the substrate at verify-
    self time. This test prevents that drift at PR review."""
    pinned_names = {p.name for p in PINNED_CHECKER_SOURCES_SELF}
    assert "_pinned_checker_sources_self.py" in pinned_names, (
        "T02 substrate-of-record violation: "
        "_pinned_checker_sources_self.py not in PINNED_CHECKER_SOURCES_SELF; "
        "§5.1 step 4 failure mode #3 (checker-set-hash drift) "
        "mechanical-enforcement broken"
    )
    assert "self_manifest.py" in pinned_names, (
        "T02 substrate-of-record violation: "
        "self_manifest.py not in PINNED_CHECKER_SOURCES_SELF; "
        "§5.1 step 4 failure mode #3 mechanical-enforcement broken"
    )


def test_self_manifest_changes_when_checker_changes(tmp_path, monkeypatch) -> None:
    """T02 closure: modifying a pinned source byte produces a
    different self-manifest hash. Substrate-attestation that the
    Form A surface reflects the checker code's integrity."""
    from furqan_lint.gate11 import _pinned_checker_sources_self as pin_mod

    baseline_hash = compute_self_checker_set_hash()

    # Substitute one pinned source with a byte-different file:
    substitute = tmp_path / "self_manifest.py"
    substitute.write_text("# byte-different content for substrate-attestation test\n")

    substituted = tuple(
        substitute if p.name == "self_manifest.py" else p for p in PINNED_CHECKER_SOURCES_SELF
    )
    monkeypatch.setattr(pin_mod, "PINNED_CHECKER_SOURCES_SELF", substituted)

    # Re-import via the same monkeypatched module:
    import furqan_lint.gate11.self_manifest as sm_mod

    monkeypatch.setattr(sm_mod, "PINNED_CHECKER_SOURCES_SELF", substituted)

    after_swap = sm_mod.compute_self_checker_set_hash()
    assert after_swap != baseline_hash, (
        "T02 Form A substrate-attestation violation: swapping "
        "self_manifest.py content did not change the computed "
        "self-attestation hash (the integrity-attestation property "
        "holds: substrate change MUST produce hash change)"
    )
