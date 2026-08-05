# Preregistration — Study 009: transcribed-oracle matrix

**Status: DRAFT — NOT FROZEN. The pre-freeze adversarial review returned
"redesign" with thirteen findings ([`PREREG-REVIEW.md`](PREREG-REVIEW.md)); this
text is retained as the reviewed draft and will be superseded by a revision
before anything freezes.** Written before the Study 009 transcriber, fixtures,
harness, or result exists or runs — none of which exist at this commit.
Deviations from a frozen version would go to [`DEVIATIONS.md`](DEVIATIONS.md),
never into this file.

## 1. Why this study exists

Runtime ADR-0014 closed the coverage layer of a project matrix — a derived report says which
declared outcomes and reachable reasons no row probes — and named the hole that remains open:

> an agent can satisfy a probe by copying the evaluator's own output into an expectation — the
> circular oracle. Coverage forces the row to exist; the arbiter rule in the `test_pack` prompt
> governs what it may contain; nothing mechanical closes the remainder.

Issue Judgment-Pack/judgment-pack-evaluator-experiments#23 proposes the thing that could close it:
expectations transcribed from **recorded decisions** — a request and the outcome a human actually
reached — rather than authored by the same kind of mind that wrote the pack. The transcriber is the
last step past three components this line already built: the acquisition proxy attests record
bytes, the portable derivation rule turns attested bytes into facts by a checkable rule, and the
fabrication gate makes derived input the only input.

Study 009 asks one question:

> Does a matrix whose expectations were transcribed from recorded outcomes catch a pack-encoding
> defect that the circular oracle — expectations copied from the evaluator's own output —
> structurally cannot?

## 2. Zero model calls

Study 009 runs **no model, no hosted API call, and no network access**. The "agent-authored"
arm is the circular oracle in its purest form, constructed mechanically: each row's expectation is
the evaluator's own disposition for that row's facts. That is not a caricature — it is the exact
failure mode ADR-0014 names, stripped of the prompt discipline that sometimes prevents it. No
claim is made about how often real agents commit it; the study measures what the oracle can and
cannot see once committed.

## 3. The pieces

All authored inside this study and frozen before the first scored run, except the reused line
components and the pinned runtime.

| Piece | Role |
|---|---|
| `policy/POLICY.md` | the prose policy — **the arbiter**. Every other artifact is checked against this text. |
| `packs/screening-correct.pack.json` | pack **C**: the prose policy encoded as a 0.2.0-draft pack |
| `packs/screening-defective.pack.json` | pack **D**: byte-identical to C except **one registered encoding defect** ([`DEFECT.md`](DEFECT.md)) |
| `records/*.json` | synthetic decision records: raw case bytes + the outcome the (synthetic) reviewer reached, derived from `POLICY.md` by the table in [`RECORDS.md`](RECORDS.md) |
| `transcription/transcribe.py` | the transcriber under study |
| `transcription/record.rule.json` | the derivation rule (this line's `derivation-rule/` format) that maps attested record bytes to a facts document |
| `../../acquisition-proxy/attest.py` | reused unchanged: attests each record's bytes, receipt + content-addressed retention |
| `../../derivation-rule/derive.py` | reused unchanged: evaluates `record.rule.json` over attested bytes |
| pinned `jpack` ≥ 0.14.0 | released binary, digest recorded in `FREEZE.json`; runs `packs validate`, `packs test`, and serves `experimental_test_packs` over MCP |

The defect in pack D is planted in the **encoding**, not the prose: `POLICY.md` stays the truth,
records follow `POLICY.md`, and D silently disagrees with both on one registered class of cases.
`DEFECT.md` registers, before the freeze: the edited condition, the class of case facts it
affects, and the exact record ids in that class.

## 4. The transcriber

`transcribe.py` implements the pipeline of issue #23, and nothing else:

1. each record's raw bytes are attested through the acquisition proxy (receipt, retention);
2. the **retained artifact bytes** — never the original file — are handed to `derive.py` under
   `record.rule.json`, producing the row's facts document and evidence availability;
3. the record's recorded outcome id is wrapped in the **registered outcome shape** —
   `{"kind": "outcome", "outcomeId": <recorded id>, "reasons": [], "handoff": {"state": "none"}}`
   — a fixed structural wrapping stated here once, never derived from the pack or the evaluator;
   the id itself is copied verbatim and never mapped, corrected, or normalized;
4. `origin` is stamped: `transcribed:<record id>@<receipt resultDigest>`;
5. rows are emitted as one matrix document the runtime accepts unchanged.

Two structural properties, held by construction and checked by the harness:

- **Transcription, never inference.** The transcriber has no pack input, no policy input, and no
  evaluator call. Its command line accepts records, a rule, and an output path — nothing else.
  A transcriber that could read the pack could reconcile a divergence away; this one cannot.
- **One matrix for every pack.** Because the transcriber never sees a pack, its output is
  byte-identical whichever pack it will be run against. The harness builds the matrix once and
  runs the same bytes against C and D.

## 5. Arms

- **Arm A — circular oracle, over pack D.** For each record's derived facts, the expectation is
  pack D's own evaluated disposition (via the pinned `jpack`, one `experimental evaluate` per
  row, output copied verbatim). `origin` is stamped `circular:<record id>`.
- **Arm B — transcribed oracle, over pack D.** The transcriber's matrix: same facts, expectations
  from the recorded outcomes.
- **Arm B′ — transcribed oracle, over pack C.** The same matrix bytes over the correct encoding.

Arms A and B share facts row for row and differ only in where the expectation came from, so any
difference in what `packs test` reports is attributable to the oracle.

## 6. Records and controls

`RECORDS.md` registers, before the freeze, a record set with at least:

- ≥ 2 records per declared outcome of pack C (every outcome witnessed);
- ≥ 3 records in the registered defect class (the rows that can catch D);
- exactly 2 **calibration controls**: records whose recorded outcome is deliberately wrong
  against `POLICY.md`, ids registered. These bound what a clean run can mean: a suite that
  cannot fail is not a suite, so the controls must produce divergences even over the correct
  pack C.

Records are synthetic and this study's own. The real-data question — whether an organization's
actual case files are faithful oracles — is **out of scope by design** (see §9).

## 7. Registered endpoints

Scored mechanically by `harness/score.py` from `packs test --format json` payloads; predictions
stated now.

| # | Endpoint | Prediction |
|---|---|---|
| E1 | Arm A over D: mismatched row count | **0** — the circular oracle cannot see the defect it was copied from |
| E2 | Arm B over D: every registered defect-class row mismatches, and every mismatching row is either defect-class or a calibration control | **yes** |
| E3 | Arm B′ over C: the mismatching rows are exactly the 2 calibration controls | **yes** |
| E4 | The transcriber's matrix bytes are identical for the C and D runs, and `transcribe.py` takes no pack or policy input (checked structurally by the harness) | **yes** |
| E5 | The transcribed matrix is accepted unchanged: `packs validate` passes for the project; every transcribed row's `origin` is echoed in the `packs test` report; the same suite runs over MCP `experimental_test_packs` with a payload equal to the CLI's modulo the `command` member | **yes** |

E1 together with E2 is the study's claim: on identical facts, the oracle that did not come from
the evaluator surfaces the encoding defect the evaluator-derived oracle structurally cannot.

## 8. What would count as failure

- E1 ≠ 0: the circular arm caught the defect — then the defect leaked into the facts derivation
  or the arms were not isolated, and the study's construction is wrong.
- E2 misses a defect-class row: the transcribed oracle is blind where it was predicted to see;
  the divergence between prediction and run is analyzed, not patched.
- E3 shows divergences beyond the controls: pack C does not faithfully encode `POLICY.md`, which
  is a fixture-authoring failure — registered as such, never fixed by editing records to match C.
- Any endpoint that cannot fail once another passes is reported as such in `ANALYSIS.md`
  (the Study 008 lesson: an endpoint that follows necessarily from an earlier one is not
  independent evidence, and saying so is part of the result).

## 9. Bounds — what this study cannot show

- **Synthetic records, one author.** Records here are derived from `POLICY.md` by a registered
  table, by the same author who encoded the packs. The independence that matters in this study is
  **structural**: the expectation stream provably never passes through the evaluator or the pack
  (E4), which is precisely the property the circular oracle lacks. What this cannot show is that
  *real* organizational records are accurate, complete, or policy-consistent oracles. That
  question needs real case files in a private project tree and is deliberately out of scope; no
  real, personal, or client data appears in this repository (spec `TESTING.md` prohibition,
  scoped as issue #23 records).
- **Byte-lineage, not truth.** `origin` records where a row came from; it never claims the row is
  right (this line's ADR-0002 ceiling, unchanged).
- **One defect, one pack family.** A single planted defect cannot support a rate; the study
  demonstrates existence — there is a defect class the circular oracle cannot catch and a
  transcribed oracle can — not prevalence.

## 10. Procedure

1. Freeze: fixtures, transcriber, rule, records, `DEFECT.md`, `RECORDS.md`, this file;
   `FREEZE.json` records SHA-256 of each plus the pinned `jpack` release digest.
2. `harness/study.py validate` — fixtures well-formed, pack C and D differ exactly at the
   registered defect, records match `RECORDS.md`'s table.
3. `harness/study.py run` — attest records, derive facts, build the three arm matrices, run
   `packs validate` + `packs test` per arm (CLI), plus the MCP run for E5.
4. `harness/study.py score` — compare payloads to §7's predictions; emit `RESULTS.json`.
5. `ANALYSIS.md` before the numbers are quoted anywhere; adversarial review afterward in
   [`ADVERSARIAL-REVIEW.md`](ADVERSARIAL-REVIEW.md).

Every run's inputs and outputs are retained content-addressed under `trials/`; no run is
discarded.
