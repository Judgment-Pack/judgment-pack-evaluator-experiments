# Preregistration — Study 021: does replayed history catch a planted defect, and can the profile tell a moved line from the rest?

**Status: DRAFT, not frozen.** Pre-freeze cross-vendor review rounds are recorded in
`PREREG-REVIEW.md`; the freeze is the squash-merge of the pull request that this file will
name, and after it this file is never edited — corrections go to `DEVIATIONS.md`.

**Nothing has run under a freeze.** Everything executed during harness development lands
under `pilots/`, is labeled harness validation, and supports no claim. The registered cells
below were derived from the packs' text and the runtime's documented semantics; the pilots
informed which structures needed naming, and every cell says which structure it names.

Two companion artifacts are registered *with* this document and pinned at the freeze:
`harness/MATRIX.json` (the registered cells and their expectations) and
`harness/MATRIX-HOLDOUT.json` (the reviewer's holdout cells, authored during review and
kept byte-for-byte). Where prose here and those artifacts could diverge, the artifacts govern.

## The freeze and the primary attempt

- **Freeze commit**: the squash-merge commit of the pull request named in `PREREG-REVIEW.md`.
- **Runtime**: the judgment-pack runtime release **v0.21.0**, the first carrying the history
  profile (runtime ADR-0034), pinned by the digest of its published linux/amd64 binary in
  `harness/PINS.json`; the scorer refuses any other binary.
- **Primary attempt root**: `results/primary-attempt-001` — literal, must not exist at the
  freeze; the scorer refuses an existing root, and the first invocation of the governing
  command is the primary attempt, crash and all.
- **Governing invocation** (fully offline; the runtime and CPython 3.12 only):

      for each policy P in fixtures/policies:
        python harness/build_ledgers.py P --n 5 10 20 50 --seeds 30 --out results/primary-attempt-001
        python harness/plant.py P --out results/primary-attempt-001
        python harness/replay.py P --ledgers results/primary-attempt-001/P \
          --defects results/primary-attempt-001/P/defects --out results/primary-attempt-001/P/cells.json
      python harness/score.py --attempt-root results/primary-attempt-001 --include-holdout

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

**R2 (descriptive):** the catch-rate curves — per policy, per defect class, per stratum, per
n — with exact 95% Clopper–Pearson intervals; and the signature table — per policy, class and
stratum, the fraction of caught cells carrying the line-moved signature, with the same
intervals. Published whichever way they land, and read only with the registered structural
account beside them.

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
- **Pins are enforced, not declared**: the scorer compares the runtime's digest before reading
  a cell, and labels an attempt REGISTERED only when the preregistration, matrix and manifest
  digests are all pinned and match; any null makes it a PILOT.
- **Determinism**: every random ledger is drawn by `random.Random("021:<policy>:<n>:<seed>")`;
  two builds of the same attempt root are byte-identical, and the harness tests assert it.

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
  evidence requirement present, absent and unknown; one pointer moved at a time from the base
  row) decided under the pack. One ledger per policy, deterministic. It stands for a history
  whose cases happen to sit where the policy draws its lines — the best case for replay.
- **`random-<n>-<seed>`** — the random stratum: n cases drawn over the pack's own pointer
  domains (an ordered literal's pointer uniformly over [0, 2 × its largest literal] at the
  literal's precision; an enumerated pointer uniformly over the pack's literals plus one value
  outside them, weighted as one more member; applicability pointers always inside the domain the
  pack applies to, since a ledger holds the decisions a pack made; booleans uniformly; every
  evidence requirement present or absent uniformly), decided under the pack; a draw the runtime
  refuses is dropped and redrawn. n ∈ {5, 10, 20, 50}, thirty seeds each. It stands for a
  history that never aimed at the lines.

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

> exactly one pointer carries disagreeing rows at all, and at at least one of that pointer's
> literals every disagreeing row lies strictly on one side of it (below xor above) and none at it.

Read per pointer, not per literal, because a pack may compare one pointer against several
literals (a rule's guard and an exception's mirror) and the profile lists one entry per literal
while the rows that disagree are the same rows. A cell whose pack draws no threshold carries no
signature; a caught cell with mismatched rows and no threshold disagreeing is *caught
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
  (`vendor-onboarding`: `request-info-incomplete` → `request-info`, the fallback) is unobservable
  to a replay of dispositions: a D7 edit that stops it firing changes the trace and not the
  disposition. Registered **undetected** on both strata.
- **S3 — boundary flips and random history.** A D3 flip changes the disposition of a case
  exactly at the literal and of no other. The literal stratum holds that case; a random draw at
  the literal's precision over [0, 2L] hits it with probability 1/(2L+1) per row. Registered
  **detected** on the literal stratum (where not masked by S1) and **undetected** on the random
  stratum at every n (rate in [0, 0.1]).
- **S4 — evidence guards under a required-evidence escalation.** Dropping an `evidence-present`
  condition (D6) from a rule whose requirement the pack marks `required` changes nothing the
  ledger can see: a case with that evidence absent escalates on the requirement before any rule
  fires, and a case with it present fires the rule either way. Registered **undetected** on both
  strata.
- **S5 — one-sided sites.** A defect whose disagreeing cases all lie on one side of the pack's
  sole threshold — because the rule or exception it edits fires only on that side, or because
  the other side is escalated by an exception before the edit can matter — carries the
  line-moved signature whenever it is caught. Registered **signature = 1** for the named D5,
  D6, D7, D8 and D9 instances of `vendor-onboarding` and `expense-approval` whose site is
  one-sided by the pack's text, on both strata; these are the registered masquerades.
- **S6 — two-sided sites.** A defect whose disagreeing cases lie on both sides of a threshold
  (D4 reversing the sole comparison; a D7 edit to an applicability-adjacent member that fires on
  both sides) carries **no** signature on the random stratum (rate in [0, 0.1] at n = 50) and
  **does** on the literal stratum wherever the base row's threshold value puts every varied
  case on one side. The literal stratum's one-sidedness is the base row's, not the defect's —
  registered as the stratum's weakness, not the profile's strength.
- **S7 — the moved line.** A D1 or D2 instance at an unmasked site carries the signature in
  every caught replicate on both strata (rate 1): the disagreeing cases are exactly those
  between the old line and the new one, on one side of the new one.

Cells outside these structures are registered from the same reading of the pack's text, each
with its reason in the matrix. `harness/MATRIX-HOLDOUT.json` holds the reviewer's cells, authored
during review from the same rules and kept byte-for-byte.

## 7. Endpoints, validity, controls, enforcement

The 016–018 regime, inherited: an ordered exhaustive decision rule (pipeline-invalid — no cells
read — → control-gate failure → zero divergence among registered cells, which is `R1 holds` →
otherwise `R1 falsified`). Control gates, evaluated first: (G1) for every policy, replaying the
**unplanted** pack against every ledger mismatches no row — the ledger is the pack's own word;
(G2) every defect instance is a valid pack, or is dropped with its note in `INDEX.json`, and the
dropped set is empty for the four policies (a non-empty set is a control failure, not a
finding); (G3) building the attempt root twice yields byte-identical ledgers. The scorer refuses
an existing attempt root, refuses an unpinned runtime, writes the aggregate files before the
adjudication, and labels the attempt.

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
