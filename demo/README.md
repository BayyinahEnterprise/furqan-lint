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
D24 all_paths_return) on a single file. On `api_v2.py`:

```
$ furqan-lint check demo/api_v2.py
PASS  demo/api_v2.py
  3 structural checks ran. Zero diagnostics.
```

`api_v1.py` fires a D11 advisory because `process_intake`
narrows the Optional from `validate_document` via an
`if result is None` guard - branch-level exhaustiveness
checking is registered as D26 Phase 3+. This is documented
behaviour, not a regression.
