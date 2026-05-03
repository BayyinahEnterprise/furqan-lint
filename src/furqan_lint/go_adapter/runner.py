"""Run structural checkers on a translated Go ``Module``.

Phase 1 (v0.8.0) wires two checkers:

* **D24 (all-paths-return)** via upstream
  ``furqan.checker.check_all_paths_return``. Same upstream
  primitive as the Python and Rust runners.
* **D11 (status-coverage with the Go ``(T, error)`` firing
  shape)** via upstream ``check_status_coverage`` with the
  cross-language ``_is_may_fail_producer`` predicate from
  ``furqan_lint.runner``. Phase B per ADR-002 §10 Q3 follow-up.
  D11 wiring lands in v0.8.0 commit 4 (this commit ships D24
  only).

Order: D24 -> D11. They are independent of each other.

Out of scope for Phase 1:

* R3 (zero-return): Go has no Rust-style ``panic!()`` /
  ``todo!()`` body-shape analogue. The closest equivalent is
  ``log.Fatal()`` / ``os.Exit()`` which is a function call, not
  a body shape. Deferred until a concrete user-reported false
  negative motivates the design.
* Generics, cross-package symbol resolution, ``go/types``: see
  ADR-002.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from furqan.checker.all_paths_return import check_all_paths_return

if TYPE_CHECKING:
    from furqan.parser.ast_nodes import Module


def check_go_module(module: Module) -> list[tuple[str, object]]:
    """Run the v0.8.0 Go checker pipeline on a translated Module.

    v0.8.0 commit 3 ships D24 only. Commit 4 adds D11 wiring with
    the cross-language ``_is_may_fail_producer`` predicate.

    Note: this runner does NOT call ``check_ring_close`` (R3).
    Go has no body-shape analogue to Rust's annotated-fn-with-
    empty-body pattern; deferred to whichever Phase introduces a
    Go-specific zero-return checker, if any.
    """
    diagnostics: list[tuple[str, object]] = []
    for d in check_all_paths_return(module):
        diagnostics.append(("all_paths_return", d))
    return diagnostics
