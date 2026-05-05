"""Documented-limit fixture: numpy_divergence_neurogolf_convention.

The v0.9.3 numpy-vs-ONNX divergence checker is opt-in by reference
presence: it only runs when (a) the ``[onnx-runtime]`` extra is
installed, (b) a sibling ``<basename>_build.py`` file exists
exporting top-level callable ``numpy_reference``, AND (c) a
sibling ``<basename>.json`` file exists in ARC-AGI task format
with ``train[*]['input']``.

This convention is **NeuroGolf-specific by design** per Decision 9
of the v0.9.3 prompt. Generic ONNX users with no NeuroGolf-shaped
sidecars will see silent-pass on the divergence checker with no
indication of why; that is the documented limit.

Resolution path: general-purpose reference-discovery conventions
(decorator-based annotation, module-level registry) and
general-purpose probe-grid formats (decorator-defined inputs,
synthetic generation) are tracked as a v0.9.5+ extension. The
substrate-side specification for those generalizations does not
yet exist; v0.9.3 ships the NeuroGolf-tight convention as the
load-bearing path because it closes the dominant-failure-mode
gap (Gap 4 from the round-32 leverage analysis).

The companion pinning test
``tests/test_onnx_numpy_divergence_documented_limit.py``
asserts the silent-pass behavior on a model with no
NeuroGolf-shaped sidecars. A future onnx release that changes
strict_mode / check_type behavior, or a NeuroGolf-side
specification change that affects the convention, must be
caught at the framework boundary.
"""
