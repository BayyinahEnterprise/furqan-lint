"""Pinning test for F25 closure substrate contract.

Per Phase G11.0.5 al-Furqan (Round 32 audit F25): the
smoke-test workflow's identity-pattern declaration was a
regex (.*) that did not match the OIDC certificate's literal
SAN. The substrate-side closure is a workflow YAML fix
(ci.yml uses literal 'ci.yml' instead of regex '.*'). These
tests pin the substrate's contract: sigstore-python's
Identity policy is literal-only at sigstore 3.x; regex
patterns require composition policies (AllOf / AnyOf /
per-OIDC-claim policies like GitHubWorkflowRef) which is
deferred Option B (per Round 32 audit section 3).

These tests run on every PR (per project convention
``pytestmark = pytest.mark.unit``). If a future PR introduces a
composition-based identity policy via the workflow OR via
Python code without first adopting Option B's chartered
scope, these tests catch it at PR review time.

Per v1.2 audit corrections (C-1 + A-1): tests pin
empirically-verified symbols only (sigstore 3.6.7 substrate
inventory). v1.1's ``isinstance(identity, VerificationPolicy)``
crashed at runtime because ``VerificationPolicy`` is a
non-runtime-checkable ``typing.Protocol``; v1.2 drops the
isinstance check and relies on the regex-method-name-absence
assertion as the load-bearing literal-vs-regex contract pin.
"""

# ruff: noqa: E402

from __future__ import annotations

import pytest

# Per project convention (5 registered markers in
# pyproject.toml: network, slow, unit, integration, mock).
pytestmark = pytest.mark.unit

# Skip if sigstore is genuinely not installed; the test pins
# the policy-class contract, not sigstore-installed-ness.
pytest.importorskip("sigstore")


def test_step6_identity_policy_is_literal_only() -> None:
    """F25 substrate contract: Identity is literal, not regex.

    Asserts that sigstore-python's Identity policy stores its
    identity argument and exposes no regex-compilation surface
    on its public method set. Per Round 32 audit section 2:
    Identity.verify performs literal set-membership matching;
    regex patterns require a different mechanism (composition
    policies / per-OIDC-claim policies), which is Option B
    (deferred).

    Per v1.2 audit C-1 fix (Option C-1-A): pin behavior via
    public API only. Do NOT use ``isinstance`` against
    ``VerificationPolicy``; it is a non-runtime-checkable
    ``typing.Protocol`` and the call raises ``TypeError`` at
    runtime. The regex-method-name absence check is the
    substrate contract; it stands as the load-bearing
    assertion.
    """
    from sigstore.verify.policy import Identity

    # Construct an Identity with a string containing regex
    # metacharacters (the F25 case verbatim). Identity treats
    # this as a literal string, not as a compiled regex pattern.
    pattern_with_regex_chars = "https://github.com/owner/repo/.github/workflows/.*@refs/heads/main"
    identity = Identity(
        identity=pattern_with_regex_chars,
        issuer="https://token.actions.githubusercontent.com",
    )

    # Substrate contract: no regex-compilation API surface on
    # the public method set. Identity does not expose match /
    # search / fullmatch / compile / pattern as public methods;
    # it is not a regex matcher. This is the load-bearing
    # assertion of the test.
    public_methods = {m for m in dir(identity) if not m.startswith("_")}
    regex_method_names = {
        "match",
        "search",
        "fullmatch",
        "compile",
        "pattern",
    }
    overlap = regex_method_names & public_methods
    assert not overlap, (
        f"Identity policy unexpectedly exposes regex API "
        f"surface: {overlap}. This breaks the F25 substrate "
        f"contract (Identity is literal, not regex). If "
        f"sigstore-python has merged regex semantics into "
        f"Identity, the F25 corrective shape needs revisiting."
    )


def test_step6_composition_policies_not_wired_in_v1() -> None:
    """F25 substrate contract: composition policies not wired.

    Pin against empirically-verified symbols (per v1.1 audit
    C-1 fix; v1.0 referenced a fictional ``IdentityPattern``
    that does not exist in sigstore-python 3.6.7). The actual
    mechanisms sigstore-python provides for pattern-matching
    variations are (per the v1.2 audit's
    ``dir(sigstore.verify.policy)`` enumeration): AllOf,
    AnyOf, GitHubWorkflowRef, GitHubWorkflowName,
    GitHubWorkflowRepository, GitHubWorkflowSHA,
    GitHubWorkflowTrigger, OIDCSourceRepositoryURI.

    v0.11.6 wires only Identity (literal) and UnsafeNoOp
    (no-policy escape) from sigstore.verify.policy. This test
    pins that wiring. Future Option B adoption (composition-
    based identity policies) requires updating this test as
    part of that PR's chartered scope.
    """
    from pathlib import Path

    import furqan_lint.gate11.verification as verification_module

    source_text = Path(verification_module.__file__).read_text()

    # The substrate-blessed policy class at v0.11.6 (substring
    # check is robust to import-form variations: bare import,
    # qualified import, alias).
    assert "Identity" in source_text, (
        "F25 substrate contract: verification.py must wire "
        "the Identity policy from sigstore.verify.policy. If "
        "this assertion fails, the verifier's identity policy "
        "wiring has been removed and F25's substrate shape "
        "needs review."
    )

    # Forbidden composition / per-OIDC-claim policies at
    # v0.11.6. Any of these arriving means Option B (or a
    # variant) has landed and this test must be updated as
    # part of that PR's scope. Per v1.2 audit A-1 fix, the
    # list is the 8-entry empirically-verified inventory from
    # ``dir(sigstore.verify.policy)``.
    forbidden_composition_or_claim_policies = [
        "AllOf",
        "AnyOf",
        "GitHubWorkflowRef",
        "GitHubWorkflowName",
        "GitHubWorkflowRepository",
        "GitHubWorkflowSHA",
        "GitHubWorkflowTrigger",
        "OIDCSourceRepositoryURI",
    ]
    for symbol in forbidden_composition_or_claim_policies:
        assert symbol not in source_text, (
            f"F25 substrate contract: verification.py at "
            f"v0.11.6 should NOT reference {symbol!r}. If "
            f"composition / per-OIDC-claim policies have "
            f"landed (Option B variant), update this test as "
            f"part of the Option B PR's scope. The v0.11.6 "
            f"wiring is Identity (literal) + UnsafeNoOp only."
        )
