"""Phase G12.0 (al-Basirah / v1.0.0) T07 self-smoke-test fixture inventory.

Pin the substrate-of-record for the gate11-self-smoke-test CI job
per F-NA-4 v1.4 absorption (delta-against-substrate convention).
Three fixtures cover: (a) fixture self-manifest JSON; (b) fixture
Sigstore bundle stub; (c) CI workflow YAML pin.

Per F-PB-NZ-1 v1.6 absorption: this NEW file contributes +3
fixtures per T07 working hypothesis.

Per §5.1 step 4 failure mode #5 of al-Basirah dispatch prompt:
the fixture identity differs from production release identity;
smoke test passing does NOT prove real-world Relying-Party
verification will succeed against production release. Closure
of failure mode #5 requires post-ship verification by an
external party using production identity.
"""

# ruff: noqa: E402

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("rfc8785")


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "gate11"
_CI_YAML = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"


def test_self_smoke_test_fixture_manifest_present() -> None:
    """T07 closure: tests/fixtures/gate11/self_manifest_smoke_v1_0.json
    present and is a valid CASM v1.0 manifest. Substrate-of-record
    pin for the fixture used by gate11-self-smoke-test (production
    flow at release.yml T06 generates an analogous manifest at
    release time)."""
    manifest_path = _FIXTURE_DIR / "self_manifest_smoke_v1_0.json"
    assert manifest_path.exists(), (
        f"T07 substrate-of-record violation: fixture self-manifest "
        f"missing at {manifest_path}"
    )
    from furqan_lint.gate11.manifest_schema import Manifest

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    parsed = Manifest.from_dict(data)
    assert parsed.module_identity["language"] == "python", (
        "T07 closure violation: fixture manifest language is not "
        "'python' (self-attestation dispatches to _verify_python "
        "via function-local _LANGUAGE_DISPATCH)"
    )
    assert parsed.casm_version == "1.0"


def test_self_smoke_test_fixture_bundle_present() -> None:
    """T07 closure: fixture Sigstore bundle stub present alongside
    manifest. Production bundle generated at release.yml T06 via
    `python -m sigstore sign`; fixture is a stub for inventory
    pinning at this CI layer (the actual Sigstore-signing flow is
    exercised by the gate11-self-smoke-test workflow at CI
    runtime, not by this static-fixture test)."""
    bundle_path = _FIXTURE_DIR / "self_manifest_smoke_v1_0.bundle"
    assert bundle_path.exists(), (
        f"T07 substrate-of-record violation: fixture bundle stub "
        f"missing at {bundle_path}"
    )
    # Bundle stub is non-empty (production bundle would be a
    # binary Sigstore Bundle protobuf-serialized JSON; the stub
    # is a placeholder marker):
    assert bundle_path.stat().st_size > 0


def test_self_smoke_test_ci_workflow_job_present() -> None:
    """T07 closure: .github/workflows/ci.yml contains the
    gate11-self-smoke-test job parallel to the four prior
    gate11 smoke jobs. Substrate-attestation that the CI matrix
    covers all five surfaces at v1.0+: four-substrate parity
    (Python / Rust / Go / ONNX) plus self-attestation.
    """
    assert _CI_YAML.exists()
    content = _CI_YAML.read_text(encoding="utf-8")
    assert "gate11-self-smoke-test:" in content, (
        "T07 substrate-of-record violation: ci.yml missing "
        "gate11-self-smoke-test job (parallel to four prior "
        "gate11 smoke jobs)"
    )
    # Five-surface parity at v1.0+:
    assert "gate11-smoke-test:" in content
    assert "gate11-rust-smoke-test:" in content
    assert "gate11-go-smoke-test:" in content
    assert "gate11-onnx-smoke-test:" in content
    # The self job MUST have id-token: write per ambient-OIDC
    # convention:
    self_pos = content.find("gate11-self-smoke-test:")
    self_block = content[self_pos : self_pos + 2500]
    assert "id-token: write" in self_block
    # And the job invokes the self_manifest module + sigstore:
    assert "python -m furqan_lint.gate11.self_manifest" in self_block
    assert "python -m sigstore sign" in self_block
