"""Phase G12.0 (al-Basirah / v1.0.0) T03 tests for release.yml T06 step.

Pin the workflow-YAML substrate-of-record: the al-Basirah T06
step in .github/workflows/release.yml that signs the self-
manifest via Sigstore and uploads it as a GitHub Release asset.

Per F-NA-4 v1.4 absorption: this NEW file contributes +3 tests
per T03 working hypothesis.
"""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("rfc8785")


_RELEASE_YML = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"


def test_release_yml_t06_step_generates_self_manifest() -> None:
    """T03 closure: release.yml contains a step that invokes
    python -m furqan_lint.gate11.self_manifest with --version and
    --output flags. Pin the substrate-of-record at workflow YAML
    layer."""
    assert _RELEASE_YML.exists(), "release.yml workflow missing"
    content = _RELEASE_YML.read_text(encoding="utf-8")
    assert "Sign and upload self-attestation manifest" in content, (
        "release.yml T06 step (Sign and upload self-attestation) " "missing"
    )
    assert (
        "python -m furqan_lint.gate11.self_manifest" in content
    ), "release.yml T06 step does not invoke self_manifest CLI"
    assert "--version" in content
    assert "--output self_manifest.json" in content


def test_release_yml_t06_step_signs_via_sigstore() -> None:
    """T03 closure: release.yml T06 step invokes the Sigstore
    signing flow with bundle output. Mirror of the existing PyPI
    Trusted Publishing flow's id-token: write permission."""
    content = _RELEASE_YML.read_text(encoding="utf-8")
    assert (
        "python -m sigstore sign" in content
    ), "release.yml T06 step does not invoke sigstore signing"
    assert "--bundle self_manifest.bundle" in content, (
        "release.yml T06 step does not produce Sigstore bundle " "artifact"
    )
    # The id-token: write permission is granted at the publish job
    # level (line 81); T06 step inherits this:
    assert "id-token: write" in content


def test_release_yml_t06_step_uploads_release_assets() -> None:
    """T03 closure: release.yml T06 step uploads
    self_manifest.json and self_manifest.bundle as GitHub Release
    assets via gh release upload command attached to v${VERSION}.

    Per al-Basirah T04 convention: the released assets are
    discoverable via convention-based URL
    https://github.com/.../releases/download/v${VERSION}/self_manifest.json
    (and .bundle)."""
    content = _RELEASE_YML.read_text(encoding="utf-8")
    assert 'gh release upload "v${VERSION}"' in content or "gh release upload" in content, (
        "release.yml T06 step does not upload assets via gh " "release upload"
    )
    assert "self_manifest.json self_manifest.bundle" in content, (
        "release.yml T06 step does not upload both manifest JSON " "+ Sigstore bundle"
    )
