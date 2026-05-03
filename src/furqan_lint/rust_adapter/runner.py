"""Run structural checkers on a translated Rust ``Module``.

Phase 2 (v0.7.1) wires three checkers:

* **R3 (zero-return)** via upstream ``furqan.checker.check_ring_close``.
  ``check_ring_close`` emits R1 (unresolved type), R3
  (zero-return on annotated function), and R4 shapes; v0.7.1
  forwards only R3 via the ``_is_r3_shaped`` discriminator.
  R1 noise is additionally suppressed by passing a frozenset of
  well-known Rust primitive type names as ``imported_types``,
  so the upstream check does not flag every ``i32`` / ``Option`` /
  ``Result`` reference as "no compound type with that name".
* **D24 (all-paths-return)** via upstream ``check_all_paths_return``.
  Suppressed on functions R3 already fired on (R3 is the more
  specific verdict for the zero-return shape).
* **D11 (status-coverage on Option-returning helpers)** via
  upstream ``check_status_coverage`` with the
  ``_is_optional_union`` predicate from the Python runner. v0.7.1
  remains Option-only; Result-aware D11 is deferred to a later
  phase.

Order: R3 -> D24 -> D11. R3 first so D24 suppression on R3-fired
functions is reachable. D24 and D11 are independent of each other.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from furqan.checker.all_paths_return import check_all_paths_return
from furqan.checker.ring_close import check_ring_close
from furqan.checker.status_coverage import check_status_coverage

from furqan_lint.runner import _is_optional_union

if TYPE_CHECKING:
    from furqan.parser.ast_nodes import Module


# Well-known Rust primitive type names plus the special "None"
# token used by the v0.7.0 translator as the second arm of
# Option<T>. Passed to ``check_ring_close`` as ``imported_types``
# so R1 noise does not dominate the diagnostic output. The
# adapter does not synthesize CompoundTypeDef nodes for
# primitives; they are referenced by name only and would otherwise
# be flagged as "no compound type with this name".
_RUST_KNOWN_TYPES: frozenset[str] = frozenset(
    {
        # Integer types
        "i8",
        "i16",
        "i32",
        "i64",
        "i128",
        "isize",
        "u8",
        "u16",
        "u32",
        "u64",
        "u128",
        "usize",
        # Floating-point
        "f32",
        "f64",
        # Other primitives
        "bool",
        "char",
        "str",
        "String",
        # Unit type
        "()",
        # Standard generics that the translator references by head
        "Result",
        "Option",
        "Box",
        "Vec",
        "Rc",
        "Arc",
        # Adapter-internal: second arm of Option<T> per the v0.7.0
        # translator (Option<T> -> UnionType(T, TypePath("None"))).
        "None",
    }
)


def check_rust_module(module: Module) -> list[tuple[str, object]]:
    """Run the v0.7.1 checker pipeline on a translated Rust Module.

    Returns a list of ``(checker_name, diagnostic)`` tuples. The
    CLI separates marads from advisories for display.

    Order: R3 -> D24 (suppressed where R3 fired) -> D11. R3 and
    D24 are non-overlapping in practice (D24 needs at least one
    return present to fire, R3 needs zero), but the suppression
    is pinned by a test as a forward-compat defensive measure.
    """
    diagnostics: list[tuple[str, object]] = []

    # R3: zero-return on annotated functions.
    r3_function_names: set[str] = set()
    for diag in check_ring_close(module, imported_types=_RUST_KNOWN_TYPES):
        if _is_r3_shaped(diag):
            diagnostics.append(("zero_return_path", diag))
            name = _diagnostic_function_name(diag)
            if name:
                r3_function_names.add(name)

    # D24: skip any function R3 already fired on.
    for diag in check_all_paths_return(module):
        name = _diagnostic_function_name(diag)
        if name and name in r3_function_names:
            continue
        diagnostics.append(("all_paths_return", diag))

    # D11: status-coverage on Option-returning helpers.
    for diag in check_status_coverage(module, producer_predicate=_is_optional_union):
        diagnostics.append(("status_coverage", diag))

    return diagnostics


def _is_r3_shaped(diag: object) -> bool:
    """True iff the ``check_ring_close`` diagnostic is the R3 shape
    (function declares non-None return type but body has no
    return statement).

    ``check_ring_close`` emits R1, R3, R4 (Marad shapes) and may
    also emit Advisory shapes for non-violation observations.
    v0.7.1 forwards only R3. Detection is by diagnosis prose
    prefix; we read either ``diagnosis`` (Marad) or ``message``
    (Advisory) defensively. Pinned by
    ``test_is_r3_shaped_recognises_only_r3`` so the discriminator
    breaks at test time, not at user time, if upstream prose drifts.
    """
    text = getattr(diag, "diagnosis", None) or getattr(diag, "message", None) or ""
    return "but its body" in text


_FUNCTION_NAME_RE = re.compile(r"function '([^']+)'")


def _diagnostic_function_name(diag: object) -> str:
    """Extract the function name a Furqan diagnostic is attached
    to, by parsing the prose ``function 'NAME'`` from either the
    ``diagnosis`` (Marad) or ``message`` (Advisory) attribute.
    Returns the empty string if no match.

    Returns ``str`` (not ``str | None``) so the consumer-side D11
    discipline is honestly propagated; the empty-string sentinel
    is filtered by the caller's ``if name and name in ...`` check.
    """
    text = getattr(diag, "diagnosis", None) or getattr(diag, "message", None) or ""
    match = _FUNCTION_NAME_RE.search(text)
    return match.group(1) if match else ""
