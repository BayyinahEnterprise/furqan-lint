"""Phase G11.3 (an-Naziat / v0.13.0) T10 smoke-test fixture inventory.

Pin the substrate-of-record for the gate11-onnx-smoke-test CI
job per F-NA-4 v1.4 absorption (delta-against-substrate
convention) + T00 step 5 substrate-actual builder discipline.

These three fixtures cover:

1. ONNX builder substrate-actual name pin: ``make_relu_model``
   in tests/fixtures/onnx/builders.py (NOT
   ``make_simple_relu_model`` per v1.6 prompt §5.1 reference;
   T00 step 5 substrate probe confirmed ``make_relu_model``
   is the substrate-actual builder name).

2. Builder produces a valid ModelProto for the smoke-test
   fixture: substrate-attestation that the gate11-onnx-smoke-
   test job's input model loads cleanly.

3. CI workflow YAML pin: gate11-onnx-smoke-test job present
   in .github/workflows/ci.yml parallel to gate11-go-smoke-
   test (al-Mursalat T08) and gate11-rust-smoke-test
   (G11.1) and gate11-smoke-test (G11.0).

Per F-PB-NZ-1 v1.6 absorption: delta-against-substrate
treats this NEW file as contributing +3 fixtures (T00 step
4.1 pinning table T08/T10 row).
"""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("onnx")
pytest.importorskip("rfc8785")


def test_onnx_smoke_test_builder_substrate_actual_name() -> None:
    """T00 step 5 + F-NA-* closure: substrate-actual builder
    name is ``make_relu_model`` (NOT ``make_simple_relu_model``
    per v1.6 prompt §5.1 reference; substrate divergence
    documented during T00 ONNX pre-flight verification per
    docs/g11.3-preflight.md).

    Closes failure mode #5 of §5.1 step 4 (builder API drift
    between prompt reference and substrate-actual)."""
    from tests.fixtures.onnx import builders

    assert hasattr(builders, "make_relu_model"), (
        "T00 step 5 substrate-of-record divergence: "
        "tests/fixtures/onnx/builders.py missing make_relu_model "
        "function"
    )
    # And specifically NOT the v1.6-prompt-referenced name:
    assert not hasattr(builders, "make_simple_relu_model"), (
        "T00 step 5 surfaced make_relu_model as substrate-actual; "
        "make_simple_relu_model was v1.6 prompt §5.1 reference "
        "drift -- preserve substrate-actual"
    )


def test_onnx_smoke_test_builder_produces_valid_model(tmp_path: Path) -> None:
    """T10 + F-NA-* closure: make_relu_model produces a
    ModelProto that loads cleanly under onnx.load. The model
    has one input (x) and one output (y), both FLOAT shape
    (1, 4), with one Relu node. Mirrors the v0.9.x ONNX
    fixture conventions."""
    import onnx
    from tests.fixtures.onnx import builders

    model = builders.make_relu_model(opset_version=14)
    out_path = tmp_path / "smoke_test_fixture.onnx"
    onnx.save(model, str(out_path))

    # Round-trip: save -> load -> assert shape conforms to
    # the documented fixture profile.
    loaded = onnx.load(str(out_path))
    assert loaded.graph.name == "test_relu"
    assert len(loaded.graph.input) == 1
    assert loaded.graph.input[0].name == "x"
    assert len(loaded.graph.output) == 1
    assert loaded.graph.output[0].name == "y"
    assert len(loaded.graph.node) == 1
    assert loaded.graph.node[0].op_type == "Relu"


def test_onnx_smoke_test_ci_workflow_job_present() -> None:
    """T10 closure: .github/workflows/ci.yml contains the
    gate11-onnx-smoke-test job parallel to gate11-smoke-test,
    gate11-rust-smoke-test, gate11-go-smoke-test. Substrate-
    attestation that the CI matrix covers all four substrates
    of the canonical mushaf chain at v0.13.0+.

    The job is documented as push-to-main-only (id-token:
    write) since it exercises ambient OIDC; PR-from-fork
    invocations would lack the OIDC permission per GitHub
    Actions security model.
    """
    ci_yml = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
    assert ci_yml.exists(), "expected .github/workflows/ci.yml present"
    content = ci_yml.read_text(encoding="utf-8")

    assert "gate11-onnx-smoke-test:" in content, (
        "T10 substrate-of-record divergence: .github/workflows/ci.yml "
        "missing gate11-onnx-smoke-test job (parallel to "
        "gate11-go-smoke-test from al-Mursalat T08)"
    )
    # And the four-substrate parity (all four substrate smoke
    # jobs present):
    assert "gate11-smoke-test:" in content
    assert "gate11-rust-smoke-test:" in content
    assert "gate11-go-smoke-test:" in content
    # The ONNX job MUST gate on push-to-main + id-token: write
    # per ambient-OIDC convention:
    onnx_job_pos = content.find("gate11-onnx-smoke-test:")
    onnx_block = content[onnx_job_pos : onnx_job_pos + 2000]
    assert "id-token: write" in onnx_block, (
        "gate11-onnx-smoke-test missing id-token: write permission"
    )
