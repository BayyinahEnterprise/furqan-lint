"""Phase G11.2 (al-Mursalat / v0.12.0) T08 smoke-test fixture inventory pins.

Per al-Mursalat T08 + F5 v1.1 absorption: explicit per-fixture
inventory naming each smoke-test substrate path and its
NEW/EXISTING status. These tests pin presence + structural
shape at the substrate-of-record layer (the actual sign-then-
verify round-trip runs in CI under ambient OIDC and is gated
on push-to-main).

Three pins per al-Mursalat T08 + Co-work T00 §5 substrate
verification record:

1. tests/fixtures/gate11/go_smoke_module.go (NEW at v0.12.0)
2. .github/workflows/ci.yml contains gate11-go-smoke-test
   job (NEW at v0.12.0)
3. ci.yml gate11-go-smoke-test job exercises the dispatch
   path through verification.verify per Route (a1-via-args)
   (asserts the workflow steps reference manifest init +
   manifest verify CLI subcommands)

The pre-existing gate11-smoke-test (Python) and
gate11-rust-smoke-test fixtures are pinned via existing
test_gate11_signing.py + the rust .github/workflows/ci.yml
job (substrate at v0.11.7 + v0.11.8 onwards).
"""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_go_smoke_module_fixture_present() -> None:
    """tests/fixtures/gate11/go_smoke_module.go is pinned at v0.12.0.

    Per al-Mursalat T08 fixture inventory + Co-work T00 §5
    SOURCE-PRESENT substrate verification. The fixture is the
    minimal Go module exercised by gate11-go-smoke-test in CI:
    single public function ``Smoke`` with the canonical
    ``(int, error)`` may-fail signature per Go convention.
    """
    fixture = REPO_ROOT / "tests" / "fixtures" / "gate11" / "go_smoke_module.go"
    assert fixture.is_file(), (
        f"al-Mursalat T08 fixture missing: {fixture} -- the "
        f"gate11-go-smoke-test CI job depends on this substrate "
        f"per fixture inventory"
    )
    # And the shape (one public function with may-fail
    # signature):
    content = fixture.read_text(encoding="utf-8")
    assert "func Smoke" in content, "go_smoke_module.go missing public Smoke function"
    assert "(int, error)" in content, (
        "go_smoke_module.go missing canonical (T, error) " "may-fail signature"
    )
    assert "package smoke" in content, "go_smoke_module.go missing 'package smoke' declaration"


def test_ci_yml_has_gate11_go_smoke_test_job() -> None:
    """``.github/workflows/ci.yml`` declares ``gate11-go-smoke-test``.

    Closes F22 fully at v0.12.0: parallel job exists alongside
    gate11-smoke-test (Python) and gate11-rust-smoke-test
    (Rust); all three exercise the dispatch surface through
    verification.verify per T02 Route (a1-via-args).
    """
    ci_yml = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_yml.is_file(), f"ci.yml not found at {ci_yml}"
    content = ci_yml.read_text(encoding="utf-8")
    assert "gate11-go-smoke-test:" in content, (
        "ci.yml missing gate11-go-smoke-test job; al-Mursalat " "T08 smoke-test parity regression"
    )
    # And the three sibling jobs all present:
    assert "gate11-smoke-test:" in content
    assert "gate11-rust-smoke-test:" in content


def test_gate11_go_smoke_job_exercises_dispatch_path() -> None:
    """The gate11-go-smoke-test CI job invokes the substrate-of-
    record CLI entry points (manifest init + manifest verify)
    per al-Mursalat T02 Route (a1-via-args).

    Substrate-honesty pin: a refactor that accidentally
    rewired the smoke test to call ``Verifier(...).verify_bundle``
    directly (bypassing verification.verify dispatch) would
    silently skip the dispatch consolidation surface this
    phase is meant to exercise. This test asserts the workflow
    body references the canonical CLI subcommands.
    """
    ci_yml = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    content = ci_yml.read_text(encoding="utf-8")
    # Find the gate11-go-smoke-test section:
    go_section_start = content.find("gate11-go-smoke-test:")
    assert go_section_start > 0
    # Take everything until the next top-level YAML key (two-
    # space-indented "  next-job:") to bound the section.
    # Practical heuristic: section continues to EOF if it's
    # the last job, which is the case here.
    go_section = content[go_section_start:]
    # Substrate-honesty assertions: the workflow body
    # exercises the CLI subcommands that route through
    # verification.verify under Route (a1-via-args).
    assert "manifest" in go_section, (
        "gate11-go-smoke-test does not exercise 'manifest' "
        "CLI subcommands; T02 Route (a1-via-args) dispatch "
        "consolidation surface not covered by smoke test"
    )
    assert "init" in go_section
    assert "verify" in go_section
    assert "--expected-identity" in go_section, (
        "gate11-go-smoke-test does not exercise identity-policy "
        "enforcement (CASM-V-035 refuse-without-policy default); "
        "smoke test should pass --expected-identity per the "
        "post-v0.11.5 F24 al-Bayyina C-1 corrective"
    )
