"""Documented limitation: same-named ``Union`` import from a non-typing module.

``from somelib import Union; -> Union[X, None]`` is treated as the
``typing.Union[X, None]`` form recognised in v0.3.2 Finding 1, even
though ``somelib.Union`` may have nothing to do with optionality.
The function returns ``None`` and PASSes silently (false negative)
in cases where ``somelib.Union`` is in fact unrelated.

The same gap applies to aliased imports: ``from typing import Union
as U; -> U[X, None]``.

The proper fix needs symbol-table tracking (parse imports, build
alias map, resolve ``U`` -> ``typing.Union`` and reject
``somelib.Union`` before the matcher runs). Same shape as the
``aliased_optional_import.py`` limitation. Probably Phase 4.

For v0.3.x: use the bare ``Union`` form (only when the import
actually came from ``typing``), the qualified ``typing.Union[X, None]``
form, or rename the import (``import typing as t``;
``t.Union[X, None]`` is recognised).

See README.md "Remaining limitations" -> "Aliased Optional / Union
imports."
"""
from __future__ import annotations

# In a real codebase this would resolve to a non-typing module's
# Union sentinel that has nothing to do with optionality. For the
# fixture we still import from typing so the file imports cleanly
# under static analysis; what we are pinning is the matcher's
# behaviour, which does not consult the import provenance either way.
from typing import Union  # imagine: ``from somelib import Union``


def f(x: int) -> Union[str, None]:
    # If ``Union`` came from a non-typing module, this would be a
    # false negative: the matcher treats the head as typing.Union
    # regardless of provenance, so the implicit ``return None`` path
    # is silently accepted as Optional. Until symbol-table tracking
    # lands, the behaviour is documented rather than fixed.
    if x > 0:
        return "y"
    return None
