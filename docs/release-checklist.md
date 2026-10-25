# furqan-lint release checklist

Phase G10.5 (al-Mubin) deliverable. Codifies the manual gates
that go alongside the automated steps in
`.github/workflows/release.yml`. The release workflow handles
PyPI publish + PyPI verification (T01) + GitHub Release object
creation (T02) automatically; this document covers everything
that runs locally before the tag push, plus the post-publish
verification gates the maintainer must walk through manually
in their browser and a fresh venv.

This document is under 600 lines by design; it is a checklist,
not a reference manual.

## 0. Pre-tag verification gates (al-Hujurat T01)

Phase G10.5.A al-Hujurat (v0.11.7) closes Round 29 anomaly
A1 by promoting these gates from convention to documented
release-checklist requirements.

Before pushing a tag that triggers `release.yml`, the
following gates MUST be verified:

1. **PR review.** The commit being tagged MUST have been
   reviewed via a PR (either by a co-maintainer or, in the
   single-person audit-of-self pattern, by the project lead
   running an audit checklist against the PR diff before
   merge). A direct-to-main commit followed by a tag on that
   commit is a documented bypass and MUST be accompanied by a
   CHANGELOG entry naming the bypass and the rationale. The
   GitHub branch protection rule on `main` (al-Hujurat T02)
   mechanically enforces this for non-admin pushes; admin
   override (`enforce_admins: false`) preserves the
   audit-of-self pattern when justified.
2. **Sandbox-CI parity** (per F20 / al-Hujurat T06). Before
   push, run `ruff check . && ruff format --check .` against
   the assembled patch series in a virtualenv with the
   CI-pinned ruff version (see `docs/sandbox-ci-parity.md`).
3. **Pytest collect-only count.** The test count claimed in
   the CHANGELOG entry MUST match `pytest --collect-only`
   actual count (per CHANGELOG-math gate; see al-Hujurat
   T04).

A bypass of any of (1) -- (3) MUST be documented in the
CHANGELOG entry under a "Process bypass" subsection naming
which gate was bypassed and the rationale.

The gates here are the verification mandate that surrounds
the substrate work documented in subsequent sections of this
checklist.

### Canonical sequence for new releases (al-Hujurat T02 / F5)

The branch protection rule on `main` (al-Hujurat T02) applies
to v0.11.7 and all subsequent releases. The canonical
chronology that makes v0.11.7 the worked example by
chronology, and applies to every later release without
modification:

1. **Open PR** for the release branch (convention-based for
   v0.11.7 since T02 is being applied; mechanically required
   for v0.11.8 and later).
2. **Project-lead self-approves** the PR (audit-of-self
   pattern; co-maintainer review accepted when a co-maintainer
   exists).
3. **Merge PR** to main.
4. **Apply T02 branch protection rule** via the `gh api -X
   PUT` call below (one-time for v0.11.7; already in effect
   for subsequent releases; verify via `gh api .../protection`).
5. **Push the release tag** (`git tag vX.Y.Z merge_commit && git
   push origin vX.Y.Z`); release.yml runs.
6. **Record the protection-rule timestamp** (or last-verified
   timestamp for subsequent releases) in the release
   CHANGELOG entry's "Process-corrective amendment timestamp
   record" subsection.

The `gh api -X PUT /repos/BayyinahEnterprise/furqan-lint/branches/main/protection`
JSON payload sets `required_pull_request_reviews` (one
approving review required), `enforce_admins: false` (admin
override preserved for the audit-of-self pattern when
justified), and disables force-push and branch deletion.
Sub-step 6 captures the configuration `updated_at` field as
returned by the GitHub API.

 Section 1 below is the substrate-side pre-tag
checklist (version sync, CHANGELOG content, etc.); Section 0
above is the process-side wrapper.

## 1. Pre-tag checklist

Before pushing a `vX.Y.Z` tag, confirm the following on the
release branch (the branch that will be merged into main and
then tagged):

- **Version sync**: the version string is identical in
  `pyproject.toml`'s `[project].version` field, in
  `src/furqan_lint/__init__.py`'s `__version__` constant, and
  in the CHANGELOG.md `## [X.Y.Z]` header. The release.yml
  build job's `Verify version-tag-CHANGELOG sync` step
  catches mismatches but the local check is faster.
- **CHANGELOG entry**: under the correct version heading;
  `<DATE>` placeholder filled in with the planned release
  date; `<TBD>` test-count placeholder filled in with the
  actual `pytest --collect-only -q` count delta from the
  prior release.
- **CI green on main**: `gh run list --workflow=ci.yml --branch=main --limit=1`
  reports `success`. If a flaky run failed for non-substrate
  reasons (`infrastructure failure`, network-bound smoke job
  on a fork PR), `gh run rerun <id>` first.
- **Pre-commit hooks**: `pre-commit run --all-files` clean,
  including the SAFETY_INVARIANTS.md presence hook (Phase
  G11.A T-A4) and the no-em-dashes guard.
- **Release sweep**: `python scripts/release_sweep.py`
  reports `release_sweep: clean`. The sweep checks README
  install pins, GitHub Action `uses:` pins, pre-commit `rev:`
  pins, and SAFETY_INVARIANTS.md presence.
- **Test count math**: the CHANGELOG-math gate
  (`tests/test_changelog_math_gate.py`) passes locally. The
  gate cross-checks the CHANGELOG `Test count: A -> B` line
  against `pytest --collect-only -q`.

## 1.5 Pre-push checklist (al-Hujurat T07 / F20 closure)

Before running the `git push origin vX.Y.Z` command that
triggers `release.yml`, walk through the following three
gates in order:

1. **Sandbox-version verification** (per
   `docs/sandbox-ci-parity.md`). Run the pre-push verification
   shell snippet from that document. If divergence reported,
   install the pinned tool version, then re-run `ruff check
   .` and `ruff format --check .` against the assembled
   patch series. Fold any formatting fixups into the
   originating commits via `git commit --fixup` +
   `git rebase --autosquash` rather than appending a
   separate "ruff format" commit.

2. **Test-count claim verification.** Run:
   ```bash
   pytest --collect-only -q | tail -1
   ```
   The output ("N tests collected") MUST match the count
   claimed in the CHANGELOG entry's `### Tests` section. If
   divergence, either correct the CHANGELOG before push, or
   document the divergence under a `### Projection drift`
   subsection (per the recalibrated CHANGELOG-math gate;
   v0.8.3 introduction with v0.11.7 al-Hujurat T04
   calibration).

3. **PR review verification.** Confirm the commit being
   tagged was reviewed via PR (per Section 0 above). If the
   audit-of-self pattern was used, confirm the audit
   checklist was walked. If a documented bypass is being
   used, confirm the CHANGELOG entry under construction
   names the bypass.

A bypass of any of these three gates MUST be documented in
the CHANGELOG entry under a "Process bypass" subsection per
Section 0.

## 2. Tag and push

Single command, tag-at-merge-commit (do NOT tag at a local-
only commit; the release.yml ancestry guard rejects tags
that are not ancestors of `origin/main`):

```bash
# After the release PR merges to main:
git fetch origin
git checkout main
git pull
# Confirm HEAD matches the merge commit you intend to tag.
git log --oneline -1

git tag -a "v${VERSION}" -m "v${VERSION}: <one-line tag annotation>"
git push origin "v${VERSION}"
```

`git push --follow-tags` triggers `.github/workflows/release.yml`
on the new tag. Watch the run via `gh run watch` or the
Actions UI.

## 3. Post-publish verification (manual gates)

After release.yml goes green, walk the four-link evidence
chain to confirm every public surface is consistent:

- **PyPI page renders**: open
  `https://pypi.org/project/furqan-lint/<VERSION>/`. Confirm
  the version number is present in the project's history
  panel and the description matches the README.
- **Fresh-venv install works**:
  ```bash
  python -m venv /tmp/furqan-lint-${VERSION}-verify
  /tmp/furqan-lint-${VERSION}-verify/bin/pip install \
      "furqan-lint==${VERSION}"
  /tmp/furqan-lint-${VERSION}-verify/bin/furqan-lint version
  ```
  The reported version string must match `${VERSION}` exactly.
- **GitHub Release object exists**:
  ```bash
  gh release view "v${VERSION}"
  ```
  must show the title `v${VERSION}` and notes derived from
  the CHANGELOG section. If T02 failed (e.g., the release
  workflow hit a transient `gh release create` error), run
  `python scripts/extract_changelog_section.py ${VERSION}`
  locally and re-run T02's command manually using the
  maintainer's `gh auth` context.
- **CHANGELOG / README cross-references resolve**: spot-check
  any `[X](#anchor)` links in the new CHANGELOG entry; spot-
  check that the README's Closure-history pointer resolves
  to CHANGELOG.md.

If any of the four gates fails, treat the release as
**partially shipped**: PyPI cannot be unpublished, but the
GitHub Release object can be re-created and the README /
CHANGELOG can be amended in a follow-up commit. Document the
failure mode in the v0.X.Y+1 patch release notes.

## 4. What the workflow handles automatically

The `.github/workflows/release.yml` workflow runs on every
`v*` tag push:

- **Build job**:
  - Build sdist + wheel via `python -m build`.
  - Verify exactly one `*-py3-none-any.whl` and one `.tar.gz`
    are produced.
  - Verify the tag commit is an ancestor of `origin/main`
    (defends against tag-pushed-at-local-only-commit drift).
  - Verify version-tag-CHANGELOG sync (the same check section
    1 covers locally).
  - Upload the artifacts.

- **Publish job**:
  - PyPI Trusted Publishing via
    `pypa/gh-action-pypi-publish@release/v1` (uses the
    `id-token: write` permission).
  - **T01 PyPI verification**: 12 polls at 10-second
    intervals (120 s window) of
    `pip index versions furqan-lint` until `${VERSION}` is
    visible. Failure mode: PyPI CDN propagation exceeded
    120 s; manual remediation is to re-run the workflow
    after a short pause.
  - **T02 GitHub Release creation**: extract the CHANGELOG
    section via `scripts/extract_changelog_section.py
    ${VERSION}`; create the Release object via
    `gh release create v${VERSION} --verify-tag`. Failure
    modes: empty CHANGELOG section (exit 1, surfaced in the
    workflow log) or `gh release create` rejecting because
    the tag does not exist yet (transient; usually resolves
    on workflow rerun).

## 5. What this checklist does not cover

Out of scope for v0.11.1:

- **Sigstore attestation of release tarballs**: planned for
  Phase G11.4 (Tasdiq al-Bayan) once the cross-substrate
  verification corpus stabilizes.
- **Multi-language CHANGELOGs** (separate Rust / Go / ONNX
  changelogs): planned post-Phase-G11.3 once all four
  substrates are shipped.
- **Release signing key rotation policy**: future; requires
  production deployment context not yet established.
- **Auto-generated release notes from CHANGELOG diff**:
  future; depends on T02's manual notes process running
  cleanly through at least three patch cycles to validate
  the CHANGELOG format is parseable.
- **SBOM in the distribution**: planned for Phase G11.4 or
  v1.5 horizon.

These items are tracked in the relevant phase's carry-forward
document (PHASE_G11_4_CARRY_FORWARD.md when authored, etc.).

## Appendix A: T03 backfill transcript

This appendix records the one-time `scripts/backfill_github_releases.py`
execution that closed finding F1 (12 historical versions tagged
on origin but absent from the GitHub Releases UI). The
maintainer ran the script from a local clone with their
`gh auth` context after the v0.11.1 release.yml landed.

The transcript template:

```
$ python scripts/backfill_github_releases.py
Backfilling 12 versions: ['0.11.0', '0.10.0', '0.9.4', ...]
v0.11.0: created
v0.10.0: created
v0.9.4: created
v0.9.3.1: created
v0.9.3: created
v0.9.2: created
v0.9.1: created
v0.9.0: created
v0.8.5: created
v0.8.4: created
v0.8.3: created
v0.8.2: created

Summary: 12 created, 0 already existed, 0 blocked.
```

If any version blocks (e.g., a tag was not pushed to origin
when a CI run created the bundle but the tag push was
rejected), record the version + reason here. Per the T03-
specific skip rule, partial backfill is acceptable; the
script continues with the next version.

The actual transcript from the v0.11.1 release window:

```
$ python scripts/backfill_github_releases.py
Backfilling 13 versions: ['0.11.1', '0.11.0', '0.10.0', '0.9.4', '0.9.3.1', '0.9.3', '0.9.2', '0.9.1', '0.9.0', '0.8.5', '0.8.4', '0.8.3', '0.8.2']
v0.11.1: already exists, skipping
v0.11.0: already exists, skipping
v0.10.0: already exists, skipping
v0.9.4: already exists, skipping
v0.9.3.1: already exists, skipping
v0.9.3: already exists, skipping
v0.9.2: already exists, skipping
v0.9.1: already exists, skipping
v0.9.0: already exists, skipping
v0.8.5: already exists, skipping
v0.8.4: already exists, skipping
v0.8.3: already exists, skipping
v0.8.2: already exists, skipping

Summary: 0 created, 13 already existed, 0 blocked.
```

Execution context: 2026-05-08 00:54 UTC (2026-05-07 19:54 CDT),
immediately after PR #21 merged at 00:50 UTC and the v0.11.1
release.yml rerun (run id 25527037199) completed successfully
at 00:53 UTC with all four phase-G10.5 critical steps green:

1. Build sdist + wheel
2. Verify tag is an ancestor of origin/main (the post-merge
   ancestry guard, now passing)
3. Verify PyPI publication (T01, first ever green; closes F7)
4. Create GitHub Release (T02, first ever green; closes F8
   forward)

Observations recorded for the Round 28 audit:

- The dry-run flag (`--dry-run`) on `backfill_github_releases.py`
  did not behave as a true dry-run on first invocation; the
  practical effect was that the dry-run pass and the real
  pass produced equivalent end states because the script's
  idempotency guard (`v<X>: already exists, skipping`) caught
  all 13 entries on the second pass. This is acceptable
  behavior empirically (no double-creation, no API-rate-limit
  spike) but the `--dry-run` flag's actual semantics should
  be confirmed against `scripts/backfill_github_releases.py`
  source before the next backfill cycle.
- v0.11.1 was included in the script's discovered version
  list and skipped via idempotency rather than excluded by
  the script's filter. This is harmless but adds a small
  amount of noise; a follow-up could pre-filter the
  most-recent-published version to keep the discovered
  set bounded to the historical-backfill scope.
- All 12 historical-backfill versions (v0.8.2 through v0.11.0)
  plus v0.11.1 plus the existing v0.1.0 are confirmed present
  on the GitHub Releases UI (14 total Release objects).

## Appendix B: Excluded versions

Per the structured table in the Phase G10.5 prompt T03, five
versions are excluded from the backfill scope:

| Version | Exclusion class                  | Reason                                                      |
|---------|----------------------------------|-------------------------------------------------------------|
| v0.2.0  | `_HISTORICAL_UNTAGGED_VERSIONS`  | tag was never pushed to origin                              |
| v0.7.0  | `_HISTORICAL_UNTAGGED_VERSIONS`  | tag was never pushed to origin                              |
| v0.7.3  | `_PRE_CHANGELOG_FORMAT_VERSIONS` | predates the `## [X.Y.Z]` CHANGELOG-section convention       |
| v0.8.0  | `_PRE_CHANGELOG_FORMAT_VERSIONS` | rolled into v0.8.1; no standalone CHANGELOG entry exists    |
| v0.8.1  | `_PRE_CHANGELOG_FORMAT_VERSIONS` | predates the `## [X.Y.Z]` convention; pre-Trusted-Publishing|

Pre-v0.8.2 entries in CHANGELOG.md (v0.3.x, v0.4.x, v0.5.x,
v0.6.x, v0.7.x except for the explicitly-excluded ones) are
also out of scope per the `_BACKFILL_FLOOR = (0, 8, 2)` bound:
they predate the release.yml + Trusted Publishing era and are
not eligible for retroactive Release-object backfill via this
tool.

If a future audit finds a Release object for one of these
five excluded versions has been hand-created on the upstream
repository, the corresponding allowlist constant in
`scripts/backfill_github_releases.py` should be updated and
the change recorded in CHANGELOG.md under the "Tooling"
section of the next patch release.

## Self-attestation discovery (Phase G12.0 al-Basirah, v1.0.0+)

From v1.0.0 onward, each furqan-lint release ships a signed
gate11 self-manifest as a GitHub Release asset, in addition to
the PyPI wheel and sdist. The release.yml T06 step generates
the self-manifest via ``python -m furqan_lint.gate11.self_manifest``,
signs it via Sigstore ambient OIDC, and uploads both
``self_manifest.json`` and ``self_manifest.bundle`` as Release
assets attached to ``v${VERSION}``.

### Convention-based URL

The published assets are discoverable from the version number
alone via convention-based URL:

  ``https://github.com/BayyinahEnterprise/furqan-lint/releases/download/v${VERSION}/self_manifest.json``
  ``https://github.com/BayyinahEnterprise/furqan-lint/releases/download/v${VERSION}/self_manifest.bundle``

The ``furqan-lint manifest verify-self`` subcommand (al-Basirah
T05) derives these URLs from the installed package version (via
``importlib.metadata.version("furqan-lint")``), downloads, and
verifies via the function-local ``_LANGUAGE_DISPATCH`` ->
``_verify_python`` path per al-Mursalat T04 + an-Naziat F-NA-3
substrate-actual.

### Operator runbook: post-tag verification

After a v1.x.0 release ships:

1. Wait for release.yml to complete all steps (PyPI Trusted
   Publishing + gh release create + T06 self-manifest sign +
   upload).
2. Verify the Release object has both assets attached:
   ```bash
   gh release view "v${VERSION}" --json assets --jq '.assets[].name'
   # Expected output (one per line):
   # self_manifest.bundle
   # self_manifest.json
   ```
3. Verify self-attestation succeeds against the published
   assets with the canonical signing identity:
   ```bash
   pip install --upgrade furqan-lint
   furqan-lint manifest verify-self      --expected-identity "https://github.com/BayyinahEnterprise/furqan-lint/.github/workflows/release.yml@refs/tags/v${VERSION}"      --expected-issuer "https://token.actions.githubusercontent.com"
   ```
4. If verify-self fails with CASM-V-072 sub-condition
   ``manifest-not-found``: re-run release.yml (idempotent on
   existing-version-on-PyPI; T06 retries with fresh OIDC token).
   If fails with sub-condition ``checker-set-hash-drift``:
   investigate pinned-source-list drift between release-time
   substrate and installed-substrate; this is a Naskh Discipline
   event requiring CHANGELOG entry. If fails with sub-condition
   ``signature-verification-unexpected``: investigate Sigstore
   bundle integrity per the upstream Sigstore project guidance.

### PyPI metadata fallback (deferred to v1.1+)

If convention-based URL fails (e.g., for a non-tagged release
that nonetheless has a self-manifest, or if GitHub Release
asset hosting moves), the PyPI project metadata's ``urls``
field can list the manifest URL explicitly. v1.0 ships with
convention-based URL only; PyPI metadata fallback is deferred
to v1.1+ if a real-world need surfaces.

End of release-checklist.md.
