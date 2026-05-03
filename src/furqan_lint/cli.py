"""Command-line entry point for ``furqan-lint``.

Subcommands:

* ``furqan-lint check <path>``           run the structural checks
  on a file or recursively on a directory of ``.py`` files.
* ``furqan-lint diff <old.py> <new.py>`` compare two versions of a
  module's public API and fire on removed names.
* ``furqan-lint version``                print the package version.
* ``furqan-lint --help``                 print usage.

Exit codes:

* ``0`` clean (no marads).
* ``1`` at least one marad fired.
* ``2`` a Python source file failed to parse.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "node_modules",
        ".tox",
        ".mypy_cache",
        "target",
    }
)


def main() -> int:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        _print_usage()
        return 0

    if args[0] == "version":
        from furqan_lint import __version__

        print(f"furqan-lint {__version__}")
        return 0

    if args[0] == "check" and len(args) >= 2:
        target = Path(args[1])
        if target.is_file():
            return _check_file(target)
        if target.is_dir():
            return _check_directory(target)
        print(f"Not found: {target}", file=sys.stderr)
        return 1

    if args[0] == "diff" and len(args) >= 3:
        old_path = Path(args[1])
        new_path = Path(args[2])
        return _check_additive(old_path, new_path)

    print(f"Unknown command: {args[0]}", file=sys.stderr)
    _print_usage(file=sys.stderr)
    return 1


def _print_usage(file: TextIO | None = None) -> None:
    out = file if file is not None else sys.stdout
    print("furqan-lint: structural-honesty checks for Python", file=out)
    print(file=out)
    print("Usage:", file=out)
    print("  furqan-lint check <file.py>", file=out)
    print("  furqan-lint check <directory/>", file=out)
    print("  furqan-lint diff <old.py> <new.py>", file=out)
    print("  furqan-lint version", file=out)


def _check_file(path: Path) -> int:
    """Dispatch a check by file suffix.

    .py -> existing Python adapter pipeline.
    .rs -> Rust adapter (Phase 1, opt-in via [rust] extra). If
    tree-sitter is not installed, prints an install hint to stderr
    and exits 1 (not 2; not-installed is a configuration issue,
    not a parse failure).

    Any other suffix is treated as Python (back-compat with v0.6.x;
    callers who pass a .py.bak or similar still get the old behaviour).
    """
    if path.suffix == ".rs":
        return _check_rust_file(path)
    return _check_python_file(path)


def _check_python_file(path: Path) -> int:
    import ast as _ast

    from furqan.errors.marad import Advisory, Marad

    from furqan_lint.adapter import translate_tree
    from furqan_lint.runner import check_python_module
    from furqan_lint.zero_return import ZeroReturnDiagnostic

    try:
        source = path.read_text(encoding="utf-8")
        tree = _ast.parse(source, filename=str(path))
        module = translate_tree(tree, str(path))
    except SyntaxError as e:
        line = e.lineno if e.lineno is not None else 0
        print(f"SYNTAX ERROR  {path}:{line}")
        print(f"  {e.msg}")
        return 2

    diagnostics = check_python_module(module, source_tree=tree)
    marads = [(n, d) for n, d in diagnostics if isinstance(d, Marad)]
    advisories = [(n, d) for n, d in diagnostics if isinstance(d, Advisory)]
    r3_diags = [(n, d) for n, d in diagnostics if isinstance(d, ZeroReturnDiagnostic)]
    is_failure = bool(marads or r3_diags)

    if not diagnostics:
        print(f"PASS  {path}")
        print("  4 structural checks ran. Zero diagnostics.")
        return 0

    if marads:
        print(f"MARAD  {path}")
        print(f"  {len(marads)} violation(s):")
        for name, m in marads:
            print(f"    [{name}] {m.diagnosis}")
            fix = getattr(m, "minimal_fix", None)
            if fix:
                print(f"      fix: {fix}")
        print()

    if r3_diags:
        print(f"MARAD  {path}")
        print(f"  {len(r3_diags)} ring-close violation(s):")
        for name, d in r3_diags:
            print(f"    [{name}] {d.diagnosis}")
        print()

    if advisories:
        print(f"ADVISORY  {path}")
        print(f"  {len(advisories)} note(s):")
        for name, a in advisories:
            msg = getattr(a, "message", str(a))
            print(f"    [{name}] {msg}")

    return 1 if is_failure else 0


def _check_rust_file(path: Path) -> int:
    """Lint a single .rs file using the Phase 1 Rust adapter.

    Runs D24 (all-paths-return) and D11 (status-coverage) only.
    Phase 2 will add the Rust analogue of return_none_mismatch and
    a ring-close R3 equivalent.
    """
    try:
        from furqan_lint.rust_adapter import (
            RustExtrasNotInstalled,
            RustParseError,
        )
        from furqan_lint.rust_adapter import parse_file as parse_rust
    except ImportError:
        print(
            "Rust support not installed. Run: pip install furqan-lint[rust]",
            file=sys.stderr,
        )
        return 1

    from furqan.errors.marad import Advisory, Marad

    try:
        module = parse_rust(path)
    except RustExtrasNotInstalled as e:
        # The package itself imported, but tree_sitter / tree_sitter_rust
        # could not be imported when parse_file probed for them. Print
        # the typed exception's message (the install hint) rather than
        # dumping a Python traceback.
        print(str(e), file=sys.stderr)
        return 1
    except RustParseError as e:
        print(f"PARSE ERROR  {path}:{e.line}")
        print(f"  {e.kind}")
        return 2

    # Phase 2 (v0.7.1): R3 + D24 + D11 via the Rust runner. The
    # runner wires upstream check_ring_close (filtered to R3-shaped
    # diagnostics), check_all_paths_return (D24), and
    # check_status_coverage (D11) in the order R3 -> D24 -> D11.
    from furqan_lint.rust_adapter.runner import check_rust_module

    diagnostics = check_rust_module(module)
    marads = [(n, d) for n, d in diagnostics if isinstance(d, Marad)]
    advisories = [(n, d) for n, d in diagnostics if isinstance(d, Advisory)]

    if not diagnostics:
        print(f"PASS  {path}")
        print("  3 structural checks ran (Rust Phase 2: R3 + D24 + D11). Zero diagnostics.")
        return 0

    if marads:
        print(f"MARAD  {path}")
        print(f"  {len(marads)} violation(s):")
        for name, m in marads:
            print(f"    [{name}] {m.diagnosis}")
            fix = getattr(m, "minimal_fix", None)
            if fix:
                print(f"      fix: {fix}")
        print()

    if advisories:
        print(f"ADVISORY  {path}")
        print(f"  {len(advisories)} note(s):")
        for name, a in advisories:
            msg = getattr(a, "message", str(a))
            print(f"    [{name}] {msg}")

    return 1 if marads else 0


def _check_additive(old_path: Path, new_path: Path) -> int:
    from furqan_lint.additive import DynamicAllError, check_additive_api

    try:
        old_source = old_path.read_text(encoding="utf-8")
        new_source = new_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Cannot read source: {e}", file=sys.stderr)
        return 1

    try:
        diagnostics = check_additive_api(new_source, old_source, filename=str(new_path))
    except SyntaxError as e:
        line = e.lineno if e.lineno is not None else 0
        print(f"SYNTAX ERROR  {e.filename or new_path}:{line}")
        print(f"  {e.msg}")
        return 2
    except DynamicAllError as e:
        path = new_path if e.where == "new" else old_path
        print(f"INDETERMINATE  {path} (additive-only)")
        print(f"  {e}")
        print(
            "  Refusing to certify a public surface that cannot be "
            "statically read. Replace the dynamic __all__ assignment "
            "with a literal list or tuple of string literals."
        )
        return 2

    if not diagnostics:
        print(f"PASS  {new_path} (additive-only)")
        print("  No public names removed.")
        return 0

    print(f"MARAD  {new_path} (additive-only)")
    print(f"  {len(diagnostics)} violation(s):")
    for m in diagnostics:
        print(f"    [additive_only] {m.diagnosis}")
        print(f"      fix: {m.minimal_fix}")
    return 1


def _check_directory(directory: Path) -> int:
    exit_code = 0
    files = sorted(
        p
        for p in directory.rglob("*")
        if p.is_file()
        and p.suffix in {".py", ".rs"}
        and not any(part in EXCLUDED_DIRS for part in p.parts)
    )
    if not files:
        print(f"No .py or .rs files found in {directory}")
        return 0
    for path in files:
        result = _check_file(path)
        exit_code = max(exit_code, result)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
