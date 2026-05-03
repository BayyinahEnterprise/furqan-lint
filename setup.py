"""setup.py: invokes the [go] extra's build hook before standard build.

The hook (furqan_lint.go_adapter._build.build_goast) compiles the
goast binary if Go is available on the build machine. If Go is
absent, the hook prints a stderr note and exits cleanly so the
wheel still builds; runtime then raises GoExtrasNotInstalled
with the install hint. Same posture as the Rust [rust] extra
(wheel installs without tree_sitter; runtime fires the install
hint).
"""

from __future__ import annotations

import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

_REPO_ROOT = Path(__file__).resolve().parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


class build_py(_build_py):
    """Custom build_py that compiles the goast binary first."""

    def run(self) -> None:
        try:
            from furqan_lint.go_adapter._build import build_goast

            build_goast()
        except ImportError:
            # Adapter package not yet on path during initial build;
            # fall through to standard build_py. The runtime hint
            # path still works.
            pass
        super().run()


setup(cmdclass={"build_py": build_py})
