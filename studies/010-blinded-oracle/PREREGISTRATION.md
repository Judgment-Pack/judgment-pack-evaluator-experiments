# Preregistration — Study 010: the blinded oracle (revision 2)

**Status: DRAFT until the protocol lock; governing thereafter.** The first
draft's pre-freeze review returned *redesign*
([`PREREG-REVIEW.md`](PREREG-REVIEW.md)); this revision implements its six
pillars and receives its own pre-freeze review before the protocol lock.
After the lock this file is never edited; corrections go to
`DEVIATIONS.md`, and a protocol change after authoring begins invalidates
the authoring attempt (§8).

## 1. The question

> Does a record set authored independently of the packs — by a
> different-vendor model given the prose policy — surface an encoding
> defect selected by entropy nobody controls, after the records were
> locked?

Study 009 established the pipeline as a constructed existence witness; the
one uncertain quantity here is **usable record coverage** of a defect class
neither author picked. The blinding claims are stated at their checkable
strength, no higher:

- **Authorship**: *one retained completion whose transcript shows no tool
  use* — the authoring call runs from an empty scratch directory outside
  this repository, and its full session transcript (every tool invocation
  or the absence of any) is retained as the evidence. This is weaker than
  an independent executor and says so: the operator selected which single
  completion to retain, under a no-retry rule registered below.
- **Selection**: the applied mutation is drawn from a **pre-committed
  ordered family** by a **drand beacon round that had not yet occurred**
  when the records were published — entropy the operator cannot steer, with
  all proof material retained for external verification.

Both outcomes of the primary endpoint are findings: a *catch* is the first
independent-oracle detection on this line; a *coverage-miss* is a measured
boundary-coverage gap in diligent independent authorship.

## 2. The policy, encoded disjointly

`policy/POLICY.md`, clauses P1–P5 over four facts —
`/vendor/sanctionsHit` (bool S), `/vendor/registeredCountry` (ISO 3166-1
alpha-2, uppercase; embargo list **KP, IR, SY**, membership exact and
case-sensitive; E := country ∈ list), `/vendor/handlesPersonalData`
(bool P), `/vendor/riskScore` (canonical decimal string r, compared
numerically):

- **P1**: S → reject
- **P2**: ¬S ∧ E → reject
- **P3**: ¬S ∧ ¬E ∧ r ≥ 70 → manual-review
- **P4**: ¬S ∧ ¬E ∧ P ∧ 40 ≤ r < 70 → manual-review
- **P5**: ¬S ∧ ¬E ∧ r < 70 ∧ (¬P ∨ r < 40) → clear

Pack C encodes exactly these five mutually exclusive rules, no
`fallbackOutcome`. `harness/regions_check.py` — part of the protocol lock —
enumerates the 24 truth regions (S × E × P × {r<40, 40≤r<70, r≥70}) and
asserts, by evaluating pack C with the pinned runtime on one probe per
region, that exactly the policy's outcome results in every region. (These
probes evaluate pack C only — never D, never a record — and run before
authoring, inside the protocol-lock gate.)

## 3. The mutation family — exact, ordered, reviewable

`FAMILY.json`, six entries, each `{index, path, old, new, predicate,
violatedClause}` — the patch a strict single-replace into pack C, the
predicate evaluator-independent over record facts:

| # | Mutation | Affected class (the predicate) |
|---|---|---|
| 0 | P3's `greater-than-or-equal` → `greater-than` | ¬S ∧ ¬E ∧ r = 70 |
| 1 | P3's threshold `"70"` → `"71"` (in P3 only) | ¬S ∧ ¬E ∧ 70 ≤ r < 71 |
| 2 | P4's lower bound `"40"` → `"41"` | ¬S ∧ ¬E ∧ P ∧ 40 ≤ r < 41 |
| 3 | P4's `handlesPersonalData equals true` → `equals false` | ¬S ∧ ¬E ∧ 40 ≤ r < 70 (P-records lose P4; ¬P-records gain a P4/P5 conflict) |
| 4 | P2's embargo list loses `"SY"` | ¬S ∧ country = SY |
| 5 | P5's inner `"40"` (the ¬P ∨ r<40 arm) → `"39"` | ¬S ∧ ¬E ∧ P ∧ 39 ≤ r < 40 |

The family spans stated boundaries (0, 1, 2), an unstated interior band
nothing in the policy text names (5), a membership literal (4), and a
boolean flip with conflict dispositions (3) — misses are plausible for 1,
2, 4, and 5, so a coverage-miss is an available outcome, not an artifact.
Mutations keep D carrier- and semantically valid; where a mutation
produces `unresolved` dispositions (no-match or conflict), those are the
registered table values, not failures.

## 4. Records: the call, the compiler, the sets

**The call.** One `codex exec` invocation (OpenAI model, the line's
cross-vendor vendor), run from a freshly created empty directory outside
this repository, sandboxed to that directory, with the prompt being
exactly the registered bytes of §7 (policy text inlined). Retained
verbatim: argv, cwd, environment allowlist, model/CLI identity, the full
session transcript (JSONL), stdout, stderr, exit status. **No-retry
rule**: the first completed invocation is the one; a transport failure
(non-zero exit with no completion) may be retried at most twice, each
attempt retained; a completed-but-disliked output may not be retried, and
the transcript inventory in `RECORDS.md` makes an unrecorded retry
detectable only by trusting the operator — the claim is narrowed
accordingly (§1).

**The compiler.** `harness/records_compile.py` — protocol-locked before
the call — turns raw stdout into record files with no operator judgment:
extract the single JSON array (first `[` to its matching `]`; anything
else in the stream is retained but ignored); per element, accept iff it
matches the closed record schema exactly (Study 009's, plus
`registeredCountry` and `handlesPersonalData`; canonical decimal grammar;
ISO-alpha-2 uppercase country; kebab-case id; no duplicate id — second
occurrence rejected with `duplicate-id`); no repair of any kind; stable
drop codes (`schema`, `decimal-form`, `country-form`, `duplicate-id`,
`outcome-value`); output = one file per accepted record plus
`RECORDS.md` listing every source index → accepted id or drop code.
`validate` regenerates records and drops from the retained raw stdout and
requires byte equality.

**The sets.** Q := accepted records whose recorded outcome differs from
the policy verdict (computed by the locked policy mirror) — retained as
data, never dropped, excluded from H. K := two synthetic wrong-outcome
controls the harness appends (ids `k-wrong-1`, `k-wrong-2`, facts and
outcomes fixed in the protocol lock, disjoint from every family
predicate). H := accepted policy-concordant records. F := accepted
records satisfying the *sampled* predicate (computed after the draw).

## 5. The draw

1. The records commit (records + `RECORDS.md` + the call artifacts,
   nothing else) is pushed to the public repository: the publication.
2. The **target round** is fixed by locked rule, not choice: the first
   drand `default`-chain round whose scheduled time is ≥ the GitHub API's
   `committer.date` of the pushed records commit **plus 300 seconds**
   (chain genesis and 30s period are constants in the protocol lock, so
   the round number is arithmetic anyone can redo). Delaying the push
   delays the round; it never reveals future randomness, so timing buys
   no steering.
3. After the round occurs: `index = int(sha256(randomness_hex ||
   records_commit_hash_hex || family_digest_hex), 16) mod 6` — domain
   inputs concatenated as lowercase hex ASCII. 2^256 mod 6 bias is
   negligible and accepted (recorded here rather than rejected-sampled).
4. `DRAW.json` retains: the records commit hash, its committer date, the
   round number and its scheduled time, the beacon `randomness` and
   `signature`, the chain info (hash, genesis, period), the family
   digest, the computed index — everything needed to re-verify against
   drand's public chain.
5. The harness generates D (family[index] applied to C), computes F by
   the sampled predicate, derives the full C and D disposition tables for
   every retained record and control (Study 009's provenance discipline),
   writes `DEFECT.json`, and commits.

## 6. Arms, endpoints, prerequisites

Arms as Study 009 (A circular over D; B transcribed over D; B′ over C),
through Study 009's repaired gates verbatim (P-A, P-ACQ, P-PNF adjusted to
the four-pointer projection, P-GATE, P-ISO), the same freeze/ledger/scorer
discipline (its DEVIATIONS §2 form), the sealed-attempt ledger, and the
same E5.

**The primary endpoint E1 is four-way and always scoreable:**

- **caught** — ≥ 1 record in H ∩ F passes under C and mismatches under D;
- **coverage-miss** — H ∩ F = ∅ (no policy-concordant record intersects
  the sampled class);
- **authoring-label-failure** — H ∩ F = ∅ but Q ∩ F ≠ ∅ (the class was
  reached only by records whose own outcome is wrong);
- **pipeline-invalid** — any prerequisite or table-conformance check
  failed; no E1 claim is made.

**E2**: every actual disposition equals its table entry under the arm's
pack; the mismatch sets are *derived* from the tables and recorded
outcomes (they are `{r : table_D(r) ≠ wrapper(recorded(r))}` under D and
likewise under C) — never hard-coded. Prediction: yes.
**E3** (descriptive, no prediction): |F|, |H∩F|, |Q|, and the coverage
profile — for each family index, whether H would have intersected its
predicate. Registered now so it cannot be invented post hoc.
**E5**: as Study 009. Prediction: yes.

E1's outcome is registered as **uncertain**; everything else is machinery.

## 7. The registered record-authoring prompt

As the first draft's §6, with the schema extended to the four facts and
this addition after the schema paragraph: "Vendors are registered in
various countries; use ISO 3166-1 alpha-2 codes, uppercase." The full
byte-exact prompt (policy inlined) is written to
`transcription/PROMPT.txt` in the protocol lock, and the call uses those
bytes with no additions.

## 8. The two locks, and the ordering

1. **Protocol lock** (one commit): this file, its review, `POLICY.md`,
   pack C, `FAMILY.json`, `PROMPT.txt`, `records_compile.py`,
   `regions_check.py`, the K controls, the policy mirror, the harness and
   scorer, `PROTOCOL-LOCK.json` (digests of all of it). Authoring may not
   begin before this commit is pushed. Any change to a locked file after
   authoring begins invalidates the attempt: `validate` re-digests
   against `PROTOCOL-LOCK.json`.
2. Authoring call → records commit (push = publication) → beacon round →
   `DRAW.json` + D + `DEFECT.json` commit.
3. **Artifact freeze** (Study 009's `FREEZE.json` form): adds only the
   generated artifacts, record files, tables, D, draw, and the pinned
   jpack digest; then `validate` → `test_study.py` → first sealed attempt
   is primary → `score` → `ANALYSIS.md` → post-run adversarial review.

## 9. Bounds

One sampled mutation (no rates). One model completion, operator-retained
(§1's narrowed claim; the transcript is evidence, not proof). The family
is public before authoring, and the model *could* be told nothing of it —
but the policy text itself names 70 and 40 and the embargo list, so
stated-boundary mutations are likely covered by any diligent author; the
informative misses live at indexes 1, 2, 4, 5, and E3 reports the profile
either way. Real records, rates, and sensitivity remain out of scope, as
does everything Study 009's §11 excluded. Byte-lineage, not truth,
unchanged.
