"""Phase G11.3 (an-Naziat / v0.13.0) T05 tests for _CHECKER_SOURCE_FILES extension.

Pin the v0.13.0 21-entry tuple state:

* Both onnx_signature_canonicalization.py (#10) and
  onnx_verification.py (#11) present in _CHECKER_SOURCE_FILES
* Alphabetical-within-section discipline preserved (F-PA-3 v1.8 +
  F-NA-5 v1.4): "onnx_s" sorts between "module_canonicalization"
  and "onnx_v"; "onnx_v" sorts between "onnx_s" and
  "python_verification"
* Total entry count 19 -> 21 (+2 per substrate-convention parity
  with al-Mursalat T05 pattern pinning BOTH go_signature_canon
  AND go_verification; surfaced as F-CW-NZ-2 MEDIUM during T05
  implementation since prompt v1.6 T05 specified +1 / 20 entries
  inserting only onnx_verification; substrate-convention
  precedent over-rode to preserve rust/go parity)
* compute_checker_set_hash() returns the v0.13.0 canonical hash
  literal
* Changes to onnx_verification.py source bytes change the
  hash (Form A substrate-attestation discipline)

Per F-NA-4 v1.4 absorption + F-PB-NZ-1 v1.6 absorption:
delta-against-substrate convention treats this NEW file as
contributing +5 fixtures (T00 step 4.1 pinning table T05 row;
4 prescribed + 1 diagnostic for F-CW-NZ-2 substrate-convention
divergence).
"""

# ruff: noqa: E402

from __future__ import annotations

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.checker_set_hash import (
    _CHECKER_SOURCE_FILES,
    compute_checker_set_hash,
)

# v0.13.0 canonical checker_set_hash literal (Form A; computed
# AFTER T04 onnx_verification.py + T03 onnx_signature_canonicalization.py
# content commits per F-PB-NZ-5 v1.6 + Perplexity Round 39.5-post-
# absorption P1 timing note). Substrate-extracted at T05
# implementation time on the v0.13.0-an-naziat-v16 branch atop
# v0.12.0 substrate `34f45f8`.
V0_13_0_CHECKER_SET_HASH = "sha256:7800b8bf55b105eaea66e927dd4d6cc04c66661d008d9ef5d194bcad3aef6cad"


def test_v0_13_0_onnx_verification_module_in_checker_source_files() -> None:
    """T05 closure: gate11/onnx_verification.py present in
    _CHECKER_SOURCE_FILES per H-6 propagation defense ONNX-side
    parity."""
    names = {p.name for p in _CHECKER_SOURCE_FILES}
    assert "onnx_verification.py" in names, (
        "T05 substrate-of-record divergence: "
        "gate11/onnx_verification.py NOT pinned in "
        "_CHECKER_SOURCE_FILES"
    )


def test_v0_13_0_onnx_signature_canonicalization_module_in_checker_source_files() -> None:
    """T05 + F-CW-NZ-2 closure: gate11/onnx_signature_canonicalization.py
    present in _CHECKER_SOURCE_FILES per al-Mursalat T05
    substrate-convention precedent (both go_signature_canon AND
    go_verification pinned; same pattern for ONNX per honest-
    asymmetry parity)."""
    names = {p.name for p in _CHECKER_SOURCE_FILES}
    assert "onnx_signature_canonicalization.py" in names, (
        "F-CW-NZ-2 substrate-convention parity violation: "
        "gate11/onnx_signature_canonicalization.py NOT pinned "
        "(al-Mursalat T05 + rust G11.1 baseline pinned BOTH "
        "signature_canonicalization + verification for each "
        "substrate; ONNX should follow same pattern)"
    )


def test_v0_13_0_onnx_module_alphabetical_position() -> None:
    """T05 + F-PA-3 v1.8 + F-NA-5 v1.4 closure: ONNX modules
    appear at canonical alphabetical positions within the
    gate11 section.

    Per F-PA-3 Option (alpha) alphabetical-within-section
    discipline: "onnx_s" sorts between "module_canonicalization"
    (m) and "onnx_v"; "onnx_v" sorts between "onnx_s" and
    "python_verification" (p). The 21-entry interleaved
    enumeration places onnx_signature_canonicalization.py at
    index #10 (zero-indexed #9) and onnx_verification.py at
    index #11 (zero-indexed #10).
    """
    paths = list(_CHECKER_SOURCE_FILES)
    paths_named = [p.name for p in paths]
    assert paths_named[8] == "module_canonicalization.py"
    assert paths_named[9] == "onnx_signature_canonicalization.py", (
        f"position #10 should be onnx_signature_canonicalization.py; " f"got {paths_named[9]!r}"
    )
    assert paths_named[10] == "onnx_verification.py", (
        f"position #11 should be onnx_verification.py; " f"got {paths_named[10]!r}"
    )
    assert paths_named[11] == "python_verification.py"


def test_v0_13_0_canonical_checker_set_hash_pinned() -> None:
    """T05 closure: compute_checker_set_hash() returns the
    v0.13.0 canonical hash literal. Pinned per F-PA-3 v1.8 +
    F-NA-5 v1.4 absorption + F-PB-NZ-5 v1.6 timing note (hash
    literal computed AFTER T03 + T04 content commits).

    Future changes to any pinned source file (including
    onnx_signature_canonicalization.py or onnx_verification.py)
    will fail this test, signaling the developer to update both
    the substrate AND this pinned hash in the same commit
    cycle per Naskh Discipline."""
    actual = compute_checker_set_hash()
    assert actual == V0_13_0_CHECKER_SET_HASH, (
        "v0.13.0 canonical checker_set_hash drift: "
        f"expected {V0_13_0_CHECKER_SET_HASH!r}, "
        f"got {actual!r}. Update V0_13_0_CHECKER_SET_HASH in "
        "this file if substrate change is intentional."
    )


def test_checker_set_hash_changes_when_onnx_verification_source_changes(
    tmp_path,
    monkeypatch,
) -> None:
    """T05 + F-NA-5 v1.4 SOURCE-PRESENT closure: modifying
    onnx_verification.py source bytes produces a different
    digest. Substrate-attestation that the Form A surface
    reflects the ONNX verifier source code (not just its
    file path)."""
    from furqan_lint.gate11 import checker_set_hash as csh

    baseline = compute_checker_set_hash()

    # Build a synthetic _CHECKER_SOURCE_FILES tuple with the
    # onnx_verification.py entry redirected to a different
    # content file in tmp_path; assert the digest differs.
    onnx_v_substitute = tmp_path / "onnx_verification.py"
    onnx_v_substitute.write_text("# byte-different content\n")

    substituted = tuple(
        onnx_v_substitute if p.name == "onnx_verification.py" else p
        for p in csh._CHECKER_SOURCE_FILES
    )
    monkeypatch.setattr(csh, "_CHECKER_SOURCE_FILES", substituted)

    after_swap = csh.compute_checker_set_hash()
    assert after_swap != baseline, (
        "Form A substrate-attestation violation: "
        "swapping onnx_verification.py content did not change "
        "the computed checker_set_hash"
    )
