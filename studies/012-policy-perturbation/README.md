# Study 012 — is the blinded author's test surface anchored to the policy's surface form?

**Where this study stands is read from `harness/PINS.json`, not asserted
here.** Four registry members carry the lifecycle and each is null until its
registered moment: `freeze.preregistrationSha256` and
`freeze.treeManifestSha256` (the freeze, filled together or integrity
refuses), `golden.sha256` (§3.2's capture), `isolationNegative.assent`
(§6 C7). All four are nulled in the manifest's normalized projection, and the
run's outputs are in `freeze.excluded`, so **no act that advances this study
moves a byte this file is covered by** — which is the only reason §2.10 rule 3
terminates, and why no status sentence lives here (round 13, finding 1). The
harness is built — the digest port from Study 011 that
[`PREREGISTRATION.md`](PREREGISTRATION.md) specifies — the twenty arm
artifacts are assembled and pinned, and §6 C10's five clean-room mirrors are
commissioned and agreeing.
The preregistration is a draft until it is frozen by merge after the final
cross-vendor review round ends clean; it governs thereafter, and
`DEVIATIONS.md` records every departure from it.

**Review status: [`PREREG-REVIEW.md`](PREREG-REVIEW.md) is the count.** It
records every round — round 1 internal; round 2 the first cross-vendor round
over the specification and arm texts; every round from round 3 on over the
complete post-port candidate tree, each with every finding dispositioned by the
maintainer and the dispositions implemented before the next round. **The number
of rounds is deliberately not copied into this file.** The record sits outside
the tree manifest so that writing a round down moves no covered byte; a copy
here would be covered, so recording a round would change the manifest and §2.10
rule 3 would require a further round to attest it — and recording THAT round
would be the same change again. The freeze binds to the manifest of the round
that ends clean, and whether one has is recorded in that file's own status
line — `OPEN` while further rounds may be commissioned, `CLOSED` once the
final round has ended clean.

## What it is

Study 011 measured that a blinded authoring call reaches all six pre-committed
boundary classes in 49 of 49 valid runs. Its post-hoc census
([`DIVERSITY.md`](../011-authorship-coverage-rates/DIVERSITY.md)) measured
*how*, and the answer was that boundary placement follows **the numbers the
policy text names**: 52.3% of records sit on one of the family's three edges or
within 0.01 of one, **three** of six classes rest on two distinct probes each
and **four** of six contain a probe that appears in every one of the 49 runs,
and the whole approach band below the unstated 39 edge — (23.75, 39) — is
empty.

That is a reading, and it was published with a prediction attached. This study
writes that prediction down as one retractable proposition and calls it **R1**:

> **R1 — the boundary-hugging in Study 011's corpus is *caused* by the policy
> text naming 40 and 70. State the same rule without the literals and the
> hugging, and the coverage that rests on it, goes away.**

Renaming the thresholds should move coverage to the new numbers; **denaming**
them — stating the same rule, with the same values, without the literals —
should collapse coverage of the classes that have a numeric edge. `CLAIM.md`
carries R1's verbatim published wording, venue, URL and retrieval date, pinned
before the freeze, so the retraction target is frozen with everything else.

This study is that prediction run as a **falsifier against our own claim**.
Five arms, semantics held constant by construction, one policy text each:

| arm | perturbation | thresholds |
| --- | --- | --- |
| **A** baseline | Study 011's policy text plus the two registered deltas, re-run fresh | 40, 70 |
| **B** reworded | the five clause bodies paraphrased; literals, order and inclusivity-adjacency pattern unchanged | 40, 70 |
| **C** reordered | the bodies byte-identical, presented in a registered permutation | 40, 70 |
| **D** renamed | the threshold literals moved; family moves with them, and one parameterized mirror serves every arm | **45, 72** |
| **E** denamed | no numeric content in any clause body; the same values by reference | 40, 70 |

Two deltas from Study 010's locked text are registered, and both are in **all
five** arms so that neither becomes a second intervention in one of them. The
*conventions delta* is one sentence — "The office's risk scale runs from zero to
one hundred." — without which arm E's threshold definitions would smuggle new
semantic information into arm E alone ([D-15]). The *preamble delta* replaces
"Study 010" with "this study", so that no arm hands its author a name-keyed
pointer to a public repository whose policy states 40 and 70 ([D-16], adopted in
round 2). Both are published verbatim and pinned by sha256; `PREREGISTRATION.md`
§2.1, §2.5 and §10 state what each costs — including that removing the pointer
does **not** remove residual memorization of a corpus public since 2026-08-06.

30 runs per arm, interleaved in a **first-order carryover-balanced order** so
that no arm owns a time slot *and* no arm is systematically preceded by any
other; per-class per-arm coverage rates over the **scheduled** slots
(intent-to-treat) with exact Clopper–Pearson 95% intervals; the pipeline-invalid
rate as its own endpoint per arm, with a published sensitivity bound on every
primary rate; and the probe census — distinct probes per class,
threshold-distance buckets — promoted from Study 011's post-hoc addendum to a
**registered secondary**.

The decision rule and the four predictions are registered before any call, with
their falsification conditions written down (`PREREGISTRATION.md` §5), **as one
ordered, exhaustive decision table** whose first matching row is the outcome and
whose last row always matches. Over the four narrow numeric classes: **placement
collapse** — arm E's *raw* records leaving the boundary, not merely its
correctly-labelled ones — on ≥ 3 of 4, with arm E's S5 labels at the
ceiling (§4.6), the B/C control gate holding and arm E reading LOW on neither
class 4 nor class 3, is CONFIRMED; arm E reading HIGH on ≥ 3 of 4 is
R1-UNSUPPORTED; coverage collapsing while the raw records stay on the boundary
on at least one of them is LABEL-COLLAPSE-ONLY; and every other pattern —
including all-MID, which N = 30 makes the likely shape of any *partial*
effect — is INDETERMINATE with R1 recorded as neither confirmed nor unsupported. Three gate rows sit above all of
them: an incomplete batch, arm E reading LOW on class 4, and a failed control
gate each adjudicate R1 in **neither** direction. The condition that matters
most:

> **If arm E maintains coverage, R1 is published as UNSUPPORTED, with the same
> prominence as the claim** — in `ANALYSIS.md`'s first paragraph,
> at the head of [`CORRECTION.md`](CORRECTION.md), linked from this block,
> in the venue `CLAIM.md` records, and as a correction banner at the
> head of Study 011's `DIVERSITY.md`. What is retracted is R1; the census's
> descriptive sentence about its own corpus stands regardless. **And the
> correction says one more thing in the same paragraph: this study does not
> thereby establish the opposite.** Maintained coverage is compatible with the
> author deriving the boundaries *and* with the author reproducing a policy
> family it has seen before, and this design separates neither.
>
> `CORRECTION.md` is written in **every** outcome and is one of
> `harness/PINS.json`'s `freeze.excluded` outputs, so this link is frozen
> before the data and cannot be dropped afterwards without moving the digest
> the final review round attested — and an absent `CORRECTION.md` is a visible
> failure to publish rather than an outcome. This README is inside that
> manifest, which is why the correction is written there and pointed at from
> here (§8, §2.10 rule 3).

Arm A is re-run rather than read off Study 011 for one reason, and it is not
elapsed time: 011's 49 runs were produced on 2026-08-07 — the same day this
study was drafted, a few hours earlier — against a model snapshot whose drift
since is **uncontrolled and unmeasurable from here**, and no pin in this
repository can rule it out. A provider-side snapshot can move between two calls
a minute apart. Those runs are **historical reference, not this study's
comparison arm**; every registered contrast is within this batch.

**What N = 30 cannot do, said here rather than only in §9.** At a true
per-class coverage of 0.95 — inside Study 011's own published interval — arm A
reads HIGH on all six classes 77.8% of the time under the scenario that respects
§2.3's class nesting, and at least 75.7% by the sharp Fréchet floor (68.7% and
63.5% under the independence layer §5.4 published for nine rounds, which counts
six classes as six free events and cannot happen — round 10, finding 4). So
roughly two runs of this study in ten would find at
least one falsifier-relevant class with no contrast verdict available, from
sampling alone. The design's own control gate passes 67.0% of the time under the
coherent scenario (76.6% under the independence layer, which overstates it: a
five-of-six tolerance gets harder, not easier, when classes move together), so
about one run in three adjudicates R1 in neither direction. And
any anchoring effect that leaves coverage above roughly one run in five is
invisible: a drop from 1.00 to 0.30 reads MID 99% of the time. Every figure is
computed before the data and asserted by a harness test.

**N was 25 in the round-1 draft, and the cross-vendor round moved it.** The
argument was not the marginal per-class figure, which rises only 0.8729 →
0.9392; it was the registered B/C control gate, which passes **0.4031 at N = 25
and 0.7658 at N = 30** — **0.4010 and 0.6702** once the class nesting is
respected, which is the reading that counts and returns the same decision. A
precondition that fails three times in five when both
control arms behave exactly as predicted is not a control. `PREREGISTRATION.md`
§5.4 and §10 [D-1] carry the whole re-adjudication, with N = 25 registered as
the alternative and its cost stated.

## How it relates to what came before

- [`009-transcribed-oracle-matrix`](../009-transcribed-oracle-matrix/) —
  established the transcription pipeline as a constructed existence witness.
- [`010-blinded-oracle`](../010-blinded-oracle/) — removed the circularity:
  records authored by a model that never saw a pack, against a defect drawn
  after publication. Result `caught`, 6/6 coverage. Its `PROTOCOL-LOCK.json` is
  the ultimate authority for **the mirror module, arm A's family, arm A's policy
  source, and the prompt bytes 011 pinned** — and **not** for the compiler, the
  transcript checker or the wrapper, all three of which Study 011 *adapted*, so
  the bytes this study ports are 011's and 010's lock is their ancestor rather
  than their authority.
- [`011-authorship-coverage-rates`](../011-authorship-coverage-rates/) — turned
  the existence result into rates: 49/49 on every class, every class LIGHT under
  the tier mapping it registered before the data. Then its census asked what
  49/49 stands on and found the answer was **two distinct probes in three of six
  classes, and a probe present in every run in four of six**. **This study
  exists because that census's reading was published as a claim rather than as
  a measurement.** Its
  [`MIRROR-AGREEMENT.md`](../011-authorship-coverage-rates/MIRROR-AGREEMENT.md)
  is the clean-room-second-mirror instrument this study ports as C10 — with
  five texts instead of one, and with the pre-data verdict registered in
  advance: an arm E whose clean-room reader cannot derive (40, 70) from the
  text alone is an ambiguity arm, and it is re-authored before the freeze
  rather than run.
- **This study** ports 011's batch driver, integrity chain, admission codes,
  transcript gates, interval arithmetic and census arithmetic **by digest**, with
  an enumerated change list bound row by row to the authority each file actually
  has (010's lock, 011's registry, or 011's own adapted bytes), and adds exactly
  one thing 011 did not have: five policy texts instead of one, each a
  registered artifact pinned by sha256 before any call, each keyed to one
  registered mirror module through its own pinned `ARM.json`, and the six
  boundary classes keyed **semantically** so they are the same six classes at
  whatever thresholds an arm carries.
- Tracker: evaluator-experiments **issue #45**, whose body registers this
  mandate.

## How to run it, once frozen

The batch is API-dependent and non-deterministic, so it runs **manually, never
in CI**. The deterministic controls and fixtures do run in CI: the
`study-012-harness` job runs the whole `harness/tests` suite, including the
three-tier ported-bytes chain, the two replication controls, the arm-artifact
checks (structure, censuses, the inclusivity-adjacency tuple equalities, arm C's
permutation properties **re-derived by exhaustive enumeration rather than
compared against a hard-coded tuple**, the **280-cell** grid with its registered
negative control, the five clean-room mirrors), the **registered call order's
position and directed-transition counts**, the fixtures — including the
`arm-mismatch`, `schedule-mismatch`, `session-reused`, manifest-alteration,
per-arm-prompt and decision-table fixtures — the interval vectors and the
operating characteristics **for the rules this study actually registers**, the
registered-illustration check on this study's own prose (including Appendix A's
five policy texts), the **whole-tree manifest** recorded by the final
`PREREG-REVIEW.md` round, and the wrapper-driven batch tests against a stand-in
CLI.

**The interpreter is a pin, not a detail**, as in Study 011: the registry names
CPython 3.12, and `integrity.py`, `batch.py`, `score_rates.py` and the wrapper
all refuse under another implementation or version series. Every command below
names it explicitly through `$PY`, by absolute path. The three path-invoked
entries also refuse unless that interpreter is running with the **safe import
path** — `-P`, or the `PYTHONSAFEPATH=1` step 0 exports — because a file
invoked by path makes its own directory `sys.path[0]`, and its head imports
resolve from there before any scan inside it can run (round 10, finding 1).

`DIR` is a scratch parent that resolves **outside every git worktree** and
carries no leak token (a path containing `jpack`, for instance, is refused).

```sh
cd studies/012-policy-perturbation

# 0. The registered interpreter, BY ABSOLUTE PATH.
PY=/home/onword/.pyenv/versions/3.12.11/bin/python3 && "$PY" -V
#    …and the SAFE IMPORT PATH, for every command below. Running a file by
#    path puts that file's own directory first on sys.path, so an entry
#    file's head imports — `subprocess` among them, which is what the
#    untracked-source scans ask git what is tracked with — resolve from the
#    very directory those scans exist to police, before a byte of them runs.
#    All three entry files REFUSE without it (§2.10, round 10 finding 1).
export PYTHONSAFEPATH=1

# 1. Ported bytes (§6 C1), the three-tier authority chain plus 011's PINS
#    AND PORTS and this study's own PORTS at their pinned digests, the five
#    arm artifacts (§6 C8: prompt equation, document structure, literal
#    census, arm B's inclusivity-adjacency tuples, arm C's four ordering
#    conditions, the 280-cell landmark grid against the single registered
#    mirror at each arm's registered pair), the class schema per arm
#    structurally (§6 C9), the five clean-room mirrors agreeing on that grid
#    (§6 C10), the whole-tree manifest recorded by the final PREREG-REVIEW.md
#    round, and the interpreter. Deterministic, offline, and also a
#    precondition of steps 4-7. It REFUSES while any "(port time)"
#    placeholder is still in PORTS.md or PINS.json.
"$PY" harness/integrity.py

# 2. The harness suite: fixtures, both replication controls, interval
#    vectors, admission codes, the level/contrast rule diffed against
#    PREREGISTRATION.md §5, and the batch driver against a stand-in CLI.
"$PY" -m pytest harness/tests -q

# 3. Freeze the preregistration: put its sha256 into harness/PINS.json
#    BOTH freeze pins — freeze.preregistrationSha256 AND freeze.treeManifestSha256,
#    the latter equal to the final round's attested digest in PREREG-REVIEW.md
#    (they land together or integrity refuses, §2.10) — and COMMIT. Nothing below will make a call or
#    compute a rate while that member is null.
sha256sum PREREGISTRATION.md

# 4. The golden-context recapture (§3.2). ONCE for the whole batch, not per
#    arm: it uses the arm-independent probe prompt, and the pre-prompt
#    context precedes the prompt. TWO probe calls; the capture is derived
#    only if they agree, and only from distinct sessions.
#
#    LEAVE --captures AND --out AT THEIR DEFAULTS. The attempts land in
#    controls/recapture/ and the capture in transcription/GOLDEN-CONTEXT.json,
#    both of which harness/PINS.json excludes from the §2.10 tree manifest.
#    This is not advice: naming any other place inside the study REFUSES,
#    because §8 retains the attempts and the bytes retained under an
#    unexcluded path would move the manifest the final review round attested
#    (round 18, finding 1 — --captures had this sentence nowhere, and no
#    check either).
"$PY" harness/batch.py capture --scratch-parent DIR
#    Then put the printed digest into harness/PINS.json golden.sha256 and
#    COMMIT both. From here on PINS.json is not edited: the batch stamps its
#    digest into every slot, and a later edit refuses the scoring. (That
#    rule is §2.10's, and it is scoped: the registry is never edited BETWEEN
#    THE BATCH AND THE SCORING; the assent edit in step 5 happens before the
#    batch and touches one of the four registered post-freeze members, which
#    the manifest's normalized projection nulls — no contradiction, and
#    round 8 finding 11 is why this parenthesis exists.)

# 5. The isolation negative control (§6 C7), ONCE. FIRST record the
#    operator's assent: edit harness/PINS.json isolationNegative.assent from
#    null to the exact string "granted" and COMMIT — this is one of the four
#    registered post-freeze members, outside the manifest's normalized
#    projection, so the freeze binding is untouched (§2.10); the command
#    refuses while it is null. One probe call with the real HOME, expected to
#    FAIL the golden match. Exits non-zero if it reached neither comparison.
#    Step 6 REFUSES until this record exists: the batch reads the assent and
#    the verdict before it creates a slot, and so does the scorer (§6 C7).
#    Leave --out at its default — the precondition reads the canonical
#    controls/isolation-negative/ and consults no flag.
"$PY" harness/batch.py capture-isolation-negative --scratch-parent DIR

# 6. The batch: 30 rounds x 5 arms = 150 sequential slots into
#    arms/<ARM>/authoring/run-NNN/, in §2.8's registered carryover-balanced
#    order: each arm holds each within-round position six times, and every
#    ordered pair of arms occurs 7 or 8 times across all 149 transitions.
#    The driver retains bytes; it computes no coverage and no verdict.
#    THE DRY RUN COMES FIRST — it creates nothing.
"$PY" harness/batch.py run --scratch-parent DIR --dry-run
"$PY" harness/batch.py run --scratch-parent DIR
#    After a crash, resume at the ledger's next GLOBAL INDEX, after the
#    recorded prefix is verified against the registered order slot for slot.
#    There is no --start-round: a round number cannot resume a partly
#    completed round without overlapping or omitting slots (§10 D-22).
"$PY" harness/batch.py run --scratch-parent DIR --resume
#    A batch that cannot finish, declared BEFORE anything is scored. It
#    records the reason, the completed schedule prefix and that slot's UTC
#    wall clock. ANY incomplete batch is descriptive-only: every verdict is
#    UNRESOLVED-BY-DESIGN and no contrast is reported, at any round and for
#    any reason (§2.8 D-21).
"$PY" harness/batch.py shortfall --reason "why it could not finish"

# 7. The scorer: admission, compilation, per-arm classification, rates,
#    intervals, the census, the §5 level/contrast/placement verdicts and the
#    §5.3 decision-table row. This command IS the registered scoring
#    interface and it is the only thing that publishes. --emit-records is its
#    WHOLE argument surface: the slots root, the registry, the arms, the
#    prompts, the families, the mirrors and the golden capture are all
#    derived from the harness's own location, and any other argument REFUSES
#    rather than being ignored (§10 D-23). It writes RESULTS.json, RATES.md
#    and CENSUS.md to the study root.
"$PY" harness/score_rates.py score --emit-records records

# 8. Read RESULTS.json's schedule.utcDay. If crossedMidnight is true, write the
#    DEVIATIONS.md entry §2.8 requires — the crossing stops nothing and the
#    scorer refuses nothing on it, so the entry is the operator's to write.
#    Then ANALYSIS.md, then post-run cross-vendor adversarial review.
```

Ordering rules, per `PREREGISTRATION.md` §2.8, §2.10 and §3.2.

**Checked in code**, and a violation refuses: N is fixed at 30 per arm in the
registry before the batch; every arm artifact is pinned by digest before any
call and re-verified before every slot and before scoring; no call is made while
the preregistration's freeze digest is unregistered or does not match; no slot is
created while `golden.sha256` is null or the file at the golden path does not
hash to it, out of the registered call order, or after `RESULTS.json` exists;
every slot records the arm, the arm prompt digest, its global schedule index,
the registry digest and the golden digest it was made under, so a slot made with
the wrong policy text scores `arm-mismatch` and a slot copied, renamed or
duplicated *within* its own arm scores `schedule-mismatch`; the ledger and the
slot set must be in bijection and the ledger's sequence must be a prefix of the
registered order; no two slots may share session evidence (`session-reused`);
every slot is sealed by a manifest chained into the ledger, and an alteration
makes the whole batch `UNRESOLVED-BY-DESIGN` rather than moving one slot out of
a denominator; a shortfall may not be declared over a batch that is not short;
and the scorer refuses unless the batch is terminal. **Computed and published
rather than enforced**: the UTC calendar dates the slots' own stamps carry, the
count of slots that carried no readable pair, and a crossed-midnight flag
(`schedule.utcDay`) — §2.8 makes a crossing a `DEVIATIONS.md` entry and not a
stopping rule, so nothing refuses on it.

**Ledger discipline, recorded and not checked**: that the golden capture, the
registry and the five arm artifacts were *committed* before round 1. This study
has no lock-commit machinery and compares nothing to a `HEAD` blob, and the
per-slot manifest chain is computed by the same operator who holds every input
to it — it makes a later alteration visible, it does not prove contemporaneous
recording. The other things **not** prevented, stated rather than papered over:
the operator reading a `completion.txt` by eye mid-batch — which in this study
would be reading the answer, since the operator holds a prediction; **the
in-process route**, where a library caller imports the scorer and computes arm
E's rate early, publishing nothing and leaving the guard unarmed; and the fact
that the perturbations were authored by the same team that published that
prediction — **three of the five arms as substantive prose, not two**.
`PREREGISTRATION.md` §7 and §9 state all three with the mitigations and their
limits. What round 2 changed is what an early look could *buy*: any incomplete
batch is descriptive-only, so stopping early forfeits the study's conclusion
outright rather than merely narrowing it.

## Reading order

1. [`PREREGISTRATION.md`](PREREGISTRATION.md) — §1 the question and **R1**, §2
   the five cells and their pins (§2.3 the six semantically-keyed classes, §2.4
   how "semantics constant" is checked, §2.5 what arm E can and cannot be), §3
   admission and the run-026 rule, §4 the endpoints and the exact interval
   procedure, **§5 the registered decision rule, the four predictions and their
   falsification conditions**, §6 the controls, §7 what is enforced, recorded and
   not prevented, §9 bounds, **§10 the register of pre-freeze decisions**, and
   Appendix A the five policy texts in draft.
2. `CLAIM.md` — R1's verbatim published wording, venue, URL and retrieval date.
   Short, and it is the thing §8 promises to retract.
3. `PREREG-REVIEW.md` — every pre-freeze review round, every finding, every
   disposition, **the sha256 of each of the five arm texts as that round
   reviewed them**, and — from the first post-port round on — **that round's
   whole-tree manifest digest**. `integrity.py` refuses unless the manifest it
   recomputes over the frozen tree equals the final round's, so everything the
   manifest covers is what ran: the texts, the harness, the scorer, the
   preregistration and this README. `PREREG-REVIEW.md` is the exception — it
   carries the attestation the freeze pin must equal, so it sits outside the
   manifest and its own honesty is [D-20]'s stated residual (§2.10). Round 2
   found the previous binding was self-authenticating.
4. `harness/PORTS.md` — what each ported file changed, at which digest, and to
   which authority each row is bound. Written at port time.
5. `arms/A…E/` — the five registered artifacts, authored and pinned at port
   time; until then, Appendix A of the preregistration carries their drafts.
   Read them before reading any result: they are the intervention, and whether
   they are what the preregistration says they are is a judgment no digest can
   make for you.
6. `MIRROR-AGREEMENT.md` — C10's five clean-room mirrors, each written from one
   arm's `POLICY.md` bytes plus the published fixed interface (a 28-byte
   prefix and 678-byte suffix around the policy minus its final LF —
   equivalently 705 non-policy bytes against the full file; the equation is
   in `MIRROR-AGREEMENT.md`) and nothing else, with the pre-assigned reader
   roster, **every attempt including every failed one**, and the per-arm
   280-cell agreement table. Read it beside `arms/` — it is the one pre-data
   check that can tell "denamed" from "written to be hard".
7. `DEVIATIONS.md` — empty until something departs — and
   [`CORRECTION.md`](CORRECTION.md), written in every outcome, naming the
   decision-table row the scorer computed and, on §5.3 (i) row 4, carrying the
   R1-UNSUPPORTED correction the block above commits to.
8. `RESULTS.json`, `RATES.md`, `CENSUS.md`, `ANALYSIS.md`, `CORRECTION.md` and
   the compiled record trees under `records/` — the run's outputs, written by
   steps 7 and 8 of the ceremony above and by nothing earlier. Every one of
   them is in `harness/PINS.json`'s `freeze.excluded`, so none is covered by
   the tree manifest.

Byte-lineage, not truth: this study measures where independently authored
records land when the policy's surface form is perturbed and its decision
structure is held fixed. It does not establish that the records are true, it
evaluates no pack and measures no defect detection, and it makes no conformance
claim of any kind.
