# furqan-lint

[![CI](https://github.com/BayyinahEnterprise/furqan-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/BayyinahEnterprise/furqan-lint/actions/workflows/ci.yml)

Structural-honesty checks for Python, powered by [Furqan](https://tryfurqan.com).

`furqan-lint` translates Python source into the Furqan AST and runs the
subset of Furqan checkers whose semantics carry across language boundaries
into idiomatic Python. <!-- FURQAN_LINT_CHECKS_AUTO_BEGIN -->
Four core Python checks ship today:

- **D24 (all-paths-return)** every control-flow path through a typed function reaches a return statement.
- **D11 (status-coverage)** when a function returns ``Optional[X]``, every caller either propagates the optionality or explicitly handles ``None``. A caller that silently collapses ``Optional[X]`` into a non-optional return type is the structural equivalent of dropping the ``Incomplete`` arm of Furqan's ``Integrity | Incomplete`` union.
- **return_none_mismatch** a function declaring ``-> str`` (or any non-Optional type) that returns ``None`` on some path is flagged as a type mismatch. Closes the D24 return-None blind spot.
- **additive_only** invoked via ``furqan-lint diff old.py new.py``, compares two versions of a module's public surface and fires on any removed name. Adding a public name is silent.

Adapter-specific checks ship under the optional extras documented below: ``[rust]`` adds R3 + D24 + D11; ``[go]`` adds D24 + D11; ``[onnx]`` adds D24-onnx + opset_compliance + D11-onnx; ``[onnx-runtime]`` adds numpy_divergence; ``[onnx-profile]`` adds score_validity ADVISORY; ``[gate11]`` adds the Sigstore-CASM Gate 11 verifier (v0.10.0+; an additive-only contract on the public surface, cryptographically witnessed via Sigstore Rekor).
<!-- FURQAN_LINT_CHECKS_AUTO_END -->

## Install

```bash
pip install furqan-lint
```

This installs the latest release from PyPI. Requires Python 3.10+ and `furqan>=0.11.0`.

### Optional adapters

```bash
pip install "furqan-lint[rust]"                  # tree-sitter Rust adapter
pip install "furqan-lint[go]"                    # Go adapter (requires Go 1.22+ toolchain at install time)
pip install "furqan-lint[onnx]"                  # ONNX graph-only checks (D24-onnx + opset-compliance + D11-onnx shape/type)
pip install "furqan-lint[onnx-runtime]"          # ONNX + numpy-vs-ONNX divergence (v0.9.3+; brings in onnxruntime + numpy)
pip install "furqan-lint[onnx-profile]"          # ONNX + score-validity ADVISORY (v0.9.4+; brings in onnx_tool)
pip install "furqan-lint[gate11]"                # Sigstore-CASM Gate 11 (v0.10.0+; brings in sigstore + rfc8785)
pip install "furqan-lint[gate11-rust]"           # Sigstore-CASM Gate 11 Rust extension (v0.11.0+; brings in sigstore + rfc8785 + tree-sitter-rust)
pip install "furqan-lint[rust,go,onnx-runtime,onnx-profile,gate11]"  # all adapters with full ONNX checks plus Gate 11
```

### Install from a specific commit or tag

```bash
pip install "git+https://github.com/BayyinahEnterprise/furqan-lint.git@v1.0.0"
```

Replace `v1.0.0` with any tag from the [release history](https://github.com/BayyinahEnterprise/furqan-lint/releases) or `main` for the development tip.

### Furqan dependency

furqan-lint requires `furqan>=0.11.0`, the Furqan programming-language tooling. As of 2026-05-03 the PyPI release of `furqan` is at v0.10.1; install v0.11.7 directly from GitHub:

```bash
pip install "git+https://github.com/BayyinahEnterprise/furqan-programming-language.git@v0.11.7"
```

This GitHub-pin step will not be necessary once `furqan` v0.11.7 is published to PyPI.

### Rust support (opt-in)

As of v0.7.0, furqan-lint can lint `.rs` files. Rust support is
behind an opt-in extra so the Python-only install path is unchanged:

```bash
pip install "furqan-lint[rust]"
```

This pulls in `tree-sitter` and `tree-sitter-rust` (PyPI ships
ARM64 and x86_64 wheels for both; no source build required).

As of v0.7.2, `.rs` files run three checkers: R3 (ring-close,
zero-return on annotated functions, via upstream
`furqan.checker.check_ring_close`), D24 (all-paths-return), and
D11 (status-coverage). The D11 producer predicate recognises
both `Option<T>` and `Result<T, E>` returns; a caller that calls
a may-fail helper without propagating the union is flagged.

The planned analogue of `return_none_mismatch` was dropped per
the v0.7.2 prompt-grounding self-check, which empirically
demonstrated that the firing condition is unreachable on any
compilable Rust source (`rustc` rejects `fn f() -> i32 { None }`
at compile time before furqan-lint sees the file). Trait objects,
lifetimes, macro expansion, closure return-type checks, and
Cargo workspace traversal remain out of scope.

Edition is read from the nearest ancestor `Cargo.toml`'s
`[package].edition` field (one of "2018", "2021", "2024"); if
no Cargo.toml is found or the field is malformed, edition
defaults to "2021". The current implementation does not branch on edition.


### Go support (opt-in)

As of v0.8.1, furqan-lint can lint `.go` files (Go diff in v0.8.1; goast emits qualified method names as of v0.8.2). Go support is
behind an opt-in extra so the Python-only install path is unchanged:

```bash
pip install "furqan-lint[go]"
```

The Go toolchain (1.21+) is required at install time so the
PEP 517 build hook can compile the bundled `goast` binary; it
is not required at runtime.

As of v0.8.1, `.go` files run two checkers: D24 (all-paths-
return) and D11 (status-coverage with the `(T, error)` firing
shape). The cross-language `_is_may_fail_producer` predicate
(Shape B) recognizes the `(T, error)` return convention; a
caller that calls a may-fail helper without propagating the
union is flagged. R3 (zero-return) is documented not-applicable
to Go: the Go compiler rejects all firing shapes at compile
time.

Additive-only diff is supported for `.go` files: `furqan-lint
diff old.go new.go` extracts uppercase-initial public names
from each file via `goast` and reports any names that were
present in `old` but not in `new`. The diagnostic prose is
language-aware: Go users see `var Name = <new>` re-export hints
rather than Python alias syntax. Cross-language diffs (e.g.
`foo.py` vs `bar.go`) return exit 2 with a "Cross-language
diff not supported" message.

### ONNX support (opt-in)

As of v0.9.0, furqan-lint can lint `.onnx` model files. ONNX
support is behind an opt-in extra so the Python-only install
path is unchanged:

```bash
pip install "furqan-lint[onnx]"
```

This pulls in `onnx>=1.14,<1.19`. The upper bound is load-bearing:
the ONNX op registry retroactively adds operators across `onnx`
package releases, so an unpinned upper bound would silently
change what counts as e.g. opset 11. No `onnxruntime` dependency:
lint-time checks operate on the graph structure, not on inference.

`.onnx` files run three structural checks (current as of v0.9.1):

- **D24-onnx (all-paths-emit).** Every declared output in
  `graph.output` must be reachable from some node in the graph
  (or be a graph input passed through). The structural shape
  mirrors a function with a missing return statement.
- **opset-compliance.** Every node's `op_type` must exist in the
  declared opset, looked up via `onnx.defs.get_schema(...,
  max_inclusive_version=opset_version)` against the pinned
  `onnx>=1.14,<1.19` registry.
- **D11-onnx (shape-coverage, v0.9.1).** Run
  `onnx.shape_inference.infer_shapes(model_proto, strict_mode=True)`;
  if it raises `InferenceError`, parse the per-op message and
  emit one `shape_coverage` diagnostic per offender. Strict-mode
  silent-passes on `dim_param` (symbolic) and empty `dim_value`
  (dynamic) shapes; this is documented as the
  `dynamic_shape_silent_pass` four-place limit.

ONNX is structurally a different substrate from Python / Rust /
Go source code. Nodes are not functions; edges are not return
statements; ValueInfo is not a type signature. The ONNX adapter
ships a *parallel diagnostic family* inspired by the Furqan
structural-honesty primitives, not new instances of the existing
`check_d24` / `check_status_coverage` checkers operating on a
unified IR. The diagnostic spirit is shared (surface claims must
match substrate dataflow); the implementation is its own
package with its own runner.

The additive-only diff covers `graph.input` and `graph.output`
ValueInfo entries only. `graph.value_info` (intermediate tensors)
and `graph.initializer` (parameter tensors) are explicitly out
of scope; including them would create false positives on every
model retraining.


### ONNX numpy_reference convention for NeuroGolf-shape models

The v0.9.3 numpy-vs-ONNX divergence checker discovers a
``numpy_reference`` callable from a sibling ``_build.py`` per
the NeuroGolf-specific four-place documented limit
``numpy_divergence_neurogolf_convention``. The convention
assumes ARC-AGI grids encoded as ``(1, 10, H, W)`` one-hot
tensors (10 channels, one per cell color).

Two canonical patterns satisfy the convention. Both produce
zero divergence findings on a well-formed model; pick the one
that matches your build pipeline. Worked examples live at
``tests/fixtures/onnx/numpy_reference_examples/``.

**Pattern A: pre-one-hot input.** The build pipeline encodes
the raw ARC-AGI grid into ``(1, 10, H, W)`` before invoking
both the ONNX model and the ``numpy_reference``. The reference
function accepts the already-encoded tensor:

```python
def numpy_reference(grid):
    import numpy as np
    # grid is already (1, 10, H, W) one-hot.
    return np.array(grid, dtype=np.float32)
```

The companion ``.json`` task file stores probe grids in the
encoded ``(1, 10, H, W)`` shape under ``train[i]["input"]``.

**Pattern B: raw grid + local encoding.** The build pipeline
keeps the ARC-AGI grid as a raw rank-2 integer grid; the
``numpy_reference`` encodes it locally to match the ONNX
model's expected ``(1, 10, H, W)`` input shape:

```python
def numpy_reference(grid):
    import numpy as np
    arr = np.array(grid, dtype=np.int64)
    h, w = arr.shape
    one_hot = np.zeros((1, 10, h, w), dtype=np.float32)
    for c in range(10):
        one_hot[0, c, :, :] = (arr == c).astype(np.float32)
    return one_hot
```

The companion ``.json`` task file stores probe grids in the
raw rank-2 form (the standard ARC-AGI format).

Both patterns are validated by tests under
``tests/test_onnx_neurogolf_adapter_examples.py``; future
``onnx`` / ``onnxruntime`` / ``numpy`` version changes that
break the convention surface as test failures rather than
stale documentation.

### Sigstore-CASM Gate 11 -- normative invariants

Phase G11.A (al-Fatiha) ships `SAFETY_INVARIANTS.md` at the
repository root as the foundational invariants document for the
Sigstore-CASM Gate 11 substrate. The file is normative for all
subsequent Phase G11.x implementations and contains the seven
canonical cryptographic and protocol invariants, the four
mandatory disclosures inherited from the Sigstore threat model,
and the foundation-status disclosure (Section 8) for the
empirical foundation of Strategy 1 (Canonical-First
Architecture).

The empirical foundation behind Strategy 1 is currently at
candidate-finding status pending independent replication; the
seven canonical invariants are NOT magnitude or prevention
claims but cryptographic and protocol specifications. Full
treatment of the strategy mappings lives in `Bayyinah
at-Tartib v1.0` (second revision May 7 2026); empirical
methodology lives in `Bayyinah al-Munasabat v1.0` (second
revision May 7 2026).

Contributors and reviewers preparing Phase G11.0 through Phase
G11.12 patches MUST read `SAFETY_INVARIANTS.md` before
submitting changes that touch `src/furqan_lint/gate11/` or any
Phase G11.x test fixtures.
### Sigstore-CASM Gate 11 (opt-in)

As of v0.10.0, furqan-lint can sign and verify a
**Compositional Additive-only Surface Manifest (CASM)** for any
Python module via Sigstore-keyed transparency. Gate 11 (Kiraman
Katibin, "the noble scribes" who keep an unforgeable record of
additive-only public surface) is behind an opt-in extra so the
default install path is unchanged:

```bash
pip install "furqan-lint[gate11]"
```

This pulls in `sigstore>=3.0.0,<4` and `rfc8785>=0.1.4,<0.2`.
The `[gate11]` extra is independent of `[onnx]` /
`[onnx-runtime]` / `[onnx-profile]`; it adds no inference
dependencies.

The CLI grows two opt-in entry points and one flag:

```bash
furqan-lint manifest init <module.py>     # OIDC sign; emit .furqan.manifest.sigstore
furqan-lint manifest verify <module.py>   # 9-step CASM-V verification
furqan-lint manifest verify-self          # v1.0+ verify furqan-lint's own gate11 self-manifest
furqan-lint manifest update <module.py>   # additive-only re-sign; refuses removals
furqan-lint check --gate11 <path>         # run normal checks + verify any CASM bundles found
```

#### Self-attestation (v1.0+; Phase G12.0 al-Basirah)

From v1.0 onward, furqan-lint signs its own releases with
gate11. The structural-honesty thesis closes on itself: the
tool that catches drift in others' code attests its own.
Relying Parties verify via:

```bash
furqan-lint manifest verify-self \
  --expected-identity "<pattern>" \
  --expected-issuer "https://token.actions.githubusercontent.com"
```

Signed self-manifests publish as GitHub Release assets at
`https://github.com/BayyinahEnterprise/furqan-lint/releases/download/v${VERSION}/self_manifest.json`
(+ corresponding `.bundle`). The `verify-self` subcommand
derives the URL from the installed package version and
dispatches verification through the function-local
`_LANGUAGE_DISPATCH` -> `_verify_python` path per
al-Mursalat T04 + an-Naziat F-NA-3 substrate-actual.

CASM-V-072 (self-attestation-failure) surfaces on three
sub-conditions: (a) manifest-not-found; (b) checker-set-
hash-drift; (c) signature-verification-unexpected. See
`docs/gate11-self-attestation.md` for the full trust-model
and remediation guidance.

`furqan-lint check` without `--gate11` produces the same
diagnostics as in v0.9.4. Gate 11 only activates when the user
opts in via the flag or the `manifest` subcommand.

**Wire format.** Each manifest is a JSON document carrying
`casm_version: "1.0"`, `language` (one of ``"python"`` (Phase
G11.0, v0.10.0), ``"rust"`` (Phase G11.1, v0.11.0), ``"go"``
(Phase G11.2, v0.12.0), ``"onnx"`` (Phase G11.3, v0.13.0) --
the canonical mushaf chain),
`module_root_hash` (BOM-stripped, LF-normalized, UTF-8 SHA-256),
`public_surface.names` (ASCII-sorted entries of kind
`function` / `class` / `constant`, each with a canonical
`signature_fingerprint`), `tooling.linter_version`,
`tooling.checker_set_hash`, and `chain_pointer.previous_bundle_hash`
for chain integrity. The whole document is canonicalized via
RFC 8785 (JSON Canonical Form) before being signed. Bundles
ship as `<module>.furqan.manifest.sigstore`.

**Verification.** `manifest verify` runs the 9-step flow
documented under the `CASM-V-NNN` error namespace:

1. Parse bundle (CASM-V-010 on JSON failure).
2. Check `casm_version == "1.0"` (CASM-V-001).
3. Check `language` is in the supported substrate set
   ``{python (Phase G11.0, v0.10.0), rust (Phase G11.1,
   v0.11.0), go (Phase G11.2, v0.12.0), onnx (Phase G11.3,
   v0.13.0)}`` (CASM-V-001) -- the complete mushaf chain.
4. Load Sigstore trust root via TUF (CASM-V-020 ADVISORY on
   refresh failure with cache fallback; CASM-V-021 if no cache).
5. Re-canonicalize the manifest (RFC 8785).
6. Verify Sigstore signature against the canonical bytes
   (CASM-V-030..034 by failure mode).
7. Compare `module_root_hash` to the on-disk module
   (CASM-V-040 on mismatch).
8. Compare `public_surface.names` to the live extraction; if
   the live module uses dynamic `__all__`, the result is
   indeterminate (CASM-V-INDETERMINATE) rather than a false
   pass. For ``language=onnx`` manifests (v0.13.0+), this
   step additionally enforces opset-policy consistency
   (CASM-V-070 on `opset_imports` mismatch) and dim_param
   consistency (CASM-V-071 on symbolic-vs-concrete drift),
   per the graph-shape canonicalization rules 9-12 in
   `gate11/onnx_signature_canonicalization.py`.
9. Check `chain_pointer` integrity against the previous bundle
   when supplied (CASM-V-060 on hard mismatch; CASM-V-061
   ADVISORY when no previous bundle is locally accessible).

`manifest update` enforces the additive-only contract: any name
removal between previous and proposed manifest is rejected
(CASM-V-050); any signature change on a retained name is
rejected (CASM-V-051). Additions are accepted and re-signed.

#### Gate 11 scope and disclosures

Gate 11 inherits the Sigstore threat model documented in Newman
et al., *Sigstore: Software Signing for Everybody* (ACM CCS
2022). The four residual disclosures are recorded here in the
Shape A documented-limit form so downstream Relying Parties can
calibrate trust.

- **(N1) Short-window OIDC-identity compromise.** A signature
  binds to the OIDC identity that requested the Fulcio
  certificate. If the signing identity's OIDC token is
  compromised within the certificate validity window
  (typically 10 minutes), an attacker can produce a CASM bundle
  that verifies cleanly. Mitigation lives outside furqan-lint
  (hardware-backed OIDC, short-lived tokens, identity-provider
  audit logging). Severity: HIGH but out-of-scope for the lint
  itself; documented per Newman 2022 section 6.
- **(N2) Typosquatting at the publish boundary.** Sigstore
  proves "an entity controlling identity X signed bytes Y at
  time T". It does *not* prove that identity X is the legitimate
  maintainer of the package the consumer thinks they are
  installing. Relying Parties must pin both the package name
  *and* the expected signing identity; furqan-lint surfaces the
  identity in the verification result so a CI policy can assert
  it.
- **(N3) Rekor entry queryability and privacy.** Rekor is a
  public append-only log. Manifest entries (including the
  module-root hash and the public-surface name list) are
  published unencrypted and become enumerable by third parties.
  Codebases that are themselves confidential or under embargo
  should not sign their CASM bundles to the public Rekor
  instance; the staging instance or a private transparency
  service is the right substrate. This is recorded as Shape A
  scope statement F7 below.
- **(N4) Log-retention horizon.** Rekor's public-instance
  retention policy is operational, not contractual. Verification
  past a multi-year horizon may require local mirroring of the
  relevant log entries. furqan-lint does not mirror Rekor on the
  user's behalf.

#### SCITT vocabulary

Gate 11 uses the IETF SCITT (Supply Chain Integrity,
Transparency, and Trust) architectural vocabulary throughout the
verification module and CHANGELOG entries: the **Issuer** is the
OIDC-identified signer; the **Transparency Service** is Rekor;
the **Relying Party** is the consumer running `manifest verify`
(or `check --gate11`); the **Auditor** is any third party who
replays the chain integrity check. The mapping is documented
inline in `src/furqan_lint/gate11/verification.py`.

#### Shape A scope statements

Two limits are documented as Shape A (acknowledged residual,
not patched in v0.10.0) rather than as defects:

- **F4. Linter-substrate trust is recursive.** The
  `tooling.checker_set_hash` field records the integrity of the
  checker code that produced the manifest. It does *not* prove
  that the checker code itself is honest; verifying that
  requires either signing furqan-lint's own release artifacts
  with Gate 11 (G11.5 carry-forward) or an independent
  reproducible build. v0.10.0 ships the field; closing the
  recursion is a later round.
- **F7. Rekor entries leak public-surface shape.** Per N3 above,
  the Rekor log publishes the manifest's hash and the public
  name list. A confidential codebase MUST NOT sign its CASM
  bundles to the public Rekor instance. v0.10.0 documents the
  failure mode; private-transparency-service routing is a later
  round.

The prompt asked these to surface as findings; v0.10.0 records
them as Shape A scope statements (acknowledged in design,
deferred by scope) rather than as defects (signaled to be fixed
this round) because the underlying substrate is the Sigstore
public infrastructure, not furqan-lint code.

### Sigstore-CASM Gate 11 (Rust extension)

As of v0.11.0, Phase G11.1 (as-Saffat) extends Sigstore-CASM
Gate 11 to Rust source files. Bundles are produced via the
existing Python sigstore-python pipeline; FFI to sigstore-rs
is deferred to v1.5 per Yusuf Horizon discipline.

```bash
pip install "furqan-lint[gate11-rust]"
```

The CLI surface dispatches on file extension:

```bash
furqan-lint manifest init src/lib.rs           # OIDC sign; emit src/lib.rs.furqan.manifest.sigstore
furqan-lint manifest verify src/lib.rs.furqan.manifest.sigstore \
    --expected-identity '<pattern>' \
    --expected-issuer 'https://token.actions.githubusercontent.com'
furqan-lint manifest update src/lib.rs         # additive-only re-sign; refuses removals
furqan-lint check --gate11 src/                # walk .rs files; verify any adjacent bundle
```

The Rust manifest declares ``module_identity.language = "rust"``
and ``public_surface.extraction_method =
"tree-sitter.rust-public-surface@v1.0"``. Public-surface
entries are emitted for top-level ``pub fn``, ``pub struct``,
``pub enum``, ``pub trait``, ``pub type``, ``pub const``,
``pub static``, and ``pub use`` re-exports.

#### Identity policy enforcement (audit C-1 + M-6 corrective)

v0.11.0 closes the Phase G11.0 v0.10.0 audit gap where
``furqan-lint manifest verify`` accepted any valid Sigstore
signature regardless of OIDC identity. The verifier now
requires an explicit Identity policy:

- ``--expected-identity <pattern>``: required for production
  verification. The pattern is matched against the signing
  certificate's Subject Alternative Name (SAN) extension via
  sigstore-python's ``Identity`` policy class.
- ``--expected-issuer <issuer>``: optional OIDC issuer
  constraint (e.g.,
  ``https://accounts.google.com``,
  ``https://token.actions.githubusercontent.com``).
- ``--allow-any-identity``: explicit opt-in to ``UnsafeNoOp()``
  policy. Use of this flag in production CI is itself an
  audit signal (Sulayman-Naml ADVISORY pattern); the
  refuse-without-policy default is the substrate-side
  enforcement of Newman 2022 N2 (typosquatting at the publish
  boundary).

Failure modes:

- ``CASM-V-035`` (no Identity policy supplied): default
  refuse-without-policy. Pass ``--expected-identity <pattern>``
  or explicitly ``--allow-any-identity``.
- ``CASM-V-032`` (identity policy mismatch): the signing
  certificate's SAN does not match the supplied pattern.
- ``CASM-V-036`` (identity extraction failure): the signing
  certificate is malformed or lacks the SAN extension. Replaces
  the v0.10.0 string sentinel ``"<unknown OIDC identity>"``.

These error codes plus the v0.10.0 codes (CASM-V-001 through
CASM-V-061) form the universal CASM-V namespace declared in
SAFETY_INVARIANTS.md Invariant 6. Phase G11.4 (Tasdiq al-Bayan)
will exercise all codes against bundles produced from at least
the Python and Rust substrates.

#### Documented limits (v1.0 scope, deferred to v1.5)

- **Method-level signing**: impl-block methods are not part of
  the v1.0 public-surface fingerprint (consistent with the
  existing ``furqan_lint.rust_adapter.extract_public_names``
  documented limit).
- **Lifetime-aware canonical types**: lifetimes are stripped
  during fingerprinting so that ``f<'a>(s: &'a str)`` and
  ``f<'b>(s: &'b str)`` produce identical fingerprints.
- **Trait-object semantic equivalence**: ``Box<dyn Trait + 'a>``
  is fingerprinted as ``Box<dyn Trait>`` (lifetime stripped;
  bounds beyond first identifier elided).
- **Macro-expansion-aware signing**: macro calls are signed at
  the source level, NOT after expansion.
- **Glob re-exports**: ``pub use foo::*`` cannot be statically
  resolved; the verifier surfaces ``CASM-V-INDETERMINATE``
  rather than a false pass per Phase G11.A Invariant 6 step 8.

These are documented limits in the Sigstore-CASM substrate;
improvement is a v1.5 horizon item tracked in
``PHASE_G11_1_CARRY_FORWARD.md``.

## Usage

```bash
furqan-lint check path/to/file.py
furqan-lint check path/to/directory/
furqan-lint diff old_version.py new_version.py
furqan-lint version
```

## CI Integration

Two ways to wire furqan-lint into your workflow.

### GitHub Action

Three lines in your workflow file run the structural checks on every
push or pull request:

```yaml
# .github/workflows/furqan-lint.yml
name: Furqan Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: BayyinahEnterprise/furqan-lint@v1.0.0
        with:
          path: src/
```

Inputs (all optional):
- `path` -- file or directory to check. Default: `.`
- `python-version` -- Python version to use. Default: `3.12`
- `furqan-lint-version` -- pinned version to install. Default: install
  latest from `main`.

### Pre-Commit Hook

Run the same checks locally on every `git commit` against staged
Python files:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/BayyinahEnterprise/furqan-lint
    rev: v1.0.0
    hooks:
      - id: furqan-lint
```

Then `pre-commit install`. Failures block the commit.

## Using with Other Tools

furqan-lint is complementary to ruff and mypy. Each catches a
different class of issue:

| Tool | Catches | Overlap with furqan-lint |
|------|---------|--------------------------|
| **ruff** | Style, unused imports, complexity, common bug patterns, formatting (replaces black + isort + flake8 + pyupgrade) | None |
| **mypy** | Type errors, some missing returns | Partial overlap on D24 and return-none. mypy does NOT catch Optional collapse (D11) or API-breaking changes (additive-only). |
| **furqan-lint** | Missing return paths, Optional collapse, return-None mismatch, API-breaking changes, zero-return functions | See mypy column |

### Recommended `.pre-commit-config.yaml` for Your Project

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy

  - repo: https://github.com/BayyinahEnterprise/furqan-lint
    rev: v1.0.0
    hooks:
      - id: furqan-lint
```

Then `pre-commit install`. Run order: ruff (lint + format) -> mypy
(types) -> furqan-lint (structural honesty). Each layer catches what
the previous layers do not.

### Contributing to furqan-lint

```bash
git clone https://github.com/BayyinahEnterprise/furqan-lint.git
cd furqan-lint
pip install -e ".[dev]"
pre-commit install

# Run all tools manually
ruff check .
ruff format --check .
mypy
pytest -q

# Run by test category
pytest -m unit         # fast, in-process, no subprocess
pytest -m integration  # CLI and pipeline tests
pytest -m "not slow"   # skip slow tests
pytest -m "not network" # skip network-dependent tests
```

The `furqan-lint check src/` self-check runs as part of pre-commit;
the tool that catches drift in other people's code must not have
drift in its own.

## Example

```python
# example.py
from typing import Optional

def find_record(id: int) -> Optional[dict]:
    if id <= 0:
        return None
    return {"id": id}

def get_name(id: int) -> str:
    record = find_record(id)
    if record is not None:
        return record["name"]
    # Missing else: falls through with no return
```

```
$ furqan-lint check example.py

MARAD  example.py
  3 violation(s):
    [all_paths_return] Function 'get_name' at line 8 declares
    -> str but not every control-flow path reaches a return
    statement.

    [status_coverage] Function 'get_name' at line 8 calls
    'find_record' (returns Optional[dict]) but declares -> str.
    The Optional is silently collapsed.

    [return_none_mismatch] Function 'get_name' at line 8
    declares -> str but returns None on at least one path.
```

## Closure history

Per-version closure ledgers are in
[CHANGELOG.md](CHANGELOG.md). This README previously
mirrored closures from v0.2.0 through v0.11.0; that mirror
was retired in v0.11.7 (Phase G10.5 al-Mubin) because
CHANGELOG.md is the canonical closure ledger and the
README mirror was repeatedly drifting out of sync. The
framework section 10.2 retirement procedure was followed:
the existing prose was deleted and a single pointer
section took its place.

## Remaining limitations

Each limitation here has a fixture in `tests/fixtures/documented_limits/`
and a test in `tests/test_documented_limits.py` pinning the current
behaviour, so any change (in either direction) is intentional rather
than silent.

- **`self.method()` calls.** The adapter resolves `self.foo()` to the
  bare method name `foo`, the same as a plain `foo()` call. This is
  not a bug today but will need revisiting if the adapter ever stores
  qualified call paths.
- **Checker coverage.** Only four of Furqan's ten checkers run on
  Python. The rest depend on Python-specific conventions (scope
  declarations, layer annotations, calibration bounds, dependency
  mapping) that standard Python does not provide.
- **Return-type expression inference.** `return_none_mismatch` only
  catches the `None` literal. A `-> int` function returning `"hello"`
  is not caught.
- **Exhaustive `match` recognition.** Each case body wraps as a
  maybe-runs `IfStmt`, so D24 cannot recognise a structurally
  exhaustive `match` (with a `case _:` arm) as guaranteed coverage.
  Future work could splice the catch-all case into the prior
  `IfStmt`'s `else_body`.
- **Aliased `Optional` / `Union` imports.** `from typing import
  Optional as MyOpt; -> MyOpt[X]` is treated as a non-Optional return
  type. The same gap applies to `Union`: `from typing import Union as
  U; -> U[X, None]` and `from somelib import Union; -> Union[X, None]`
  both bypass the bare-name and `typing.` / `t.` matchers. The matcher
  recognises the bare `Optional` / `Union` names and the qualified
  `typing.` / `t.` forms only; arbitrary aliases and same-named imports
  from non-`typing` modules need symbol-table tracking (parse imports,
  build alias map, resolve before matching), which is deferred to a
  future phase. Workaround: use the bare or qualified form, or rename
  the import to `import typing as t`.
- **Local classes inside any function or method body.** A class
  defined inside a function body or a method body has its methods
  silently dropped. The v0.3.2 nested-class fix added recursive
  descent through top-level `ClassDef` -> `ClassDef` (so
  `Outer.Inner.method` is collected); it does NOT extend through
  `FunctionDef` -> `ClassDef` regardless of whether the
  `FunctionDef` is at module scope or inside another `ClassDef`. The
  argument for the asymmetry: a local class is a private
  implementation detail (often a closure-like return value), not
  part of the module's public contract that D24 and
  `return_none_mismatch` exist to enforce. If a real-world
  regression demonstrates otherwise, extend the function walker to
  descend into local `ClassDef` bodies and call
  `_collect_class_methods`.
### Rust adapter (current as of v0.8.3)

Each Rust limit has a fixture in
`tests/fixtures/rust/documented_limits/` and a pinning test in
`tests/test_rust_correctness.py`.

- **Trait-object return types.** Functions returning `Box<dyn Trait>`
  are translated to a `TypePath` that ignores the trait-object
  payload. Trait-object polymorphism is out of scope; a future
  a future checker would be the right place to revisit. Pinned as
  `tests/fixtures/rust/documented_limits/trait_object_return.rs`.
- **Lifetime-affected return types.** Functions with explicit
  lifetime parameters (`fn f<'a>(...) -> &'a str`) have their
  lifetimes stripped during translation; the return type is
  treated as `-> &'a str` literally (no lifetime semantics).
  D24's path-coverage logic is unaffected; a future borrow-pattern
  checker would need lifetime preservation. Pinned as
  `tests/fixtures/rust/documented_limits/lifetime_param_return.rs`.
- **Closures with annotated return types.** `closure_expression`
  nodes are skipped for D24, D11, AND R3 in v0.7.1. The outer
  function is checked normally; the closure body is opaque.
  A future phase may revisit when there is a concrete user-reported
  false negative. Pinned as
  `tests/fixtures/rust/documented_limits/closure_with_annotated_return.rs`.
- **`extract_public_names` omits impl-block methods.**
  The Rust additive-only diff path's name extractor walks only
  top-level CST root children; methods defined inside
  `impl Type { ... }` blocks are intentionally not collected
  in v0.8.3. Asymmetric with goast (which emits qualified
  method names like `Counter.increment` as of v0.8.2). Pinned
  as `tests/fixtures/rust/documented_limits/impl_methods_omitted.rs`
  (added in v0.8.3). Resolution path: registered as a v0.8.4
  candidate.
- **`panic!()` (or any diverging macro) used as a tail expression
  with no `;`.** The translator synthesizes a `ReturnStmt(opaque)`
  for any tail expression per the v0.7.0 R1 rule, so R3 (zero-return)
  does not fire on `fn f() -> i32 { panic!() }`. Adding a fix
  would require either a hardcoded diverging-macro allowlist
  (brittle) or cross-file type inference of the macro's expansion
  type (out of scope). A future phase may revisit if the Rust ecosystem
  standardizes a `#[diverging]` attribute. Pinned as
  `tests/fixtures/rust/documented_limits/r3_panic_as_tail_expression.rs`.



### Go adapter (current as of v0.8.2)

Each Go limit has a fixture in
`tests/fixtures/go/documented_limits/` and a pinning test in
`tests/test_go_documented_limits.py` (or, for the older
translator-level limits, in `tests/test_go_translator.py`).

- **3+-element return signatures.** Translate to opaque
  `TypePath("<multi-return>")`. D24 and D11 see the function
  but cannot reason about the individual arms. Pinned as
  `tests/fixtures/go/documented_limits/multi_return_three_or_more.go`.
- **2-element non-error tuple returns.** Translate to opaque
  `TypePath("(T, U)")`. D11's may-fail predicate does NOT fire
  on these; only `(T, error)` shapes are recognized as may-fail
  per locked decision 4. Pinned as
  `tests/fixtures/go/documented_limits/two_element_non_error_tuple.go`.
- **`for` and `for-range` bodies.** Wrap as may-runs-0-or-N
  opaque IfStmt. D24 cannot prove that a `for` body that always
  returns guarantees coverage. Pinned as
  `tests/fixtures/go/documented_limits/for_statement_opaque.go`.
- **`switch` bodies.** Wrap as may-runs-0-or-N opaque IfStmt;
  case-arm returns are invisible to D24. Pinned as
  `tests/fixtures/go/documented_limits/switch_statement_opaque.go`.
- **`select` bodies.** Wrap as may-runs-0-or-N opaque IfStmt.
  Pinned as
  `tests/fixtures/go/documented_limits/select_statement_opaque.go`.
- **`defer` statements.** Wrap as opaque; the deferred call's
  effect on control flow (panic recovery, resource cleanup) is
  not modeled. Pinned as
  `tests/fixtures/go/documented_limits/defer_statement_opaque.go`.
- **Interface method dispatch.** Calls through interface
  receivers are not specially modeled; the receiver type is
  opaque to the adapter. Pinned as
  `tests/fixtures/go/documented_limits/interface_method_dispatch.go`.
- **Generic type parameters.** Syntactically allowed in
  signatures but their constraints are ignored. Pinned as
  `tests/fixtures/go/documented_limits/generic_type_parameters.go`.
- **R3 not-applicable.** The Go compiler rejects all R3 firing
  shapes (zero-return on annotated functions) at compile time;
  the only compilable nearest-edge case is a named-return with
  bare `return`, which the translator sees as having a return
  statement. Pinned as
  `tests/fixtures/go/documented_limits/r3_compile_rejected.go`
  (added in v0.8.1).

### ONNX adapter (current as of v0.9.4)

Each ONNX limit has a fixture in
`tests/fixtures/onnx/documented_limits/` and a pinning test in
`tests/test_onnx_correctness.py`,
`tests/test_onnx_public_surface_additive.py`, or
`tests/test_onnx_shape_coverage.py`.

- **score_validity is opt-in via [onnx-profile] (v0.9.4).**
  The v0.9.4 score-validity ADVISORY checker wraps
  `onnx_tool.model_profile()` to surface profiler-coverage
  gaps (e.g., the cont45 TopK-without-axis crash). It runs only
  when the `[onnx-profile]` extra is installed (which brings in
  `onnx_tool`); otherwise it silent-passes. ADVISORY findings
  exit 0 (the model is structurally valid; the failure is in
  the deployment-side profiler). Pinned as
  `tests/fixtures/onnx/documented_limits/score_validity_optin_extra.py`.

- **numpy_divergence requires NeuroGolf-convention sidecars
  (v0.9.3).** The numpy-vs-ONNX divergence checker is opt-in by
  reference presence: it only runs when (a) the
  `[onnx-runtime]` extra is installed, (b) a sibling
  `<basename>_build.py` exists exporting top-level callable
  `numpy_reference`, AND (c) a sibling `<basename>.json` exists
  in ARC-AGI task format with `train[*]['input']`. Generic ONNX
  users with no NeuroGolf-shaped sidecars see silent-pass on
  the divergence checker. General-purpose reference-discovery
  conventions (decorator-based annotation) and probe-grid
  formats are a v0.9.5+ extension. Pinned as
  `tests/fixtures/onnx/documented_limits/numpy_divergence_neurogolf_convention.py`.

- **Dynamic shape silent-pass.** Strict-mode shape inference
  silent-passes on `dim_param` (symbolic batch / sequence dims
  like `"batch"`) and empty `dim_value` (dynamic shapes). v0.9.1
  takes the position that this is the right default because
  ONNX models with `dim_param` are typically deployment-time
  signature shapes that bind concrete values at runtime; a
  future release may revisit if a concrete user-reported false
  negative motivates a stricter mode. Pinned as
  `tests/fixtures/onnx/documented_limits/dynamic_shape_silent_pass.py`.
- **`graph.value_info` and `graph.initializer` not in additive
  contract.** The additive-only diff (`furqan-lint diff
  old.onnx new.onnx`) covers `graph.input` and `graph.output`
  ValueInfo only. Intermediate tensors and initializers are out
  of scope per Decision 5 of the v0.9.0 prompt; including them
  would create false positives on every model retraining.
  Pinned as `tests/fixtures/onnx/documented_limits/intermediates_excluded.py`.
- **ONNX op-registry pin window `>=1.14,<1.19`.** Op registry
  version is pinned to prevent silent semantics drift across
  `onnx` package upgrades (the ONNX op registry retroactively
  adds operators across releases). Consumers requiring a newer
  registry must wait for a furqan-lint patch release that bumps
  the pin. Pinned as
  `tests/fixtures/onnx/documented_limits/registry_pin_window.py`.

### Retired in v0.9.1

- **D11-onnx deferred to v0.9.1** (former `shape_coverage_deferred`
  documented limit). v0.9.1 ships D11-onnx via strict-mode shape
  inference, so the deferral entry is no longer load-bearing.
  The companion v0.9.0 pinning test
  `test_onnx_d11_deferred_v0_9_0_passes` is also deleted in
  v0.9.1 commit 4 per the delete-plus-add discipline (round-30
  MED-1 closure). The v0.9.1 firing test
  `test_d11_onnx_fires_on_shape_mismatch` replaces it.

## License

Apache-2.0.
