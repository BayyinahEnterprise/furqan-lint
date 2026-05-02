"""Structural tests for the GitHub Action and pre-commit hook
configuration files.

These tests verify that the YAML files exist, parse cleanly, and
have the shape downstream consumers depend on. They do NOT execute
the action or the hook - that requires GitHub's runner or a
pre-commit installation, both out of scope for unit testing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(rel_path: str):
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"{rel_path} does not exist"
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f), path


# ---------------------------------------------------------------------------
# action.yml
# ---------------------------------------------------------------------------

def test_action_yml_exists_and_is_valid_yaml() -> None:
    data, path = _load("action.yml")
    assert isinstance(data, dict)
    assert data.get("name"), "action.yml must declare a name"
    assert data.get("description"), "action.yml must declare a description"


def test_action_yml_has_required_inputs() -> None:
    data, _ = _load("action.yml")
    inputs = data.get("inputs", {})
    assert "path" in inputs
    assert "python-version" in inputs
    # Inputs MUST be optional with sensible defaults so a user can
    # adopt the action with three lines of YAML and zero required
    # input.
    assert inputs["path"].get("required") is False
    assert inputs["python-version"].get("required") is False
    assert inputs["path"].get("default") == "."


def test_action_yml_uses_composite_runs() -> None:
    """The action is a composite of standard setup-python +
    install + run steps. Avoids needing a Docker image."""
    data, _ = _load("action.yml")
    runs = data.get("runs", {})
    assert runs.get("using") == "composite"
    steps = runs.get("steps", [])
    assert len(steps) >= 3
    # The last step must be the actual furqan-lint invocation.
    last = steps[-1]
    assert "furqan-lint check" in last.get("run", "")


# ---------------------------------------------------------------------------
# .pre-commit-hooks.yaml
# ---------------------------------------------------------------------------

def test_pre_commit_hooks_yaml_exists_and_is_valid() -> None:
    data, _ = _load(".pre-commit-hooks.yaml")
    assert isinstance(data, list)
    assert len(data) == 1


def test_pre_commit_hooks_yaml_entry_is_furqan_lint_check() -> None:
    data, _ = _load(".pre-commit-hooks.yaml")
    hook = data[0]
    assert hook["id"] == "furqan-lint"
    assert hook["entry"] == "furqan-lint check"
    assert hook["language"] == "python"
    # Hook must scope to .py files; running on every file would be
    # noisy and slow.
    assert hook["types"] == ["python"]
