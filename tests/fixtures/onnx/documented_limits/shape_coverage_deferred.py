"""Documented-limit fixture: shape_coverage_deferred.

D11-onnx (shape-coverage on ONNX edges) is deferred to v0.9.1
per Decision 3 of the v0.9.0 prompt. ONNX shape compatibility
requires its own design round given symbolic dim_params,
NumPy broadcasting, axis insertion (Reshape/Squeeze/Unsqueeze),
and dynamic shapes (-1 / empty dim_value). Shipping a
one-sentence specification produces unbounded false positives.

The companion fixture builder
``tests/fixtures/onnx/builders.py::make_shape_mismatch_d11_deferred_model``
constructs a model with an internal-edge shape mismatch that
v0.9.1's D11-onnx checker would catch. v0.9.0 accepts the model;
the pinning test
``tests/test_onnx_public_surface_additive.py::test_onnx_d11_deferred_v0_9_0_passes``
records that acceptance.

Resolution path: v0.9.1 will ship D11-onnx with a tight
'compatible' definition pinned by fixtures.
"""
