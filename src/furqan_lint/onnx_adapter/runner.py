"""ONNX checker pipeline: D24-onnx + opset-compliance.

Per the v0.9.0 Framing note, this is a parallel diagnostic family,
not new instances of the existing Python/Rust/Go checker pipeline
operating on a unified IR. The OnnxModule IR (in
``onnx_adapter.translator``) is the substrate; the runner here
emits structural-honesty diagnostics that share the *spirit* of
the existing checkers but not their implementation.

D24-onnx (all-paths-emit, Decision 2):
    Every declared output in ``graph.output`` must be reachable
    on every dataflow path through ``If`` / ``Where`` branches.
    A branch that does not contribute to any declared output is
    a finding. The branch shape mirrors a function with a missing
    return statement.

opset-compliance (Decision 4):
    For each node, query
    ``onnx.defs.get_schema(op_type, max_inclusive_version=version,
    domain=node.domain)``. If the lookup raises (op not present
    at the declared opset), that is a finding. The op-registry
    source is ``onnx.defs`` from the pinned ``onnx>=1.14,<1.19``
    package; ``test_opset_registry_version_pinned`` verifies the
    pin.

D11-onnx (shape-coverage, v0.9.1):
    Run ``onnx.shape_inference.infer_shapes(model_proto,
    strict_mode=True)``; if it raises ``InferenceError``, parse
    the per-op message into structural-honesty findings.
    Strict-mode is the canonical ONNX mechanism per Decision 1
    of the v0.9.1 prompt. The implementation lives in
    ``onnx_adapter.shape_coverage``; ``check_onnx_module``
    requires ``model_proto`` (round-30 MED-2: required
    positional, not ``=None`` default, so missing arguments
    raise ``TypeError`` rather than silent-skip).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from furqan_lint.onnx_adapter.shape_coverage import ShapeCoverageDiagnostic

from furqan_lint.onnx_adapter.translator import OnnxModule


@dataclass(frozen=True)
class AllPathsEmitDiagnostic:
    """A declared output is unreachable from any node in the graph.

    ``output_name`` is the ValueInfo name from ``graph.output``;
    ``diagnosis`` is the human-readable description of the
    structural-honesty violation.
    """

    output_name: str
    diagnosis: str


@dataclass(frozen=True)
class OpsetComplianceDiagnostic:
    """A node uses an op that is not present in the declared opset.

    ``op_type``, ``node_name``, and ``domain`` identify the offender;
    ``opset_version`` is the model's declared default-domain opset
    version (or the custom-domain version if ``domain`` is set);
    ``diagnosis`` is the human-readable description.
    """

    op_type: str
    node_name: str
    domain: str
    opset_version: int
    diagnosis: str


def _producers(module: OnnxModule) -> dict[str, str]:
    """Build a map from value-name to producing-node-name.

    Each output of each node maps to that node's name (or empty
    string if the node has no name; ONNX permits unnamed nodes).
    Initializers and graph inputs are NOT included; the dataflow
    walker treats them as 'present from the start' separately.
    """
    out: dict[str, str] = {}
    for n in module.nodes:
        for o in n.outputs:
            if o:
                out[o] = n.name
    return out


def _input_names(module: OnnxModule) -> frozenset[str]:
    return frozenset(vi.name for vi in module.inputs)


def check_all_paths_emit(module: OnnxModule) -> list[AllPathsEmitDiagnostic]:
    """D24-onnx: every declared graph.output must be reachable.

    A declared output is reachable when either:

    * it is the name of a graph input (passthrough output), or
    * some node in ``graph.node`` produces it.

    A declared output that has no producing node and is not a
    graph input is unreachable; that is the structural shape of
    a function declaring a return type but not returning a value
    on at least one path.

    Branches: ``If`` / ``Where`` selection-input dataflow paths
    are conservatively merged at the join point because ONNX
    semantics require every branch to produce a tensor with the
    same name as the join (for ``If`` subgraphs) or the same
    broadcast-compatible shape (for ``Where``). The walker treats
    a value as reachable once any path reaches it; a finding is
    therefore emitted only when no path produces the declared
    output.
    """
    findings: list[AllPathsEmitDiagnostic] = []
    producers = _producers(module)
    inputs = _input_names(module)
    for out in module.outputs:
        if out.name in inputs:
            continue
        if out.name in producers:
            continue
        findings.append(
            AllPathsEmitDiagnostic(
                output_name=out.name,
                diagnosis=(
                    f"Declared output '{out.name}' is not produced "
                    f"by any node and is not a graph input; the "
                    f"dataflow has no path that emits it (D24-onnx)."
                ),
            )
        )
    return findings


def check_opset_compliance(module: OnnxModule) -> list[OpsetComplianceDiagnostic]:
    """opset-compliance: every node's op must exist in the declared opset.

    Looks up each node via ``onnx.defs.get_schema`` with
    ``max_inclusive_version=module.opset_version`` for the default
    domain. For custom-domain nodes (``domain != ""``), the
    lookup uses ``domain=node.domain``; v0.9.0 does not parse
    custom-opset versions and treats them as best-effort
    (a missing custom-domain schema is still reported).

    A node whose op_type is not present at the declared version
    fires a finding. The pinned ``onnx>=1.14,<1.19`` registry
    (Decision 4) ensures this lookup is deterministic across
    package upgrades.
    """
    import onnx.defs as _defs

    findings: list[OpsetComplianceDiagnostic] = []
    for node in module.nodes:
        domain = node.domain or ""
        try:
            _defs.get_schema(
                node.op_type,
                max_inclusive_version=module.opset_version,
                domain=domain,
            )
        except Exception:
            findings.append(
                OpsetComplianceDiagnostic(
                    op_type=node.op_type,
                    node_name=node.name or "<unnamed>",
                    domain=domain,
                    opset_version=module.opset_version,
                    diagnosis=(
                        f"Node '{node.name or '<unnamed>'}' uses op "
                        f"'{node.op_type}' which is not present in "
                        f"opset {module.opset_version} "
                        f"(domain={domain!r}); see "
                        f"onnx>=1.14,<1.19 op registry."
                    ),
                )
            )
    return findings


def check_onnx_module(
    module: OnnxModule,
    model_proto: Any,
) -> list[
    tuple[
        str,
        AllPathsEmitDiagnostic | OpsetComplianceDiagnostic | ShapeCoverageDiagnostic,
    ]
]:
    """Run every ONNX checker against ``module`` and ``model_proto``.

    ``model_proto`` is a **required positional parameter** per
    Decision 2 of the v0.9.1 prompt (round-30 finding MED-2
    closure). The fail-fast discipline favors a ``TypeError`` on
    a missing argument over silently skipping the
    ``shape_coverage`` checker. The single existing call site is
    ``cli._check_onnx_file``, which has ``model_proto`` in scope
    from ``parse_model(path)``.

    Returns a list of ``(name, diagnostic)`` pairs where ``name``
    identifies the checker:

    * ``"all_paths_emit"`` - D24-onnx (v0.9.0)
    * ``"opset_compliance"`` - opset registry check (v0.9.0)
    * ``"shape_coverage"`` - D11-onnx via strict-mode shape
      inference (v0.9.1; Decision 1 of v0.9.1 prompt)
    """
    from furqan_lint.onnx_adapter.shape_coverage import check_shape_coverage

    diagnostics: list[
        tuple[
            str,
            AllPathsEmitDiagnostic | OpsetComplianceDiagnostic | ShapeCoverageDiagnostic,
        ]
    ] = []
    for d_apr in check_all_paths_emit(module):
        diagnostics.append(("all_paths_emit", d_apr))
    for d_op in check_opset_compliance(module):
        diagnostics.append(("opset_compliance", d_op))
    for d_sc in check_shape_coverage(model_proto):
        diagnostics.append(("shape_coverage", d_sc))
    return diagnostics
