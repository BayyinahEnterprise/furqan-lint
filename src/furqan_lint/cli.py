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


EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "node_modules",
        ".tox",
        ".mypy_cache",
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


def _print_usage(file=None) -> None:
    out = file if file is not None else sys.stdout
    print("furqan-lint: structural-honesty checks for Python", file=out)
    print(file=out)
    print("Usage:", file=out)
    print("  furqan-lint check <file.py>", file=out)
    print("  furqan-lint check <directory/>", file=out)
    print("  furqan-lint diff <old.py> <new.py>", file=out)
    print("  furqan-lint version", file=out)


def _check_file(path: Path) -> int:
    from furqan.errors.marad import Advisory, Marad

    from furqan_lint.adapter import translate_file
    from furqan_lint.runner import check_python_module

    try:
        module = translate_file(path)
    except SyntaxError as e:
        line = e.lineno if e.lineno is not None else 0
        print(f"SYNTAX ERROR  {path}:{line}")
        print(f"  {e.msg}")
        return 2

    diagnostics = check_python_module(module)
    marads = [(n, d) for n, d in diagnostics if isinstance(d, Marad)]
    advisories = [(n, d) for n, d in diagnostics if isinstance(d, Advisory)]

    if not diagnostics:
        print(f"PASS  {path}")
        print("  3 structural checks ran. Zero diagnostics.")
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
    from furqan_lint.additive import check_additive_api

    try:
        old_source = old_path.read_text(encoding="utf-8")
        new_source = new_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Cannot read source: {e}", file=sys.stderr)
        return 1

    try:
        diagnostics = check_additive_api(
            new_source, old_source, filename=str(new_path)
        )
    except SyntaxError as e:
        line = e.lineno if e.lineno is not None else 0
        print(f"SYNTAX ERROR  {e.filename or new_path}:{line}")
        print(f"  {e.msg}")
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
    py_files = sorted(
        p
        for p in directory.rglob("*.py")
        if not any(part in EXCLUDED_DIRS for part in p.parts)
    )
    if not py_files:
        print(f"No .py files found in {directory}")
        return 0
    for path in py_files:
        result = _check_file(path)
        if result > exit_code:
            exit_code = result
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
