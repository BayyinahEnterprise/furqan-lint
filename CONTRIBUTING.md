# Contributing to furqan-lint

Thanks for considering a contribution. furqan-lint is in its
infancy and runs on a tight-iteration audit-and-patch cadence;
this document captures the conventions that keep that cadence
working.

## How to file a finding

Findings are filed against substrate, not against people. Use the
round-N audit format:

- **Severity:** HIGH / MEDIUM / LOW / ADVISORY.
  - HIGH: ships broken or regresses a load-bearing invariant.
  - MEDIUM: would surface in an external review; substrate gap.
  - LOW: cosmetic, prose, or rare-edge.
  - ADVISORY: suggestion outside the patch surface; no fix
    required this round.
- **Reproducer:** minimal command sequence or test that surfaces
  the issue. Reproducers must run on the v0.8.x test suite (or
  a stated alternative) without external data.
- **Fix shape:** one to three sentences describing the change.
- **Suggested workflow addition (optional):** if the finding
  recurs, propose the gate that forecloses it. Gates are preferred
  over one-time fixes.

Open an issue using the template above, or submit a PR that
references the finding inline in the commit body.

## Commit-message conventions

- One finding per commit. Avoid bundling unrelated changes.
- Conventional-commits header: `feat(scope): ...`, `fix(scope):
  ...`, `docs(scope): ...`, `chore: ...`.
- Body grounds the change against a written prompt or audit
  finding. Reference round numbers, audit names, or prompt
  revisions where relevant.
- For CHANGELOG: use the placeholder + release-commit pattern.
  Early commits in a release land an empty section header with
  `<DATE>` / `<TBD>` placeholders so the CHANGELOG-math gate
  skips them; the final release commit populates the section
  and stamps the date.

## Co-author trailer requirement

Every commit ends with the cowork co-author trailer:

```
Co-authored-by: Claude (cowork) <claude+cowork@anthropic.com>
```

This records the audit-and-patch loop that produced the change.
Commits without the trailer will be flagged in review.

## Locally-running gates

Before opening a PR, run the full local test surface:

```bash
pip install -e ".[dev,rust,go]"
# Requires Go 1.22+ on PATH for the [go] extra to build goast.
python -m pytest -q
mypy
ruff check .
ruff format --check .
```

Em-dash check (mirrors the CI lint job):

```bash
LC_ALL=C.UTF-8 grep -rPn --exclude=CODE_OF_CONDUCT.md \
  '[\x{2013}\x{2014}]' src/ tests/ README.md CHANGELOG.md pyproject.toml \
  && echo "Em-dashes found" || echo "Em-dash check: clean"
```

CI runs the same gates across a 14-job matrix
(test-python-only / test-rust / test-go / test-full across
Python 3.10-3.13 plus a single full-extras job).

## Sigstore-CASM Gate 11 -- normative invariants

Before submitting a patch that touches `src/furqan_lint/gate11/`
or any Phase G11.x test fixtures, contributors MUST read
`SAFETY_INVARIANTS.md` at the repository root. That file is
normative: every Phase G11.x implementation must satisfy every
invariant declared there. A pre-commit hook verifies that
`SAFETY_INVARIANTS.md` is present in the repository when a
commit touches Gate 11 substrate; the hook guards presence
only, not semantic freshness, so reviewers carry the
responsibility of verifying that proposed Gate 11 changes do
not contradict the invariants in the absence of a paired
amendment to `SAFETY_INVARIANTS.md`.

## Sigstore-CASM Gate 11 testing

Gate 11 (v0.10.0+) tests live under `tests/test_gate11_*.py`
and require the `[gate11]` extra installed:

```bash
pip install -e ".[dev,gate11]"
python -m pytest -q tests/test_gate11_*.py
```

Tests that exercise the live Sigstore signing path (interactive
or ambient OIDC, network-bound) are gated behind the
`FURQAN_LINT_GATE11_SMOKE_TEST` environment variable so the
default `pytest -q` run never blocks on credentials or network:

```bash
FURQAN_LINT_GATE11_SMOKE_TEST=1 python -m pytest -q tests/test_gate11_signing.py
```

CI runs the full `pytest -q` suite without the smoke flag on
every push, and runs the smoke-test job separately on
push-to-main with `id-token: write` so the ambient GitHub
Actions OIDC identity is available.

When adding a new diagnostic family that should be covered by
Gate 11, update the `_extract_public_names` /
`signature_canonicalization` test surface in lockstep with the
new public symbol; the canonical-fingerprint regression tests
will fail otherwise.

## The four-place pattern for documented limits

Every documented limit in the Rust or Go adapter lives in four
places:

1. A fixture file in `tests/fixtures/<lang>/documented_limits/`
   that exercises the limit shape.
2. A README entry under
   `tests/fixtures/<lang>/documented_limits/README.md` describing
   what the limit is and why it is documented rather than fixed.
3. A CHANGELOG entry on the release that shipped or moved the
   limit.
4. A pinning test in
   `tests/test_<lang>_documented_limits.py` (or the per-language
   correctness file) that exercises the fixture.

The four-place-completeness gate
(`tests/test_four_place_completeness_gate.py`) checks that the
four pieces stay in sync. Any new documented limit must arrive
with all four pieces in the same commit (or in commits that land
together in the same release).

## Reciprocal contract

Every release closes prior-round findings; every release names
new "Out of scope" items honestly; every release answers the
five questions (what was added, what was fixed, what was retired,
what was deferred, what's the post-merge checklist) in the
CHANGELOG. Structural prevention via gates is preferred over
one-time fixes, and gates self-test against fixtures of the
shape they catch. The framework's discipline-lineage is preserved
across releases: each round's substrate findings inform the next
round's gate authorisations, and locked decisions from one
release carry forward unless a later release explicitly rescinds
them. Findings are filed against substrate (the artifact being
audited), not against people; fixes are scoped per-finding.

The reciprocal aspect: contributors trust the maintainer to apply
audits honestly and to credit findings in commit bodies; the
maintainer trusts contributors to file findings in the round-N
format above without padding severity or attaching personal
narrative. When the framework gets a public DOI in a future
release, this section will link out to the canonical reference;
until then, the inline text above is load-bearing.

## Project lead

Bilal Syed Arfeen is the project lead. furqan-lint is a Bayyinah
Enterprise project in its infancy; expect tight cadence and
direct review.
