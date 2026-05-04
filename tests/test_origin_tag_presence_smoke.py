"""Smoke-test for ``scripts/verify_origin_tags.py`` (v0.8.4 §7.12).

The production gate runs in CI's lint job (where it has network
access to query origin via ``git ls-remote --tags origin``). The
pytest suite must remain hermetic; this smoke-test only exercises
the script's ``--dry-run`` mode, which parses ``CHANGELOG.md`` and
prints the expected tag list to stdout WITHOUT making any network
call.

What the smoke-test pins:

* The script is invokable via ``python scripts/verify_origin_tags.py``.
* ``--dry-run`` exits 0.
* The output contains the versions any CHANGELOG at v0.8.4 ship time
  will have, modulo the v0.7.4 absorbed-into exclusion. Concretely:
  ``v0.7.3``, ``v0.8.3``, ``v0.8.4`` (three anchor pins).
* The output does NOT contain ``v0.7.4`` (absorbed-into exclusion).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "verify_origin_tags.py"


def test_origin_tag_script_dry_run_emits_expected_versions() -> None:
    """``--dry-run`` prints the expected tag list to stdout, exits 0,
    and does not make a network call."""
    assert SCRIPT.is_file(), f"missing script at {SCRIPT}"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"--dry-run exited {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    tags = result.stdout.splitlines()
    # Anchor pins: any CHANGELOG at v0.8.4 ship time has these.
    for anchor in ("v0.7.3", "v0.8.3", "v0.8.4"):
        assert anchor in tags, f"expected {anchor!r} in dry-run output; got: {tags}"
    # Absorbed-into exclusion: v0.7.4's header reads
    # "## [0.7.4] - 2026-05-03 (absorbed into v0.8.0)" and the
    # script must drop it.
    assert (
        "v0.7.4" not in tags
    ), f"v0.7.4 was absorbed into v0.8.0 and must be excluded; got: {tags}"


def test_historical_untagged_allowlist_is_documented_and_frozen() -> None:
    """The script's ``_HISTORICAL_UNTAGGED_VERSIONS`` allowlist is the
    explicit acknowledgement of the v0.2.0 / v0.7.0 historical drift
    surfaced when the gate ran for the first time on PR #10. Pin the
    allowlist's exact contents so any future edit (additions or
    removals) requires an explicit code change visible in diff.

    Adding a post-v0.8.4 version to this allowlist is forbidden by
    the docstring contract; the gate must catch new versions at PR
    time. This test does not enforce that contract directly (a
    test cannot infer release-time intent), but it does make any
    silent extension of the allowlist visible.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("verify_origin_tags", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    allowlist = module._HISTORICAL_UNTAGGED_VERSIONS
    assert allowlist == frozenset({"v0.2.0", "v0.7.0"}), (
        f"historical-untagged allowlist drifted from the documented"
        f" v0.2.0 / v0.7.0 pair; got {sorted(allowlist)}. Any change"
        f" requires an audit note in CHANGELOG.md per the script's"
        f" allowlist contract."
    )
