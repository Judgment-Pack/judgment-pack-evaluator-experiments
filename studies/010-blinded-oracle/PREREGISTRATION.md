# Preregistration — Study 010: the blinded oracle

**Status: DRAFT — NOT FROZEN. The pre-freeze cross-vendor review returned
"redesign" ([`PREREG-REVIEW.md`](PREREG-REVIEW.md)); this text is retained
as the reviewed draft and will be superseded before anything freezes.**
Registered as Study 009's next question (its §1). Nothing here has been
built or run.

## 1. The question, and why it can actually fail

Study 009 was a constructed existence witness: one mind authored policy,
packs, defect, and records, with full knowledge of both oracles, and its
endpoints were entailed by construction. This study removes the author from
the middle:

> Does a record set authored **independently of the packs** — by a
> different-vendor model given only the prose policy — surface an encoding
> defect **neither author chose knowing the other's work**?

The blinding is structural, not promised:

- **The record author never sees a pack.** The records are authored by an
  OpenAI model (`codex exec`, the line's cross-vendor reviewer vendor) from
  `policy/POLICY.md` alone; the authoring prompt is registered verbatim in
  §6 and contains the policy text, the record schema, and a
  defect-agnostic instruction — no boundary hints, no pack, no mutation
  family. One run; its complete unedited output is retained; no run
  discarded.
- **The pack author never sees the records when the defect is chosen.** The
  defect is not chosen by anyone: a **registered mutation family** of six
  single-condition mutations of pack C is committed *before* the records
  exist, and the applied mutation is selected by public coin —
  `sha256(<records-locking commit hash>) mod 6` — after the records are
  locked. Nobody can steer the coin toward or away from what the records
  cover.

Because coverage of the sampled defect class is now genuinely unknown, the
primary endpoint **can fail**, and both outcomes are findings:

- a **catch** is the first evidence on this line that an independently
  authored oracle surfaces an unseen encoding defect;
- a **miss** is a measured boundary-coverage gap in diligent independent
  record authorship — the thing a real organization's case files would also
  have, and exactly what Study 009's §11 said constructed fixtures cannot
  measure.

What stays out of scope: real organizational records (the private-pilot
question), rates (one sampled mutation), and everything Study 009's §11
already excluded.

## 2. Model calls

One: the record-authoring call to the different-vendor model. It is part of
the *fixture provenance*, not a treatment arm; its prompt and complete
output are frozen artifacts. Everything downstream is deterministic and
model-free, exactly as Study 009.

## 3. Mechanics — Study 009's, incorporated by reference

The pipeline, gates, freeze discipline, ledger, and scoring are **Study
009's third revision verbatim** (its §§7–10 as repaired through its
DEVIATIONS §2), with these deltas only:

1. **The policy is richer** (`policy/POLICY.md`, clauses P1–P5): sanctions
   hit → reject (P1); embargoed registration country → reject (P2); no hit,
   risk ≥ 70 → manual review (P3); no hit, personal-data handling and risk ≥
   40 → manual review (P4); otherwise clear (P5). Facts: `/vendor/
   sanctionsHit` (bool), `/vendor/registeredCountry` (string),
   `/vendor/handlesPersonalData` (bool), `/vendor/riskScore` (canonical
   decimal string). The embargo list is stated in the policy text.
2. **The record schema** adds the two facts; the projection rule copies all
   four `/vendor` pointers, identity-mapped; `pnf_check.py` requires exactly
   that rule.
3. **The mutation family** (`FAMILY.json`, committed before records exist):
   six entries, each a strict `{path, old, new}` patch to one condition of
   pack C — one per comparison or equality the rules make (P1's boolean,
   P2's membership, P3's threshold op, P3's threshold value, P4's threshold
   value, P4's boolean). Each entry carries its evaluator-independent defect
   predicate and the policy clause it violates.
4. **The coin**: `int(sha256(records_commit_hash_hex), 16) % 6`, computed by
   the harness from the commit that locks `records/` (the Codex output
   transcribed to files, one commit, nothing else in it). `DEFECT.json` is
   then generated — patch from the family, sets computed from the records by
   the sampled predicate, expected dispositions derived per Study 009's
   provenance discipline — and committed with D.
5. **Sets**: F = records satisfying the sampled defect predicate (may be
   empty — that is the miss outcome); K = two wrong-outcome controls the
   harness *appends* itself (synthetic, disclosed, not Codex-authored, ids
   prefixed `k-`), because the suite must still be able to fail even on a
   miss; H = the rest. Records failing the closed schema or the canonical
   decimal form are dropped with the drop recorded (the model is not
   graded on JSON hygiene; dropped ids are listed in `RECORDS.md`).

## 4. Arms and endpoints

Arms exactly as Study 009 (A circular over D; B transcribed over D; B′ over
C), built and admitted by the same gates.

| # | Endpoint | Prediction |
|---|---|---|
| E1 | **The catch question**: Arm B over D mismatches on ≥ 1 record in F (only scoreable when F ≠ ∅) | **registered as uncertain** — this is the measurement |
| E2 | Table conformance: every actual disposition equals its DEFECT.json entry under the arm's pack; entailed mismatch sets are exactly F ∪ K under D and K under C | **yes** |
| E3 | Coverage report: |F|, and the boundary-coverage profile of the Codex record set against the family's six predicates (how many family members the record set *would* have caught), reported descriptively | — |
| E5 | Pipeline fidelity, as Study 009 E5 | **yes** |

Prerequisites P-A, P-ACQ, P-PNF, P-GATE, P-ISO: Study 009's, verbatim. The
dependency map: E2 is entailed as in Study 009; **E1 is not entailed by
anything** — it is the one genuinely uncertain bit, which is the point.

## 5. Procedure and ordering (commit-enforced)

1. This preregistration + its review (docs-only commit).
2. `policy/POLICY.md`, pack C, `FAMILY.json`, rule, harness deltas
   (committed **before** any record exists).
3. The Codex record-authoring run: prompt + complete output committed
   verbatim; records transcribed to files; **one commit containing only
   `records/` and `RECORDS.md`** — its hash is the coin input.
4. Harness computes the coin, generates D and `DEFECT.json`, commits them.
5. `validate` → `test_study.py` → `freeze` → commit → **first attempt is
   primary** under Study 009's ledger rules → `score` → `ANALYSIS.md` →
   post-run adversarial review.

Every ordering claim above is checkable from the commit graph.

## 6. The registered record-authoring prompt

Verbatim, with `<POLICY>` replaced by the full text of `policy/POLICY.md`:

```
You are the records clerk of a fictional vendor-governance office. Below is
the office's screening policy. Author the decision records of 16 distinct
vendor screening cases this office decided under it, as a JSON array.

Each record: {"caseId": "<kebab-case id you invent>", "vendor":
{"legalName": <string>, "sanctionsHit": <bool>, "registeredCountry":
<string>, "handlesPersonalData": <bool>, "riskScore": <decimal string, no
trailing zeros>}, "decision": {"outcome": <"clear"|"manual-review"|
"reject">, "decidedBy": <string>, "decidedAt": <ISO 8601 UTC>}}.

Make the set what a diligent office's files would look like: exercise every
clause of the policy, include the borderline cases a careful clerk would
have seen, and record the outcome the policy requires for each. Do not
include commentary — output only the JSON array.

<POLICY>
```

The instruction is defect-agnostic by construction: it names no threshold,
no comparison, and no pack.

## 7. Bounds

One sampled mutation (no rates); a different-vendor *model*, not a human
organization (the private pilot stays out of scope); the mutation family is
public in the repository, and the blinding claim is about what the record
author's prompt contained, which is registered verbatim — a reader must
judge the prompt, not trust the author; byte-lineage, not truth, unchanged.
