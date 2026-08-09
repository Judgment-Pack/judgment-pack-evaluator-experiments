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

**This file specifies the harness rather than describing it: it was written
before the harness existed.** Study 012 is built by porting Study 011's harness
by digest after this preregistration is reviewed. Every port table below carried
`(port time)` where a digest goes; those cells are filled once, when the port is
taken, and committed before the freeze — the port is taken and every cell is
filled (§2.2 [D-20] step 2). A `(port time)` cell surviving into the frozen file
is a defect, and `harness/integrity.py` refuses on it.

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
`PROTOCOL-LOCK.json` is the ultimate authority for **the mirror module, arm
A's family, arm A's policy source, and the prompt bytes 011 pinned** — and,
stated exactly because an earlier draft overstated it, **not** for the
compiler, the transcript checker or the wrapper: Study 011 *adapted* all
three, so the bytes this study ports are **011's**, and 010's lock is their
ancestor rather than their authority (§2.2's authority column and §6 C1's
tier 3 are where that distinction is enforced). Tracker:
evaluator-experiments **issue #45**, whose body registers this mandate.

## 1. The question

Study 011 measured that a blinded authoring call reaches all six registered
boundary classes in 49 of 49 valid runs. Its post-hoc census measured *how*,
and the answer was uncomfortable: 410 of 784 records (52.3%) sit on one of the
family's three edges or within 0.01 of one; **three** of the six classes (0, 2
and 5) rest on two distinct probes each, and **four** of six (0, 1, 2 and 3)
contain a probe that appears in every one of the 49 runs; the whole band
(23.75, 39) below the **unstated** 39 edge is empty, while the two thresholds
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
| **A** baseline | none — Study 011's policy text plus the two registered deltas, `CONVENTIONS_DELTA` [D-15] and `PREAMBLE_DELTA` [D-16], both of which are in **all five** arms | 40, 70 | the registered mirror at (40, 70); 010's locked family |
| **B** reworded | the five clause bodies paraphrased; every literal, the clause order and the inclusivity-adjacency pattern unchanged | 40, 70 | A's |
| **C** reordered | the five clause bodies byte-identical to A's, presented in a registered permutation | 40, 70 | A's |
| **D** renamed | the threshold literals moved | **45, 72** | the registered mirror at (45, 72); the σ-image of A's family (§2.4) |
| **E** denamed | no numeric content in any clause body; the same values stated only by reference | 40, 70, by reference | A's |

**One mirror module serves all five arms**, parameterized by the arm's
registered `(T_low, T_high)` **[D-14]**; §2.2 and §2.6 register it and C8
clause 6 checks that its verdicts agree with arm A's on every landmark.

### 2.1 Why A is re-run rather than read off Study 011

Study 011's 49 valid runs are **historical reference, not this study's
baseline**. They were produced on 2026-08-07 — the same day this file was
drafted, a few hours earlier — against a model snapshot whose drift since is
uncontrolled and unmeasurable from here. **The reason is not elapsed time and
this file no longer says it is**: a provider-side snapshot can move between two
calls a minute apart, nothing in this repository observes it, and a contrast
between an arm run in this batch and a batch run at any earlier moment
confounds the perturbation with whatever moved in between. The interval being
short makes the confound smaller than it would otherwise be; it does not make
it measurable, and an unmeasurable confound is not one this study is willing to
put under a registered contrast.

So arm A is Study 011's registered call, re-run in the same batch as B–E, and
every registered contrast in §5 is **within this batch**.

**Arm A's prompt is 011's pinned text plus exactly the two registered deltas,
and nothing else.** Both deltas are in **all five arms**, which is the whole
point of each: `CONVENTIONS_DELTA` adds the scale sentence to every arm so
that arm E's threshold definitions do not smuggle a second intervention into
arm E only (§2.5, **[D-15]**), and `PREAMBLE_DELTA` replaces the preamble's
study name in every arm so that arm E is *de-referenced as well as denamed*
(§2.5, **[D-16]**, adopted in round 2). The consequence for this section is
that arm A's prompt no longer hashes to Study 011's pinned prompt digest
`a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2`. What is
required in code instead, and is a stronger relation than the digest was:

```
arms/A/POLICY.md == 010's locked policy/POLICY.md bytes
                   with PREAMBLE_DELTA applied at its single occurrence
                   and CONVENTIONS_DELTA appended at the registered position
arms/A/PROMPT.txt == HEADER + (arms/A/POLICY.md minus its final LF)
```

where both deltas are published verbatim in §2.6 and Appendix A; the
**assembled preamble** and `CONVENTIONS_DELTA` are each pinned by their own
sha256 in `harness/PINS.json`; and `HEADER` is derived from 011's pinned prompt
bytes (§2.6). So the byte relation to 011's cell is still arithmetic on bytes
and not an assurance; it is now an *equation with two published, pinned
residues* rather than an equality. 011's prompt digest is still pinned and
still verified — as the source of `HEADER`, which is the 948 bytes of 011's
prompt that precede the policy text.

Registered as a cost rather than as a detail: **two registered deltas is one
more than an earlier draft carried**, and D-16's alternative — keeping 010's
preamble byte-identical — is what the second one buys out of. §2.5 states what
it buys and §5.3 (i) states what it does not.

The comparison of arm A against Study 011's published rates is reported in
`ANALYSIS.md` as **drift information, with no verdict attached** (§4.7). It is
not a contrast, it gates nothing, and no registered decision reads it — which
is also why the conventions delta costs this study nothing that gates anything:
the digest pin was load-bearing only for that drift report.

One consequence is registered here rather than discovered later, and it is
registered as *weaker* than an earlier draft claimed. **An arm-A class below
HIGH is at least as likely to be sampling noise at N = 30 as drift**: §5.4
records that at a true per-class p of 0.95 — inside Study 011's own published
interval, whose lower bound is 0.9275 — the probability that arm A reads HIGH
on **all six** classes is **0.6865** under the registered conditional-
independence scenario, and on all four narrow numeric classes **0.7782** (at
the N = 25 the round-2 review re-adjudicated away from, the same figures were
0.4424 and 0.5806). **Both assume an independence across classes that §2.3's
own nesting makes unavailable** (round 10, finding 4): class 0 nests in class 1
and class 2 in class 3, so the six classes are four indicators, a conjunction
gets *easier* rather than harder, and under the containment-respecting companion
§5.4 publishes beside those figures the all-six probability is **0.7782** — the
same digits as the independence all-four-narrow cell, a different quantity — and
the all-four-narrow probability **0.8285**, with 0.5806 and 0.6651 at N = 25.
The consequence below is stated on the *smaller* of each pair, so it is not
weakened by the correction. So a single arm-A class below HIGH is **reported as an
unresolved baseline for that class, not as a drift finding**, every §5
contrast involving that class is INDETERMINATE by §5.2's own rule, and the
drift report of §4.7 stands beside it without a verdict.

**The drift classification is numeric or it does not exist [D-19].** An earlier
draft said a "pattern that §5.4's operating characteristics make implausible —
several classes at once, or a class far below the cut" is reported as drift,
which is an unregistered rule wearing a registered one's clothes: "several" and
"far below" are the analyst's to set after seeing the data. The registered rule
is now a count and a bound, both fixed here:

> **Arm A is reported as DRIFT-SUSPECTED iff arm A reads below HIGH on four or
> more of its six classes, or reads LOW on any one of them.** Anything else —
> including three classes below HIGH — is reported as **an unresolved baseline
> on those classes and nothing more**. No other pattern is called drift, and no
> quantity outside this rule may be cited as evidence of drift.

Under the scenario above, P(four or more of six below HIGH) is **0.0002** at
N = 30 and **0.0032** at N = 25 under the independence layer, and **0.0041** and
**0.0197** under the containment-respecting companion (round 10, finding 4) —
the rule counts *classes* and a single group below HIGH puts two classes below
HIGH at once, which is why this rate multiplies by more than twenty where the
gate merely falls by a tenth. **The larger figure is the one to quote:** the
rule fires by sampling alone about **four times in a thousand** runs of this
study at the registered N, and about two in a hundred at the alternative. Even
when it fires it is
reported as **a finding about the contemporaneous baseline, not as a
measurement of drift**, which this design cannot make: there is no second
snapshot to compare against.

### 2.2 What is constant across the arms, and where it comes from

Everything except the arm's policy text. The chain of authority runs three
levels deep and is verified in code before any call and before any scoring
(§6 C1):

```
Study 012's harness/PORTS.md      (pinned in harness/PINS.json at port time)
    -> Study 011's harness/PINS.json   e0007697…   (pinned here)
       Study 011's harness/PORTS.md    783cc9c3…   (pinned here)
        -> Study 010's PROTOCOL-LOCK.json          (pinned in 011)
```

**Every link in that chain is a pinned digest, including the two ends.** An
earlier draft said 011's `PINS.json` and `PORTS.md` were "both pinned" while
specifying a digest only for the former, and left this study's own `PORTS.md`
unpinned — so the file that records what every enumerated change *was* could
be rewritten after the review with nothing refusing. The registered digests:

| chain artifact | sha256 | pinned where |
| --- | --- | --- |
| Study 011 `harness/PINS.json` | `e0007697` `2377a640236c95496feb083e49730f22c80d82b896d1d1d77fc6dc79` | `harness/PINS.json`, verified by C1 before every batch and every scoring |
| Study 011 `harness/PORTS.md` | `783cc9c3` `2f8b2c77ba3ab91cbe4caaa91e9d9b035dd539659b77ed423f689ea3` | same |
| Study 010 `PROTOCOL-LOCK.json` | `4966aa82` `1325417f2cbce24a1a6ce7a10a45eefcbe2ec8fc16a4b2f1113543b1` — the digest **011** pins for it, not one this study chooses | 011's `PINS.json`, verified transitively |
| Study 012 `harness/PORTS.md` | `e00b4476bc383d541068ad4e671975f6ad090676762a8aaf55676361ff5b0f08` | `harness/PINS.json`, and in the final review round's tree manifest (§2.10) |

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
(`e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f`) with the
registered `PREAMBLE_DELTA` and `CONVENTIONS_DELTA` of §2.1 and §2.6, and it
appears in the enumerated-change table below with **010's lock directly** as
its source-side authority. It does not travel "through 011's `PORTS.md`":
Study 011 holds no separate copy of the policy text — it inlines it in the
prompt — so there is no 011-side blob for that row to answer to, and an
earlier draft's "through 011 `PORTS`" wording named a provenance step that
does not exist.
`arms/A/PROMPT.txt` is likewise derived rather than copied: `HEADER` is taken
from 011's pinned prompt bytes
(`a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2`, itself
010-locked as `transcription/PROMPT.txt`) and the prompt equation of §2.6
rebuilds it. Both digests remain pinned and verified in the roles just named.

| ported with enumerated changes | source sha256 | source authority | destination sha256 | registered scope of the change |
| --- | --- | --- | --- | --- |
| `harness/policy_mirror.py` | `276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba` | 010's lock | `5c631b7bd062e21564bec0edecdb558768638adff8ffcb33132c5ec32ec0bc5b` | **[D-14]** the two threshold comparisons read `T_low` and `T_high` from the arm's `ARM.json` instead of the literals 40 and 70; the module is otherwise line-for-line 010's, and the diff is published in `harness/PORTS.md`. **One module serves all five arms** — see below |
| `arms/A/POLICY.md` | `e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f` | **010's lock directly** — 011 holds no separate policy copy, so there is no 011-side blob for this row | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` | exactly two registered deltas and nothing else: `PREAMBLE_DELTA` applied at its single occurrence and `CONVENTIONS_DELTA` appended at the registered position (§2.1, §2.6, Appendix A). Both are published verbatim; the assembled preamble and the conventions delta are each pinned by their own sha256 |
| `harness/records_compile.py` | `6de92175b3f93d563b7e79c60a2e3fd641d96f40cc594fb8c3753c3655c90a1c` | **011's own bytes** (011 adapted it from 010's `e58edce3…`) | `6de92175b3f93d563b7e79c60a2e3fd641d96f40cc594fb8c3753c3655c90a1c` | none — byte-identical if the port takes it unchanged; the output-root parameter 011 added already suffices |
| `harness/transcript_check.py` | `0c9d7c798fc8738acb05dada3230251c9fba6109e15ed5b6b5ee8a4b2e708218` | **011's own bytes** (011 adapted it from 010's `42d977c4…`) | `64542bc5d6d8f6682a29dee870aa07feb5757db3941c48af581a974c2423a5b2` | the registered-prompt-terminal gate takes **the arm's** prompt bytes instead of one fixed prompt, and (round 5, finding 7) a completion that does not decode raises its own exception class so the scorer can name `completion-unreadable`; no other check logic changes |
| `transcription/authoring_call.sh` | `6e1239f3ea425669e88878dc2b4d3f6eb41ff9ffe859c76479c9bb8dea41a90e` | **011's own bytes** (011 adapted it from 010's `3b8909aa…`) | `d8877f3d78af54a7c43b8c53571b76ac4e0d540048f57ddcdaa7826f3c6b3fee` | §2.7 |
| `harness/integrity.py` | `7cecea4b0e86c0f7593d8fe9caaa3e4770aa1ec829b0cda574668449acae2a1c` | 011's commit only | `c092a1fe301c0aafe35d24ee8eab632045440aee9df5b763c003d07d1fdeae9d` | the three-level chain above; the per-arm artifact checks of §6 C8 and C9 |
| `harness/batch.py` | `fb513e9f30cc28dcb3748b502e679fea6ec9270d15b730334ac01936f0b1deb7` | 011's commit only | `a6c948951567caebdddb211161c89235ec08d113e63dec89c8a2e168908a7211` | §2.8's registered carryover-balanced call order and its global index; per-arm slot roots; the arm and schedule stamps in `CALL.json`; the chained ledger and per-slot manifests of §2.9 |
| `harness/score_rates.py` | `b8239532d1a796b593a602c55126f0a1a363ffce325c8804581727aef2f81984` | 011's commit only | `4f52035fbf9ff9451f49f9f173874f3d523f122f8e7e0eb9c623203760c0a81f` | per-arm scoring against that arm's mirror and family; the §5 level and contrast verdicts; the §4.5 census; the old-edge cross-scoring of §4.6 |
| `harness/census.py` (from 011's `analysis/diversity.py`) | `16bad4a911ef49b8cc03fcda4ecbfe15f813eba067799c9017e7ba39be5ebf68` | 011's commit only | `911eb25773923789e5ddeae20f0bfa68032f932ae9c62fd7e9a21ad8aa8b73ea` | promoted from a post-hoc script to a registered secondary: parameterized by the arm's edge set and family, distances bucketed as §4.5 registers, no clock and no randomness (unchanged) |

**The port happens before the final cross-vendor review, not after it
[D-20].** An earlier draft ordered the work review → port → freeze, which put
every `(port time)` cell — four inherited harness sources, this study's own
`PORTS.md`, and all twenty arm-artifact digests — outside the reach of every
review that ran. The registered order is now:

```
1. review rounds over the specification and the arm texts   (this file, Appendix A)
2. THE PORT: every harness file written, every arm artifact assembled,
   every (port time) cell filled, PORTS.md and PINS.json completed
3. THE FINAL cross-vendor review, over the complete post-port candidate tree
4. the freeze: the tree manifest of the final review round is recorded in
   PINS.json, the preregistration's own digest is filled, and the file is merged
```

so that the last review sees the bytes that run, including the ported code. The
cost is registered rather than hidden: the final round is a larger review than
a specification-only round, and if it finds anything that changes a byte, the
port and the review both repeat — §2.10 makes that a rule and not a preference.

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

**The two nestings are load-bearing, not a curiosity** (round 10, finding 4).
Adjacency imposes nothing — different records in one run can witness class 5 and
class 3 — but *containment* does: correctness is a property of the record
(§4.1), so a record witnessing class 0 in a run witnesses class 1 in that run
and carries the same correctness bit, and the two classes' coverage indicators
are ordered slot by slot. §5.4 registers what that costs its joint arithmetic
and publishes the corrected figures. The two pairs are `NESTED_CLASS_PAIRS` in
`harness/score_rates.py`, and `harness/tests/test_mirror.py` asserts over the
280-cell landmark grid at every arm's registered threshold pair that they are
**exactly** the ordered pairs of classes whose members are contained in one
another — a registered fact that until round 10 lived only in this sentence.

### 2.4 Arm D's threshold substitution, and how "semantics constant" is checked

Arm D moves `T_low` 40 → 45 and `T_high` 70 → 72, and everything keyed to them
moves with them: the policy text's two literals, the mirror's two comparisons,
and the five family edges of §2.3. The moves are deliberately **unequal** (+5
and +2) so that no single **additive shift** explains the arm, and deliberately
still ordered `T_low` < `T_low`+1 < `T_high` so the six classes stay
disjointness-compatible and non-empty.

**"Additive shift" is the exact word and an earlier draft used the wrong one.**
It said *affine*, which is false: unequal moves exclude a translation `x + c`,
they do not exclude an affine map. `0.9x + 9` sends 40 → 45 and 70 → 72
exactly, so an author who rescaled rather than translated would produce arm D's
pair. Nothing in this study excludes that, the claim is narrowed to what is
true — **(45, 72) is not a translation of (40, 70)** — and the wider claim is
withdrawn.

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
                             T_low  - 1 - 0.01,
                             T_low  - 1,     T_low  - 0.01,  T_low,
                             T_low  + 0.01,  T_low  + 1 - 0.01,  T_low  + 1,
                             T_high - 0.01,  T_high,         T_high + 0.01,
                             T_high + 1 - 0.01,  T_high + 1,
                             100 ]
grid(arm)  = {false,true} x {KP, IR, SY, CA, DE} x {false,true} x landmarks(arm)
```

**Fourteen landmarks, 280 cells per arm** (2 × 5 × 2 × 14). Five sit **on** an
edge one of the six predicates names — `T_low − 1`, `T_low`, `T_low + 1`,
`T_high`, `T_high + 1` — seven are **0.01 probes** placed beside one of those
five, and `0` and `100` are the floor and the ceiling. Nothing else is in the
set, and it has been closed twice, each time by a review that found a mutant
family it could not see:

- `T_low + 1` and `T_high + 1` are the **exclusive upper bounds of classes 2
  and 1** (§2.3), and the four landmarks round 1 added are those two edges
  together with the 0.01 probe below each; a nine-landmark grid probed neither
  edge, so a family encoding class 2 as `[45, 47)` or class 1 as `[72, 74)`
  would have passed the class-membership half unchanged (round 1);
- `T_low − 1 − 0.01` is the point immediately below **class 5's lower edge**;
  a thirteen-landmark grid probed the edge but nothing under it, so a family
  encoding class 5 as `[T_low − 2, T_low)` passed **every one of the 260
  cells** (round 2). Verified both ways before it was written in: the mutant
  agrees with arm A's class vector on all 260 cells of the old grid and
  disagrees on the new one.

**The claim the grid carries, stated exactly and no wider.** For **every edge
any of the six predicates names** — `T_low − 1`, `T_low`, `T_low + 1`,
`T_high`, `T_high + 1` — the grid holds a point exactly at the edge **and its
0.01 neighbour on the side the predicates answer differently**, so both answers
appear as cells and every inclusive/exclusive decision the six predicates make
is pinned by a pair of adjacent cells. Which side that neighbour is on is not
uniform, and an earlier draft's "a point 0.01 to its excluded side" was wrong
for two of the five: below an **inclusive lower** bound the neighbour is the
excluded point (`T_low − 1 − 0.01`, `T_low − 0.01`, `T_high − 0.01`), while at
an **exclusive upper** bound the point at the edge is *itself* the excluded
side and the 0.01 point below it is the **included** one (`T_low + 1 − 0.01`
for class 2, `T_high + 1 − 0.01` for class 1). `T_low + 0.01` and
`T_high + 0.01` probe just above the two edges that are an exclusive upper
bound and an inclusive lower bound at once; `T_high + 0.01` is what separates
class 0's `= T_high` from a `≥ T_high`, and `T_low + 0.01` is its symmetric
counterpart, which no predicate of the registered family distinguishes from
`T_low`. What it does **not** establish, because no finite grid can: that two
families agreeing on all 280 cells agree everywhere. A
mutant that differs only strictly between two adjacent landmarks survives this
check, and **C9's structural equality of the predicate encodings is what bounds
that** — the two controls are complements and §6 C9 says which failure each
one catches.

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

*Second, and stated because an earlier draft got it wrong twice:* arm E's
`POLICY.md` **is not digit-free**, and no honest version of it can be. **Four
non-label digit-runs, from two sources**, survive in the frozen bytes, in text
that is byte-identical across all five arms and is therefore not a difference
between them:

| digit-run | where | why it is there |
| --- | --- | --- |
| `4` | P5's body, "unless P4 applies" | a structural cross-reference to a clause label, present identically in A, B, C, D and E |
| `3166`, `1`, `2` | the conventions paragraph's `ISO 3166-1 alpha-2` | inherited from 010, held byte-identical across all five arms |

plus the clause labels `P1`–`P5` themselves. **The count and the sources are
stated because two earlier drafts miscounted them**: the first said "three
digit-runs survive" while listing rows rather than runs, and both carried a
fifth run, `010`, from the preamble's "Synthetic policy for Study 010" — which
**round 2 removes from every arm** under `PREAMBLE_DELTA` (D-16 adopted). The
figure the round-2 review computed over the bytes it read, *five non-label runs
from three sources*, was correct of those bytes; the figure above is correct of
the round-2 bytes.

Registered mechanically (§6 C8), and true of the frozen artifact:

> **The only digit-runs anywhere in arm E's `POLICY.md` are the clause labels
> `P1`–`P5`, in-body clause-label references of the form `P<n>`, and the token
> `ISO 3166-1 alpha-2`; and no digit-run in the file equals `40` or `70`.**
> The clause-body census of §2.6 and C8 runs over each body with clause-label
> tokens `P1`–`P5` masked out, so "arm E's clause bodies carry no numeric
> content" is checked as the statement it is meant to be rather than refuted
> by a cross-reference.

**The preamble's study name was a recall channel, and round 2 closes it
[D-16].** "Study 010" was a name-keyed pointer to a public repository whose
policy text states 40 and 70: arm E was *denamed but not de-referenced*, and
retained one textual hook by which a contaminated snapshot could look up the
literals it was denied. The registered `PREAMBLE_DELTA` replaces that name with
a self-reference in **all five arms**, so the preamble stays byte-identical
across arms and arm E loses the hook:

```
Synthetic policy for Study 010.   ->   Synthetic policy for this study.
```

one substitution, at its single occurrence in 010's locked bytes, +1 byte, and
the assembled preamble is pinned by its own sha256 in `harness/PINS.json`.

**What that fixes and what it does not, stated exactly.** It removes the one
*textual* route from arm E's own bytes to the literals. It does **not** remove
residual memorization: the policy family's clause wording, its country codes
and its outcome vocabulary have been public in this repository since
2026-08-06, and a snapshot that has seen the corpus could recognise the *shape*
of the policy without being told its name. So §5.3 (i)'s recall explanation is
narrowed rather than deleted — from "recall keyed to a name the text supplies"
to "recall keyed to the text's own shape" — and the honest statement stands:
**this study still cannot separate derive-then-hug from residual
memorization.** What it can now say is that no arm hands the author a pointer.
The cost is registered in §2.1 and under [D-16]: a second registered delta from
010's locked text, on top of D-15's.

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
| A | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` | `2a6f031e17735494646dd734ee04b4430027babf62b10e1ba9a57675f37de430` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | `3349ccd06e875c76eda19278a3ce8cae61a61e807fc3e43fb1d93adcb387b86d` |
| B | `f3215bd98d77ecdf036b90470083c645a6a666b817b5a7b0072c448377e020f6` | `9da426a75e42bb13909daa097e1dc32b1cfdec86330fa69555e6c40081ff2dde` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | `aeef4aa084cdc85e10510c57844709745b397f7c7651b0d4b743fc509fee3f4d` |
| C | `77e79b2eb51ebc9114fa35037b9375dd08b4bfd8e34188a4518f086447a0c00a` | `bff3e24751087815935b748041ae2db19df5f0408dea886219fe13e0531c053c` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | `e1572c0bfa03427726f062c0b42dcc74205a6a3d2da50d50bc23e41e42217cef` |
| D | `bf6b6d47e8e3168b9f09f6ec3c45d1a502a0c7cc476848a49afc896516218bf5` | `0d47c2b135736376744dc00c9c66965465357e6a98e2ccd750505d931e9606d1` | `20391068ad761d028b3b1a8fc2bc3a04f7aec61c7f365a0ef2db9b90f25c20fc` | `2b5b341b4a9794aa512098fdbec1a468f6d037082e06cddc8913f8dac25355f2` |
| E | `8d1141f3eabc57a96739cb4c8740e95683482e51da6388212b3abc443192f55e` | `5bbb3a58dd16cd2ef2353e5cc137c74d467c5cb098e4896d2ccce8b165cf2b66` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | `cd9d88d93c55a1069337e51d3fc70604bec232b4a7bb2b6e1b03dbcb2559e084` |

Arm A's `POLICY.md` and `PROMPT.txt` were `(port time)` at registration rather than filled from
011's lock because of the two registered deltas (§2.1, [D-15], [D-16]); what
is filled now, and checked, is the pair of authorities they are derived from —
010's locked `policy/POLICY.md` at
`e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f` and 011's
pinned prompt at
`a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2`. If the
review reverses both D-15 and D-16, arm A's two cells become those two digests
outright and the derivation collapses to equality.

**What `FAMILY.json` carries beyond §2.3's six classes, and which of it this
study reads.** The file is Study 010's family document — arm A's is that file
byte for byte (§6 C9), and the other four are the same document instantiated
at their own pair by the same generator — so it carries members 010 needed and
this study does not. **Read here:** `embargoList`, and per mutation `index`,
`title`, `predicate` and `predicateProse` (the scorer's `load_arm()` reads
exactly these), and `patch`, which **§6 C2 reads against Study 010's locked
pack C** and which [D-6] reads for arm D to demonstrate that the pack-side
clause is unavailable there. **Inert in this study, read by nothing:**
`familyVersion`, `pack`, `note`, and per mutation `violatedClause`, `underD`
and `reasonsUnderD`. They are 010's plant-and-evaluate vocabulary: `note`
describes a drand draw selecting one index and a patch applied to pack C to
produce a pack D, and `underD` and `reasonsUnderD` describe that D's
dispositions. **This study draws nothing, plants nothing and evaluates no
pack**, so `note`'s "PREREGISTRATION.md §5" is 010's §5 and not this file's,
and `pack`'s path resolves in Study 010's tree — where §6 C2 does read it, at
the digest 010's own `PROTOCOL-LOCK.json` locks — and not in this one. They
are retained rather than removed because arm A's bytes are 010's lock and one
generator produces all five arms: editing them would break the byte equality
this study's class schema is anchored to (§6 C9,
`harness/tests/test_assembly.py`). The member list is registered here in full
so that a reviewer attesting the §2.10 tree manifest is attesting a file whose
every member this document names.

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

- the **preamble is byte-identical in all five arms**, and equals 010's
  preamble with the registered `PREAMBLE_DELTA` **[D-16]** applied at its
  single occurrence — the substitution `Study 010` → `this study`, published
  verbatim in Appendix A, with the assembled preamble pinned by its own
  sha256. Keeping the preamble fixed across arms is what confines each arm's
  variation to the intervention; removing the study name is what stops arm E
  carrying a pointer to a public text that states 40 and 70 (§2.5). C8 checks
  both the cross-arm equality and the derivation from 010's bytes;
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
  are the registered reference wordings. **The inclusivity invariant applies to
  arm E in the only form it can, and the difference is registered rather than
  glossed**: E has no literals, so no adjacency *side* can be preserved — you
  cannot write "the review threshold or above" in English the way you write "70
  or above". What is checked is that E's six bound phrases carry the **same six
  senses in the same six places** as A's: inclusive at `T_high` in P3;
  inclusive at `T_low` and exclusive at `T_high` in P4; exclusive at `T_high`
  twice and exclusive at `T_low` once in P5. The side flips from *after the
  literal* to *before the name* at the two inclusive bounds, and that flip is
  **inherent to denaming, not an authored choice** — which is exactly why it is
  written down here instead of being discovered in the analysis.

**Arm B carries a clause-level invariant the digit census cannot express.**
The literal multiset is preserved by any paraphrase that keeps the numbers;
what 011's census identifies as the single most anchoring-relevant feature of
the text is the **boundary-inclusivity phrasing** — A's P4 reads "40 or above
but below 70" — and those are exactly the cues the on-edge records at 40 and 70
answer. If B collapsed and that phrasing were unconstrained, "the paraphrase
weakened the inclusivity cue" would explain it at least as well as "the author
anchors to the prompt's shape", and §5.3 (iii)'s registered dependency would
take arm E's result down with it. So, registered and checked in C8:

> **In every arm whose clause bodies state the thresholds as literals — A, B,
> C and D — each numeric bound is stated with an explicit inclusivity word
> immediately adjacent to its literal, and the adjacency pattern of arm B's
> bodies matches arm A's clause for clause** — same clause, same literal, same
> side, an inclusivity word of the same sense on the same side of the literal.
> Arm E states no literals; it carries the invariant in the named form
> registered above — its six bound senses equal A's six, in the same six
> clauses, with the side comparison omitted because a named bound has no side.

The registered vocabulary, so that "inclusivity word" is a check and not a
reading: the **inclusive** cues are `or above`, `or more`, `or higher` and
`at or above`; the **exclusive** cues are `below`, `under` and `less than`. The
check masks clause-label tokens `P1`–`P5` first (as the digit census does),
strips emphasis markers, and records for each remaining literal the ordered
tuple *(clause label, literal, side, sense)*; the invariant is that arm B's
tuple sequence equals arm A's, and that arm D's equals arm A's under σ. Arm
C's bodies are byte-identical to A's, so C's tuple sequence is A's own and
is established by that byte equality rather than by a second comparison.

**The vocabulary is closed, and that is part of the invariant rather than an
implementation detail.** A bound whose cue is not one of the seven listed
phrases fails the check even if a reader would call it an inclusivity cue —
"up to but not including 70" says the right thing and is not on the list. The
closure is deliberate: an open-ended notion of "an inclusivity word" is a
reading, and a reading is what this invariant exists to replace. Its cost is
that the invariant constrains B's word choice and not only B's word *order*,
which §2.6 already registers as the price of the control. The seven phrases are
what arms A, B, C and D actually use; a future arm needing another would be
changing a registered property, not filling a gap.

**Round 2 found the invariant violated by the very text it was written for,
and the text is what changed.** The round-1 arm B read "from **40** up to but
not including 70": A's P4 lower cue follows the literal ("40 or above"), B's
preceded it ("from 40"), and Appendix A's own substitution table flagged the
asymmetry as "the review's to adjudicate" while §6 C8 asserted the invariant
held and the round-1 re-verification reported 46 registered properties passing.
Both cannot be true. The registered resolution is the one that keeps the
control: **arm B's P4 is rewritten** so its lower bound reads "**40 or more**"
and its upper bound "**below 70**", matching A's sides and senses clause for
clause. The invariant is not weakened, and the round-1 property count is
corrected in `PREREG-REVIEW.md` rather than left standing.

**What the invariant costs arm B, registered rather than discovered.** It
constrains the six bound phrases to A's sides and senses, so B's paraphrase
lives in everything *except* the bound phrases — and at P4's upper bound and
P5's three bounds it now uses A's own cue word. Arm B is therefore a paraphrase
of the *clause frames*, not of the *boundary language*, and §5.3 (iii) reads a
B result against that fact: a B that tracks says this reframing did not move
coverage, and says nothing about a paraphrase that also moves the cues. That is
a narrower control than an unconstrained paraphrase would be, and it is the
narrowness that makes it a control at all.

The clause-by-clause A ↔ B substitution table is published under **[D-4]** in
Appendix A so the pre-freeze review adjudicates each substitution rather than
reading five paragraphs as a whole.

**Arm C's permutation is registered as (P1, P2, P4, P5, P3) [D-5].** The
constraint it satisfies is stated generally rather than as one special case,
and it is checked in code:

1. **every explicit clause-label reference resolves backward** — P5's body says
   "unless P4 applies", and P4 is at position 3 with P5 at position 4;
2. **every three-part "absent a sanctions hit or an embargoed registration"
   precondition resolves backward** — P3, P4 and P5 all open with it, and both
   P1 (which establishes sanctions hits) and P2 (which establishes embargoed
   registrations) precede all three;
3. **the two-part "Absent a sanctions hit" precondition resolves backward too**
   — P2 opens with it, and P1 is at position 1;
4. subject to 1–3, the permutation **moves as many clauses as possible**:
   three of five (P3 3→5, P4 4→3, P5 5→4), with P1 and P2 in place.

**(P1, P2, P4, P5, P3) is the unique permutation satisfying 1–4**, verified by
exhaustive enumeration of all 120: exactly three permutations resolve every
reference backward — the identity, (P1, P2, P4, P3, P5) which moves two, and
this one which moves three — and no other reaches three. A harness test
re-derives that from the parsed bodies rather than comparing against a
hard-coded tuple.

**Arm C is no longer a derangement, and that is the round-2 trade [D-5].** The
round-1 registration was (P2, P1, P4, P5, P3): the unique *derangement* that
resolves clause 1 and clause 2, at the cost of leaving P2's own two-part opener
forward-referencing P1 at position 2 — provably unavoidable, since *derangement
+ every reference backward* is empty over all 120 permutations, by the same
enumeration. Round 2's finding is that arm C is **a control on which arm E's
interpretation depends**, so a residual comprehension difficulty in C is not a
disclosed cost but a live alternative explanation for a C-collapse — and a
C-collapse disarms E under §5.3 (iii)'s dependency. Comprehensibility
therefore wins over full derangement: every reference in arm C resolves
backward, and the price is that two of five clauses keep their positions.
(P2, P1, P4, P5, P3) is registered under **[D-5]** as the alternative, with the
trade stated in both directions — full derangement is the stronger *perturbation*
and the weaker *control*, and this study needs C to be a control.

Nothing else about the permutation is claimed; one permutation is one
permutation, and moving three clauses is not "reordering the policy" in
general.

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
011's cell is the composition of that equation with the two registered deltas
(§2.1).

### 2.7 The wrapper is an adaptation of an adaptation

`transcription/authoring_call.sh` is Study 011's wrapper, whose whole isolation
invocation is unchanged but for the one line named below: fresh `HOME` and
`CODEX_HOME`, `env -i` with `PATH`
and `TMPDIR` constructed rather than inherited, exclusive leak-token-free
scratch outside every git worktree, `--ignore-user-config`, explicit model,
binary digest and CLI version checked **before** the call, byte-exact prompt,
stdin closed, credential copied and deleted on the seal path and on `EXIT`,
`INT`, `TERM` and `HUP`, recursive pre-call inventory of the isolated home,
new-session identification by set difference, registry and golden digests
stamped per run. **One line of that invocation is repaired rather than
carried**, and `harness/PORTS.md` names it: 011 read the repository root with
the `git rev-parse` nested inside a `cd`, so a failed one left the root
silently equal to the caller's directory and the scratch check compared against
a directory nobody chose; here the toplevel is read first and an empty one
refuses. It is not a fourth permitted difference — the differences below are
this study's arguments, stamps and naming, and a defensive refusal on a study
that is not inside a worktree is none of those — and no run this study can make
reaches it, because the study is a git-tracked directory of this repository.
The permitted differences are exactly these, and `harness/PORTS.md` carries the
diff:

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

### 2.8 Sample size, the registered call order, and the shortfall rule

**N = 30 slots per arm [D-1]**, 150 authoring slots in total, fixed before the
batch and executed **sequentially, never in parallel**. §5.4 is the power
reasoning and round 2 re-adjudicated it against the *actual* registered rules
rather than a stricter proxy; the short version is that the study's binding
quantity is not the marginal per-class figure but **the joint probability that
the B and C control gate of §5.3 (iii) passes at all**, and that gate stands at
**0.4031 at N = 25 and 0.7658 at N = 30** under the registered scenario —
**0.4010 and 0.6702** under the containment-respecting companion §5.4 publishes
beside it (round 10, finding 4), which is the coherent reading and returns the
same decision. A
control that fails three times in five under a *true null effect in both
control arms* is not a control, which is this file's own criterion, applied to
itself. N = 25 is registered as the alternative under [D-1] with that cost
attached.

#### The registered call order: first-order carryover-balanced [D-7]

**The five arms are interleaved, not run in blocks**, because blocked execution
would confound the arm with the drift across the batch — the same reason §2.1
refuses Study 011 as a baseline, applied within the day. The batch is 30
**rounds**; each round runs one slot of each arm.

**Balancing position is not enough, and round 2 found the gap.** The round-1
schedule rotated (A, B, C, D, E) cyclically by round, which balances *position*
perfectly and balances *predecessor* not at all: under it arm E follows arm D
in 20 of its 25 calls and arm C in the other 5, and **never once follows A or
B** — verified by enumeration over the round-1 schedule. Provider-side state
carried from one call to the next is exactly what §7 admits this design cannot
exclude, and under a schedule like that, state carried from arm D's 45/72
prompt could *manufacture* arm E's predicted collapse. §7 claimed such state
"could only blur a contrast"; against an unbalanced predecessor structure that
claim was false, and it is withdrawn.

The registered order is built from a **Williams design for five treatments**,
which is the standard construction for first-order carryover balance. Ten
sequences, each a permutation of the five arms:

| | order |
| --- | --- |
| **W1** | A, B, E, C, D |
| **W2** | B, C, A, D, E |
| **W3** | C, D, B, E, A |
| **W4** | D, E, C, A, B |
| **W5** | E, A, D, B, C |
| **W6** | D, C, E, B, A |
| **W7** | E, D, A, C, B |
| **W8** | A, E, B, D, C |
| **W9** | B, A, C, E, D |
| **W10** | C, B, D, A, E |

(W1–W5 are the cyclic rows of the Williams first row `A, B, E, C, D`; W6–W10
are those five rows reversed.) Over the ten, **each arm holds each of the five
positions exactly twice** and **each of the twenty ordered pairs X→Y is
adjacent exactly twice**.

The batch is **three blocks of those ten sequences**, each block in its own
registered order:

```
block 1 (rounds  1-10):  W2 W4 W7 W10 W1 W9 W8 W6 W3 W5
block 2 (rounds 11-20):  W4 W3 W2 W10 W9 W8 W5 W1 W7 W6
block 3 (rounds 21-30):  W4 W6 W5 W7  W1 W2 W10 W8 W9 W3
```

The three orders are registered artifacts, chosen before any call so that the
round-boundary transitions are as flat as an odd number of them permits. **The
properties the harness test asserts over the expanded 150-slot order**, each
re-derived from the table above rather than restated:

| property | registered value |
| --- | --- |
| slots per arm | 30, all five equal |
| **position counts** | each arm in each within-round position exactly **6** times (25 cells, all 6) |
| **within-round directed transitions** | each of the 20 ordered pairs X→Y exactly **6** times (120 transitions) |
| **round-boundary transitions** | 29 in total; no arm ever immediately follows itself; 9 ordered pairs occur twice and 11 occur once |
| **total directed transitions** | 149; every ordered pair occurs **7 or 8** times — max minus min is **1** |

The full transition matrix, rows = predecessor, columns = successor, over all
149 transitions:

```
      A   B   C   D   E
  A   -   7   7   7   8
  B   7   -   8   8   7
  C   7   7   -   8   8
  D   8   8   7   -   7
  E   8   7   8   7   -
```

**Exact balance is arithmetically impossible here and the file says so rather
than claiming it.** 150 slots give 149 transitions and 149 is not a multiple of
20, so no order over this batch can make all twenty counts equal. What is
achievable and is registered is *max − min = 1*, and the within-round half is
exactly balanced at 6 apiece. That is the strongest first-order statement this
shape admits.

**A truncated batch is not balanced, and no balance is claimed over one.** If
the batch stops short, the transition census of the prefix that ran is
published as computed and every registered balance property is reported as
**not established**. §5's verdicts are unavailable in that case anyway (the
stopping rule below), so nothing reads a balance the prefix does not have.

All 150 slots are begun and completed within **one UTC calendar day**;
spilling past midnight is a `DEVIATIONS.md` entry, not a stopping rule. **The
rule is computed, not asserted** (round 10, finding 9): the scorer publishes
the UTC calendar dates the retained stamps carry, the count of slots that
carried no readable pair, and whether the batch crossed midnight, under
`schedule.utcDay` (§4.7). Crossing it is published as a fact and written up in
`DEVIATIONS.md`, and it stops nothing. The dates are the calendar parts of each
slot's own `startedAt` and `endedAt`; a slot whose pair the scorer cannot read
contributes no date and is counted instead, so **one day is established only
when every slot carried a readable pair** — the same "published as computed,
reported as not established" rule the transition census above is under.

**Denominators.** Let N = 30 be the slots executed per arm, `I_X` the
pipeline-invalid runs in arm X, and `V_X = N − I_X` its valid runs. **The
primary endpoint's denominator is N, not `V_X`** — §4.2 registers why, and it
is a round-2 change: excluding pipeline-invalid runs conditions the endpoint on
an outcome the arm's own policy text can influence. `V_X` survives as the
per-protocol secondary's denominator. The §5 cuts are stated on **exact
interval bounds**, not on observed coverage, precisely so that a denominator
carrying more misses faces a boundary that already carries them — Study 011
§5's lesson, reused. **[D-13]** The arms are not truncated to a common
denominator; every arm's N, `I_X` and `V_X` are published beside its rates, and
if two arms' valid counts differ by more than 2 the per-protocol secondary
carries a stated caution.

#### The stopping rule: an incomplete batch is descriptive-only [D-21]

**If the batch does not complete all 30 rounds, this study returns no verdict
of any kind.** Not a reduced-confidence verdict, not a verdict on the arms that
happen to be complete, not a contrast over a smaller denominator. Every level
verdict is `UNRESOLVED-BY-DESIGN`, no contrast is computed or reported, and the
batch is published as slots, rates, intervals and census — the whole descriptive
surface — with R of 30 rounds named in the headline.

**Why the rule is this blunt.** §7 admits an in-process route: nothing prevents
a library caller importing the scorer, computing arm E's rate at round 10,
publishing nothing, and leaving the driver's guard unarmed. Combined with the
interleaved order — every arm exists from round 1 — and a shortfall declarable
at any round, that is textbook optional stopping: an operator holding a
directional prediction could look, like what they saw, and declare a shortfall.
An earlier draft answered this with a **floor** — no verdict below eleven valid
runs, since a perfect arm's exact lower bound is 0.6915 at V = 10 and 0.7151 at
V = 11 — and with a recorded wall clock. Round 2's finding is that a floor does
not remove optional stopping, it only moves it: the operator waits until round
11 and then stops when the picture is favourable. **A timestamp is not a
pre-commitment, and a denominator large enough to support a verdict is exactly
the denominator an interested stopper wants.** The registered operating
characteristics of §5.4 are computed for a fixed N and do not describe a rule
that may stop when the data look right; publishing them beside a stopped
batch's verdicts would be publishing a guarantee this study did not earn.

So the rule keys on **completeness, not on size**:

- **any incomplete batch, at any round, for any reason, is descriptive-only.**
  All 30 level verdicts are `UNRESOLVED-BY-DESIGN`; no contrast verdict, no
  COLLAPSE-DISJOINT, no §5.3 pattern verdict, and no R1 adjudication is
  computed, reported, or inferable from the published tables;
- the same holds **per arm** if any arm holds fewer than 30 scheduled slots,
  whatever the round count was;
- `V_X` < 11 is retained as a *second*, independent floor for the per-protocol
  secondary, so a complete batch that lost most of an arm to pipeline
  invalidity also returns no per-protocol verdict for it;
- the scorer computes and writes all of this itself, so "the rule could not
  have fired" is a published fact rather than a reader's inference from a table
  of INDETERMINATEs;
- and this is registered **before any call**, so it costs the study a real
  outcome: a batch that dies at round 29 for reasons no one chose publishes no
  verdict. That is the price of the guarantee, it is paid in advance, and
  [D-21] records the alternative (verdicts above a floor, with the stopping
  risk stated) and why it was not taken.

**Shortfall declaration.** If the batch cannot complete, the driver writes
`SHORTFALL.json` naming the reason, the last completed round *R*, **the exact
completed prefix of the registered schedule** (§2.8's global index of the last
completed slot), and **the UTC wall-clock time of the last completed slot
that retains a `CALL.json`** — the declaration names which slot that was
(`lastSlotEndedAtFrom`), a tail of clockless refusals falls back to the last
slot that has one, and a prefix with no clock at all records both members
null with the reason stated (round 4, finding 10) — all **before
anything is scored**, and the headline reports "R of 30 rounds completed".
`batch.py shortfall` refuses when the slots present are not fewer than the
registered plan, and the scorer requires the declaration's prefix to match the
slots actually present, slot for slot. The wall-clock member does not make a
stop involuntary — §7 still lists that as unproven — but it timestamps the stop
against the append-only ledger. **An arm the completed prefix has not reached
holds no `authoring/` root at all** — the driver creates one with that arm's
first slot — and under the declaration the scoring reads it as an empty
population rather than as an arm dropped from the batch, while a prefix of zero
slots carries no ledger at all, because the ledger is written inside the run
loop after a slot, and the scoring admits its absence only on a declaration
recording zero rounds, zero slots and no last slot (round 9, finding 4).

**Resume after a crash [D-22].** Resumption is by **global schedule index**,
not by round: `batch.py run --resume` reads the ledger, finds the highest
global index recorded, verifies that the ledger's prefix is exactly the
registered schedule's prefix of that length, and continues at the next index.
`--start-round K` is **removed** — round 2 found it cannot resume a partly
completed round without either overlapping slots the ledger holds or silently
omitting the rest of that round, and neither is detectable after the fact from
a round number alone. The ledger `BATCH.json` holds one append-only record per
slot carrying `(globalIndex, round, position, arm, slotIndex)`; a resumed
invocation merges into it, refuses to overlap any recorded global index, and
refuses if the recorded prefix diverges from the registered schedule at any
position. No slot is ever re-run.

**Prohibited, without exception:** computing any rate or verdict before the
batch is sealed; adding rounds after any rate has been computed; running a
second batch and pooling it with this one; recomputing a published rate or
verdict on a different population; **and dropping, adding or re-authoring an
arm after any call has been made.** An arm is a registered artifact; a sixth
arm, or a different arm E, is a separate study with its own registration.
Mechanically, as in 011: the driver cannot compute coverage; the scorer refuses
unless the batch is terminal; the driver refuses to create any slot in any arm
once `RESULTS.json` exists; no invocation can plan a slot past global index
150; and the registered scoring command takes the batch root and an optional
record-emission directory and refuses every other argument.

### 2.9 What each slot retains

Study 011's retention set, unchanged, plus the arm and schedule stamps:
`CALL.json` (argv, cwd, isolated home and `CODEX_HOME`, environment names **and
values**, model, CLI identity and binary digest, integer exit status,
new-session count, slot index, round index, **within-round position**,
**global schedule index**, **arm id**, **arm prompt digest**, UTC start/end,
the recursive pre-call inventory of the isolated home, whether the credential
was copied and removed, and the digests of the registry (`pinsSha256`) and the
golden capture (`goldenSha256`)), `stdout.raw`, `stderr.raw`, `session.jsonl`,
`context.json`, `completion.txt` (written **only** when the process exited 0),
and `REFUSAL.json` when the wrapper's exit status was not 0. Nothing in that
set is a judgment.

**Each slot is sealed by a terminal manifest, and the manifest is chained into
the ledger.** When the wrapper returns from a slot — on every exit path, refusals
included — the **driver** writes `SLOT-MANIFEST.json`:
every entry in the slot tree — regular files by relative path, byte length
and sha256; anything that is not a regular file (a symlink, a directory with
no files, any other kind) by relative path and a type marker, so that adding
ANY entry after the seal breaks it rather than buying an admission code and
a denominator change (round 7, finding 3) — and the sha256 of that sorted
list. The ledger record for the slot
carries that manifest digest **and the previous ledger record's digest**, so
`BATCH.json` is a hash chain over the batch in schedule order rather than a
list of independent lines. The sealer is the driver and not the wrapper
by round 3's finding 5, dispositioned: the wrapper is not the last writer
into a refused slot — `REFUSAL.json` and the schedule stamps are the
driver's — so a wrapper-side seal would cover every slot except exactly
the ones whose retained bytes explain a failure, and the pipeline-invalid
rate is an endpoint (§4.4). Round 2's finding is the reason the seal exists: a slot
tree with retained bytes and no seal can be edited afterwards, and **one
edited slot moves a verdict** — changing a single arm-A miss turns 22/25 MID
into 22/24 HIGH, and changing a single arm-E hit turns 3/25 MID into 2/24 LOW.
Registered consequence, in advance: **if any slot's recomputed manifest differs
from the ledger's, or the chain does not verify, the batch is not scored
confirmatorily at all** — the discrepancy is published, every level verdict is
`UNRESOLVED-BY-DESIGN`, and no contrast is reported. It is *not* handled by
moving the slot into `V_X`'s complement, which would let an alteration buy
exactly the denominator change that produces the verdict.

Registered honestly, because a hash chain in the same tree is not a
transparency log: **the operator can recompute the whole chain.** What the
chain establishes is that a slot was not altered *in isolation* or after the
ledger was published; it does not establish that the ledger was written
honestly. §7 lists it under "recorded, not proven" in those words.

All 150 slots are committed, invalid ones included (§8) — roughly 90 KB per
slot, about 13 MB in total.

### 2.10 The batch registry

`harness/PINS.json` is the run-time registry: the codex binary digest, CLI
version and model; the digests of every arm's `POLICY.md`, `PROMPT.txt`,
`FAMILY.json` and `ARM.json`; **the digest of the single registered mirror
module `harness/policy_mirror.py`** (§2.2 [D-14]), which is the arbiter of
every arm's labels and is pinned here as well as in `harness/PORTS.md`; **the
digests of the assembled preamble and of `CONVENTIONS_DELTA`** (§2.1, §2.6
[D-15], [D-16]); **the digest of `CLAIM.md`** (§1); the probe prompt; N and
**the registered call order of §2.8**; the interpreter; the recorded operator
assent for §6 C7; **Study 011's `PINS.json` and `PORTS.md` digests and this
study's own `PORTS.md` digest** (§2.2); the recaptured golden context's digest
(`null` until §3.2's capture is registered); this preregistration's digest at
the freeze (`null` until then); **the final review round's tree manifest
digest** (below); and a pointer to `harness/PORTS.md`.

#### The review-to-freeze binding is over the whole tree [D-20]

**Round 2's first finding is that the round-1 binding was self-authenticating,
and it was right.** That binding recorded, per review round, the sha256 of the
five arm texts, and required each frozen `arms/<X>/POLICY.md` to equal the
digest the final round recorded. But `PREREG-REVIEW.md` is itself a file in
this study directory: the preregistration, the README, `CLAIM.md`, the port
table, the harness sources, `PINS.json`, the five arm texts **and the review
record's own digest table** could all move together between the last review and
the freeze, and every specified equality would still pass — because the thing
each artifact is checked against is a number the same commit supplies. Only the
five policy texts were covered at all; nothing bound the code that computes the
verdicts.

Registered instead, and this is what "the artifacts that were reviewed are the
artifacts that ran" now means:

1. **The final review round is performed over the complete post-port candidate
   tree** (§2.2 [D-20] fixes the ordering that makes this possible), and the
   reviewer attests **an exact commit id and a tree manifest** covering every
   artifact of this study — `PREREGISTRATION.md`, `README.md`,
   `PREREG-REVIEW.md` as it stood entering that round, `CLAIM.md`, all twenty
   arm files, every `harness/` source and test, `harness/PORTS.md`,
   `analysis/mirror2_<arm>.py` for all five arms, and `MIRROR-AGREEMENT.md`.
   **The manifest's carrier handling, registered exactly** (round 3
   finding 1 and round 4 finding 2, dispositioned): `PREREG-REVIEW.md` is
   excluded — it carries the attestation, and a manifest covering its own
   attestation record changes the moment the digest is written down — and
   `harness/PINS.json` is bound through its **normalized projection**: the
   registry parsed, its four post-freeze members
   (`freeze.treeManifestSha256`, `freeze.preregistrationSha256`,
   `golden.sha256`, `isolationNegative.assent`) set to null, canonically serialized, and
   hashed into the manifest as its own entry. **What the binding
   establishes is stated exactly, because round 5 demonstrated the wider
   claim false**: the manifest detects every edit that leaves the
   registry's pin or the final round's attestation standing; an edit that
   updates the pin must also match the attestation line the final review
   round wrote into `PREREG-REVIEW.md`, which `verify_tree()`
   cross-checks, so defeating the binding requires rewriting the review
   record itself — and THAT is forbidden by rule and visible to the
   reviewer who holds the transcript, not prevented by a digest. The two
   freeze pins refuse unless they land together, in both directions. The
   four nulled members are bound elsewhere (the manifest member is the binding
   itself, the golden per slot by the `goldenSha256` stamp against the
   committed capture, the assent a consent record). **Compiled bytecode
   beside a reviewed source loads even under `-B`** (round 5, finding 3),
   so the verification gate validates every cache entry against the
   source beside it — the running interpreter's magic number and the
   header's own stamp or source hash — and refuses anything orphaned,
   stale or foreign: a fresh cache of a reviewed source is that source
   compiled, and admits; a cache the sources did not produce refuses. What remains outside
   any digest is `PREREG-REVIEW.md`'s own honesty, which is [D-20]'s
   stated residual; the externally signed attestation stays the stronger
   alternative. A frozen registry whose `preregistrationSha256` is filled
   while `treeManifestSha256` is null **refuses** — the two freeze pins
   land together or not at all (round 4, finding 1). The manifest is the sorted list of
   `(relative path, byte length, sha256)` over every tracked regular file in
   the study directory, and its own sha256 is the **tree manifest digest**.
2. **That digest is recorded in `PREREG-REVIEW.md` and pinned in
   `harness/PINS.json`**, and `harness/integrity.py` recomputes the manifest
   over the frozen tree and refuses unless it matches — excluding only the
   files that cannot exist yet by construction (`RESULTS.json`, `RATES.md`,
   `CENSUS.md`, `ANALYSIS.md`, `DEVIATIONS.md`, and the slot trees), which are
   named in the registry as an explicit exclusion list rather than left to a
   pattern. An entry ending in `/` names a tree and excludes it and everything
   beneath it; every other entry names exactly one file and excludes that path
   and nothing under it, so an unlisted tracked file that merely sits below an
   excluded file's name stays in the manifest.
3. **Any byte change after the final review requires a new review round.**
   There is no "editorial" exemption, no "the digest table was updated" path,
   and no way to change one file and re-record one digest: the manifest covers
   everything at once, so any edit invalidates it and the only way forward is
   another round with its own attestation.
4. Registered honestly, because this is a bound and not a proof: **the manifest
   is computed by this study's own code over this study's own worktree.** It
   binds the *reviewer's* attestation to a specific byte state, and it makes a
   post-review edit visible to anyone who recomputes it; it does not make the
   tree externally timestamped, and this study has no transparency log (§7).
   An externally signed attestation — the reviewer signing the manifest digest
   with a key this repository does not hold — is registered as [D-20]'s
   alternative and is the stronger form.

**The rule applies from round 3 onward.** Rounds 1 and 2 reviewed a
specification and five draft texts before any port existed, so they record what
they could bind: the five arm-text digests, computed from Appendix A by the
registered assembly rule. The freeze is bound to the **final** round's tree
manifest, and a final round that carries only arm digests is not a final round.

The committed `harness/PINS.json` is the registry of record and that is
enforced per run and per population, exactly as in 011: the wrapper records the
digest of the registry it ran under, the scorer computes the committed file's
digest itself, and any slot whose stamp differs is `registry-mismatch`. The
**scorer takes no registry argument at all** and derives every path from the
harness's own location, because a supplied registry identical to the committed
one except for the arm digests or for N would otherwise redefine what was
measured while every per-slot stamp still matched.

**The population root is derived too, and round 2 is why [D-23].** An earlier
draft left `--slots` on both the scorer and the shortfall declaration, so the
population could be pointed at any directory of the right shape — a copy with a
slot removed, a duplicated arm, a renamed tree. Every per-slot check would still
pass, because a same-arm slot copied into the same arm is not `arm-mismatch`.
The registered surface is now:

```
score_rates.py score [--emit-records DIR]      # the ONLY publisher
batch.py shortfall --reason TEXT
```

and **`--slots` does not exist on either**. The canonical `arms/` root is
`harness/../arms`, resolved from the harness's own location; anything else
refuses. `--emit-records` survives because its target must be *outside* the
population and is checked to be (§7).

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
reported with its refusal code, and — under the round-2 endpoint of §4.2 —
**counted as covering nothing in the primary denominator rather than removed
from it**. A run that is admissible and compiles but whose author produced
nothing usable is **authoring-empty** — valid, counted, covering nothing.
Excluding authoring-empty runs would quietly condition every rate on the author
having succeeded, which is not the quantity §1 asks for, and in this study it
would do something worse: **a perturbation that makes the author fail outright
would be scored as if it had never been tried.**

**Round 2 found that the same argument applies to pipeline-invalid runs, and
this file had made the opposite call.** The old text justified excluding them
on the ground that "the gates are arm-independent by construction". The gates
are; **the probability of tripping them is not**. A policy text can move
whether the author reaches for a tool (transcript whitelist), whether the
process exits 0, whether a completion is produced at all, and whether what it
produces parses — every one of those is a refusal code in the table below, and
every one of them is downstream of the intervention. Conditioning the primary
endpoint on surviving them is post-treatment selection, and it points the wrong
way: the arm whose text most disrupts authoring loses exactly the runs that
would have covered nothing. §4.2 registers the fix — intent-to-treat over the
scheduled N — and this section registers the classification that feeds it.

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
- pipeline loss is **conservatively charged against the arm that produced it**
  in the primary endpoint (§4.2), and its effect on every rate is published as
  the registered sensitivity bound `[k/N, (k+I)/N]`, so a reader can see
  exactly how much of a rate the losses could account for;
- an arm losing conspicuously more runs than the others is **reported as a
  finding about that arm**, not filtered away as noise. The *gates* are
  arm-independent by construction; **tripping them is not**, and an earlier
  draft's claim that a refusal rate can never be an effect of the policy text
  is withdrawn. What is still refused is the reverse move: a high `rho_X` is
  not read as *support* for a collapse prediction, because §5's rules read
  coverage and nothing else.

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
| **`schedule-mismatch`** | **pipeline-invalid** |
| **`session-reused`** | **pipeline-invalid** |
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

**Three codes are new to this study**, and each closes a route round 1 or round
2 found open:

- **`arm-mismatch`** — the slot's recorded arm or arm-prompt digest is not the
  arm whose tree it sits in;
- **`schedule-mismatch`** — the slot's recorded `(globalIndex, round, position,
  arm)` is not what §2.8's registered call order assigns to that global index,
  or the slot at that index in the ledger is not this slot. This is what a
  same-arm copy, a rename, or a duplicated slot trips: `arm-mismatch` cannot
  see any of them, because a copy of an A slot placed in the A tree names the
  right arm and carries the right prompt digest. **The ledger and the slot set
  must be in bijection** — every ledger record has exactly one slot at its
  registered path, every slot has exactly one ledger record, and the counts
  agree per arm and in total. A slot with no ledger record, or a ledger record
  with no slot, refuses the whole scoring rather than scoring that slot;
- **`session-reused`** — the slot's `session.jsonl` bytes, session id, or the
  identifying members of its `CALL.json` (working directory, isolated home,
  start clock) are shared with **any other slot in any arm**. §3.2 already
  applies this rule to the two capture slots, on the reasoning that a copied
  slot must not be able to agree with itself; round 2's finding is that the
  same reasoning applies to the 150 batch slots, where a copied slot would
  otherwise add a covered run to a denominator. Cross-slot uniqueness is
  checked over the whole population before any rate is computed.

Every other code, and every registration behind it — the `lstat`-first
slot-tree rule, the totality rule that reads `REFUSAL.json` inside the total
path through the duplicate-key loader, `refusal-conflict`, `scorer-error` — is
Study 011 §3.3's, ported unchanged, and the port is reviewed against that text
rather than re-derived.

**One class of failure is deliberately *not* a refusal code, because a code
would understate it.** A slot whose recomputed `SLOT-MANIFEST.json` disagrees
with the ledger, or a ledger whose hash chain does not verify (§2.9), does not
mark that slot invalid: it **invalidates confirmatory scoring for the whole
batch**. Every level verdict is `UNRESOLVED-BY-DESIGN`, no contrast is
reported, and the discrepancy is published with the slot named. Round 2's
reasoning, registered so it is not softened later: a code that moves one slot
out of `V_X` hands an alteration precisely the denominator change that produces
the verdict it was made to produce.

## 4. Endpoints

Estimation and registered decision rules. **No hypothesis test, no p-value, no
multiplicity correction** — there is no test to correct. The §5 verdicts are
decisions computed from exact intervals by a rule fixed before the data, not
inferences with an error rate to control.

**The full verdict surface, counted here so it is not undercounted later:**

| verdicts | how many | where |
| --- | --- | --- |
| primary (ITT) level verdicts, per arm × per class | 5 × 6 = **30** | §5.1, §4.2 |
| **S1 placement level verdicts**, per arm × per class | 5 × 6 = **30** | §5.1, §4.6 S1 |
| **per-protocol level verdicts**, per arm × per class | 5 × 6 = **30** | §5.1, §4.6 S11 |
| contrast verdicts (four arms against A × per class) | 4 × 6 = **24** | §5.2 |
| **placement contrast verdicts** | 4 × 6 = **24** | §5.2 |
| level verdicts under S10 old-edge cross-scoring | up to 5 × 6 = **30** | §4.6 S10 |
| registered census expectation patterns (per arm) | **5** | §4.5 |
| **the decision-table row** — one, for the whole study | **1** | §5.3 |

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

### 4.2 Primary endpoint: per-class per-arm coverage rate, intent-to-treat

**The denominator is the arm's scheduled slots, N, and a slot that produced no
usable evidence is counted as covering nothing.** For each arm
X ∈ {A, B, C, D, E} and each i ∈ 0…5:

```
k_{i,X} = |{ slots s of arm X : s is valid and H(s) ∩ class_i(s) ≠ ∅ }|
c_{i,X} = k_{i,X} / N                                   <- PRIMARY (ITT)
```

reported as the exact fraction, as a decimal to 3 places, and with the §4.3
interval. Thirty numbers with thirty intervals.

**Why the denominator is N and not `V_X` [D-24].** An earlier draft made
`k/V_X` primary and defended it on the ground that the admission gates are
arm-independent. §3.3 now records why that defence does not hold: the gates are
arm-independent, the *probability of tripping them* is not, and excluding
tripped runs conditions the primary endpoint on a post-treatment outcome the
intervention can move. The direction of the bias is the bad one — an arm whose
text disrupts authoring sheds exactly the slots that would have covered
nothing, and its rate rises. Intent-to-treat over the scheduled slots removes
that channel: **every slot the schedule created is in every denominator, and a
slot that did not yield an admissible, compiled, class-reaching record counts
as not reaching the class**, whatever the reason.

**The sensitivity bound is published beside every primary rate**, because ITT
is conservative in the other direction and this file will not pretend
otherwise. With `I_X` pipeline-invalid slots in arm X, the true rate over the
runs that *could* have covered lies in

```
[ k_{i,X} / N ,  (k_{i,X} + I_X) / N ]
```

— the lower end is the registered primary (every invalid slot assumed to have
covered nothing), the upper end is its complement (every invalid slot assumed
to have covered). Both ends are published, per class per arm, with the §4.3
interval on each. When `I_X = 0` the two ends coincide and the bound is a
point, which is the expected case: Study 011 lost one slot in fifty.

**`k/V_X` survives as the registered per-protocol secondary** (§4.6 S11), with
its own intervals, published beside the primary and never substituted for it.
Where the two disagree in level, **the primary governs every §5 verdict** and
the disagreement is reported in `ANALYSIS.md` as a finding about the arm's
pipeline loss.

Denominators are identical across classes *within* an arm by construction —
they are N for every arm and every class — and the scorer asserts it: it
collects the six `trials` values it just wrote per arm for each endpoint and
refuses the whole scoring unless the primary set is exactly `{N}` and the
per-protocol set is exactly `{V_X}`.

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

**What "exact" means here, stated because the word is doing more work than it
can carry.** Clopper–Pearson coverage is exact **conditional on the slots of a
class being independent Bernoulli trials with a constant success probability**.
The arithmetic is exact rationals with no libm; the *model* is an assumption,
and §7 records that this study cannot rule out provider-side state shared
across calls, which would break both halves of it. So every interval in this
file is an exact interval **for a model this design cannot verify**, the phrase
"exact interval" always means that, and §9 repeats it. S6 (distinct completions
across arms) is the one observable that would hint at the assumption failing.

**Registered test vectors, asserted by the harness tests in CI.** At n = 30,
this study's own denominator, with the two §5.1 cut locations marked:

| k / 30 | exact 95% interval | |
| --- | --- | --- |
| 0 | [0.0000, 0.1157] | |
| 1 | [0.0008, 0.1722] | |
| 2 | [0.0082, 0.2207] | |
| 3 | [0.0211, 0.2653] | **LOW cut** — the largest k with `U ≤ 0.30` |
| 4 | [0.0376, 0.3072] | first k above the LOW cut |
| 15 | [0.3130, 0.6870] | |
| 26 | [0.6928, 0.9624] | last k below the HIGH cut |
| 27 | [0.7347, 0.9789] | **HIGH cut** — the smallest k with `L ≥ 0.70` |
| 28 | [0.7793, 0.9918] | |
| 29 | [0.8278, 0.9992] | |
| 30 | [0.8843, 1.0000] | a perfect arm |

**The n = 25 vectors are retained** because N = 25 is [D-1]'s live alternative
and the review may take it: `k=0 → [0.0000, 0.1372]`, `k=1 → [0.0010, 0.2035]`,
`k=2 → [0.0098, 0.2603]`, `k=3 → [0.0255, 0.3122]`,
`k=12 → [0.2780, 0.6869]`, `k=22 → [0.6878, 0.9745]`,
`k=23 → [0.7397, 0.9902]`, `k=24 → [0.7965, 0.9990]`,
`k=25 → [0.8628, 1.0000]`.

And **Study 011's registered vectors at n = 50 are retained as a port
control** — `k=0 → [0.0000, 0.0711]`, `k=1 → [0.0005, 0.1065]`,
`k=25 → [0.3553, 0.6447]`, `k=40 → [0.6628, 0.8997]`,
`k=45 → [0.7819, 0.9667]`, `k=50 → [0.9289, 1.0000]` — so the ported
arithmetic is checked against numbers a predecessor already published.

**The frozen interval scope.** An interval is computed and published for every
rate whose denominator is N or `V_X`: the six primary ITT rates per arm and the
upper end of each one's sensitivity bound (§4.2); the six per-protocol rates
per arm (§4.6 S11); the raw, Q and Q-only per-class rates per arm (§4.6 S1,
S2); the all-six rate per arm (S3); the old-edge cross-scored rates per arm
(§4.6 S10); and the pipeline-invalid rate per arm (§4.4). It is **not**
computed for the mislabel share, whose denominator is the runs that reached the
class, nor for any record-level pooled quantity, nor for any census count in
§4.5, because records within a run are not independent. A harness test walks
`RESULTS.json` and requires the set of blocks carrying `ci95` to be exactly
that list.

### 4.4 Primary endpoint: the pipeline-invalid rate, per arm

`rho_X = I_X / N`, with an exact interval, and the histogram of refusal codes
over §3.3's registered table, **per arm and pooled**. Reported in the headline
beside the coverage rates, never as a footnote. At `rho_X ≥ 0.10` the arm's
contrasts carry a stated caution over the whole arm.

**Under the round-2 endpoint this rate is no longer verdict-neutral, and the
old sentence saying it was is withdrawn.** With `k/N` primary, a
pipeline-invalid slot lowers that arm's primary rate by `1/N` for every class
it would have covered, so `rho_X` is exactly the width of the §4.2 sensitivity
bound. That is not double-counting — it is the single place the loss is
charged, and the bound's upper end is published so the reader can undo it. What
the earlier text got right and this keeps: `rho_X` is not itself evidence for
or against any §5 prediction, because no §5 rule reads it.

At N = 30 this endpoint is coarse and the coarseness is registered: 0/30 gives
[0.0000, 0.1157] and 1/30 gives [0.0008, 0.1722], so this study cannot
distinguish a 2% loss rate from a 12% one and does not try.

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
  1.0. This is the table that showed the empty (23.75, 39) band.
- **X4 — within-run and across-run redundancy**: distinct profiles per run, and
  the number of runs sharing a whole-run profile multiset.
- **X5 — per-clause deciding counts** and the outcome distribution.
- **X6 — the misderivation sentinel list, arm E only.** Registered *before* the
  data, as a named census output, so that a comprehension failure in arm E is
  **diagnosed rather than assumed away by S5**. The census reports, per listed
  value, the count of records at it and within 0.01 of it:

  | value | the misreading that produces it |
  | --- | --- |
  | 70, 40 | the correct derivation — seven tenths and four tenths of a full range of one hundred |
  | 0.7, 0.4 | the fractions taken as scores rather than as fractions *of the range* |
  | 7, 4 | "seven tenths"/"four tenths" read as the numerals alone |
  | 28 | four tenths of the **review threshold** (0.4 × 70) instead of of the range — the reading an earlier draft's pronoun made available, removed under D-3 |

  **This is a sentinel list, not an enumeration, and round 2 corrected the
  claim.** An earlier draft called it "every value arm E's frozen wording
  admits under a wrong but coherent reading". No finite list can be that: a
  reader can compound a scale error with a fraction error, misread the
  conventions paragraph's range, apply one threshold's derivation to the other,
  or arrive at a value by a route nobody anticipated. What X6 does is check the
  four *anticipated* families cheaply and in advance. **X4's and X3's full
  distributions are what catch an unanticipated one**, and a mass of arm E
  records at any single value not in this list is reported as a finding in its
  own right.
  Registered honestly: **28 comes from wording this study has already
  removed** — it is kept as a sentinel precisely because removing a reading is
  not the same as proving it gone, and if 28 appears anyway that is
  information about the model rather than about the text.
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
than to the *token* — **derive-then-hug**. It is registered here so it is
available before the data rather than improvised after it. §5.3 (i) registers
**residual memorization** beside it as the other explanation of exact
clustering, and records that **this design cannot separate the two**: [D-16]
removes the textual pointer, not the corpus.

### 4.6 The other secondaries, ported

- **S1 — raw intersection rate**, per class per arm: the class was reached by
  some accepted record, **label irrelevant**. `a_i − c_i` is the label tax.
  **S1 is not a secondary in the ordinary sense: §5.3 (i)'s confirmation rule
  reads it directly**, because it is the only endpoint in this file that
  measures *where the author put records* rather than *where the author put
  records and labelled them correctly*. It carries the same §4.2 denominator
  (N, intent-to-treat), the same §4.3 intervals and the same §5.1 cuts as the
  primary, so a level verdict on S1 means what a level verdict on the primary
  means. §5.3 (i) is where it is read.
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
  scored against **arm A's** family predicates, **label irrelevant, exactly as
  S1 is**: an S10 hit is an accepted record that falls in one of the baseline's
  classes, whether or not its own outcome matches this arm's mirror. This is
  class membership only: it asks where each arm's records land in *the
  baseline's* coordinate system, and that is a question about placement, so the
  label filter is not applied. An earlier draft took the H/Q split from the
  arm's own mirror, which made a record placed at 40 or 70 and labelled by the
  old thresholds invisible to the one endpoint registered to see it — under
  arm D's (45, 72) mirror old class 2 (P ∧ [40, 41)) was then unreachable
  altogether and old classes 0 and 1 reachable only through records that handle
  personal data (round 10, finding 7). It is the direct measure of the rename
  prediction and its registered pattern is in §5.3.
- **S11 — the per-protocol coverage rate**, per class per arm: §4.2's `k/V_X`,
  the quantity an earlier draft made primary, with its own §4.3 intervals and
  its own §5.1 level verdicts. Published beside the primary, never substituted
  for it, and where the two levels disagree the disagreement is itself
  reported. New in round 2.

**The S-numbers diverge from Study 011's, and the mapping is stated rather
than left to trip a reader coming from that file.** 011's S8 is the
pipeline-invalid rate and its S9 the wall clock; here the pipeline-invalid rate
is **promoted out of the secondaries to §4.4** as a primary endpoint, **S8** is
the wall clock (011's S9), **S9** is 011's §5 tier mapping (which 011 carried
in its §5 rather than as a secondary), and **S10** and **S11** are new to this
study. S1–S7 are 011's S1–S7 unchanged in meaning, keyed per arm.

**S1, S2 and S5 are load-bearing this time and are registered as such — and
round 2 found that saying so was not enough.** They are what separate three
readings of a collapse in arm D or E, and an earlier draft called them
load-bearing while giving them no cut and letting no decision read them:

**"At the ceiling" is a cut, not a word** (round 3, finding 9,
dispositioned): arm E's S5 labels are at the ceiling iff it has **at least
one accepted record** and |Q| = 0 among them — no accepted record
mislabelled across the arm's valid runs. **An arm with no accepted record at
all has no accuracy to read** (round 10, finding 8), exactly as S2's
mislabel share has no denominator to read: its pooled rate is published as
`null` and its labels read **degraded**, the direction that does not
confirm, and this file registers that here rather than leaving it to the
scorer. The literal ceiling is chosen over a tolerance because §4.6's third
row is exact under it, and any tolerance would be a number this file never
registered; §5.4's operating characteristics model coverage only and do not
describe this conjunct, which is stated here rather than discovered.

| S1 (raw placement) | S5 / S2 (labels) | the reading | what §5.3 (i) does with it |
| --- | --- | --- | --- |
| **LOW** — the class was reached at most 3 times of 30 | at the ceiling | no accepted record was mislabelled, and where placement collapsed the class was reached at most 3 times of 30 — LOW bounds placement, it does not zero it | **PLACEMENT collapse** — this is what R1 predicts, and the only thing that confirms it |
| **LOW** | degraded | at least one accepted record was mislabelled, or the arm produced no accepted record at all | **comprehension collapse** — published as one, R1 not confirmed |
| **HIGH or MID** — the records *are* at the boundary | degraded, so H-coverage falls | the author placed records at the boundary and labelled them wrong | **label collapse** — the hugging did **not** go away; R1 is not confirmed and saying otherwise would be reading a labelling failure as an anchoring result |

**What the ceiling establishes, and what it does not** (round 9, finding 2).
`|Q| = 0` says every accepted record arm E produced carries the label the
mirror assigns it. It does **not** say the author derived either threshold.
`harness/policy_mirror.py`'s `verdict()` returns at the sanctions clause and
then at the embargo clause **before it reads `riskScore`**, so a record with a
sanctions hit or a registration in KP/IR/SY is labelled correctly at every
threshold pair, and a record far below both thresholds is labelled correctly at
every pair above it. Class 4's predicate is exactly the first kind, so an arm E
whose accepted records are all sanctions or embargo cases reads `|Q| = 0`,
keeps class 4 out of collapse, places nothing in classes 0, 1, 2, 3 and 5, and
would reach §5.3's row 5 having exercised neither number. Row 5's **fifth
conjunct** is stated on that arm's own records: **arm E does not read LOW on
class 3**, the interior review band `¬S ∧ ¬E ∧ T_low ≤ risk < T_high`, whose
members are by definition scored *between* the two thresholds and are labelled
by a mirror that has passed the sanctions and embargo clauses and read
`riskScore` — so covering it at all means placing records the two numbers
bracket.

**The conjunct is a level verdict on arm E and not a contrast against arm A**
(round 10, finding 3). Round 9 registered it as a contrast — arm E not reading
COLLAPSE on class 3 — and a contrast is INDETERMINATE, never COLLAPSE, whenever
the baseline itself is not HIGH (§5.2), so that form was satisfied *vacuously*
by an arm E that covered class 3 in none of its thirty runs whenever arm A fell
short there: the one arm the conjunct was added to refuse. Read on arm E's own
level the conjunct is uniformly at least as strong, strictly stronger in exactly
that case, and it moves no figure §5.4 publishes. Class 3 is **not** the one
class whose members are scored between the two thresholds — class 2 nests
strictly inside it — it is the only class *available*: 0, 1, 2 and 5 are the
four the prediction says will collapse, so requiring any of them not to collapse
would contradict the proposition row 5 confirms, and class 4 has no numeric
content at all.

The conjunct is registered as **excluding a degenerate case, not as
establishing comprehension**, and its weakness is registered with it: *not LOW*
is not *HIGH*, so a class 3 covered in as few as four of thirty runs satisfies
it, and it tolerates a wrong-but-nearby derivation — which is what §4.5's X6
census is for. **No conjunct available to this design could establish
comprehension**: the set of threshold pairs consistent with a set of correct
labels is an *interval* and never a point, and a record on each side of a
threshold bounds that interval only to the gap between the two records — so a
straddle conjunct would have to register a straddle **width**, and a straddle of
width 2 already avoids all four of §2.3's one-wide bands (classes 0, 1, 2 and 5)
and is therefore compatible with the LOW verdicts row 5 requires. Round 10
considered exactly that conjunct, **conceded** that a correctly-labelled
straddle of both thresholds would establish real threshold-sensitivity and is
satisfiable by the arm R1 predicts, and **declined** it: it needs a cut this
file never registered, it has no §5.4 model, and it would make a §5 decision
read the record-level values §4.5 registers as descriptive and gating nothing.
The two readings above are therefore named for the explanations they make
available, not for propositions this rule establishes; §4.5's X6 is registered
against the anticipated misderivations for exactly this reason — "diagnosed
rather than assumed away by S5" (§4.5) — and no §5 decision reads it.
**CONFIRMED therefore means the placement pattern with clean labels, an intact
class 4 and arm E not reading LOW on class 3; it does not mean the author
understood the thresholds, and this file does not claim it does.**

That third row is why §5.3 (i)'s confirmation rule reads S1 and not only the
primary: **H ⊆ raw by construction**, so a class can lose H-coverage entirely
while every raw record still sits on 40 and 70 — and the registered
proposition R1 is about where the records *are*.

### 4.7 What is reported, and how

`RESULTS.json` carries, for every rate, the integer numerator, the integer
denominator, the float point estimate, and both bounds, arm by arm — so every
published decimal is recomputable from integers. It carries the ITT primary and
its sensitivity bound, the S1 placement rate and the S11 per-protocol rate side
by side for every arm and class, each labelled by which denominator it is over,
and it carries **the §5.3 decision-table row number and name** as a first-class
member rather than as prose. It also carries, under `schedule.utcDay`, §2.8's
one-UTC-calendar-day property as **computed** from the slots' own retained
stamps: the observed date set, the count of slots that carried no readable
pair, and the two flags `crossedMidnight` and `oneDayEstablished`. No rate, no
interval, no level and no decision-table row reads any of them.
`RATES.md` is the scorer's rendering of the rate
tables; `CENSUS.md` is the scorer's rendering of §4.5; `ANALYSIS.md` leads with
the five arms' per-class rates, the five `rho_X`, the §5 verdict table and the
decision-table row, and applies §5's rules without adjusting them.
`ANALYSIS.md` also reports, without a verdict: arm A against Study 011's
published rates and census (drift, §2.1, under §2.1's numeric rule and no
other), the realised call-order transition census against §2.8's registered
counts, and the recaptured golden against 011's (§3.2).

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

The rule applies unchanged to the **primary ITT rate** (§4.2, denominator N),
to the **S1 raw-placement rate** (§4.6, denominator N), and to the
**per-protocol rate** (S11, denominator `V_X`). Every level verdict in this
file names which of the three it is a verdict on.

The two cuts are symmetric about 0.5 and, at n = 30, land at: HIGH iff
`k ≥ 27` (the arm missed at most 3 of 30), LOW iff `k ≤ 3` (the arm reached the
class at most 3 times of 30). MID is everything between, and MID is a real
outcome that gets published as MID.

**[D-2]** These cuts are this study's, not Study 011's. 011's LIGHT cut of
`L ≥ 0.80` lands at `k ≥ 29` at n = 30 — one miss allowed in thirty — so a
single stray miss in a control arm would still read as an inconclusive result,
and at the N = 25 alternative it needs a perfect arm outright (`k = 24` gives
`L = 0.7965`). The operating characteristics in §5.4 are why 0.70 and 0.30 were
chosen instead, and they are stated so the review can move them before the data
rather than a reader after it. 011's tier cuts are still computed and
published, as S9.

The cuts are stated **on bounds, not on observed coverage**, so that a
denominator carrying more misses faces a boundary that already carries them.
That is Study 011 §5's own correction, and it is why unequal per-protocol
denominators (§2.8) do not silently move a registered threshold. Two floors are
registered rather than one:

- **the primary and S1 have no denominator floor**, because ITT fixes their
  denominator at N = 30 for every arm and every class; what governs them
  instead is §2.8's completeness rule — an incomplete batch returns no verdict
  at all;
- **the per-protocol rate keeps the `V_X` floor**: below `V_X` = 11 the HIGH
  level is unreachable (a perfect arm is bounded below at 0.6915 at V = 10 and
  0.7151 at V = 11; 11 is the smallest denominator at which a perfect arm reads
  HIGH under this cut), so such an arm's six S11 verdicts are
  `UNRESOLVED-BY-DESIGN` rather than a table of MIDs a reader might mistake for
  a measurement.

### 5.2 The contrast verdict, per arm per class

Against arm A, in the same batch, on the **primary ITT rate**:

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

**The same rule, computed on S1, is the PLACEMENT contrast**, and it is a
distinct registered verdict rather than a gloss on the first:

| condition (levels on the **S1 raw** rate) | placement contrast |
| --- | --- |
| level(A, S1) = HIGH and level(X, S1) = LOW | **PLACEMENT-COLLAPSE** |
| level(A, S1) = HIGH and level(X, S1) = HIGH | **PLACEMENT-TRACKING** |
| otherwise | **PLACEMENT-INDETERMINATE** |

Because `H(r) ⊆ A(r)` for every run, `k_H ≤ k_raw` always, so
**PLACEMENT-COLLAPSE implies COLLAPSE on the same class** and the converse
fails exactly in the case §4.6's table calls a *label collapse*. Both verdicts
are published for all 24 arm×class contrasts; §5.3 (i) says which one confirms
R1 and which one does not.

**A second, weaker contrast is reported beside the first and never substituted
for it [D-17].** The level-gated rule above discards information: a class where
arm E reads LOW (`k = 3`, `U = 0.2653`) while arm A reads MID (say `k = 26`,
`L = 0.6928`) is published as INDETERMINATE even though the two exact intervals
are disjoint by a wide margin in the predicted direction — and §5.4's joint
arithmetic makes that a live shape for a partial baseline, not a corner
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

**The confirmation rule reads PLACEMENT, not labelled coverage, and round 2 is
why.** The primary endpoint counts runs in which a *correctly labelled* record
fell inside a class. R1 is a proposition about **where the author puts
records**. Those come apart in one direction and it is the direction that
matters: because `H(r) ⊆ A(r)`, an arm E that still places records exactly on
40 and 70 but mislabels them loses H-coverage entirely while the hugging R1
predicts would disappear is **still there**. Under an earlier draft that
pattern read as CONFIRMED. It is not confirmation of R1; it is a labelling
failure, and §4.6's table names it as one.

So, over the four narrow numeric classes 0, 1, 2 and 5, and **only after the
gates of the decision table below**:

| pattern | reading | published as |
| --- | --- | --- |
| **PLACEMENT-COLLAPSE on ≥ 3 of 4, with arm E's S5 labels at the ceiling (§4.6) and arm E not reading LOW on class 3** | R1 **confirmed for this instance** | CONFIRMED |
| E reads HIGH on the primary on **≥ 3 of 4** | the predicted collapse did not occur | **R1-UNSUPPORTED** |
| COLLAPSE on ≥ 3 of 4 **without** placement collapse on ≥ 3 | the records are still at the boundary and the labels failed | **LABEL-COLLAPSE-ONLY** |
| every other pattern | neither | **INDETERMINATE** |

> **Confirmation, registered [D-10]:** R1 is **confirmed for this instance** —
> in the sense §5.5 and §9 bound: one denaming, one policy family, one model,
> one day — iff **arm E's S1 placement level is LOW with arm A's HIGH on three
> or more of the four narrow numeric classes**, **and** arm E's S5 labels are
> at the ceiling (§4.6, round 3 finding 9 — |Q| = 0 among its accepted
> records), **and** the B/C control gate of (iii) holds, **and** class 4 does
> not collapse in arm E, **and** arm E does not read **LOW** on class 3 (round
> 9, finding 2; stated on arm E's own level rather than on a contrast against
> arm A, round 10, finding 3 — the interior review band, whose members are
> scored between the two thresholds and so cannot be covered by a record the
> mirror decides before it reads `riskScore`, and the only class this conjunct
> could be stated on, since 0, 1, 2 and 5 are the four the prediction says will
> collapse and class 4 has no numeric content; §4.6 registers that it
> establishes no comprehension). Nothing less confirms it, and the five
> conditions are conjunctive.

> **Non-support, registered [D-10]:** if arm E's primary level verdict is
> **HIGH for three or more of the four narrow numeric classes**, the collapse
> R1 predicted **did not occur**, and R1 is published as **UNSUPPORTED** with
> the same prominence as the claim — in `ANALYSIS.md`'s headline, in this
> study's README, in the venue `CLAIM.md` records, and as a correction banner
> at the head of
> `studies/011-authorship-coverage-rates/DIVERSITY.md`. It is stated as a
> correction, not as a nuance. What is withdrawn is **R1**; the census's
> descriptive sentence about its own corpus stands regardless, and §8 says so.

**Why the outcome is called UNSUPPORTED and not "R1 is wrong", registered
before the data so it cannot be read as softening afterwards.** R1 is a
*causal* claim: the hugging is caused by the text naming 40 and 70. An arm E
that maintains coverage refutes R1's prediction, and that is all it does
directly. It is **compatible with contamination**: the policy family's clause
wording, country codes and outcome vocabulary have been public in this
repository since 2026-08-06, and a snapshot that has seen the corpus can
reproduce this policy's boundaries without being told them and without deriving
them. [D-16] removes the one *textual* pointer — no arm names a study — but no
design in this repository can remove residual memorization from a public
corpus. So:

- **R1-UNSUPPORTED is unconditional** as a verdict and is published as one. The
  prediction failed; the study's own claim does not survive its own test.
- **The positive counter-thesis is not claimed.** "The author derives
  boundaries rather than copying them" is one explanation of maintained
  coverage; "the author recognises this policy family and reproduces its
  boundaries" is another; and **this design cannot separate them.** Any
  write-up asserting the first is a claim this study did not earn, and §8's
  correction text says so in the same paragraph as the retraction.
- The registered evidence reported beside the verdict, changing no verdict:
  **§4.5's X3 near-edge tables and X2 buckets.** Exact clustering on 40 and 70
  in arm E is consistent with derive-then-hug **and** with memorization and
  separates neither; **dispersion** — mass in the `0.01 < d ≤ 1` buckets, or at
  X6's sentinel values — is consistent with neither and is the one observation
  that would point at derivation. It is reported as a pointer and never as a
  verdict.

**INDETERMINATE is a real outcome.** Two COLLAPSE and two MID is INDETERMINATE.
**All four MID is INDETERMINATE** — and §5.4 records that at a true coverage of
0.30 this rule returns MID 99.1% of the time, so an all-MID arm E is exactly
what any *partial* anchoring effect looks like here. It is published as
INDETERMINATE, R1 is recorded as **neither confirmed nor unsupported**, and no
post-hoc pattern is substituted for the registered one.

§4.6's S5 separates a placement collapse whose accepted records are all
correctly labelled from one whose labels failed — and §4.6 records what that
does and does not establish, because a record decided by a sanctions hit or an
embargoed registration is labelled correctly without either threshold being
read; §4.5's X6 census is what flags an anticipated wrong derivation; and
§4.5's X2/X3 census is what distinguishes "no anchor" from "an anchor derived
and then hugged".

**(ii) D vs A — coverage follows the numbers.** Predicted: **TRACKING on all
six classes under D's own family**, and, under the S10 old-edge cross-scoring
against arm A's family:

| old-edge class, arm D | predicted | why |
| --- | --- | --- |
| 0 (exactly 70) | LOW | D's records hug 72 |
| 1 ([70, 71)) | LOW | same |
| 2 (P ∧ [40, 41)) | LOW | D's records hug 45 |
| 3 ([40, 70)) | **HIGH — not a falsifier** | arm A's 30-wide band. Most of D's `[45, 72)` band lies inside it, so a diffuse D covers it easily — but **not "by construction"**: the sub-band `[70, 72)` is inside D's class 3 and outside A's, so a D that placed every record there would read LOW here. The earlier draft's "by construction" is withdrawn |
| 4 (SY) | **HIGH — not a falsifier** | no numeric content |
| 5 (P ∧ [39, 40)) | LOW | D's below-threshold hugs are at 44 |

**The two keyings ask two different questions, and the asymmetry is
registered rather than left to be noticed.** D's new-keyed levels are its
primary ITT levels — correctly-labelled coverage under its own (45, 72)
family, because TRACKING means doing the task under the policy the arm states.
Its old-keyed levels are S10's, and S10 is placement: class membership under
arm A's predicates with no label filter. The second outcome's claim is that
the model "reproduced 40 and 70 in the face of a text that says 45 and 72",
which is a claim about where records were placed and not about how they were
labelled; and the first outcome's exclusion — old-keyed not HIGH-patterned —
exists to catch a D that reached **both** threshold pairs, which it cannot do
if a record placed at 70 and labelled by the old rule is quarantined before
arm A's predicates are read. Under D's mirror that quarantine is not
hypothetical: an author labelling by (40, 70) mislabels every record in old
class 2 and every non-personal-data record at 70, so a label-filtered S10 was
blind in exactly the case the second outcome names and blind in exactly the
case the first outcome's exclusion names.

**Three outcomes are registered for arm D, not two.**

> **The second outcome, registered:** if D's **new-keyed** verdicts are LOW on
> the narrow numeric classes while its **old-keyed** verdicts are HIGH, the
> model reproduced 40 and 70 in the face of a text that says 45 and 72. That is
> not a failure of the anchoring hypothesis. It is published as
> **OLD-EDGE-PREFERENCE**, and it is registered with **two** explanations, not
> one:
>
> 1. **contamination** — this policy family has been public in this repository
>    since Study 010 merged (2026-08-06), and a snapshot that has seen it can
>    reproduce 40 and 70 against a text that says otherwise;
> 2. **round-number salience** — 40 and 70 are decade-round and 45 and 72 are
>    not, so an author drawn to round values rather than to the stated literal
>    produces the same table, having seen nothing. [D-18] registers this as the
>    cost of the (45, 72) pair and (50, 80) as the salience-matched
>    alternative.
>
> **Nothing in this study separates them**, the earlier draft's name
> ("contamination signal") asserted the first, and the name is changed to one
> that asserts neither. What would separate them is an arm at a
> non-round pair with the *same* roundness profile as (45, 72) but no public
> history — which is a different study.
>
> **The outcome names and the count, registered** (round 3, finding 10,
> dispositioned — the scorer needed names and a threshold this section had
> not spelled): the predicted first outcome is published as
> **COVERAGE-FOLLOWS-THE-NUMBERS** (new-keyed HIGH on three or more of the
> four narrow numeric classes, old-keyed not HIGH-patterned); LOW-pattern
> counts reuse the registered pattern minimum of **three of the four**
> narrow numeric classes, the same cut §5.3 (i) registers for arm E rather
> than a second number; and a D whose new-keyed and old-keyed levels
> satisfy none of the three named outcomes is published as
> **D-INDETERMINATE**, an outcome and not a blank.

> **The third outcome, registered:** if D's **new-keyed** verdicts are LOW on
> the narrow numeric classes **and its old-keyed verdicts are LOW too**, that
> is neither tracking nor old-edge preference. It is a **general degradation** —
> the author placed records at neither threshold pair — and it is **published as
> one**, not read as evidence for or against R1. §4.5's X2 and X3 census under
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
classes and arm C reads TRACKING on at least five of its six**. This is the
**control gate**, it is a gate and not a caution, and the decision table below
places it above every reading of arm E. Below it, the study publishes arm E's
verdicts *and* says the controls did not hold: if B falls short, E's collapse
could be paraphrase-driven; if C falls short, it could be order-driven; either
way the weaker reading is what gets claimed.

What that dependency costs is stated before the data rather than discovered
after it, and round 2 found the earlier statement of the cost was computed for
the wrong rule. It is a joint condition over twelve **contrast** verdicts, and
every TRACKING verdict requires **arm A HIGH on that class as well** — so the
gate is a statement about eighteen level verdicts, not twelve. §5.4 records
that at a true per-class p of 0.95 the gate passes **0.7658** of the time at
N = 30 and **0.4031** at N = 25. The earlier draft cited `q¹² = 0.1957` as
"P(all twelve read HIGH)", which omits arm A's requirement; the actual
all-twelve-TRACKING probability is `q¹⁸`, **0.3235** at N = 30 and **0.0866**
at N = 25. The five-of-six form is chosen for exactly that reason: requiring
all twelve would make the dependency fail two times in three under a *true null
effect in both control arms*, and a dependency that usually fails is not a
control. That the five-of-six form *itself* fails three times in five at N = 25
is the round-2 argument that moved [D-1] to N = 30.

Round 10, finding 4: those two gate figures assume an independence across
classes that §2.3's own nesting makes unavailable, and at these N a
**tolerance** rule is the kind that gets *harder* when classes move together —
a nested pair going below HIGH spends two of the six at once. Under the
containment-respecting companion §5.4 now publishes beside them, the gate is
**0.6702** at N = 30 and **0.4010** at N = 25. The argument is unchanged in both
halves: 0.4010 still fails more often than it passes, 0.6702 still does not, and
the all-twelve form is worse again.

**(iv) Class 4, the embargo-membership class, in every arm.** Predicted:
**TRACKING in all four contrasts.** It is the only class whose predicate names
no numeric boundary, and Study 011's census found it the best-witnessed class
in the corpus (26 distinct probes, no probe reaching more than 11 of 49 runs).

> **Falsification, registered:** if class 4 collapses in arm E, the effect is
> not literal-specific — something about the denamed text degraded authoring
> generally — and every other reading of arm E in this study is withdrawn in
> favour of that one. The decision table below gives that rule its precedence
> explicitly rather than leaving "withdrawn in favour of" to a reader.

#### The decision table, ordered, exhaustive, and total

Round 2's finding: the rules above were individually crisp and jointly
under-determined. The E table did not incorporate the control gate; the class-4
rule claimed to override "every other reading" with no stated precedence; arm
D's rule said "LOW on the narrow classes" with no count and named no outcome
for the mixed case; and the drift rule ran on "several" and "far below". A
motivated analyst could have argued more than one outcome from the same
integers. **This is the whole rule.** It is evaluated top to bottom, the first
row whose condition holds is the outcome, and the last row always holds.

Notation, all computed by the scorer from the integers it just wrote: `nP` =
the number of the four narrow numeric classes on which arm E reads
PLACEMENT-COLLAPSE (§5.2); `nC` = the number on which it reads COLLAPSE on the
primary; `nH` = the number on which arm E's primary level is HIGH; `gate` = arm
B TRACKING on ≥ 5 of 6 **and** arm C TRACKING on ≥ 5 of 6.

| # | condition | outcome for R1 | published as |
| --- | --- | --- | --- |
| 1 | the batch is incomplete (§2.8), or any arm holds fewer than 30 scheduled slots, or a slot manifest or the ledger chain fails to verify (§2.9) | not adjudicated | **UNRESOLVED-BY-DESIGN** — descriptive publication only, no contrast reported |
| 2 | arm E reads COLLAPSE on **class 4** | not adjudicated | **E-DEGRADED-GENERALLY** — the denamed text degraded authoring generally; every other reading of arm E is withdrawn |
| 3 | `gate` is false | not adjudicated | **CONTROLS-FAILED** — arm E's verdicts published in full, with the weaker reading named: paraphrase-driven if B fell short, order-driven if C |
| 4 | `nH ≥ 3` | **unsupported** | **R1-UNSUPPORTED** — §8's correction fires |
| 5 | `nP ≥ 3` **and arm E's S5 labels are at the ceiling (§4.6) and arm E does not read LOW on class 3** | **confirmed for this instance** | **CONFIRMED** |
| 6 | `nC ≥ 3` and `nP < 3` | not adjudicated | **LABEL-COLLAPSE-ONLY** — the records are still at the boundary; the labels are not |
| 7 | *(else)* | neither confirmed nor unsupported | **INDETERMINATE** |

Registered notes on the table, so its edges are not left to be discovered:

- **Rows 4 and 5 cannot both hold.** `k_H ≤ k_raw` per class, so a class with
  E's primary HIGH has E's placement HIGH too and cannot be a placement
  collapse; with four classes, `nH ≥ 3` and `nP ≥ 3` are incompatible. The
  order is stated anyway, because a decision table with an unreachable
  ambiguity is still a decision table with an ambiguity.
- **Row 5 is a conjunction and §4.6's reading is not** (round 9, finding 2). A
  placement collapse whose labels are at the ceiling reads §4.6's *first* row —
  the reading that confirms — and still falls through to row 7 if arm E reads
  LOW on class 3. The reading is published beside the row as it always is,
  and row 7 records **which conjunct refused**, because a gloss saying the
  reading did not confirm would state a rule smaller than the one that ran.
- **The fifth conjunct reads a §5.1 level and not a §5.2 contrast** (round 10,
  finding 3). The class-3 condition is a verdict on arm E alone, so it holds
  arm E to its own coverage whatever arm A did on that class; the round-9
  contrast form was satisfied vacuously whenever arm A was not HIGH there,
  which is the case §4.6 registers it to refuse.
- **Rows 1–3 are gates and produce no R1 verdict of any kind**, in either
  direction. A study that would publish CONFIRMED through a failed control but
  not R1-UNSUPPORTED through one would be a study with a preferred answer.
- **Every row is published with the full verdict tables beside it**, including
  the rows that adjudicate nothing. `UNRESOLVED-BY-DESIGN`, `CONTROLS-FAILED`
  and `E-DEGRADED-GENERALLY` are outcomes, not failures to report.
- **The scorer computes the row**, writes its number and its name into
  `RESULTS.json`, and a harness test parses this table out of this file and
  diffs it against the scorer's own. No operator selects a row.

### 5.4 What N = 30 can and cannot resolve

Computed with this study's own interval code, before any data, and asserted by
a harness test so the rule's power is not left to a reader's intuition. Under
the §5.1 cuts at n = 30 (HIGH iff `k ≥ 27`, LOW iff `k ≤ 3`), the probability
the rule assigns each level to a class whose *true* coverage is p:

| true p | P(HIGH) | P(LOW) | P(MID) |
| --- | --- | --- | --- |
| 1.00 | 1.0000 | 0.0000 | 0.0000 |
| 0.98 | 0.9971 | 0.0000 | 0.0029 |
| 0.95 | 0.9392 | 0.0000 | 0.0608 |
| 0.90 | 0.6474 | 0.0000 | 0.3526 |
| 0.80 | 0.1227 | 0.0000 | 0.8773 |
| 0.50 | 0.0000 | 0.0000 | 1.0000 |
| 0.30 | 0.0000 | 0.0093 | 0.9907 |
| 0.20 | 0.0000 | 0.1227 | 0.8773 |
| 0.10 | 0.0000 | 0.6474 | 0.3526 |
| 0.05 | 0.0000 | 0.9392 | 0.0608 |
| 0.02 | 0.0000 | 0.9971 | 0.0029 |
| 0.00 | 0.0000 | 1.0000 | 0.0000 |

**Every `0.0000` in this table is a rounded figure and not a zero, except in
the two degenerate rows, where four of them are exact.** P(HIGH) at p = 0.30 is
about 1.1 × 10⁻¹¹ and P(LOW) at p = 0.95 is smaller still; they are printed to
four places because every other number here is, and no rule in §5 reads them.
The four exceptions are arithmetic and not rounding: at p = 1.00 no outcome has
`k ≤ 3` and at p = 0.00 none has `k ≥ 27`, so P(LOW) and P(MID) in the first
row and P(HIGH) and P(MID) in the last are exactly zero. The same is true of
the `0.0000` lower bounds at `k = 0` in §4.3 and §4.4, which are exact —
Clopper–Pearson puts no lower bound above zero on a count of zero — and of the
`1.0000` upper bounds at `k = n`, which are exactly one. Outside those
degenerate cells, nothing in this study asserts that any of these events is
impossible.

#### The joint figures, and exactly what they assume

The study's own headline is a joint statement, so the joint arithmetic is
registered beside the marginal. **These are conditional-independence scenarios,
not bounds, and round 2 corrected an earlier draft that called them "lower
bounds" and independence "the worst case".** Both claims were wrong:
independence is neither an upper nor a lower bound on a joint probability, and
for positively dependent classes — which is what Study 011's corpus suggests,
since its runs covered all six classes together in every valid run — the true
joint probability of a **conjunction** is *higher* than the independence
product, not lower. **That direction is a property of the conjunctions and not
of this section, and an earlier form of this sentence claimed it for both kinds
of rule (round 10, finding 4).** It holds for "all six HIGH", "all four narrow
HIGH", "all twelve TRACKING" and "all four narrow COLLAPSE". It is **false for
the five-of-six control gate and for the three-of-four patterns `nP ≥ 3` and
`nH ≥ 3`**, where dependence makes a *tolerance* harder rather than easier:
classes that move together fail together, and one nested pair going below HIGH
spends two of the six at once — the whole of what five-of-six allows. Under the
containment-respecting companion below, the gate falls from 0.7658 to **0.6702**
at N = 30 and row 5's coverage-side quantity from 0.7359 to **0.6253**, while
all six HIGH *rises* from 0.6865 to 0.7782. **The direction is a property of a
rule at a `q`, not of a rule**: at N = 20, where `q` is 0.7358 and five-of-six
is in practice a conjunction — only an all-four-group pattern, or one missing a
one-class group, can reach five — the gate *rises* instead, 0.0557 to 0.1078.
The falls are at N = 25 and N = 30, which are the two N's [D-1] compares, and
`nH ≥ 3` falls at all three. The Fréchet lower bound is what an
actual worst case looks like, and it is given below beside each product so the
gap is visible.

**Every independence layer used, named:**

1. **across classes within an arm** — the six per-class indicators of one arm
   are treated as independent. Study 011's corpus contradicts this directly,
   and on two of the six classes it is not contradicted but **unavailable**
   (round 10, finding 4). §2.3 registers that the classes are **not disjoint**:
   *class 0 nests in class 1 and class 2 nests in class 3*, as predicates over
   one record. Correctness is a property of the **record** and not of the class
   (§4.1 defines `H(r)` per record; §4.2 reads a class through it), so a record
   that witnesses class 0 in a run witnesses class 1 in that same run and
   carries the same correctness bit. `Y₀ ≤ Y₁` and `Y₂ ≤ Y₃` slot by slot, on
   the primary endpoint and on S1 alike. Independence across such a pair would
   need `P(Y₀ = 1, Y₁ = 0) = p₀(1 − p₁) = 0`, so `p₀ = 0` or `p₁ = 1`: **there
   are no nondegenerate marginals at which it is available**, and no choice of
   `p` rescues it. And **two indicators with the same mean, one never exceeding
   the other, are equal almost surely** — layer 4's sentence, which holds here
   for the same reason and which this file applied to `H ⊆ raw` for nine rounds
   without noticing it also applies to `class 0 ⊆ class 1`. At this scenario's
   equal `0.95` marginals, therefore, each nested pair is a *single* indicator
   and arms A, B and C have **four** free class indicators, not six. Every
   figure computed under this layer is published below beside a
   containment-respecting companion and labelled as the approximation it is;
2. **across arms** — arm A's, B's, C's and E's class indicators are treated as
   independent of one another. The interleaved schedule and any provider-side
   state (§7) work against it;
3. **across slots within a class** — the Clopper–Pearson interval itself
   assumes constant-p independent Bernoulli slots (§4.3);
4. **between the primary and the S1 placement endpoint**, wherever a figure
   below combines them. These are *not* independent — `H ⊆ raw` — and any such
   figure is marked: the row-5 joint below is the one, and the paragraph after
   that table says what the combination assumes.

Under layers 1–3, at `q = P(HIGH | p)` from the table above:

| true p | P(HIGH), one class | P(all **four** narrow HIGH) | P(all **six** HIGH) | Fréchet lower bound on all six | P(all **twelve** TRACKING, B and C) |
| --- | --- | --- | --- | --- | --- |
| 1.00 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 0.98 | 0.9971 | 0.9885 | 0.9828 | 0.9826 | 0.9492 |
| 0.95 | 0.9392 | 0.7782 | 0.6865 | 0.6354 | 0.3235 |

**The same three rows with layer 1 repaired**, since the layer as stated is not
available: each nested pair is one indicator, the four groups `{0,1}`, `{2,3}`,
`{4}` and `{5}` are independent within an arm and across arms, and layer 3 is
untouched. This is a **scenario and not a bound** exactly as the table above is
— the residual independence among the four groups is still an assumption, and
one coherent coupling in the other direction, the three arms' groups
comonotone, puts the control gate at 0.8789 rather than 0.6702 at N = 30:

| true p | P(HIGH), one class | P(all **four** narrow HIGH) | P(all **six** HIGH) | sharp Fréchet floor on all six | P(all **twelve** TRACKING, B and C) |
| --- | --- | --- | --- | --- | --- |
| 1.00 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 0.98 | 0.9971 | 0.9913 | 0.9885 | 0.9884 | 0.9658 |
| 0.95 | 0.9392 | 0.8285 | 0.7782 | 0.7569 | 0.4713 |

The exponents are the count of *indicators*, not of classes: all six HIGH is
`q⁴`, all four narrow HIGH is `q³` — classes 0, 1, 2 and 5 are the groups
`{0,1}`, `{2,3}` and `{5}` — and all twelve TRACKING is `q¹²`, three arms at
four groups each. **`q⁴ = 0.7782` therefore appears in both tables meaning two
different things**: the independence reading of all four narrow classes above,
and the containment-respecting reading of all six here.

**The first table's Fréchet column counts the wrong number of events, and its
1.00 top is not a top (round 10, finding 4).** `max(0, 6q − 5)` is what *six
free* marginals imply; six classes are four indicators, so the sharp floor on
the all-six conjunction is **`max(0, 4q − 3)` = 0.7569** at N = 30 and **0.4916**
at N = 25, against the 0.6354 the table above prints and the 0.2374 the
withdrawn N = 25 sentence gave beside it, and the floor on the
all-four-narrow conjunction is `max(0, 3q − 2)` = **0.8177** and **0.6187**. The
top is capped by the marginals alone at `min_i q_i = q` — **0.9392** at N = 30
and **0.8729** at N = 25 — because no conjunction exceeds its smallest
marginal, whatever the dependence. So the honest statement at p = 0.95 and
N = 30 is **"between 0.757 and 0.939, and 0.778 under the containment-respecting
scenario"**, and at N = 25 **"between 0.492 and 0.873, and 0.581"**; the
withdrawn form read "between 0.64 and 1.00, and 0.69 under independence" and
both of its ends were loose.

**Cells of the first table lie below their own floors and are attainable by no
population with these marginals — two of them in the `p = 0.95` row and three in
the `p = 0.98` row.** At p = 0.95, `q⁶ = 0.6865` sits under
0.7569 and `q⁴ = 0.7782` under 0.8177 (at N = 25, 0.4424 under 0.4916 and
0.5806 under 0.6187); in the p = 0.98 row the same two cells, 0.9828 and
0.9885, sit under 0.9884 and 0.9913, and there the all-twelve cell 0.9492 sits
under its own `max(0, 12q − 11)` = 0.9653 as well. At p = 0.95 the all-twelve
cell does **not**: `q¹⁸ = 0.3235` is above its 0.2707 floor. At N = 20 and
p = 0.95 the floors are 0 and 0.2075 and every cell is feasible. **The model is
unavailable everywhere; the numbers are impossible only where this paragraph
says they are**, which is the whole of the claim and more than a reader could
have got from "these are scenarios". Nothing in §5.3 reads an infeasible cell,
and they stay printed because §5.4's convention is to keep a superseded figure
beside its correction rather than to replace it silently.

**P(all twelve TRACKING) is `q¹⁸`, not `q¹²`.** A TRACKING verdict requires
arm A HIGH on that class as well as the control arm, so all twelve TRACKING is
eighteen level verdicts, not twelve. `q¹²` at p = 0.95 is 0.4713 at N = 30 and
0.1957 at N = 25; the correct `q¹⁸` figures are **0.3235** and **0.0866**.

**The companion table's all-twelve cell is `q¹²` again, and it is not that
`q¹²`.** The earlier draft reached twelve by dropping arm A's six verdicts from
the eighteen; the companion reaches twelve by collapsing each of the three
arms' six classes to four indicators, arm A's included. The two agree to every
digit — 0.4713 at N = 30, 0.1957 at N = 25 — and are different quantities. That
`18 − 6` and `3 × 4` are both twelve is an accident of these numbers and not a
shared derivation, and this paragraph exists so a later reader does not read the
companion as the rejected draft returning.

#### Operating characteristics for the rules this file actually registers

Round 2's finding, and the one that moved [D-1]: the earlier draft published
power for *stricter proxies* of its own rules — all-four COLLAPSE where the
rule says three-of-four, `q¹²` where the gate says five-of-six over eighteen
verdicts — and then reasoned about N from those numbers. Recomputed for the
registered rules, under the scenario the prediction describes (`p = 0.95` on
every class of arms A, B and C and on E's classes 3 and 4; `p = 0.05` on arm
E's four narrow numeric classes). The first eight rows are under independence
layers 1–3 as published; the five `under containment` rows below them are the
same rules with layer 1 repaired on the two nested pairs (round 10, finding 4):

| registered rule | where | N = 20 | **N = 25** | **N = 30** |
| --- | --- | --- | --- | --- |
| per-class COLLAPSE | §5.2 | 0.5415 | 0.7619 | 0.8822 |
| all four narrow COLLAPSE | — | 0.0860 | 0.3370 | 0.6056 |
| **`nP ≥ 3` — row 5's coverage pattern (S5 is outside this model)** | §5.3 (i) | 0.3771 | 0.7583 | **0.9292** |
| **the B/C control gate (row 3 passes)** | §5.3 (iii) | 0.0557 | 0.4031 | **0.7658** |
| all twelve TRACKING (`q¹⁸`) | §5.3 (iii) | 0.0040 | 0.0866 | 0.3235 |
| **CONFIRMED *and* the gate holds — the coverage-side joint quantity** | table row 5 | 0.0364 | 0.3536 | **0.7359** |
| `nH ≥ 3` when R1 is false and E truly sits at 0.95 — **the marginal pattern alone** | §5.3 (i) | 0.7142 | 0.9187 | **0.9796** |
| **row 4 reached — `nH ≥ 3` *and* class 4 does not collapse *and* the B/C gate holds: the power to publish R1-UNSUPPORTED** | table row 4 | 0.0398 | 0.3704 | **0.7502** |
| under containment — `nP ≥ 3`, row 5's coverage pattern | §5.3 (i) | 0.4276 | 0.7188 | **0.8699** |
| under containment — the B/C control gate | §5.3 (iii) | 0.1078 | 0.4010 | **0.6702** |
| under containment — the coverage-side CONFIRMED-and-gate quantity | table row 5 | 0.0714 | 0.3408 | **0.6253** |
| under containment — `nH ≥ 3`, the marginal pattern alone | §5.3 (i) | 0.6845 | 0.8588 | **0.9358** |
| under containment — row 4 reached, the power to publish R1-UNSUPPORTED | table row 4 | 0.0738 | 0.3444 | **0.6272** |

**The five `under containment` rows are the same five rules under the repaired
layer 1** (round 10, finding 4), and they are the rows that carry N: every one
of them is a *tolerance* — five of six, three of four — and at **N = 25 and
N = 30** every one of them **falls**, by 0.04 to 0.12 at N = 30. At N = 20 four
of the five rise instead, because at `q = 0.7358` a five-of-six or three-of-four
tolerance is reached almost only by the pattern that satisfies it entirely, and
a conjunction is what containment makes *easier*; `nH ≥ 3` falls at all three N.
The two N's [D-1] compares are the two where the correction costs power. These
rows are a scenario and not a bound, as
the rows above them are. The three rules with no companion row here are the two
conjunctions and the one marginal, which move the other way or not at all:
`per-class COLLAPSE` is one class's marginal and is **unchanged** at
0.5415 / 0.7619 / 0.8822, `all four narrow COLLAPSE` rises to
0.1587 / 0.4424 / **0.6865**, and `all twelve TRACKING` rises to the companion
table's `q¹²`, 0.0252 / 0.1957 / **0.4713**. That the corrected all-four-narrow
COLLAPSE figures are digit-for-digit the *independence* all-six HIGH figures is
arithmetic and not a transcription: under §5.1's cuts `P(LOW | p = 0.05)` and
`P(HIGH | p = 0.95)` are the same number exactly, so the corrected quantity is
`(q·l)³ = q⁶`.

The CONFIRMED-and-gate row and the row-4 row are both computed **jointly over
arm A's six-class pattern** rather than as products of marginals, because the
gate and the collapse condition on the same arm-A HIGH verdicts.

**Row 5 is the one figure in this section that combines the primary and the S1
placement endpoint — layer 4 — and the scenario's own assignment is what makes
reading one pattern twice exact.** The control gate and row 2 are verdicts on
the primary; `nP` is a verdict on S1 (§5.2); the arithmetic above reads arm A's
six-class HIGH pattern once and lets both read it. That is exact under this
scenario because the scenario assigns its `p` **to both endpoints** — the
per-slot probability that the class is reached, labelled or not — and because
`H(r) ⊆ A(r)` holds path by path (§4.1), so the primary's per-slot class
indicator never exceeds S1's. Two indicators with the same mean, one never
exceeding the other, are **equal almost surely**: `k_H = k_raw` on every class,
and a class's primary level and its S1 level are the same verdict. **The
marginal assignment is therefore the joint model**, and layer 4 enters here as
an identity rather than as an independence — there is no joint freedom left for
a separate model to describe. It is not a free assumption. A scenario carrying
a label tax (§4.6's `a_i − c_i > 0`) separates the two endpoints, and the other
extreme — arm A's two HIGH patterns independent of one another — turns
`0.0364 / 0.3536 / 0.7359` into **0.0210 / 0.3057 / 0.7116**. **That extreme is
itself unreachable and is printed to bound the premise's materiality, not as a
candidate model** (round 10, finding 4): `H ⊆ raw` makes the two patterns
pathwise ordered, and independence between pathwise-ordered indicators is
available at no nondegenerate marginals — the same sentence that puts layer 1
beyond reach on the nested class pairs, stated once in layer 1 above and
applying wherever one registered indicator implies another. What the figure
shows is how far row 5 can move if the endpoints separate at all, which is the
only work it is asked to do. Nor is the
substitution one-sided once the endpoints do separate: for arm A it under-reads
the S1 HIGH set, because primary HIGH implies S1 HIGH pointwise, while for arm
E a label tax puts P(E reads S1 LOW) *below* the `P(LOW | p = 0.05)` the
arithmetic uses — the two directions disagree, which is why the premise is
stated here rather than converted into a bound. It is also not a claim about
arm E's labels: equality of the class-level indicators does not entail
`|Q| = 0`, so row 5's S5 conjunct stays outside this model exactly as the
paragraph below says. The `nP ≥ 3` row uses only the first half of this — that
`p` is assigned to S1 as well — and row 4, the gate, both COLLAPSE rows, `nH`
and all-twelve TRACKING read the primary alone.

**The last two rows are one quantity's two halves, and round 3's finding 11 is
that an earlier draft published the first under the second's name.**
`0.7142 / 0.9187 / 0.9796` is the marginal probability that arm E reads HIGH on
three or more of the four narrow numeric classes. It is *not* the power to
reach decision row 4: the table is evaluated top to bottom, row 2 (arm E
collapsing on class 4) and row 3 (the B/C control gate) are decided first, and
R1-UNSUPPORTED is published only through both. Conditional on a complete,
sealed batch (row 1 not firing), and under independence layers 1-3, the power
to publish R1-UNSUPPORTED is **0.0397841 at N = 20, 0.3703584 at N = 25 and
0.7501924 at N = 30** — the marginal times the gate's 0.0557 / 0.4031 / 0.7658,
the class-4 term being `1 − P(LOW | p = 0.95)` and below 10⁻²³ at every N. The
table's row-5 figure carries that term **twice** (round 9, finding 2): §5.3's
row 5 requires arm E not to read LOW on class 3 as well as class 4 not
collapsing, arm E's class 3 sits at `p = 0.95` in the scenario above exactly as
its class 4 does, so the second term has the same magnitude and no figure in the
table moves. It does **not** have the same shape (round 10, finding 3): the
class-3 conjunct is a level verdict on arm E, so it enters as `1 − P(E class 3
LOW)` in *every* arm-A pattern, where the class-4 term is
`1 − P(A HIGH) · P(E class 4 LOW)` and drops out of the pattern in which arm A
is not HIGH on class 4. Row 4 reads neither: the falsification half is
untouched.

**The consequence is registered rather than left to be noticed.** The control
gate binds R1-UNSUPPORTED exactly as it binds CONFIRMED (0.7502 against 0.7359
at N = 30, and 0.6272 against 0.6253 under containment): rows 1-3 produce no R1
verdict *in either direction*, and a study that could publish one adjudication
through a failed control and not the other would be a study with a preferred
answer. N = 30 is retained on that arithmetic — on **both** readings of it, and
the corrected one is the reading that counts — stated honestly, rather than
raised.

**Every CONFIRMED-side figure in this section is a coverage-side quantity**
(round 4, finding 5, dispositioned): §5.4's model has no label-error term, and
row 5's S5 conjunct — arm E's labels at the ceiling — is outside it. The
figures are therefore exact for the coverage pattern and upper bounds for the
confirmatory outcome; the actual probability of CONFIRMED is these numbers
times an unmodeled P(no accepted arm-E record mislabelled), which this file
declines to invent a distribution for. The R1-UNSUPPORTED row is not affected:
row 4 reads coverage alone. Row 5's **fifth** conjunct — arm E not reading LOW
on class 3 (round 9, finding 2; restated on arm E's own level round 10,
finding 3) — is by contrast *inside* this model, entered as
`1 − P(E class 3 LOW)`, which reads arm E alone and therefore applies in every
arm-A pattern rather than in the class-4 term's shape; it is carried in the
arithmetic, it moves no printed figure, and it does not narrow the gap between
these quantities and the confirmatory one, which remains S5.

`harness/score_rates.py::decision_operating_characteristics()` computes every
independence figure in this section with this study's own interval and threshold
code, and `harness/score_rates.py::containment_operating_characteristics()` —
its sibling, not its replacement — computes every `under containment` one from
the same primitives and the registered `NESTED_CLASS_PAIRS`.
`harness/tests/test_verdict_parity.py` diffs the tables above against both, row
by row, pins both sets of numbers, and asserts the infeasibility arithmetic
(`q⁶ < 4q − 3` and `q⁴ < 3q − 2` at N = 25 and N = 30) and the direction facts
rather than transcribing them.
`harness/tests/test_mirror.py` turns §2.3's nesting itself into a computed fact:
over the 280-cell landmark grid, at **every** arm's registered threshold pair,
the ordered pairs of classes whose members are contained in one another are
exactly `{(0,1), (2,3)}`.

Read plainly:

- **The binding quantity is the control gate, and at N = 25 it fails more often
  than it passes.** 0.4031 is the probability that the design's own
  precondition for interpreting arm E holds *when both control arms are
  behaving exactly as predicted*. This file's own criterion — "a dependency
  that usually fails is not a control" — condemns N = 25 by that number. At
  N = 30 the gate passes 0.7658 of the time and the coverage-side CONFIRMED
  quantity — the upper bound §5.4 names, S5 unmodeled — lands 0.7359 of the
  time, against 0.3536 at N = 25. That is the
  argument that moved [D-1]; it is not the marginal 0.8729 → 0.9392, which is
  the comparison an earlier draft made and which understates the difference
  because it does not compound. **Both readings return the same answer, and the
  answer is registered on the corrected one (round 10, finding 4).** Under
  containment the gate is **0.4010** at N = 25 against **0.6702** at N = 30, and
  the coverage-side quantity **0.3408** against **0.6253**: the tolerance rules
  lose about a tenth at N = 30, so the criterion is applied to a smaller number
  than the one that moved [D-1] — and it returns the same verdict, because
  0.4010 still fails more often than it passes and 0.6702 still does not. The
  0.5 line falls between the two N's on either arithmetic. **N = 30 is retained
  on arithmetic that a population can produce**, which is what the incoherent
  layer could not offer.
- **The baseline is comfortable marginally and less comfortable jointly.** At a
  true p of 0.95 — *inside* 011's own published interval, lower bound 0.9275 —
  arm A reads HIGH on all six classes 68.7% of the time under independence and
  at least 63.5% by the Fréchet bound as that bound was printed. Under the
  containment-respecting reading, which is the coherent one, it is **77.8%**,
  with a sharp floor of 75.7% and a cap of 93.9%. Since §5.2 makes
  `level(A) = HIGH` a precondition of any COLLAPSE, **roughly two runs of this
  study in ten** would find at least one falsifier-relevant class with no
  contrast verdict available, **from sampling alone, under zero drift** —
  against roughly *four in ten* at N = 25, where the same quantity is 0.5806.
  Round 10, finding 4 repaired the pairing as well as the model: the withdrawn
  form read "three in ten" against "four in ten" and its two halves were
  different quantities at different N — `1 − q⁶` at N = 30 against `1 − q⁴` at
  N = 25 — where 0.2218 and 0.4194 are one quantity read twice. §2.1 registers
  the consequence: such a class is reported as an unresolved baseline, not as
  drift.
- **A real collapse is caught.** At a true p of 0.05 the rule says LOW 93.9% of
  the time, and at 0.02, 99.7%. The prediction is that E's numeric classes go
  to roughly zero, and that is the regime the rule resolves.
- **A partial collapse is not.** At a true p of 0.30 the rule says MID
  essentially always (99.1%), and at 0.10 it says LOW only 64.7% of the time.
  **N = 30 separates "still reliably covered" from "essentially never covered"
  and resolves nothing in between**, and every MID in the published table means
  exactly that. Stated as the smallest real effect this design cannot see:
  **any anchoring effect that leaves coverage above roughly one run in five is
  invisible to this study.** A drop from 1.00 to 0.30 reads MID 99% of the
  time; a drop to 0.10 reads LOW only 65% of the time; only a fall below about
  0.08 is called four times in five (P(LOW) = 0.7842 at p = 0.08, 0.8450 at
  0.07, 0.8974 at 0.06). §9 repeats it in those words.
- **Multiplicity, where it bites and where it does not.** The 30 primary level
  verdicts, the 30 S1 placement verdicts, the 30 per-protocol verdicts, the 24
  contrast verdicts, the 24 placement contrasts and the up-to-30 S10 verdicts
  (§4) are all marginal and no simultaneous claim is made over any of them.
  Where it matters is the *pattern* thresholds of §5.3 — "three or more of
  four", the control gate — and there the arithmetic is in the table above
  rather than assumed. The predicted effect is 1.00 → ~0, which is not a regime
  where multiplicity is the binding uncertainty; the binding uncertainty is
  §9's, and this bullet exists so nobody mistakes one for the other.

#### Why 30, and not 20, 25 or 50

The exact bounds, for a perfect arm: n = 11 → [0.7151, 1] — **the smallest
denominator at which a perfect arm reads HIGH under the 0.70 cut**;
n = 16 → [0.7941, 1] (HIGH, and an earlier draft's claim that it was below the
cut was wrong); n = 17 → [0.8049, 1]; n = 20 → [0.8316, 1]; n = 25 →
[0.8628, 1]; n = 30 → [0.8843, 1]; n = 50 → [0.9289, 1]. A half-covered class
carries ±0.228 at n = 20, ±0.205 at 25, ±0.187 at 30, ±0.145 at 50. At n = 20
the HIGH cut lands at `k ≥ 19` (one miss allowed), at n = 25 at `k ≥ 23` (two),
at n = 30 at `k ≥ 27` (three), at n = 50 at `k ≥ 42` (eight).

**The budget, with the probe calls counted.** Each N costs `5N` authoring calls
plus 2 golden probes and 1 isolation-negative probe, and Study 011's observed
mean was 42.08 seconds per call:

| N | authoring | total calls | sequential wall clock |
| --- | --- | --- | --- |
| 20 | 100 | 103 | ~72 min |
| 25 | 125 | 128 | ~90 min |
| **30** | **150** | **153** | **~107 min** |
| 50 | 250 | 253 | ~177 min |

All four are inside the one-day rule; the earlier draft's "150 calls and about
105 minutes" for N = 30 omitted the three probes, and its "250 calls and about
three hours" for N = 50 omitted them too.

**[D-1] N = 30 is the proposal**, on the control gate (0.7658 against 0.4031)
and the coverage-side row-5 quantity (0.7359 against 0.3536 — §5.4's upper
bound for CONFIRMED; S5 unmodeled), at a 20% larger
budget and 17 more minutes. **Both pairs are carried, and the decision is the
same on either** (round 10, finding 4): with §2.3's containment respected the
same two comparisons read **0.6702 against 0.4010** and **0.6253 against
0.3408**, the registered criterion — "a dependency that usually fails is not a
control" — condemns 25 and retains 30 on both, and the corrected pair is the one
a population can produce. **N = 25 is registered as the alternative** with
its cost attached in full: the control gate fails three times in five under a
true null in both control arms on either reading, the coverage-side CONFIRMED bound lands about one time in
three, and — a second cost, found while constructing §2.8's schedule — **25
rounds do not tile the ten-sequence Williams block**, so the registered
carryover-balanced order would have to be reconstructed for 25 and this file
does not carry that construction. N should stay a multiple of 5 for §2.8's
position balance, and a multiple of 10 for its transition balance.

### 5.5 What a verdict does not license

A TRACKING verdict on arm B says that *this* paraphrase — under §2.6's
inclusivity invariant, so a paraphrase of the clause frames and not of the
boundary language — did not move coverage. It does not say paraphrase never
does. A TRACKING verdict on arm C says that *this* permutation, which moves
three clauses and leaves every reference resolving backward, did not move
coverage; it says nothing about an order that breaks a reference. A COLLAPSE
verdict on arm E says that *this* denaming did move coverage. Each arm is one
instance of its perturbation type; that is the design's central limitation and
§9 states it again rather than leaving it here.

**A CONFIRMED row does not license the causal claim in general, and an
R1-UNSUPPORTED row does not license its negation.** CONFIRMED means one
denaming, of one policy family, at one model snapshot, on one day, produced a
placement collapse on at least three of four narrow classes with arm E's S5
labels at the ceiling, class 4 not collapsing, arm E not reading LOW on class 3,
and both controls holding — the full [D-10] conjunction, restated whole so no
summary of it states a smaller rule (round 6, finding 3). It does **not**
establish that the author derived either threshold: §4.6 registers why
`|Q| = 0` is not comprehension evidence, the class-3 conjunct establishes no
comprehension either, and §4.5's X6 is descriptive and gates nothing (round 9,
finding 2; round 10, finding 3). R1-UNSUPPORTED means that collapse did not happen, and is compatible
with a snapshot that has seen this policy family before (§5.3 (i), §7, §9).
Neither row is a measurement of "anchoring" as a property of models.

No verdict in this study is a statement about defect detection. No pack is
evaluated, no mutation is applied, no evaluator runs. "Coverage" means a
correctly-labelled record fell inside a registered predicate under the correct
policy — and the placement endpoint means only that *some* accepted record did,
label or no label — and Study 011's census already recorded that the claim "low
probe diversity costs detection power" is a plausible mechanism there and a
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
011's `harness/PINS.json` against the digest this study pins for it
(`e0007697…`); **verifies Study 011's `harness/PORTS.md` against the digest
this study pins for it (`783cc9c3…`)** — round 2's finding, since an earlier
draft called it pinned while pinning only the registry beside it; verifies
Study 010's `PROTOCOL-LOCK.json` (`4966aa82…`) against the digest *011* pins
for it; **verifies this study's own `harness/PORTS.md` against the digest
`harness/PINS.json` records for it**, so the file that says what each
enumerated change *was* cannot be rewritten after the review; then binds every
row of §2.2 **to the authority that row actually has**, as three tiers.

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
`HEAD` blob (this study has no lock-commit machinery), and **the four files
this study takes from Study 011's own harness are bound to no lock at all**,
because 011 pinned none. What rests on review and on C3 rather than on a digest
chain is exactly those four: `batch.py`, `score_rates.py`, `integrity.py`, and
the census — and, from round 3 onward, on §2.10's tree manifest, which does not
give them an *ancestor* but does bind them to the bytes a reviewer read.

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
   named threshold, and an empty (23.75, 39) approach band. The census is a
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

**Further fixtures for the three new admission codes and the one changed
admission check**, registered because `arm-mismatch`, `schedule-mismatch` and
`session-reused` are the codes this study introduces (§3.3) and the
arm-specific terminal-prompt gate is the only check it changes — and because in
this study **five** prompts first meet that gate on a real slot, under an
interleaved order where an off-by-one in the driver's arm sequence would place
slots in the wrong tree silently. 011 could note that its one registered prompt
first met the ported gate on batch slot 1; that consolation is not available
here. So C4 additionally requires:

1. **a synthetic slot whose transcript carries arm B's prompt bytes inside arm
   A's tree**, required to score exactly `arm-mismatch` — not
   `context-mismatch`, not `transcript-refused`;
2. **a synthetic slot whose `CALL.json` `arm` stamp and `armPromptSha256`
   disagree with each other**, required to score `arm-mismatch`;
3. **one admissible slot per arm**, so the arm-specific terminal-prompt gate is
   exercised at **all five** registered prompt digests in CI, before the batch
   rather than on slot 1;
4. **a same-arm slot copied to another index in its own arm** — right arm,
   right prompt digest, right registry, so `arm-mismatch` cannot see it —
   required to score `schedule-mismatch`, and required to make the ledger↔slot
   bijection fail (§3.3);
5. **a slot whose recorded `(globalIndex, round, position, arm)` disagrees with
   §2.8's registered call order**, required to score `schedule-mismatch`;
6. **two slots sharing session bytes**, required to score `session-reused` on
   the later one;
7. **a slot whose `SLOT-MANIFEST.json` disagrees with its bytes**, required to
   make the whole scoring return `UNRESOLVED-BY-DESIGN` with no contrast — the
   fixture that proves the §2.9 consequence is code and not a sentence, and
   required to demonstrate specifically that the altered slot is **not**
   quietly moved out of `V_X`;
8. **a synthetic population exercising every row of §5.3's decision table**,
   including rows 1, 2, 3 and 6, at known integers — because a table whose
   gate rows never fire in any test is a table nobody has run.

**C5 — the population is the registered schedule, and the verdicts are in
code.** The scorer derives the canonical `arms/` root from its own location
(§2.10 [D-23]; there is no `--slots`), reads every slot of every arm, computes
each run's admission verdict and each arm's populations itself with the §3.3
rule, and refuses unless **all** of the following hold:

1. every slot carries a terminal outcome;
2. the ledger `BATCH.json` and the slot set are **in bijection** — one ledger
   record per slot, one slot per record, at the path the record names;
3. the ledger's `(globalIndex, round, position, arm)` sequence is **exactly a
   prefix of §2.8's registered call order**, with no gap and no reordering;
4. each arm's slot indices are exactly the contiguous range `1…count_X`, where
   `count_X` is **derived from that prefix** rather than from a round number —
   which is what an earlier draft could not do, since it required `1…R` from
   `SHORTFALL.json`'s round count while §2.8's own text left arms holding `R`
   or `R−1` slots, and a partly completed round satisfies neither;
5. when a shortfall is declared, the declared prefix equals the ledger's
   prefix, slot for slot;
6. the ledger's hash chain verifies and every slot's `SLOT-MANIFEST.json`
   recomputes (§2.9) — and a failure here does **not** move a slot out of a
   denominator, it makes the whole scoring `UNRESOLVED-BY-DESIGN`;
7. the prefix is the **complete** 150-slot order, or every verdict is
   `UNRESOLVED-BY-DESIGN` and no contrast is computed (§2.8's stopping rule).

**The §5.1 level verdicts, §5.2 contrast verdicts and §5.3 decision-table row
are computed by the scorer from the integers it just wrote, by the registered
rules, with no operator input and no flag that changes a cut**, and a harness
test parses §5.1's, §5.2's and §5.3's tables out of this file and diffs them
against the scorer's own. No rate or verdict may be computed by any other path,
and none is reported without its denominator beside it.

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
registry, and the command refuses without it. The control precedes the batch by
code and not only by ceremony: `batch.preflight()` creates no slot, and
`score_rates.py` reads none, unless the registry records the assent and
`controls/isolation-negative/VERDICT.json` carries one of the three registered
outcomes under that same assent and against the golden capture this batch runs
behind. Any of the three satisfies it — a `no-context` verdict still exits
non-zero and is still reported as undemonstrated; what the batch refuses is a
control that never ran.

**C8 — the arm artifacts are what §2 says they are.** This is the control that
makes "semantics constant, surface perturbed" checkable, and it is this study's
own. `harness/integrity.py` requires, before any call and before any scoring:

1. every arm's four files at their registered digests; the **single registered
   mirror module** `harness/policy_mirror.py` at its registered destination
   digest (§2.2 [D-14]), because it is the arbiter of every arm's labels; and
   the **assembled preamble**, `CONVENTIONS_DELTA` and `CLAIM.md` at theirs;
2. the prompt equation of §2.6 for every arm — `PROMPT.txt` = `HEADER` +
   `POLICY.md` minus its final LF — with `HEADER` derived from **011's pinned
   prompt bytes minus 010's locked policy bytes**, 948 bytes, and `arms/A`
   satisfying the same equation as every other arm;
3. the document structure of §2.6 parsed for every arm: one preamble, exactly
   five clause bullets with labels P1–P5 each appearing once, one conventions
   paragraph;
4. the **preamble byte-identical across all five arms** and equal to **010's
   preamble with `PREAMBLE_DELTA` applied at its single occurrence** — checked
   both ways, so neither the cross-arm equality nor the derivation from 010's
   bytes can be satisfied alone; the conventions paragraph byte-identical
   across A, B, C, D and equal to **010's conventions paragraph plus
   `CONVENTIONS_DELTA`**; and E's equal to that plus the registered
   threshold-definition sentence and nothing else;
5. the **literal census** over clause bodies, run under §2.6's definition —
   digit-runs with clause-label tokens `P1`–`P5` masked out first:
   - B's clause-body digit-run census equals A's, which is
     `{40, 40, 70, 70, 70, 70}`;
   - **B's inclusivity-adjacency pattern matches A's clause for clause**
     (§2.6): in every arm that states its thresholds as literals — A, B, C and
     D — each numeric bound carries an explicit inclusivity word from the
     registered vocabulary immediately adjacent to its literal, on the same
     side, of the same sense, in the same clause — compared as the ordered
     tuple sequence *(label, literal, side, sense)* for A, B and D, and
     required to be **equal**, not merely compatible; C's tuple sequence is
     A's own by the byte-identity of its bodies with A's (next bullet), not by
     a second comparison. **D's tuple sequence must equal A's under σ**, and
     **E's six bound senses must equal A's six senses in the same clauses**,
     with the side comparison omitted for E because a named bound carries no
     side (§2.6);
   - C's bodies are byte-identical to A's, and its label order is the
     registered permutation, which must resolve **every explicit clause-label
     reference backward**, **every three-part "absent a sanctions hit or an
     embargoed registration" precondition backward**, and **the two-part
     "Absent a sanctions hit" precondition backward**, and must be the
     **maximum-movement** permutation that does — the four conditions of §2.6,
     checked by re-deriving them from the parsed bodies and by enumerating all
     120 permutations rather than by comparing against a hard-coded tuple;
   - D's clause-body digit-run census is A's under σ, which is
     `{45, 45, 72, 72, 72, 72}`;
   - **E's clause-body digit-run census is empty**, and the digit-runs in the
     whole of E's `POLICY.md` are exactly the clause labels `P1`–`P5` and
     in-body clause-label references of the form `P<n>` — five plus one — and
     the token `ISO 3166-1 alpha-2` — three more — **and no digit-run anywhere
     in the file equals `40` or `70`**. Registered as the truth of the frozen
     artifact rather than as an aspiration, and corrected twice: a first draft
     asserted the file was digit-free except for the labels and
     `ISO 3166-1 alpha-2`, which was false of P5's own cross-reference
     (`unless P4 applies`) and of the inherited preamble (`Study 010`), and the
     check as written would have refused the study's own artifact; round 2
     removes the preamble's study reference from every arm under
     `PREAMBLE_DELTA` (§2.5, [D-16]), which is why it no longer appears in this
     list;
6. the **landmark-grid verdict equality** of §2.4: the registered mirror
   module, **at its registered destination digest**, instantiated at each arm's
   registered `(T_low, T_high)` from that arm's pinned `ARM.json`, produces arm
   A's verdict vector elementwise over that arm's own **280-cell** grid, and
   every arm's family produces A's class-membership vector elementwise over the
   same grid. The grid is the 14-landmark set of §2.4, and the harness test
   additionally asserts the **negative** control that motivated its last
   landmark: a family encoding class 5 as `[T_low − 2, T_low)` agrees with arm
   A on all 260 cells of the 13-landmark grid and **disagrees** on the
   14-landmark one.

What C8 cannot check, stated in the control itself: that arm B's prose is a
*paraphrase* rather than a subtle semantic change, and that arm E's references
are *comprehensible*. Clause 6 catches any divergence that reaches the mirror;
it catches nothing that lives only in the prose. That gap is narrowed by **C10**
and by cross-vendor review of the five texts before the freeze, and is closed by
neither; §7 and §9 say so.

**C9 — the class schema, structurally and extensionally.** Every arm's
`FAMILY.json` must equal §2.3's schema instantiated at that arm's (`T_low`,
`T_high`) — over the members §2.6 registers as read; §2.6 also names the inert
members the file carries from 010 — six contiguous indices, and **structural
equality of all six predicate encodings** after substituting that arm's pair,
not merely extensional agreement on the landmark grid. The two bound different
failures and this control asserts the stronger one: structural equality refuses
a predicate that encodes the right set by a different construction, which the
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
this instrument **earlier the same day** this study was drafted — its
`MIRROR-AGREEMENT.md` merged at 13:50 and this draft was committed at 18:43 on
2026-08-07 — for exactly the circularity this study inherits and multiplies:
"the mirror encodes the same policy text the prompt inlines, so a misreading
the model and the mirror share produces 784/784 agreement no matter how many
witness records exist." Study 012 has **five** policy texts, **three** of which
(B, D and E) are substantive authored prose from the team holding the
prediction, and it is the one pre-data check that can answer the central
attack on this design — *is arm E's wording derivable, or was it written to
be hard?*

**What carries no model call is the verdict, not the instrument** (round 9,
finding 7). An earlier draft of this paragraph took round 1 finding 5's own
phrase — "the one cheap, model-call-free, pre-data check" — and it was false
as written: each clean-room mirror is **authored by a model session**, one per
arm, and `MIRROR-AGREEMENT.md` publishes the reader identity, the verbatim
commission prompt, the raw output and the consulted statement for every
attempt. What carries no model call is the **decision**:
`integrity.verify_mirror2()` executes the clean-room module and the registered
mirror over the 280-cell grid and compares verdicts, so agreement is settled
by code rather than by any reader's report of it, and no model is asked
whether the mirrors agree. **"Pre-data" survives unchanged and is meant
literally**: every reader ran against arm bytes already frozen and pinned,
before the first authoring call of the batch and before any rate existed that
a reader's result could be selected against. "Before any call" in this control
means the batch's authoring calls, of which C10 makes none; C10's own reader
sessions are pre-assigned, ordered, counted and published as such.

Registered, per arm, before any call:

1. **the readers are pre-assigned, and the assignment is recorded before any
   of them runs.** `MIRROR-AGREEMENT.md` names, per arm, the reader identity
   (vendor, model, harness) that will be given that arm and the order in which
   the five are commissioned. Round 2's finding: with no pre-designation,
   "commission a reader, and if it fails, commission another" is available and
   invisible, and the arm most likely to need a second reader is arm E — the
   one arm whose derivability is the study's central question;
2. an independent author receives **that arm's `POLICY.md` bytes and nothing
   of the study's substance beyond the published interface suffix** — the
   record shape and the three outcome tokens, published verbatim in
   `MIRROR-AGREEMENT.md`, carrying no threshold, no class and no study term
   (round 3, finding 8, dispositioned) — and otherwise nothing
   else** — not another arm, not the registered mirror, not `FAMILY.json`, not
   a record, not this file — and writes `analysis/mirror2_<arm>.py`;
3. **every clean-room mirror must agree with that arm's registered mirror
   elementwise on the §2.4 landmark grid**, all 280 cells. This is a
   precondition of the batch, not a post-hoc analysis: `harness/integrity.py`
   refuses while any arm's clean-room mirror is missing or disagreeing;
4. **every attempt is retained and published, including every failed one.** A
   reader that cannot produce a mirror, produces one that disagrees, or reports
   that it could not determine the thresholds is recorded in
   `MIRROR-AGREEMENT.md` with its output, its report and the arm it was given.
   Nothing is discarded and no attempt is unpublished; a study that keeps only
   the readers that agreed has measured nothing;
5. the isolation rule, the builder's own report of what it consulted, and the
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

**And a re-authored arm restarts the instrument, rather than reusing its
verdict.** If any arm text changes for any reason after its clean-room reader
has run — a re-authoring under this control, a review finding, an editorial
fix — then **that arm gets a fresh reader that has not seen the previous
version**, its earlier attempt stays published as an attempt against the
earlier bytes, and §2.10's tree manifest makes the change a new review round
besides. An agreement obtained against bytes that no longer exist is not
evidence about the bytes that run, and round 2 found the earlier text silently
permitted carrying one forward.

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
  mirror module at its registered digest**, the assembled preamble,
  `CONVENTIONS_DELTA` and `CLAIM.md` at theirs, the prompt equation, the
  document structure, the preamble and conventions equalities **in both
  directions** (cross-arm, and derived from 010's bytes), the literal census,
  arm B's inclusivity-adjacency tuple equality with arm A and arm D's under σ,
  arm E's bound-sense equality, arm C's four ordering conditions re-derived by
  enumeration, and the 280-cell landmark-grid verdict and class equality across
  all five arms with its registered negative control (C8), and the class schema
  per arm, structurally (C9);
- **the whole-tree review binding**: the tree manifest the final review round
  attested, recomputed over the frozen study directory and refused on any
  mismatch (§2.10 [D-20]) — this supersedes the round-1 binding, which covered
  only the five arm texts and was authenticated by the same commit it was
  meant to constrain;
- **the provenance chain at both ends**: 011's `PINS.json` *and* `PORTS.md` at
  their pinned digests, 010's `PROTOCOL-LOCK.json` at the digest 011 pins, and
  this study's own `PORTS.md` at the digest `PINS.json` records (C1);
- **a clean-room second mirror per arm, agreeing elementwise on the landmark
  grid**, as a precondition of the batch rather than a post-hoc analysis (C10);
- the codex binary digest and the CLI version string, both **before the call**,
  and the model name;
- the registered interpreter (implementation and version series), refused by the
  wrapper before it calls anything and by the batch and the scorer before they
  run;
- the registry of record, per run and per population: every run records the
  registry digest it was made under and any other is `registry-mismatch`; the
  scorer takes no registry, family, prompt, arm, golden **or slots** path at
  all and derives each from the harness's own location, refusing every argument
  but an optional record-emission directory (§2.10 [D-23]);
- **the arm binding, per slot**: the arm id and the arm prompt digest are
  stamped by the wrapper and checked by the scorer against the tree the slot
  sits in, so a slot made with the wrong policy text cannot enter another arm's
  denominator (`arm-mismatch`);
- **the schedule binding, per slot and per population**: every slot records its
  global schedule index, round, position and arm; the scorer refuses unless the
  ledger is in bijection with the slot set and the ledger's sequence is exactly
  a prefix of §2.8's registered call order (`schedule-mismatch`, C5). A
  same-arm slot copied, renamed or duplicated fails here, which is what
  `arm-mismatch` alone could not see;
- **cross-slot session uniqueness** over the whole population, on raw retained
  evidence, so no slot can agree with a copy of itself (`session-reused`);
- **per-slot terminal manifests chained into the ledger** (§2.9), with a
  mismatch invalidating confirmatory scoring for the batch rather than moving
  one slot out of a denominator;
- **the registered call order**: the driver refuses to create a slot out of the
  registered global-index order, refuses any plan that would reach past global
  index 150, refuses to resume anywhere but at the ledger's next index, and
  refuses any slot in any arm once `RESULTS.json` exists;
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
- **§6 C7's control recorded before the first slot**: the registry's assent, the
  canonical verdict at `controls/isolation-negative/`, one of the three
  registered outcomes, and the record bound to the same assent and the same
  golden capture — checked by the driver before it creates a slot and by the
  scorer before it reads one;
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
  each arm and each endpoint; **and the §5.1, §5.2 and §5.3 rules — including
  the ordered decision table — diffed against this file's tables by a test and
  computed by the scorer alone**;
- **the stopping rule**: an incomplete batch, or any arm short of its 30
  scheduled slots, yields `UNRESOLVED-BY-DESIGN` on every level verdict and no
  contrast at all, computed by the scorer and published as a stated fact
  (§2.8 [D-21]);
- the batch/score separation: the driver cannot compute coverage or a verdict;
  the scorer refuses unless the batch is terminal (exactly 150 slots, or a
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
- **that the per-slot manifests and the ledger chain were written honestly.**
  §2.9's chain makes a post-hoc edit to a slot visible to anyone who recomputes
  it, and that is all it does: the operator holds every input to the chain and
  could recompute the whole of it. There is no external timestamp and no
  transparency log in this study, and the chain is a bound against later
  alteration rather than a proof of contemporaneous recording;
- **that a midnight crossing was written up.** §2.8's one-UTC-calendar-day
  property is *computed* and published under `schedule.utcDay` — the date set
  the retained stamps carry, the undated-slot count and the two flags — so a
  reader can check the premise this file's §9 bounds and [D-10]'s confirmation
  sentence rest on, rather than taking "one day" on the document's word. What
  the flag cannot establish is that the `DEVIATIONS.md` entry §2.8 requires was
  written: the same operator holds every input, which is this section's
  standing position on the ledger chain. The publication is the auditable half
  and the write-up is the operator's;
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
- **the in-process route.** Study 011 §2.4 stated the ceiling plainly and this
  study restores it. The registered scoring command is the only *publisher*,
  and what arms the driver's guard is `RESULTS.json` existing — but **nothing
  prevents a library caller importing the scorer and computing an arm's rate in
  process, publishing nothing and leaving the marker unarmed**. Here the
  operator holds a directional prediction and the schedule is interleaved, so
  every arm exists from the first round. **Nothing here prevents the look.**
  What round 2 changed is what the look could *buy*: under §2.8's stopping rule
  an incomplete batch yields no verdict at all, at any round and for any
  reason, so an operator who reads arm E early and stops has published a
  descriptive table and forfeited the study's conclusion. An earlier draft
  answered this with a floor at eleven valid runs plus a recorded wall clock,
  which left the whole range from round 11 to round 24 open to exactly this
  move; that answer is withdrawn as insufficient and §2.8 [D-21] replaces it.
  What still is not prevented: an operator who looks, dislikes what they see,
  and **completes the batch anyway** while writing the analysis around it —
  bounded only by the fixed N, the fixed arm set, the registered decision table
  computed by the scorer, and the append-only chained ledger;
- that a declared shortfall was involuntary. This is unchanged and it is why
  the stopping rule keys on completeness rather than on the declared reason.

**Not prevented:**

- **All five perturbations were authored by the team that published the
  prediction [D-9].** This is the design's structural conflict and it is stated
  here rather than in a footnote — and it is stated at its **full extent**,
  which an earlier draft understated by naming only D and E. **Three of the
  five arms are substantive authored prose from the prediction-holding team**:
  arm B is a five-clause paraphrase, arm D is A's text under a substitution,
  arm E is a denaming with two authored reference sentences. Arm C is A's
  bodies in a different order — authored only in the choice of permutation, and
  that choice is now itself a registered maximum under four stated constraints.
  Only arm A is inherited. The conflict is sharpest where the control is
  weakest: a B that collapses disarms E under §5.3 (iii), so an author who
  wanted E's result had an interest in a B that *tracks*, and an author who
  wanted a clean story had an interest in a B whose bound phrases match A's —
  which is exactly what §2.6's invariant now requires. That coincidence is
  named here rather than left for a reader to notice.
  **Five things bound the conflict and none removes it:** every arm artifact is
  **registered by digest before any call**, so the texts cannot be adjusted
  once a rate exists; the **mirror is the arbiter** and C8 binds every arm's
  mirror to A's, so an accidental semantic change is a refusal rather than a
  result; **C10's clean-room second mirrors** re-derive each arm's semantics
  from that arm's bytes alone, with pre-assigned readers, every attempt
  retained, and a fresh reader after any re-authoring, and an arm E whose
  reader cannot derive (40, 70) is re-authored before the freeze rather than
  run; every artifact gets **cross-vendor adversarial review before the
  freeze**, whose findings and dispositions are published with this study; and
  **that review is bound to the frozen bytes by a whole-tree manifest** (§2.10
  [D-20]), so nothing this study ships — not a policy text, not the scorer, not
  this file — can change between the final review and the freeze without
  another review. §9 repeats it as a bound.
- **Contamination through the public repository.** `POLICY.md`, `FAMILY.json`,
  `PROMPT.txt` and Study 010's and 011's records have been public in this
  repository since 2026-08-06. The transcript whitelist mechanically excludes
  tool use, so no run can *retrieve* the repository during authoring; what
  cannot be excluded is that a model snapshot has seen this material. [D-16]
  removes the one *textual* pointer — no arm names a study — and that is a
  strictly smaller intervention than removing memorization, which nothing here
  can do. Two registered readings turn on it and neither is resolvable inside
  this design: §5.3 (i)'s R1-UNSUPPORTED outcome is **contamination-compatible**
  and is published saying so, and §5.3 (ii)'s OLD-EDGE-PREFERENCE outcome has
  contamination and round-number salience as two explanations this study cannot
  separate. Arm D is a partial probe on the first; a partial probe is all it
  is.
- **Prior-context leakage that reproduces the golden capture after
  normalization.** The allowlist matches normalized digests, not raw bytes, so
  it cannot refuse a leak that stays inside the normalization equivalence class.
- **A credential copy surviving a `SIGKILL` or a power loss.** The residual is
  one file under the operator's own scratch parent, and the remedy is manual.
- **Per-run isolation limits.** Fresh `HOME` and `CODEX_HOME` close the paths
  Study 010 found empirically. They do not close provider-side state: if the
  pinned CLI's backend carries cross-session memory keyed to the credential, the
  150 runs are not independent in the way this study assumes, and §4.3's
  intervals rest on an assumption that is then false. S6 is the one observable
  that would hint at it.
  **An earlier draft claimed such state "could only blur a contrast, not
  manufacture one", and that claim was false of the schedule it was written
  for.** Under the round-1 cyclic rotation arm E followed arm D in 20 of its 25
  calls and never followed A or B, so state carried from arm D's 45/72 prompt
  would have been carried into arm E's call almost every time — which is a
  mechanism for manufacturing exactly the predicted collapse, not for blurring
  it. §2.8's carryover-balanced order is the fix: every ordered pair of arms
  occurs 7 or 8 times in 149 transitions, so no arm is systematically preceded
  by any other. **What that buys and what it does not:** balance means a
  carryover effect is spread evenly across arms instead of loading onto one
  contrast, which is the difference between a bias and added variance. It does
  not remove the state, this study cannot measure it, and a *truncated* batch
  is not balanced at all — which is one more reason §2.8's stopping rule
  returns no verdict from one.
- **What `/tmp` still exposes.** The pinned CLI's sandbox is writable at
  `[workdir, /tmp, $TMPDIR]`; each run gets its own workdir and its own `TMPDIR`
  inside it, and the recommended scratch parent is outside `/tmp`. A run that
  used a tool at all is refused by the whitelist — and under §4.2's
  intent-to-treat endpoint it stays in the denominator counting as covering
  nothing, so the primary rates are **not** conditional on the author having
  happened not to use one. The per-protocol secondary S11 still is, which is
  what that endpoint is for.
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
> numeric classes, §5.3 (i) row 4 — `R1` is published as UNSUPPORTED, with the
> same prominence as the claim: in `ANALYSIS.md`'s first paragraph, in this
> study's README, in the venue and at the URL `CLAIM.md` records, and as a
> correction banner at the head of
> `studies/011-authorship-coverage-rates/DIVERSITY.md`.** No re-cutting of §5's
> thresholds, no "the effect was smaller than expected", no relegation to a
> limitations section.

**The correction says two things, and the second is not optional.** First: the
prediction R1 made did not happen — the coverage R1 said rests on the literals
did not go away when the literals went away, and R1 is withdrawn. Second, in
the same paragraph and not in a footnote: **this study does not thereby
establish the opposite.** Maintained coverage in arm E is compatible with the
author deriving the boundaries *and* with the author reproducing a policy
family it has seen before, and this design separates neither (§5.3 (i), §7,
§9). A correction that retracted R1 and installed "the author derives
boundaries" in its place would be trading one unearned causal claim for
another, which is the failure this whole study exists to avoid. §5.3 (i)
registers the census evidence that points one way or the other and registers
that it changes no verdict.

**What is retracted is R1 and nothing else.** The census's own committed
sentence — "boundary placement follows the numbers the policy names, not an
independent search for edges" — is a description of Study 011's own corpus,
it is true of those 784 records whatever arm E does, and it stands. The
correction banner says exactly that: the descriptive finding stands, the causal
extension R1 does not. Retracting a description that is true would be as
dishonest as keeping a causal claim that is false.

Beyond that:

- all 150 raw slot directories across the five arms, **including every invalid
  one**, with every byte the run left in them and nothing removed, in one of
  Study 011 §8's four registered slot shapes, each with its
  `SLOT-MANIFEST.json`; beside them the chained ledger `BATCH.json` and
  `SHORTFALL.json` if one is declared. Nothing in the tree is `.gitignore`d;
- **the expanded 150-slot registered call order and its realised transition
  census**, so a reader can check §2.8's balance claims against what actually
  ran rather than against the construction;
- the per-run admission verdict, refusal code, counts and class classification
  the scorer derives, for **every** slot, in `RESULTS.json`'s `runs` array;
- the compiled record trees for the valid runs whose completion held a parseable
  JSON array, emitted outside the slot tree;
- every recapture attempt's captures and the C7 negative control's retained
  files;
- `RESULTS.json`, `RATES.md` and `CENSUS.md`, written by the registered scoring
  command, with every rate's integers and bounds and every census count;
- `ANALYSIS.md` leading with the five arms' rates, the five `rho_X`, the §5
  verdict table and **the decision-table row the scorer computed** — a class
  covered in 1 run of 30 is published as 1/30 with its interval, in the
  headline;
- **the five arm artifacts themselves**, as committed before the batch, so any
  reader can judge whether the perturbations are what this file says they are;
- **`CLAIM.md`** — the verbatim published wording of R1, its venue, its URL and
  its retrieval date — committed and pinned before the freeze, so the
  retraction target is frozen with everything else;
- **`MIRROR-AGREEMENT.md`** — C10's five clean-room mirrors, the pre-assigned
  reader roster, **every attempt including every failed one**, the isolation
  rule each builder ran under, each builder's own report of what it consulted,
  and the per-arm 280-cell agreement table, following Study 011's format;
- `DEVIATIONS.md` for every departure from this file, written as it happens;
- **`PREREG-REVIEW.md`** — the complete pre-freeze review record, following
  Study 011's per-round, per-finding disposition format, carrying **per round
  the sha256 of each of the five arm texts as that round reviewed them** and,
  **from round 3 onward, that round's whole-tree manifest digest** (§2.10
  [D-20]). `harness/integrity.py` refuses unless the manifest it recomputes
  over the frozen tree equals the one the final round recorded, so nothing the
  manifest covers can change between the last review and the freeze — not a
  clause of arm E with Appendix A updated to match, not the scorer, not this
  file. **The review record itself is outside the manifest**, because it
  carries the attestation (§2.10): what stands in a digest's place there is the
  cross-check that the freeze pin equal the **last** attestation digest
  recorded in it, so defeating the binding requires rewriting the review record
  — forbidden by rule and visible to the reviewer who holds the transcript, not
  prevented by a digest;
- the pre-freeze cross-vendor adversarial review of **the complete post-port
  tree**, and the post-run cross-vendor review, both with per-finding
  dispositions, both recorded in `PREREG-REVIEW.md`.

No slot is deleted. No rate or verdict is recomputed on a different population
after the fact. If the study is abandoned before the batch — pin drift, failed
recapture, an arm that cannot be made to pass C8 — that is published too, in
`DEVIATIONS.md`, with the reason.

## 9. Bounds

Thirty samples per arm, five arms, one prompt template, one model, one CLI
build, one policy family of six classes, one machine, one day. At n = 30 a
perfect arm is bounded below at 0.8843 and a half-covered class carries ±0.187,
so this study separates "reliably covered" from "essentially never covered" and
resolves nothing between — §5.4 says exactly what that costs.

**The smallest real effect this design cannot see, stated plainly: any
anchoring effect that leaves coverage above roughly one run in five.** A drop
from 1.00 to 0.30 reads MID 99% of the time; a drop to 0.10 reads LOW only 65%
of the time; only a fall below about 0.08 is called four times in five. A
partial anchoring effect — the outcome most designs of this kind actually
find — is invisible here and is published as INDETERMINATE, which is what
INDETERMINATE means in this file.

**Every interval here is exact for a model this design cannot verify.**
Clopper–Pearson coverage is exact conditional on independent, constant-`p`
Bernoulli slots; §7 records that provider-side state shared across calls cannot
be excluded, and if it exists both halves of that condition fail. The phrase
"exact interval" in this file always means "exact under that model", never
"assumption-free".

**The joint figures are scenarios, not bounds, and the independence one is not
even available.** Every "P(all six)" in this file was computed under an explicit
independence assumption across classes and across arms that Study 011's own
corpus contradicts — its runs covered all six classes together in every valid
run — and on two of the six classes that assumption is **arithmetically
unavailable** rather than doubtful: §2.3's class 0 nests in class 1 and class 2
in class 3, correctness is a property of the record, and two pathwise-ordered
indicators are independent at no nondegenerate marginals (round 10, finding 4).
Independence is not a worst case either, and not in one direction: for
positively dependent classes a **conjunction** reads *higher*, while a
**tolerance** — the five-of-six control gate, the three-of-four patterns — reads
*lower* at the two N's this study weighed. §5.4 publishes a
containment-respecting companion beside every affected figure, with the sharp
Fréchet floor and the cap the marginals imply, and the honest form of the
headline joint figure at p = 0.95 and N = 30 is **"at least 0.757, and 0.778
under the containment-respecting scenario"** — the withdrawn form, "at least
0.6354, and 0.6865 under independence", named a floor computed for six free
events and a figure below that floor.

**The baseline is not fully comfortable jointly.** At a true per-class coverage
of 0.95, inside Study 011's own published interval, arm A reads HIGH on all six
classes 77.8% of the time under the containment-respecting scenario (68.7%
under the independence layer, which understates it). So roughly two runs of this
study in ten would find at least one falsifier-relevant class with no contrast
verdict available, from sampling alone and with nothing wrong — four in ten at
the N = 25 this study nearly registered. That is a bound
on what this design can return, not a prediction about the model, and §2.1
registers that such a class is reported as an unresolved baseline rather than
as drift.

**And the design's own precondition can fail.** §5.3 (iii)'s control gate — B
and C each TRACKING on five of six classes — passes 76.6% of the time at N = 30
under the independence layer and **67.0%** under the containment-respecting
companion, which is the coherent reading and the smaller one, so about one run
of this study in three returns
`CONTROLS-FAILED` and adjudicates R1 in neither direction, with both control
arms behaving exactly as predicted. At the N = 25 this study nearly registered
it would have been three runs in five on either reading.

**An incomplete batch returns nothing.** §2.8's stopping rule is a real cost
and not a formality: a batch that dies at round 29 for reasons nobody chose
publishes a full descriptive surface and no verdict at all. That is the price
of removing optional stopping, and it is paid before the data rather than
argued about after.

**Each arm is one instance of its perturbation.** One paraphrase, one
permutation, one rename, one denaming. A TRACKING verdict on arm B is evidence
about that paraphrase; it is not a measurement of paraphrase-robustness, and
nothing here supports the plural. Arm D in particular is one *pair* of
thresholds, (45, 72), whose roundness differs from (40, 70)'s — §2.4 and
[D-18] state that confound and §5.3 (ii) registers the outcome it would
produce.

**The perturbations were authored by the team that predicted the outcome —
three of the five arms as substantive prose, not two.** Arm B's paraphrase is
authored, and arm B is the control whose failure would disarm arm E, which
makes it the arm where the conflict has the most to gain. Registration before
any call, the mirror as arbiter with C8's mechanical equality across arms,
C10's clean-room re-derivation of each arm's semantics from that arm's bytes
alone with pre-assigned readers and every attempt published, cross-vendor
review of the complete post-port tree before the freeze, and the whole-tree
manifest binding between that review record and the frozen bytes are the
mitigations. They bound the risk; they do not remove it, and a reader who
discounts this study for that reason is applying the right standard.

**Arm E denames literals, it does not remove numeric information, and it does
not remove memorization.** Its threshold values are recoverable by arithmetic
from words, because a policy that did not determine them would be a different
policy and the contrast would be confounded. What E measures is the cost of
*indirection*, not of *absence*. [D-16] removes the one textual pointer any arm
carried to a public text stating 40 and 70; what it cannot remove is that this
policy family has been public since 2026-08-06 and a model snapshot may have
seen it. So an arm E that maintains coverage is published as **R1-UNSUPPORTED
and contamination-compatible**, and this study does not claim the positive
counter-thesis.

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

**The review record is bound to the bytes it reviewed, and from round 3 that
means the whole tree.** `PREREG-REVIEW.md` follows Study 011's per-round,
per-finding disposition format and records, per round, **the sha256 of each of
the five arm texts as that round reviewed them** and — from the first
post-port round onward — **that round's whole-tree manifest digest** (§2.10
[D-20]). `harness/integrity.py` refuses unless the manifest it recomputes over
the frozen tree equals the final round's.

**The sequencing changed in round 2 and the change is the point.** It was
review → port → freeze, which left every ported byte and every filled digest
outside the reach of every review that ran. It is now:

```
review rounds over the specification and the arm texts
  -> THE PORT (harness written, arms assembled, every (port time) cell filled)
    -> THE FINAL cross-vendor round, over the complete post-port tree
      -> the freeze
```

**Decisions marked with a round in the last column were opened by a review**,
not by the drafters, and each records the option the maintainer took and the
option not taken. Round 1 opened D-14 through D-18; round 2 opened D-19 through
D-24 and re-adjudicated D-1, D-4, D-5, D-7, D-9, D-10, D-13, D-16 and D-18.

| # | decision | proposal | alternative, and what turns on it | opened |
| --- | --- | --- | --- | --- |
| **D-1** | N per arm (§2.8, §5.4) | **30** | **25** (the round-1 proposal, re-adjudicated in round 2). The decisive quantity is not the marginal P(HIGH \| p=0.95), which rises only 0.8729 → 0.9392, but the **registered B/C control gate of §5.3 (iii), which passes 0.4031 at N = 25 and 0.7658 at N = 30**, and the coverage-side CONFIRMED quantity (§5.4's upper bound; S5 unmodeled), 0.3536 against 0.7359. Round 10, finding 4: both pairs are read under an independence across classes that §2.3's nesting makes unavailable, and the containment-respecting companion §5.4 now publishes puts the same comparisons at **0.4010 against 0.6702** and 0.3408 against 0.6253 — at these two N a tolerance rule gets harder, not easier, when classes move together. This file's own criterion — a dependency that usually fails is not a control — condemns N = 25 on its own numbers, on either reading. N = 25 also costs the §2.8 schedule: **25 rounds do not tile the ten-sequence Williams block**, so its carryover-balanced order would have to be reconstructed and this file does not carry that construction. 20 is worse again (gate 0.0557). N = 30 costs +25 calls and ~17 minutes. Keep a multiple of 5 for position balance and of 10 for transition balance | draft; re-adjudicated round 2 |
| **D-2** | The §5.1 level cuts | **`L ≥ 0.70` HIGH, `U ≤ 0.30` LOW** | Study 011's tier cuts 0.80/0.40. At N = 30 the 0.80 cut lands at `k ≥ 29` — one miss in thirty — and at N = 25 it needs a perfect arm, so a single stray miss in a control arm reads INDETERMINATE either way. Interacts with D-1 | draft |
| **D-3** | Arm E's exact reference wording (§2.5, §4.5 X6, Appendix A) | the Appendix A text **as rewritten in round 1**: one denominator, no pronoun, §2.3's own threshold names — "The **review threshold** is seven tenths of that full range; the **personal-data threshold** is four tenths of that same full range." | any wording that keeps the clause-body digit census empty and the values exactly derivable. The round-1 draft's wording is **not** an option: its pronoun admitted 28 (two fifths of the review threshold), it called `T_low` the "clearance threshold" against §2.3's own key, and its two denominators made one derivation harder than the other. X6 registers the misderivation audit under either wording | draft; rewritten round 1 |
| **D-4** | Arm B's exact paraphrase (Appendix A) | the Appendix A text **as rewritten in round 2**, plus the clause-by-clause A ↔ B substitution table the review adjudicates row by row. P4 now reads "**40 or more** but **below 70**", so every bound's cue sits on A's side with A's sense | any paraphrase preserving the clause-body digit census, the clause order, the semantics, **and §2.6's inclusivity-adjacency pattern**. The round-1 text is **not** an option: its "from **40** up to but not including 70" put P4's lower cue *before* the literal where A's is *after*, violating the very invariant round 1 added — round 2 found it, and the invariant is kept and the text changed rather than the reverse. Weakening the invariant is the alternative not taken, and it would cost §5.3 (iii)'s dependency its meaning | draft; invariant added round 1; text fixed round 2 |
| **D-5** | Arm C's permutation and label handling (§2.6) | **(P1, P2, P4, P5, P3)**, labels travel with their bodies. It resolves **every** reference backward — explicit label references, both precondition forms, including P2's own two-part opener — and is the **unique maximum-movement** permutation that does, moving three of five | (a) **(P2, P1, P4, P5, P3)** — the round-1 registration, and the unique *derangement* resolving the explicit and three-part references, at the cost of leaving P2's own opener forward-referencing P1; *derangement + every reference backward* is **empty** over all 120 permutations, so the two properties cannot both be had. Round 2's finding: arm C is a control on which arm E's interpretation depends, so a residual comprehension difficulty in C is a live alternative explanation for a C-collapse and not merely a disclosed cost — comprehensibility beats full derangement here, and the trade is that C perturbs order less. (b) renumbering labels to presentation order, which would add a second perturbation. The round-1 draft's (P2, P4, P1, P5, P3) is **not** an option | draft; replaced round 1; replaced again round 2 |
| **D-6** | Arm D's C2 pack-side clause (§6 C2) | replace with the C8 landmark-grid check and say so | construct a threshold-shifted pack `C_D` solely to keep the clause, adding an artifact no run evaluates | draft |
| **D-7** | The call order within the batch (§2.8) | **the registered first-order carryover-balanced order**: a Williams design for five treatments (ten sequences), three blocks, in the three registered block orders. Each arm holds each position 6 times; each ordered pair is adjacent exactly 6 times within rounds; every ordered pair occurs 7 or 8 times over all 149 transitions | cyclic rotation by round (the round-1 proposal) — balances position perfectly and predecessor not at all: under it **arm E follows D in 20 of 25 calls, C in 5, and A or B never**, so provider-side carryover from arm D's 45/72 prompt could manufacture arm E's predicted collapse. Round 2 found it and §7's claim that such state "could only blur a contrast" is withdrawn with it. Also available: fixed within-round order (confounds arm with position) or blocking by arm (confounds arm with time-of-day drift). Exact balance over 149 transitions is arithmetically impossible; max − min = 1 is the registered achievable | draft; replaced round 2 |
| **D-8** | Golden recapture and C7, once or per arm (§3.2, §6 C7) | **once for the whole batch**, because both use the arm-independent probe prompt and the pre-prompt context does not depend on the prompt | per arm, which costs 10 extra probe calls and buys nothing this file can name | draft |
| **D-9** | Who authors the arm texts (§7, §9) | the study team — **three of the five arms as substantive authored prose (B, D, E), which round 2 corrected from two** — with **C10's clean-room re-derivation under pre-assigned readers with every attempt published and a fresh reader after any re-authoring**, cross-vendor adversarial review of the complete post-port tree before the freeze, and the review record bound to that tree by manifest | cross-vendor *authorship* to a registered spec, which weakens the conflict in §9 and adds an uncontrolled authoring step of its own | draft; C10 and the digest binding added round 1; extent corrected and C10 hardened round 2 |
| **D-10** | The E decision patterns (§5.3 i) | **CONFIRMED iff PLACEMENT-COLLAPSE (S1) on ≥ 3 of the 4 narrow numeric classes, *and* arm E's S5 labels are at the ceiling (§4.6), *and* the B/C control gate holds, *and* class 4 does not collapse, *and* arm E does not read LOW on class 3 (round 9, finding 2, stated on arm E's own level rather than on a contrast against arm A in round 10, finding 3 — a contrast is INDETERMINATE whenever arm A is not HIGH on the class, so the round-9 form passed vacuously for the very arm it was added to refuse; it establishes no comprehension, and §4.6 registers that no conjunct here could); R1-UNSUPPORTED iff E reads HIGH on the primary on ≥ 3 of 4; LABEL-COLLAPSE-ONLY iff COLLAPSE on ≥ 3 without placement collapse on ≥ 3; every other pattern INDETERMINATE**, all-MID explicitly included, with §5.3's ordered decision table making the whole rule total | ≥ 2 of 4 (more easily decided in both directions) or all 4 (harder in both); and confirmation on the *primary* rather than on S1 placement — the round-1 form, which round 2 found reads the wrong mechanism: because `H ⊆ raw`, an arm E that still places records on 40 and 70 but mislabels them loses H-coverage entirely and would have read CONFIRMED while the hugging R1 predicts would vanish was still there. The round-1 draft registered only the falsification half, which let a motivated analyst call 2 COLLAPSE + 2 MID a confirmation afterwards | draft; confirmation half added round 1; mechanism and totality fixed round 2 |
| **D-11** | Which classes the collapse prediction covers (§2.3, §5.3) | **0, 1, 2, 5 only**; classes 3 and 4 predicted TRACKING everywhere | include class 3, which a diffuse author covers by accident across a 30-wide band (27-wide in arm D) and which would therefore flatter the prediction | draft |
| **D-12** | S10 old-edge cross-scoring status (§4.6, §5.3 ii) | **registered secondary with its own registered predicted pattern** | promote to primary (it is the sharper measure of the rename claim) or drop it (it is the only registered probe on contamination) | draft |
| **D-13** | Unequal valid counts across arms (§2.8, §4.2) | **no truncation**; the primary endpoint's denominator is N for every arm (intent-to-treat), and the per-protocol secondary S11 uses each arm's own `V_X` with a caution if two arms differ by more than 2 | truncate every arm to the common minimum, at the cost of discarding admitted runs. Round 2's move of the primary to N makes this decision smaller than it was: unequal denominators now affect only the secondary | draft; scope narrowed round 2 |
| **D-14** | How arm D gets a mirror (§2.2, §2.6, §2.10, §6 C1, C8 clause 6) | **(b) one 010-locked module parameterized by (`T_low`, `T_high`) read from the arm's registered `ARM.json`.** One mirror artifact, one destination digest, five arms; D's behaviour is keyed to an artifact that is already pinned before any call, and the §2.2 row becomes an enumerated-change port bound to 010's lock on the source side | **(a) a fifth registered per-arm file `arms/<X>/MIRROR.py`**, five artifacts pinned in §2.6, §2.10 and C8 clause 1, with D's derived from 010's locked mirror by substituting exactly two integer literals and the diff published in `harness/PORTS.md`. (a) keeps each arm's mirror byte-visible in its own directory; (b) keeps the count of unreviewed artifacts at one. Under either, C8 clause 6 runs against the arm's actual mirror at its registered digest. **Round 1 found that neither was registered**: the draft ported the mirror byte-identically, which encodes 40/70 and cannot serve arm D, and pinned no per-arm mirror anywhere | round 1 |
| **D-15** | Where the scale sentence goes (§2.1, §2.5, §2.6, Appendix A) | **(a) the identical sentence "The office's risk scale runs from zero to one hundred." in all five arms' conventions paragraphs**, as the registered `CONVENTIONS_DELTA`, pinned by its own sha256. This relaxes §2.1's arm-A byte-equality to *011's pinned text plus exactly that published delta* — acceptable because §2.1 already declares 011's runs historical and every contrast within-batch, so the prompt digest was load-bearing only for the §4.7 drift report, which gates nothing | (b) **a sixth arm A′ = A + the scale sentence** as an explicit scale-disclosure control, +25 calls, which measures the confound instead of eliminating it; (c) **keep it in arm E only** and state in §5.3 (i), §8 and §9 that arm E carries two differences from baseline and its falsifier is correspondingly weaker. Round 1's finding: the scale sentence is *new semantic information* — neither 011's prompt header nor 010's conventions bounds `riskScore` anywhere, 011's corpus contains scores authored with no stated scale, and no mirror can catch a domain hint because the mirror encodes no domain | round 1 |
| **D-16** | The preamble's study reference (§2.1, §2.5, §2.6, §5.3 i) | **replace `Study 010` with `this study` in all five arms**, as the registered `PREAMBLE_DELTA` at its single occurrence in 010's locked bytes, with the assembled preamble pinned by its own sha256. This removes the one textual hook by which any arm points at a public text stating 40 and 70 | **keep the preamble byte-identical to 010's** (the round-1 proposal) and register the recall channel it leaves open. Round 2's finding: with the name in place, an arm E that maintained coverage was being labelled an unconditional falsification of R1 while the text handed the author a pointer to the answer — recall does not falsify a causal proposition about denaming. The adopted option costs **a second registered delta from 010's locked text**, on top of D-15's, and it buys strictly less than it appears to: it removes the *pointer*, not residual memorization of a corpus public since 2026-08-06, which is why §5.3 (i) publishes maintained coverage as **contamination-compatible** rather than as a clean falsification | round 1; adopted round 2 |
| **D-17** | The contrast rule (§5.2) | **the level-gated rule, plus COLLAPSE-DISJOINT (`U_X < L_A`) reported beside it and never substituted for it**, and the same level-gated rule computed on S1 as the **PLACEMENT contrast**. All computable from the same integers; none needs a distribution for a difference of proportions, so the estimation-first posture is preserved | **the level-gated rule alone**, accepting that a class where E reads LOW and A reads MID is published as INDETERMINATE despite widely disjoint intervals in the predicted direction. Round 1's finding: the contrast rule is the study's second-most consequential registered choice after the level cuts, and the draft registered thirteen decisions without it | round 1; placement contrast added round 2 |
| **D-18** | Arm D's threshold pair (§2.4, §5.3 ii, §9) | **(45, 72)** — no single **additive shift** explains it, which is the confound this pair was chosen to exclude. Round 2 corrected the claim's wording: unequal moves exclude a translation, **not** an affine map (`0.9x + 9` sends 40 → 45 and 70 → 72), and the wider claim is withdrawn | **(50, 80)** — salience-matched (both decade-round, as 40 and 70 are) and width-preserving (class 3 stays 30 wide, where (45, 72) narrows it to 27), at the cost of being exactly a +10 additive shift of (40, 70). The two candidates trade one confound against the other and the review picks which one this study would rather not be able to rule out. Under either, §5.3 (ii)'s second outcome is published as **OLD-EDGE-PREFERENCE** with contamination *and* round-number salience as two explanations this study cannot separate, and the third — new-keyed LOW *and* old-keyed LOW, a general degradation — stays registered | round 1; terminology and outcome name fixed round 2 |
| **D-19** | How drift is classified (§2.1) | **numeric: arm A is DRIFT-SUSPECTED iff it reads below HIGH on four or more of its six classes, or LOW on any one.** Everything else, including three classes below HIGH, is an unresolved baseline on those classes and nothing more | **remove the drift classification entirely** and report only unresolved baselines, which costs the study its one registered way of naming a baseline that has plainly moved. The round-1 wording — "several classes at once, or a class far below the cut" — is **not** an option: it is an unregistered rule wearing a registered one's clothes, since "several" and "far below" are the analyst's to set after the data. Round 2's finding. Under the registered scenario the numeric rule fires by sampling alone with probability 0.0002 at N = 30 — **0.0041 under the containment-respecting companion** (round 10, finding 4), the larger figure and the one §2.1 quotes, because a nested pair below HIGH puts two of the six classes below HIGH at once | round 2 |
| **D-20** | Review-to-freeze binding and the port ordering (§2.2, §2.10, §7, §8) | **the final cross-vendor round reviews the complete post-port candidate tree and attests an exact commit and tree manifest**; the manifest digest is pinned and recomputed at the freeze; any byte change requires a new round; the port therefore happens **before** the final review, not after it | **an externally signed attestation** — the reviewer signing the manifest digest with a key this repository does not hold — which is strictly stronger and is not available in this environment. The round-1 binding is **not** an option: it covered only the five arm texts and was self-authenticating, since `PREREG-REVIEW.md`, Appendix A, the policies and `PINS.json` could all move together in one commit and every specified equality would still pass. Cost of the adopted option: the final round is a much larger review, and any finding that changes a byte repeats both the port and the round | round 2 |
| **D-21** | What an incomplete batch may return (§2.8, §7, §9) | **nothing: descriptive-only, every verdict `UNRESOLVED-BY-DESIGN`, no contrast, at any round, for any reason** | **verdicts above a floor** — the round-1 rule, no verdict below eleven valid runs plus a recorded wall clock. Round 2's finding: a floor does not remove optional stopping, it relocates it to round 11, and an operator holding a directional prediction can read arm E in process (§7) and stop when the picture is favourable. A timestamp is not a pre-commitment. Cost of the adopted option, paid in advance: a batch that dies at round 29 for reasons nobody chose publishes a full descriptive surface and no conclusion | round 2 |
| **D-22** | How a crashed batch resumes (§2.8, §6 C5) | **by global schedule index**: `--resume` continues at the ledger's next index after verifying the recorded prefix against §2.8's registered order, slot for slot | `--start-round K`, the round-1 form, which is **not** an option: it cannot resume a partly completed round without either overlapping recorded slots or silently omitting the rest of that round, and a round number alone makes neither detectable afterwards | round 2 |
| **D-23** | The scorer's argument surface and the population root (§2.10, §6 C5) | **`--slots` is removed** from the scorer and from the shortfall declaration; the canonical `arms/` root is derived from the harness's own location, and `--emit-records` is the whole remaining surface | keep `--slots` for operator convenience, which round 2 found lets the published population be pointed at any tree of the right shape — a copy with a slot removed, a duplicated arm — with every per-slot check still passing, because a same-arm copy is not `arm-mismatch` | round 2 |
| **D-24** | The primary endpoint's denominator (§3.3, §4.2, §4.6 S11) | **intent-to-treat: `k/N` over the scheduled slots**, with pipeline-invalid slots counted as covering nothing and the `[k/N, (k+I)/N]` sensitivity bound published beside every rate | **`k/V_X`**, the round-1 primary, retained as the per-protocol secondary S11. Round 2's finding: the admission gates are arm-independent but the probability of tripping them is not — a policy text can move tool use, exit status, completion production and parseability — so excluding tripped runs conditions the primary on a post-treatment outcome, and the bias runs the wrong way, since the arm whose text most disrupts authoring sheds exactly the slots that would have covered nothing. Cost of the adopted option: ITT is conservative in the other direction, which is what the published bound exists to show | round 2 |

---

## Appendix A — the five policy texts (DRAFT)

**These are drafts.** The frozen artifacts are `arms/<X>/POLICY.md`, and their
digests in `harness/PINS.json` are authoritative. Registered as a check: a
harness test requires each arm's `POLICY.md` bytes to equal the text printed
below, so this appendix cannot drift from the artifact after the freeze — the
same registered-illustration discipline Study 011 applied to its own prose.
**That check alone is not enough**, because a clause and its illustration can
move together between the last review round and the freeze and still satisfy
it; what closes that is §2.10's whole-tree manifest, which covers this file and
`arms/` in the same digest, so a co-moving edit moves the manifest and the
freeze refuses. `PREREG-REVIEW.md`'s per-round arm digests are the record of
what each round read, not a check — no code reads them — and the residual §2.10
registers is a rewritten review record, forbidden by rule rather than prevented
by a digest.

**The preamble, byte-identical in all five arms** — inherited from Study 010
with the registered `PREAMBLE_DELTA` **[D-16]** applied, so that no arm hands
its author a name-keyed pointer to a public text stating 40 and 70 (§2.5). It
is held fixed across arms so that each arm's variation is confined to the
intervention:

```
# Vendor screening policy — the arbiter

Synthetic policy for this study. Every other artifact in this study is checked
against this text; a divergence between a pack and this text is a pack bug.
This is also the exact policy text the record author receives (inlined in the
registered prompt), so it is the whole of what the two sides share.
```

`PREAMBLE_DELTA` is the substitution `Study 010` → `this study`, applied at its
**single occurrence** in 010's locked `policy/POLICY.md` (byte offset 64, one
occurrence, verified against the locked bytes). It lengthens the file by one
byte. The assembled preamble is **343 bytes**, sha256
`83b7b27fb8cb9054d4536edc6d20ec1c7f9e57cc66f69b5c68891f9def83734d`, and it is
pinned by that digest in `harness/PINS.json`.

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
sentence — sha256
`3b121dd02f8aedd103d0d047b77ee289f788b8d8d22589e396e13baa268223e0`, pinned by
that digest in `harness/PINS.json`. Arm A's `POLICY.md` is therefore
1759 + 55 + 1 = **1815 bytes**, the last byte being `PREAMBLE_DELTA`'s.

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
with `PREAMBLE_DELTA` **[D-16]** and `CONVENTIONS_DELTA` **[D-15]**, and it must
produce arm A's prompt under §2.6's equation with `HEADER` derived from 011's
pinned prompt bytes. If the review reverses both deltas, arm A is 010's locked
file outright and arm A's prompt is 011's pinned digest.

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
  vendor that **handles personal data** and carries a risk score of **40 or
  more** but **below 70** is likewise sent to **manual review**.
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
census cannot express, as the ordered tuple *(literal, side, sense)* the
harness compares: each numeric bound with an explicit inclusivity word from the
registered vocabulary immediately adjacent to its literal, on the same side,
of the same sense, in the same clause.

| clause | arm A | arm B | inclusivity adjacency |
| --- | --- | --- | --- |
| P1 | "A vendor with a sanctions hit is **rejected**, regardless of anything else." | "If a vendor has a sanctions hit, the outcome is **reject**, whatever else the file shows." | no numeric bound |
| P2 | "Absent a sanctions hit, a vendor registered in an embargoed country … is **rejected**." | "With no sanctions hit, a vendor whose registration is in an embargoed country … is also **rejected**." | no numeric bound |
| P3 | "risk score is **70 or above**" | "carrying a risk score of **70 or more**" | (70, after, inclusive) in both |
| P4 lower | "**40 or above** but below 70" | "risk score of **40 or more** but below 70" | (40, after, inclusive) in both — **fixed in round 2**; the round-1 B read "from **40** up to but not including 70", which put the cue *before* the literal and broke the invariant this table exists to display |
| P4 upper | "40 or above but **below 70**" | "40 or more but **below 70**" | (70, before, exclusive) in both |
| P5 outer | "risk score is **below 70**" | "vendor scoring **below 70**" | (70, before, exclusive) in both |
| P5 gloss (non-P) | "clears **below 70**" | "clears anywhere **below 70**" | (70, before, exclusive) in both |
| P5 gloss (P) | "clears only **below 40**" | "clears only **below 40**" | (40, before, exclusive) in both, byte-identical |

**Verified over the assembled bytes**: arm B's six tuples equal arm A's six,
clause for clause, in order — `(P3, 70, after, inclusive)`,
`(P4, 40, after, inclusive)`, `(P4, 70, before, exclusive)`,
`(P5, 70, before, exclusive)`, `(P5, 70, before, exclusive)`,
`(P5, 40, before, exclusive)`. Arm D's equal these under σ; arm C's are A's
own, reordered with their clauses. **What the invariant costs is stated in
§2.6 and is real**: B's paraphrase now lives in the clause frames and not in
the boundary language, and at four of the six bounds B uses A's own cue word.

### A.3 Arm C — reordered [D-5]

Bodies byte-identical to arm A's; presentation order **(P1, P2, P4, P5, P3)**;
each label travels with its own body.

```
- **P1.** A vendor with a sanctions hit is **rejected**, regardless of
  anything else.
- **P2.** Absent a sanctions hit, a vendor registered in an embargoed
  country — **KP, IR, or SY** — is **rejected**.
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

**Movement:** P3 3→5, P4 4→3, P5 5→4 — **three of five clauses move**; P1 and
P2 keep their positions. This is **not** a derangement, and §2.6 and [D-5]
state why round 2 traded the derangement away.

**Reference resolution**, checked by re-deriving it from the parsed bodies —
**every reference resolves backward, with no residual**:

| reference | in clause at position | resolved by clause at position | backward? |
| --- | --- | --- | --- |
| "unless P4 applies" | P5, position 4 | P4, position 3 | yes |
| "absent a sanctions hit **or an embargoed registration**" | P4 (3), P5 (4), P3 (5) | P1 (1) and P2 (2) | yes, all three |
| "Absent a sanctions hit" | P2, position 2 | P1, position 1 | **yes — the round-1 residual is gone** |

**Uniqueness, by exhaustive enumeration of all 120 permutations and asserted by
a harness test.** Exactly three permutations resolve every reference backward:
the identity (0 clauses move), (P1, P2, P4, P3, P5) (2 move), and
(P1, P2, P4, P5, P3) (3 move). So the registered permutation is the **unique
maximum-movement** permutation under the full constraint set. The same
enumeration confirms round 1's finding that *derangement + every reference
backward* is **empty**: the two properties cannot both be had, and round 2
chose comprehensibility because arm C is a control on which arm E's reading
depends. The round-1 registration (P2, P1, P4, P5, P3) — the unique derangement
under the weaker constraint set — is [D-5]'s alternative (a). §5.3 (iii) reads
a C-collapse against this table.

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
in this file**, exhaustively and verified over the assembled bytes, are nine:
the five clause labels `P1`–`P5`; the `4` in P5's `unless P4 applies`; and
`3166`, `1` and `2` in the token `ISO 3166-1 alpha-2` in the inherited
conventions paragraph. **Four are non-label runs, from two sources**, and
**none equals `40` or `70`**; the clause-body census under §2.6's definition is
empty — which is what §6 C8 clause 5 checks. The preamble's `010` is gone under
`PREAMBLE_DELTA` **[D-16]**, adopted in round 2; §2.5 records what removing it
buys and what it does not.

**Arm E's bound senses, matching arm A's clause for clause** (§2.6 — the side
cannot be preserved when the bound is a name rather than a numeral, and that is
inherent to denaming): `(P3, T_high, inclusive)`, `(P4, T_low, inclusive)`,
`(P4, T_high, exclusive)`, `(P5, T_high, exclusive)`,
`(P5, T_high, exclusive)`, `(P5, T_low, exclusive)` — the same six senses, in
the same six places, as arm A's six literals carry.
