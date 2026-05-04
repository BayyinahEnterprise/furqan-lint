"""Tests for probe-grid discovery (v0.9.3 commit 2 part).

Covers 4 probe-grid tests:

* finds primary location <dir>/<basename>.json
* finds fallback ../tasks/<basename>.json
* returns None when no task file
* returns multiple grids when train has multiple examples
"""

from __future__ import annotations

import json
from pathlib import Path


def _write_task(path: Path, train_inputs: list) -> None:
    """Write a minimal ARC-AGI task file with the given train inputs."""
    obj = {
        "train": [{"input": grid, "output": grid} for grid in train_inputs],
        "test": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_discover_probe_grids_finds_primary_location(tmp_path: Path) -> None:
    """For ``<dir>/foo.onnx``, ``<dir>/foo.json`` with valid
    train[*]['input'] is returned."""
    from furqan_lint.onnx_adapter.probe_grid import discover_probe_grids

    onnx_path = tmp_path / "foo.onnx"
    onnx_path.write_bytes(b"")
    _write_task(tmp_path / "foo.json", [[[1, 2], [3, 4]]])
    grids = discover_probe_grids(onnx_path)
    assert grids == [[[1, 2], [3, 4]]]


def test_discover_probe_grids_finds_fallback_tasks_directory(
    tmp_path: Path,
) -> None:
    """When the primary location is empty, the fallback
    ``<dir>/../tasks/<basename>.json`` is checked."""
    from furqan_lint.onnx_adapter.probe_grid import discover_probe_grids

    models_dir = tmp_path / "models"
    models_dir.mkdir()
    onnx_path = models_dir / "bar.onnx"
    onnx_path.write_bytes(b"")
    _write_task(tmp_path / "tasks" / "bar.json", [[[5, 6]]])
    grids = discover_probe_grids(onnx_path)
    assert grids == [[[5, 6]]]


def test_discover_probe_grids_returns_none_when_no_task_file(
    tmp_path: Path,
) -> None:
    """No task file at primary or fallback location means
    silent-pass per Decision 6 condition (c)."""
    from furqan_lint.onnx_adapter.probe_grid import discover_probe_grids

    onnx_path = tmp_path / "lonely.onnx"
    onnx_path.write_bytes(b"")
    assert discover_probe_grids(onnx_path) is None


def test_discover_probe_grids_returns_multiple_grids_for_multi_example_task(
    tmp_path: Path,
) -> None:
    """Multi-example tasks (``train`` of length > 1) emit one
    grid per example in document order. The downstream divergence
    check then emits one finding per diverging probe."""
    from furqan_lint.onnx_adapter.probe_grid import discover_probe_grids

    onnx_path = tmp_path / "multi.onnx"
    onnx_path.write_bytes(b"")
    _write_task(
        tmp_path / "multi.json",
        [[[1]], [[2]], [[3]]],
    )
    grids = discover_probe_grids(onnx_path)
    assert grids == [[[1]], [[2]], [[3]]]
