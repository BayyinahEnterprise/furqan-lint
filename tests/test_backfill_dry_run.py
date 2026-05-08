"""Phase G11.0.1 (at-Tawbah) T08 / F18 flagship closure: pin the
backfill_github_releases.py --dry-run / --apply contract.

The Round 28 audit observed the runbook's --dry-run invocation
creating 12 Release objects because the pre-v0.11.2 script
silently no-op'd --dry-run and called gh release create
unconditionally. v0.11.2 closes the gap by requiring an
explicit mutually-exclusive --dry-run / --apply flag; the
no-flag invocation now exits 2 with argparse usage rather
than silently mutating live state.

This is the structural-honesty thesis applied to the project's
own scripts: the documented surface claim must match the
substrate behavior.
"""

# ruff: noqa: E402, SIM115

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parent.parent / "scripts" / "backfill_github_releases.py"


def test_no_flag_exits_2_with_usage():
    """Default no-flag invocation MUST exit 2 with argparse
    usage; MUST NOT silently execute backfill.
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=SCRIPT.parent.parent,
    )
    assert proc.returncode == 2, (
        f"expected exit 2 (argparse required-arg failure); "
        f"got {proc.returncode} with stdout={proc.stdout!r} "
        f"stderr={proc.stderr!r}"
    )
    assert "--dry-run" in proc.stderr
    assert "--apply" in proc.stderr


def test_both_flags_rejected_as_mutually_exclusive():
    """--dry-run and --apply together MUST be rejected by
    argparse as ambiguous configuration.
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run", "--apply"],
        capture_output=True,
        text=True,
        cwd=SCRIPT.parent.parent,
    )
    assert proc.returncode == 2
    assert "not allowed with argument" in proc.stderr


def test_dry_run_makes_no_subprocess_calls():
    """--dry-run MUST NOT call gh release create. Any
    subprocess.run invocation against gh in --dry-run mode is
    a regression of the F18 closure.
    """
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        import importlib

        import backfill_github_releases as mod

        importlib.reload(mod)
        with mock.patch.object(mod.subprocess, "run") as mocked:
            mocked.return_value = mock.Mock(returncode=0, stdout="", stderr="")
            rc = mod.main(["--dry-run"])
            assert rc == 0
            # Verify NO subprocess.run call invoked `gh release create`.
            for call in mocked.call_args_list:
                cmd = call.args[0] if call.args else call.kwargs.get("args", [])
                assert (
                    "gh" not in cmd[:2] or "release" not in cmd
                ), f"--dry-run must not call gh release create; saw {cmd}"
    finally:
        sys.path.remove(str(SCRIPT.parent))


def test_dry_run_lists_expected_versions():
    """--dry-run output must enumerate the in-scope version set
    so the operator can preview before committing to --apply.
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run"],
        capture_output=True,
        text=True,
        cwd=SCRIPT.parent.parent,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "DRY-RUN" in out
    # The 12-version backfill scope per the prompt's structured
    # table: v0.8.2..v0.11.0, excluding v0.11.1+ workflow-managed
    # versions (F19 incidental closure).
    for v in (
        "0.11.0",
        "0.10.0",
        "0.9.4",
        "0.8.2",
    ):
        assert f"v{v}" in out, f"--dry-run output missing v{v}"
    assert "v0.11.1" not in out, (
        "F19 incidental closure regressed: v0.11.1 (workflow-"
        "managed) must NOT appear in backfill scope."
    )


def test_workflow_managed_floor_excludes_v0_11_1_and_later():
    """F19 incidental closure: the version filter MUST exclude
    v0.11.1 and later because release.yml T02 creates Release
    objects on tag push for those versions.
    """
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        import importlib

        import backfill_github_releases as mod

        importlib.reload(mod)
        versions = mod._extract_versions_from_changelog()
        assert "0.11.1" not in versions
        assert "0.11.0" in versions
    finally:
        sys.path.remove(str(SCRIPT.parent))
