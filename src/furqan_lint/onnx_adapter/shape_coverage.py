"""D11-onnx: shape-coverage on ONNX edges via strict-mode shape inference.

Catches ``onnx.shape_inference.InferenceError`` raised by
``infer_shapes(model_proto, strict_mode=True)`` and parses the
per-op diagnostic into structural-honesty findings. Decision 1
of the v0.9.1 prompt: strict_mode is the canonical ONNX
mechanism for catching declared-vs-inferred shape disagreement.
It uses ONNX's own per-op shape rules, handles broadcasting
natively, and silent-passes on dim_param / empty dim_value.

The checker is the third member of the ONNX checker family
(after D24-onnx all-paths-emit and opset-compliance). Per
Decision 5 of the v0.9.1 prompt, no translator extension is
needed: strict_mode operates on ``ModelProto`` directly, not
on the OnnxModule IR.

Empirical message format (onnx 1.17.0 through 1.21.0):

    [ShapeInferenceError] Inference error(s):
     (op_type:Concat): [ShapeInferenceError] Inferred shape and
     existing shape differ in dimension 1: (20) vs (10)

The ``_PER_OP_RE`` regex captures one finding per
``(op_type:NAME): [KIND] BODY`` line. If the message format
ever changes such that no per-op match is found, the checker
falls back to a single generic diagnostic so the user still
sees the issue.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ShapeCoverageDiagnostic:
    """A strict-mode shape-inference disagreement on one node.

    ``op_type`` and ``error_kind`` come from the bracketed prefix
    of the ONNX error message; ``message`` is the human-readable
    body; ``diagnosis`` and ``minimal_fix`` are the
    structural-honesty user-facing prose. ``error_kind`` is a
    forensic detail (Decision 6 of the v0.9.1 prompt; round-30
    finding m2 closure) that gives users the exception kind tag
    without enlarging the public surface.
    """

    op_type: str
    error_kind: str
    message: str
    diagnosis: str
    minimal_fix: str


# Empirical message format (onnx 1.14 through 1.21):
#   (op_type:Concat): [ShapeInferenceError] body
#   (op_type:Concat, node name: concat_c): [ShapeInferenceError] body
# ONNX includes the node name when one is set; the regex captures
# the op_type only and discards the optional ", node name: ..."
# suffix so downstream code sees a clean op name like "Concat".
_PER_OP_RE = re.compile(
    r"\(op_type:(?P<op>[^,)]+)(?:,[^)]*)?\):\s*\[(?P<kind>[^\]]+)\]\s*(?P<body>[^\n]+)"
)


def check_shape_coverage(model_proto: Any) -> Iterator[ShapeCoverageDiagnostic]:
    """Run strict-mode shape inference on ``model_proto``; yield
    one :class:`ShapeCoverageDiagnostic` per per-op mismatch.

    Raises :class:`furqan_lint.onnx_adapter.OnnxExtrasNotInstalled`
    if the ``[onnx]`` extra is missing (the
    ``onnx.shape_inference`` import probes for the package).

    Silent-passes on:

    * dim_param shapes (symbolic dims like ``"batch"``)
    * empty dim_value (dynamic shapes)
    * broadcast-compatible op inputs (e.g., Add of ``[1,10]`` and
      ``[5,10]``)

    These behaviors are inherent to strict_mode itself, not
    custom logic in this checker. Decision 3 of the v0.9.1
    prompt: dynamic shapes silent-pass natively; no special-case
    code needed. The empirical pin test
    ``test_d11_onnx_silent_pass_on_dim_param`` catches future
    onnx changes that would alter this behavior.
    """
    try:
        import onnx.shape_inference
    except ImportError as e:
        from furqan_lint.onnx_adapter import OnnxExtrasNotInstalled

        raise OnnxExtrasNotInstalled(
            "ONNX support not installed. Run: pip install furqan-lint[onnx]"
        ) from e

    try:
        onnx.shape_inference.infer_shapes(model_proto, strict_mode=True)
    except onnx.shape_inference.InferenceError as e:
        msg = str(e)
        matches = list(_PER_OP_RE.finditer(msg))
        if not matches:
            # Unparseable format. Emit one generic finding so the
            # user still learns of the issue even though the
            # parser cannot extract per-op detail.
            yield ShapeCoverageDiagnostic(
                op_type="<unknown>",
                error_kind="<unknown>",
                message=msg,
                diagnosis=(f"Strict-mode shape inference failed: {msg}"),
                minimal_fix=(
                    "Correct the declared shapes to match op "
                    "semantics, or insert a Reshape node if the "
                    "disagreement is intentional."
                ),
            )
            return
        for m in matches:
            op = m.group("op")
            kind = m.group("kind")
            body = m.group("body").strip()
            yield ShapeCoverageDiagnostic(
                op_type=op,
                error_kind=kind,
                message=body,
                diagnosis=(
                    f"Op '{op}' fails strict-mode shape inference: "
                    f"{body}. A declared edge shape disagrees with "
                    f"the op's computed shape."
                ),
                minimal_fix=(
                    f"Correct the declared shape on the edge "
                    f"connected to '{op}', or insert a Reshape node "
                    f"if the disagreement is intentional."
                ),
            )
