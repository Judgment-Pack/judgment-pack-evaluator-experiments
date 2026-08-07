# Preregistration — Study 012: is the blinded author's test surface anchored to the policy's surface form?

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review;
governing thereafter.**

**Nothing has run.** No authoring call has been made for this study, no arm
artifact has been frozen, no batch exists, no completion has been read, no rate
has been computed. Every number below is either a pin copied from Study 011's
committed artifacts, a registered test vector for the interval arithmetic, an
operating characteristic computed from that arithmetic before any data exists,
or a threshold chosen before any data exists. When the batch runs, results go
to `RESULTS.json`, `RATES.md`, `CENSUS.md` and `ANALYSIS.md`; departures from
this file go to `DEVIATIONS.md`. After the freeze this file is never edited.

**The harness does not exist yet, and this file specifies it rather than
describing it.** Study 012 is built by porting Study 011's harness by digest
after this preregistration is reviewed. Every port table below carries
`(port time)` where a digest will go; those cells are filled once, when the
port is taken, and committed before the freeze. A `(port time)` cell surviving
into the frozen file is a defect, and `harness/integrity.py` refuses on it.

**§10 is a register of the parameters this draft does not settle.** Where the
design has a genuinely open choice, this file states a proposal, states the
alternative, and marks it **[D-n]**. Those are the decisions the pre-freeze
review is for. Everything not so marked is registered as written.

Predecessors: [`studies/011-authorship-coverage-rates`](../011-authorship-coverage-rates/)
— its `PREREGISTRATION.md` is the source of every ported gate, every interval,
and the section discipline of this file; its `DIVERSITY.md` is the census whose
reading this study exists to falsify; its `DEVIATIONS.md` is empty and its
`ANALYSIS.md` §"The one invalid run" is the rule §3.3 restates. And
[`studies/010-blinded-oracle`](../010-blinded-oracle/), whose
`PROTOCOL-LOCK.json` is still the ultimate authority for the compiler, the
mirror, the transcript gates and arm A's prompt and family. Tracker:
evaluator-experiments **issue #45**, whose body registers this mandate.

## 1. The question

Study 011 measured that a blinded authoring call reaches all six registered
boundary classes in 49 of 49 valid runs. Its post-hoc census measured *how*,
and the answer was uncomfortable: 410 of 784 records (52.3%) sit on one of the
family's three edges or within 0.01 of one; **three** of the six classes (0, 2
and 5) rest on two distinct probes each, and **four** of six (0, 1, 2 and 3)
contain a probe that appears in every one of the 49 runs; the whole band
[23.75, 39) below the **unstated** 39 edge is empty, while the two thresholds
the policy text names outright are hugged to two or three decimal places from
both sides. The census's own summary was that "boundary placement follows the
numbers the policy names, not an independent search for edges".

That is a reading, not a measurement. This study asks whether the reading is
right:

> Is the blinded author's test surface anchored to the policy's **surface
> form** — its named numeric literals, its wording, its clause order — or to
> the policy's **decision structure**? Hold the decision structure constant,
> perturb the surface, and see whether coverage of the six registered boundary
> classes moves with the surface or stays with the structure.

The reading was published with a prediction attached: renaming the thresholds
should move coverage to the new numbers and change almost nothing else, and
**denaming** them — stating the same rule with the same values but no literal
— should collapse coverage of the classes that have a numeric edge.

**The proposition this study can retract is written once, here, and referred
to by name everywhere else:**

> **R1 — the boundary-hugging in Study 011's corpus is *caused* by the policy
> text naming 40 and 70. State the same rule without the literals and the
> hugging, and the coverage that rests on it, goes away.**

R1 is the causal extension, and it is what arm E can falsify. It is **not**
the census's own committed sentence — "boundary placement follows the numbers
the policy names, not an independent search for edges" — which is a
description of Study 011's own corpus and stays true whatever arm E does. §5.3
(i) and §8 refer to R1 by name; §8's retraction commitment is a commitment
about R1 and about nothing else.

**`CLAIM.md` freezes the prediction with everything else.** The verbatim
published wording of R1, its venue, its URL and its retrieval date are
committed to this study directory as `CLAIM.md` before the freeze, and its
digest is pinned in `harness/PINS.json` beside every other artifact, so the
retraction target cannot drift after the data. A `CLAIM.md` that is missing or
unpinned at the freeze is a defect and `harness/integrity.py` refuses on it.
Registered honestly: the repository's own `DIVERSITY.md` proposes the
follow-up in its "what these bytes cannot answer" section — "a policy arm
whose thresholds are stated obliquely or not at all" — but carries no wording
of R1's directional prediction, which is why the venue record has to be
committed rather than cited.

This study is that prediction run as a falsifier against our own claim. §5
registers the decision rule and the falsification conditions before any call,
and §8 commits to publishing the correction with the same prominence as the
claim if the denamed arm maintains coverage.

What the answer is a property of, stated once so it is not overread: **five
policy texts × one prompt template × one model × one CLI build × one defect
family**, executed on one machine on one day. The perturbations are single
instances — one paraphrase, one permutation, one rename, one denaming — so
nothing here estimates an effect of "paraphrase" or "denaming" in general.
Byte-lineage, not truth, unchanged.

## 2. The five cells

Five arms. **Semantics are constant across all five by construction**, and
§2.4 and §6 C8/C9 register how that is checked in code rather than asserted in
prose. What varies is one artifact per arm: the policy text the prompt inlines.

| arm | perturbation | thresholds | mirror and family |
| --- | --- | --- | --- |
| **A** baseline | none — Study 011's policy text plus the registered conventions delta [D-15] | 40, 70 | the registered mirror at (40, 70); 010's locked family |
| **B** reworded | the five clause bodies paraphrased; every literal and the clause order unchanged | 40, 70 | A's |
| **C** reordered | the five clause bodies byte-identical to A's, presented in a registered permutation | 40, 70 | A's |
| **D** renamed | the threshold literals moved | **45, 72** | the registered mirror at (45, 72); the σ-image of A's family (§2.4) |
| **E** denamed | no numeric content in any clause body; the same values stated only by reference | 40, 70, by reference | A's |

**One mirror module serves all five arms**, parameterized by the arm's
registered `(T_low, T_high)` **[D-14]**; §2.2 and §2.6 register it and C8
clause 6 checks that its verdicts agree with arm A's on every landmark.

### 2.1 Why A is re-run rather than read off Study 011

Study 011's 49 valid runs are **historical reference, not this study's
baseline**. They were produced on 2026-08-07 against a model snapshot whose
drift since is uncontrolled and unmeasurable from here. A contrast between an
arm run today and a batch run months ago confounds the perturbation with
whatever moved in between, and no pin in this repository can rule that out.

So arm A is Study 011's registered call, re-run in the same batch as B–E, and
every registered contrast in §5 is **within this batch**.

**Arm A's prompt is 011's pinned text plus exactly the registered conventions
delta [D-15], and nothing else.** §2.6's conventions paragraph adds one
sentence — the scale sentence — to all five arms alike, so that arm E's
threshold definitions do not smuggle a second intervention into arm E only
(the reasoning is in §2.5 and the choice is registered as **[D-15]**). The
consequence for this section is that arm A's prompt no longer hashes to Study
011's pinned prompt digest
`a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2`. What is
required in code instead, and is a stronger relation than the digest was:

```
arms/A/POLICY.md == 010's locked policy/POLICY.md bytes
                   with CONVENTIONS_DELTA inserted at the registered position
arms/A/PROMPT.txt == HEADER + (arms/A/POLICY.md minus its final LF)
```

where `CONVENTIONS_DELTA` is published verbatim in §2.6 and Appendix A, pinned
by its own sha256 in `harness/PINS.json`, and `HEADER` is derived from 011's
pinned prompt bytes (§2.6). So the byte relation to 011's cell is still
arithmetic on bytes and not an assurance; it is now an *equation with a
published, pinned residue* rather than an equality. 011's prompt digest is
still pinned and still verified — as the source of `HEADER`, which is the 948
bytes of 011's prompt that precede the policy text.

The comparison of arm A against Study 011's published rates is reported in
`ANALYSIS.md` as **drift information, with no verdict attached** (§4.7). It is
not a contrast, it gates nothing, and no registered decision reads it — which
is also why the conventions delta costs this study nothing that gates anything:
the digest pin was load-bearing only for that drift report.

One consequence is registered here rather than discovered later, and it is
registered as *weaker* than an earlier draft claimed. **An arm-A class below
HIGH is at least as likely to be sampling noise at N = 25 as drift**: §5.4
records that at a true per-class p of 0.95 — inside Study 011's own published
interval, whose lower bound is 0.9275 — the probability that arm A reads HIGH
on **all six** classes is only **0.4424**, and on all four narrow numeric
classes only **0.5806**. So a single arm-A class below HIGH is **reported as
an unresolved baseline for that class, not as a drift finding**, every §5
contrast involving that class is INDETERMINATE by §5.2's own rule, and the
drift report of §4.7 stands beside it without a verdict. Only a pattern that
§5.4's operating characteristics make implausible under zero drift — several
classes at once, or a class far below the cut — is reported as drift, and even
then it is reported as a finding about the contemporaneous baseline and not as
a measurement of drift, which this design cannot make.

### 2.2 What is constant across the arms, and where it comes from

Everything except the arm's policy text. The chain of authority runs three
levels deep and is verified in code before any call and before any scoring
(§6 C1):

```
Study 012's harness/PORTS.md
    -> Study 011's harness/PINS.json + harness/PORTS.md   (both pinned here)
        -> Study 010's PROTOCOL-LOCK.json                 (pinned in 011)
```

**Each row answers to the authority named in its own column, and C1 binds it
to that authority and to no other** (§6 C1 states the three tiers as a table,
because the file's *port kind* and its *authority* are different facts and an
earlier draft conflated them).

| ported byte-identically from Study 011 | 011 sha256 | authority |
| --- | --- | --- |
| `arms/A/FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | 010's lock, through 011's `PORTS.md` |
| `transcription/PROBE-PROMPT.txt` | `128aaa9a67b601c66b11d8d233a336cca1e064401bb24994929b9965f77f45e7` | **011's `PINS.json`** — 011 introduced this file and it appears in no `lockedInputs` of 010 |

`arms/A/POLICY.md` is **not** a byte-identical port: it is 010's locked
`policy/POLICY.md`
(`e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f`) plus the
registered `CONVENTIONS_DELTA` of §2.1 and §2.6, and it appears in the
enumerated-change table below with 010's lock as its source-side authority.
`arms/A/PROMPT.txt` is likewise derived rather than copied: `HEADER` is taken
from 011's pinned prompt bytes
(`a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2`, itself
010-locked as `transcription/PROMPT.txt`) and the prompt equation of §2.6
rebuilds it. Both digests remain pinned and verified in the roles just named.

| ported with enumerated changes | source sha256 | source authority | destination sha256 | registered scope of the change |
| --- | --- | --- | --- | --- |
| `harness/policy_mirror.py` | `276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba` | 010's lock | (port time) | **[D-14]** the two threshold comparisons read `T_low` and `T_high` from the arm's `ARM.json` instead of the literals 40 and 70; the module is otherwise line-for-line 010's, and the diff is published in `harness/PORTS.md`. **One module serves all five arms** — see below |
| `arms/A/POLICY.md` | `e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f` | 010's lock, through 011's `PORTS.md` | (port time) | `CONVENTIONS_DELTA` inserted at the registered position (§2.1, §2.6, Appendix A), and nothing else. The delta is published verbatim and pinned by its own sha256 |
| `harness/records_compile.py` | `6de92175b3f93d563b7e79c60a2e3fd641d96f40cc594fb8c3753c3655c90a1c` | **011's own bytes** (011 adapted it from 010's `e58edce3…`) | (port time) | none — byte-identical if the port takes it unchanged; the output-root parameter 011 added already suffices |
| `harness/transcript_check.py` | `0c9d7c798fc8738acb05dada3230251c9fba6109e15ed5b6b5ee8a4b2e708218` | **011's own bytes** (011 adapted it from 010's `42d977c4…`) | (port time) | the registered-prompt-terminal gate takes **the arm's** prompt bytes instead of one fixed prompt; no other check logic changes |
| `transcription/authoring_call.sh` | `6e1239f3ea425669e88878dc2b4d3f6eb41ff9ffe859c76479c9bb8dea41a90e` | **011's own bytes** (011 adapted it from 010's `3b8909aa…`) | (port time) | §2.7 |
| `harness/integrity.py` | (port time) | 011's commit only | (port time) | the three-level chain above; the per-arm artifact checks of §6 C8 and C9 |
| `harness/batch.py` | (port time) | 011's commit only | (port time) | §2.8's per-arm round-robin schedule; per-arm slot roots; the arm stamp in `CALL.json` |
| `harness/score_rates.py` | (port time) | 011's commit only | (port time) | per-arm scoring against that arm's mirror and family; the §5 level and contrast verdicts; the §4.5 census; the old-edge cross-scoring of §4.6 |
| `harness/census.py` (from 011's `analysis/diversity.py`) | (port time) | 011's commit only | (port time) | promoted from a post-hoc script to a registered secondary: parameterized by the arm's edge set and family, distances bucketed as §4.5 registers, no clock and no randomness (unchanged) |

**One mirror module, five arms, parameterized by a registered artifact
[D-14].** Study 010's locked `policy_mirror.py` encodes 40 and 70 as literals
and therefore cannot serve arm D, whose thresholds are 45 and 72. The
registered resolution is that the ported module takes `(T_low, T_high)` from
the arm's own `ARM.json` — a file already registered per arm and pinned by
sha256 before any call (§2.6, §2.10) — so that **exactly one mirror artifact
exists, at one destination digest, and each arm's behaviour is keyed to a
registered artifact rather than to unpinned code**. The parameterization is
the *only* change: `harness/PORTS.md` publishes the diff, and C8 clause 6 runs
the landmark-grid equality against that module at its registered destination
digest, instantiated at each arm's registered pair. The alternative — a fifth
per-arm file `arms/<X>/MIRROR.py`, five artifacts to pin and five diffs to
review — is recorded in §10 under **[D-14]**.

Study 011's own harness files (`batch.py`, `score_rates.py`, `integrity.py`,
`analysis/diversity.py`) are **not pinned by any lock in Study 011** — that
study's §7 says so plainly, and pinned only its six 010-derived ports. So the
source column for those four rows can be bound to nothing older than the
commit the port was taken at, and their authority column says so. What that costs and what covers it is stated in
§6 C1 and §7 rather than glossed: the recorded commit, cross-vendor review of
the diff, and C3's two replication controls, which run the ported counting and
the ported census over retained bytes whose answers are already published.

The model, the CLI, and the binary are pinned to Study 011's values:

```
model            gpt-5.6-sol
CLI              codex-cli 0.145.0
binary sha256    a2a05dafaa1acb002a45eaec0a462de5b13694fcfcd7bc43305f14781ce7be14
```

The wrapper refuses to run a slot unless the resolved codex binary hashes to
exactly that digest **and** reports exactly that version string, both checked
before the call is made. If the local binary has drifted by the time the batch
runs, the study **does not run with a substitute**: the drift is recorded in
`DEVIATIONS.md` and the study is either re-registered against the new pin or
abandoned. A contrast measured across two binaries is not a contrast.

Sampling parameters are not pinned beyond the CLI defaults under
`--ignore-user-config`: this CLI exposes no temperature or seed control at
`codex exec`. Recorded, not controlled, exactly as in 011.

### 2.3 The six boundary classes, keyed semantically

The classes are **not** six numbers. They are six semantic keys, instantiated
per arm from that arm's two thresholds — `T_low` (the personal-data threshold)
and `T_high` (the review threshold). All five edge values derive from the pair,
so an arm's whole family is determined by it:

| i | semantic key | predicate at (`T_low`, `T_high`) | A, B, C, E (40, 70) | D (45, 72) |
| --- | --- | --- | --- | --- |
| 0 | the review threshold, exactly | ¬S ∧ ¬E ∧ risk = `T_high` | = 70 | = 72 |
| 1 | one-wide band above the review threshold | ¬S ∧ ¬E ∧ `T_high` ≤ risk < `T_high`+1 | [70, 71) | [72, 73) |
| 2 | one-wide band above the personal-data threshold | ¬S ∧ ¬E ∧ P ∧ `T_low` ≤ risk < `T_low`+1 | [40, 41) | [45, 46) |
| 3 | the interior review band | ¬S ∧ ¬E ∧ `T_low` ≤ risk < `T_high` | [40, 70) | [45, 72) |
| 4 | embargo membership: registered in SY | ¬S ∧ country = SY | — | — |
| 5 | one-wide band below the personal-data threshold, **whose lower edge the policy text never states** | ¬S ∧ ¬E ∧ P ∧ `T_low`−1 ≤ risk < `T_low` | [39, 40) | [44, 45) |

(S = sanctions hit, E = embargoed registration, P = handles personal data.)

At (40, 70) this schema reproduces Study 010's locked `FAMILY.json` exactly,
and C9 requires arm A's family to equal that file byte for byte. Class 4 has no
numeric content in any arm and is the study's internal control: it is predicted
unaffected everywhere (§5.3). Class 3 is a wide band that a diffuse author
covers by accident — **30 wide in arms A, B, C and E, and 27 wide in arm D**,
because D's shift is deliberately unequal (§2.4) — and it is likewise predicted
unaffected everywhere and is
**not** part of the collapse prediction — registered here so it cannot be
recruited as supporting evidence afterwards **[D-11]**. The narrow numeric
classes, which are what the prediction is about, are **0, 1, 2 and 5**.

Three properties of the classes carry over from 011 unchanged: they are **not
disjoint** (0 nests in 1, 2 nests in 3, 5 is adjacent to 3), coverage is
non-emptiness per predicate rather than a partition, and the six intervals are
marginal rather than a simultaneous region.

### 2.4 Arm D's threshold substitution, and how "semantics constant" is checked

Arm D moves `T_low` 40 → 45 and `T_high` 70 → 72, and everything keyed to them
moves with them: the policy text's two literals, the mirror's two comparisons,
and the five family edges of §2.3. The moves are deliberately **unequal** (+5
and +2) so that no single affine shift explains the arm, and deliberately still
ordered `T_low` < `T_low`+1 < `T_high` so the six classes stay disjointness-
compatible and non-empty.

**The pair (45, 72) is an authored choice with two named costs, registered as
[D-18] rather than presented as forced.** (i) *Salience.* 40 and 70 are
decade-round; 45 is a multiple of five and 72 is round in no ordinary sense.
If an author's placement is drawn to round values rather than to the literal
the text states, arm D's classes 0 and 1 lose coverage for a reason that is
**not** the rename — which is why §5.3 (ii) now registers a third outcome for
arm D rather than only the two an earlier draft carried. (ii) *Band width.*
The unequal shift changes class 3's width from 30 to **27**, so arm D's class
3 is 10% narrower than every other arm's and the phrase "a 30-wide band" is
false of it. Every occurrence of that phrase in this file is now qualified
with the arm it describes. The salience-matched alternative (50, 80) —
decade-round on both sides, class 3 width 30 exactly as in arms A, B, C and E
— is registered in §10 under **[D-18]**, together with the cost it carries and
that (45, 72) does not: 40 → 50 and 70 → 80 **is** a single additive shift of
+10, which is the confound (45, 72) was chosen to exclude. The two candidates
trade one confound against the other and the review picks which one this study
would rather not be able to rule out.

"Semantics constant" cannot mean "the same verdict for the same score" in arm
D — the thresholds moved, so it means **the same verdict at the corresponding
landmark**. That correspondence is registered as a landmark grid and checked in
code (§6 C8):

```
landmarks(T_low, T_high) = [ 0,
                             T_low  - 1,     T_low  - 0.01,  T_low,
                             T_low  + 0.01,  T_low  + 1 - 0.01,  T_low  + 1,
                             T_high - 0.01,  T_high,         T_high + 0.01,
                             T_high + 1 - 0.01,  T_high + 1,
                             100 ]
grid(arm)  = {false,true} x {KP, IR, SY, CA, DE} x {false,true} x landmarks(arm)
```

**Thirteen landmarks, 260 cells per arm** (2 × 5 × 2 × 13). The four landmarks
at `T_low + 1` and `T_high + 1`, on both sides, are there because those are the
**exclusive upper bounds of classes 2 and 1** (§2.3) and an earlier
nine-landmark grid probed neither: a family that encoded class 2 as
`[45, 47)` or class 1 as `[72, 74)` would have passed the class-membership half
of the check unchanged, while the grid was advertised as the check that carries
the whole claim about arm D. It now probes every edge the six predicates name.

The registered requirement: **the verdict vector of every arm's mirror over its
own grid, in the registered cell order, is elementwise equal to arm A's**, and
the class-membership vector of every arm's family over its own grid is
elementwise equal to arm A's. The mirror is the single registered module of
§2.2 at its registered destination digest, instantiated at that arm's
registered `(T_low, T_high)` from its pinned `ARM.json`; nothing unpinned
computes a landmark. For B, C and E this is implied by their sharing arm A's
threshold pair and family bytes, and is checked anyway. For D it is the whole
content of the claim that D is a rename and not a different policy.

What this check does **not** cover, stated here because it is the study's
largest unmechanised risk: it relates each arm's *mirror* to A's, and says
nothing about whether each arm's *prose* says what its mirror computes. That
relation is bounded from three sides and closed by none: §6 C8's literal census
bounds it syntactically, **§6 C10's clean-room second mirrors bound it by
independent re-derivation from each arm's own bytes**, and cross-vendor
pre-freeze review of the five texts is the rest. §7 lists it under "recorded,
not checked" and §9 lists it as a bound.

### 2.5 Arm E's denaming, and what it cannot be

Arm E states the same policy, with the same two threshold values, using no
numeric literal in any clause body. It is worth being exact about what that can
and cannot mean, because the naive reading makes the arm invalid.

**E is not "the policy with the numbers removed."** A policy that does not
determine 40 and 70 is a *different policy*, its mirror is not A's, and the
contrast would confound denaming with a semantics change — the one thing every
other part of this design spends its effort preventing. E therefore states the
values **indirectly and exactly**: the clause bodies name a *review threshold*
and a *personal-data threshold*, and the conventions paragraph defines each as
a fraction of the scale, in words. The values are recoverable by arithmetic,
the mirror is the same registered module at the same pair (40, 70), and the six
classes are A's.

**The intervention is one difference, and keeping it one difference required a
change to the other four arms [D-15].** The scale sentence — "The office's risk
scale runs from zero to one hundred." — is *new semantic information*: neither
011's prompt header nor 010's conventions paragraph bounds `riskScore`
anywhere, and 011's corpus contains scores authored with no stated scale at all
(12, 12.5, 23.75 among them). Telling an author the scale is 0–100 can move
record placement on its own, and no mirror can catch it, because the mirror
encodes no domain. Putting that sentence in arm E alone would have made arm E
two interventions and its falsifier correspondingly weaker. So **the scale
sentence goes in all five arms' conventions paragraphs** as the registered
`CONVENTIONS_DELTA` of §2.1 and §2.6, and what remains unique to arm E is
exactly the threshold-definition sentence. The alternative — E-only, accepting
the confound and saying so in §5.3 (i), §8 and §9 — is registered in §10 under
**[D-15]**, as is the sixth-arm option that would control it directly.

So the intervention E actually applies is: **the model must derive the
thresholds rather than copy them.** The prediction is that indirection alone
costs the boundary-hugging behaviour the census found. If it does not, R1 is
wrong.

**Two residuals are registered rather than argued away.**

*First,* E's threshold values appear nowhere as digits, but "seven tenths" and
"one hundred" are numbers spelled as words: E denames the *threshold literals*,
it does not remove numeric information. A reader who expected "no numbers at
all" is owed that sentence, and §9 repeats it.

*Second, and stated because an earlier draft got it wrong:* arm E's
`POLICY.md` **is not digit-free**, and no honest version of it can be. Three
digit-runs survive in the frozen bytes, in text that is byte-identical across
all five arms and is therefore not a difference between them:

| digit-run | where | why it is there |
| --- | --- | --- |
| `010` | the preamble's "Synthetic policy for Study 010" | inherited from 010, held byte-identical across all five arms (§2.6) |
| `4` | P5's body, "unless P4 applies" | a structural cross-reference to a clause label, present identically in A, B, C, D and E |
| `3166`, `1`, `2` | the conventions paragraph's `ISO 3166-1 alpha-2` | inherited from 010, held byte-identical across all five arms |

plus the clause labels `P1`–`P5` themselves. Registered mechanically (§6 C8),
and true of the frozen artifact:

> **The only digit-runs anywhere in arm E's `POLICY.md` are the clause labels
> `P1`–`P5`, in-body clause-label references of the form `P<n>`, the token
> `ISO 3166-1 alpha-2`, and the preamble's study reference; and no digit-run
> in the file equals `40` or `70`.** The clause-body census of §2.6 and C8
> runs over each body with clause-label tokens `P1`–`P5` masked out, so
> "arm E's clause bodies carry no numeric content" is checked as the statement
> it is meant to be rather than refuted by a cross-reference.

**The preamble's `010` is a recall channel, and it is registered as one.**
"Study 010" is a name-keyed pointer to a public repository whose policy text
states 40 and 70. Arm E is therefore *denamed but not de-referenced*: it
retains one textual hook by which a contaminated snapshot could recall the
literals it was denied. §5.3 (i) registers this as a third reading of an
E-maintains-coverage outcome, with the discriminator named. **[D-16]** records
the alternative — replacing the study reference with a digit-free, name-free
equivalent in all five arms — and what it would cost.

**[D-3]** The exact reference wording of arm E is the single most consequential
authored artifact in this study. Appendix A carries the draft; the pre-freeze
review fixes it, and it is frozen with this file. Three authored difficulties
that were **not** the intervention have already been removed from that draft
under D-3, because each one alone could have manufactured the predicted
collapse: a pronoun whose nearest antecedent gave a coherent wrong derivation
(two fifths of the review threshold is 28); the name "clearance threshold" for
`T_low`, which §2.3 calls the *personal-data threshold* and which arm A's own
P5 makes a clearance boundary for the *other* threshold; and two different
denominators ("seven tenths", "two fifths"), which made one derivation strictly
harder than the other for no design reason. The frozen wording uses one
denominator, no pronoun, and §2.3's own key. §4.5's **X6** registers the
plausible-misderivation census that diagnoses a comprehension failure instead
of assuming it away.

### 2.6 The arm artifacts, and the structure a policy text must have

Each arm is a directory `arms/<A|B|C|D|E>/` holding exactly four registered
files, each pinned by sha256 in `harness/PINS.json` **before any call**:

| file | what it is |
| --- | --- |
| `POLICY.md` | the arm's policy text — the intervention |
| `PROMPT.txt` | the shared prompt header with this arm's policy inlined |
| `FAMILY.json` | §2.3's schema at this arm's (`T_low`, `T_high`) |
| `ARM.json` | the arm id, its (`T_low`, `T_high`), and its declared perturbation kind. **The (`T_low`, `T_high`) pair here is what parameterizes the single registered mirror module** (§2.2 [D-14]), so this file is load-bearing for every label in its arm and is pinned like every other |

| arm | `POLICY.md` sha256 | `PROMPT.txt` sha256 | `FAMILY.json` sha256 | `ARM.json` sha256 |
| --- | --- | --- | --- | --- |
| A | (port time) | (port time) | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | (port time) |
| B | (port time) | (port time) | (port time — equals A's) | (port time) |
| C | (port time) | (port time) | (port time — equals A's) | (port time) |
| D | (port time) | (port time) | (port time) | (port time) |
| E | (port time) | (port time) | (port time — equals A's) | (port time) |

Arm A's `POLICY.md` and `PROMPT.txt` are `(port time)` rather than filled from
011's lock because of the registered `CONVENTIONS_DELTA` (§2.1, [D-15]); what
is filled now, and checked, is the pair of authorities they are derived from —
010's locked `policy/POLICY.md` at
`e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f` and 011's
pinned prompt at
`a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2`. If the
review chooses D-15's alternative (E-only scale sentence), arm A's two cells
become those two digests outright and the derivation collapses to equality.

**The policy document's structure is registered**, because the mechanical
checks of §6 C8 parse it:

1. a **preamble** — the title line and the introductory paragraph;
2. five **clause bullets**, each beginning `- **P<n>.** `, whose text after the
   label is that clause's **body**;
3. a **conventions paragraph** — the trailing prose about decimal strings,
   country codes and exhaustiveness.

**The clause-body digit-run census, defined once.** A *digit-run* is a maximal
run of digit characters. The census of a clause body is the multiset of
digit-runs in that body **with clause-label tokens `P1`–`P5` masked out
first** — those are structural cross-references (A's own P5 body says "unless
P4 applies"), they are present identically in every arm, and counting them
would make every arm's census carry a `4` that says nothing about the
intervention. Registered as the definition every clause below and C8 clause 5
use.

Registered per arm, and checked:

- the **preamble is byte-identical in all five arms**. It is inherited from
  Study 010 and its references to packs and to Study 010 are historical;
  keeping it fixed is what confines each arm's variation to the intervention.
  What that costs arm E is registered in §2.5 and §5.3 (i) and its alternative
  is **[D-16]**;
- the **conventions paragraph is byte-identical in A, B, C and D**, and equals
  010's conventions paragraph plus the registered `CONVENTIONS_DELTA`
  **[D-15]**, which is exactly one sentence and is published verbatim in
  Appendix A and pinned by its own sha256:

  ```
  The office's risk scale runs from zero to one hundred.
  ```

  arm E's conventions paragraph is that same text with the registered
  threshold-definition sentence appended, and nothing else;
- **A**: the five bodies are 010's, byte-identical, in order P1…P5;
- **B**: the five bodies are paraphrases; the ordered sequence of clause labels
  is P1…P5; the digit-run census of the bodies equals A's, which is
  `{40, 40, 70, 70, 70, 70}`;
- **C**: the five bodies are **byte-identical to A's**; the presentation order
  is the registered permutation; each label travels with its own body;
- **D**: the five bodies are A's with the two threshold literals substituted;
  the digit-run census is A's under σ, which is `{45, 45, 72, 72, 72, 72}`;
- **E**: the five bodies' digit-run census is **empty**; P1's and P2's bodies
  are byte-identical to A's (they carry no numeric content), and P3, P4 and P5
  are the registered reference wordings.

**Arm B carries a clause-level invariant the digit census cannot express.**
The literal multiset is preserved by any paraphrase that keeps the numbers;
what 011's census identifies as the single most anchoring-relevant feature of
the text is the **boundary-inclusivity phrasing** — A's P4 reads "40 or above
but below 70", B's reads "from 40 up to but not including 70" — and those are
exactly the cues the on-edge records at 40 and 70 answer. If B collapsed and
that phrasing were unconstrained, "the paraphrase weakened the inclusivity cue"
would explain it at least as well as "the author anchors to the prompt's
shape", and §5.3 (iii)'s registered dependency would take arm E's result down
with it. So, registered and checked in C8:

> **In every arm at (40, 70), each numeric bound is stated with an explicit
> inclusivity word immediately adjacent to its literal, and the adjacency
> pattern of arm B's bodies matches arm A's clause for clause** — same clause,
> same literal, same side, an inclusivity word on the same side of the literal.

The clause-by-clause A ↔ B substitution table is published under **[D-4]** in
Appendix A so the pre-freeze review adjudicates each substitution rather than
reading five paragraphs as a whole.

**Arm C's permutation is registered as (P2, P1, P4, P5, P3) [D-5].** The
constraint it satisfies is stated generally rather than as one special case,
and it is checked in code:

1. it is a **derangement** — no clause keeps its position: P1 1→2, P2 2→1,
   P3 3→5, P4 4→3, P5 5→4;
2. **every explicit clause-label reference resolves backward** — P5's body says
   "unless P4 applies", and P4 is at position 3 with P5 at position 4;
3. **every three-part "absent a sanctions hit or an embargoed registration"
   precondition resolves backward** — P3, P4 and P5 all open with it, and both
   P1 (which establishes sanctions hits) and P2 (which establishes embargoed
   registrations) occupy positions 1 and 2.

**(P2, P1, P4, P5, P3) is the unique permutation of the five clauses
satisfying 1–3**, verified by exhaustive enumeration of all 120 permutations
and asserted by a harness test. The permutation an earlier draft registered,
(P2, P4, P1, P5, P3), fails clause 3: P4 at position 2 opens with "absent a
sanctions hit or an embargoed registration" while P1 does not appear until
position 3.

**One residual forward reference remains, and no derangement can remove it.**
P2's own body opens with the two-part "Absent a sanctions hit", and under
(P2, P1, P4, P5, P3) it sits at position 1 with P1 at position 2. Requiring
*that* reference to resolve backward as well would force P1 to position 1 and
P2 to position 2, which is not a derangement — the constraint set is provably
unsatisfiable, by the same enumeration. So arm C perturbs order and leaves
exactly one two-part precondition unresolved at first reading, and §5.3 (iii)
reads a C-collapse against that fact rather than against a stronger claim. The
alternative — (P1, P2, P4, P5, P3), which resolves *every* reference backward
and is the maximum-movement permutation that does, at the cost of leaving two
clauses in place instead of deranging all five — is registered under **[D-5]**.
Nothing else about the permutation is claimed; one permutation is one
permutation.

**The prompt relation is registered and checked**, not described:

```
HEADER          = (011's pinned PROMPT.txt bytes) with 010's locked policy bytes
                  (minus their final LF) removed from the end   -> 948 bytes
arms/X/PROMPT.txt == HEADER + (arms/X/POLICY.md bytes with the final LF removed)
```

`HEADER` is **derived** rather than authored, from two digests that are both
pinned and both verified: 011's prompt at `a68dad10…` (2706 bytes) and 010's
policy at `e46f8c48…` (1759 bytes, 1758 without the final LF), which gives
2706 − 1758 = **948** header bytes. Every arm's prompt — arm A's included —
must satisfy the equation above with no trailing newline. So "only the policy
differs" is arithmetic on bytes and not an assurance, and arm A's relation to
011's cell is the composition of that equation with the registered
`CONVENTIONS_DELTA` (§2.1).

### 2.7 The wrapper is an adaptation of an adaptation

`transcription/authoring_call.sh` is Study 011's wrapper, whose whole isolation
invocation is unchanged: fresh `HOME` and `CODEX_HOME`, `env -i` with `PATH`
and `TMPDIR` constructed rather than inherited, exclusive leak-token-free
scratch outside every git worktree, `--ignore-user-config`, explicit model,
binary digest and CLI version checked **before** the call, byte-exact prompt,
stdin closed, credential copied and deleted on the seal path and on `EXIT`,
`INT`, `TERM` and `HUP`, recursive pre-call inventory of the isolated home,
new-session identification by set difference, registry and golden digests
stamped per run. The permitted differences are exactly these, and
`harness/PORTS.md` carries the diff:

1. it takes the **arm id** and the **arm's prompt path** as arguments, and
   writes into `arms/<ARM>/authoring/run-NNN/`;
2. it stamps `arm` and `armPromptSha256` into `CALL.json`, so a slot names the
   arm it was made under and the exact prompt bytes it was made with. §3.3's
   `arm-mismatch` is then a per-slot check rather than a claim about the
   driver's bookkeeping;
3. it names its scratch, isolated home and per-run binary directory `s012-…`.

It **does not** retry, judge a completion, compile records, or decide
admissibility. Because it is adapted, the pre-freeze review reviews it as its
own artifact, exactly as 011's review did.

### 2.8 Sample size, the round-robin schedule, and the shortfall rule

**N = 25 slots per arm [D-1]**, 125 authoring slots in total, fixed before the
batch and executed **sequentially, never in parallel**. §5.4 is the power
reasoning; the short version is that N = 25 is the smallest round number at
which the registered HIGH cut is reachable with slack (a perfect arm's exact
lower bound is 0.8628, and an arm may miss twice and still read HIGH) and at
which a genuine collapse to ≤ 0.05 is called LOW about 87% of the time.

**The five arms are interleaved round-robin, not run in blocks [D-7].** The
batch is 25 **rounds**; each round runs one slot of each arm. Blocked
execution would confound the arm with the two-hour drift across the batch —
the same reason §2.1 refuses Study 011 as a baseline, applied within the day.
Within round *j* the arm order is the cyclic shift of (A, B, C, D, E) by
(*j*−1) mod 5, so over 25 rounds **each arm occupies each within-round position
exactly five times**. That balance is why N is a multiple of 5, and if the
review moves N it should keep it one.

All 125 slots are begun and completed within **one UTC calendar day**;
spilling past midnight is a `DEVIATIONS.md` entry, not a stopping rule.

**Denominators.** Let N = 25 be the slots executed per arm, `I_X` the
pipeline-invalid runs in arm X, and `V_X = N − I_X` its valid runs. Every rate
in §4 is computed over that arm's own `V_X`. The §5 cuts are stated on **exact
interval bounds**, not on observed coverage, precisely so that an arm with a
smaller `V_X` faces a boundary that already carries its smaller sample — Study
011 §5's lesson, reused. **[D-13]** The arms are not truncated to a common
denominator; each `V_X` is published beside its rates, and if two arms' valid
counts differ by more than 2 the contrasts carry a stated caution.

**Shortfall rule.** If the batch cannot complete all 25 rounds, the driver
writes `SHORTFALL.json` naming the reason, the last completed round *R*, and
**the UTC wall-clock time of the last completed slot**, all **before anything
is scored**, and the headline reports "R of 25 rounds completed". Because the
schedule is round-robin, a shortfall at round *R* leaves every arm with *R* or
*R*−1 slots, which is the reason the schedule is round-robin and not blocked: a
batch that dies half way still has five comparable arms rather than two
complete ones and three empty. `batch.py shortfall` refuses when the slots
present are not fewer than the registered plan, and the scorer requires the
declaration's round count to match the slots actually present. The wall-clock
member does not make a stop involuntary — §7 still lists that as unproven — but
it timestamps the stop against the append-only ledger, so a declaration and the
slots it was made over can be read in order.

**The shortfall floor, registered.** The §5.1 HIGH cut is *unreachable* at
small denominators: a perfect arm's exact lower bound is **0.6915 at V = 10**
and **0.7151 at V = 11**, so no arm with fewer than **eleven valid runs** can
read HIGH under the `L ≥ 0.70` cut, every contrast involving it is
INDETERMINATE by construction, and the study produces no verdict at all.
Registered consequences, in advance:

- since a shortfall at round *R* leaves every arm with *R* or *R*−1 slots and
  `V_X ≤` that, **a shortfall at *R* < 11 rounds leaves the level rule unable
  to return HIGH for any arm**. The batch is published as slots and rates —
  every integer, every interval, the whole census — with **every verdict
  recorded as `UNRESOLVED-BY-DESIGN`**, and **no contrast is reported**;
- more generally, and checked per arm rather than per batch: any arm whose
  `V_X` < 11 is recorded `UNRESOLVED-BY-DESIGN` on all six classes and enters
  no contrast, whatever *R* was, because pipeline-invalid runs reduce `V_X`
  below the slot count;
- the scorer computes this itself and writes it, so "the rule could not have
  fired" is a published fact rather than a reader's inference from a table of
  INDETERMINATEs.

**Resume after a crash.** `batch.py run --start-round K` continues at round K
and runs the remaining `25 − K + 1` rounds. The ledger `BATCH.json` holds one
append-only record per slot; a resumed invocation merges into it and refuses to
overlap a slot the ledger already records. No slot is ever re-run.

**Prohibited, without exception:** computing any rate or verdict before the
batch is sealed; adding rounds after any rate has been computed; running a
second batch and pooling it with this one; recomputing a published rate or
verdict on a different population; **and dropping, adding or re-authoring an
arm after any call has been made.** An arm is a registered artifact; a sixth
arm, or a different arm E, is a separate study with its own registration.
Mechanically, as in 011: the driver cannot compute coverage; the scorer refuses
unless the batch is terminal; the driver refuses to create any slot in any arm
once `RESULTS.json` exists; no invocation can plan a round past 25; and the
registered scoring command takes the batch root and an optional
record-emission directory and refuses every other argument.

### 2.9 What each slot retains

Study 011's retention set, unchanged, plus the arm stamp: `CALL.json` (argv,
cwd, isolated home and `CODEX_HOME`, environment names **and values**, model,
CLI identity and binary digest, integer exit status, new-session count, slot
index, round index, **arm id**, **arm prompt digest**, UTC start/end, the
recursive pre-call inventory of the isolated home, whether the credential was
copied and removed, and the digests of the registry (`pinsSha256`) and the
golden capture (`goldenSha256`)), `stdout.raw`, `stderr.raw`, `session.jsonl`,
`context.json`, `completion.txt` (written **only** when the process exited 0),
and `REFUSAL.json` when the wrapper's exit status was not 0. Nothing in that
set is a judgment.

All 125 slots are committed, invalid ones included (§8) — roughly 90 KB per
slot, about 11 MB in total.

### 2.10 The batch registry

`harness/PINS.json` is the run-time registry: the codex binary digest, CLI
version and model; the digests of every arm's `POLICY.md`, `PROMPT.txt`,
`FAMILY.json` and `ARM.json`; **the digest of the single registered mirror
module `harness/policy_mirror.py`** (§2.2 [D-14]), which is the arbiter of
every arm's labels and is pinned here as well as in `harness/PORTS.md`; **the
digest of `CONVENTIONS_DELTA`** (§2.1, §2.6 [D-15]); **the digest of
`CLAIM.md`** (§1); the probe prompt; N and the round-robin schedule; the
interpreter; the recorded operator assent for §6 C7; the recaptured golden
context's digest (`null` until §3.2's capture is registered); this
preregistration's digest at the freeze (`null` until then); **the five arm
`POLICY.md` digests recorded by the final round of `PREREG-REVIEW.md`** (§8,
finding of the round-1 review — the binding that makes "the texts that were
reviewed are the texts that ran" a checked relation); and a pointer to
`harness/PORTS.md`.

The committed `harness/PINS.json` is the registry of record and that is
enforced per run and per population, exactly as in 011: the wrapper records the
digest of the registry it ran under, the scorer computes the committed file's
digest itself, and any slot whose stamp differs is `registry-mismatch`. The
**scorer takes no registry argument at all** and derives every path from the
harness's own location, because a supplied registry identical to the committed
one except for the arm digests or for N would otherwise redefine what was
measured while every per-slot stamp still matched.

`PINS.json` is **not edited between the batch and the scoring**. The freeze
digest is filled at the freeze, the golden digest before round 1, and after
that the file stands.

## 3. Admission per run

Every gate is Study 011's, ported, with exactly one addition: the
registered-prompt-terminal gate is checked against **the arm's** prompt bytes.

### 3.1 The ported gates

A run is **admissible** iff all hold:

1. **Transcript whitelist.** Every `response_item` payload is either a
   `message` with role user, developer, or assistant carrying only
   role-appropriate content items, or an **inert `reasoning` item**. Any other
   payload type — every call form, call output, tool role, attachment, or
   unknown type — refuses. Transcript lines are parsed with duplicate-key
   rejection.
2. **Registered arm prompt terminal.** Exactly one user message equals the
   bytes of **this slot's arm's** `PROMPT.txt`, and no user or developer
   message follows it. A slot whose transcript carries another arm's prompt is
   refused here and scored `arm-mismatch` (§3.3).
3. **Golden context.** The pre-prompt context reproduces
   `transcription/GOLDEN-CONTEXT.json` exactly — count, roles, order, and
   normalized digests and lengths of every message before the prompt. The
   normalization is the ported one. This is an allowlist, and any change
   refuses.
4. **Leak denylist**, as ported, over pre-prompt messages and the call working
   directory.
5. **Model and cwd binding.** Every `turn_context` that names a model or a
   working directory names `gpt-5.6-sol` and this call's own directory.
6. **Exit 0**, recorded as an integer, and exactly one new session file in the
   isolated home.
7. **Completion binding.** At least one assistant message follows the prompt,
   and `completion.txt`'s bytes equal the last one's concatenated
   `output_text`.
8. **Binary pin.** The recorded binary digest and CLI version equal §2.2's
   pins.
9. **Arm binding.** `CALL.json`'s `arm` names the arm whose slot tree the run
   sits in, and its `armPromptSha256` equals that arm's registered prompt
   digest.

**Compiler regeneration.** The ported `records_compile.py` turns
`completion.txt` into that run's `records/` and `RECORDS.md` with no operator
judgment: largest-span JSON array extraction with a strict duplicate-key-
rejecting decoder, then per-element admission in the registered order `schema`,
`decimal-form`, `country-form`, `id-form`, `outcome-value`, `timestamp-form`,
`duplicate-id`, first failing check naming the drop code, no repair of any
kind. `verify` regenerates from the retained bytes and requires byte equality,
the exact file-name set, and regular files only. **The compiler is
arm-independent** — it validates record *shape*, never policy semantics — and
the port is required to leave it so.

### 3.2 The golden recapture: once, for all five arms [D-8]

**One recapture serves the whole batch, and the reason is registered rather
than assumed.** The pre-prompt context *precedes* the prompt and does not
depend on it — that is the property that made Study 011's probe-prompt capture
legitimate in the first place, and it does not become five properties because
there are five prompts. The capture is taken with the ported probe prompt,
whose bytes are `Reply with exactly one word: ready`, which is arm-independent
by construction.

The procedure is 011's, unchanged:

1. `batch.py capture --scratch-parent DIR` makes **two** probe calls into
   `controls/recapture/attempt-1/` and derives the capture only if their
   normalized context lists are identical. One capture cannot show that a
   context reproduces. The derivation refuses fewer than two agreeing slots
   however it is invoked, and refuses when two capture slots share any raw
   evidence that identifies a call (session bytes, session id, or the call
   record's own clock, working directory and home), so a copied slot cannot
   agree with itself.
2. Identical → the capture is written to `transcription/GOLDEN-CONTEXT.json`,
   its digest replaces the `null` in the registry, and both are committed
   **before the first round runs**. Not identical → the batch does not start,
   the discrepancy goes to `DEVIATIONS.md`, and the repeat lands in
   `attempt-2`; no arm data exists at that point, so this cannot be a
   data-dependent choice.
3. Every slot of every arm records the golden digest its batch verified at
   preflight, so a capture derived after the batch and re-pinned makes every
   slot `golden-mismatch` rather than re-admitting it.
4. The recaptured capture is compared against Study 011's pinned golden
   (`a8a2a735…`) and the comparison is reported in `ANALYSIS.md`. It gates
   nothing.

One consequence is registered: **the golden may not be re-derived mid-batch.**
If the environment changes such that honest runs stop matching, the rounds
already run cannot be re-admitted under a new capture, so the batch is declared
short at the last good round and the study reports the arms as far as they got.

### 3.3 Invalid runs, the partition, and the run-026 rule

A run that fails admission or regeneration is **pipeline-invalid**: counted,
reported with its refusal code, and excluded from that arm's rate
denominators. A run that is admissible and compiles but whose author produced
nothing usable is **authoring-empty** — valid, counted, covering nothing.
Excluding authoring-empty runs would quietly condition every rate on the author
having succeeded, which is not the quantity §1 asks for, and in this study it
would do something worse: **a perturbation that makes the author fail outright
would be scored as if it had never been tried.**

**The run-026 rule, registered.** Study 011 lost one run of fifty to
`transcript-refused` — a pre-prompt context that differed from the golden at
its first developer item, most likely service-side boilerplate variation. That
run was published, named, counted in the pipeline-invalid rate, and **not
adjudicated by opening the transcript to see whether the difference "mattered"**.
This study does the same, and states why in advance: an allowlist that starts
making exceptions is a denylist. Registered consequences:

- a refused transcript is **pipeline loss, published, never opened to
  adjudicate admission**. The bytes are retained and published; nobody reads
  them to decide the run's fate;
- the pipeline-invalid rate is **its own endpoint, per arm** (§4.4), reported
  in the headline beside the coverage rates;
- pipeline loss is **not** evidence about a perturbation. If one arm loses
  conspicuously more runs than the others, that is reported as a caution over
  that arm's contrasts and is not itself a contrast result — the gates are
  arm-independent by construction and no registered reading treats a refusal
  rate as an effect of the policy text.

The partition is registered exhaustively, code by code. This is every outcome
the scorer can assign to a run, and a harness test parses this table out of
this file and diffs it against the scorer's own partition table and against the
codes its admission can actually return.

| outcome | partition |
| --- | --- |
| `slot-symlink` | pipeline-invalid |
| `slot-irregular` | pipeline-invalid |
| `slot-shape` | pipeline-invalid |
| `call-unreadable` | pipeline-invalid |
| `model-mismatch` | pipeline-invalid |
| `binary-mismatch` | pipeline-invalid |
| `cli-mismatch` | pipeline-invalid |
| `registry-mismatch` | pipeline-invalid |
| `golden-mismatch` | pipeline-invalid |
| **`arm-mismatch`** | **pipeline-invalid** |
| `isolation-unproven` | pipeline-invalid |
| `session-count` | pipeline-invalid |
| `call-nonzero-exit` | pipeline-invalid |
| `no-session` | pipeline-invalid |
| `no-completion` | pipeline-invalid |
| `no-context` | pipeline-invalid |
| `transcript-refused` | pipeline-invalid |
| `context-mismatch` | pipeline-invalid |
| `completion-unreadable` | pipeline-invalid |
| `compile-refused` | pipeline-invalid |
| `regeneration-mismatch` | pipeline-invalid |
| `refusal-conflict` | pipeline-invalid |
| `scorer-error` | pipeline-invalid |
| *(no code, no parseable array)* | **authoring-empty — valid, in every denominator, covering nothing** |
| *(no code)* | **valid** |

`arm-mismatch` is the one new code: the slot's recorded arm or arm-prompt
digest is not the arm whose tree it sits in. Every other code, and every
registration behind it — the `lstat`-first slot-tree rule, the totality rule
that reads `REFUSAL.json` inside the total path through the duplicate-key
loader, `refusal-conflict`, `scorer-error` — is Study 011 §3.3's, ported
unchanged, and the port is reviewed against that text rather than re-derived.

## 4. Endpoints

Estimation and registered decision rules. **No hypothesis test, no p-value, no
multiplicity correction** — there is no test to correct. The §5 verdicts are
decisions computed from exact intervals by a rule fixed before the data, not
inferences with an error rate to control.

**The full verdict surface, counted here so it is not undercounted later:**

| verdicts | how many | where |
| --- | --- | --- |
| level verdicts (per arm × per class) | 5 × 6 = **30** | §5.1 |
| contrast verdicts (four arms against A × per class) | 4 × 6 = **24** | §5.2 |
| level verdicts under S10 old-edge cross-scoring | up to 5 × 6 = **30** | §4.6 S10 |
| registered census expectation patterns (per arm) | **5** | §4.5 |

**Every one of them is marginal, and no simultaneous claim is made over any of
them.** Every interval is marginal too. §5.4 says where multiplicity actually
bites — in the *pattern* thresholds of §5.3, which are joint statements — and
gives the joint arithmetic for each of them before the data.

### 4.1 The sets, per valid run

Computed by the scorer over that run's compiled records only. **The registered
mirror module at that arm's registered `(T_low, T_high)` is the arbiter for
that arm's labels** — one module, at the destination digest §2.2 and §2.10
pin, instantiated from the arm's pinned `ARM.json` — and the arm's own family
is the arbiter for that arm's classes. No unpinned code decides a label. No
evaluator runs; no pack is evaluated; jpack never runs.

- **A(r)** — the run's accepted records.
- **H(r)** — records in A whose recorded `decision.outcome` equals
  `verdict(record.vendor, T_low_X, T_high_X)` for the run's arm X.
- **Q(r)** — A \ H: records reaching a class with their own label wrong.
  Retained as data, never dropped, never counted in H.
- **class_i(r)** — the records in A satisfying arm X's `FAMILY.json` mutation
  *i*'s predicate under the ported `predicate_matches`.

### 4.2 Primary endpoint: per-class per-arm coverage rate

For each arm X ∈ {A, B, C, D, E} and each i ∈ 0…5:

```
k_{i,X} = |{ valid runs r of arm X : H(r) ∩ class_i(r) ≠ ∅ }|
c_{i,X} = k_{i,X} / V_X
```

reported as the exact fraction, as a decimal to 3 places, and with the §4.3
interval. Thirty numbers with thirty intervals. Denominators are identical
across classes *within* an arm by construction, and the scorer asserts it: it
collects the six `trials` values it just wrote per arm and refuses the whole
scoring unless the set is exactly `{V_X}`.

### 4.3 Clopper–Pearson 95% intervals, normatively

Study 011 §4.3's procedure, ported verbatim, so that a reader can recompute
every published bound from `RESULTS.json`'s integers alone and the arithmetic
cannot drift with a platform's libm:

```
alpha          = Fraction(1, 40)                        # 0.025, one tail of a two-sided 95%
tail_ge(k,n,p) = sum over j = k..n of  C(n,j) * p^j * (1-p)^(n-j)
tail_le(k,n,p) = sum over j = 0..k of  C(n,j) * p^j * (1-p)^(n-j)

lower(k,n) = 0.0  if k == 0  else  bisect(lambda p: tail_ge(k,n,p) <  alpha)
upper(k,n) = 1.0  if k == n  else  bisect(lambda p: tail_le(k,n,p) >  alpha)

bisect(pred):                       # pred is monotone: true on [0,root), false after
    lo, hi = 0.0, 1.0
    repeat EXACTLY 200 times:       # fixed iteration count, no early exit
        mid = (lo + hi) / 2.0       # IEEE-754 double
        if pred(mid): lo = mid
        else:         hi = mid
    return lo
```

`C(n,j)` is `math.comb`; the tail sums are evaluated in `fractions.Fraction`
and every comparison against `Fraction(1,40)` is an exact rational comparison;
terms are summed in ascending `j`; there is no randomness anywhere and nothing
to seed.

**Registered test vectors, asserted by the harness tests in CI.** At n = 25,
this study's own denominator:

| k / 25 | exact 95% interval |
| --- | --- |
| 0 | [0.0000, 0.1372] |
| 1 | [0.0010, 0.2035] |
| 2 | [0.0098, 0.2603] |
| 3 | [0.0255, 0.3122] |
| 12 | [0.2780, 0.6869] |
| 22 | [0.6878, 0.9745] |
| 23 | [0.7397, 0.9902] |
| 24 | [0.7965, 0.9990] |
| 25 | [0.8628, 1.0000] |

And **Study 011's registered vectors at n = 50 are retained as a port
control** — `k=0 → [0.0000, 0.0711]`, `k=1 → [0.0005, 0.1065]`,
`k=25 → [0.3553, 0.6447]`, `k=40 → [0.6628, 0.8997]`,
`k=45 → [0.7819, 0.9667]`, `k=50 → [0.9289, 1.0000]` — so the ported
arithmetic is checked against numbers a predecessor already published.

**The frozen interval scope.** An interval is computed and published for every
rate whose denominator is `V_X` or N: the six primary rates per arm (§4.2); the
raw, Q and Q-only per-class rates per arm (§4.6 S1, S2); the all-six rate per
arm (S3); the old-edge cross-scored rates per arm (§4.6 S10); and the
pipeline-invalid rate per arm (§4.4). It is **not** computed for the mislabel
share, whose denominator is the runs that reached the class, nor for any
record-level pooled quantity, nor for any census count in §4.5, because records
within a run are not independent. A harness test walks `RESULTS.json` and
requires the set of blocks carrying `ci95` to be exactly that list.

### 4.4 Primary endpoint: the pipeline-invalid rate, per arm

`rho_X = I_X / N`, with an exact interval, and the histogram of refusal codes
over §3.3's registered table, **per arm and pooled**. Reported in the headline
beside the coverage rates, never as a footnote. At `rho_X ≥ 0.10` the arm's
contrasts carry a stated caution over the whole arm. It changes no verdict:
pipeline-invalid runs have already left the denominator and already widened
every bound, and charging them twice would be double-counting — Study 011 §5's
correction, ported.

At N = 25 this endpoint is coarse and the coarseness is registered: 0/25 gives
[0.0000, 0.1372] and 1/25 gives [0.0010, 0.2035], so this study cannot
distinguish a 2% loss rate from a 15% one and does not try.

### 4.5 Registered secondary: the probe census, promoted

Study 011's diversity census was post-hoc. Here it is **registered before the
data**, with the definitions and the arithmetic ported from
`analysis/diversity.py`, because the census is what the question in §1 is
actually about: a coverage rate counts the runs in which a class was reached
and says nothing about how many different ways it was reached.

The four definitions are the census's own, restated so this file is
self-contained, and **keyed to the arm's thresholds** rather than to 40 and 70:

- **band** — the three decision regions on `riskScore`: `< T_low`,
  `[T_low, T_high)`, `>= T_high`.
- **profile** — `(sanctionsHit, embargoed?, handlesPersonalData, band)`, where
  *embargoed?* is `registeredCountry` in KP/IR/SY. Two records with the same
  profile ask the policy the same question.
- **probe** — `(exact riskScore string, sanctionsHit, embargo-normalised
  country, handlesPersonalData)`. Non-embargoed countries collapse to one token
  because the policy cannot distinguish CA from DE. The count with the exact
  country code is also reported and is a count of *surface* variation.
- **deciding clause** — the first clause of the mirror's if-chain that fires.

Distances are exact `Decimal` arithmetic on the `riskScore` strings against the
arm's three edges — `T_low − 1` (unstated in every arm), `T_low` and `T_high` —
which for A, B, C, E are {39, 40, 70} and for D are {44, 45, 72}.

Registered census endpoints, per arm, all descriptive, all published:

- **X1 — distinct probes per class**, the count and the modal probe's run
  share, and the runs still covered if the modal probe is deleted. Study 011's
  values, which are the reference this study's A arm is read against, were
  **2, 6, 2, 24, 26, 2** — three classes (0, 2, 5) on two probes each, and four
  classes (0, 1, 2, 3) containing a probe present in every one of the 49 runs.
- **X2 — the threshold-distance histogram**, over the registered buckets:
  `exactly on an edge`, `0 < d ≤ 0.001`, `0.001 < d ≤ 0.01`,
  `0.01 < d ≤ 0.1`, `0.1 < d ≤ 1`, `d > 1`. The buckets are registered rather
  than the raw distances on the census's own recommendation: the interesting
  rare event is "distance in (0.01, 1.0]", which occurred 4 times in 784
  records in Study 011.
- **X3 — the near-edge tables**, per edge: the exact values strictly below
  within 1.0, the count exactly at, and the exact values strictly above within
  1.0. This is the table that showed the empty [23.75, 39) band.
- **X4 — within-run and across-run redundancy**: distinct profiles per run, and
  the number of runs sharing a whole-run profile multiset.
- **X5 — per-clause deciding counts** and the outcome distribution.
- **X6 — the plausible-misderivation census, arm E only.** Registered *before*
  the data, as a named census output, so that a comprehension failure in arm E
  is **diagnosed rather than assumed away by S5**. The registered list is every
  value arm E's frozen wording admits under a wrong but coherent reading, and
  the census reports, per value, the count of records at it and within 0.01 of
  it:

  | value | the misreading that produces it |
  | --- | --- |
  | 70, 40 | the correct derivation — seven tenths and four tenths of a full range of one hundred |
  | 0.7, 0.4 | the fractions taken as scores rather than as fractions *of the range* |
  | 7, 4 | "seven tenths"/"four tenths" read as the numerals alone |
  | 28 | four tenths of the **review threshold** (0.4 × 70) instead of of the range — the reading an earlier draft's pronoun made available, removed under D-3 and registered here because removing a reading is not the same as proving it gone |

  Mass at 0.7/0.4, 7/4 or 28 is evidence that arm E measured comprehension
  rather than anchoring, and §5.3 (i) reads it that way. Descriptive; no §5
  decision reads X6, and it carries no interval (record-level counts).

**Registered expectations, descriptive, no verdict attached.** These are stated
before the data so they cannot be invented after it, and no §5 decision reads
them:

- under **D**, the mass of X2's on-edge and near-edge buckets moves to the new
  edges {45, 72}, and the near-edge tables at 40 and 70 empty out;
- under **E**, the on-edge bucket shrinks and the `0.01 < d ≤ 1` buckets grow —
  a diffuse author has nothing to hug;
- under **B** and **C**, X1 and X2 stay close to arm A's;
- in **every** arm, class 4's probe count stays far above the numeric classes',
  because it has no edge to collapse onto.

If E's records nevertheless cluster exactly on 40 and 70, the model derived the
literals and then anchored on them, and the anchoring is to the *value* rather
than to the *token* — **derive-then-hug**, reading 2 of the three §5.3 (i)
enumerates. It is registered here so it is available before the data rather
than improvised after it. §5.3 (i) also registers **recall** as reading 3, and
records that exact clustering cannot separate reading 2 from reading 3.

### 4.6 The other secondaries, ported

- **S1 — raw intersection rate**, per class per arm: the class was reached by
  some accepted record, label irrelevant. `a_i − c_i` is the label tax.
- **S2 — reached-but-mislabelled**, per class per arm, and the mislabel share
  `s_i` over the runs that reached the class (0 when that denominator is 0).
- **S3 — coverage breadth per run**, per arm: the distribution over 0…6 and the
  all-six rate with an interval.
- **S4 — record volumes** per arm: `|A|`, `|H|`, `|Q|`, dropped, the drop-code
  histogram, and per-run min/mean/max of all four.
- **S5 — label accuracy** per arm: pooled `|H| / (|H| + |Q|)`, and the per-run
  mean and range over the valid runs with at least one accepted record, with
  both the trials and the excluded count published. No interval: records within
  a run share an author turn.
- **S6 — distinct outputs** per arm and across arms: the number of distinct
  `sha256(completion.txt)` and the largest identical group. Identical
  completions are data, not defects, but they weaken the independence premise,
  so `ANALYSIS.md` reports this before the rates if any group exceeds one.
- **S7 — coverage against round index**, per class per arm: the ordered 0/1
  sequence and its halves. Descriptive; no trend statistic is registered.
- **S8 — wall clock** per slot, over the slots that reached the call, with the
  count that did not named.
- **S9 — the review tiers of Study 011 §5**, applied per arm unchanged: LIGHT
  at exact lower bound ≥ 0.80, STANDARD at ≥ 0.40, FULL below, with the one-step
  escalation at mislabel share ≥ 0.20. Reported because it is the product
  quantity the previous study registered; it is **not** the §5 decision rule of
  this study and no contrast reads it.
- **S10 — old-edge cross-scoring [D-12].** Every arm's records are *also*
  scored against **arm A's** family predicates, with labels still taken from
  that arm's own mirror. This is class membership only: it asks where each arm's
  records land in *the baseline's* coordinate system. It is the direct measure
  of the rename prediction and its registered pattern is in §5.3.

**The S-numbers diverge from Study 011's, and the mapping is stated rather
than left to trip a reader coming from that file.** 011's S8 is the
pipeline-invalid rate and its S9 the wall clock; here the pipeline-invalid rate
is **promoted out of the secondaries to §4.4** as a primary endpoint, **S8** is
the wall clock (011's S9), **S9** is 011's §5 tier mapping (which 011 carried
in its §5 rather than as a secondary), and **S10** is new to this study. S1–S7
are 011's S1–S7 unchanged in meaning, keyed per arm.

**S5 and S2 are load-bearing this time and are registered as such.** They are
what separates two readings of a collapse in arm D or E. If coverage collapses
while label accuracy stays at the ceiling, the model understood the thresholds
and simply did not *test* them — an anchoring result. If label accuracy
degrades too, the model failed to derive or apply the values, and the collapse
is a comprehension failure, not an anchoring one. Both are publishable; they
are different findings; and which one this study is looking at is decided by a
quantity registered before the data.

### 4.7 What is reported, and how

`RESULTS.json` carries, for every rate, the integer numerator, the integer
denominator, the float point estimate, and both bounds, arm by arm — so every
published decimal is recomputable from integers. `RATES.md` is the scorer's
rendering of the rate tables; `CENSUS.md` is the scorer's rendering of §4.5;
`ANALYSIS.md` leads with the five arms' per-class rates, the five `rho_X`, and
the §5 verdict table, and applies §5's rule without adjusting it. `ANALYSIS.md`
also reports, without a verdict: arm A against Study 011's published rates and
census (drift, §2.1), and the recaptured golden against 011's (§3.2).

## 5. The registered decision rule, and the predictions

Registered before any data, applied afterwards, never re-cut. If the verdicts
this rule produces look wrong, they are published as computed and the
disagreement goes in `ANALYSIS.md` as a limitation of the rule — not repaired
by moving a threshold.

### 5.1 The level verdict, per arm per class

One quantity in one unit, as in Study 011 §5: the exact Clopper–Pearson bounds
of §4.3 for that arm's own rate, written `L_{i,X}` and `U_{i,X}`.

| condition | level |
| --- | --- |
| `L_{i,X} ≥ 0.70` | **HIGH** |
| otherwise, `U_{i,X} ≤ 0.30` | **LOW** |
| otherwise | **MID** |

The two cuts are symmetric about 0.5 and, at `V_X` = 25, land at: HIGH iff
`k ≥ 23` (the arm missed at most 2 of 25), LOW iff `k ≤ 2` (the arm reached the
class at most 2 times of 25). MID is everything between, and MID is a real
outcome that gets published as MID.

**[D-2]** These cuts are this study's, not Study 011's. 011's LIGHT cut of
`L ≥ 0.80` is unreachable at N = 25 by anything but a perfect arm (`k = 24`
gives `L = 0.7965`), which would make a single stray miss in a control arm read
as an inconclusive result; the operating characteristics in §5.4 are why 0.70
and 0.30 were chosen instead, and they are stated so the review can move them
before the data rather than a reader after it. 011's tier cuts are still
computed and published, as S9.

The cuts are stated **on bounds, not on observed coverage**, so that an arm
with a smaller `V_X` faces a boundary that already carries its smaller sample.
That is Study 011 §5's own correction, and it is why unequal arm denominators
(§2.8) do not silently move a registered threshold. Its floor is registered in
§2.8: **below `V_X` = 11 the HIGH level is unreachable** (a perfect arm is
bounded below at 0.6915 at V = 10 and 0.7151 at V = 11), and such an arm's six
verdicts are `UNRESOLVED-BY-DESIGN` rather than a table of MIDs a reader might
mistake for a measurement.

### 5.2 The contrast verdict, per arm per class

Against arm A, in the same batch:

| condition | contrast |
| --- | --- |
| level(A) = HIGH and level(X) = LOW | **COLLAPSE** |
| level(A) = HIGH and level(X) = HIGH | **TRACKING** |
| otherwise | **INDETERMINATE** |

COLLAPSE therefore entails disjoint 95% intervals in the predicted direction
(`U_X ≤ 0.30 < 0.70 ≤ L_A`) without needing a separate difference statistic and
without a distribution for a difference of proportions. INDETERMINATE covers
both "the arm landed in the middle" and "the baseline itself was not HIGH", and
it is a publishable outcome, not a failure to report.

**A second, weaker contrast is reported beside the first and never substituted
for it [D-17].** The level-gated rule above discards information: a class where
arm E reads LOW (`k ≤ 2`, `U ≤ 0.2603`) while arm A reads MID (say `k = 22`,
`L = 0.6878`) is published as INDETERMINATE even though the two exact intervals
are disjoint by a wide margin in the predicted direction — and §5.4's joint
arithmetic makes that the *likely* shape of a partial baseline, not a corner
case. So:

| condition | second contrast |
| --- | --- |
| `U_X < L_A` | **COLLAPSE-DISJOINT** |
| otherwise | **—** |

COLLAPSE-DISJOINT is computed from the same integers, adds no distribution for
a difference of proportions, and is **reported beside the level-gated verdict,
never in place of it**. §5.3's registered predictions and falsification
conditions are stated on the level-gated COLLAPSE alone; COLLAPSE-DISJOINT
gates nothing and falsifies nothing. The alternative — the level-gated rule
alone, accepting the discarded information — is registered under **[D-17]**.

### 5.3 The four registered predictions, and what falsifies each

**(i) E vs A — the falsifier this study exists for.** Predicted: **COLLAPSE on
the four narrow numeric classes 0, 1, 2 and 5**, with class 3 (a 30-wide band
in arms A, B, C and E) and class 4 (no numeric content) predicted TRACKING.

**Both directions are registered, symmetrically, and every remaining pattern
is registered too [D-10].** An earlier draft was crisp on falsification and
silent on confirmation, which is the wrong asymmetry for a study whose headline
would be the confirmed prediction. Over the four narrow numeric classes 0, 1, 2
and 5:

| pattern | reading | published as |
| --- | --- | --- |
| COLLAPSE on **≥ 3 of 4** | R1 **confirmed** | CONFIRMED |
| HIGH on **≥ 3 of 4** | R1 **falsified** | FALSIFIED |
| every other pattern | neither | **INDETERMINATE** |

> **Falsification, registered [D-10]:** if arm E's level verdict is **HIGH for
> three or more of the four narrow numeric classes**, **R1 is wrong**. The
> correction is published with the same prominence as the claim — in
> `ANALYSIS.md`'s headline, in this study's README, in the venue `CLAIM.md`
> records, and as a correction banner at the head of
> `studies/011-authorship-coverage-rates/DIVERSITY.md` — and it is stated as a
> correction, not as a nuance. What is retracted is **R1**; the census's
> descriptive sentence about its own corpus stands regardless, and §8 says so.

> **Confirmation, registered [D-10]:** if arm E's level verdict is **LOW on
> three or more of the four narrow numeric classes with arm A HIGH on the
> same** — that is, COLLAPSE on ≥ 3 of 4 — R1 is **confirmed for this
> instance**, in the sense §5.5 and §9 bound: one denaming, one policy family,
> one model, one day.

**INDETERMINATE is a real outcome and is very likely the modal one.** Two
COLLAPSE and two MID is INDETERMINATE. **All four MID is INDETERMINATE** — and
§5.4 records that at a true coverage of 0.30 this rule returns MID 99.1% of the
time, so an all-MID arm E is exactly what any *partial* anchoring effect looks
like here. It is published as INDETERMINATE, R1 is recorded as **neither
confirmed nor falsified**, and no post-hoc pattern is substituted for the
registered one.

§4.6 S5 is what distinguishes a collapse that means "did not test the boundary"
from one that means "could not derive the boundary"; §4.5's X6 census is what
diagnoses a wrong derivation specifically; and §4.5's X2/X3 census is what
distinguishes "no anchor" from "an anchor derived and then hugged".

**A third reading of an E-maintains-coverage outcome is registered before the
data, because arm E is denamed but not de-referenced.** §2.5 records that arm
E's preamble retains "Study 010", a name-keyed pointer to a public repository
whose policy states 40 and 70. So an arm E that maintains coverage admits three
readings, not two:

1. **R1 is wrong** — the author derives boundaries rather than copying them;
2. **derive-then-hug** — the author derived 40 and 70 from the words and then
   anchored on the *values*, so the anchoring is to the value rather than to
   the token (already registered at the end of §4.5, and it stands);
3. **recall** — the author recognised the named study and recalled its
   literals, deriving nothing.

The registered discriminator is **§4.5's X3 near-edge tables**: exact
clustering on 40 and 70 in arm E is consistent with reading 2 *and* with
reading 3 and cannot separate them, while **dispersion** — mass in the
`0.01 < d ≤ 1` buckets, or in X6's misderivation values — is consistent with
neither and supports reading 1. Registered honestly: **this study cannot
separate readings 2 and 3 from each other.** [D-16] is the design change that
would (a preamble carrying no study name), and it is the review's to make.

**(ii) D vs A — coverage follows the numbers.** Predicted: **TRACKING on all
six classes under D's own family**, and, under the S10 old-edge cross-scoring
against arm A's family:

| old-edge class, arm D | predicted | why |
| --- | --- | --- |
| 0 (exactly 70) | LOW | D's records hug 72 |
| 1 ([70, 71)) | LOW | same |
| 2 (P ∧ [40, 41)) | LOW | D's records hug 45 |
| 3 ([40, 70)) | **HIGH — not a falsifier** | arm A's 30-wide band, which D's [45, 72) records fall inside by construction |
| 4 (SY) | **HIGH — not a falsifier** | no numeric content |
| 5 (P ∧ [39, 40)) | LOW | D's below-threshold hugs are at 44 |

**Three outcomes are registered for arm D, not two.**

> **Falsification, registered:** if D's **new-keyed** verdicts are LOW on the
> narrow numeric classes while its **old-keyed** verdicts are HIGH, the model
> reproduced 40 and 70 in the face of a text that says 45 and 72. That is not a
> failure of the anchoring hypothesis; it is a **contamination signal** — this
> policy family has been public in this repository since Study 010 merged
> (2026-08-06) — and it is registered here, before the data, as the reading
> that outcome gets.

> **The third outcome, registered:** if D's **new-keyed** verdicts are LOW on
> the narrow numeric classes **and its old-keyed verdicts are LOW too**, that
> is neither tracking nor contamination. It is a **general degradation** — the
> author placed records at neither threshold pair — and it is **published as
> one**, not read as evidence for or against R1. The registered candidate
> explanation is §2.4's salience confound [D-18]: 40 and 70 are decade-round
> and 45 and 72 are not, so an author drawn to round values rather than to the
> stated literal produces exactly this pattern. §4.5's X2 and X3 census under
> arm D is what shows where the records went instead, and S5 is what says
> whether the labels survived.

**(iii) B vs A and C vs A — the anchoring controls.** Predicted: **TRACKING on
all six classes in both arms.**

> **Falsification, registered:** a COLLAPSE on any class in arm B or arm C
> indicts anchoring to the prompt's *shape* beyond its literals — the author is
> following the sentences, not the rule. That is a finding in its own right and
> is published as one.

And a dependency that is registered rather than discovered at write-up time,
**stated as a count rather than as a word**: arm E's result is interpretable as
a literal effect only if **arm B reads TRACKING on at least five of its six
classes and arm C reads TRACKING on at least five of its six**. Below that, the
study publishes arm E's verdicts *and* says the controls did not hold: if B
falls short, E's collapse could be paraphrase-driven; if C falls short, it
could be order-driven; either way the weaker reading is what gets claimed.

What that dependency costs is stated before the data rather than discovered
after it. It is a joint condition over twelve level verdicts, and §5.4 records
that at a true per-class p of 0.95 — inside 011's own published interval —
**P(all twelve read HIGH) is 0.1957**. The five-of-six form is chosen for
exactly that reason: requiring all twelve would make the dependency fail
roughly four times in five under a *true* null effect in both control arms, and
a dependency that usually fails is not a control.

**(iv) Class 4, the embargo-membership class, in every arm.** Predicted:
**TRACKING in all four contrasts.** It is the only class whose predicate names
no numeric boundary, and Study 011's census found it the best-witnessed class
in the corpus (26 distinct probes, no probe reaching more than 11 of 49 runs).

> **Falsification, registered:** if class 4 collapses in arm E, the effect is
> not literal-specific — something about the denamed text degraded authoring
> generally — and every other reading of arm E in this study is withdrawn in
> favour of that one.

### 5.4 What N = 25 can and cannot resolve

Computed with this study's own interval code, before any data, and asserted by
a harness test so the rule's power is not left to a reader's intuition. Under
the §5.1 cuts at `V_X` = 25 (HIGH iff `k ≥ 23`, LOW iff `k ≤ 2`), the
probability the rule assigns each level to a class whose *true* coverage is p:

| true p | P(HIGH) | P(LOW) | P(MID) |
| --- | --- | --- | --- |
| 1.00 | 1.0000 | 0.0000 | 0.0000 |
| 0.98 | 0.9868 | 0.0000 | 0.0132 |
| 0.95 | 0.8729 | 0.0000 | 0.1271 |
| 0.90 | 0.5371 | 0.0000 | 0.4629 |
| 0.80 | 0.0982 | 0.0000 | 0.9018 |
| 0.50 | 0.0000 | 0.0000 | 1.0000 |
| 0.30 | 0.0000 | 0.0090 | 0.9910 |
| 0.20 | 0.0000 | 0.0982 | 0.9018 |
| 0.10 | 0.0000 | 0.5371 | 0.4629 |
| 0.05 | 0.0000 | 0.8729 | 0.1271 |
| 0.02 | 0.0000 | 0.9868 | 0.0132 |
| 0.00 | 0.0000 | 1.0000 | 0.0000 |

**The joint figures, registered beside the marginal ones**, because the study's
own headline is a joint statement and an earlier draft published only the
marginal column. Computed under an independence assumption across classes that
the data will not support (Study 011's runs covered all six classes together in
every valid run), which makes these **lower bounds on the true joint
probabilities rather than estimates of them** — and stated anyway, because
independence is the assumption under which they are *worst*, and a design that
survives its worst case does not need the better one. Asserted by the same
harness test as the marginal table:

| true p | P(HIGH), one class | P(all **four** narrow HIGH) | P(all **six** HIGH) | P(all **twelve** HIGH, arms B and C) |
| --- | --- | --- | --- | --- |
| 1.00 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 0.98 | 0.9868 | 0.9481 | 0.9231 | 0.8522 |
| 0.95 | 0.8729 | 0.5806 | 0.4424 | 0.1957 |

and, for the predicted effect itself, `P(all four classes COLLAPSE)` at
`p_A = 0.95` and `p_E = 0.05` — each class needing arm A HIGH *and* arm E LOW —
is **0.3370**.

Read plainly:

- **The baseline is comfortable marginally and is not comfortable jointly.**
  Study 011 observed 49/49 with a lower bound of 0.9275; at a true p of 0.98 an
  arm reads HIGH 98.7% of the time, and at 0.95, 87.3%. But at that same 0.95 —
  which is *inside* 011's own published interval — **arm A reads HIGH on all
  six classes only 44.2% of the time, and on all four narrow numeric classes
  only 58.1%.** Since §5.2 makes `level(A) = HIGH` a precondition of any
  COLLAPSE, there is roughly a 42% chance that at least one falsifier-relevant
  class cannot yield a contrast verdict at all, **from sampling alone, under
  zero drift**. §2.1 registers the consequence: an arm-A class below HIGH is
  reported as an unresolved baseline for that class, not as a drift finding.
- **Even a near-total collapse is not certain to be read as one.** At
  `p_A = 0.95` and `p_E = 0.05` — the regime the prediction describes — the
  probability of COLLAPSE on all four narrow numeric classes is 0.3370, while
  the registered CONFIRMED pattern (≥ 3 of 4) is far more attainable. That
  asymmetry is why the pattern threshold is three and not four.
- **A real collapse is caught.** At a true p of 0.05 the rule says LOW 87.3% of
  the time, and at 0.02, 98.7%. The prediction is that E's numeric classes go
  to roughly zero, and that is the regime the rule resolves.
- **A partial collapse is not.** At a true p of 0.30 the rule says MID
  essentially always (99.1%), and at 0.10 it says LOW only 53.7% of the time.
  **N = 25 separates "still reliably covered" from "essentially never covered"
  and resolves nothing in between**, and every MID in the published table means
  exactly that. Stated as the smallest real effect this design cannot see:
  **any anchoring effect that leaves coverage above roughly one run in five is
  invisible to this study.** A drop from 1.00 to 0.30 reads MID 99% of the
  time; a drop to 0.10 reads LOW only 54% of the time; only a fall below about
  0.06 is reliably called (P(LOW) = 0.8129 at p = 0.06, 0.7466 at 0.07). §9
  repeats it in those words.
- **Multiplicity, where it bites and where it does not.** The 30 level verdicts,
  the 24 contrast verdicts and the up-to-30 S10 verdicts (§4) are all marginal
  and no simultaneous claim is made over any of them. Where it matters is the
  *pattern* thresholds of §5.3 — "three or more of four", the twelve-verdict
  control dependency — and there the arithmetic is stated rather than assumed:
  if E's four narrow numeric classes each truly sat at 0.95, the probability of
  reading three-or-more HIGH would be 0.9187, under the same independence
  assumption as the joint table above. The predicted effect is 1.00 → ~0, which
  is not a regime where multiplicity is the binding uncertainty; the binding
  uncertainty is §9's, and this bullet exists so nobody mistakes one for the
  other.

**Why 25 and not 20, 30 or 50.** The exact bounds, for a perfect arm:
n = 16 → [0.7941, 1] (below the HIGH cut, so a perfect arm could not read
HIGH); n = 17 → [0.8049, 1]; n = 20 → [0.8316, 1]; n = 25 → [0.8628, 1];
n = 30 → [0.8843, 1]; n = 50 → [0.9289, 1]. A half-covered class carries
±0.228 at n = 20, ±0.205 at 25, ±0.187 at 30, ±0.145 at 50. At n = 20 the HIGH
cut lands at `k ≥ 19` — one miss allowed — and P(HIGH | p = 0.95) falls to
0.736; at n = 30 it lands at `k ≥ 27` and P(HIGH | p = 0.95) rises to 0.939.
Thirty is better and costs 25 more calls; fifty is better still and costs 125
more. **The budget: 5 arms × 25 = 125 authoring calls, plus 2 golden probes and
1 isolation-negative probe = 128 calls**, which at Study 011's observed mean of
42.08 seconds per call is about 90 minutes of sequential wall clock, comfortably
inside the one-day rule. At N = 30 it is 150 calls and about 105 minutes; at
N = 50, 250 calls and about three hours. **[D-1]** N = 25 is the proposal
because it is the smallest multiple of 5 that gives the HIGH cut two runs of
slack and catches the predicted collapse with high probability; the review may
move it to 30 for a materially better control arm at a 20% larger budget, and
should keep it a multiple of 5 for §2.8's position balance.

**The joint figures strengthen the case for N = 30 more than the marginal ones
do, and are stated here so D-1 is decided on the right quantity.** Marginally,
P(HIGH | p = 0.95) rises 0.8729 → 0.9392 — a 6.6-point gain that looks modest.
Jointly, **P(arm A reads HIGH on all six classes) rises 0.4424 → 0.6865**, from
a coin flip to better than two in three, because the marginal gain compounds
six times. That is the quantity §5.2 actually depends on, and at N = 25 it is
the single largest way this design fails without anything being wrong.

### 5.5 What a verdict does not license

A TRACKING verdict on arm B says that *this* paraphrase did not move coverage.
It does not say paraphrase never does. A COLLAPSE verdict on arm E says that
*this* denaming did. Each arm is one instance of its perturbation type; that is
the design's central limitation and §9 states it again rather than leaving it
here.

No verdict in this study is a statement about defect detection. No pack is
evaluated, no mutation is applied, no evaluator runs. "Coverage" means a
correctly-labelled record fell inside a registered predicate under the correct
policy, and Study 011's census already recorded that the claim "low probe
diversity costs detection power" is a plausible mechanism there and a
demonstrated one nowhere.

## 6. Controls and counting integrity

Two lessons from this line's own history govern this section. Study 008: verify
an independence premise **from source** before freezing it, and add controls
that bound what an endpoint can mean. Study 001 `DEVIATIONS.md` §2: a
preregistration constrains what you may claim, it does not check that the claim
was computed on the population it names — the scorer must enforce the
population itself.

**C1 — ported bytes, through a three-level chain, bound by authority rather
than by port kind.** `harness/integrity.py`, in this order: verifies Study
011's `harness/PINS.json` against the digest this study pins for it; verifies
Study 010's `PROTOCOL-LOCK.json` against the digest *011* pins for it; reads
011's `PORTS.md`; then binds every row of §2.2 **to the authority that row
actually has**, as three tiers.

An earlier draft bound the chain by port kind — "every file this study ports
from 011 that 011 itself ported from 010 must equal 010's locked digest on the
source side" — and that rule **refuses this study's own inputs**. Study 011
*adapted* three of those files, so their 011-side bytes differ from 010's lock
by construction, and the fourth over-reach bound a file 010 never locked. The
three tiers, with every digest checked against the artifact that carries it:

| tier | files | source-side binding | destination-side binding |
| --- | --- | --- | --- |
| **1 — 010's lock** | `harness/policy_mirror.py` (`276b5f73…`), `arms/A/FAMILY.json` (`7c3c49e6…`), `arms/A/POLICY.md`'s source `policy/POLICY.md` (`e46f8c48…`), 011's `transcription/PROMPT.txt` (`a68dad10…`, the source of `HEADER`) | equal to the digest in 010's `PROTOCOL-LOCK.json` `lockedInputs`, **and** equal to 011's own copy where 011 holds one | `FAMILY.json` equal to the lock on both sides; the mirror and `arms/A/POLICY.md` equal to the digest `harness/PORTS.md` records for the enumerated change |
| **2 — 011's `PINS.json`** | `transcription/PROBE-PROMPT.txt` (`128aaa9a…`) | equal to the digest **011's `PINS.json`** records. 011 introduced this file; it appears in no `lockedInputs` of 010 and must never be bound to one | equal to 011's digest — a byte-identical port |
| **3 — 011's own bytes** | `harness/records_compile.py` (`6de92175…`), `harness/transcript_check.py` (`0c9d7c79…`), `transcription/authoring_call.sh` (`6e1239f3…`) | equal to the **011-side** digest recorded in this study's `harness/PORTS.md`, **and** to the destination cell of 011's own `PORTS.md` provenance row for that file. **Never** to 010's lock — 011 adapted each of them (from `e58edce3…`, `42d977c4…` and `3b8909aa…` respectively) and the difference is registered, not a defect | equal to the digest `harness/PORTS.md` records |

The four files this study takes from 011's *own* harness (`batch.py`,
`score_rates.py`, `integrity.py`, the census) are in no tier: 011 pinned none of
them, and they are bound to the recorded commit and to nothing older. C1
additionally requires the port table to name exactly the registered set of
files, so a deleted row is a refusal rather than a check silently dropped, and
re-checks the running interpreter against the registry's `python` member. Any
mismatch refuses. It runs in CI **and as a precondition of the batch and the
scorer** — `batch.preflight()` before it creates a slot, `score()` before it
reads one.

What C1 does **not** do, so §7 cannot claim it: it compares no file to a git
`HEAD` blob (this study has no lock-commit machinery), `harness/PORTS.md` is
itself unpinned, and **the four files this study takes from Study 011's own
harness are bound to no lock at all**, because 011 pinned none. What rests on
review and on C3 rather than on a digest chain is exactly those four:
`batch.py`, `score_rates.py`, `integrity.py`, and the census.

**C2 — family/pack coherence, for the arms where it is available.** For arms A,
B, C and E — every arm at (40, 70) — Study 011 C2 runs unchanged against Study
010's pack C, read in place at its pinned digest: every mutation's `patch`
preimage must be present byte-exact at its JSON pointer, the six `index`
members must be contiguous 0–5, and every mutation applied to pack C must
**change** it.

For arm **D** that clause is not available: pack C encodes 40 and 70, so D's
patch preimages are not in it. **[D-6]** The proposal is to replace the
pack-side clause for arm D with §2.4's landmark-grid check (C8) and to state
plainly that D's family is coherent with D's *mirror* and with nothing else;
the alternative the review may prefer is to construct a threshold-shifted pack
`C_D` purely so the clause survives, at the cost of a new artifact that no run
in this study ever evaluates. Either way, no pack is evaluated here and this
control bounds what a *patch* can mean, not what a predicate can.

**C3 — two replication controls, against published numbers.**

1. **The counting.** The ported compiler, mirror and class arithmetic are run
   over Study 010's retained `completion.txt` (digest pinned) and must
   reproduce 010's published profile exactly: `accepted = 16`, `|H| = 16`,
   `|Q| = 0`, H ∩ class counts `(2, 2, 2, 4, 1, 1)`, Q ∩ class counts all zero.
2. **The census.** The ported `harness/census.py` is run over Study 011's
   retained valid slots and must reproduce that study's published headline
   exactly: 49 runs × 16 accepted records = 784, 0 dropped, distinct probes per
   class **(2, 6, 2, 24, 26, 2)**, 410 of 784 records on or within 0.01 of a
   named threshold, and an empty [23.75, 39) approach band. The census is a
   registered secondary in this study, so its port is replication-controlled
   against the numbers `DIVERSITY.md` published rather than reviewed by eye.

C3 does **not** exercise `transcript_check.py` or the wrapper; those are
covered by the admission tests, by §3.2's golden procedure on real bytes, and by
the wrapper-driven harness tests against a stand-in CLI.

**C4 — synthetic fixtures with a known coverage and census profile.**
Hand-authored completions committed as constants whose expected output —
accepted ids, drop codes, H/Q membership, per-class coverage, and the census
counts — is registered in the same committed module. CI runs compiler →
classifier → scorer → census over them and requires equality. The fixtures must
contain at least: one element exercising **each** drop code; at least one class
reached **only** by a mislabelled record; at least one class reached by **no**
record; at least two synthetic runs, one `authoring-empty` and one
`pipeline-invalid`, so the population arithmetic is exercised at known `k` and
`n`; **a synthetic arm at (45, 72) whose records reproduce the same six classes
at the shifted edges**, so the arm parameterization is exercised rather than
assumed; **a synthetic arm whose records cover the new-keyed classes and not the
old-keyed ones**, so S10's cross-scoring is exercised at a known answer; and the
§4.3 registered test vectors at n = 25 and n = 50.

**Three fixtures for the one new admission code and the one changed admission
check**, registered because `arm-mismatch` is the only code this study
introduces and the arm-specific terminal-prompt gate is the only check it
changes — and because in this study **five** prompts first meet that gate on a
real slot, under a round-robin rotation where an off-by-one in the driver's arm
order would place slots in the wrong tree silently. 011 could note that its one
registered prompt first met the ported gate on batch slot 1; that consolation
is not available here. So C4 additionally requires:

1. **a synthetic slot whose transcript carries arm B's prompt bytes inside arm
   A's tree**, required to score exactly `arm-mismatch` — not
   `context-mismatch`, not `transcript-refused`;
2. **a synthetic slot whose `CALL.json` `arm` stamp and `armPromptSha256`
   disagree with each other**, required to score `arm-mismatch`;
3. **one admissible slot per arm**, so the arm-specific terminal-prompt gate is
   exercised at **all five** registered prompt digests in CI, before the batch
   rather than on slot 1.

**C5 — the population filter and the verdicts are in code.** The scorer reads
every slot of every arm, computes each run's admission verdict and each arm's
valid population itself with the §3.3 rule, and refuses if any slot lacks a
terminal outcome, if any arm's slot indices are not exactly the contiguous
range **1…R — where R is the round count `SHORTFALL.json` declares, and exactly
1…N when no shortfall is declared** — or if the arms' slot counts are not the
round-robin schedule's for that R. (An earlier draft required 1…N
unconditionally, which contradicts §2.8's own shortfall path, under which arms
hold R or R−1 slots.) The existing requirement stands unchanged: the declared
round count must match the slots actually present.
**The §5.1 level verdicts and §5.2 contrast verdicts are computed by the scorer
from the integers it just wrote, by the registered rule, with no operator input
and no flag that changes a cut**, and a harness test parses §5.1's and §5.2's
tables out of this file and diffs them against the scorer's own tables. No rate
or verdict may be computed by any other path, and none is reported without its
denominator beside it.

**C6 — isolation demonstrated per run.** Study 011 C6's clause list, ported
unchanged and enforced per run: `isolation: isolated`; a resolved isolated
`HOME` with `CODEX_HOME` its own `.codex`; a working directory that is neither
the home, nor inside it, nor a parent of it; the environment's names exactly
`PATH`, `HOME`, `TMPDIR`, `CODEX_HOME` with non-empty values agreeing with the
recorded paths; a child `PATH` of exactly the six registered system directories
plus one per-run binary directory outside the isolated home; a leak-token-free
working directory re-screened from the recorded path; a `TMPDIR` inside that
run's working directory and not `/tmp`; stdin recorded closed;
`credentialRemoved` exactly when `credentialCopied`; and the **recursive**
pre-call inventory of the isolated home equal to `['.codex', '.codex/auth.json']`
or `['.codex']`. The exactly-one-new-session requirement refuses under
`session-count`, the scratch-outside-every-worktree rule is a wrapper gate, and
the golden and transcript gates refuse under `context-mismatch` and
`transcript-refused` — named here rather than folded into `isolation-unproven`,
because a code should name the cause the evidence establishes.

**C7 — the isolation gate's power, once [D-8].** Before the batch, one probe
call is made **deliberately without isolation**, with the operator's real `HOME`
and its `.codex`, everything else as registered. Registered outcomes: `refused`
(the golden match failed — the expectation), `matched` (the gate has no
demonstrated power against home leakage here; recorded as a stated limitation,
the batch proceeds), and `no-context` (neither comparison happened; exits
non-zero, and the gate's power is reported as undemonstrated). It runs **once
for the whole batch**, not per arm, and the justification is §3.2's: the control
uses the probe prompt and tests home leakage, neither of which depends on which
policy text an arm carries. Retention is by code, not by care: the verdict, a
`CALL.json` stripped of every member naming the operator's environment, and the
context digests when there are any; the transcript is digested, deleted, and
the deletion verified. **Operator assent is a recorded precondition** in the
registry, and the command refuses without it.

**C8 — the arm artifacts are what §2 says they are.** This is the control that
makes "semantics constant, surface perturbed" checkable, and it is this study's
own. `harness/integrity.py` requires, before any call and before any scoring:

1. every arm's four files at their registered digests; the **single registered
   mirror module** `harness/policy_mirror.py` at its registered destination
   digest (§2.2 [D-14]), because it is the arbiter of every arm's labels; and
   `CONVENTIONS_DELTA` and `CLAIM.md` at theirs;
2. the prompt equation of §2.6 for every arm — `PROMPT.txt` = `HEADER` +
   `POLICY.md` minus its final LF — with `HEADER` derived from **011's pinned
   prompt bytes minus 010's locked policy bytes**, 948 bytes, and `arms/A`
   satisfying the same equation as every other arm;
3. the document structure of §2.6 parsed for every arm: one preamble, exactly
   five clause bullets with labels P1–P5 each appearing once, one conventions
   paragraph;
4. the **preamble byte-identical across all five arms**; the conventions
   paragraph byte-identical across A, B, C, D and equal to **010's conventions
   paragraph plus `CONVENTIONS_DELTA`**; and E's equal to that plus the
   registered threshold-definition sentence and nothing else;
5. the **literal census** over clause bodies, run under §2.6's definition —
   digit-runs with clause-label tokens `P1`–`P5` masked out first:
   - B's clause-body digit-run census equals A's, which is
     `{40, 40, 70, 70, 70, 70}`;
   - **B's inclusivity-adjacency pattern matches A's clause for clause**
     (§2.6): in every arm at (40, 70), each numeric bound carries an explicit
     inclusivity word immediately adjacent to its literal, on the same side, in
     the same clause;
   - C's bodies are byte-identical to A's, and its label order is the
     registered permutation, which must be a **derangement**, must resolve
     **every explicit clause-label reference backward**, and must resolve
     **every three-part "absent a sanctions hit or an embargoed registration"
     precondition backward** — the three conditions of §2.6, checked by
     re-deriving them from the parsed bodies rather than by comparing against a
     hard-coded tuple;
   - D's clause-body digit-run census is A's under σ, which is
     `{45, 45, 72, 72, 72, 72}`;
   - **E's clause-body digit-run census is empty**, and the digit-runs in the
     whole of E's `POLICY.md` are exactly the clause labels `P1`–`P5`, in-body
     clause-label references of the form `P<n>`, the token `ISO 3166-1
     alpha-2`, and the preamble's study reference — **and no digit-run anywhere
     in the file equals `40` or `70`**. Registered as the truth of the frozen
     artifact rather than as an aspiration: an earlier draft asserted arm E's
     file was digit-free except for the labels and `ISO 3166-1 alpha-2`, which
     is false of the inherited preamble (`Study 010`) and of P5's own
     cross-reference (`unless P4 applies`), and the check as written would have
     refused the study's own artifact. §2.5 states what the surviving `010`
     costs and §5.3 (i) registers the reading it makes available;
6. the **landmark-grid verdict equality** of §2.4: the registered mirror
   module, **at its registered destination digest**, instantiated at each arm's
   registered `(T_low, T_high)` from that arm's pinned `ARM.json`, produces arm
   A's verdict vector elementwise over that arm's own **260-cell** grid, and
   every arm's family produces A's class-membership vector elementwise over the
   same grid.

What C8 cannot check, stated in the control itself: that arm B's prose is a
*paraphrase* rather than a subtle semantic change, and that arm E's references
are *comprehensible*. Clause 6 catches any divergence that reaches the mirror;
it catches nothing that lives only in the prose. That gap is narrowed by **C10**
and by cross-vendor review of the five texts before the freeze, and is closed by
neither; §7 and §9 say so.

**C9 — the class schema, structurally and extensionally.** Every arm's
`FAMILY.json` must equal §2.3's schema instantiated at that arm's (`T_low`,
`T_high`) — six contiguous indices, and **structural equality of all six
predicate encodings** after substituting that arm's pair, not merely
extensional agreement on the landmark grid. The two bound different failures
and this control asserts the stronger one: structural equality refuses a
predicate that encodes the right set by a different construction, which the
grid cannot see and which would make "the classes are the same six classes"
false in the only sense that matters for a rename. Arm A's `FAMILY.json` must
additionally equal Study 010's locked `FAMILY.json`
(`7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f`) byte for
byte. So "the classes are keyed semantically and constant by construction" is a
checked relation, and the arm that anchors it is the arm whose family a previous
study locked. C8 clause 6's grid equality runs in addition, not instead: it is
the extensional check, and it is what catches an error in the substitution
itself.

**C10 — a clean-room second mirror per arm, before any call.** Study 011 built
this instrument one day before this study was drafted, in
`MIRROR-AGREEMENT.md`, for exactly the circularity this study inherits and
multiplies: "the mirror encodes the same policy text the prompt inlines, so a
misreading the model and the mirror share produces 784/784 agreement no matter
how many witness records exist." Study 012 has **five** policy texts, two of
which (D and E) are authored by the team holding the prediction, and it is the
one pre-data, model-call-free check that can answer the central attack on this
design — *is arm E's wording derivable, or was it written to be hard?*

Registered, per arm, before any call:

1. an independent author receives **that arm's `POLICY.md` bytes and nothing
   else** — not another arm, not the registered mirror, not `FAMILY.json`, not
   a record, not this file — and writes `analysis/mirror2_<arm>.py`;
2. **every clean-room mirror must agree with that arm's registered mirror
   elementwise on the §2.4 landmark grid**, all 260 cells. This is a
   precondition of the batch, not a post-hoc analysis: `harness/integrity.py`
   refuses while any arm's clean-room mirror is missing or disagreeing;
3. the isolation rule, the builder's own report of what it consulted, and the
   full agreement table are published as `MIRROR-AGREEMENT.md` in this study
   directory, following 011's format — including 011's own honesty about what
   agent isolation is: a claim about a process, not a proof.

**The failure consequence is registered in advance, because registering it
afterwards is worthless.** If the clean-room reader given arm E's text alone
**cannot derive (40, 70) from it**, then arm E is an **ambiguity arm rather
than a denaming arm**, its collapse would measure comprehension rather than
anchoring, and it is **re-authored and re-registered before the freeze rather
than run**. The same rule applies to any arm: a clean-room disagreement on the
grid is a defect in the arm text or in the registered mirror, and it is fixed
before the freeze, not explained after the data.

## 7. What is enforced, what is recorded, what is not prevented

Scoped to this design. This study has no publication ordering, no transparency
log, and no beacon, and needs none: there is no draw and no prediction about a
future event — the endpoints are rates and verdicts over slots that anyone with
the pinned binary can re-run.

**Mechanically enforced** (a violation refuses, or the run is scored
pipeline-invalid). Every item names code that runs in the batch, in the scorer,
or in both:

- the three-level ported-byte chain, **each row bound to the authority its own
  column names** — 010's lock, 011's `PINS.json`, or 011's own adapted bytes —
  checked before the driver creates a slot and before the scorer reads one (C1);
- **every arm artifact at its registered digest**, **the single registered
  mirror module at its registered digest**, `CONVENTIONS_DELTA` and `CLAIM.md`
  at theirs, the prompt equation, the document structure, the preamble and
  conventions equalities, the literal census, arm B's inclusivity-adjacency
  pattern, arm C's three ordering conditions, and the 260-cell landmark-grid
  verdict and class equality across all five arms (C8), and the class schema
  per arm, structurally (C9);
- **a clean-room second mirror per arm, agreeing elementwise on the landmark
  grid**, as a precondition of the batch rather than a post-hoc analysis (C10);
- the codex binary digest and the CLI version string, both **before the call**,
  and the model name;
- the registered interpreter (implementation and version series), refused by the
  wrapper before it calls anything and by the batch and the scorer before they
  run;
- the registry of record, per run and per population: every run records the
  registry digest it was made under and any other is `registry-mismatch`; the
  scorer takes no registry, family, prompt, arm or golden path at all and
  derives each from the harness's own location, refusing every argument but the
  batch root and an optional record-emission directory;
- **the arm binding, per slot**: the arm id and the arm prompt digest are
  stamped by the wrapper and checked by the scorer against the tree the slot
  sits in, so a slot made with the wrong policy text cannot enter another arm's
  denominator (`arm-mismatch`);
- **the round-robin schedule**: the driver refuses to create a slot out of the
  registered (round, position) order, refuses any plan that would reach past
  round 25, and refuses any slot in any arm once `RESULTS.json` exists;
- a slot tree of regular files and directories only, decided by `lstat` before
  anything in the tree is opened, before any other check and before the batch's
  own `REFUSAL.json` is read;
- the record-emission directory disjoint from every arm's slot tree, checked on
  both sides' resolved paths **and** their filesystem identity, so publishing
  the derived record trees cannot add a slot to a population that was just
  published;
- the golden recapture derived from at least two **distinct sessions**, checked
  on raw retained evidence, from **probe** calls at the pinned probe-prompt
  digest, under the same ported-bytes, interpreter and freeze preflight the
  calls run; and the golden bound to its pin **and to every slot of every arm**;
- the preregistration's freeze digest as a precondition of the calls as well as
  the scoring, refused while it is null rather than skipped; and
  `harness/integrity.py` refuses while any `(port time)` placeholder remains in
  `harness/PORTS.md` or `harness/PINS.json`;
- the per-run fresh `HOME`/`CODEX_HOME`, the `env -i` scrub with `PATH` and
  `TMPDIR` constructed rather than inherited, the exclusive leak-token-free
  scratch outside every worktree, closed stdin, and every C6 clause;
- the transcript whitelist, the **arm-specific** terminal-prompt rule, the leak
  denylist, the model/cwd binding on every `turn_context` that names either,
  integer exit 0, and completion byte-binding;
- compiler regeneration with byte equality and the exact file set;
- slot exclusivity, contiguous slot indices per arm, and an append-only ledger a
  resumed run merges into and refuses to overwrite;
- the §3.3 partition and the population filter, with the registered code table
  diffed against the code by a test; the equality of the six denominators within
  each arm; **and the §5.1 and §5.2 rules, diffed against this file's tables by
  a test and computed by the scorer alone**;
- the batch/score separation: the driver cannot compute coverage or a verdict;
  the scorer refuses unless the batch is terminal (exactly 25 rounds, or a
  matching `SHORTFALL.json`, never both); the registered scoring command is the
  only publisher and writes to the study root or nowhere.

**Deliberately not claimed.** This study has **no lock-commit machinery**:
nothing compares a worktree file to its `HEAD` blob, and no pinned input is
required to equal a committed blob. What integrity rests on instead is the
digest chain above, ledger discipline, and re-runnability.

**Recorded but not proven:**

- **that each arm's prose says what its mirror computes.** C8 clause 6 binds
  every arm's *mirror* to A's; the prose-to-mirror relation is bounded by C10's
  clean-room re-derivation and by human review, and closed by neither. This is
  still the study's largest unmechanised premise and it is named here rather
  than implied — but it is no longer left to "cross-vendor review of the five
  texts and nothing else", which is what an earlier draft said while the
  predecessor study's own instrument for it sat unported;
- **that arm B is a paraphrase and not a semantic edit**, and that arm E's
  references are derivable by a competent reader. The literal census and the
  inclusivity-adjacency invariant bound the first syntactically; C10 bounds the
  second by one independent reader's re-derivation, which is evidence and not
  proof — a single clean-room author who derives (40, 70) shows the text
  *can* be read that way, not that it will be;
- that the retained slots are ALL the invocations that occurred — an off-ledger
  call leaves no slot;
- that `CALL.json`'s self-reported fields describe the process that ran; only
  the model, the working directory and the pre-prompt context are independently
  corroborated;
- the CLI's sampling configuration, recorded as a version and a binary digest
  and not controlled;
- **that the operator did not read a `completion.txt` by eye during the
  batch** — the artifacts make it possible, the design forbids computing rates
  rather than reading files, and no mechanism here can close it. In this study
  that residual is larger than in 011, because the operator holds a *prediction*
  and the batch is interleaved: a mid-batch glance at arm E would be a glance at
  the answer. Nothing prevents it; the ledger, the fixed N, the fixed arms and
  the registered rule are what bound what such a glance could change;
- **the in-process route, and its interaction with the interleaved schedule
  and the shortfall path.** Study 011 §2.4 stated the ceiling plainly and this
  study restores it, with the interaction named rather than left for a reader
  to assemble from three separate bullets. The registered scoring command is
  the only *publisher*, and what arms the driver's guard is `RESULTS.json`
  existing — but **nothing prevents a library caller importing the scorer and
  computing an arm's rate in process, publishing nothing and leaving the marker
  unarmed**. Here the operator holds a directional prediction, the schedule is
  interleaved so every arm exists from round 1, and §2.8 permits a shortfall
  declaration at any round. So an operator could in principle read arm E's
  coverage at round 10 and stop the batch at a favourable round. **Nothing here
  prevents it.** What bounds it: the fixed N, the fixed arm set, the
  append-only ledger, the registered rule that no rate is recomputed on a
  different population, `SHORTFALL.json`'s recorded wall clock of the last
  completed slot (§2.8) — and the fact that a shortfall below R = 11 produces
  no verdict at all (§2.8's floor), so the favourable early stop this route
  would buy is, for the first ten rounds, worth nothing;
- that a declared shortfall was involuntary.

**Not prevented:**

- **The perturbations were authored by the team that published the
  prediction [D-9].** This is the design's structural conflict and it is stated here
  rather than in a footnote. Someone who expects E to collapse can write an E
  that collapses for reasons other than denaming — a clumsy sentence, an
  ambiguous reference, an accidental semantic change. **Five** things bound it
  and none removes it: every arm artifact is **registered by digest before any
  call**, so the texts cannot be adjusted once a rate exists; the **mirror is
  the arbiter** and C8 binds every arm's mirror to A's, so an accidental
  semantic change is a refusal rather than a result; **C10's clean-room second
  mirrors** re-derive each arm's semantics from that arm's bytes alone, and an
  arm E whose reader cannot derive (40, 70) is re-authored before the freeze
  rather than run; the five texts get **cross-vendor adversarial review before
  the freeze**, whose findings and dispositions are published with this study;
  and **that review is bound to the frozen bytes** — `PREREG-REVIEW.md` records
  the sha256 of each of the five arm texts per round, and
  `harness/integrity.py` refuses unless each frozen `arms/<X>/POLICY.md` digest
  equals the digest the final review round recorded, so "the texts that were
  reviewed are the texts that ran" is a checked relation rather than a
  sequencing convention. §9 repeats it as a bound.
- **Contamination through the public repository.** `POLICY.md`, `FAMILY.json`,
  `PROMPT.txt` and Study 010's and 011's records have been public in this
  repository since 2026-08-06. The transcript whitelist mechanically excludes
  tool use, so no run can *retrieve* the repository during authoring; what
  cannot be excluded is that a model snapshot has seen this material. Arm D is
  the one arm that puts a partial probe on it — §5.3 (ii) registers what a
  D-old-edge-HIGH outcome would mean — and a partial probe is all it is.
- **Prior-context leakage that reproduces the golden capture after
  normalization.** The allowlist matches normalized digests, not raw bytes, so
  it cannot refuse a leak that stays inside the normalization equivalence class.
- **A credential copy surviving a `SIGKILL` or a power loss.** The residual is
  one file under the operator's own scratch parent, and the remedy is manual.
- **Per-run isolation limits.** Fresh `HOME` and `CODEX_HOME` close the paths
  Study 010 found empirically. They do not close provider-side state: if the
  pinned CLI's backend carries cross-session memory keyed to the credential, the
  125 runs are not independent in the way this study assumes. S6 is the one
  observable that would hint at it. **The interleaved schedule makes this
  sharper, not weaker**: arms alternate call by call, so provider-side state
  carried across calls is carried across arms, and a contrast between arms is
  the one thing such a state could not manufacture out of nothing — but it could
  blur one, and this study cannot measure that.
- **What `/tmp` still exposes.** The pinned CLI's sandbox is writable at
  `[workdir, /tmp, $TMPDIR]`; each run gets its own workdir and its own `TMPDIR`
  inside it, and the recommended scratch parent is outside `/tmp`. A run that
  used a tool at all is refused by the whitelist and leaves the denominator, so
  the rates are conditional on the author having happened not to use one.
- **Five texts, one prompt template, one model, one policy family, one day.**
  Every rate and every verdict is conditional on all of them.

## 8. Out of scope, and the publication commitment

**Out of scope:** other models and other vendors (no second vendor credential
exists in this environment); prompt perturbations — the prompt header is held
byte-identical across arms on purpose, and the "withhold the borderline
instruction" arm Study 011's census recommended is a **different study**;
sampling-parameter sweeps (the CLI exposes none); more than one instance of any
perturbation type; real operational records; any evaluator or runtime behaviour
(jpack never runs, no pack is evaluated, no disposition is produced); any draw,
beacon or transparency log; validation of Study 011 §5's tier mapping; and
everything Study 011 §8, Study 010 §10 and Study 009 §11 excluded. No
conformance claim of any kind is made, here or anywhere in this repository.

Two silent drops from Study 011 are named rather than left silent:

- **Study 011 §5's per-row composition rule is not ported.** That rule —
  `row_review_tier()`: a row matching several classes takes the strictest of
  their tiers, a row matching none takes FULL — is a function on *rows*, and no
  row is scored in this study. The per-class tiers appear here as **S9** only
  because 011 registered them. This is a different thing from the exclusion
  above: "validation of 011's tier mapping" is out of scope, *and* the row rule
  is not carried at all.
- **The S-numbers diverge from 011's**, and §4.6 states the mapping.

**Publication commitment.** Everything is published regardless of outcome, and
in this study that commitment has a named edge case, so it is stated as a rule
and not as a sentiment:

> **If arm E maintains coverage — HIGH on three or more of the four narrow
> numeric classes, §5.3 (i) — `R1` is published as WRONG, with the same
> prominence as the claim: in `ANALYSIS.md`'s first paragraph, in this study's
> README, in the venue and at the URL `CLAIM.md` records, and as a correction
> banner at the head of
> `studies/011-authorship-coverage-rates/DIVERSITY.md`.** No re-cutting of §5's
> thresholds, no "the effect was smaller than expected", no relegation to a
> limitations section.

**What is retracted is R1 and nothing else.** The census's own committed
sentence — "boundary placement follows the numbers the policy names, not an
independent search for edges" — is a description of Study 011's own corpus,
it is true of those 784 records whatever arm E does, and it stands. The
correction banner says exactly that: the descriptive finding stands, the causal
extension R1 does not. Retracting a description that is true would be as
dishonest as keeping a causal claim that is false.

Beyond that:

- all 125 raw slot directories across the five arms, **including every invalid
  one**, with every byte the run left in them and nothing removed, in one of
  Study 011 §8's four registered slot shapes; beside them the ledger
  `BATCH.json` and `SHORTFALL.json` if one is declared. Nothing in the tree is
  `.gitignore`d;
- the per-run admission verdict, refusal code, counts and class classification
  the scorer derives, for **every** slot, in `RESULTS.json`'s `runs` array;
- the compiled record trees for the valid runs whose completion held a parseable
  JSON array, emitted outside the slot tree;
- every recapture attempt's captures and the C7 negative control's retained
  files;
- `RESULTS.json`, `RATES.md` and `CENSUS.md`, written by the registered scoring
  command, with every rate's integers and bounds and every census count;
- `ANALYSIS.md` leading with the five arms' rates, the five `rho_X`, and the §5
  verdict table — a class covered in 1 run of 25 is published as 1/25 with its
  interval, in the headline;
- **the five arm artifacts themselves**, as committed before the batch, so any
  reader can judge whether the perturbations are what this file says they are;
- **`CLAIM.md`** — the verbatim published wording of R1, its venue, its URL and
  its retrieval date — committed and pinned before the freeze, so the
  retraction target is frozen with everything else;
- **`MIRROR-AGREEMENT.md`** — C10's five clean-room mirrors, the isolation rule
  each builder ran under, each builder's own report of what it consulted, and
  the per-arm 260-cell agreement table, following Study 011's format;
- `DEVIATIONS.md` for every departure from this file, written as it happens;
- **`PREREG-REVIEW.md`** — the complete pre-freeze review record, following
  Study 011's per-round, per-finding disposition format, and **carrying, per
  round, the sha256 of each of the five arm texts as that round reviewed
  them**. `harness/integrity.py` refuses unless each frozen
  `arms/<X>/POLICY.md` digest equals the digest recorded in the final review
  round, so a clause of arm E cannot change between the last review and the
  freeze with Appendix A updated to match — the registered-illustration check
  would pass either way, because both would have moved together, and this is
  the binding that catches it;
- the pre-freeze cross-vendor adversarial review of this file **and of the five
  arm texts**, and the post-run cross-vendor review, both with per-finding
  dispositions, both recorded in `PREREG-REVIEW.md`.

No slot is deleted. No rate or verdict is recomputed on a different population
after the fact. If the study is abandoned before the batch — pin drift, failed
recapture, an arm that cannot be made to pass C8 — that is published too, in
`DEVIATIONS.md`, with the reason.

## 9. Bounds

Twenty-five samples per arm, five arms, one prompt template, one model, one CLI
build, one policy family of six classes, one machine, one day. At `V_X` = 25 a
perfect arm is bounded below at 0.8628 and a half-covered class carries ±0.205,
so this study separates "reliably covered" from "essentially never covered" and
resolves nothing between — §5.4 says exactly what that costs.

**The smallest real effect this design cannot see, stated plainly: any
anchoring effect that leaves coverage above roughly one run in five.** A drop
from 1.00 to 0.30 reads MID 99% of the time; a drop to 0.10 reads LOW only 54%
of the time; only a fall below about 0.06 is reliably called. A partial
anchoring effect — the outcome most designs of this kind actually find — is
invisible here and is published as INDETERMINATE, which is what INDETERMINATE
means in this file.

**The baseline is not jointly comfortable.** At a true per-class coverage of
0.95, inside Study 011's own published interval, arm A reads HIGH on all six
classes only 44.2% of the time. So roughly two runs of this study in five would
find at least one falsifier-relevant class with no contrast verdict available,
from sampling alone and with nothing wrong. That is a bound on what this
design can return, not a prediction about the model, and §2.1 registers that
such a class is reported as an unresolved baseline rather than as drift.

**Each arm is one instance of its perturbation.** One paraphrase, one
permutation, one rename, one denaming. A TRACKING verdict on arm B is evidence
about that paraphrase; it is not a measurement of paraphrase-robustness, and
nothing here supports the plural. Arm D in particular is one *pair* of
thresholds, (45, 72), whose roundness differs from (40, 70)'s — §2.4 and
[D-18] state that confound and §5.3 (ii) registers the outcome it would
produce.

**The perturbations were authored by the team that predicted the outcome.**
Registration before any call, the mirror as arbiter with C8's mechanical
equality across arms, C10's clean-room re-derivation of each arm's semantics
from that arm's bytes alone, cross-vendor review of the five texts before the
freeze, and the digest binding between that review record and the frozen bytes
are the mitigations. They bound the risk; they do not remove it, and a reader
who discounts this study for that reason is applying the right standard.

**Arm E denames literals, it does not remove numeric information.** Its
threshold values are recoverable by arithmetic from words, because a policy that
did not determine them would be a different policy and the contrast would be
confounded. What E measures is the cost of *indirection*, not of *absence*.

**Nothing here measures defect detection.** No pack is evaluated, no mutation is
applied, no evaluator runs, no unresolved/no-match/conflict outcome is observed.
Coverage means a correctly-labelled record fell inside a registered predicate
under the correct policy. Study 011's census already recorded that "low probe
diversity costs detection power" is a plausible mechanism and a demonstrated
nothing, and this study does not change that.

**The mirror is the reference semantics, not ground truth.** A record is
"correctly labelled" here when its recorded outcome agrees with the arm's
mirror, and the mirror implements the same policy the prompt inlines — so label
accuracy measures how reliably the model applies a policy it was just handed,
not any independent validation. In arm E that circularity is *smaller* than
elsewhere, because the mirror carries the literals and the prompt does not; that
is worth noticing and is not worth much.

**One policy family, one model, one vendor.** The rates and the verdicts are a
property of the pinned tuple in §2.2 and expire with it. A new CLI build, a new
model snapshot, or a different policy shape requires a new study, not an
extrapolation. Nothing here establishes that any other model, or a human clerk,
anchors the same way.

Byte-lineage, not truth, unchanged.

## 10. Register of pre-freeze review decisions

Every genuinely open parameter, its proposal, and its alternative. The
pre-freeze review settles each one; the settled values are written into this
file before it is frozen, and after that this section is history.

**The review record is bound to the bytes it reviewed.** `PREREG-REVIEW.md`
follows Study 011's per-round, per-finding disposition format and records, per
round, **the sha256 of each of the five arm texts as that round reviewed
them**. `harness/integrity.py` refuses unless each frozen
`arms/<X>/POLICY.md` digest equals the digest the final round recorded. The
sequencing is unchanged and is still right — the review settles D-3, D-4, D-5,
D-14 through D-18; then the port fills the digests; then the freeze — but the
sequencing is no longer the only thing holding it together.

**Decisions marked with a round in the last column were opened by the round-1
review**, not by the drafters, and each records the option the maintainer took
and the option not taken.

| # | decision | proposal | alternative, and what turns on it | opened |
| --- | --- | --- | --- | --- |
| **D-1** | N per arm (§2.8, §5.4) | **25** | 30 (P(HIGH \| p=0.95) rises 0.8729 → 0.9392 marginally, and **P(arm A HIGH on all six) rises 0.4424 → 0.6865** jointly, +25 calls) or 20 (marginal falls to 0.7358, joint to 0.1587, −25 calls). Keep a multiple of 5 for §2.8's position balance | draft |
| **D-2** | The §5.1 level cuts | **`L ≥ 0.70` HIGH, `U ≤ 0.30` LOW** | Study 011's tier cuts 0.80/0.40. At N = 25 the 0.80 cut needs a perfect arm, so a single stray miss in a control arm reads INDETERMINATE. Interacts with D-1 | draft |
| **D-3** | Arm E's exact reference wording (§2.5, §4.5 X6, Appendix A) | the Appendix A text **as rewritten in round 1**: one denominator, no pronoun, §2.3's own threshold names — "The **review threshold** is seven tenths of that full range; the **personal-data threshold** is four tenths of that same full range." | any wording that keeps the clause-body digit census empty and the values exactly derivable. The round-1 draft's wording is **not** an option: its pronoun admitted 28 (two fifths of the review threshold), it called `T_low` the "clearance threshold" against §2.3's own key, and its two denominators made one derivation harder than the other. X6 registers the misderivation audit under either wording | draft; rewritten round 1 |
| **D-4** | Arm B's exact paraphrase (Appendix A) | the Appendix A draft, **plus the clause-by-clause A ↔ B substitution table** the review adjudicates row by row | any paraphrase preserving the clause-body digit census, the clause order, the semantics, **and §2.6's inclusivity-adjacency pattern** — the last is new in round 1, because the digit census cannot express the boundary-inclusivity phrasing that 011's census calls the most anchoring-relevant feature of the text | draft; invariant added round 1 |
| **D-5** | Arm C's permutation and label handling (§2.6) | **(P2, P1, P4, P5, P3)**, labels travel with their bodies. It is the **unique** permutation that is a derangement, resolves every explicit label reference backward, and resolves every three-part "absent …" precondition backward | (a) **(P1, P2, P4, P5, P3)** — resolves *every* reference backward including P2's own two-part opener, which no derangement can, at the cost of leaving P1 and P2 in place (3 of 5 clauses move); (b) renumbering labels to presentation order, which would add a second perturbation. The round-1 draft's (P2, P4, P1, P5, P3) is **not** an option: P4 at position 2 opens with "absent a sanctions hit or an embargoed registration" while P1 does not appear until position 3 | draft; replaced round 1 |
| **D-6** | Arm D's C2 pack-side clause (§6 C2) | replace with the C8 landmark-grid check and say so | construct a threshold-shifted pack `C_D` solely to keep the clause, adding an artifact no run evaluates | draft |
| **D-7** | Arm ordering within the batch (§2.8) | **round-robin, cyclic rotation by round** | fixed within-round order (simpler; confounds arm with within-round position) or blocked by arm (confounds arm with time-of-day drift, and is why round-robin is proposed) | draft |
| **D-8** | Golden recapture and C7, once or per arm (§3.2, §6 C7) | **once for the whole batch**, because both use the arm-independent probe prompt and the pre-prompt context does not depend on the prompt | per arm, which costs 10 extra probe calls and buys nothing this file can name | draft |
| **D-9** | Who authors the arm texts (§7, §9) | the study team, with **C10's clean-room re-derivation**, cross-vendor adversarial review of the five texts before the freeze, and the review record bound to the frozen digests | cross-vendor *authorship* to a registered spec, which weakens the conflict in §9 and adds an uncontrolled authoring step of its own | draft; C10 and the digest binding added round 1 |
| **D-10** | The E decision patterns (§5.3 i) | **CONFIRMED iff COLLAPSE on ≥ 3 of the 4 narrow numeric classes; FALSIFIED iff HIGH on ≥ 3 of 4; every other pattern INDETERMINATE**, all-MID explicitly included | ≥ 2 of 4 (more easily decided in both directions) or all 4 (harder in both). The round-1 draft registered only the falsification half, which let a motivated analyst call 2 COLLAPSE + 2 MID a confirmation afterwards with nothing in this file to stop them | draft; confirmation half added round 1 |
| **D-11** | Which classes the collapse prediction covers (§2.3, §5.3) | **0, 1, 2, 5 only**; classes 3 and 4 predicted TRACKING everywhere | include class 3, which a diffuse author covers by accident across a 30-wide band (27-wide in arm D) and which would therefore flatter the prediction | draft |
| **D-12** | S10 old-edge cross-scoring status (§4.6, §5.3 ii) | **registered secondary with its own registered predicted pattern** | promote to primary (it is the sharper measure of the rename claim) or drop it (it is the only registered probe on contamination) | draft |
| **D-13** | Unequal valid counts across arms (§2.8) | **no truncation**; each arm uses its own `V_X`, and a caution is stated if two arms differ by more than 2 | truncate every arm to the common minimum for the contrasts, at the cost of discarding admitted runs | draft |
| **D-14** | How arm D gets a mirror (§2.2, §2.6, §2.10, §6 C1, C8 clause 6) | **(b) one 010-locked module parameterized by (`T_low`, `T_high`) read from the arm's registered `ARM.json`.** One mirror artifact, one destination digest, five arms; D's behaviour is keyed to an artifact that is already pinned before any call, and the §2.2 row becomes an enumerated-change port bound to 010's lock on the source side | **(a) a fifth registered per-arm file `arms/<X>/MIRROR.py`**, five artifacts pinned in §2.6, §2.10 and C8 clause 1, with D's derived from 010's locked mirror by substituting exactly two integer literals and the diff published in `harness/PORTS.md`. (a) keeps each arm's mirror byte-visible in its own directory; (b) keeps the count of unreviewed artifacts at one. Under either, C8 clause 6 runs against the arm's actual mirror at its registered digest. **Round 1 found that neither was registered**: the draft ported the mirror byte-identically, which encodes 40/70 and cannot serve arm D, and pinned no per-arm mirror anywhere | round 1 |
| **D-15** | Where the scale sentence goes (§2.1, §2.5, §2.6, Appendix A) | **(a) the identical sentence "The office's risk scale runs from zero to one hundred." in all five arms' conventions paragraphs**, as the registered `CONVENTIONS_DELTA`, pinned by its own sha256. This relaxes §2.1's arm-A byte-equality to *011's pinned text plus exactly that published delta* — acceptable because §2.1 already declares 011's runs historical and every contrast within-batch, so the prompt digest was load-bearing only for the §4.7 drift report, which gates nothing | (b) **a sixth arm A′ = A + the scale sentence** as an explicit scale-disclosure control, +25 calls, which measures the confound instead of eliminating it; (c) **keep it in arm E only** and state in §5.3 (i), §8 and §9 that arm E carries two differences from baseline and its falsifier is correspondingly weaker. Round 1's finding: the scale sentence is *new semantic information* — neither 011's prompt header nor 010's conventions bounds `riskScore` anywhere, 011's corpus contains scores authored with no stated scale, and no mirror can catch a domain hint because the mirror encodes no domain | round 1 |
| **D-16** | The preamble's study reference (§2.5, §2.6, §5.3 i) | **keep the preamble byte-identical across all five arms**, inherited from 010, and register the recall channel it leaves open: §5.3 (i)'s third reading, with X3 dispersion as the registered discriminator | **replace "Study 010" with a digit-free, name-free equivalent in all five arms**, which removes arm E's one textual hook back to a public policy stating 40 and 70 — and separates §5.3 (i)'s readings 2 and 3, which this design otherwise cannot — at the cost of a second registered delta from 010's locked text, on top of D-15's | round 1 |
| **D-17** | The contrast rule (§5.2) | **the level-gated rule, plus COLLAPSE-DISJOINT (`U_X < L_A`) reported beside it and never substituted for it.** Both computable from the same integers; neither needs a distribution for a difference of proportions, so the estimation-first posture is preserved | **the level-gated rule alone**, accepting that a class where E reads LOW and A reads MID is published as INDETERMINATE despite widely disjoint intervals in the predicted direction. §5.4's joint arithmetic makes that the *likely* shape of a partial baseline, not a corner case. Round 1's finding: the contrast rule is the study's second-most consequential registered choice after the level cuts, and the draft registered thirteen decisions without it | round 1 |
| **D-18** | Arm D's threshold pair (§2.4, §5.3 ii, §9) | **(45, 72)** — no single additive shift explains it, which is the confound this pair was chosen to exclude | **(50, 80)** — salience-matched (both decade-round, as 40 and 70 are) and width-preserving (class 3 stays 30 wide, where (45, 72) narrows it to 27), at the cost of being exactly a +10 additive shift of (40, 70). The two candidates trade one confound against the other and the review picks which one this study would rather not be able to rule out. Under either, §5.3 (ii)'s third outcome — new-keyed LOW *and* old-keyed LOW, published as a general degradation — stays registered | round 1 |

---

## Appendix A — the five policy texts (DRAFT)

**These are drafts.** The frozen artifacts are `arms/<X>/POLICY.md`, and their
digests in `harness/PINS.json` are authoritative. Registered as a check: a
harness test requires each arm's `POLICY.md` bytes to equal the text printed
below, so this appendix cannot drift from the artifact after the freeze — the
same registered-illustration discipline Study 011 applied to its own prose.
**That check alone is not enough**, because a clause and its illustration can
move together between the last review round and the freeze and still satisfy
it; what closes that is §8's and §10's binding of `PREREG-REVIEW.md`'s
per-round arm digests to the frozen bytes.

**The preamble, byte-identical in all five arms** (inherited from Study 010; its
references to packs and to Study 010 are historical and are kept fixed so that
each arm's variation is confined to the intervention — with the cost to arm E
registered in §2.5 and §5.3 (i) and the alternative in **[D-16]**):

```
# Vendor screening policy — the arbiter

Synthetic policy for Study 010. Every other artifact in this study is checked
against this text; a divergence between a pack and this text is a pack bug.
This is also the exact policy text the record author receives (inlined in the
registered prompt), so it is the whole of what the two sides share.
```

**The conventions paragraph, byte-identical in A, B, C and D.** It is 010's
conventions paragraph plus `CONVENTIONS_DELTA` **[D-15]** — the final
sentence, which is in **all five arms** so that arm E's threshold definitions
are one intervention and not two:

```
Risk scores are decimal strings and compare numerically. Registered
countries are two-letter uppercase codes in the ISO 3166-1 alpha-2 style;
the policy consults no registry — embargo-list membership is exact,
case-sensitive string comparison against KP, IR, and SY, and any other
two-letter code is a non-embargoed registration. The three outcomes —
clear, manual review, reject — are exhaustive over complete inputs (all
four facts present and well-formed, which is what the study's gates admit);
the policy takes no position on incomplete inputs, which no admitted
record can present. The office's risk scale runs from zero to one hundred.
```

`CONVENTIONS_DELTA` is exactly ` The office's risk scale runs from zero to one
hundred.` — **55 bytes**, one leading space, appended to the end of 010's final
sentence — and it is pinned by its own sha256 in `harness/PINS.json`. Arm A's
`POLICY.md` is therefore 1759 + 55 = **1814 bytes**.

**The assembly rule, registered so every digest below is reproducible from
these bytes**: an arm's `POLICY.md` is

```
PREAMBLE + "\n\n" + <that arm's clause-bullet block> + "\n\n"
         + <that arm's conventions block> + "\n"
```

where each block is the fenced code block printed under its heading in this
appendix, without its trailing newline, and arm E's conventions block is the
shared conventions block, a newline, and arm E's appended sentence. The
resulting five digests are recorded per review round in `PREREG-REVIEW.md`
(§8, §10) and are what `harness/integrity.py` binds the frozen artifacts to.

### A.1 Arm A — baseline (clause bodies, in order P1…P5)

Byte-identical to Study 010's. The whole file is 010's locked `policy/POLICY.md`
plus `CONVENTIONS_DELTA` **[D-15]**, and it must produce arm A's prompt under
§2.6's equation with `HEADER` derived from 011's pinned prompt bytes. Under
D-15's alternative (c) it is 010's locked file outright and arm A's prompt is
011's pinned digest.

```
- **P1.** A vendor with a sanctions hit is **rejected**, regardless of
  anything else.
- **P2.** Absent a sanctions hit, a vendor registered in an embargoed
  country — **KP, IR, or SY** — is **rejected**.
- **P3.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **70 or above** goes to **manual review**.
- **P4.** Absent a sanctions hit or an embargoed registration, a vendor that
  **handles personal data** and whose risk score is **40 or above but below
  70** goes to **manual review**.
- **P5.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **below 70** is **cleared**, unless P4 applies — that
  is, a vendor that does not handle personal data clears below 70, and a
  vendor that does handle personal data clears only below 40.
```

### A.2 Arm B — reworded [D-4]

Same literals, same order, paraphrased bodies.

```
- **P1.** If a vendor has a sanctions hit, the outcome is **reject**,
  whatever else the file shows.
- **P2.** With no sanctions hit, a vendor whose registration is in an
  embargoed country — **KP, IR, or SY** — is also **rejected**.
- **P3.** With neither a sanctions hit nor an embargoed registration, any
  vendor carrying a risk score of **70 or more** is sent to **manual
  review**.
- **P4.** With neither a sanctions hit nor an embargoed registration, a
  vendor that **handles personal data** and carries a risk score from **40
  up to but not including 70** is likewise sent to **manual review**.
- **P5.** With neither a sanctions hit nor an embargoed registration, a
  vendor scoring **below 70** is **cleared** except where P4 catches it: a
  vendor that handles no personal data clears anywhere below 70, while one
  that does handle personal data clears only below 40.
```

**Clause-body digit-run census** (§2.6's definition — clause-label tokens
masked, so P5's "unless P4 applies" contributes nothing): sorted,
`{40, 40, 70, 70, 70, 70}` — arm A's exactly, verified against both texts.

**The clause-by-clause A ↔ B substitution table [D-4]**, published so the
pre-freeze review adjudicates each substitution rather than reading five
paragraphs as a whole. The right-hand column is the §2.6 invariant the digit
census cannot express: each numeric bound with an explicit inclusivity word
immediately adjacent to its literal, on the same side, in the same clause.

| clause | arm A | arm B | inclusivity adjacency |
| --- | --- | --- | --- |
| P1 | "A vendor with a sanctions hit is **rejected**, regardless of anything else." | "If a vendor has a sanctions hit, the outcome is **reject**, whatever else the file shows." | no numeric bound |
| P2 | "Absent a sanctions hit, a vendor registered in an embargoed country … is **rejected**." | "With no sanctions hit, a vendor whose registration is in an embargoed country … is also **rejected**." | no numeric bound |
| P3 | "risk score is **70 or above**" | "carrying a risk score of **70 or more**" | inclusive-at-70, word *after* the literal, both arms |
| P4 lower | "**40 or above** but below 70" | "from **40** up to but not including 70" | inclusive-at-40, word after the literal in A ("or above"), before it in B ("from") — **the one asymmetry in the table, and the review's to adjudicate** |
| P4 upper | "40 or above but **below 70**" | "from 40 **up to but not including 70**" | exclusive-at-70, word before the literal, both arms |
| P5 outer | "risk score is **below 70**" | "vendor scoring **below 70**" | exclusive-at-70, word before the literal, both arms |
| P5 gloss (non-P) | "clears **below 70**" | "clears anywhere **below 70**" | exclusive-at-70, word before the literal, both arms |
| P5 gloss (P) | "clears only **below 40**" | "clears only **below 40**" | exclusive-at-40, word before the literal, byte-identical |

### A.3 Arm C — reordered [D-5]

Bodies byte-identical to arm A's; presentation order **(P2, P1, P4, P5, P3)**;
each label travels with its own body.

```
- **P2.** Absent a sanctions hit, a vendor registered in an embargoed
  country — **KP, IR, or SY** — is **rejected**.
- **P1.** A vendor with a sanctions hit is **rejected**, regardless of
  anything else.
- **P4.** Absent a sanctions hit or an embargoed registration, a vendor that
  **handles personal data** and whose risk score is **40 or above but below
  70** goes to **manual review**.
- **P5.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **below 70** is **cleared**, unless P4 applies — that
  is, a vendor that does not handle personal data clears below 70, and a
  vendor that does handle personal data clears only below 40.
- **P3.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **70 or above** goes to **manual review**.
```

**Derangement:** P1 1→2, P2 2→1, P3 3→5, P4 4→3, P5 5→4 — every clause moves.

**Reference resolution**, checked by re-deriving it from the parsed bodies:

| reference | in clause at position | resolved by clause at position | backward? |
| --- | --- | --- | --- |
| "unless P4 applies" | P5, position 4 | P4, position 3 | yes |
| "absent a sanctions hit **or an embargoed registration**" | P4 (3), P5 (4), P3 (5) | P1 (2) and P2 (1) | yes, all three |
| "Absent a sanctions hit" | P2, position 1 | P1, position 2 | **no — the one residual** |

**The residual is unavoidable and is registered rather than hidden.** Requiring
P2's own two-part opener to resolve backward forces P1 to position 1 and P2 to
position 2, which is not a derangement; the constraint set *derangement + every
reference backward* is empty over all 120 permutations, verified by exhaustive
enumeration and asserted by a harness test. Of the permutations that do resolve
every reference backward, the one that moves the most clauses is
(P1, P2, P4, P5, P3), which moves three of five — that is D-5's alternative
(a). §5.3 (iii) reads a C-collapse against this table and not against a
stronger claim.

### A.4 Arm D — renamed [D-18]

Arm A's bodies with σ applied: `T_low` 40 → 45, `T_high` 70 → 72.

```
- **P1.** A vendor with a sanctions hit is **rejected**, regardless of
  anything else.
- **P2.** Absent a sanctions hit, a vendor registered in an embargoed
  country — **KP, IR, or SY** — is **rejected**.
- **P3.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **72 or above** goes to **manual review**.
- **P4.** Absent a sanctions hit or an embargoed registration, a vendor that
  **handles personal data** and whose risk score is **45 or above but below
  72** goes to **manual review**.
- **P5.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **below 72** is **cleared**, unless P4 applies — that
  is, a vendor that does not handle personal data clears below 72, and a
  vendor that does handle personal data clears only below 45.
```

**Clause-body digit-run census** (clause-label tokens masked): sorted,
`{45, 45, 72, 72, 72, 72}` — arm A's `{40, 40, 70, 70, 70, 70}` under σ,
verified against both texts.

The six classes at (45, 72): 0 → exactly 72; 1 → [72, 73); 2 → P ∧ [45, 46);
3 → [45, 72), **a 27-wide band, not 30**; 4 → SY, unchanged; 5 → P ∧ [44, 45).
The width difference is D-18's second cost and §2.4 states it.

### A.5 Arm E — denamed [D-3]

The clause bodies carry **no numeric content**: their digit-run census under
§2.6's definition is **empty**. P1 and P2 are byte-identical to arm A's,
because they carry no numeric content in any arm. P5's body retains the
cross-reference "unless P4 applies" — as every arm's P5 does — and the `4` in
that token is masked by the census definition rather than pretended away.

```
- **P1.** A vendor with a sanctions hit is **rejected**, regardless of
  anything else.
- **P2.** Absent a sanctions hit, a vendor registered in an embargoed
  country — **KP, IR, or SY** — is **rejected**.
- **P3.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **at or above the review threshold** goes to **manual
  review**.
- **P4.** Absent a sanctions hit or an embargoed registration, a vendor that
  **handles personal data** and whose risk score is **at or above the
  personal-data threshold but below the review threshold** goes to **manual
  review**.
- **P5.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **below the review threshold** is **cleared**, unless
  P4 applies — that is, a vendor that does not handle personal data clears
  below the review threshold, and a vendor that does handle personal data
  clears only below the personal-data threshold.
```

Arm E's conventions paragraph is the shared conventions paragraph (010's, plus
`CONVENTIONS_DELTA`) with exactly this one sentence appended, and nothing else:

```
The **review threshold** is seven tenths of that full range; the
**personal-data threshold** is four tenths of that same full range.
```

**Why this wording and not the round-1 draft's [D-3].** Seven tenths of one
hundred is seventy; four tenths of one hundred is forty. One denominator
serves both, so neither derivation is harder than the other; there is no
pronoun, so no antecedent can be mistaken; and the names are §2.3's own keys —
`T_high` is the *review threshold* and `T_low` is the *personal-data
threshold*. The round-1 draft said "the **clearance threshold** is two fifths
of it", which carried three authored difficulties that were not the
intervention: "it" nearest-resolved to *the review threshold*, and two fifths
of seventy is **28** — a coherent wrong derivation that would have landed arm
E's records exactly where a collapse looks like one; "clearance threshold" is
the wrong name for `T_low`, and arm A's own P5 makes seventy a clearance
boundary for non-personal-data vendors, so the name pointed at the other
threshold; and the two denominators made one derivation strictly harder than
the other for no design reason. An independent author of arm E — the
counterfactual §7 and §9 invoke as the mitigation — would have fixed all three,
and none of them is denaming. §4.5's **X6** registers the plausible-
misderivation census (including 28) so that a comprehension failure is
diagnosed rather than assumed away.

So arm E's semantics, mirror and family are arm A's exactly. **The digit-runs
in this file**, exhaustively, are: the clause labels `P1`–`P5`; the `4` in P5's
`unless P4 applies`; `3166`, `1` and `2` in the token `ISO 3166-1 alpha-2` in
the inherited conventions paragraph; and `010` in the inherited preamble's
"Synthetic policy for Study 010". **None equals `40` or `70`**, and the
clause-body census under §2.6's definition is empty — which is what §6 C8
clause 5 checks. §2.5 registers what the surviving `010` costs, §5.3 (i)
registers the reading it makes available, and **[D-16]** is the change that
would remove it.
