## [0.11.2] - 2026-05-09

### Substrate corrective (at-Tawbah / G11.0.1)

Phase G11.0.1 closes the two genuine prospective audit
gaps the v0.11.0 + v0.11.1 ship did not absorb (per Round 28
empirical state audit), plus closes Round 28 finding F18
(flagship: backfill_github_releases.py --dry-run flag silently
no-op'd). The other amended_4 prospective findings (C-1, H-5,
H-6, M-7) were already backported to the unified Python
verifier substrate via the G11.1 commits ee656ad +
c6b219a; this release acknowledges that and pins the
remaining two gaps explicitly.

#### Closures

- H-4 HIGH (Python signature canonicalization): the Python
  `_canonical_type_string` fell through to
  `ast.unparse(node.slice)` for multi-argument generic
  parameters, producing tuple-stringification artifacts like
  `Dict[(str, int)]` instead of `Dict[str, int]`. v0.11.2
  recurses element-wise on the Tuple slice and flattens
  inner unions across the Subscript-Union boundary so
  `Union[Optional[T], List[U]]` canonicalizes consistently.
  Cross-language symmetry with the Rust verifier's amended_4
  T03 rules 6 + 7 is now restored. (T03)
- F18 HIGH (Round 28 flagship): scripts/backfill_github_releases.py
  now requires an explicit `--dry-run` (preview only) or
  `--apply` (real `gh release create` calls) flag. The default
  no-flag invocation exits 2 with argparse usage rather than
  silently mutating live GitHub state. The structural-honesty
  thesis applied to the project's own scripts: the documented
  surface claim ("--dry-run is preview mode") now matches the
  substrate behavior. (T08)

#### Closures from amended_4 prospective defenses (no-op acknowledgement)

The following corrections were already applied in v0.11.0
via the G11.1 commits ee656ad + c6b219a; this entry pins the
audit register state explicitly:

- C-1 CRITICAL (verifier UnsafeNoOp default): closed in v0.11.0
  by `verification.step6_verify_sigstore`'s refuse-without-
  policy default raising CASM-V-035; cross-applied to both
  Python and Rust pipelines via the unified verifier.
- H-5 HIGH (trusted_root threading): closed in v0.11.0 by
  `Verifier(_inner=trusted_root)` lower-level constructor.
- H-6 HIGH (checker_set_hash placeholder): closed in v0.11.0
  by `compute_checker_set_hash()` Form A substantive hash
  over pinned source-file tuple.
- M-7 MEDIUM (string-sentinel identity extraction): closed
  in v0.11.0 by `_extract_identity` raising CASM-V-036
  typed errors.

#### New corrective work this release

- M-5 MEDIUM: `step5_canonicalize_manifest` docstring now
  references `Manifest.from_dict` as the canonical
  enforcement site; redundant in-step enforcement prose
  removed. (T06)
- M-6 MEDIUM: SECURITY.md Newman 2022 N2 disclosure wording
  now names `--expected-identity` and CASM-V-035 explicitly,
  closing the surface-substrate gap. (T06)
- F19 LOW (incidental): backfill version-filter excludes
  v0.11.1+ workflow-managed releases via the new
  `_WORKFLOW_MANAGED_FLOOR = (0, 11, 1)` constant in
  `scripts/backfill_github_releases.py`. (T08 side closure)

#### Substrate canonical-authority extension

- SAFETY_INVARIANTS.md Section "Invariant 6" step 6 now
  documents CASM-V-032 (identity policy mismatch),
  CASM-V-035 (no identity policy supplied), and CASM-V-036
  (identity extraction failure) explicitly per amended_4
  T05 specification. (T01)

#### Deferrals

- F4 ONNX empty-graph: Phase G11.3 scope.
- F5 Release-vs-tag QUESTION: QUESTIONS.md.
- F10 SBOM: Phase G11.4 or v1.5.
- F12 furqan PyPI dep: declined Shape C.
- F17 framework section 4 amendment: framework-side.
- F20 sandbox-CI parity: separate release-checklist amendment.
- F21 PyPI CDN cache transient: separate runbook amendment.

### Tests

Test count: 576 (v0.11.1 ship state) -> 589 (v0.11.2).
Net delta: +13 (8 in test_python_signature_h4.py covering
the H-4 fixtures + inner-difference detection + tuple-value
preservation; 5 in test_backfill_dry_run.py covering F18
no-flag exit / both-flags rejection / no-subprocess-call /
expected-version enumeration / F19 workflow-managed-floor).

### Cross-language symmetry restored

After v0.11.2, the Python verifier's signature canonicalization
matches the Rust verifier's amended_4 T03 rules 6 + 7
(nested-generic element-wise recursion). The other amended_4
defenses (C-1 identity policy, H-5 trusted_root threading,
H-6 checker_set_hash, M-7 typed identity-extraction errors)
were already shared between the two pipelines from v0.11.0.

### Round-28 closure ledger

| Disposition | Count | Findings |
|-------------|-------|----------|
| Genuine v0.11.2 closure | 4 | H-4, M-5, M-6, F18 |
| Acknowledgement (closed in v0.11.0) | 4 | C-1, H-5, H-6, M-7 |
| Side closure | 1 | F19 |
| Deferral | 7 | F4, F5, F10, F12, F17, F20, F21 |

---

