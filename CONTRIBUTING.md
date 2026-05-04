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
