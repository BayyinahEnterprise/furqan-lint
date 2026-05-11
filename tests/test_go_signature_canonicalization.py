"""Phase G11.2 (al-Mursalat) T03: Go signature canonicalization tests.

Pins the five canonical type-string outputs per al-Mursalat T03
rules 6-8 (mirror of Python H-4 closure rules 1-5 from
at-Tawbah T03):

  Rule 6: nested element-wise recursion
  Rule 7: multi-return iteration as list (not stringified)
  Rule 8: channel direction preservation

Each fixture is documented at the prompt's T03 specification
and pinned here so substrate drift in canonicalize rules
trips this test before the gate11-go-smoke-test would.
"""

# ruff: noqa: E402

from __future__ import annotations

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.go_signature_canonicalization import (
    _canonicalize_type,
    canonical_signature_fingerprint,
    canonicalize_function_signature,
)

# ---------------------------------------------------------------
# Rule 6: nested element-wise recursion
# ---------------------------------------------------------------


def test_rule_6_nested_slice_map_pointer_generic() -> None:
    """``[]map[string]*Result[T, E]`` canonicalizes as
    ``slice[map[string][pointer[Result[T,E]]]]`` per rule 6.

    Closes the H-4 nested-generic failure mode (Phase G11.0
    v0.10.0 Python fall-through). Each container token
    (slice, map, pointer) is explicitly named; the inner
    generic ``Result[T, E]`` recurses element-wise without
    tuple-stringification.
    """
    canonical = _canonicalize_type("[]map[string]*Result[T, E]")
    assert (
        canonical == "slice[map[string][pointer[Result[T,E]]]]"
    ), f"rule 6 nested recursion drift: got {canonical!r}"


# ---------------------------------------------------------------
# Rule 7: multi-return signature iteration
# ---------------------------------------------------------------


def test_rule_7_multi_return_iterates_as_list() -> None:
    """A signature ``(int, error)`` iterates ``ReturnTypeNames``
    as a list at the function-signature level; the canonical
    dict's ``return_types`` field is ``["int", "error"]``,
    NOT ``"(int, error)"`` (stringified).

    Closes failure mode #5 of as-Saffat ranked list (multi-
    return mis-iteration): if a future refactor collapsed the
    list into a string the fingerprint would change but the
    surface claim would not, which is the silent-pass mode
    rule 7 specifically forbids.
    """
    sig = canonicalize_function_signature(
        name="F",
        params=[],
        return_types=["int", "error"],
        is_variadic=False,
    )
    assert sig["return_types"] == ["int", "error"]
    assert isinstance(sig["return_types"], list)
    # Critically, NOT a string:
    assert not isinstance(sig["return_types"], str)


# ---------------------------------------------------------------
# Rule 8: channel direction preservation (three structurally
# distinct types)
# ---------------------------------------------------------------


def test_rule_8_channel_direction_preserved() -> None:
    """``chan T``, ``<-chan T``, ``chan<- T`` are three
    structurally distinct types per rule 8.

    The direction markers MUST be reflected in the canonical
    string. A future refactor that collapsed all three into
    ``channel[T]`` would silently equate distinct types; this
    fixture catches the drift.
    """
    bidirectional = _canonicalize_type("chan *T")
    recv_only = _canonicalize_type("<-chan *T")
    send_only = _canonicalize_type("chan<- *T")
    assert bidirectional == "channel[pointer[T]]"
    assert recv_only == "channel_recv[pointer[T]]"
    assert send_only == "channel_send[pointer[T]]"
    # All three must be distinct:
    assert bidirectional != recv_only
    assert bidirectional != send_only
    assert recv_only != send_only


def test_signal_channel_idiom() -> None:
    """``map[string]chan struct{}`` (the Go signal-channel
    idiom) canonicalizes preserving the map-of-channels-of-
    empty-struct structure.

    Tests rule 6 recursion through a map's value type into a
    channel container into a struct atom.
    """
    canonical = _canonicalize_type("map[string]chan struct{}")
    assert (
        canonical == "map[string][channel[struct{}]]"
    ), f"signal channel canonicalization drift: got {canonical!r}"


def test_variadic_context_idiom() -> None:
    """``func(ctx context.Context, opts ...Option) (Result, error)``
    -- the variadic + context idiom common in Go APIs.

    The variadic ``...Option`` is canonicalized as type
    ``Option`` with ``is_variadic=True`` at the signature
    level; the ``context.Context`` qualified-name atom is
    preserved verbatim; the multi-return ``(Result, error)``
    iterates as a list per rule 7.
    """
    sig = canonicalize_function_signature(
        name="DoWork",
        params=[
            {"name": "ctx", "type": "context.Context"},
            {"name": "opts", "type": "...Option"},
        ],
        return_types=["Result", "error"],
        is_variadic=True,
    )
    # context.Context preserved as qualified atom:
    assert sig["parameters"][0]["type"] == "context.Context"
    # Variadic ...Option canonicalized as the inner type;
    # variadic-ness captured at signature level:
    assert sig["parameters"][1]["type"] == "Option"
    assert sig["is_variadic"] is True
    # Multi-return iterates as list:
    assert sig["return_types"] == ["Result", "error"]
    # Signature is RFC 8785 hashable (sanity check the
    # downstream fingerprint computation works):
    fp = canonical_signature_fingerprint(sig)
    assert len(fp) == 64  # sha256 hex digest length
    assert all(c in "0123456789abcdef" for c in fp)
