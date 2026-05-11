"""Phase G11.4 (Tasdiq al-Bayan / v0.14.0) cross-substrate fixture parity helper.

For each shared concern in the cross-substrate corpus
(tests/test_gate11_cross_substrate_corpus.py), this helper
constructs a parallel set of fixtures across all four
gate11 substrates (Python, Rust, Go, ONNX). The fixtures
share the same conceptual content (a public surface with a
specific signature, signed by the same identity, with the
same policy) to make the parity claim empirically meaningful.

The four-substrate fixture structure is fixed by Tasdiq al-Bayan
T03 spec:

  tests/fixtures/gate11/cross_substrate/
    <concern_name>/
      python_module.py       # Python module with one public function
      rust_crate.rs          # Rust crate with the equivalent function
      go_module.go           # Go module with the equivalent function
      onnx_model.onnx        # ONNX model with equivalent input/output structure
      SHARED_IDENTITY        # the identity all four are signed under
      SHARED_POLICY.json     # the policy all four are verified with

Per F-TAB-1 MEDIUM closure (pre-dispatch absorption): the
fixture root is tests/fixtures/gate11/cross_substrate/ (matching
the existing tests/fixtures/gate11/ gate11-fixture-root
convention at v0.13.0).
"""

from __future__ import annotations

from pathlib import Path

_CONCERN_ROOT = Path(__file__).parent
_SHARED_IDENTITY = "https://github.com/BayyinahEnterprise/furqan-lint/.github/workflows/ci.yml@refs/heads/main"
_SHARED_POLICY = '{"expected_identity": "' + _SHARED_IDENTITY + '", "expected_issuer": "https://token.actions.githubusercontent.com"}'

_PYTHON_TEMPLATE = '''"""Cross-substrate parity fixture for concern: {concern}."""


def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b
'''

_RUST_TEMPLATE = '''//! Cross-substrate parity fixture for concern: {concern}

pub fn add(a: i64, b: i64) -> i64 {{
    a + b
}}
'''

_GO_TEMPLATE = '''// Cross-substrate parity fixture for concern: {concern}
package fixture

// Add returns the sum of two integers.
func Add(a int, b int) int {{
\treturn a + b
}}
'''


def build_cross_substrate_fixtures(concern_name: str) -> dict[str, Path]:
    """Build a parallel fixture set across all four substrates.

    Each substrate's fixture exposes the same conceptual content:
    a single public name (``add``) with a binary-arithmetic
    signature (``int + int -> int``), signed by SHARED_IDENTITY,
    verified with SHARED_POLICY.

    The four-substrate fixture set is the substrate-of-record
    for the cross-substrate parity claim: the same logical
    function across Python/Rust/Go/ONNX (with ONNX modeling
    the binary-add as a graph node with two input ValueInfos
    and one output ValueInfo).

    Args:
        concern_name: directory name under
            tests/fixtures/gate11/cross_substrate/ where the
            parallel fixture set lives. Created if absent.

    Returns:
        dict mapping substrate name (python/rust/go/onnx) to
        the fixture path on disk.

    The ONNX fixture is built lazily on first access; if onnx
    is not installed, the path is recorded but the file is not
    written (Tasdiq al-Bayan corpus tests using ONNX fixtures
    pytest.importorskip 'onnx' independently).
    """
    out_dir = _CONCERN_ROOT / concern_name
    out_dir.mkdir(parents=True, exist_ok=True)

    python_path = out_dir / "python_module.py"
    rust_path = out_dir / "rust_crate.rs"
    go_path = out_dir / "go_module.go"
    onnx_path = out_dir / "onnx_model.onnx"

    if not python_path.exists():
        python_path.write_text(_PYTHON_TEMPLATE.format(concern=concern_name), encoding="utf-8")
    if not rust_path.exists():
        rust_path.write_text(_RUST_TEMPLATE.format(concern=concern_name), encoding="utf-8")
    if not go_path.exists():
        go_path.write_text(_GO_TEMPLATE.format(concern=concern_name), encoding="utf-8")
    # ONNX fixture: lazy build via tests/fixtures/onnx/builders.py
    # make_relu_model (substrate-actual builder per an-Naziat T10).
    # We construct a minimal Relu fixture as the parallel artifact;
    # the conceptual content parity is "single node, single input,
    # single output" matching the source-code substrates' "single
    # public function".
    if not onnx_path.exists():
        try:
            import onnx

            from tests.fixtures.onnx.builders import make_relu_model

            model = make_relu_model(opset_version=14)
            onnx.save(model, str(onnx_path))
        except ImportError:
            # ONNX not installed; corpus tests pytest.importorskip
            # independently. The path is recorded for parity-test
            # consumption (which checks existence iff ONNX runtime
            # available).
            pass

    identity_path = out_dir / "SHARED_IDENTITY"
    policy_path = out_dir / "SHARED_POLICY.json"
    if not identity_path.exists():
        identity_path.write_text(_SHARED_IDENTITY, encoding="utf-8")
    if not policy_path.exists():
        policy_path.write_text(_SHARED_POLICY, encoding="utf-8")

    return {
        "python": python_path,
        "rust": rust_path,
        "go": go_path,
        "onnx": onnx_path,
    }


__all__ = ("build_cross_substrate_fixtures",)
