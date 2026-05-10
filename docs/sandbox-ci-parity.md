# Sandbox-CI parity discipline

The CI matrix pins specific tool versions (ruff, mypy, pytest,
etc.) via `pyproject.toml`'s `[dev]` extra. The local sandbox
environment may have different versions installed; the
divergence produces fixup commits between local-clean and
CI-clean states.

## Pre-push verification

Before pushing a tag that triggers `release.yml`, run:

```bash
# Verify sandbox ruff matches CI-pinned ruff
PINNED_RUFF=$(python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    cfg = tomllib.load(f)
deps = cfg['project']['optional-dependencies']['dev']
for d in deps:
    if d.startswith('ruff'):
        print(d.split('==')[1])
        break
")
INSTALLED_RUFF=$(ruff --version | awk '{print $2}')
test "$PINNED_RUFF" = "$INSTALLED_RUFF" || \
  echo "DIVERGENCE: pinned=$PINNED_RUFF installed=$INSTALLED_RUFF"
```

If divergence is reported, install the pinned version:

```bash
pip install "ruff==$PINNED_RUFF"
```

Then re-run `ruff check .` and `ruff format --check .`
against the assembled patch series.

## Why this matters

Round 29 audit's F20 closure documents the empirical case:
during the v0.11.1 G10.5 al-Mubin ship, the sandbox's ruff
version (0.8.0) was newer than the CI-pinned version (0.6.9);
local `ruff check .` was clean, CI's `ruff check .` failed on
formatting differences introduced by the newer version. The
fixup commit had to be appended to the patch series and
folded via `--autosquash`.

The discipline below prevents the divergence at push time
rather than catching it at CI time.

## Enforcement profile (added in v0.11.7 per Round 30 audit F6 absorption)

This discipline ships at **convention status**, not enforced
status. Unlike the PR-review gate (al-Hujurat T01 + T02),
which is mechanically enforced via GitHub branch protection
rules, the sandbox-CI parity check exists only as
documentation and a pre-push checklist item. There is no
mechanical enforcement of local-environment state.

The asymmetry is defensible: PR review operates on a remote
main branch where GitHub can enforce a rule; sandbox-CI
parity operates on a local-developer environment where the
project has no observability or control. Mechanical
enforcement of local-environment state would require either
a pre-commit hook (which the developer can disable) or a
remote check that re-runs CI on the developer's exact local
state (which is impractical without per-developer build
infrastructure).

The discipline is therefore at **candidate-discipline
status**: convention with audit-of-self verification at
pre-push checklist time. Promotion to enforced status is a
v1.x candidate closure if either (a) a pre-commit hook is
added that runs the parity check and fails on divergence
(developer-disable risk acknowledged), or (b) remote CI is
extended to verify the developer's reported local-version
state against pinned versions.

This convention-vs-enforcement asymmetry is named explicitly
because the failure mode (silent local-CI divergence) is
the same shape as the PR-review pre-mechanical failure
mode (silent direct-to-main commits). The difference is
substrate: PR review can be mechanically enforced; sandbox
parity cannot, in the current operational scope.
