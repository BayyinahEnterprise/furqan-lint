# Security Policy

## Supported versions

| Version | Status                |
|---------|-----------------------|
| 0.10.x  | Supported             |
| 0.9.x   | Supported             |
| 0.8.x   | End-of-life           |
| 0.7.x   | End-of-life           |
| <= 0.6  | End-of-life           |

Only the latest 0.9.x and 0.10.x releases receive security
fixes. Earlier 0.7.x and 0.8.x releases are end-of-life and
will not be patched; upgrade to the latest 0.10.x release to
receive security updates.

## Reporting a vulnerability

Please do NOT file a public GitHub issue for security-impacting
bugs. Public disclosure before a fix ships gives potential
attackers a window during which the substrate is documented and
unpatched.

Instead, email the project lead directly:

- Bilal Syed Arfeen (project lead): doctordopemusic@gmail.com

Use a clear subject line such as "furqan-lint security report:
<short description>". Include:

- Affected version(s) (the output of `furqan-lint version`).
- A minimal reproducer (commands, fixture content, or a small
  patch that surfaces the issue).
- The impact you observed or believe is reachable.
- Any constraints on disclosure timing if you have a downstream
  release of your own to coordinate.

## Response time commitment

Best-effort within 14 days for an initial response. furqan-lint
is in its infancy and runs on a small team; turnaround on a fix
will depend on severity and the complexity of the substrate
change. We will acknowledge the report, confirm reproducibility,
and share an estimated fix-and-release window in the initial
response.

## Disclosure policy

Coordinated disclosure preferred. We will:

1. Confirm receipt within the response window above.
2. Work with you to scope the fix and a target release.
3. Publish the fix in a tagged release with a CHANGELOG entry
   that names the affected versions and the fix shape.
4. Credit the reporter in the CHANGELOG entry unless you ask
   to remain anonymous.

If a fix is not feasible within the agreed window, we will
discuss alternatives (workaround documentation, version
deprecation) before any public disclosure.


## Sigstore-CASM Gate 11 -- cryptographic substrate identity

The cryptographic substrate identity of the Sigstore-CASM Gate
11 family of phases (G11.0 through G11.12) is normatively
specified in `SAFETY_INVARIANTS.md` at the repository root.
Reporters of vulnerabilities affecting the Gate 11 substrate
should reference the relevant invariant section (1 through 7)
or disclosure (1 through 4) plus the corresponding `CASM-V-NNN`
error code where applicable.

Vulnerabilities in the upstream Sigstore stack (sigstore-python,
sigstore-rs, sigstore-go, Fulcio, Rekor, TUF) should be
reported to the Sigstore project via its own coordinated
disclosure channel; see https://github.com/sigstore/sigstore/security.

## Sigstore-CASM Gate 11 disclosures

Gate 11 ships as the opt-in `[gate11]` extra (v0.10.0+) and
inherits the Sigstore threat model documented in Newman et al.,
*Sigstore: Software Signing for Everybody* (ACM CCS 2022). Four
residual disclosures apply to any consumer running
`furqan-lint manifest verify` or `furqan-lint check --gate11`:

1. **Short-window OIDC-identity compromise.** A compromised
   OIDC token within the Fulcio certificate validity window
   (typically 10 minutes) can produce a CASM bundle that
   verifies cleanly. Mitigation lives in the identity provider,
   not in the lint.
2. **Typosquatting at the publish boundary.** Sigstore proves
   "identity X signed bytes Y at time T", not "identity X is
   the legitimate maintainer". Relying Parties must pin both
   the package name and the expected signing identity.
3. **Rekor entry queryability and privacy.** The public Rekor
   log publishes manifest hashes and public-surface name lists
   unencrypted. Confidential codebases should sign to the
   staging instance or a private transparency service rather
   than the public Rekor.
4. **Log-retention horizon.** Rekor retention is operational,
   not contractual. Long-horizon verification may need local
   mirroring of relevant entries.

Two Shape A scope statements are open against v0.10.0:

- **F4. Linter-substrate trust is recursive.** The
  `tooling.checker_set_hash` field records the checker code's
  integrity but does not prove the checker code itself is
  honest. Closing the recursion (signing furqan-lint releases
  with Gate 11) is a later round.
- **F7. Rekor entries leak public-surface shape.** Confidential
  codebases MUST NOT sign their CASM bundles to the public
  Rekor instance. Private-transparency-service routing is a
  later round.

Vulnerabilities in the Gate 11 verification flow itself
(misverification, signature bypass, namespace confusion) should
be reported through the same channel as other security reports.
Issues in upstream Sigstore (sigstore-python, Fulcio, Rekor)
should be reported to the Sigstore project; see
https://github.com/sigstore/sigstore-python#security.


## Sigstore-CASM Gate 11 Rust extension (v0.11.0)

The Phase G11.1 Rust extension uses the same Sigstore
substrate as the Phase G11.0 Python pipeline. The four
mandatory disclosures (OIDC issuer compromise; typosquatting;
Rekor privacy; log retention horizon) apply identically to
Rust manifests.

### Identity policy enforcement

Relying Parties MUST configure ``--expected-identity`` for
production verification. The default refuse-without-policy
behaviour (``CASM-V-035``) is a substrate-side enforcement
of Newman 2022 N2 (typosquatting at the publish boundary).
Use of ``--allow-any-identity`` in production CI is itself
an audit signal: it is an explicit opt-in to ``UnsafeNoOp()``
policy whose presence in CI logs is the substrate-side
visibility that the Sulayman-Naml ADVISORY pattern (Phase
G11.A Strategy 7) provides.
