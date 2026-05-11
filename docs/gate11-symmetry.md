# Gate 11 three-substrate symmetry

After v0.12.0 (al-Mursalat / Phase G11.2 ship), the Python,
Rust, and Go verifiers share behavior on:

| Concern | Python | Rust | Go |
|---|---|---|---|
| Identity policy default (CASM-V-035 refuse-without-policy) | v0.11.2+ (v0.11.5 F24 al-Bayyina corrective) | v0.11.0+ | v0.12.0+ |
| Identity policy enforcement (`--expected-identity` required) | v0.11.2+ | v0.11.0+ | v0.12.0+ |
| trusted_root threading (v0.11.8-LIVE construction pattern) | v0.11.2+ (v0.11.5 F24 corrective) | v0.11.0+ | v0.12.0+ |
| checker_set_hash Form A/B (`sha256(linter_version)` forbidden) | v0.11.2+ | v0.11.0+ | v0.12.0+ |
| Identity-extraction error handling (CASM-V-036) | v0.11.2+ | v0.11.0+ | v0.12.0+ |
| Signature canonicalization (nested element-wise recursion) | v0.11.2+ | v0.11.0+ | v0.12.0+ |
| CLI dispatch by manifest-declared language | v0.12.0+ | v0.12.0+ | v0.12.0+ |

The dispatch surface symmetry (last row) was closed at
v0.12.0 al-Mursalat: the CLI's `manifest verify` subcommand
(plus the `check --gate11` directory-walk path) inspects
`manifest.module_identity["language"]` and routes through the
single canonical entry `verification.verify(manifest, args)`
which dispatches to private per-language handlers
(`_verify_python`, `_verify_rust`, `_verify_go`) via the
function-local `_LANGUAGE_DISPATCH` dict. The prior rows
landed in their respective language ships.

The v0.11.5 F24 al-Bayyina hotfix re-routed the Python
verifier's sigstore API path (from `sigstore._internal.trust`
to the public `sigstore.trust` with fallback per H-5
propagation defense). v0.12.0 Go mirrors the post-F24 live
pattern (not the at-Tawbah v0.11.2 reference).

## Substrate-of-record entries

The substrate modules participating in the three-substrate
symmetry are pinned in `_CHECKER_SOURCE_FILES` (gate11/
checker_set_hash.py) per F-PA-3 v1.8 alphabetical-within-
section discipline:

| Section | Entries |
|---|---|
| Core | `additive.py`, `cli.py` |
| gate11 | `__init__.py`, `bundle.py`, `cli.py`, `go_signature_canonicalization.py` (al-Mursalat T03), `go_verification.py` (al-Mursalat T04), `manifest_schema.py`, `module_canonicalization.py`, `python_verification.py` (as-Saff T04(b)), `rust_manifest.py`, `rust_signature_canonicalization.py`, `rust_surface_extraction.py`, `rust_verification.py` (as-Saff T04(b)), `signature_canonicalization.py`, `signing.py`, `surface_extraction.py`, `verification.py` |
| go_adapter | `cmd/goast/main.go` (al-Mursalat T05; goast source pin per F6 v1.1 SOURCE-PRESENT branch + F-PF-3 v1.7 absorption) |

Tuple count: 16 entries at v0.11.8 → 19 entries at v0.12.0
(+3: two gate11 Go modules + one go_adapter goast source).
Substrate-attestation rationale: a Relying Party detects
substrate divergence between bundles signed by furqan-lint
installations whose Go substrate modules disagree; the goast
binary's source code is part of the Form A checker_set_hash
surface, not just the gate11/* verification modules.

## Successor phase

Phase G11.4 Tasdiq al-Bayan (cross-substrate verification
corpus) will exercise the symmetry as a unified test matrix
that runs the same conceptual test against each substrate.
After G11.4, the foundation is in place for v1.0
self-attestation (furqan-lint signing its own releases with
gate11).
