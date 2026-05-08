"""Phase G10.5 (al-Mubin) T04c: pin README Sigstore-CASM section.

After v0.11.1 ships, the README MUST contain:
  - "Sigstore-CASM Gate 11" as a section header
  - "[gate11]" in the install matrix
  - "[gate11-rust]" in the install matrix
  - "SAFETY_INVARIANTS.md" referenced as canonical authority

This pinning test closes finding F15 (Round 27: README does
not document the Sigstore-CASM substrate that shipped in
v0.10.0 + v0.11.0).
"""

from __future__ import annotations

from pathlib import Path

README = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")


def test_sigstore_casm_section_header_present() -> None:
    assert "Sigstore-CASM Gate 11" in README, (
        "README must reference Sigstore-CASM Gate 11 as a "
        "section header so the substrate that shipped in "
        "v0.10.0 + v0.11.0 is visible in the README rather "
        "than only in SECURITY.md and CHANGELOG.md."
    )


def test_gate11_install_row_present() -> None:
    assert 'pip install "furqan-lint[gate11]"' in README, (
        "README install matrix must include the [gate11] " "row (closes F15)."
    )


def test_gate11_rust_install_row_present() -> None:
    assert 'pip install "furqan-lint[gate11-rust]"' in README, (
        "README install matrix must include the [gate11-rust] " "row (closes F15)."
    )


def test_safety_invariants_pointer_present() -> None:
    assert "SAFETY_INVARIANTS.md" in README, (
        "README must point to SAFETY_INVARIANTS.md as the "
        "canonical cryptographic-substrate authority "
        "(closes F15; per Phase G11.A amended_2 T-A2)."
    )
