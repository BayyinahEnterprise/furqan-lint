"""Structural tests for the v0.8.4 release.yml workflow.

The release workflow listens for ``v*`` tag pushes, builds sdist
plus wheel, verifies tag/version/CHANGELOG sync at release-time,
and publishes to PyPI via Trusted Publishing (OIDC). These pins
defend the load-bearing structural pieces against drift.

What's pinned:

* The workflow exists and is valid YAML.
* It triggers on ``v*`` tag pushes (not on every commit).
* The ``publish`` job has ``permissions.id-token: write`` (REQUIRED
  for OIDC) and ``environment: pypi`` (MATCHES the PyPI Trusted
  Publisher config).
* The ``build`` job verifies the tag commit is an ancestor of
  ``origin/main`` (catches local-only-tag failure mode).

The PyPI Trusted Publisher is configured at:
- Owner: BayyinahEnterprise
- Repository: furqan-lint
- Workflow: release.yml
- Environment: pypi
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_PATH = REPO_ROOT / ".github" / "workflows" / "release.yml"


def _load_release() -> dict:
    assert RELEASE_PATH.is_file(), f"{RELEASE_PATH} does not exist"
    with RELEASE_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_release_workflow_triggers_on_version_tags() -> None:
    """The workflow must fire on tag pushes matching ``v*``. PyPI
    publish is irreversible per-version; running on every commit
    or branch push would either spam PyPI with malformed candidates
    or fail OIDC. Pinning the trigger prevents accidental rewiring.
    """
    data = _load_release()
    # PyYAML parses the bareword ``on`` as Python True (it's a YAML
    # 1.1 boolean). Accept either key shape.
    triggers = data.get("on", data.get(True))
    assert triggers is not None, f"release.yml has no 'on' trigger; data: {data}"
    push = triggers.get("push", {})
    tags = push.get("tags", [])
    assert "v*" in tags, (
        f"release workflow must trigger on v* tags; got {tags}. "
        f"Anything else either misses real releases or fires on noise."
    )


def test_release_workflow_publish_job_has_oidc_and_pypi_environment() -> None:
    """The publish job MUST request ``id-token: write`` (without it,
    OIDC token issuance fails and PyPI rejects the publish) AND
    bind to the ``pypi`` environment (the Trusted Publisher config
    on PyPI requires this exact environment name to authorize the
    publish; mismatched names fail the OIDC trust decision).

    Both are load-bearing for the publish to succeed; pinning them
    prevents a future rewrite from silently breaking the release
    path.
    """
    data = _load_release()
    publish = data["jobs"]["publish"]
    permissions = publish.get("permissions", {})
    assert permissions.get("id-token") == "write", (
        f"publish job must have id-token: write for OIDC; " f"got permissions: {permissions}"
    )
    assert publish.get("environment") == "pypi", (
        f"publish job must bind to environment: pypi to match the "
        f"PyPI Trusted Publisher config; got {publish.get('environment')!r}"
    )


def test_release_workflow_build_job_verifies_tag_on_main() -> None:
    """The build job must verify the tag commit is an ancestor of
    ``origin/main``. Without this check, a tag pushed at a local-
    only commit would still trigger publish; the published artifact
    would not reflect what's actually on the branch and the audit
    trail (commit history) would diverge from PyPI.

    Pinning the merge-base ancestry check prevents that failure
    mode going forward.
    """
    text = RELEASE_PATH.read_text(encoding="utf-8")
    # The check is implemented as `git merge-base --is-ancestor`
    # against `origin/main`. Pin both literals.
    assert "merge-base --is-ancestor" in text, (
        "build job must verify tag commit ancestry via " "`git merge-base --is-ancestor`"
    )
    assert "origin/main" in text, "ancestry check must compare against origin/main"
