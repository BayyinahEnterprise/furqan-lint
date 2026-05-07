# Security Policy

## Supported versions

| Version | Status                |
|---------|-----------------------|
| 0.8.x   | Supported             |
| 0.7.x   | End-of-life           |
| <= 0.6  | End-of-life           |

Only the latest 0.8.x release receives security fixes. Earlier
0.7.x releases are end-of-life and will not be patched; upgrade
to the latest 0.8.x release to receive security updates.

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
