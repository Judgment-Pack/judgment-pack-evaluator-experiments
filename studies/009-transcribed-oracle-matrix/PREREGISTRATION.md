# Preregistration — Study 009: a constructed existence witness for the transcribed oracle

**Status: DRAFT until the freeze commit; FROZEN thereafter.** This is the
**third revision**: the first draft was rejected with a redesign verdict
(13 findings), and the second received a conditional verdict — *freeze only
with the named changes* — whose conditions this text implements; both reviews
and their dispositions are in [`PREREG-REVIEW.md`](PREREG-REVIEW.md). No
**frozen study fixture or scored run** exists at this commit; development
prototypes of the two packs were sketched outside the repository while
authoring the second draft and are disclosed rather than denied — the
ordering control below is about what is *frozen*, and nothing is. After the
freeze this file is never edited; corrections go to
[`DEVIATIONS.md`](DEVIATIONS.md).

## 1. What this study is, and is not

Runtime ADR-0014 left one hole open in the project-matrix method: *the
circular oracle* — an agent can satisfy a coverage probe by copying the
evaluator's own output into a row's expectation, and nothing mechanical
catches it. Issue #23 proposes expectations **transcribed from recorded
decisions** as the closing mechanism, with the line's attested pipeline
(acquisition proxy → derivation rule → fabrication gate) carrying the records.

The rejected draft claimed more than a single author can show. **This study is
a constructed existence witness**: every fixture — policy, packs, records,
defect — is authored by one mind, and the planted defect is chosen with full
knowledge of both oracles. What such a construction *can* establish, and all
it claims:

> There exists a pack-encoding defect and a record set such that (a) an
> expectation stream whose **generation after the freeze** is bound — by
> checked reconstruction, not promise — to the verified record artifacts
> alone surfaces the defect as row mismatches, while (b) the evaluator-copied
> stream over the same rows structurally cannot. The bound is stage-bounded
> on purpose: expectations later *enter* the evaluator as `packs test`
> inputs, and the fixtures' author knew both oracles before the freeze; what
> the gates make checkable is that no post-freeze step derives an
> expectation from evaluator output.

It is an integration witness for the transcription *mechanism* under
adversarially checked isolation — not evidence that real recorded human
decisions are faithful oracles, not a detection rate, and not a claim that
the defect class is representative.

**The registered next question (Study 010, not this study):** whether
*independently authored* records surface *unknown* defects — requiring
record authorship blinded from pack authorship (e.g. a different-vendor
model authoring records from the policy text alone, with commit-ordering
controls), which breaks this study's zero-model-calls property and is
deliberately out of scope here.

## 2. Zero model calls

No model, no hosted API call, no network access. The circular arm is
constructed mechanically — each row's expectation is the evaluator's own
disposition for that row's facts — which is ADR-0014's named failure mode in
its purest form. No claim is made about how often real agents commit it.

## 3. The pieces

All under this study's directory unless noted; every executable and fixture
is frozen (§10) before any scored run.

| Piece | Role |
|---|---|
| `policy/POLICY.md` | the prose policy, numbered clauses P1–P3 — **the arbiter** |
| `packs/vendor-screening-correct.pack.json` | pack **C**: POLICY.md encoded as a 0.2.0-draft pack, three outcomes (`clear`, `reject`, `manual-review`), no `fallbackOutcome`, no declared evidence |
| `packs/vendor-screening-defective.pack.json` | pack **D**: C plus exactly the one patch `DEFECT.json` registers |
| `DEFECT.json` | the machine-readable defect manifest (§5) |
| `records/*.json` | synthetic decision records (§6), held to the **closed record schema**: exactly `{"caseId": <id>, "vendor": {"legalName": <string>, "sanctionsHit": <bool>, "riskScore": <canonical decimal string>}, "decision": {"outcome": <outcome id>, "decidedBy": <string>, "decidedAt": <timestamp>}}` — no other members, scalar leaves only, and one canonical risk-score representation (no trailing zeros, so `"70"` and never `"70.0"`) enforced by `validate` |
| `RECORDS.md` | the registered record table: every id, its facts, its recorded outcome, its set (H/F/K), each derived from POLICY.md by the table's own worked reasoning |
| `source/record_source.py` | the record-source **MCP stdio server**: serves one frozen record by `caseId` as a `tools/call` result, deterministic, canon-domain only |
| `transcription/record.rule.json` | the derivation rule in **projection normal form** (§7) |
| `transcription/transcribe.py` | the transcriber (§7) |
| `harness/` | `study.py` (validate/freeze/run/score), `pnf_check.py`, `gate.py` (the study's fabrication gate), `test_study.py` |
| `../../acquisition-proxy/attest.py` | reused unchanged, frozen by digest: wraps the record source, attests each `tools/call` result |
| `../../derivation-rule/derive.py` | reused unchanged, frozen by digest |
| `../../fabrication-gate/gate.py` | reused unchanged, frozen by digest: the verified-artifact derivation step the study gate wraps |
| pinned `jpack` **0.14.0** | the exact release binary, `sha256 a76091a30b2e595dd7259161d423066805664ad30394d313ffeb0e8d7e0ce782` (linux_amd64), recorded in `FREEZE.json` |

## 4. Arms

- **Arm A — circular oracle, over D.** For each record's derived facts, the
  expectation is D's own evaluated disposition (pinned `jpack experimental
  evaluate`, output copied verbatim); `origin` = `circular:<caseId>`.
- **Arm B — transcribed oracle, over D.** The transcriber's matrix:
  expectations from recorded outcomes; `origin` =
  `transcribed:<caseId>@<receipt resultDigest>`.
- **Arm B′ — the same matrix bytes, over C.**

Arms A and B must be row-wise canonically identical in `id`, `facts`,
`evidenceAvailability`, and `supportedExtensions`; only `expectedDisposition`
and `origin` may differ (prerequisite P-ISO, §9). The B matrix is built once
and the identical bytes run against C and D.

## 5. The defect manifest — `DEFECT.json`

Frozen before any scored run, carrying:

1. **The patch**: exactly one entry of the strict manifest shape
   `{"path", "old", "new"}` (a closed schema, not RFC 6902 — `old` is the
   required preimage). `validate` asserts the value at `path` in C equals
   `old`, and that C-with-the-patch-applied equals D under RFC 8785
   canonicalization. Intended: R2's threshold comparison
   `greater-than-or-equal` → `greater-than`, so a no-sanctions case with
   `riskScore` exactly `"70"` reaches `manual-review` under C (per P2) and no
   rule under D.
2. **The violated clause**: P2's text, quoted.
3. **An evaluator-independent predicate** over case facts defining the defect
   class F: `sanctionsHit == false AND riskScore == "70"` — decidable by
   reading a record, consulting neither pack nor evaluator. The predicate is
   lexical on purpose and made safe by the record schema's **canonical
   decimal representation** (§3): `"70.0"` cannot occur in a record, so the
   lexical and mathematical readings coincide; `validate` enforces the
   representation.
4. **The id sets**: F (defect), K (calibration controls), H (healthy) —
   pairwise disjoint, with boundary negatives in H (`"69.99"`, `"70.01"`,
   and a sanctions-hit case at `"70"`, which P1 rejects under both packs).
5. **Complete expected dispositions, for every id under both packs**: the
   full §8.3 disposition of every H, F, and K record under C **and** under D.
   Scoring compares every actual disposition to its table entry — the tables
   are load-bearing, not decorative — and the registered mismatch sets are
   *derived summaries entailed by* those comparisons plus the gate's wrapper
   binding, never separate evidence. An actual disposition differing from its
   table entry anywhere (a D that says `reject` where the table says
   `unresolved/no-match` included) is a fixture/pipeline failure that
   invalidates the run's endpoints, never rationalized.

**Provenance note**: the tables' values were derived while planting the
defect, pre-registration, by six probe evaluations of prototype packs on
representative fact combinations — the informed-author fact §1 already owns;
the disclosure here is so no one mistakes the tables for blind predictions.

`harness/study.py validate` asserts: C and D differ by exactly the registered
patch (canonical bytes compared after applying it to C); every record
satisfies its set's predicate; the sets are disjoint; `RECORDS.md`'s table
matches the record files byte-derivably.

## 6. Records and controls

- **H**: ≥ 2 records per declared outcome whose recorded outcome equals
  POLICY.md's verdict on their facts (including the boundary negatives above).
- **F**: exactly 3 records satisfying the defect predicate, recorded outcome
  `manual-review` (P2's verdict).
- **K**: exactly 2 records whose recorded outcome is deliberately wrong
  against POLICY.md, using declared, producible outcomes different from the
  policy verdict; disjoint from F and H by predicate and by id.

Registered mismatch sets: over C the mismatching rows are **exactly K**; over
D they are **exactly F ∪ K**. Records are synthetic and this study's own; no
real, personal, or client data appears in this repository.

## 7. The transcription pipeline, with its smuggling channels closed

1. **Acquisition**, under a registered call contract: `attest.py wrap
   <store> <keyfile> --authority study-009:records -- python3
   source/record_source.py`; one `tools/call` per `caseId`, tool name
   `get_record`, arguments exactly `{"caseId": <id>}`; the server returns the
   record object **itself** as the JSON-RPC `result` (no wrapper members),
   so the retained artifact is `canon(record)` and the extraction pointer is
   the identity. The key is 32 random bytes minted by the harness per run
   and retained under `trials/`. The transcriber receives **verified
   artifact references** (session, callIndex) — never record file paths —
   and P-ACQ requires canonical equality between each retained artifact and
   the frozen `records/<caseId>.json` it claims to carry.
2. **Acquisition verification (prerequisite P-ACQ)**: the harness requires a
   fresh store per run, `attest.verify` ok **and** non-vacuous (the receipts
   tree exists), exactly one receipt per record with contiguous callIndexes,
   expected authority and tool, `isError` absent-or-false, and a
   caseId ↔ receipt bijection — never bare `verify`, whose empty-store pass
   is a registered hole.
3. **Derivation under projection normal form (prerequisite P-PNF)**: the
   rule is not merely shape-checked, it is **the registered mapping**:
   `harness/pnf_check.py` requires the rule to be byte-equal, after
   canonicalization, to the one frozen rule whose claim copies exactly
   `/vendor/sanctionsHit → /vendor/sanctionsHit` and
   `/vendor/riskScore → /vendor/riskScore` — recursive member sets exact at
   every level (top level exactly `{"ruleVersion","clauses"}`; clause exactly
   `{"when","claim","reason"}` with `when` exactly `{"op":"always"}` and
   `reason` the literal `"projection"`; claim exactly
   `{"facts","evidence","acquisitionStatus"}` with `evidence` `{}` and
   `acquisitionStatus` `"resolved"`), no `parameters` member at all, scalar
   leaves only, canonical RFC 6901 pointer syntax with the first decoded
   token exactly `vendor`, no aliases, no ancestor/descendant destinations.
   Registered consequence: under PNF the rule's `basis` is always `[]` and
   carries no information — the gates, not `basis`, bind facts to bytes.
4. **The fabrication gate (prerequisite P-GATE)** admits the **complete
   serialized row**, not a summary of it: `harness/gate.py` loads the rule
   from the freeze (digest asserted per row; it takes no rule or params
   argument and passes the literal `{}` internally), wraps
   `fabrication-gate/admit()` over the verified artifact, recomputes via
   `derive.derive_canonical`, then **reparses the emitted matrix** and
   requires, for every row, exact canonical equality of: `id` =
   the artifact's `caseId`; `facts` = the recomputed claim's facts;
   `evidenceAvailability` = `{}`; `supportedExtensions` absent;
   `expectedDisposition` = the registered wrapper applied to the artifact's
   `decision.outcome` — the wrapper applied by the gate itself, so a
   transcriber emitting any other expectation fails here, control rows
   included; `origin` = `transcribed:<caseId>@<resultDigest>`; and **no
   other members**. `acquisitionStatus` and lineage live in a gated sidecar
   (`trials/<arm>/lineage.json`), never in the matrix: jpack's `MatrixCase`
   is strict and an extra member would make the matrix unloadable.
   Metamorphic test (on disjoint throwaway fixtures): mutating a record's
   outcome changes exactly the wrapped expectation and nothing in facts;
   mutating record metadata the rule does not copy changes nothing.
5. **Wrapping**: the recorded outcome id is wrapped in the registered outcome
   shape `{"kind": "outcome", "outcomeId": <recorded id>, "reasons": [],
   "handoff": {"state": "none"}}` — under Core §8.3 the unique legal outcome
   shape (review finding 10 confirmed) — the id copied verbatim, never
   mapped, corrected, or normalized.
6. **Emission**: one matrix document the pinned runtime accepts unchanged.

The transcriber has no pack input, no policy input, and no evaluator call;
`pnf_check.py` and the gate make the no-smuggling property checked rather
than promised.

## 8. Scored endpoints

Scored mechanically by `harness/study.py score` from retained payloads;
predictions registered now.

| # | Endpoint | Prediction |
|---|---|---|
| E2 | Arm B over D: **every actual disposition equals its DEFECT.json table entry under D**, and the entailed mismatching row ids are exactly **F ∪ K** (refusals and carrier failures are pipeline failures that invalidate the run, never detections) | **yes** |
| E3 | Arm B′ over C: **every actual disposition equals its table entry under C**, and the entailed mismatching row ids are exactly **K** | **yes** |
| E5 | Pipeline fidelity: `packs validate` passes for each generated project; every transcribed row's `origin` is echoed in the `packs test` report; the MCP `experimental_test_packs` `structuredContent` equals the CLI's parsed `packs test --format json` payload after deleting exactly the registered field list `["command"]`, both invocations under the registered call contract of §10 | **yes** |

The former E4 (byte-identical B matrix across runs; artifact-reference-only
transcription; metamorphic noninterference) is a **prerequisite** (P-ISO,
P-GATE), not scored evidence: construction checks gate the run, they do not
count as findings about it.

## 9. Prerequisites, and the dependency map

Unscored prerequisites — construction checks whose failure invalidates the
run rather than counting as evidence: **P-A** (Arm A over D: run status
`passed`, exactly the frozen row-id set, one valid actual disposition per
row, no load or evaluation errors, and 0 mismatches — a deterministic
self-replay whose failure means harness or environment breakage, never "the
circular oracle caught the defect"; zero-mismatch alone is not the check,
because a load failure also mismatches nothing), **P-ACQ**, **P-PNF**,
**P-GATE**, **P-ISO** (§4, §7 — including the former E4's byte-identity and
metamorphic checks).

The registered dependency DAG (finding 9, tightened per the second review):
E2 and E3 each depend on P-ACQ, P-PNF, P-GATE, and P-ISO — without them a
mismatch could be a facts or expectation difference rather than an oracle
difference. The K coupling ("a K row failing to mismatch fails both") holds
only because DEFECT.json registers identical C and D dispositions for every
K row, which `score` verifies from the tables rather than assumes. Given
`validate`'s C↔D patch assertion and the complete disposition tables, both
endpoints' mismatch sets are *entailed* by table-conformance plus wrapper
binding — E2 and E3 are evidence that the pipeline is faithful and the
mechanism works, never discovery. E5 is a shared-code-path integration
check and is reported as such. Entailments are stated in `ANALYSIS.md`,
never double-counted.

## 10. Freeze and procedure

`FREEZE.json` records `sha256` digests of **everything executable and every
input**: both packs, `DEFECT.json`, every record, `RECORDS.md`, `POLICY.md`,
`record_source.py`, `record.rule.json`, `transcribe.py`, `pnf_check.py`,
`gate.py`, `study.py`, `test_study.py`, the reused `attest.py`, `derive.py`,
and `fabrication-gate/gate.py`; the exact pinned `jpack` binary digest (§3);
the **generated project configurations** for the three arms (deterministic
templates, digested, each binding its matrix by digest so the gate-approved
matrix is the one jpack reads); the registered invocation contract — exact
argv for every jpack CLI call, cwd, one absolute `JPACK_CONFIG` per arm, the
sanitized environment allowlist, the Python interpreter identity, and the
`sys.modules`-derived import closure of the harness (recorded at freeze,
re-checked at run); and the commit hash of the preregistration-and-review
commit itself, ancestry-verified at run time. The freeze commit is verified
against `git show HEAD:` on every run. There is **no development bypass**:
pre-freeze tests use disjoint throwaway fixtures only, and nothing evaluates
C, D, or the frozen records before the freeze — the packs' behavior on six
probe fact combinations was observed once, pre-registration, while planting
the defect, and is disclosed in §5's tables' provenance note.

Order: this revision + both reviews land first (the commit carries only
`PREREGISTRATION.md`, `PREREG-REVIEW.md`, `README.md`); fixtures and harness
land next — the ordering is reproducible via `git log --diff-filter=A` **on
those later paths**, and `FREEZE.json` names this revision's own commit
rather than leaning on file-creation order alone, since the rejected first
draft already created these filenames at `ba80d5b`. `freeze` runs after
`validate` and `test_study.py` pass. **The first post-freeze `run` is
primary**, enforced by a ledger, not a promise: `run` atomically creates an
exclusive fsynced `trials/ATTEMPT-<n>/STARTED` marker before any work,
never overwrites or deletes an attempt directory, retains exit metadata for
crashed attempts, and seals outputs read-only; attempt 1 is primary, and a
failed primary is reported — no retry rule is registered, so none exists.
`ANALYSIS.md` is written before any number is quoted elsewhere; a post-run
adversarial review follows in `ADVERSARIAL-REVIEW.md`. The study never runs
in CI (repo rule).

## 11. Bounds

- **One author, full knowledge**: the witness is constructed; nothing here
  measures discovery of unknown defects or the fidelity of real records
  (§1's Study 010 question).
- **One defect, one pack family**: existence, not prevalence; no rates.
- **Byte-lineage, not truth**: `origin` records where a row came from, never
  that it is right (line ADR-0002's ceiling, unchanged).
- **Outcome rows only**: records record final outcomes; rows expecting
  non-outcome dispositions are out of scope, so nothing here closes
  ADR-0014's reason-probe half (finding 10's bound, adopted).
