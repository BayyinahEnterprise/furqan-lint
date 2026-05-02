"""Structural tests for the CI workflow configuration.

Verify the YAML file exists, parses cleanly, and exercises the
expected matrix and quality gates. These are not integration tests
of the workflow itself - they pin the structural promise that any
reorganisation of CI must preserve.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[1]
CI_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _load_ci() -> dict:
    assert CI_PATH.is_file(), f"{CI_PATH} does not exist"
    with CI_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_ci_workflow_exists_and_is_valid_yaml() -> None:
    data = _load_ci()
    assert isinstance(data, dict)
    assert data.get("name") == "CI"
    assert "jobs" in data
    assert "test" in data["jobs"]


def test_ci_workflow_tests_python_310_through_313() -> None:
    data = _load_ci()
    matrix = data["jobs"]["test"]["strategy"]["matrix"]
    versions = matrix["python-version"]
    # Each listed version must be present. Missing one would mean
    # a Python release went untested on every PR.
    for required in ["3.10", "3.11", "3.12", "3.13"]:
        assert required in versions, (
            f"CI matrix is missing Python {required}; covers "
            f"{versions}"
        )


def test_ci_workflow_includes_version_sync() -> None:
    """The version-sync gate is the project's only barrier against
    shipping a release where __version__ and pyproject.toml
    disagree. Removing it would let the bug back in."""
    data = _load_ci()
    steps = data["jobs"]["test"]["steps"]
    step_names = " ".join(s.get("name", "") for s in steps)
    assert "Verify version sync" in step_names


def test_ci_workflow_includes_emdash_check() -> None:
    """The em-dash policy lives in the CI workflow, not in code, so
    the regex literal must appear in the workflow YAML."""
    text = CI_PATH.read_text(encoding="utf-8")
    # Must scan src/, tests/, README.md per the documented policy.
    assert "src/" in text
    assert "tests/" in text
    assert "README.md" in text
    # The regex used to detect en-dash (U+2013) and em-dash (U+2014).
    assert "x{2013}" in text or "x{2014}" in text
