"""Regression tests for the v0.3.5 corrective fixes.

Two documented limitations from the Fraz audit chain are
promoted to fixes in v0.3.5:

* try/except modeling - the false-negative D24 case (a function
  whose only return is inside a ``try`` block whose except
  handler falls through). Documented since v0.3.1 as
  "Exception-driven fall-through."
* PEP 604 redundant None - ``None | None`` now translates to
  bare ``TypePath("None")``, the same shape Optional[None]
  (v0.3.4) and Union[None] (v0.3.3) produce. Documented in
  v0.3.4 as a v0.4.0 candidate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from furqan.parser.ast_nodes import TypePath, UnionType

from furqan_lint.adapter import translate_source
from furqan_lint.return_none import check_return_none
from furqan_lint.runner import check_python_module


REPO_ROOT = Path(__file__).resolve().parents[1]


def _d24(module) -> list:
    return [d for n, d in check_python_module(module) if n == "all_paths_return"]


# ---------------------------------------------------------------------------
# try/except modeling
# ---------------------------------------------------------------------------

def test_try_return_except_no_return_fires_d24() -> None:
    """probe11: ``try: return X; except: pass`` - the except branch
    falls through despite the function declaring a return type."""
    src = (
        "def f() -> int:\n"
        "    try:\n"
        "        return 42\n"
        "    except ValueError:\n"
        "        pass\n"
    )
    module = translate_source(src, "<t>")
    assert len(_d24(module)) == 1


def test_try_no_return_except_return_fires_d24() -> None:
    """try.body has no return, only the except branch returns -
    the success path falls through."""
    src = (
        "def f(x) -> int:\n"
        "    try:\n"
        "        x = int(x)\n"
        "    except ValueError:\n"
        "        return 0\n"
    )
    module = translate_source(src, "<t>")
    assert len(_d24(module)) == 1


def test_try_return_except_return_passes_d24() -> None:
    """Both the success path and the handler return - D24 must
    NOT fire."""
    src = (
        "def f() -> int:\n"
        "    try:\n"
        "        return 42\n"
        "    except ValueError:\n"
        "        return 0\n"
    )
    module = translate_source(src, "<t>")
    assert _d24(module) == []


def test_try_except_else_all_return_passes_d24() -> None:
    """probe12: try-body assigns, except returns, else returns -
    every branch returns. D24 must NOT fire."""
    src = (
        "def f(x) -> int:\n"
        "    try:\n"
        "        y = int(x)\n"
        "    except ValueError:\n"
        "        return 0\n"
    "    else:\n"
        "        return y\n"
    )
    module = translate_source(src, "<t>")
    assert _d24(module) == []


def test_finally_return_covers_all_paths() -> None:
    """A return in ``finally`` covers every possible exit path
    regardless of try/except shape."""
    src = (
        "def f() -> int:\n"
        "    try:\n"
        "        x = 1\n"
        "    finally:\n"
        "        return 0\n"
    )
    module = translate_source(src, "<t>")
    assert _d24(module) == []


def test_try_return_none_except_pass_fires_return_none() -> None:
    """The return_none_mismatch checker must still fire on
    ``return None`` inside a try block."""
    src = (
        "def f() -> str:\n"
        "    try:\n"
        "        return None\n"
        "    except Exception:\n"
        "        return 'fallback'\n"
    )
    module = translate_source(src, "<t>")
    assert len(check_return_none(module)) == 1


def test_bare_except_no_return_fires_d24() -> None:
    """``except:`` (no exception type) with no return is treated
    the same as ``except Exception:`` for D24's purposes."""
    src = (
        "def f() -> int:\n"
        "    try:\n"
        "        return 42\n"
        "    except:\n"
        "        pass\n"
    )
    module = translate_source(src, "<t>")
    assert len(_d24(module)) == 1


def test_nested_try_in_if_fires_correctly() -> None:
    """A try block inside an if branch that doesn't all-paths-
    return on its own still fires when the outer if has no else."""
    src = (
        "def f(x) -> int:\n"
        "    if x:\n"
        "        try:\n"
        "            return 1\n"
        "        except Exception:\n"
        "            pass\n"
    )
    module = translate_source(src, "<t>")
    assert len(_d24(module)) == 1


def test_try_with_multiple_handlers_all_return_passes() -> None:
    """All handlers return, success path returns - whole function
    all-paths-returns."""
    src = (
        "def f(x) -> int:\n"
        "    try:\n"
        "        return int(x)\n"
        "    except ValueError:\n"
        "        return 0\n"
        "    except TypeError:\n"
        "        return -1\n"
    )
    module = translate_source(src, "<t>")
    assert _d24(module) == []


def test_try_with_multiple_handlers_one_falls_through_fires() -> None:
    """If any handler falls through, D24 fires."""
    src = (
        "def f(x) -> int:\n"
        "    try:\n"
        "        return int(x)\n"
        "    except ValueError:\n"
        "        return 0\n"
        "    except TypeError:\n"
        "        pass\n"
    )
    module = translate_source(src, "<t>")
    assert len(_d24(module)) == 1


# ---------------------------------------------------------------------------
# PEP 604 None | None symmetric tightening
# ---------------------------------------------------------------------------

def test_pipe_none_none_translates_to_bare_none_typepath() -> None:
    """``None | None`` must translate to bare ``TypePath(base="None")``,
    matching Optional[None] (v0.3.4) and Union[None] (v0.3.3)."""
    src = (
        "def f() -> None | None:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    rt = module.functions[0].return_type
    assert isinstance(rt, TypePath)
    assert rt.base == "None"


def test_pipe_none_none_return_none_passes() -> None:
    """``None | None`` is type(None); ``return None`` is correct
    typing and must NOT fire return_none_mismatch."""
    src = (
        "def f() -> None | None:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_pipe_int_none_still_translates_to_union_type() -> None:
    """Regression: the v0.3.5 None|None shortcut must NOT affect
    the normal ``X | None`` path."""
    src = (
        "def f() -> int | None:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    rt = module.functions[0].return_type
    assert isinstance(rt, UnionType)
    assert rt.left.base == "int"
    assert rt.right.base == "None"


def test_redundant_pipe_int_none_none_still_passes() -> None:
    """``int | None | None`` is semantically ``int | None``;
    return None must continue to PASS."""
    src = (
        "def f() -> int | None | None:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []
