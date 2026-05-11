# Gate 11 four-substrate symmetry (with honest asymmetries)

After v0.13.0 (an-Naziat / Phase G11.3 ship), the Python,
Rust, Go, and ONNX verifiers share behavior on the
identity-policy / trusted-root / dispatch substrate, with
honest asymmetries where ONNX is structurally different
(graph-shape canonicalization vs type-shape; ONNX-specific
opset/dim_param checks):

| Concern | Python | Rust | Go | ONNX |
|---|---|---|---|---|
| Identity policy default (CASM-V-035 refuse-without-policy) | v0.11.2+ (v0.11.5 F24 al-Bayyina corrective) | v0.11.0+ | v0.12.0+ | v0.13.0+ |
| Identity policy enforcement (`--expected-identity` required) | v0.11.2+ | v0.11.0+ | v0.12.0+ | v0.13.0+ |
| trusted_root threading (v0.11.8-LIVE construction pattern) | v0.11.2+ (v0.11.5 F24 corrective) | v0.11.0+ | v0.12.0+ | v0.13.0+ |
| checker_set_hash Form A/B (`sha256(linter_version)` forbidden) | v0.11.2+ | v0.11.0+ | v0.12.0+ | v0.13.0+ |
| Identity-extraction error handling (CASM-V-036) | v0.11.2+ | v0.11.0+ | v0.12.0+ | v0.13.0+ |
| Signature canonicalization (type-shape vs graph-shape) | type-shape v0.11.2+ | type-shape v0.11.0+ | type-shape v0.12.0+ | **graph-shape** v0.13.0+ (honest asymmetry) |
| CLI dispatch by manifest-declared language | v0.12.0+ | v0.12.0+ | v0.12.0+ | v0.13.0+ |
| Opset-policy-mismatch (CASM-V-070) | N/A | N/A | N/A | v0.13.0+ |
| Dim-param-violation (CASM-V-071) | N/A | N/A | N/A | v0.13.0+ |

The dispatch surface symmetry was closed at v0.12.0
al-Mursalat for the source-code substrates: the CLI's
`manifest verify` subcommand (plus the `check --gate11`
directory-walk path) inspects
`manifest.module_identity["language"]` and routes through the
single canonical entry `verification.verify(manifest, args)`
which dispatches to private per-language handlers
(`_verify_python`, `_verify_rust`, `_verify_go`) via the
function-local `_LANGUAGE_DISPATCH` dict. v0.13.0 an-Naziat
extends the dispatch with a fourth lazy-import + dict entry
for ONNX (`_verify_onnx`), closing the canonical mushaf chain
at the CLI surface. Phase G11.4 Tasdiq al-Bayan operates
against this four-entry surface as a drift-detection
invariant rather than adding entries.

ONNX-specific asymmetries (last two rows + the type-shape /
graph-shape distinction at signature canonicalization) are
named honestly rather than forced into a type-shape parallel.
The four-place documented limits at
`tests/test_gate11_onnx_limits.py` mechanically enforce each
asymmetry (binary substrate; dim_param partial concreteness;
intermediates excluded; NeuroGolf sidecar boundary per
`docs/onnx-attestation-boundary.md` T07).

The v0.11.5 F24 al-Bayyina hotfix re-routed the Python
verifier's sigstore API path (from `sigstore._internal.trust`
to the public `sigstore.trust` with fallback per H-5
propagation defense). v0.12.0 Go mirrors the post-F24 live
pattern (not the at-Tawbah v0.11.2 reference).

## Substrate-of-record entries

The substrate modules participating in the four-substrate
symmetry are pinned in `_CHECKER_SOURCE_FILES` (gate11/
checker_set_hash.py) per F-PA-3 v1.8 + F-NA-5 v1.4
alphabetical-within-section discipline:

| Section | Entries |
|---|---|
| Core | `additive.py`, `cli.py` |
| gate11 | `__init__.py`, `bundle.py`, `cli.py`, `go_signature_canonicalization.py` (al-Mursalat T03), `go_verification.py` (al-Mursalat T04), `manifest_schema.py`, `module_canonicalization.py`, `onnx_signature_canonicalization.py` (an-Naziat T03), `onnx_verification.py` (an-Naziat T04), `python_verification.py` (as-Saff T04(b)), `rust_manifest.py`, `rust_signature_canonicalization.py`, `rust_surface_extraction.py`, `rust_verification.py` (as-Saff T04(b)), `signature_canonicalization.py`, `signing.py`, `surface_extraction.py`, `verification.py` |
| go_adapter | `cmd/goast/main.go` (al-Mursalat T05; goast source pin per F6 v1.1 SOURCE-PRESENT branch + F-PF-3 v1.7 absorption) |

Tuple count: 16 entries at v0.11.8 -> 19 entries at v0.12.0
(+3: two gate11 Go modules + one go_adapter goast source)
-> 21 entries at v0.13.0 (+2: two gate11 ONNX modules per
F-CW-NZ-2 substrate-convention parity precedent from
al-Mursalat T05 and Phase G11.1 baseline pinning both
signature_canonicalization + verification files for each
substrate). Substrate-attestation rationale: a Relying Party
detects substrate divergence between bundles signed by
furqan-lint installations whose ONNX substrate modules
disagree; both onnx_signature_canonicalization.py and
onnx_verification.py are part of the Form A checker_set_hash
surface at v0.13.0+.

## Successor phase

Phase G11.4 Tasdiq al-Bayan (cross-substrate verification
corpus) will exercise the symmetry as a unified test matrix
that runs the same conceptual test against each of the four
substrates (4 signers x 4 verifiers = 16 cells). Honest
asymmetries documented in this file (graph-shape vs type-
shape canonicalization; ONNX-specific opset/dim_param
checks) are not forced into parallel; they are exercised in
their own corpus entries. After G11.4, the foundation is in
place for v1.0 self-attestation (furqan-lint signing its own
releases with gate11).
