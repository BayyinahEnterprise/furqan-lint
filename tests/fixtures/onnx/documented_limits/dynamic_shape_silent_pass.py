"""Documented-limit fixture: dynamic_shape_silent_pass.

D11-onnx (strict-mode shape inference) silent-passes on dynamic
shapes: dim_param (symbolic dims like ``"batch"``) and empty
dim_value (unset / dynamic). This is inherent to strict_mode
itself per Decision 3 of the v0.9.1 prompt; v0.9.1 ships no
custom logic to override it.

Resolution path: a future release may revisit if a concrete
user-reported false negative motivates a stricter dynamic-shape
mode. v0.9.1 takes the position that strict_mode's silent-pass
is the right default because (a) ONNX models with dim_param
are typically deployment-time signature shapes for runtimes
that bind concrete values later, so the disagreement-window
between declared and used shape is closed at bind-time rather
than authoring-time; (b) requiring all shapes to be static
would break legitimate model-export workflows for transformer
and convolutional architectures with batch / sequence dims.

The companion fixture builder
``tests/fixtures/onnx/builders.py::make_dim_param_passthrough_model``
constructs a model with a ``dim_param`` input/output that v0.9.1
accepts. The pinning test
``tests/test_onnx_shape_coverage.py::test_d11_onnx_dynamic_shape_silent_pass_pin``
records the silent-pass behavior so a future onnx release that
changes the policy is caught at the framework boundary.
"""
