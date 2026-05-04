"""Documented-limit fixture: intermediates_excluded.

The additive-only diff covers ``graph.input`` and ``graph.output``
ValueInfo entries only. ``graph.value_info`` (intermediate
tensors) and ``graph.initializer`` (parameter tensors) are
explicitly out of scope per Decision 5 of the v0.9.0 prompt
(round-24 finding m2 closure).

Including initializers in the additive contract would create
false positives on every model retraining: initializer tensor
names and shapes change as a routine matter and do not
constitute the model's external interface. Including
intermediates would have a similar drift problem; their names
are an implementation detail of the graph's internal dataflow.

The companion fixture builder
``tests/fixtures/onnx/builders.py::make_intermediates_only_diff_model``
constructs a model whose graph.input and graph.output are
identical to ``make_relu_model`` but whose intermediate value
names differ. The pinning test
``tests/test_onnx_public_surface_additive.py::test_onnx_diff_intermediates_excluded``
asserts that the diff fires no MARAD.

External tools that target intermediate tensor names by string
are out of scope; if they were in scope, the user would diff
the relevant fixture themselves.
"""
