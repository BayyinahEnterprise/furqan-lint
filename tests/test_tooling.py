"""Verify dev-tooling configuration files exist and have the right
shape.

Three structural tests covering the v0.5.0 tooling rollout:

* The repo's own ``.pre-commit-config.yaml`` declares the expected
  set of hooks (ruff, ruff-format, mypy, em-dash guard, dogfood).
* ``pyproject.toml`` carries the ``[tool.ruff]`` configuration block.
* All five pytest markers (unit, integration, mock, slow, network)
  are registered in ``pyproject.toml``.

These are structural tests, not functional tests of the tools
themselves: they pin the configuration's *shape* so any restructure
that drops a hook or marker is detected on the next test run.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.unit
def test_pre_commit_config_has_required_hooks() -> None:
    """The repo's own ``.pre-commit-config.yaml`` declares ruff,
    ruff-format, mypy, the em-dash guard, and the furqan-lint
    dogfood hook."""
    yaml = pytest.importorskip("yaml")
    config = yaml.safe_load((REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    hook_ids: list[str] = []
    for repo in config["repos"]:
        for hook in repo["hooks"]:
            hook_ids.append(hook["id"])
    for expected in (
        "ruff",
        "ruff-format",
        "mypy",
        "no-em-dashes",
        "furqan-lint-self",
    ):
        assert (
            expected in hook_ids
        ), f"Missing hook '{expected}' in .pre-commit-config.yaml. Hooks present: {hook_ids}"


@pytest.mark.unit
def test_pyproject_has_ruff_config() -> None:
    """``pyproject.toml`` must carry the ``[tool.ruff]`` block.

    Without this the pre-commit and CI ruff invocations would fall
    back to defaults, which is not the same configuration the team
    has tuned.
    """
    with (REPO_ROOT / "pyproject.toml").open("rb") as f:
        config = tomllib.load(f)
    assert "ruff" in config.get("tool", {}), "Missing [tool.ruff] in pyproject.toml"


@pytest.mark.unit
def test_pyproject_has_all_pytest_markers() -> None:
    """All five pytest markers (unit, integration, mock, slow,
    network) must be registered. Unregistered markers raise a
    PytestUnknownMarkWarning that errors under ``-W error``."""
    with (REPO_ROOT / "pyproject.toml").open("rb") as f:
        config = tomllib.load(f)
    markers = config.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("markers", [])
    marker_names = [m.split(":")[0].strip() for m in markers]
    for expected in ("unit", "integration", "mock", "slow", "network"):
        assert (
            expected in marker_names
        ), f"Missing pytest marker: {expected}. Markers present: {marker_names}"


@pytest.mark.integration
def test_ruff_check_exits_zero_on_repo() -> None:
    """Functional verification that ruff check passes on the repo.

    Pairs with the structural test_pyproject_has_ruff_config per
    framework Section 8.6 (structural-vs-functional pairing). Catches
    the v0.5.0 CRITICAL where ruff config existed but ruff check
    failed in the pinned-version environment (8 UP038 violations
    that ruff>=0.8.0 resolved to 0.15.12 silently dropped).

    Because [dev] now pins ruff==0.8.0 exactly, the ruff binary on
    PATH in any contributor or CI environment is the same version
    pre-commit uses. This test means what it says only because of
    that pin.
    """
    result = subprocess.run(
        ["ruff", "check", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"ruff check failed on repo:\n{result.stdout}"


@pytest.mark.integration
def test_ruff_format_check_exits_zero_on_repo() -> None:
    """Functional verification that ruff format --check passes.

    Catches unformatted files before they reach CI. Same version-pin
    contract as test_ruff_check_exits_zero_on_repo.
    """
    result = subprocess.run(
        ["ruff", "format", "--check", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"ruff format --check failed:\n{result.stdout}"
