# Preregistration — Study 021: does replayed history catch a planted defect, and can the profile tell a moved line from the rest?

**Status: FROZEN by the squash-merge of the pull request `PREREG-REVIEW.md` names; governing
thereafter.** Eight pre-freeze cross-vendor review rounds concluded with `freezable as written`
(`PREREG-REVIEW.md`). After the freeze this file is never edited — corrections go to
`DEVIATIONS.md`.

**Nothing has run under a freeze: as of the freeze commit no registered attempt exists.**
Everything executed during harness development lands under `pilots/`, is labeled harness
validation, and supports no claim. The registered cells
below were derived from the packs' text and the runtime's documented semantics; the pilots
informed which structures needed naming, and every cell says which structure it names. Said
plainly, because the apparatus is deterministic: the pilots drew random ledgers from seeds
1–30 and the registrations were checked against them before the freeze; the registered attempt
draws seeds **101–130**, which no pilot has drawn, so the random-stratum cells are adjudicated
on ledgers the registration never saw. The literal stratum is one deterministic ledger per
policy and its cells are, by construction, checked in the pilots — those cells register a
reading of the pack's text, and what the registered attempt adds for them is only that the
pinned release behaves as the development binary did.

Two companion artifacts are registered *with* this document and pinned at the freeze:
`harness/MATRIX.json` (the registered cells and their expectations) and
`harness/MATRIX-HOLDOUT.json` (the reviewer's holdout cells, authored during review and
kept byte-for-byte). Where prose here and those artifacts could diverge, the artifacts govern.

## The freeze and the primary attempt

- **Freeze commit**: the squash-merge commit of pull request #105, named in `PREREG-REVIEW.md`.
- **Runtime**: the judgment-pack runtime release **v0.21.0**, the first carrying the history
  profile (runtime ADR-0034), pinned by the digest of its published linux/amd64 binary in
  `harness/PINS.json`; the scorer refuses any other binary. That one member is filled after
  the freeze, by a single commit made when v0.21.0 publishes, carrying the published binary's
  digest and touching nothing else — `harness/PINS.json` is outside the manifest for this
  reason, and `DEVIATIONS.md` names that commit; until it is filled the runner refuses to
  start a registered attempt, so no registered draw can precede the pin.
- **Primary attempt root**: `results/primary-attempt-001` — literal, must not exist at the
  freeze; the runner refuses an existing root, and the first invocation of the governing
  command is the primary attempt, crash and all.
- **Governing invocation** (fully offline; the runtime and CPython 3.12 only), one command:

      python harness/run_attempt.py --attempt-root results/primary-attempt-001

  The runner first holds the pins — every freeze pin non-null and matching its file, the
  runtime's digest equal to the pin, the manifest equal to the tree — and refuses to start
  otherwise, so no reserved seed is drawn under a null or mismatching pin; then creates the
  root exclusively (an existing root, whatever it holds, is refused); writes `ATTEMPT.json`
  first — an attempt id, the label, the runtime's version and digest, the raw digest of
  `harness/PINS.json`, the reserved seeds and sizes, the policies — and only then builds every
  ledger with the reserved seeds (`--reserved`, which the builder allows only under a valid
  registered marker in the attempt root), plants every defect, replays every cell with the
  unplanted gate, and scores with the holdout. Every record the attempt writes — the defect
  index, the gate record, the cells — carries the attempt id, and every cell carries the digest
  of the ledger and of the defect pack it replayed; an output is written once and never
  overwritten. A crash after the marker leaves the marker: the root is spent, and a second
  attempt needs a new root named in `DEVIATIONS.md`.

## 1. Question

A pack drafted from policy documents is tested against the decisions that were actually made
under the policy: each past decision becomes a matrix row whose facts are what was on file and
whose expectation is what was recorded, never what the draft produces (runtime ADR-0034; the
plan's rule: *documents write the rules, past decisions test them, the two never cross*). The
runtime replays the rows and reports, beside the mismatches, a **profile**: agreement by origin,
coverage by origin, and at each threshold the pack draws how many past cases sit below, at and
above it and how many of those disagree. Two questions, both about the mechanism and neither
about any model:

1. **Catch.** When a mechanical defect is planted in a pack, does replaying a ledger of decisions
   made under the unplanted pack catch it — and how does that depend on the defect's class,
   on where the ledger's cases came from, and on how many there are?
2. **Masquerade.** A moved threshold is the one defect the profile was built to show. When a
   defect of another class is caught, how often does the profile's threshold report carry the
   same signature a moved line carries — so that a reader would take a defect for a policy
   change, or a policy change for a defect?

**R1 (primary, retractable):** for every registered cell in `harness/MATRIX.json` (and, with
`--include-holdout`, the holdout matrix), the observed value of the cell's endpoint lies within
its registered interval. A divergence in any cell falsifies R1 — including a detection on a cell
registered as undetected, and a signature on a cell registered as carrying none: a replay that
caught what the ledger cannot see, or a profile that told a defect from a moved line where the
registration says it cannot, would each be a defect in the registration's account of the
mechanism, and must be able to falsify it.

**R2 (descriptive):** the catch-rate curves — per policy, per defect **instance**, per n on the
random stratum — with exact 95% Clopper–Pearson intervals, exact because an instance's thirty
seeded ledgers at one n are independent draws; the literal stratum's one deterministic ledger
per policy reported as a count and a rate with **no interval**, since it is not a sample of
anything; per defect class the random counts pooled over the class's instances, which share
ledgers, with a binomial *reference* interval that carries no nominal coverage claim; and the
signature table — per instance and per class, among the **caught** cells (a caught cell whose
pack draws no threshold counts as carrying none, and is counted separately as threshold-free),
the fraction carrying the line-moved signature, with the same kinds of interval and the same
exclusion of the literal stratum. Published whichever way they land, and read only with the
registered structural account beside them.

This is **not an interoperability study** and not a model study: no external component and no
language model exists anywhere in the apparatus. It measures what one runtime mechanism can and
cannot show about one kind of history, study-internal end to end; its claims are correspondingly
narrow (§9).

## 2. Apparatus and pins

- **Runtime only** (D-1): every evaluation, candidate derivation and replay is the pinned
  `jpack` binary; the harness is CPython standard library, and writes the projects the runtime
  reads (`configVersion "3"`, one pack, one matrix) into temporary directories.
- **Policies** (D-2): the four packs of the demo's enterprise project, vendored byte-for-byte
  under `fixtures/policies/` with a manifest — `expense-approval`, `sanctions-screening`,
  `data-request-intake-triage`, `vendor-onboarding` — each with a **base row**: the first row of
  its own reviewed matrix, a complete applicable case the pack decides without escalation. They
  are the policies the runtime's own examples were written against; they were not authored for
  this study, and nothing in them was changed.
- **Pins are enforced, not declared**: before reading a cell the scorer compares the runtime's
  digest with the pin, each of the preregistration, the matrix, the holdout matrix and the
  manifest with its pinned digest where one is filled, and the manifest with the tree; a
  mismatch refuses the run. A registered adjudication further requires every pin non-null,
  the holdout included and non-empty, and the attempt marker parsed and matched — label
  `REGISTERED`, runtime digest equal to the scorer's runtime and to the pin, pins digest equal
  to the current `harness/PINS.json`, seeds 101–130, the registered sizes and policies — and
  refuses on any mismatch rather than falling back to a pilot label; a pilot adjudication
  requires a marker that says `PILOT`. The runner records the runtime's identity when the
  ledgers are built, and the scorer holds its own runtime to it.
- **Determinism**: every random ledger is drawn by `random.Random("021:<policy>:<n>:<seed>")`;
  two builds of the same ledger are byte-identical — a harness test asserts it, and the scorer
  rebuilds one random ledger per policy under the pinned runtime and compares bytes (G3).

## 3. Scenario

For each policy, a **ledger** is a matrix whose rows are cases decided under the *original*
pack: the expectation of every row is that pack's own disposition, read off a rehearsal
evaluation (runtime ADR-0028: nothing is recorded), never authored and never taken from a
perturbed pack. A **defect** is one mechanical edit to the pack (§4). A **cell** replays one
ledger against one defective pack with `packs test` and records whether any row mismatched, how
many, and the profile's threshold report.

Two ledger strata, registered as different kinds of history:

- **`literal`** — the literal-adjacent stratum: the runtime's own `packs suggest` candidates
  (every literal the pack compares, one unit either side at the authored precision, midpoints
  between adjacent literals, one unit outside the outermost; each enumerated member; each
  evidence requirement present, absent and unknown), each candidate's sparse facts **overlaid
  on the base row** so that one pointer moves at a time and every other holds the base's
  value, decided under the pack. The overlay has two consequences the stratum owns: the
  candidate `suggest` emits with no facts at all — its absence probe (runtime ADR-0024) —
  becomes a duplicate of the base case, so **fact absence and its `onUnknown` paths are outside
  this stratum**; and a candidate's own evidence availability, where it states one, replaces
  the base's for that requirement. One ledger per policy, deterministic. It stands for a
  history whose cases happen to sit where the policy draws its lines — the best case for
  replay.
- **`random-<n>-<seed>`** — the random stratum: n cases drawn over the pack's own pointer
  domains (an ordered literal's pointer **discrete-uniform over the lattice** [0, 2 × its
  largest literal] at the literal's precision, so every lattice value has probability
  1/(2L+1) in units; an enumerated pointer uniformly over the pack's literals plus one value
  outside them, weighted as one more member; applicability pointers always inside the domain the
  pack applies to; booleans uniformly; every evidence requirement present or absent uniformly),
  decided under the pack. A draw the runtime refuses, or one the pack does not apply to, is not
  a decision: it is dropped and redrawn, and a generator that cannot fill a ledger fails the
  construction rather than returning a short one. n ∈ {5, 10, 20, 50}, thirty seeds each; the
  registered attempt draws seeds 101–130, which the builder refuses except under a valid
  registered attempt marker in the output root, itself written only after the pins held. It
  stands for a history that never aimed at the lines. Two bounds of this generator, stated as
  its own: it pools every literal a pointer is compared against, whether in the applicability
  or in a rule, so a pack whose applicability shares a pointer with a rule would draw that
  pointer from the applicability's domain alone (none of the four does); and its case
  distribution is one among many a real history could have (§8).

## 4. Defect classes

Nine classes, each planted at **every site the pack offers**, every instance validated by
`jpack spec validate` and dropped with a note if the edit leaves an invalid pack:

| Class | Edit |
|---|---|
| D1 `threshold-up` | an ordered literal moved up by a quarter of itself, rounded half-to-even at the literal's authored precision, and by one unit at that precision where a quarter rounds to nothing |
| D2 `threshold-down` | the same, down |
| D3 `boundary-flip` | `greater-than-or-equal` ↔ `greater-than`, `less-than-or-equal` ↔ `less-than` |
| D4 `comparison-reversed` | greater ↔ less, or-equal kept |
| D5 `outcome-swapped` | a rule's outcome replaced by the first other outcome the pack declares |
| D6 `condition-dropped` | one condition removed from an `all` of two or more |
| D7 `enum-member-replaced` | one member of an `in` list, or an `equals` string literal, replaced by a value outside the domain (applicability excluded) |
| D8 `exception-effect-changed` | escalate → force the pack's first outcome; force-outcome → escalate |
| D9 `fallback-changed` | `fallbackOutcome` replaced by the first other outcome |

D1–D4 are the classes a moved or mis-drawn line produces; D5–D9 change what the pack says
without moving a line. A **policy change** in this design *is* a D1 or D2 edit: the artifact of
a deliberately moved threshold and of an accidentally moved one is the same document, which is
why the masquerade question is asked of the profile and not of the pack.

## 5. The registered signature

The **line-moved signature** is read off `profile.thresholds`, per **pointer**, across origins:

> exactly one pointer carries disagreeing rows at all; at at least one of that pointer's
> literals every disagreeing row lies strictly on one side of it (below xor above) and none at
> it; and every mismatched row of the replay is **placed** on that pointer — the profile's
> below, at and above buckets account for all of them.

Read per pointer, not per literal, because a pack may compare one pointer against several
literals (a rule's guard and an exception's mirror) and the profile lists one entry per literal
while the rows that disagree are the same rows; and the one-side condition is **existential
over the pointer's literals**, so a retained literal that every changed case lies on one side
of satisfies it even where a moved literal has a changed case at it. The placement condition
is there because the profile places only rows whose value it can compare (runtime ADR-0034): a
mismatched row with the pointer absent, or whose value is not a decimal of Core §2.2's grammar,
sits in no bucket, and a signature over the placed rows alone would say nothing about it. A cell whose pack draws no threshold carries
no signature; a caught cell with mismatched rows and no threshold disagreeing is *caught
off-threshold*, and carries none.

What the signature is for: a reader of the profile who sees it would conclude "the line moved".
The study measures how often that conclusion is right.

## 6. Cells and their registered expectations

`harness/MATRIX.json` registers cells of two endpoints:

- `caught` — the fraction of a defect instance's replicate ledgers (in a stratum, at an n) in
  which the replay mismatched at least one row; registered as an interval [min, max];
- `lineMovedWhenCaught` — among the caught replicates, the fraction carrying the signature;
  registered as an interval, with `allowsNoCaught` where the registration expects no catch.

Each cell names the structure in the pack's text that its expectation follows from. The
structures, registered once and applied per cell:

- **S1 — coincident guards.** Where a rule's own ordered guard and an exception's mirror sit at
  the same literal on the same pointer (`vendor-onboarding`: `approve-standard`'s
  `annualSpendUsd < 250000` and `committee-review-threshold`'s `≥ 250000`), a D1 or D3 defect
  at the *rule's* site is masked by the exception on every ledger: the rows the moved or
  flipped guard would newly admit are the rows the exception escalates. Registered
  **undetected** on both strata.
- **S2 — a rule whose outcome is the fallback.** A rule that decides what the fallback decides
  (`vendor-onboarding`: `request-info-incomplete` → `request-info`; `data-request-intake-triage`:
  `clarify-incomplete-or-not-evaluable` → `clarify-return`) is unobservable to a replay of
  dispositions where it fires alone: a D7 edit that stops it firing changes the trace and not the
  disposition. It *is* observable where another rule can fire with it — the two together are a
  `conflict` (Core §8.3) where one alone decides — so the registration is per literal: undetected
  on both strata for the literals no other rule's condition can share (`vendor-onboarding`'s
  two; triage's `pending` and `not-evaluable`), detected for triage's `incomplete`, which the
  hard-fail case fires beside `decline-hard-appropriateness-failure`.
- **S3 — boundary flips and random history.** A D3 flip changes the disposition of a case
  exactly at the literal and of no other. The literal stratum holds that case; a random draw at
  the literal's precision over [0, 2L] hits it with probability 1/(2L+1) per row, and the case
  must also satisfy whatever else the rule needs. Registered **detected** on the literal stratum
  (where not masked by S1), and on the random stratum at n = 50 registered per policy from that
  probability: `vendor-onboarding` (1/500001) in [0, 0.1]; `expense-approval` (1/151, and the
  case must be permitted and receipted) in [0, 0.25]; `sanctions-screening` (1/3) in [0.9, 1].
  A flip caught on the random stratum carries no signature: every changed case sits AT the
  literal.
- **S4 — evidence guards under a required-evidence escalation.** Dropping an `evidence-present`
  condition (D6) from a rule whose requirement the pack marks `required` changes nothing the
  ledger can see: a case with that evidence absent escalates on the requirement before any rule
  fires, and a case with it present fires the rule either way. Registered **undetected** on both
  strata.
- **S5 — one-sided sites.** A defect whose disagreeing cases all lie on one side of the pack's
  sole threshold — because the rule or exception it edits fires only on that side, because the
  other side is escalated by an exception before the edit can matter (a true escalating
  exception blocks a forced outcome, Core §8.3), or because a reversed comparison's own side is
  the escalated one — carries the line-moved signature whenever it is caught. Registered
  **signature = 1** at n = 50 for the named D4, D5, D6, D7, D8 and D9 instances of
  `vendor-onboarding`, `expense-approval` and `sanctions-screening` whose site is one-sided by
  the pack's text; these are the registered masquerades. Two qualifications the text also
  gives, each a statement about the **support** of the changed cases that becomes a
  finite-ledger prediction in the matrix: a changed case that sits exactly AT the literal
  breaks the signature when no other literal of the pointer qualifies, so a site whose changed
  cases include the literal itself registers a signature near 0 with the probability that a
  ledger happens to hold only its other changed cases (`sanctions-screening`'s matched literal
  1 in D5-06: [0, 0.1]) or exactly 0 where every changed case sits at it (its D2, whose moved
  literal 0 is the floor of the domain, as S7 says), and one
  whose changed cases reach the literal with a computable probability registers an interval
  from it (`expense-approval`'s fallback, reached at 75: [0.8, 1]; `vendor-onboarding`'s
  exception moved at 250000 in D8-23: [0.95, 1]); and an edit that removes the pack's only
  ordered comparison (`expense-approval` D6 dropping the amount guard) leaves no threshold to
  report, so it is caught off-threshold and carries none.
- **S6 — two-sided sites.** A defect whose changed cases lie on both sides of a threshold in
  their support (D4 reversing the sole comparison; a D7 edit to a category member that changes
  cases at every amount) carries the signature on a random ledger only when the ledger happens
  to hold changed cases on one side alone — which is a matter of how many changed cases a
  ledger holds: with about nineteen (`expense-approval` D5-13) or with every row on one side
  changing (`vendor-onboarding` D4-19, `sanctions-screening` D4-04) the probability is under
  0.001 and the cell registers [0, 0.1]; with about six (`expense-approval`'s D7 category
  edits and D4-09, where only a receipted case changes) it is about 0.08 per caught ledger and
  the cell registers [0, 0.35]. On the literal stratum the same defect **does** carry the
  signature wherever the base row's threshold value puts every varied case on one side; that
  one-sidedness is the base row's, not the defect's — registered as the stratum's weakness, not
  the profile's strength.
- **S7 — the moved line.** A D1 or D2 instance at an unmasked site carries the signature in
  every caught replicate (rate 1): the changed cases are exactly those between the old line and
  the new one, on one side of the new one — except where a random draw can land exactly on the
  new literal and change there, which sits AT it and breaks the signature **when no other
  literal of the pointer qualifies**: `expense-approval` D2's new literal 56 is the pack's only
  one, so the cell registers an interval from that probability ([0.5, 1]); `vendor-onboarding`
  D2-17's retained guard at 250000 still has every changed case below it, so the signature
  survives an at-row and the cell registers 1; and where every changed case is at the new
  literal (`sanctions-screening` D2, moved to the floor 0) the cell registers 0.

Cells outside these structures are registered from the same reading of the pack's text, each
with its reason in the matrix. `harness/MATRIX-HOLDOUT.json` holds the reviewer's cells, authored
during review from the same rules and kept byte-for-byte.

## 7. Endpoints, validity, controls, enforcement

The 016–018 regime, inherited: an ordered exhaustive decision rule (pipeline-invalid — no cells
read, or any registered cell unobserved, the complete set of its ledgers not present — →
control-gate failure → zero divergence among registered cells, which is `R1 holds` →
otherwise `R1 falsified`). A registered cell that expects no catch (`allowsNoCaught`) holds
only over the complete set of its ledgers with none caught; a missing observation never holds.
Control gates, evaluated first and recorded in the adjudication:
(G1) for every policy, replaying the **unplanted** pack against every ledger mismatches no row —
the ledger is the pack's own word (`replay.py --policy-pack`, the `cells.gate.json` record);
(G2) every defect instance is a valid pack, or is dropped with its note in `INDEX.json`, and the
dropped set is empty for the four policies (a non-empty set is a control failure, not a
finding), every valid instance has a cell against every ledger, and the ledger set is exactly
the registered one (the literal ledger and seeds 101–130 at each n); (G3) the random ledgers
are deterministic in the seed: the scorer rebuilds one per policy under the pinned runtime and
compares bytes. Before any gate is read the scorer holds the records to be **the registered
experiment's**: every retained mutant equal to the planter's document for its site; **every**
ledger — the literal one and every random one at its declared seed — rebuilt byte for byte
under the pinned runtime; every signature record complete — the profile present, its
threshold entries retained whole and exactly the replayed pack's distinct (pointer, literal)
ordered comparisons (none for a pack that draws no line, which the runtime reports by omitting
the member), every replay naming the rows that mismatched, and every entry exactly what the ledger and
those rows imply — for every boundary of the pack and every origin of the ledger, the rows
whose value at the pointer is a decimal of Core §2.2's grammar placed below, at or above the
literal by mathematical value, and among them the rows that mismatched, zero counts included
— so that the pack's boundaries describe the same mismatched rows jointly, not each on its
own; from those entries the bucket sums and the recorded verdict are recomputed and must
agree; a replay whose report carries no profile, a threshold set that is
not the pack's, or an origin set that is not the ledger's, fails the construction, as does one
that does not run to a verdict, reads fewer rows than the ledger holds, or reports a status
that disagrees with its count. Any shortfall in that validity is pipeline-invalid before
anything is aggregated; only the executed controls — G1 as a completed, bound unplanted replay
that mismatched (its count within its rows), G2 as a dropped instance documented with a
validation result and a note, whose registered cells are then recorded as dropped rather than
as missing evidence, G3 — fail as control gates. The scorer
refuses an existing adjudication, refuses an unpinned or mismatching runtime, writes each of
its three files once and never over an existing one, and labels the attempt.

## 8. Analytic limitations

The intervals are per cell over thirty seeded replicates and say nothing across policies; four
policies are a census of a demo, not a sample of anything. The random generator is one
distribution among many a real history could have; a history concentrated near a policy's lines
behaves like the literal stratum and one spread thin like the random one, and real histories
are neither. The defect taxonomy is nine mechanical classes; a defect a person would plant is
not necessarily one of them.

## 9. What this study cannot show

No claim about any model's drafting; no claim that a caught defect would be *understood* as one
by a reader; no claim that the signature's masquerades are the profile's fault rather than the
question's — a moved line and a swapped outcome on one side of it are the same observation, and
the profile reports observations. No claim about real histories. No claim about the runtime's
correctness beyond the pinned binary's behaviour on these inputs. The policies are the demo's,
so nothing here is independent evidence about anything but this mechanism on those four packs.

## 10. Publication commitment

The catch-rate curves, the signature table and the adjudication are published in full whichever
way they land — every diverging cell, every registered non-detection, every masquerade — because
a precise map of what replayed history buys a draft, and of what the profile's threshold report
can and cannot tell, is the study's most useful possible output and the registered input to the
runtime's ADR-0034 and the plan's Phase 5.
