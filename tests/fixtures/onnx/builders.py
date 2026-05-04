"""Programmatic ONNX fixture builders.

Per Decision 5 / round-24 finding Q3, no .onnx binary fixtures are
committed to the repository. Tests that need an ONNX model
construct one via these helpers (using ``onnx.helper.make_model``)
and write it to ``tmp_path``.

Provenance of every ONNX test fixture is therefore visible in
this file. A reviewer can read these builders and reconstruct
exactly what each fixture asserts about the substrate.

This module imports ``onnx`` at top level. Tests that import it
must be skipped when the ``[onnx]`` extra is missing
(``pytest.importorskip("onnx")``).
"""

from __future__ import annotations

from pathlib import Path

import onnx


def _vi(name: str, shape, elem_type=None):
    if elem_type is None:
        elem_type = onnx.TensorProto.FLOAT
    return onnx.helper.make_tensor_value_info(name, elem_type, list(shape))


def make_relu_model(opset_version: int = 14):
    """A trivial single-Relu model: x -> Relu -> y, both [1,4] FLOAT.

    Useful as a clean baseline: D24-onnx and opset-compliance both
    pass.
    """
    node = onnx.helper.make_node("Relu", ["x"], ["y"])
    graph = onnx.helper.make_graph(
        nodes=[node],
        name="test_relu",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y", [1, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", opset_version)],
        ir_version=8,
    )


def make_unreachable_output_model(opset_version: int = 14):
    """A model with a declared output that no node produces.

    ``graph.input = [x]``, ``graph.output = [y, z]``. Node graph
    produces ``y`` (via Relu) but ``z`` has no producer node
    anywhere in ``graph.node``. D24-onnx fires.
    """
    node_y = onnx.helper.make_node("Relu", ["x"], ["y"])
    graph = onnx.helper.make_graph(
        nodes=[node_y],
        name="test_unreachable",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y", [1, 4]), _vi("z", [1, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", opset_version)],
        ir_version=8,
    )


def make_unknown_op_model():
    """A model with an op_type that does not exist in any opset.

    opset-compliance fires because schema lookup returns no match.
    Uses a fabricated op name ``XQyzNotARealOp`` that we are
    confident will never appear in the ONNX op registry.
    """
    node = onnx.helper.make_node("XQyzNotARealOp", ["x"], ["y"])
    graph = onnx.helper.make_graph(
        nodes=[node],
        name="test_unknown_op",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y", [1, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def make_two_output_model():
    """A two-output model where both outputs are reachable.

    x -> Relu -> y (output 1)
    x -> Identity -> z (output 2)
    """
    node_y = onnx.helper.make_node("Relu", ["x"], ["y"], name="relu_y")
    node_z = onnx.helper.make_node("Identity", ["x"], ["z"], name="ident_z")
    graph = onnx.helper.make_graph(
        nodes=[node_y, node_z],
        name="test_two_outputs",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y", [1, 4]), _vi("z", [1, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def make_renamed_output_model():
    """Same shape as make_relu_model but the output is named
    ``y_renamed`` instead of ``y``. Diff against make_relu_model
    fires MARAD on the removed ``y`` output."""
    node = onnx.helper.make_node("Relu", ["x"], ["y_renamed"])
    graph = onnx.helper.make_graph(
        nodes=[node],
        name="test_renamed",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y_renamed", [1, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def make_shape_changed_model():
    """Same shape as make_relu_model but output ``y`` is now
    [2, 4] instead of [1, 4]. Diff against make_relu_model fires
    MARAD because shape is part of the public-name format
    (``output:y:1x4`` vs ``output:y:2x4`` are different strings).
    """
    node = onnx.helper.make_node("Relu", ["x"], ["y"])
    graph = onnx.helper.make_graph(
        nodes=[node],
        name="test_shape_changed",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y", [2, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def make_additive_model():
    """A model that is additive over make_relu_model: same input
    ``x``, two outputs (the original ``y`` plus a new ``z``).
    Diff against make_relu_model passes (no removals)."""
    node_y = onnx.helper.make_node("Relu", ["x"], ["y"], name="relu_y")
    node_z = onnx.helper.make_node("Identity", ["x"], ["z"], name="ident_z")
    graph = onnx.helper.make_graph(
        nodes=[node_y, node_z],
        name="test_additive",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y", [1, 4]), _vi("z", [1, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def make_intermediates_only_diff_model():
    """A model with the same graph.input and graph.output as
    make_relu_model but a different intermediate value_info name.

    Used by test_onnx_diff_intermediates_excluded to confirm that
    differences confined to intermediates do not register a MARAD.
    """
    node_a = onnx.helper.make_node("Relu", ["x"], ["mid_renamed"], name="relu_a")
    node_b = onnx.helper.make_node("Identity", ["mid_renamed"], ["y"], name="ident_b")
    graph = onnx.helper.make_graph(
        nodes=[node_a, node_b],
        name="test_intermediates",
        inputs=[_vi("x", [1, 4])],
        outputs=[_vi("y", [1, 4])],
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def make_shape_mismatch_d11_deferred_model():
    """A model with an actual static-shape mismatch on the output
    ValueInfo. ``Concat([1,10], [1,10], axis=1)`` produces ``[1,20]``
    but the graph declares the output as ``[1,10]``;
    ``onnx.shape_inference.infer_shapes(..., strict_mode=True)``
    raises ``InferenceError``.

    v0.9.0 shipped this builder with a clean Relu->Identity chain
    (no mismatch) under the same name; the round-30 audit caught
    that the pinning test ``test_onnx_d11_deferred_v0_9_0_passes``
    was passing for the wrong reason (model was clean, not because
    D11 was deferred). v0.9.1 fixes the builder as part of the
    retirement (Decision 4 of the v0.9.1 prompt).

    Constructed so opset-compliance and D24-onnx still pass: Concat
    is in opset 14 and the declared output ``c`` is reachable from
    the Concat node.
    """
    node = onnx.helper.make_node("Concat", ["a", "b"], ["c"], axis=1, name="concat_c")
    graph = onnx.helper.make_graph(
        nodes=[node],
        name="test_d11_static_mismatch",
        inputs=[_vi("a", [1, 10]), _vi("b", [1, 10])],
        outputs=[_vi("c", [1, 10])],  # WRONG: actual is [1, 20] from Concat axis=1
    )
    return onnx.helper.make_model(
        graph,
        opset_imports=[onnx.helper.make_opsetid("", 14)],
        ir_version=8,
    )


def write_model(path: Path, model) -> Path:
    """Serialize ``model`` to ``path`` and return ``path``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, str(path))
    return path
