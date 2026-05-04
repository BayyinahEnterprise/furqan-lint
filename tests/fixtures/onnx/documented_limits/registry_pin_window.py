"""Documented-limit fixture: registry_pin_window.

The ONNX op-registry pin window is ``onnx>=1.14,<1.18`` per
Decision 4 of the v0.9.0 prompt. The upper bound is load-bearing:
the ONNX op registry retroactively adds operators to historical
opsets across ``onnx`` package releases, so an unpinned upper
bound would silently change what counts as e.g. opset 11.

The pin enforcement test
``tests/test_onnx_correctness.py::test_opset_registry_version_pinned``
reads the resolved ``onnx.__version__`` and asserts it falls
within the declared window, plus asserts that two known
retroactive-addition cases (Relu at opset 14, Identity at
opset 14) are handled deterministically.

Consumers requiring a newer registry must wait for a
furqan-lint patch release that bumps the pin. The bump is a
tracked release-time decision (which retroactive op additions
between the old and new pin would shift opset-compliance
verdicts must be inventoried before raising the upper bound).
"""
