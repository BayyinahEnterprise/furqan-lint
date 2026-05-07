"""Phase G10.5 (al-Mubin) T04b: pin README closure-sections retirement.

After v0.11.1 ships, the README MUST NOT contain any
``## Closed in v`` headers. CHANGELOG.md is the canonical
closure ledger; the README mirror was retired per framework
section 10.2 retirement procedure.
"""

from __future__ import annotations

from pathlib import Path


def test_no_closed_in_v_headers_remain() -> None:
    text = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")
    offenders = [ln for ln in text.splitlines() if ln.startswith("## Closed in v")]
    assert offenders == [], (
        "README closure-sections retirement (T04b) regressed: "
        f"found {len(offenders)} '## Closed in v' headers: "
        f"{offenders[:3]}. Per framework section 10.2 retirement "
        "procedure, these must remain absent; CHANGELOG.md is the "
        "canonical closure ledger."
    )


def test_closure_history_pointer_present() -> None:
    text = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")
    assert "## Closure history" in text
    assert "[CHANGELOG.md](CHANGELOG.md)" in text
