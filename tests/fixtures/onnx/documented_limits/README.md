# ONNX adapter documented limits

Each entry below has a fixture file in this directory, a CHANGELOG
entry by exact stem, a top-level README entry by topic keyword,
and at least one pinning test under `tests/test_*.py`.

## Inventory (current as of v0.9.3)

- `numpy_divergence_neurogolf_convention` (v0.9.3): the
  numpy-vs-ONNX divergence checker is opt-in by reference
  presence and uses the NeuroGolf-specific
  ``<basename>_build.py`` + ``<basename>.json`` convention.
  Generic ONNX users without these sidecars see silent-pass on
  the divergence checker. Pinned by
  `tests/test_onnx_numpy_divergence_documented_limit.py::test_numpy_divergence_silent_pass_when_neurogolf_convention_absent`.

- `dynamic_shape_silent_pass` (v0.9.1): D11-onnx silent-passes on
  dim_param (symbolic) and empty dim_value (dynamic) shapes per
  Decision 3 of the v0.9.1 prompt. Inherent to strict_mode; no
  custom logic overrides it. Pinned by
  `tests/test_onnx_shape_coverage.py::test_d11_onnx_dynamic_shape_silent_pass_pin`.

- `intermediates_excluded` (v0.9.0): the additive-only diff covers
  `graph.input` and `graph.output` ValueInfo only; `graph.value_info`
  and `graph.initializer` are out of scope per Decision 5 / round-24
  finding m2. Pinned by
  `tests/test_onnx_public_surface_additive.py::test_onnx_diff_intermediates_excluded`.

- `registry_pin_window` (v0.9.0): the `[onnx]` extra pins
  `onnx>=1.14,<1.19` per Decision 4 / round-24 finding M2. Pinned by
  `tests/test_onnx_correctness.py::test_opset_registry_version_pinned`.

## Retired

- `shape_coverage_deferred` (retired in v0.9.1): D11-onnx was
  deferred from v0.9.0 to v0.9.1; the v0.9.1 release ships D11-onnx
  via strict-mode shape inference, so the deferral entry is no
  longer load-bearing. The companion v0.9.0 pinning test
  `test_onnx_d11_deferred_v0_9_0_passes` is also deleted in v0.9.1
  commit 4 per Decision 4 (delete-plus-add discipline; round-30
  MED-1 closure). The v0.9.1 firing test
  `test_d11_onnx_fires_on_shape_mismatch` (in
  `tests/test_onnx_shape_coverage.py`) replaces it.
