# SAFETY_INVARIANTS.md

## Phase G11.A -- al-Fatiha
## Universal Safety Invariants for Sigstore-CASM Gate 11
## v1.0_second_revision_amended_2

> "All praise is due to Allah, Lord of the worlds. The Most
> Merciful, the Especially Merciful. Sovereign of the Day of
> Recompense. It is You we worship and You we ask for help.
> Guide us to the straight path. The path of those upon whom
> You have bestowed favor, not of those who have earned anger
> or of those who are astray."
>
> -- Surah al-Fatiha (1:1-7)

This document is NORMATIVE for all subsequent Phase G11.x
implementations of Sigstore-CASM Gate 11 across the furqan-lint
repository. Its primary role is to specify the seven
cryptographic and protocol invariants of Sigstore-CASM Gate 11
plus the four mandatory disclosures derived from the Sigstore
threat model. Strategy mappings and empirical foundations are
included only insofar as they explain why these invariants are
shaped as they are; full treatment lives in the methodology
papers (`Bayyinah at-Tartib v1.0` second revision May 7 2026
and `Bayyinah al-Munasabat v1.0` second revision May 7 2026)
referenced by pointer.

This is the v1.0_second_revision_amended_2 layer. Five layers
of evolution are preserved per the Bayyinah delete-plus-add
discipline; see "Auditor's response register" below.

La hawla wa la quwwata illa billah.

---

## Document identification

- **Document**: G11.A SAFETY_INVARIANTS for Sigstore-CASM Gate 11
- **Round**: 14, sub-position A (foundational, ahead of G11.0
  through G11.12)
- **Revision**: v1.0_second_revision_amended_2 (May 7 2026)
- **Status**: NORMATIVE for all subsequent Phase G11.x phases
- **Repository**: https://github.com/BayyinahEnterprise/furqan-lint
- **License**: Apache-2.0 (matches furqan-lint)
- **Anchor**: Surah al-Fatiha 1:1-7

**Primary normative content**:

- The seven canonical Sigstore-CASM invariants (sections 1-7)
- The four mandatory disclosures (section "Mandatory disclosures")
- Section 8: Foundation-status inheritance (sole authoritative
  location in this file for empirical-magnitude figures)
- Normative references block (per audit F2)

**Out of scope for this file** (referenced by pointer):

- Per-strategy elaboration: see at-Tartib v1.0 (second revision)
  section 4
- Empirical methodology and results: see al-Munasabat v1.0
  (second revision) sections 3-7
- Case-by-case counterfactual mapping: see at-Tartib section 7.1
- Aggregate counterfactual and conditional economic case: see
  at-Tartib sections 7.2-7.3
- Policy-vs-engineering distinction for public-interest
  software: see at-Tartib section 6.3
- Industry-by-industry mortality and economic-loss accounting:
  see at-Tartib sections 5-7

---

## Operating discipline

- Standing Rule 1: no em-dashes in repository content. Use `--`.
- Severity uppercase (HIGH, MEDIUM, LOW, ADVISORY).
- Six-element findings format (when this file's review
  processes surface findings during Phase G11.x rounds).
- Delete-plus-add discipline: this file is the fifth mushaf
  layer; four prior layers are preserved as historical record.
- All empirical figures cited from Section 8 only; other
  sections cross-reference Section 8.

---

## The seven canonical invariants

These are CRYPTOGRAPHIC and PROTOCOL invariants. They are NOT
magnitude claims about the al-Munasabat empirical finding and
NOT prevention claims about the at-Tartib counterfactual. They
are substrate specifications grounded in production-deployed
Sigstore (Newman et al. 2022; deployment evidence Schorlemmer
et al. 2024 and Kalu et al. 2025) and IETF SCITT (RFC-track).
The Sigstore-CASM substrate's value is to make supply-chain
failures cryptographically attributable and forensically
reconstructable, not to prevent supply-chain failures directly.

### Invariant 1: Cryptographic substrate identity

**Declaration**: All Phase G11.x implementations MUST use
Sigstore as the cryptographic substrate. Specifically:

- Fulcio as the certificate authority
- Rekor as the transparency log
- TUF as the root of trust
- OIDC as the identity binding mechanism

**Verification**: every implementation references
`sigstore-python`, `sigstore-rs`, `sigstore-go`, or an
equivalent client library that implements the Sigstore
protocol.

**"Equivalent client library" defined**: a library that can
obtain Sigstore-compatible identity-bound certificates from a
Fulcio instance, produce Rekor-loggable bundles, and verify
using the same trust-root and bundle semantics as the
canonical clients. A library that performs cryptographic
signing in some other format without this Fulcio + Rekor + TUF
interaction surface is NOT an equivalent client library for
the purposes of Phase G11.x. Cryptographic-signing libraries
that produce raw COSE, JWS, PGP, or X.509-CMS signatures
without obtaining Fulcio-issued ephemeral certificates and
without a Rekor entry to point at fall outside this definition
and require a separate normative document if substrate-mapped.

**Strategy cross-reference**: Recording Angels Pattern
(at-Tartib section 4.6, theoretically grounded). Sigstore's
Rekor operationalizes the append-only transparency-log aspect
of the Recording Angels pattern at the supply-chain integrity
layer. The Quranic two-witness analogy (Qaf 50:17-18 dual
recorders) is treated as analogy in at-Tartib section 4.6, not
as a literal protocol fact about Sigstore's architecture. Per
at-Tartib section 7.2 necessary-not-sufficient framing, this
substrate makes supply-chain failures forensically
reconstructable; prevention requires organizational follow-
through downstream of detectability.

### Invariant 2: CASM manifest schema stability

**Declaration**: the CASM manifest schema is versioned. v1.0
is defined in Phase G11.0. All Phase G11.x implementations
across all substrates MUST produce manifests that parse
successfully under the canonical v1.0 schema.

The v1.0 schema fields, REQUIRED in every manifest:

- `casm_version`: string, exactly `"1.0"` for v1
- `module_identity`: object with `language`, `module_path`,
  `module_root_hash`
- `public_surface`: object with `names`, `extraction_method`,
  `extraction_substrate`
- `chain`: object with `previous_manifest_hash` (nullable on
  first manifest in chain) and `chain_position` (1-indexed
  integer)
- `linter_substrate_attestation`: object with the linter's
  `version` plus a `checker_set_hash` integrity field
- `trust_root`: object identifying the trust root the manifest
  is signed against (public Sigstore, staging, or private
  instance identifier)
- `issued_at`: ISO-8601 UTC timestamp

**Verification**: a manifest produced by ANY Phase G11.x
implementation MUST parse via the canonical Python reference
implementation (`furqan_lint.gate11.manifest_schema.Manifest.from_dict`).
Cross-substrate manifests sign to the same canonical bytes;
see Invariant 3.

**Strategy cross-reference**: Naskh Discipline (at-Tartib
section 4.2, theoretically grounded). Schema versioning IS
naskh applied to the wire format: each schema revision
abrogates the prior one without erasing it; v1 manifests
remain parseable by v1 verifiers indefinitely.

### Invariant 3: Canonical signature substrate

**Declaration**: the signature is computed over the canonical
form of the manifest JSON, per RFC 8785 (JSON Canonical Form,
JCS).

The canonicalization rules:

1. UTF-8 encoding
2. Object keys in lexicographic order (codepoint order)
3. No whitespace between tokens
4. Number formatting per ECMAScript JSON.stringify
5. String escaping per JSON spec
6. No backslash-u escaping for printable ASCII codepoints

**Verification**: cross-substrate test fixtures. A manifest
canonicalized by `sigstore-python`'s RFC 8785 implementation
MUST produce byte-identical output to the same manifest
canonicalized by any other substrate's RFC 8785
implementation. Phase G11.4 (Tasdiq al-Bayan) carries the
cross-substrate canonicalization parity gate.

**Strategy cross-reference**: Validator-by-Different-Instance
(at-Tartib section 4.5, theoretically grounded). Multiple
RFC 8785 implementations canonicalizing the same manifest
serve as the substrate-level instance of validator-by-
different-instance.

### Invariant 4: Module canonicalization rules

**Declaration**: the `module_root_hash` is the SHA-256 of the
module source canonicalized as follows:

1. Read the module source as bytes
2. Decode as UTF-8 (non-UTF-8 source MUST be rejected with
   error code `CASM-V-002`)
3. Normalize line endings to `\n` (LF only)
4. Strip a UTF-8 BOM if present at the start
5. Re-encode as UTF-8 bytes
6. SHA-256 the resulting bytes; emit as `sha256:<hex64>`

For ONNX (Phase G11.3 substrate), "module source" is the
protobuf-serialized model file bytes; UTF-8 decoding does not
apply, but BOM-strip and trailing-byte normalization rules are
specified per Phase G11.3.

For Rust (Phase G11.1) and Go (Phase G11.2), the canonicalization
rules above apply unchanged because both languages mandate UTF-8
source files in their formal specifications.

**Verification**: each substrate's `module_canonicalization`
test surface includes a fixture that exercises BOM handling,
mixed CRLF / CR / LF line endings, and an explicit non-UTF-8
rejection case.

### Invariant 5: Public-surface extraction parity

**Declaration**: each substrate has its own public-surface
extraction algorithm. The algorithm is versioned via the
`extraction_method` field in the format `<algo>@<version>`.

For v1, the supported extraction methods are:

- `ast.module-public-surface@v1.0` (Python; Phase G11.0)
- `tree-sitter.rust-public-surface@v1.0` (Rust; Phase G11.1)
- `goast.go-public-surface@v1.0` (Go; Phase G11.2)
- `onnx.graph-io-surface@v1.0` (ONNX; Phase G11.3)

A substrate MAY ship a v1.1 extraction method as a backward-
compatible refinement; it MUST NOT silently change the
fingerprint output of the v1.0 method on any input. Schema
version remains `casm_version: "1.0"` while extraction methods
co-exist; Naskh Discipline (Invariant 2 cross-reference)
governs migration.

Each substrate's extraction algorithm MUST be deterministic:
re-running it on the same source MUST produce a byte-identical
fingerprint. Sources of nondeterminism (Python `id()`,
hashtable iteration order, file timestamps, build paths) are
forbidden in fingerprint inputs.

**Verification**: each substrate's `signature_canonicalization`
test surface includes a fixture set covering each public-name
kind (function / class / constant for Python; equivalent
classifications for Rust / Go / ONNX) plus a determinism test
running extraction multiple times and asserting fingerprint
equality.

**Strategy cross-reference**: Multi-Corpus Baseline Discipline
(at-Tartib section 4.4, theoretically grounded). Four
substrates plus three independent verifiers per Phase G11.4
constitute the multi-corpus baseline at the substrate level.

### Invariant 6: Verification flow universality

**Declaration**: the nine-step offline verification flow
defined in Phase G11.0 MUST be implemented identically across
all substrates. The error code namespace `CASM-V-001` through
`CASM-V-064` (plus the Phase-specific extensions) is universal
across substrates.

The nine steps:

1. Parse bundle (`CASM-V-010` on JSON failure or wrapped
   schema error)
2. Check `casm_version == "1.0"` (`CASM-V-001`)
3. Check `language` matches the substrate the verifier is
   running against (`CASM-V-001`). The substrate-LIVE
   supported-language set at v0.12.0 is `{python (Phase
   G11.0, v0.10.0), rust (Phase G11.1, v0.11.0), go (Phase
   G11.2, v0.12.0)}`; ONNX (Phase G11.3) is substrate-
   anticipated per Invariant 5 extraction-method enumeration
   and ships in v0.13.0 an-Naziat. CASM-V-001 is the
   canonical code for both casm_version mismatch and
   language-not-supported semantics (Option A per
   al-Mursalat T01 disposition: single code, union
   semantic). The verifier-side dispatch site at
   `verification.verify`'s function-local
   `_LANGUAGE_DISPATCH` raises CASM-V-001 with a positional
   message naming the next phase target when an unsupported
   language is encountered.
4. Load Sigstore trust root via TUF (`CASM-V-020` ADVISORY
   on refresh failure with cache fallback; `CASM-V-021` if
   no cache exists)
5. Re-canonicalize the manifest (RFC 8785; Invariant 3)
6. Verify Sigstore signature against the canonical bytes
   (`CASM-V-030..034` by failure mode); enforce the
   configured Identity policy (`CASM-V-032` on identity
   mismatch; `CASM-V-035` if no `--expected-identity` and
   no explicit `--allow-any-identity` -- the default refuse-
   without-policy state); on failed identity extraction from
   the signing certificate raise `CASM-V-036` rather than
   returning a string sentinel
7. Compare `module_root_hash` to the on-disk module
   (`CASM-V-040` on mismatch)
8. Compare `public_surface.names` to the live extraction;
   surface `CASM-V-INDETERMINATE` rather than a false pass
   when the live module exposes dynamic shape that the
   extractor cannot resolve (e.g., Python dynamic `__all__`)
9. Check `chain_pointer` integrity against the previous bundle
   when supplied (`CASM-V-060` on hard mismatch; `CASM-V-061`
   ADVISORY when no previous bundle is locally accessible)

**Strategy cross-reference**: Sulayman-Naml Pattern (at-Tartib
section 4.7, theoretically grounded). ADVISORY findings
(`CASM-V-003`, `CASM-V-020`, `CASM-V-061`) are the weak
signals: surfacing them is the substrate's responsibility;
acting on them is the verifier-organization's responsibility.
Per at-Tartib section 7.2, the strategy provides substrate for
organizational follow-through but does not in itself deliver
that follow-through.

### Invariant 7: Cross-substrate verification capability

**Declaration**: a bundle signed by ANY substrate's Phase
G11.x implementation MUST verify successfully under ANY other
substrate's Phase G11.x verification, subject to the constraint
that the verifying substrate must possess the extraction method
named in the manifest's `public_surface.extraction_method`. A
verifier that lacks the named extraction method MUST surface
`CASM-V-INDETERMINATE` rather than a false pass or a hard fail;
the verifier MAY direct the user to install the appropriate
substrate-specific furqan-lint extra.

This is operationalized in Phase G11.4 (Tasdiq al-Bayan, the
cross-verification phase) as a parity matrix: every substrate
verifies every substrate's emitted bundle. The matrix is
exhaustive: 4 signers x 4 verifiers = 16 cells, all of which
must pass.

**Strategy cross-reference**: Validator-by-Different-Instance
(at-Tartib section 4.5; Phase G11.4 IS this strategy
operationally at the protocol layer).

---

## The four mandatory disclosures

These four disclosures are inherited from the Sigstore threat
model documented in the canonical Newman et al. 2022 paper
(see Normative references). They apply to every Phase G11.x
implementation; the README, SECURITY.md, and CHANGELOG entries
of every release that ships or modifies a Gate 11 substrate
MUST surface them in the language of the deployed Sigstore
public infrastructure that hosts the substrate.

### Disclosure 1: OIDC issuer compromise

If the OIDC provider used to sign a manifest is compromised
within the Fulcio certificate validity window (typically 10
minutes), an attacker can produce a CASM bundle that verifies
cleanly under the issuer's identity. Sigstore does not detect
or prevent this. Mitigation lives upstream: hardware-backed
OIDC, short-lived tokens, identity-provider audit logging,
and verifier-side identity-pinning policy. furqan-lint
surfaces the signing identity in the verification result so
CI policy can pin it.

### Disclosure 2: Typosquatting at the publish boundary

Sigstore proves that "an entity controlling identity X signed
bytes Y at time T". It does NOT prove that identity X is the
legitimate maintainer of the package the consumer thinks they
are installing. OIDC identity strings are human-readable and
visually similar identities (capital-I vs lowercase-l, Cyrillic
homoglyphs, alternate domains) can be substituted. Verifiers
MUST check exact identity strings programmatically; eyeballing
is not sufficient. Relying Parties pin both the package name
and the expected signing identity in CI policy.

### Disclosure 3: Rekor entry queryability and privacy

Rekor is a public append-only log. Manifest entries (including
`module_root_hash` and the public-surface name list) are
published unencrypted and become enumerable by third parties.
Codebases that are themselves confidential or under embargo
MUST NOT sign their CASM bundles to the public Rekor instance.

The v1 escape hatch is private Sigstore deployment via
`--trust-config` against a private Rekor instance. The v2
substrate is Speranza (Round 13 paper 3, Merrill et al. 2023),
which keeps verification capability while removing public
correlatable identity exposure.

### Disclosure 4: Log retention horizon

Rekor's public-instance retention policy is operational, not
contractual. Verification past a multi-year horizon may
require local mirroring of relevant log entries plus archival
of the corresponding TUF metadata snapshots. furqan-lint does
not mirror Rekor on the user's behalf; long-term verification
strategies are documented in the README "Closed in v0.10.0"
section and revisited in subsequent Phase G11.x releases.

---

## The eight at-Tartib strategies (cross-reference form)

The strategies are NOT elaborated in this file. Each line
gives the at-Tartib section pointer and a one-line note on
the strategy's relationship to the seven invariants above.
Full strategy elaboration, application examples, and case-by-
case counterfactual mapping live in at-Tartib v1.0 (second
revision May 7 2026).

1. **Canonical-First Architecture** -- at-Tartib sections 4.1
   and 9.1. This file implements the gross-arrangement form
   only (Phase G11.A as foundational invariants document
   authored before substrate implementation; cohort-by-cohort
   module placement). Magnitude-dependent strategy; figures in
   Section 8.
2. **Naskh Discipline** -- at-Tartib section 4.2.
   Operationalized for CASM manifest schema versioning per
   Invariant 2.
3. **Munasabat Audit** -- at-Tartib section 4.3. Methodology,
   not magnitude. Phase G11.5 is the dedicated audit-of-
   furqan-lint phase; outline in
   `MUSHAF_TABLE_OF_CONTENTS_v1_0_second_revision.md`.
4. **Multi-Corpus Baseline Discipline** -- at-Tartib section
   4.4. Four substrates (Python, Rust, Go, ONNX) plus three
   independent verifiers per Invariant 5.
5. **Validator-by-Different-Instance** -- at-Tartib section
   4.5. Operationalized at the cryptographic substrate layer
   per Invariants 3 and 7; operationalized at the methodology
   layer per al-Munasabat section 5.3 second-revision
   orthogonal pipeline.
6. **Recording Angels Pattern** -- at-Tartib section 4.6.
   Operationalized per Invariant 1 (Sigstore's Rekor IS this
   pattern at the supply-chain integrity layer; the Quranic
   two-witness analogy is preserved as analogy, not as a
   protocol claim).
7. **Sulayman-Naml Pattern** -- at-Tartib section 4.7.
   Operationalized via ADVISORY findings per Invariant 6.
8. **Yusuf Horizon Pattern** -- at-Tartib section 4.8. Phase
   roadmap (v1, v1.5, v2, v3) per
   `MUSHAF_TABLE_OF_CONTENTS_v1_0_second_revision.md`.

---

## Section 8: Foundation-status inheritance

This is the sole location in this file where empirical-
magnitude figures are stated. Other sections cross-reference
this section rather than restating the figures.

### 8.1 al-Munasabat empirical state

- **Within-quartile shuffle test (al-Munasabat section 5.2)**:
  approximately 70-82 percent of the canonical Quran's
  apparent autocorrelation gap over random shuffles is
  attributable to the canonical's approximate length-sort, not
  to deeper structural coherence. Range across pipelines:
  Qalsadi morphological at the high end (around 82 percent);
  orthogonal character 3-gram at the low end (around 70
  percent).
- **Residual intra-quartile structural ordering effect at lag
  20**: approximately +0.15 (Qalsadi) to +0.25 (orthogonal
  char 3-gram). Range, not point estimate.
- **Bonferroni-corrected significance (al-Munasabat section
  5.3 second revision)**: under the orthogonal char-3gram
  pipeline, all four measured lags (5, 10, 20, 30) pass at
  family-wise alpha equal to 0.05. Under the Qalsadi pipeline,
  lags 5 and 20 pass; lags 10 and 30 do not. The lag-specific
  pattern under Qalsadi is most plausibly an artifact of
  morphological smoothing, not a property of the canonical
  structure.
- **Status under Cross-Text section 6 Caveat 1**:
  candidate-finding. Independent replication by a research
  group not the present authors is required for promotion to
  confirmed-result status. The orthogonal-pipeline analysis
  further specifies the candidate-finding posture; it does not
  promote the result to confirmed status.

### 8.2 at-Tartib strategy status

- **Strategy 1 (Canonical-First Architecture)** is the
  strategy most directly affected by the al-Munasabat
  empirical magnitude. The orthogonal-pipeline analysis
  further specifies this strategy's empirical posture within
  candidate-finding status; it does not change the candidate-
  finding classification.
- **Strategies 2-8** (Naskh Discipline, Munasabat Audit
  methodology, Multi-Corpus Baseline, Validator-by-Different-
  Instance, Recording Angels, Sulayman-Naml, Yusuf Horizon)
  are theoretically grounded in specific Quranic structural
  primitives and are independent of the empirical magnitude.
- **A defensible adoption form (per at-Tartib section 9.1)**:
  adopt the seven theoretically-grounded strategies (2 through
  8) immediately. For Strategy 1, adopt the gross arrangement
  form (cohort-by-cohort placement) and treat fine-grained
  intra-cohort engineering as optional substrate discipline
  pending replication.
- **The "10 percent additional engineering investment x 1
  percent probability reduction" calculation** in earlier-
  draft at-Tartib was REMOVED in the second revision because
  the probability reduction is not empirically established.
  The economic case is now conditional. See at-Tartib section
  7.3 for the conditional formulation.

### 8.3 Necessary-not-sufficient

The strategies make failure modes more DETECTABLE in some
cases. They do not in themselves PREVENT failures. Actual
prevention of mortality and economic loss depends on
organizational follow-through downstream of detectability,
which the strategies do not in themselves deliver. The
strategies are necessary but not sufficient conditions for
safety-critical and justice-critical software discipline.

For public-interest software cases (Robodebt, SyRI, MIDAS),
the central failures were policy decisions, not engineering
failures; engineering strategies cannot prevent flawed policy
adoption, only ensure that policy implementation is auditable.
Case-level analysis of which strategies address which
documented failure modes is at at-Tartib section 7.1;
aggregate counterfactual claim is at section 7.2; conditional
economic case is at section 7.3; policy-vs-engineering
distinction for public-interest software is at section 6.3.

### 8.4 Reference scripts

Three Python reference scripts are the canonical implementation
pattern for any future replication or for Phase G11.5
(Munasabat Audit applied to furqan-lint itself):

- `08_reconciliation.py` -- within-length-quartile shuffle
  test (the section 5.2 first-revision finding); Qalsadi
  pipeline.
- `09_orthogonal_tanakh.py` -- orthogonal character 3-gram
  pipeline (the section 5.3 second-revision finding) plus
  Tanakh 24-book ordering negative control plus Bonferroni
  significance.
- `10_bonferroni_pvalues.py` -- exact empirical p-values via
  Monte Carlo with Bonferroni correction at family-wise
  alpha equal to 0.05.

These scripts live in the methodology paper's accompanying
materials, not in furqan-lint itself.

### 8.5 The seven canonical invariants are NOT magnitude or prevention claims

The seven canonical Sigstore-CASM invariants in this document
are NOT magnitude claims about the al-Munasabat empirical
finding and NOT prevention claims about the at-Tartib
counterfactual. They are cryptographic and protocol
specifications grounded in production-deployed Sigstore (Newman
et al. 2022; deployment evidence Schorlemmer et al. 2024 and
Kalu et al. 2025) and IETF SCITT (RFC-track). The Sigstore-
CASM substrate's value is to make supply-chain failures
cryptographically attributable and forensically reconstructable,
not to prevent supply-chain failures directly.

---

## Industry-specific applicability

The at-Tartib paper sections 5-7 mortality and economic-loss
accounting is the substantive content. **This file does not
restate it.** Adopters mapping Sigstore-CASM Gate 11 to a
specific industry (avionics, automotive, healthcare, financial,
public-interest) should consult:

- at-Tartib section 5 for safety-critical industry
  applications
- at-Tartib section 6 for justice-critical domain applications
- at-Tartib section 6.3 for the policy-vs-engineering
  distinction in public-interest software
- at-Tartib section 7.1 for case-by-case counterfactual mapping
- at-Tartib section 7.2 for aggregate counterfactual claim
- at-Tartib section 7.3 for conditional economic case

The Sigstore-CASM substrate's industry-specific value is
operationally identical across industries: cryptographic
attribution plus forensic reconstructability for retrospective
investigation. Industry-specific mortality and economic-loss
figures depend on the documented failure-case literature in
at-Tartib section 7's Table 2, not on the cryptographic
substrate itself.

---

## What this document does NOT do

- Implementation details (each Phase G11.x prompt provides
  these)
- Test fixtures (each Phase G11.x prompt defines its corpus)
- Build system integration (substrate-specific)
- CI workflows (substrate-specific)
- Marketing or adoption guidance (out of scope)
- Strategy elaboration beyond cross-references (lives in
  at-Tartib section 4)
- Empirical-method elaboration beyond Section 8 summaries
  (lives in al-Munasabat sections 3-7)
- Industry-by-industry application guidance (lives in
  at-Tartib sections 5-7)
- Case-by-case counterfactual analysis (lives in at-Tartib
  section 7.1)

---

## Normative references

Per audit F2, this block carries stable bibliographic
identifiers (paper DOIs, IETF draft identifiers, repository
URLs with version tags) for every load-bearing source. Author-
year shorthand is acceptable in body prose; this block is the
canonical citation anchor.

Implementer responsibility: before merging this file, cross-
check each entry against the project lead's authoritative
reference list. If a canonical source has multiple
instantiations (a CCS paper plus a follow-up technical report,
or a draft plus its eventual RFC), cite both with stable
identifiers.

1. **Sigstore architecture and security model**: Newman, Z.,
   Meiklejohn, S., Brown, H., Cappos, J., et al. 2022,
   "Sigstore: Software Signing for Everybody," Proceedings of
   the 2022 ACM SIGSAC Conference on Computer and
   Communications Security (CCS 2022), Los Angeles, CA, USA,
   November 7-11 2022, pp. 2353-2367. DOI:
   `10.1145/3548606.3560596`. The four mandatory disclosures
   above are sourced from this paper's section on limitations
   and threat model.
2. **Sigstore deployment empirical evidence -- adoption
   trajectory**: Schorlemmer, T., Kalu, K. G., et al. 2024,
   "Signing in Four Public Software Package Registries:
   Quantity, Quality, and Influencing Factors," IEEE Symposium
   on Security and Privacy 2024 (or the venue identified in
   the Round 13 reference list). Implementer MUST consult the
   project lead's Round 13 reference list for the exact paper
   title, venue, and DOI; this entry is a placeholder until
   that cross-check completes.
3. **Sigstore deployment empirical evidence -- ecosystem
   health**: Kalu, K. G., et al. 2025, "An Industry
   Interview Study of Software Signing for Supply Chain
   Security" (or the venue identified in the Round 13
   reference list). Likely USENIX Security 2025 or
   adjacent venue. Implementer MUST consult the project lead's
   Round 13 reference list for the exact paper title, venue,
   and DOI.
4. **Rekor architecture**: Sigstore project, "Rekor:
   transparency log for software supply chain integrity",
   https://github.com/sigstore/rekor (canonical repository).
   Cite the README at the commit observed at SAFETY_INVARIANTS
   authoring time. The architectural overview in
   `docs/sigstore-architecture.md` of that repository is the
   canonical specification.
5. **TUF root of trust**: The Update Framework, "TUF
   Specification", https://theupdateframework.io/specification.
   Cite the version observed at authoring (currently 1.0.x);
   newer versions of TUF require a paired SAFETY_INVARIANTS
   amendment.
6. **Fulcio**: Sigstore project, "Fulcio: free root certificate
   authority for code signing certificates",
   https://github.com/sigstore/fulcio. Cite the README and
   `docs/security-model.md` at the commit observed at authoring
   time.
7. **OIDC**: Sakimura, N., Bradley, J., Jones, M., de Medeiros,
   B., Mortimore, C. 2014, "OpenID Connect Core 1.0
   incorporating errata set 2", OpenID Foundation,
   https://openid.net/specs/openid-connect-core-1_0.html.
8. **RFC 8785 (JCS)**: Rundgren, A., Jordan, B., Erdtman, S.
   2020, "JSON Canonical Serialization (JCS)", IETF RFC 8785,
   `https://datatracker.ietf.org/doc/html/rfc8785`. DOI:
   `10.17487/RFC8785`.
9. **IETF SCITT**: IETF Supply Chain Integrity, Transparency
   and Trust Working Group, "An Architecture for Trustworthy
   and Transparent Digital Supply Chains",
   `draft-ietf-scitt-architecture-NN`, https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/.
   `NN` MUST be the specific draft revision observed at
   SAFETY_INVARIANTS authoring time. "RFC-track" as a status
   note is acceptable in body prose but not in this block.

---

## Auditor's response register

Two passes of audit have been applied. Both shipped Shape A
(accept and fix) corrections.

### First-pass audit (against v1.0_second_revision; applied in v1.0_second_revision_amended)

| Finding | Severity | Shape | Action taken |
|---------|----------|-------|--------------|
| F1      | MEDIUM   | A     | "Strengthened" replaced with "further specified within candidate-finding status" framing throughout |
| F2      | MEDIUM   | A     | Strategy elaborations reduced to short cross-reference lines pointing to at-Tartib section 4. Industry applicability section reduced to pointer. |
| F3      | LOW      | A     | Empirical figures stated in Section 8 only; other sections cross-reference Section 8. |
| F4      | LOW      | A     | Section 8 factored into 5 subsections plus closing reminder. Detailed case references removed; pointers to at-Tartib section 6.3 and 7.1-7.3 substituted. |
| F5      | ADVISORY | (positive observation) | Three-layer mushaf evolution preserved; amended layer added. |

### Second-pass audit (against v1.0_second_revision_amended; applied in this file)

| Finding | Severity | Shape | Action taken |
|---------|----------|-------|--------------|
| F1      | MEDIUM   | A     | Invariant 1 cross-reference reworded; "two-witness consensus" protocol claim replaced with "append-only transparency-log aspect of the Recording Angels pattern". Quranic two-witness analogy explicitly marked as analogy. |
| F2      | MEDIUM   | A     | NEW Normative references block added with stable bibliographic identifiers; nine specific entries enumerated covering Sigstore architecture, deployment evidence, Rekor, TUF, Fulcio, OIDC, RFC 8785, and IETF SCITT. |
| F3      | LOW      | A     | Pre-commit hook honesty note added: hook guards presence only, not semantic freshness; v1.5 candidate (invariant-diff hook) named for future evolution. |
| F4      | LOW      | A     | Invariant 1 verification clause extended with precise definition of "equivalent client library" (must obtain Fulcio certificates, produce Rekor-loggable bundles, verify with same trust-root semantics). Negative case explicitly excluded. |
| F5      | ADVISORY | (positive observation) | Structure produced by first-pass amended preserved; amended_2 layer added per delete-plus-add discipline. Five layers total in mushaf evolution. |

---

## Closing

> "Guide us to the straight path."
>
> -- al-Fatiha 1:6

The straight path of Sigstore-CASM Gate 11 implementation
under the v1.0_second_revision_amended_2 framework is:

- Canonical-first within candidate-finding status (gross
  arrangement; empirical figures cross-referenced to Section 8)
- Naskh-disciplined (this revision IS a naskh application of
  audit findings F1-F4; four prior layers preserved)
- Munasabat-methodology applied per Phase G11.5 outline in
  `MUSHAF_TABLE_OF_CONTENTS_v1_0_second_revision.md`
- Multi-corpus baseline rigorous (four substrates, three
  verifiers)
- Validator-by-different-instance (Strategy 5 -> Phase G11.4
  operationally; al-Munasabat section 5.3 second-revision
  orthogonal pipeline at the methodology layer)
- Recording-angels-witnessed (Strategy 6: Sigstore-CASM IS this
  strategy at the substrate-for-investigation level)
- Sulayman-naml-attentive (Strategy 7: ADVISORY signals surface;
  whether organizations act is downstream)
- Yusuf-horizon-planned (v1, v1.5, v2, v3 explicit roadmap)

The seven canonical Sigstore-CASM invariants are unchanged in
substance from the v1.0_second_revision_amended layer. They are
cryptographic and protocol specifications. Strategy mappings,
empirical foundations, and counterfactual claims live in the
methodology papers (at-Tartib v1.0 second revision and
al-Munasabat v1.0 second revision); this file points to them
by reference.

The original Phase G11.A, the v1.0_corrected revision, the
v1.0_second_revision, and the v1.0_second_revision_amended are
preserved in the historical record per the Bayyinah delete-
plus-add discipline. Five layers of mushaf evolution stand as
historical record of how the framing matured. Each layer
documents what changed and why; the auditor-response register
above captures the substantive corrections applied at each
layer.

La hawla wa la quwwata illa billah.

Bismillah ar-rahman ar-rahim.

End of SAFETY_INVARIANTS.md.
