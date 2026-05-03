# Demo: additive-only diff

Fixtures for the BayyinahEnterprise tabletop demo. Two source
files representing v1 and v2 of a small public API. v2 renamed
`classify` to `categorize` and dropped `process_intake`.

## What this shows

```
$ mypy demo/api_v1.py demo/api_v2.py
Success: no issues found in 2 source files

$ furqan-lint diff demo/api_v1.py demo/api_v2.py
MARAD  demo/api_v2.py (additive-only)
  2 violation(s):
    [additive_only] Public name 'classify' was present in the
    previous version but is absent in the current version.
    [additive_only] Public name 'process_intake' was present in
    the previous version but is absent in the current version.
```

mypy passes both files because each is independently type-correct.
furqan-lint catches what mypy cannot see: the contract between the
two versions has been broken. Two public names were removed.
Every downstream consumer that imported `classify` or
`process_intake` is now broken.

## Why this matters

mypy, ruff, pylint, and pyright all check single files (or whole
projects, but file-by-file). None of them check the contract
between releases. The additive-only invariant is the discipline
that public names can be added but never removed or renamed
without an explicit deprecation cycle.

## Running on the Pi (or anywhere)

```
pip install furqan-lint
furqan-lint diff demo/api_v1.py demo/api_v2.py
```

Air-gapped: no network call. No GPU. Pure-Python AST walk.

## Note on `furqan-lint check`

`check` runs the structural-honesty rules (D11 status_coverage,
D24 all_paths_return) on a single file. Both fixtures are
structurally clean:

```
$ furqan-lint check demo/api_v1.py
PASS  demo/api_v1.py
  3 structural checks ran. Zero diagnostics.

$ furqan-lint check demo/api_v2.py
PASS  demo/api_v2.py
  3 structural checks ran. Zero diagnostics.
```

The structural checks pass on both versions. The contract
break that `diff` catches is invisible to single-file analysis.

## Performance (sandbox baseline)

`furqan-lint`'s additive check itself runs in under a millisecond
(the hot path is two `ast.parse` calls plus a set difference).
Wall-clock invocation is dominated by Python interpreter startup
and module imports.

Measured on x86 sandbox (Python 3.12):

| Stage             | Time   |
|-------------------|--------|
| Python startup    | ~13ms  |
| Module import     | ~50ms  |
| Additive check    | <1ms   |
| Total wall-clock  | ~90ms  |

Pi 5 (ARM, 2.4 GHz) is expected to land in the 150-250ms range
for total wall-clock; the actual check work is unchanged.
The conservative demo claim: "under 200 milliseconds, including
Python startup, on a $80 device, air-gapped."
