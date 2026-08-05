# Preregistration — Study 010: the blinded oracle (revision 3)

**Status: DRAFT until the protocol lock; governing thereafter.** Revision 1
was rejected in pre-freeze review (verdict *redesign*: operator entropy, no
structural blinding); revision 2 was rejected again (verdict *redesign*: a
steerable publication clock, an overlapping E1, and an inheritance claim
the Study 009 harness cannot honor). Revision 3 repairs all fourteen
findings; both reviews and their dispositions are in
[`PREREG-REVIEW.md`](PREREG-REVIEW.md). This revision is reviewed together
with the complete, byte-exact protocol-lock candidate — policy, pack C,
family, prompt, compiler, checkers, harness, controls — not as prose alone.
After the lock this file is never edited; corrections go to
`DEVIATIONS.md`, and a change to any locked file after authoring begins
invalidates the attempt (§8).

## 1. The question

> Does a record set authored independently of the packs — by a
> different-vendor model given the prose policy — surface an encoding
> defect selected by entropy nobody controls, after the records were
> immutably published?

Study 009 established the pipeline as a constructed existence witness; the
one uncertain quantity here is **usable record coverage** of a defect class
neither author picked. The blinding claims are stated at their checkable
strength, no higher — §9 states exactly which properties are mechanically
enforced, which are recorded but not proven, and which are not prevented:

- **Authorship**: *one retained completion whose transcript shows no tool
  use* — the authoring call runs from an empty scratch directory outside
  this repository, and its full session transcript is retained. The
  transcript-to-compiler binding is mechanical (§4); the no-retry rule is
  recorded, not proven (§9).
- **Selection**: the applied mutation is drawn from a **pre-committed
  ordered family** by a **drand beacon round that had not yet occurred**
  when the records were published, where "published" is an inclusion in the
  Sigstore Rekor transparency log whose timestamp the operator cannot set
  (§5), with all proof material retained.

Both non-degenerate outcomes of the primary endpoint are findings: a
*catch* is the first independent-oracle detection on this line; a
*coverage-miss* is a measured boundary-coverage gap in diligent independent
authorship.

## 2. The policy, encoded disjointly

`policy/POLICY.md`, clauses P1–P5 over four facts —
`/vendor/sanctionsHit` (bool S), `/vendor/registeredCountry` (uppercase
two-letter code; embargo list **KP, IR, SY**, membership exact and
case-sensitive; E := country ∈ list), `/vendor/handlesPersonalData`
(bool P), `/vendor/riskScore` (canonical decimal string r, compared
numerically):

- **P1**: S → reject
- **P2**: ¬S ∧ E → reject
- **P3**: ¬S ∧ ¬E ∧ r ≥ 70 → manual-review
- **P4**: ¬S ∧ ¬E ∧ P ∧ 40 ≤ r < 70 → manual-review
- **P5**: ¬S ∧ ¬E ∧ r < 70 ∧ (¬P ∨ r < 40) → clear

Pack C (`packs/vendor-screening-correct.pack.json`, part of the reviewed
candidate) encodes exactly these five mutually exclusive rules, no
`fallbackOutcome`. The country domain is **syntactic**: `[A-Z]{2}`, no
registry snapshot — the policy semantics distinguish only the three embargo
codes, so an unassigned code is simply a non-embargoed country, and
membership never consults a registry.

`harness/policy_mirror.py` is the study's **independent reference
semantics**: the policy verdict and the family predicates, implemented over
record facts with no evaluator call. `harness/regions_check.py` — run
inside the protocol-lock gate, before authoring, against pack C only, never
D, never a record — asserts that the pinned runtime's disposition of pack C
equals the mirror's outcome on all 24 truth regions (S × E × P × {r<40,
40≤r<70, r≥70}) **and** on a locked boundary battery: r ∈ {39, 39.5, 40,
41, 69.9, 70, 70.5, 71} × P ∈ {true, false} with ¬S and a non-embargoed
country, each embargo country at r = 5, and SY at r = 85. Residual risk —
a pack defect invisible to all 44 probes yet coincident in outcome — is
bounded by the review of pack C's exact bytes, and is stated in §9.

## 3. The mutation family — exact, ordered, reviewable

`FAMILY.json` (part of the reviewed candidate), six entries with contiguous
`index` members 0–5; per entry the normative members are `patch` (a strict
single-replace into pack C: JSON pointer, preimage `old`, replacement
`new`), `predicate` (the machine-checkable affected class the mirror
interprets), and `reasonsUnderD` (the registered unresolved reason set,
keyed by the personal-data value). Prose members annotate; the machine
members govern.

| # | Mutation | Affected class |
|---|---|---|
| 0 | P3's `greater-than-or-equal` → `greater-than` | ¬S ∧ ¬E ∧ r = 70 |
| 1 | P3's threshold `"70"` → `"71"` (in P3 only) | ¬S ∧ ¬E ∧ 70 ≤ r < 71 |
| 2 | P4's lower bound `"40"` → `"41"` | ¬S ∧ ¬E ∧ P ∧ 40 ≤ r < 41 |
| 3 | P4's `handlesPersonalData` → `false` | ¬S ∧ ¬E ∧ 40 ≤ r < 70 (P: no-match; ¬P: P4/P5 conflict) |
| 4 | P2's embargo list loses `"SY"` | ¬S ∧ country = SY |
| 5 | P5's inner `"40"` (the ¬P ∨ r<40 arm) → `"39"` | ¬S ∧ ¬E ∧ P ∧ 39 ≤ r < 40 |

The family spans stated boundaries (0, 1, 2), an unstated interior band
(5), a membership literal (4), and a boolean flip with conflict
dispositions (3) — misses are plausible for 1, 2, 4, and 5, so a
coverage-miss is an available outcome, not an artifact. Every defect class
disposes as an outcome under C and as `unresolved` (no-match or conflict,
per `reasonsUnderD`) under its D; those are registered table values, not
failures.

## 4. Records: the call, the binding, the compiler, the sets

**The call.** One `codex exec` invocation (OpenAI model, the line's
cross-vendor vendor), run by the registered
`transcription/authoring_call.sh` from a freshly created empty directory
outside this repository, prompt = the exact bytes of
`transcription/PROMPT.txt` (§7), stdin closed. Retained verbatim under
`transcription/authoring/`: `CALL.json` (argv, cwd, environment allowlist,
CLI identity, exit status), `stdout.raw`, `stderr.raw`, `session.jsonl`
(the full session transcript), and `completion.txt` (the compiler input,
extracted mechanically as below). **No-retry rule**: the first completed
invocation is the one; a transport failure (non-zero exit with no
completed assistant message) may be retried at most twice, each attempt
retained; a completed-but-disliked output may not be retried. §9 states
what this rule proves and what it merely records.

**The transcript binding** (`harness/transcript_check.py`, locked). The
attempt is admissible only if, mechanically checked from `session.jsonl`:

1. the transcript contains **zero** tool invocations — no `response_item`
   entry whose payload type is any call form (`function_call`,
   `custom_tool_call`, `local_shell_call`, `web_search_call`, or any type
   ending in `_call`) and no call-output entries;
2. the **last user message**'s text equals `PROMPT.txt`'s bytes exactly
   (UTF-8);
3. at least one assistant message exists, and `completion.txt`'s bytes
   equal the UTF-8 encoding of the **last assistant message**'s
   concatenated `output_text` items — the registered completion;
4. `CALL.json` records exit status 0.

A violation of 1–4 is an inadmissible authoring attempt: the run refuses
and E1 is `pipeline-invalid` unless a retained retry (transport-failure
rule above) is admissible.

**The compiler.** `harness/records_compile.py` — locked before the call —
turns `completion.txt` into record files with no operator judgment.
Extraction is registered normatively: scan every `[` position left to
right; parse each with a strict JSON decoder that **rejects duplicate
object keys anywhere** in the candidate; among positions that parse as an
array, select the one spanning the most characters, ties to the earliest;
everything outside the selected span is retained but ignored, and
`RECORDS.md` records the selected span's offsets and the stream length. No
parseable array → the compile refuses → E1 `pipeline-invalid`. Admission:
an element is accepted iff it passes, in this registered order, each check
of: `schema` (the closed record shape: exact member sets, exact primitive
types), `decimal-form` (canonical decimal grammar
`^(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$`), `country-form` (`^[A-Z]{2}$`),
`id-form` (kebab-case `^[a-z0-9]+(-[a-z0-9]+)*$`, and the `k-` prefix is
reserved for controls — an authored `k-…` id drops here), `outcome-value`
(one of `clear`, `manual-review`, `reject`), `duplicate-id` (a previously
**accepted** element already claimed the id; a dropped earlier occurrence
reserves nothing). The first failing check's code is the drop code; there
is no repair of any kind. Output: `records/<caseId>.json` (2-space
indented, sorted keys, trailing newline) plus `RECORDS.md` listing every
source index → accepted id or drop code. `validate` regenerates all of it
from the retained `completion.txt` and requires byte equality including
the exact file-name set — extra or missing files refuse.

**The sets.** Over **authored accepted records only**: H := records whose
recorded outcome equals the mirror's verdict; Q := the rest (retained as
data, never dropped, excluded from H). K := the two locked controls in
`controls/` (`k-wrong-1`, `k-wrong-2`): policy-discordant by construction,
disjoint from every family predicate, never counted in H, Q, or F.
F := accepted authored records satisfying the sampled predicate (computed
after the draw). Authored records and controls live in separate locked
manifests; the record source (`source/record_source.py`) serves their
union deterministically, and every arm's acquisition covers all of
H ⊔ Q ⊔ K with a per-record receipt bijection through Study 009's gates.

## 5. The draw

**The witness.** At lock time the operator generates a fresh P-256
keypair: the public key is committed and locked
(`transcription/witness-pub.pem`); the private key never enters the
repository and is used exactly once. Publication of the records is the
**Rekor inclusion**: a `hashedrekord` entry in the public Sigstore Rekor
log (`rekor.sigstore.dev`) over the canonical manifest bytes
`"study-010-records-commit\n" + <40-hex commit OID> + "\n"`, signed with
the witness key. Rekor's `integratedTime` — set by the log, not the
operator — is the publication clock, and the entry's `logIndex` orders it.

**The binding rule.** The attempt is bound to the entry with the
**minimal `logIndex`** among Rekor entries verifiable with the locked
witness public key. Later entries under that key are void. The check runs
online (`study.py witness`, with retries; Rekor's search index lags
inclusion by design, so it is re-run before freeze and again in the
post-run review) and its raw responses are retained; `validate` re-verifies
offline from the retained entry: the artifact digest equals the sha256 of
the manifest bytes reconstructed from the records commit OID, and the
signature verifies under the locked public key.

**The round.** Locked constants: the drand mainnet default chain's chain
hash, public key, scheme (`pedersen-bls-chained`), genesis time G, and
period p = 30 s, captured at lock time from `/v2/beacons/default/info`
with the raw response retained. Registered arithmetic, integer POSIX
seconds throughout:

```
scheduled(R) = G + (R - 1) * p
T            = integratedTime + 300
targetRound  = floor((T - G + p - 1) / p) + 1     # first R with scheduled(R) >= T
```

The harness fetches **only** `targetRound` — never latest, never a
neighbor — from two independent relays (`api.drand.sh` and
`drand.cloudflare.com`, both addressed by chain hash) and requires
byte-identical `signature` values; raw responses from both are retained in
`DRAW.json`. `randomness` is computed as sha256 of the signature bytes —
the chained scheme's definition. If the round cannot be retrieved from
either relay within 3600 seconds of `scheduled(targetRound)`, the draw
refuses and the attempt is `pipeline-invalid`. BLS verification inputs —
chain public key, round, `signature`, `previous_signature` — are all
retained for external verification; the harness's own checks are the
dual-relay byte equality and the randomness recomputation (§9).

**The index.** Registered byte-normative derivation:

```
preimage = ASCII("study-010-draw-v1\n"
                 + randomness_hex + "\n"     # 64 lowercase hex chars
                 + commit_oid_hex + "\n"     # 40 lowercase hex chars
                 + family_digest_hex + "\n") # 64 lowercase hex chars
index    = int.from_bytes(sha256(preimage).digest(), "big") mod 6
```

where `family_digest_hex` is the sha256 hex digest of the locked
`FAMILY.json` bytes. The sampled mutation is the `FAMILY.json` entry whose
`index` **member** equals the residue (the lock asserts members 0–5 exist
contiguously). The 2^256 mod 6 bias is negligible and accepted. `DRAW.json`
retains the preimage fields, the digest, the residue, the Rekor entry, and
both relay responses; `validate` recomputes the residue and the round
arithmetic from retained bytes.

**After the draw** the harness applies the sampled patch to C to produce
D, computes F, and derives the per-record C and D disposition tables for
every authored record and control **from the reference semantics only**:
`underC` = the mirror's verdict wrapped in the registered outcome shape;
`underD` = `underC` except on the sampled predicate, where it is
`unresolved` with the mutation's `reasonsUnderD` reason set. No evaluator
call touches table derivation; the evaluator's agreement with the tables
is exactly what E2 tests, and a divergence is `pipeline-invalid`, never a
table amendment. `DEFECT.json` (sets + tables) and
`packs/vendor-screening-defective.pack.json` are committed with
`DRAW.json`.

## 6. Arms, endpoints, prerequisites

Arms as Study 009 — A (circular over D), B (transcribed over D), B′
(transcribed over C) — through the **Study 010 port** of its repaired
gates: the four-pointer PNF projection (`harness/pnf_check.py`), the
complete-row fabrication gate (`harness/gate.py`), fresh-store
acquisition with receipt bijection over H ⊔ Q ⊔ K, arm isolation, the
sealed-attempt ledger, and the CLI/MCP comparison. The port is part of the
reviewed candidate; nothing is claimed "verbatim" — the 009 harness's
three-fact schema, disjoint F/K/H partition, and hard-coded mismatch sets
do not transfer, and the 010 driver (`harness/study.py`) is reviewed as
its own artifact.

**Attempt ledger totality.** `run` creates the attempt directory and its
`STARTED` marker exclusively before any work; every exit path — success
or exception — writes a terminal state (`DONE` or `CRASHED.json`), seals
the attempt (a content manifest plus read-only permissions; the seal is
tamper-evidence against accident, not against the owner — §9), and never
overwrites. **The primary attempt is the first attempt started under the
current committed freeze, whatever its terminal state.** A primary attempt
without `DONE` scores E1 = `pipeline-invalid`; later attempts are
sensitivity data only, recorded in `DEVIATIONS.md`.

**E1, an ordered partition** (evaluated top to bottom; exactly one label):

1. **pipeline-invalid** — the primary attempt lacks `DONE`, or any
   prerequisite fails: transcript binding (§4), compiler regeneration,
   witness/draw recomputation, P-A (arm A's complete deterministic
   self-replay), acquisition verification, gate admission, E2's table
   conformance, or E5's surface conformance.
2. **caught** — H ∩ F ≠ ∅ (every H ∩ F row's table already passes under C
   and mismatches under D; E2 having passed in step 1 makes the label a
   statement about the evaluator's actual dispositions, not the tables).
3. **authoring-label-failure** — Q ∩ F ≠ ∅ (the sampled class was reached
   only by records whose own recorded outcome is wrong).
4. **coverage-miss** — otherwise (no authored record intersects the
   sampled class).

**E2**: for each of B (under D) and B′ (under C), every actual disposition
equals its reference-table entry, and the row-status mismatch set equals
the **derived** set `{record : table(record) ≠ wrapper(recorded outcome)}`
— never hard-coded. Prediction: yes. (Derived consequences: under C the
set is Q ∪ K; under D it is Q ∪ K ∪ (H ∩ F).)
**E3** (descriptive, no prediction): ids and counts for F, H ∩ F, Q ∩ F,
|H|, |Q|, and the per-family coverage profile — for every index, the H and
Q records intersecting its predicate, K always excluded. Registered now so
it cannot be invented post hoc.
**E5**: as Study 009 — all projects validate, origins echoed exactly,
CLI/MCP payload equality after removing the registered `command` field.
Prediction: yes.

E1's outcome is registered as **uncertain**; everything else is machinery.

## 7. The registered record-authoring prompt

`transcription/PROMPT.txt`, byte-exact (the fence below is the entire
file, policy text inlined; the transcript binding's check 2 compares
against the file bytes):

```
You are the records clerk of a fictional vendor-governance office. Below is
the office's screening policy. Author the decision records of 16 distinct
vendor screening cases this office decided under it, as a JSON array.

Each record: {"caseId": "<kebab-case id you invent>", "vendor":
{"legalName": <string>, "sanctionsHit": <bool>, "registeredCountry":
<string>, "handlesPersonalData": <bool>, "riskScore": <decimal string, no
trailing zeros>}, "decision": {"outcome": <"clear"|"manual-review"|
"reject">, "decidedBy": <string>, "decidedAt": <ISO 8601 UTC>}}.

Vendors are registered in various countries; use ISO 3166-1 alpha-2 codes,
uppercase.

Make the set what a diligent office's files would look like: exercise every
clause of the policy, include the borderline cases a careful clerk would
have seen, and record the outcome the policy requires for each. Do not
include commentary — output only the JSON array.

<POLICY>
```

with `<POLICY>` replaced by the full text of `policy/POLICY.md`. The
instruction is defect-agnostic by construction: it names no threshold, no
comparison, and no pack.

## 8. The two locks, and the ordering

1. **Protocol lock** (one commit, pushed, then externally timestamped by a
   Rekor inclusion over the lock commit's OID under the witness key —
   the same manifest form as §5 with prefix `study-010-lock-commit`):
   `PROTOCOL-LOCK.json` pins the byte digests of every locked input —
   this file, `PREREG-REVIEW.md`, `policy/POLICY.md`, pack C,
   `FAMILY.json`, `PROMPT.txt`, `record.rule.json`, `transcribe.py`,
   `authoring_call.sh`, the controls, `record_source.py`, the harness
   (driver, gate, pnf, mirror, compiler, regions and transcript checkers,
   tests), and the shared line code (`attest.py`, `derive.py`, the
   fabrication gate) — plus the pinned jpack v0.15.0 binary digest, the
   witness public key, the drand chain constants with the raw `/info`
   response, and the draw rule constants. `PROTOCOL-LOCK.json` does not
   digest itself; its bytes are bound by the lock commit, and `validate`
   asserts the on-disk file equals `HEAD`'s and that its key set is
   exactly the registered list. The lock command refuses unless
   `regions_check` passes and every family patch applies to pack C.
   Authoring may not begin before this commit is pushed.
2. Authoring call → records commit → **Rekor inclusion of the records
   commit (the publication)** → push → beacon round → `DRAW.json` +
   pack D + `DEFECT.json` commit.
3. **Artifact freeze** (`FREEZE.json`): adds the generated artifacts —
   authoring retention, records, `RECORDS.md`, D, `DRAW.json`,
   `DEFECT.json`, the witness inclusion — to the locked set, and binds
   the protocol-lock digest. Then `validate` → `test_study.py` → `run`
   (first attempt is primary) → `score` → `ANALYSIS.md` before quoting
   numbers → post-run adversarial review.

## 9. What is enforced, what is recorded, what is not prevented

**Mechanically enforced** (a violation refuses or scores
`pipeline-invalid`): the locked bytes and their non-drift; pack C ≡ mirror
on the 44 probes; the transcript binding (no tool events, prompt bytes,
completion bytes); compiler regeneration byte equality; the Rekor
inclusion's signature, artifact binding, and minimal-logIndex rule; the
round arithmetic and dual-relay signature equality; the index
recomputation; table derivation from the reference semantics only; the
gates, receipt bijection, and arm isolation; attempt-ledger totality.

**Recorded but not proven**: that the retained authoring invocation is the
first completed one (the no-retry rule); that no other codex sessions ran;
wall-clock claims beyond Rekor's `integratedTime` and drand's round
schedule.

**Not prevented**: off-ledger evaluations of C or any candidate D against
the records before publication (all six patches are public; a coverage
profile is computable privately); transient tool edits restored before
commit; abandoning an attempt before its records are published and
starting over (a new authoring call under a fresh lock would be visible in
the commit graph, but a discarded *unpublished* attempt would not); BLS
verification of the beacon signature (material retained; verification
delegated to the external reader — the harness checks dual-relay
agreement and the randomness definition, not the pairing equation).

None of the unprevented actions can steer the sampled index once the
records are published, because the index depends only on
post-publication beacon output and already-locked bytes; what they could
do is bias *which record set* reached publication — exactly the residual
the narrowed authorship claim of §1 concedes.

## 10. Bounds

One sampled mutation (no rates). One model completion, operator-retained
under the narrowed claim. The family is public before authoring, and the
policy text itself names 70, 40, and the embargo list, so stated-boundary
mutations are likely covered by any diligent author; the informative
misses live at indexes 1, 2, 4, and 5, and E3 reports the profile either
way. Real records, rates, and sensitivity remain out of scope, as does
everything Study 009's §11 excluded. Byte-lineage, not truth, unchanged.
