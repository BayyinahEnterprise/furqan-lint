# ONNX adapter documented limits (v0.9.0)

Each entry below has a fixture file in this directory, a CHANGELOG
entry by exact stem, a top-level README entry by topic keyword,
and at least one pinning test under `tests/test_*.py`.

## Inventory

- `shape_coverage_deferred`: D11-onnx (shape-coverage) is deferred
  to v0.9.1 per Decision 3 of the v0.9.0 prompt. Pinned by
  `tests/test_onnx_public_surface_additive.py::test_onnx_d11_deferred_v0_9_0_passes`.

- `intermediates_excluded`: the additive-only diff covers
  `graph.input` and `graph.output` ValueInfo only; `graph.value_info`
  and `graph.initializer` are out of scope per Decision 5 / round-24
  finding m2. Pinned by
  `tests/test_onnx_public_surface_additive.py::test_onnx_diff_intermediates_excluded`.

- `registry_pin_window`: the `[onnx]` extra pins `onnx>=1.14,<1.18`
  per Decision 4 / round-24 finding M2. Pinned by
  `tests/test_onnx_correctness.py::test_opset_registry_version_pinned`.
