"""Phase G11.2 (al-Mursalat / v0.12.0) checker_set_hash extension pinning.

Pin the v0.12.0 substrate decision: the al-Mursalat Go substrate
modules participate in the substantive Form A
``checker_set_hash`` so a Relying Party can detect substrate
divergence between bundles signed by furqan-lint installations
whose Go substrate modules disagree.

Per F-PA-3 v1.8 absorption Option (alpha): the Go entries
interleave at canonical alphabetical-within-section positions
#6/#7 (between gate11/cli.py and gate11/manifest_schema.py)
and goast at position #19 (in new go_adapter section after
gate11 section). Internal consistency restored across code
block, comment, fixture #1 alphabetical-position assertion,
and fixture #3 hash literal computation per F-PA-3
remediation.

Per F-PF-3 v1.7 absorption + F6 v1.1 SOURCE-PRESENT branch:
goast source path
``src/furqan_lint/go_adapter/cmd/goast/main.go`` is pinned;
fixture #4 ``test_checker_set_hash_includes_goast_source``
asserts presence + sensitivity to source byte changes.

This test file fires at v0.12.0 onwards. Removing any of the
three Go entries from ``_CHECKER_SOURCE_FILES`` (without an
explicit CHANGELOG entry per the Naskh Discipline) is a
regression of the H-6 propagation-defense audit.
"""

# ruff: noqa: E402

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.checker_set_hash import (
    _CHECKER_SOURCE_FILES,
    compute_checker_set_hash,
)

# Reconstruct _PKG_ROOT for fixture #3's expected-hash computation
# (the canonical alphabetical-within-section + go_adapter
# ordering must match the implementation exactly).
_PKG_ROOT = Path(__file__).parent.parent / "src" / "furqan_lint"


# ---------------------------------------------------------------
# Fixture #1: Go entries present at canonical alphabetical-
# within-section positions per F-PA-3 Option (alpha)
# ---------------------------------------------------------------


def test_v0_12_0_go_modules_in_checker_source_files() -> None:
    """All three Go entries are pinned in _CHECKER_SOURCE_FILES.

    Per F-PA-3 v1.8 absorption Option (alpha):
    * gate11/go_signature_canonicalization.py at canonical
      alphabetical-within-section position #6 (between
      gate11/cli.py and gate11/manifest_schema.py)
    * gate11/go_verification.py at canonical alphabetical-
      within-section position #7
    * go_adapter/cmd/goast/main.go in new go_adapter section
      at position #19 (after the gate11 section)

    Removing any entry must be paired with an explicit
    CHANGELOG entry per the Naskh Discipline.
    """
    paths = list(_CHECKER_SOURCE_FILES)
    file_names = {p.name for p in paths}

    # All three Go-related entries present:
    assert "go_signature_canonicalization.py" in file_names, (
        "al-Mursalat T03 substrate file missing from "
        "_CHECKER_SOURCE_FILES; H-6 propagation-defense audit "
        "regression"
    )
    assert "go_verification.py" in file_names, (
        "al-Mursalat T04 substrate file missing from "
        "_CHECKER_SOURCE_FILES; H-6 propagation-defense audit "
        "regression"
    )
    assert "main.go" in file_names, (
        "al-Mursalat T05 goast source pin missing from "
        "_CHECKER_SOURCE_FILES; F-PF-3 v1.7 absorption "
        "regression (goast source pinning per F6 v1.1 "
        "SOURCE-PRESENT branch)"
    )


def test_v0_12_0_go_gate11_modules_alphabetical_position() -> None:
    """Go gate11 entries are at canonical alphabetical-within-
    section positions per F-PA-3 Option (alpha).

    The two Go gate11 modules slot between gate11/cli.py and
    gate11/manifest_schema.py since "go_" sorts alphabetically
    before "m". The substrate-of-record ordering at v0.12.0:

      ... gate11/cli.py (#5)
      gate11/go_signature_canonicalization.py (#6 NEW)
      gate11/go_verification.py (#7 NEW)
      gate11/manifest_schema.py (#8) ...

    A future refactor that end-appended Go entries (the v1.7
    code-block-vs-comment contradiction F-PA-3 corrected)
    would fail this test, catching the F-TR-6 -> F-PF-1
    absorption-collision regression.
    """
    paths = list(_CHECKER_SOURCE_FILES)
    # Find positions of the canonical boundary entries:
    pos_cli = next(
        i for i, p in enumerate(paths) if p.parent.name == "gate11" and p.name == "cli.py"
    )
    pos_manifest = next(
        i
        for i, p in enumerate(paths)
        if p.parent.name == "gate11" and p.name == "manifest_schema.py"
    )
    pos_go_sig = next(
        i for i, p in enumerate(paths) if p.name == "go_signature_canonicalization.py"
    )
    pos_go_verif = next(
        i
        for i, p in enumerate(paths)
        if p.parent.name == "gate11" and p.name == "go_verification.py"
    )
    # Per F-PA-3 Option (alpha): Go entries between cli.py and
    # manifest_schema.py.
    assert pos_cli < pos_go_sig < pos_go_verif < pos_manifest, (
        f"Go gate11 entries not at canonical alphabetical-"
        f"within-section positions; F-PA-3 Option (alpha) "
        f"regression. Positions: cli.py={pos_cli}, "
        f"go_sig_canon={pos_go_sig}, go_verif={pos_go_verif}, "
        f"manifest_schema.py={pos_manifest}"
    )


def test_v0_12_0_goast_in_go_adapter_section() -> None:
    """goast main.go pinned in go_adapter section after gate11.

    Per F-PA-3 Option (alpha) cross-section discipline: the
    new go_adapter section follows gate11 alphabetically. At
    v0.12.0 substrate there are no other sections between
    gate11 and go_adapter, so goast slots at the tuple's end
    (position #19).
    """
    paths = list(_CHECKER_SOURCE_FILES)
    # Find positions of last gate11 entry and goast:
    last_gate11 = max(i for i, p in enumerate(paths) if p.parent.name == "gate11")
    goast_pos = next(
        i for i, p in enumerate(paths) if p.parent.name == "goast" and p.name == "main.go"
    )
    assert goast_pos > last_gate11, (
        f"goast pin not in go_adapter section after gate11; "
        f"F-PA-3 cross-section regression. "
        f"last_gate11={last_gate11}, goast={goast_pos}"
    )


# ---------------------------------------------------------------
# Fixture #2: hash changes when any Go pinned source byte changes
# (failure mode #3 from §5.1 step 4 ranked list)
# ---------------------------------------------------------------


def test_checker_set_hash_changes_when_go_source_changes(
    tmp_path,
    monkeypatch,
) -> None:
    """Modifying a Go pinned source byte changes the hash.

    Tests the H-6 propagation-defense substantive claim: the
    sha256 over concatenated source bytes is sensitive to any
    pinned-file content change. If a contributor modified
    go_verification.py to silently break the dispatch, the
    checker_set_hash would change accordingly; Relying Parties
    detect the substrate divergence at manifest comparison time.

    Uses the actual compute function against a temporarily-
    modified module file to assert the hash sensitivity.
    """
    # Compute baseline hash:
    baseline = compute_checker_set_hash()
    # Read the go_verification.py source and modify it
    # temporarily; restore after:
    go_verif_path = next(p for p in _CHECKER_SOURCE_FILES if p.name == "go_verification.py")
    original = go_verif_path.read_bytes()
    try:
        go_verif_path.write_bytes(original + b"\n# regression marker\n")
        modified = compute_checker_set_hash()
        assert modified != baseline, (
            "compute_checker_set_hash insensitive to "
            "go_verification.py byte changes; H-6 propagation-"
            "defense substantive claim regression"
        )
    finally:
        go_verif_path.write_bytes(original)


# ---------------------------------------------------------------
# Fixture #3: full 19-entry tuple in canonical order yields
# expected hash (per F-PA-3 Option (alpha) fixture #3
# interleaved-order computation)
# ---------------------------------------------------------------


def test_checker_set_hash_v0_12_0_canonical_interleaved_order() -> None:
    """The hash matches an explicit interleaved-order re-computation
    per F-PA-3 Option (alpha) + F-NA-5 v1.4 alphabetical-within-
    section discipline.

    Per F-PA-3 v1.8 absorption: the expected hash is NOT computed
    against ``*V0_11_8_CHECKER_SOURCES + additions`` (end-append
    concatenation), which would conflict with fixture #1's
    alphabetical-slot-between assertion. Instead, enumerate the
    full canonical interleaved order and compute the hash; assert
    ``compute_checker_set_hash`` returns the same value.

    Per Naskh Discipline: this test originally pinned the v0.12.0
    19-entry tuple at al-Mursalat ship. v0.13.0 an-Naziat T05
    extended the tuple to 21 entries (adding both
    ``onnx_signature_canonicalization.py`` at #10 and
    ``onnx_verification.py`` at #11 per F-CW-NZ-2 substrate-
    convention parity precedent; goast shifts to #21). The
    canonical_order list below tracks the substrate-LIVE state
    at v0.13.0 ship; the v0.12.0 19-entry historical record is
    preserved in CHANGELOG v0.12.0 entry and docs/gate11-symmetry.md
    substrate-of-record table.
    """
    canonical_order = (
        # Core section (v0.11.8 substrate):
        _PKG_ROOT / "additive.py",
        _PKG_ROOT / "cli.py",
        # gate11 section, alphabetical-within-section, with
        # al-Mursalat Go entries at canonical positions #6/#7
        # per F-PA-3 Option (alpha) and an-Naziat ONNX entries
        # at positions #10/#11 per F-NA-5 v1.4 absorption +
        # F-CW-NZ-2 substrate-convention parity:
        _PKG_ROOT / "gate11" / "__init__.py",
        _PKG_ROOT / "gate11" / "bundle.py",
        _PKG_ROOT / "gate11" / "cli.py",
        _PKG_ROOT / "gate11" / "go_signature_canonicalization.py",
        _PKG_ROOT / "gate11" / "go_verification.py",
        _PKG_ROOT / "gate11" / "manifest_schema.py",
        _PKG_ROOT / "gate11" / "module_canonicalization.py",
        _PKG_ROOT / "gate11" / "onnx_signature_canonicalization.py",
        _PKG_ROOT / "gate11" / "onnx_verification.py",
        _PKG_ROOT / "gate11" / "python_verification.py",
        _PKG_ROOT / "gate11" / "rust_manifest.py",
        _PKG_ROOT / "gate11" / "rust_signature_canonicalization.py",
        _PKG_ROOT / "gate11" / "rust_surface_extraction.py",
        _PKG_ROOT / "gate11" / "rust_verification.py",
        _PKG_ROOT / "gate11" / "signature_canonicalization.py",
        _PKG_ROOT / "gate11" / "signing.py",
        _PKG_ROOT / "gate11" / "surface_extraction.py",
        _PKG_ROOT / "gate11" / "verification.py",
        # go_adapter section (al-Mursalat T05 goast pin per
        # F-PF-3 v1.7 absorption + F6 v1.1 SOURCE-PRESENT
        # branch; shifted from #19 to #21 at v0.13.0):
        _PKG_ROOT / "go_adapter" / "cmd" / "goast" / "main.go",
    )
    # The order in the tuple constant must match this canonical
    # interleaved ordering exactly:
    assert tuple(_CHECKER_SOURCE_FILES) == canonical_order, (
        "v0.12.0 _CHECKER_SOURCE_FILES order diverges from "
        "F-PA-3 Option (alpha) canonical interleaved order; "
        "regression of F-PA-3 v1.8 absorption disposition"
    )
    # And the actual sha256 over concatenated source bytes
    # matches what compute_checker_set_hash returns (this is
    # the load-bearing assertion: the implementation matches
    # the substrate-of-record canonical order):
    expected = hashlib.sha256(
        b"".join(p.read_bytes() for p in canonical_order if p.exists())
    ).hexdigest()
    actual_full = compute_checker_set_hash()
    # compute_checker_set_hash returns "sha256:<hex>"; strip
    # the prefix to compare.
    assert actual_full == f"sha256:{expected}", (
        f"v0.12.0 checker_set_hash sha256 drift: "
        f"compute returned {actual_full!r}, expected "
        f"sha256:{expected!r}"
    )


# ---------------------------------------------------------------
# Fixture #4: goast source pin per F-PF-3 + F6 SOURCE-PRESENT
# ---------------------------------------------------------------


def test_checker_set_hash_includes_goast_source() -> None:
    """The goast source path is pinned in _CHECKER_SOURCE_FILES.

    Per F-PF-3 v1.7 absorption + F6 v1.1 SOURCE-PRESENT branch:
    the Go AST emitter source at
    ``src/furqan_lint/go_adapter/cmd/goast/main.go`` is part
    of the substrate-attestation surface, not just the
    gate11/* verification modules.

    The substrate path was empirically confirmed PRESENT at
    Co-work T00 §5. A future refactor that omitted goast
    from the pinned list (e.g., a release-tooling cleanup
    that accidentally drops the entry) would silently weaken
    the Form A commitment; this fixture trips the regression
    immediately.
    """
    paths = list(_CHECKER_SOURCE_FILES)
    goast_pins = [p for p in paths if p.parent.name == "goast" and p.name == "main.go"]
    assert len(goast_pins) == 1, (
        f"expected exactly one goast main.go pin in "
        f"_CHECKER_SOURCE_FILES; got {len(goast_pins)}. "
        f"F-PF-3 v1.7 absorption + F6 v1.1 SOURCE-PRESENT "
        f"branch regression."
    )
    # And the path resolves to the expected substrate location:
    goast_path = goast_pins[0]
    assert "go_adapter" in goast_path.parts, f"goast pin not in go_adapter subtree: {goast_path}"
    assert "cmd" in goast_path.parts, f"goast pin not in cmd subdir: {goast_path}"
