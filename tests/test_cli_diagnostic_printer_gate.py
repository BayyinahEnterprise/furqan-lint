"""AST gate: cli._check_onnx_file's diagnostic-printing tuple
must include every *Diagnostic class in furqan_lint.onnx_adapter.

Round-34 HIGH-1's bug class closure (Part 5 of v0.9.4):
v0.9.3 added NumpyDivergenceDiagnostic to the runner and
__all__ but not to the printer's isinstance tuple. v0.9.3.1
fixed the bug instance for that family. This gate prevents
recurrence: when v0.9.4 adds ScoreValidityDiagnostic, the
gate fires unless the tuple is extended.

Part 5b(a) extension: the gate also AST-scans for the
``getattr(d, "minimal_fix", None)`` block following the
diagnosis print, so a future refactor that removes the
minimal_fix print without removing the diagnosis print
(re-introducing the v0.9.3 inconsistency with the
Python/Rust/Go printers) fires the gate.

Negative-test self-verification: the gate's parser is
exercised against a synthetic CLI source missing one
Diagnostic class; assert it correctly identifies the missing
entry. This proves the gate's parser actually works (vs.
silently passing because all entries always match by accident).
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = REPO_ROOT / "src" / "furqan_lint" / "cli.py"
ONNX_INIT_PATH = REPO_ROOT / "src" / "furqan_lint" / "onnx_adapter" / "__init__.py"
RUNNER_PATH = REPO_ROOT / "src" / "furqan_lint" / "onnx_adapter" / "runner.py"


def _diagnostic_classes_from_runner(runner_path: Path) -> set[str]:
    """AST-scan runner.py for class definitions ending in
    'Diagnostic'. Catches AllPathsEmitDiagnostic and
    OpsetComplianceDiagnostic which are runner-internal types
    not exported in __all__."""
    tree = ast.parse(runner_path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name.endswith("Diagnostic")
    }


def _diagnostic_exports_from_init(init_path: Path) -> set[str]:
    """AST-scan __init__.py's __all__ tuple for *Diagnostic exports."""
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    val = node.value
                    if isinstance(val, ast.Tuple | ast.List):
                        return {
                            elt.value
                            for elt in val.elts
                            if isinstance(elt, ast.Constant)
                            and isinstance(elt.value, str)
                            and elt.value.endswith("Diagnostic")
                        }
    return set()


def _printer_isinstance_classes(cli_path: Path) -> set[str]:
    """AST-scan _check_onnx_file's body for the isinstance(d, X | Y | ...)
    expression inside the for-name-d-in-diagnostics loop. Returns
    the set of class names in the type union."""
    tree = ast.parse(cli_path.read_text(encoding="utf-8"))
    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_check_onnx_file":
            target_func = node
            break
    if target_func is None:
        return set()
    classes: set[str] = set()
    for sub in ast.walk(target_func):
        if not isinstance(sub, ast.Call):
            continue
        if not (isinstance(sub.func, ast.Name) and sub.func.id == "isinstance"):
            continue
        if len(sub.args) < 2:
            continue
        type_arg = sub.args[1]
        # Walk the type union (BinOp tree of '|') for Name nodes.
        stack: list = [type_arg]
        while stack:
            n = stack.pop()
            if isinstance(n, ast.Name):
                if n.id.endswith("Diagnostic"):
                    classes.add(n.id)
            elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr):
                stack.append(n.left)
                stack.append(n.right)
    return classes


def _printer_has_minimal_fix_block(cli_path: Path) -> bool:
    """AST-scan _check_onnx_file for the
    getattr(d, "minimal_fix", None) call inside the for-name-d
    loop. Round-34 v0.9.3.1 carry-forward Part 5b(a) gate
    extension: every diagnostic-printing loop must print
    minimal_fix when present."""
    tree = ast.parse(cli_path.read_text(encoding="utf-8"))
    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_check_onnx_file":
            target_func = node
            break
    if target_func is None:
        return False
    for sub in ast.walk(target_func):
        if not isinstance(sub, ast.Call):
            continue
        if not (isinstance(sub.func, ast.Name) and sub.func.id == "getattr"):
            continue
        if len(sub.args) < 2:
            continue
        second_arg = sub.args[1]
        if isinstance(second_arg, ast.Constant) and second_arg.value == "minimal_fix":
            return True
    return False


def test_gate_cli_diagnostic_printer_includes_all_diagnostic_classes() -> None:
    """The CLI's _check_onnx_file printer's isinstance tuple
    must be the union of all *Diagnostic classes defined in
    runner.py plus those exported via furqan_lint.onnx_adapter.
    Round-34 HIGH-1 bug-class closure."""
    runner_classes = _diagnostic_classes_from_runner(RUNNER_PATH)
    init_classes = _diagnostic_exports_from_init(ONNX_INIT_PATH)
    expected = runner_classes | init_classes
    actual = _printer_isinstance_classes(CLI_PATH)
    missing = expected - actual
    extra = actual - expected
    assert not missing, (
        f"CLI printer's isinstance tuple is missing diagnostic classes: "
        f"{sorted(missing)}. Round-34 HIGH-1 bug class: when a new "
        f"*Diagnostic family is added to the runner or __all__, the "
        f"printer's tuple must be extended in the same commit. The "
        f"surface drops the diagnostic body otherwise."
    )
    # Extras are fine (printer can be a superset; new families may
    # ship and not yet have their isinstance entry tightened up).
    # But we report them so a future refactor sees them.
    if extra:
        print(f"CLI printer isinstance has unrecognized classes: {sorted(extra)}")


def test_gate_cli_diagnostic_printer_prints_minimal_fix() -> None:
    """The CLI's _check_onnx_file printer must call
    getattr(d, 'minimal_fix', None) inside the diagnostic-printing
    loop. Round-34 v0.9.3.1 carry-forward Part 5b(a): the ONNX
    printer must match the Python/Rust/Go printer pattern that
    prints both diagnosis AND minimal_fix."""
    assert _printer_has_minimal_fix_block(CLI_PATH), (
        "CLI _check_onnx_file printer is missing the "
        "getattr(d, 'minimal_fix', None) block. The Python, Rust, "
        "and Go marad printers in the same cli.py print both "
        "d.diagnosis AND d.minimal_fix; the ONNX printer must "
        "match this pattern. Round-34 v0.9.3.1 carry-forward."
    )


def test_gate_negative_test_parser_detects_missing_entry(tmp_path: Path) -> None:
    """Negative-test self-verification: synthesize a CLI source
    with the printer missing one *Diagnostic class; assert the
    AST-based parser correctly identifies the missing entry.
    This proves the gate's parser actually works rather than
    silently passing because the real codebase happens to be
    correct."""
    fake_cli = tmp_path / "fake_cli.py"
    fake_cli.write_text(
        "def _check_onnx_file(path):\n"
        "    diagnostics = []\n"
        "    for name, d in diagnostics:\n"
        "        if isinstance(d, AllPathsEmitDiagnostic | OpsetComplianceDiagnostic):\n"
        "            print(d.diagnosis)\n",
        encoding="utf-8",
    )
    found = _printer_isinstance_classes(fake_cli)
    assert found == {"AllPathsEmitDiagnostic", "OpsetComplianceDiagnostic"}
    # Synthesize an "expected" set with three families; the missing
    # one must surface.
    expected = {
        "AllPathsEmitDiagnostic",
        "OpsetComplianceDiagnostic",
        "ShapeCoverageDiagnostic",
    }
    missing = expected - found
    assert missing == {"ShapeCoverageDiagnostic"}, (
        "negative-test parser failed to identify ShapeCoverageDiagnostic "
        "as missing from the synthetic CLI source"
    )
