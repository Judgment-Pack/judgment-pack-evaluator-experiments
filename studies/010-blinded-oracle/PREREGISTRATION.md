# Preregistration — Study 010: the blinded oracle (revision 4)

**Status: DRAFT until the protocol lock; governing thereafter.** Three
pre-freeze reviews rejected the three prior revisions: revision 1
(operator entropy, no structural blinding), revision 2 (a steerable
publication clock, an overlapping E1, an unhonorable inheritance claim),
and revision 3 (an unauthenticated publication clock, an unsound
uniqueness gate, post-beacon record substitution, and eleven further
mechanization gaps — alongside confirmation that the draw arithmetic,
family, tables, controls, and derived mismatch sets are sound). Revision 4
repairs all of it; every review and its disposition is in
[`PREREG-REVIEW.md`](PREREG-REVIEW.md). This revision is reviewed together
with the complete, byte-exact protocol-lock candidate — policy, pack C,
family, prompt, compiler, checkers, harness, controls — not as prose
alone. After the lock this file is never edited; corrections go to
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
`transcription/authoring_call.sh`: from a freshly created empty directory
whose resolved path is outside the repository's git root; with an
environment scrubbed to exactly `PATH` and `HOME`; with the `codex` binary
required to match the sha256 the protocol lock pinned; prompt = the exact
bytes of `transcription/PROMPT.txt` (the file carries **no trailing
newline**, so the shell argument is byte-identical to the file); stdin
closed. Each invocation lands in an immutable numbered slot
`transcription/authoring/call-N` (N ≤ 3) retaining `CALL.json` (argv, cwd,
environment allowlist, CLI identity and binary digest, integer exit
status, new-session count), `stdout.raw`, `stderr.raw`, `session.jsonl`,
and `completion.txt`. **Retry rule**: a slot that completed (exit 0) may
never be followed by another slot; a transport failure (nonzero exit) may
be retried into the next slot, at most three slots total; the admissible
call is the single completed slot, mechanically resolved — it must also
record exactly one new codex session and retain all five files. §9 states
what the slot discipline proves and what it merely records.

**The transcript binding** (`harness/transcript_check.py`, locked). The
parse is a strict whitelist over the transcript's `response_item` payloads:
only `message` entries with role `user`, `developer`, or `assistant` are
admissible, user/developer content must be entirely `input_text` and
assistant content entirely `output_text`; ANY other payload type — every
call form and call output, tool roles, attachments, unknown types —
refuses the attempt. The attempt is admissible only if: exactly one
user/developer message equals `PROMPT.txt`'s bytes; no user/developer
message follows it; at least one assistant message answers it; and
`completion.txt`'s bytes equal the last such assistant message's
concatenated `output_text`. `CALL.json` must record integer exit status 0
(a JSON boolean is not an integer here). A violation is an inadmissible
authoring attempt: the run refuses and E1 is `pipeline-invalid`.

**The compiler.** `harness/records_compile.py` — locked before the call —
turns `completion.txt` into record files with no operator judgment. The
input is read as bytes and UTF-8 decoded with no newline translation.
Extraction is registered normatively: scan every `[` position left to
right; parse each with a strict JSON decoder that rejects duplicate object
keys anywhere and the non-JSON constants `NaN`/`Infinity`/`-Infinity`;
among positions that parse as an array, select the one spanning the most
characters, ties to the earliest; everything outside the selected span is
retained but ignored, and `RECORDS.md` records the selected span's offsets
and the stream length. No parseable array → the compile refuses → E1
`pipeline-invalid`. Admission: an element is accepted iff it passes, in
this registered order (the first failing check's code is the drop code;
every string form is a FULL match; there is no repair of any kind):
`schema` (the closed record shape: exact member sets, exact primitive
types), `decimal-form` (`(0|[1-9][0-9]*)(\.[0-9]*[1-9])?`),
`country-form` (`[A-Z]{2}`), `id-form` (kebab-case
`[a-z0-9]+(-[a-z0-9]+)*`, with the `k-` prefix reserved for controls),
`outcome-value` (one of `clear`, `manual-review`, `reject`),
`timestamp-form` (`YYYY-MM-DDTHH:MM:SSZ`), `duplicate-id` (a previously
**accepted** element already claimed the id; a dropped occurrence reserves
nothing). Output: `records/<caseId>.json` (2-space indented, sorted keys,
trailing newline) plus `RECORDS.md` listing every source index → accepted
id or drop code. `verify` regenerates all of it from the retained
completion bytes and requires byte equality, the exact file-name set, and
regular files only — an extra entry of any name or type refuses.

**The sets.** Over **authored accepted records only**: H := records whose
recorded outcome equals the mirror's verdict; Q := the rest (retained as
data, never dropped, excluded from H). K := the two locked controls in
`controls/` (`k-wrong-1`, `k-wrong-2`): policy-discordant by construction,
disjoint from every family predicate, never counted in H, Q, or F.
F := accepted authored records satisfying the sampled predicate (computed
after the draw). Authored records and controls live in separate locked
manifests; the record source (`source/record_source.py`) serves their
union deterministically, and every arm's acquisition covers all of
H ⊔ Q ⊔ K with a per-record receipt bijection through the ported gates.

## 5. The draw

**The witness keys.** At lock time the operator generates two fresh P-256
keypairs; both public keys are committed and locked
(`transcription/witness-lock-pub.pem`,
`transcription/witness-records-pub.pem`), the private keys never enter the
repository, and each signs exactly one thing: the lock key signs the lock
commit's Rekor timestamp, the records key signs the records publication.
Separate keys make the uniqueness rule unambiguous.

**Publication.** The records publication is a `hashedrekord` inclusion in
the public Sigstore Rekor log over the canonical manifest bytes
`"study-010-records-commit\n" + <40-hex commit OID> + "\n"`, signed with
the records key. **The inclusion is authenticated, not just retained**
(`verify_inclusion`, run at publication, at draw, and in every validate):
the entry body must decode to a hashedrekord binding the manifest digest,
the retained witness signature, and the locked records public key; the
entry UUID must be the leaf hash `sha256(0x00 ‖ body)`; the entry `logID`
must equal the sha256 of the Rekor log key pinned at lock time; and the
log's `signedEntryTimestamp` must verify under that pinned key over the
canonical `{body, integratedTime, logID, logIndex}` payload — after which
`integratedTime` and `logIndex` are the log's word, not the operator's.
The raw upload response is retained.

**Uniqueness.** The binding inclusion is the single entry under the
records key. The online check (`witness`, and the freeze gate itself
re-runs it rather than trusting a file): search the log's index by each
locked public key; every returned entry must be one the protocol made
(the one lock timestamp under the lock key, the one publication under the
records key); any stranger refuses the study; the records entry must be
indexed before the freeze may proceed. Rekor's search index lags inclusion
by design, so the check retries, and the post-run review re-runs it into a
numbered retained sibling. What this cannot prove — entries under OTHER
keys, parallel unpublished attempts — is in §9.

**The round.** Locked constants: the drand mainnet default chain's chain
hash, public key, scheme (`pedersen-bls-chained`), genesis time G, and
period p = 30 s, captured at lock time from the chain-info endpoint with
the raw response retained. Registered arithmetic, integer POSIX seconds
throughout:

```
scheduled(R) = G + (R - 1) * p
T            = integratedTime + 300
targetRound  = floor((T - G + p - 1) / p) + 1     # first R with scheduled(R) >= T
```

The harness fetches **only** `targetRound` — never latest, never a
neighbor — from the two registered relays (`api.drand.sh` and
`drand.cloudflare.com`), both addressed by chain hash, and requires
byte-identical `signature` and `previous_signature` values; each relay's
raw response bytes and retrieval timestamp are retained in `DRAW.json`.
`randomness` is computed as sha256 of the signature bytes — the chained
scheme's definition. If retrieval has not COMPLETED within 3600 seconds of
`scheduled(targetRound)`, the draw refuses and the attempt is
`pipeline-invalid`. BLS pairing verification is delegated to the external
reader with every input retained (§9).

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
contiguously). The 2^256 mod 6 bias is negligible and accepted.

**After the draw** the harness re-verifies that the records commit is
unchanged and that the worktree's published paths byte-equal that commit's
tree, then applies the sampled patch to C to produce D and derives
`DEFECT.json` — sets and per-record C/D disposition tables — **from the
published commit's tree bytes**, never the worktree, using the reference
semantics only: `underC` = the mirror's verdict wrapped in the registered
outcome shape; `underD` = `underC` except on the sampled predicate, where
it is `unresolved` with the mutation's `reasonsUnderD` reason set. No
evaluator call touches table derivation; the evaluator's agreement with
the tables is exactly what E2 tests, and a divergence is
`pipeline-invalid`, never a table amendment. `validate` recomputes the
complete canonical `DEFECT.json` body from the published tree and requires
byte equality — one derivation authority, exact H/Q/F/K sets, no ghosts.

## 6. Arms, endpoints, prerequisites

Arms as Study 009 — A (circular over D), B (transcribed over D), B′
(transcribed over C) — through the **Study 010 port** of its repaired
gates: the four-pointer PNF projection (`harness/pnf_check.py`), the
complete-row fabrication gate (`harness/gate.py`), fresh-store
acquisition with receipt bijection over H ⊔ Q ⊔ K, arm isolation, the
sealed-attempt ledger, and the CLI/MCP comparison. The port is part of the
reviewed candidate; nothing is claimed "verbatim", and the 010 driver
(`harness/study.py`) is reviewed as its own artifact.

**Attempt ledger totality.** `run` refuses only if no freeze file exists
to bind to; otherwise it creates the attempt directory, its exclusive
`STARTED` marker, and the freeze-digest binding BEFORE any fallible work —
freeze verification and validation failures are crashed attempts, not
silent non-attempts. Every exit path writes a terminal state (`DONE` or
`CRASHED.json`) and seals the attempt: a content manifest whose named set
must remain EXACTLY the attempt's file set (an added `DONE` is a drifted
seal, not a promotion), plus read-only permissions — tamper-evidence
against accident, not against the owner (§9). **The primary attempt is
the first attempt started under the current committed freeze, whatever
its terminal state.** A primary attempt without `DONE` scores E1 =
`pipeline-invalid`; later attempts are sensitivity data only, recorded in
`DEVIATIONS.md`. `score` is itself total: malformed or missing retained
data writes E1 = `pipeline-invalid` with the error retained, never a bare
exception.

**E1, an ordered partition** (evaluated top to bottom; exactly one label):

1. **pipeline-invalid** — the primary attempt lacks `DONE`, or any
   prerequisite fails: the admissible-call resolution, transcript binding
   (§4), compiler regeneration, publication authentication and uniqueness,
   draw recomputation, P-A (arm A's complete deterministic self-replay),
   acquisition verification, gate admission, E2's table conformance, or
   E5's surface conformance.
2. **caught** — H ∩ F ≠ ∅ (with E2 passed, every H ∩ F row's actual
   disposition passes under C and mismatches under D; the scorer re-checks
   per row and can only demote to `pipeline-invalid`).
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

`transcription/PROMPT.txt`, byte-exact, **no trailing newline** (the fence
below shows the pre-policy text; the file continues with the full text of
`policy/POLICY.md` and the transcript binding's check compares against the
file bytes):

```
You are the records clerk of a fictional vendor-governance office. Below is
the office's screening policy. Author the decision records of 16 distinct
vendor screening cases this office decided under it, as a JSON array.

Each record: {"caseId": "<kebab-case id you invent>", "vendor":
{"legalName": <string>, "sanctionsHit": <bool>, "registeredCountry":
<string>, "handlesPersonalData": <bool>, "riskScore": <decimal string, no
trailing zeros>}, "decision": {"outcome": <"clear"|"manual-review"|
"reject">, "decidedBy": <string>, "decidedAt": <ISO 8601 UTC, like
2026-06-01T09:30:00Z>}}.

Vendors are registered in various countries; use ISO 3166-1 alpha-2 codes,
uppercase.

Make the set what a diligent office's files would look like: exercise every
clause of the policy, include the borderline cases a careful clerk would
have seen, and record the outcome the policy requires for each. Do not
include commentary — output only the JSON array.
```

The instruction is defect-agnostic by construction: it names no threshold,
no comparison, and no pack.

## 8. The two locks, and the ordering

1. **Protocol lock** (one commit, pushed, then Rekor-timestamped under the
   lock key): `PROTOCOL-LOCK.json` pins the byte digests of every locked
   input — this file, `PREREG-REVIEW.md`, `policy/POLICY.md`, pack C,
   `FAMILY.json`, `PROMPT.txt`, `record.rule.json`, `transcribe.py`,
   `authoring_call.sh`, both witness public keys, the controls,
   `record_source.py`, the harness (driver, gate, pnf, mirror, compiler,
   regions/transcript checkers, tests), and the shared line code — plus
   the pinned jpack digest, the pinned codex binary digest and version,
   the drand chain constants with the raw info response, the Rekor log
   public key, and the draw-rule constants. Lock verification is
   **canonical**: the manifest's key set must be exactly the registered
   list, every locked input must be a regular file matching BOTH the
   worktree and its HEAD blob, and the recorded constants must equal the
   registered constants — a hand-edited lock fails, it does not narrow.
   `PROTOCOL-LOCK.json` does not digest itself; its bytes are bound by the
   lock commit. The lock command refuses unless the 44-probe battery
   passes and every family patch applies to pack C. Authoring may not
   begin before this commit is pushed.
2. Authoring call (slots) → records commit → **authenticated Rekor
   inclusion of the records commit (the publication)** → push → beacon
   round → `DRAW.json` + pack D + `DEFECT.json` commit.
3. **Artifact freeze** (`FREEZE.json`): re-runs the online uniqueness
   check itself, then validates everything and pins the generated
   artifacts — call slots, records, `RECORDS.md`, D, `DRAW.json`,
   `DEFECT.json`, the witness inclusions and search — with the same
   canonical key-set and HEAD-blob discipline, binding the protocol-lock
   digest. Then `validate` → `test_study.py` → `run` (first attempt is
   primary) → `score` → `ANALYSIS.md` before quoting numbers → post-run
   adversarial review.

## 9. What is enforced, what is recorded, what is not prevented

**Mechanically enforced** (a violation refuses or scores
`pipeline-invalid`): the canonical lock and freeze manifests (exact key
sets, worktree ≡ HEAD blobs, registered constants); pack C ≡ mirror on the
44 probes; the admissible-call resolution (single completed slot, one new
session, pinned binary digest as recorded); the strict transcript
whitelist and byte bindings; compiler regeneration with the exact file
set; the publication's cryptographic authentication (body, UUID leaf
hash, pinned log key, signed entry timestamp) and the online
single-entry-per-key uniqueness check at freeze; the round arithmetic,
dual-relay raw-byte agreement, post-retrieval deadline, and index
recomputation; DEFECT.json's byte-recomputation from the published tree;
the gates, receipt bijection, and arm isolation; attempt-ledger totality
with exact-set seals and a total scorer.

**Recorded but not proven**: that the retained call slots are ALL the
invocations that occurred (an off-ledger call leaves no slot); that
`CALL.json`'s self-reported fields (binary digest, session count,
environment) describe the process that actually ran — the wrapper computes
them, and the wrapper is locked, but the operator runs the wrapper;
wall-clock claims beyond Rekor's authenticated `integratedTime` and
drand's round schedule.

**Not prevented**: entries in the transparency log under keys other than
the two locked ones — an operator could run parallel unpublished attempts
under fresh keys and publish only a favorable one; what the protocol
proves to a reader is that THIS record set was published before THIS
round, not that no sibling attempt existed (each abandoned sibling would
leave its own permanent log entries under its own keys, discoverable only
if those keys are known). Off-ledger evaluations of C or any candidate D
against the records before publication (all six patches are public; a
coverage profile is computable privately). Transient tool edits restored
before commit. BLS pairing verification of the beacon signature (material
retained; the harness checks dual-relay agreement and the randomness
definition, not the pairing equation). Re-locking after seeing records
would be visible as a second lock commit and Rekor timestamp in the
public history, but nothing mechanical forbids it — the reader checks the
graph.

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
