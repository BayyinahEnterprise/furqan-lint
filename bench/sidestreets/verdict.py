"""furqan-lint's verdict on a specimen, in-process (module API + source tree)."""

from __future__ import annotations

import ast

from furqan.errors.marad import Marad

from furqan_lint.adapter import translate_source
from furqan_lint.runner import check_python_module


def verdict(source: str, fname: str = "f") -> dict[str, bool]:
    diags = check_python_module(translate_source(source), ast.parse(source))
    tag = f"function '{fname}'"
    out = {"d24": False, "r3": False, "d11": False, "d11_note": False, "return_none": False}
    for name, d in diags:
        text = str(d)
        owner = getattr(d, "function_name", None)
        if owner is not None:
            if owner != fname:
                continue
        elif tag not in text:
            continue
        if name == "all_paths_return":
            out["d24"] = True
        elif name == "zero_return_path":
            out["r3"] = True
        elif name == "return_none_mismatch":
            out["return_none"] = True
        elif name == "status_coverage":
            if isinstance(d, Marad):
                out["d11"] = True
            else:
                out["d11_note"] = True
    return out
