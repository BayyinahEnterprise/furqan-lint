"""Documented-limit fixture: score_validity_optin_extra.

The v0.9.4 score-validity ADVISORY checker is opt-in via the
``[onnx-profile]`` pip extra. When the extra is not installed
(``import onnx_tool`` raises ``ImportError``), the checker
silent-passes per Decision 6 (a) of the v0.9.4 prompt.

This convention is consistent with the v0.9.3 numpy_divergence
checker's NeuroGolf-convention silent-pass: opt-in by extra
installation rather than by global flag, so generic ONNX users
who don't want the additional install weight see no behavior
change. The four-place pattern surfaces this so users
understand the silent-pass is intentional.

Resolution path: a future release may revisit if a concrete
need motivates always-on score-validity (e.g., the ``onnx``
package itself begins shipping a profiler that does not have
the schema-default-coverage gap that ``onnx_tool 1.0.x`` has).
For v0.9.4 the opt-in shape matches user-installation cost
expectations.

The companion pinning test
``tests/test_onnx_score_validity_documented_limit.py``
asserts the silent-pass behavior when the [onnx-profile]
extra is mocked-absent. A future onnx_tool version that
changes the schema-default-coverage behavior must be caught
at the framework boundary by extending the firing tests in
tests/test_onnx_score_validity.py.
"""
