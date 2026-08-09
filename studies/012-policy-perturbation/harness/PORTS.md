# Ports — what Study 012 takes, from where, and what changed

Study 012 runs Study 011's authoring call five ways and compares coverage
across five policy texts. The semantics it counts with are inherited as
**bytes**, not as descriptions, through a three-level chain
(PREREGISTRATION.md §2.2): this file records every port, its digest on both
sides, and exactly what was changed. `harness/integrity.py` machine-reads the
table below and binds each row **to the authority that row actually has** —
§6 C1's three tiers — before any call is made and before anything is scored.

The chain, with every link a pinned digest including the two ends:

```
this file                          (pinned in harness/PINS.json at port time)
    -> Study 011's harness/PINS.json   e0007697…   (pinned in PREREGISTRATION.md §2.2 and in integrity.py)
       Study 011's harness/PORTS.md    783cc9c3…   (same)
        -> Study 010's PROTOCOL-LOCK.json  4966aa82…  (the digest 011 pins, not one this study chooses)
```

The port was taken at commit

```
commit 3b93d3e7917e917516bd55cf4c7f5285c91fbc13
```

which is the squash commit that landed Study 011's final PR (#44) — the four files taken from 011's *own*
harness (tier "none" below) are bound to that commit and to nothing older,
because 011 pinned none of them; §6 C1 states what that costs and what covers
it (cross-vendor review of the diffs, and C3's two replication controls
against published numbers).

## The table

| source | source sha256 | destination (in this study) | destination sha256 | changed |
|---|---|---|---|---|
| `harness/policy_mirror.py` | `276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba` | `harness/policy_mirror.py` | `5c631b7bd062e21564bec0edecdb558768638adff8ffcb33132c5ec32ec0bc5b` | **[D-14]** the two threshold comparisons read `T_low` and `T_high` from the arm's `ARM.json` instead of the literals 40 and 70; signature `verdict(vendor, t_low, t_high)`, no defaults; docstrings record the port. The full diff is published below |
| `policy/POLICY.md` | `e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f` | `arms/A/POLICY.md` | `d47513c3b33d0278df7af38d3257d19abe4d2f9b07166730df1b863f122441f6` | exactly two registered deltas and nothing else: `PREAMBLE_DELTA` at its single occurrence and `CONVENTIONS_DELTA` appended at the registered position (§2.1, §2.6, Appendix A); both published verbatim and pinned by their own sha256 |
| `FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | `arms/A/FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | no — byte-identical to 010's lock on both sides |
| `transcription/PROBE-PROMPT.txt` | `128aaa9a67b601c66b11d8d233a336cca1e064401bb24994929b9965f77f45e7` | `transcription/PROBE-PROMPT.txt` | `128aaa9a67b601c66b11d8d233a336cca1e064401bb24994929b9965f77f45e7` | no — byte-identical; the authority is **011's `PINS.json`** (011 introduced this file; it is in no lockedInputs of 010) |
| `harness/records_compile.py` | `6de92175b3f93d563b7e79c60a2e3fd641d96f40cc594fb8c3753c3655c90a1c` | `harness/records_compile.py` | `6de92175b3f93d563b7e79c60a2e3fd641d96f40cc594fb8c3753c3655c90a1c` | none — taken unchanged; the output-root parameter 011 added already suffices (§2.2) |
| `harness/transcript_check.py` | `0c9d7c798fc8738acb05dada3230251c9fba6109e15ed5b6b5ee8a4b2e708218` | `harness/transcript_check.py` | `64542bc5d6d8f6682a29dee870aa07feb5757db3941c48af581a974c2423a5b2` | the registered-prompt-terminal gate takes **the arm's** prompt bytes instead of one fixed prompt, and an `arm` label travels with the call so a refusal names the arm and the scorer can say `arm-mismatch`; no other check logic changes. Round 5 finding 7: a completion that does not decode raises its own `CompletionUndecodable` so the scorer can say `completion-unreadable` — the checks themselves are unchanged |
| `transcription/authoring_call.sh` | `6e1239f3ea425669e88878dc2b4d3f6eb41ff9ffe859c76479c9bb8dea41a90e` | `transcription/authoring_call.sh` | `d8877f3d78af54a7c43b8c53571b76ac4e0d540048f57ddcdaa7826f3c6b3fee` | §2.7's three permitted differences, plus the one repair §2.7 and this file register — 011's nested `rev-parse` refuses instead of silently meaning the caller's directory — and nothing else. Round 10, finding 6: the registered branch RESOLVES each component of its anchor before creating the next, so a replaced `arms` or `<ARM>` is refused with nothing made outside the study, where `mkdir -p` used to make it first — see below |
| `harness/integrity.py` | `7cecea4b0e86c0f7593d8fe9caaa3e4770aa1ec829b0cda574668449acae2a1c` | `harness/integrity.py` | `c092a1fe301c0aafe35d24ee8eab632045440aee9df5b763c003d07d1fdeae9d` | the three-level chain above; the per-arm artifact checks of §6 C8 and C9; the C10 gate; the [D-20] tree manifest, whose exclusion list `manifest_excluded()` matches as §2.10 item 2 states it — an entry ending `/` is a tree and takes everything beneath it, every other entry is exactly one path (round 9, finding 5). Round 10 finding 1: this file is README step 1's path-invoked entry and it now REFUSES unless the interpreter is running with the safe import path (`-P`, or the `PYTHONSAFEPATH=1` README step 0 exports). Invoking a script by path makes that script's own directory `sys.path[0]`, so the head imports here — `subprocess`, which `verify_bytecode()`'s tree-wide untracked-source scan runs on, among them — resolve from the harness directory before any byte of the file runs, and the module-scope `sys.path.insert(0, HERE)` has no scan before it. The flag is the closure; the in-file refusal only establishes that the operator applied it, and the docstring says so rather than claiming a gate against a hostile tree |
| `harness/batch.py` | `fb513e9f30cc28dcb3748b502e679fea6ec9270d15b730334ac01936f0b1deb7` | `harness/batch.py` | `a6c948951567caebdddb211161c89235ec08d113e63dec89c8a2e168908a7211` | §2.8's registered carryover-balanced call order and its global index; per-arm slot roots; the arm and schedule stamps; the chained ledger and per-slot manifests of §2.9; resume by global index [D-22]; the shortfall surface [D-23]; §6 C7 as a batch precondition. Round 10 finding 1: the same safe-import-path refusal as `integrity.py`, first inside the `__main__` guard and above the untracked-source tripwire — the tripwire cannot precede this file's own head imports, and `subprocess`, the module it asks git what is tracked with, is one of them. Round 10 finding 5: the `no-context` message says "neither registered comparison happened" — `no-context` IS one of the three registered outcomes, so the old wording was false about the registration it was reporting — and `require_isolation_negative()` reads the record's SHAPE as well as its bindings, through the one predicate `score_rates.c7_record_shape_problems()` both gates share |
| `harness/score_rates.py` | `b8239532d1a796b593a602c55126f0a1a363ffce325c8804581727aef2f81984` | `harness/score_rates.py` | `5d33c28b04ed8cf7806850d3835792cb04b75a0fa2c06bf8f8ed58f091a66439` | per-arm scoring against that arm's mirror instantiation and family; the §5 level and contrast verdicts; the §4.5 census; the §4.6 old-edge cross-scoring; the §3.3 partition with `arm-mismatch` and `schedule-mismatch`; the [D-21] stopping rule; §6 C7 as a batch precondition; and [D-21] over the short prefixes §2.8 leaves — an arm the prefix has not reached has no `authoring/` root and is an empty population under the declaration, the empty prefix carries no ledger, and both are admitted only against a declaration that records them. Round 9 finding 2: §5.3's row 5 carries a **fifth** conjunct, `INTERIOR_CLASS` — so an arm whose accepted records were all decided before the score is read no longer confirms; §4.6's two reading cells state what the integers show and no longer a mental state. Round 10 finding 3: that conjunct is **arm E must not read LOW on class 3**, a §5.1 level verdict on arm E and not the §5.2 contrast round 9 wrote — a contrast is INDETERMINATE whenever arm A is not HIGH on the class, so the round-9 form passed vacuously for exactly the degenerate arm it was added to refuse, and `decision_row()` takes the levels to say so; no §5.4 figure moves. Round 10 finding 2: a LOW placement verdict BOUNDS placement at three of thirty and does not zero it, and the row-1 cells say so. Round 10 finding 8: the S5 ceiling is registered as at least one accepted record **and** `|Q| = 0`, so the row-2 cell is true of the empty arm as well. Round 10 finding 4: §5.4's first independence layer is unavailable between two of the six classes — §2.3's class 0 nests in class 1 and class 2 in class 3, correctness is a property of the record, so those coverage indicators are ordered pathwise and independence between them holds at no nondegenerate marginals — so the module gains `NESTED_CLASS_PAIRS`, `class_groups()`, `containment_joint_figures()` and `containment_operating_characteristics()`, the coherent companion whose figures §5.4 publishes beside the independence ones. `decision_operating_characteristics()` is deliberately NOT rewritten: its numbers stay published as the incoherent approximation they are, and its docstring says so. Round 10 finding 7: **S10 is raw — label irrelevant, exactly as S1 is**. The old-edge intersection took the H side of this arm's own mirror, which quarantined a record placed at 40 or 70 and labelled by the old thresholds before arm A's predicates were read — under arm D's (45, 72) mirror old class 2 was unreachable that way altogether and old classes 0 and 1 only through personal-data records — so §5.3 (ii)'s second outcome was blind to the very shape it names and its first outcome's exclusion could not exclude a D that reached both threshold pairs. One expression; the level-endpoint set, the verdict-surface count, §4.3's interval scope, `RESULTS.json`'s shape and `ANALYSIS.md`'s columns are all unchanged. Round 10 finding 9: §2.8's one-UTC-calendar-day rule is **computed rather than asserted** — `utc_day()` publishes, under `schedule.utcDay`, the date set the slots' own retained stamps carry, the count of slots that carried no readable pair, `crossedMidnight` and `oneDayEstablished`, from the same stamp parser S8's duration uses. Nothing refuses on it: §2.8 registers a crossing as a `DEVIATIONS.md` entry and not a stopping rule. No cut, threshold, verdict, decision-table row, endpoint, class or N moves. Round 10 finding 1: the same safe-import-path refusal as the other two path-invoked entries, first inside the `__main__` guard and above the untracked-source tripwire — sharper here than the head imports, because the `subprocess` the scan itself runs on is imported INSIDE the scan and still resolves from the directory the scan polices. Round 10 finding 5: `c7_record_shape_problems()` is added and both gates read it, so the driver's preflight and the scorer's precondition enforce one rule about the members `batch.py` always writes — `registeredOutcomes` equal to the registered three, `deletedByCode` a name-to-digest object (present, never required non-empty: the `no-context` case legitimately deletes nothing), `wrapperExit` an int with bool excluded. The retained SET — the stripped `CALL.json`, `context.json` — is deliberately NOT required, because that would be a change to §6 C7's and §7's registered sentences rather than a code repair; and no predicate here speaks to provenance, since `controls/isolation-negative/` is in `freeze.excluded` and no digest covers those bytes. Round 11 finding 1: §5.3's **row 2** — the class-4 gate §5.3 (iv) gives override force — is now **arm E must not read LOW on class 4**, a §5.1 level verdict on arm E and not the §5.2 contrast every registered statement of it used. The same vacuity round 10 repaired one class over, and worse: a contrast is INDETERMINATE whenever arm A is not HIGH on the class, so the registered form stopped gating anything exactly where an unresolved baseline met a collapsed embargo class, and rows 4 **and** 5 were both published beneath it — CONFIRMED for an arm E that reached the embargo class in none of its thirty runs. `decision_row()` reads the level, the `why` names arm A's own class-4 level beside it because only the withdrawal and not the attribution survives an unresolved baseline, and §5.4's class-4 term becomes a constant factor in both operating-characteristics functions rather than a per-shape one: `row4` is now exactly the marginal times the gate times that term, and no published figure moves at any N. Round 11 finding 4: §4.6's comprehension-collapse row keeps its NAME — registered pre-data, keyed on by fixtures and three assertions — and its GLOSS now carries §4.6's own disclaimer, so the sentence that makes the name a label rather than a finding about the author travels into `RESULTS.json` and `ANALYSIS.md` with it. Round 11 finding 5: §5.3's row 6 and §4.6's third reading fire at `nC >= 3` and `nP < 3`, which permits one or two genuine placement collapses among the four and reads *not LOW* rather than HIGH, so their cells now name the class they hold of and the four-of-thirty floor a not-LOW class may sit at. Round 11 finding 2: §5.4's containment companion still multiplied the two LOW indicators of arm E's classes 2 and 3 — the one nested pair whose classes do not share a marginal here, so round 10's merge was unavailable there and round 10 concluded wrongly that nothing was left to respect. Containment fixes that pair's 2×2 table from its two marginals alone, so the module gains `_ordered_placement()` and `containment_operating_characteristics()` computes row 5's `nP >= 3` and `1 - P(E class 3 LOW)` jointly instead of as a product: the repair ADDS no assumption and removes one §2.3 forbids. `decision_operating_characteristics()` is again deliberately NOT rewritten. The two exact rationals differ by less than 1.1e-34 at N = 30 and collapse to the same IEEE double at every N, so no printed §5.4 figure and no pinned digit moves. Round 11 finding 3: `placement_contrast_verdict()`'s docstring claimed PLACEMENT-COLLAPSE implies COLLAPSE on the same class, and `k_H <= k_raw` orders each arm's OWN two endpoints only — a baseline that places its records in a class and mislabels enough of them reads S1 HIGH and primary MID, so `nP <= nC` is not an invariant and a CONFIRMED batch can carry `nP = 4` against `nC = 3`. The docstring now states the condition the implication needs — arm A HIGH on the PRIMARY — rather than the implication; no executable line changes, because the scorer already computed the two counts independently and correctly. No cut, threshold, class, endpoint, N, decision-table row or published §5.4 figure moves. Round 11 finding 6: §2.8's one-UTC-calendar-day rule is registered over **all 150 slots**, and `utc_day()` established it on any prefix whose dates agreed — a five-slot batch published `oneDayEstablished: true` beside `schedule.complete: false`, eight lines apart in one dict literal, while the docstring cited §2.8's truncated-batch idiom and implemented only the unreadable-stamp half of it. `complete` is now a REQUIRED argument of `utc_day()` and a third conjunct of that flag, and `crossedMidnight` deliberately takes neither conjunct: a prefix that crossed midnight crossed it, and withholding the flag would hide a recorded deviation behind a truncation. §2.8's establishment sentence is sharpened to name the imported half rather than leave it to the cross-reference — a further necessary condition on an "established only when", not a change of rule. The `_epoch()` calendar-range gap found beside it is **named and deferred** in that function's own docstring rather than fixed here: it is unreachable from the instrument (the wrapper's own `date -u` cannot emit an out-of-range field), only an out-of-range HOUR could hide a crossing, and the parser is deliberately shared with §4.6 S8's wall clock, so tightening it turns published S8 durations null — a second published secondary, and a disposition of its own. Round 11 finding 7: `c7_record_shape_problems()`'s docstring gave a FALSE reason for its three members — "the ones written unconditionally on every path" picks out eleven, not three, because `batch.py` writes the whole verdict from ONE `_write_json` call and presence therefore discriminates nothing. The reason is now the true one the docstring's own next paragraph already supplied (the three whose SHAPE is fixed on every path and is checkable without a string diff over a registered paragraph), and the provenance disclaimer states the direction it runs in: a record that FAILS a predicate provably is not the driver's, and one that passes all three has proved nothing about where it came from. Nothing else moves — not the gate predicates, not either error string, not §6 C7's or §7's registered sentences: C7's retention sentence is a claim about the WRITER, it is true of the writer and covered by six real-command assertions, and the code already refuses strictly more than the prose promises. Round 11 finding 8: §5.3 (ii) row 3's GLOSS — "the author placed records at neither threshold pair" — is false of an arm D that placed a record in each of its own four narrow numeric classes in every run and mislabelled every one of them. The new-keyed side is the labelled PRIMARY and the old-keyed side is arm A's disjoint predicates, so such an arm reads LOW on both and fires row 3 while its records are exactly where D's own policy says to put them; the sentence is published, going into `RATES.md` beside the `why`. Round 10 disclosed this residual by name so round 11 would inherit rather than rediscover it, and it is decided here by **narrowing the gloss** to what the two LOW readings support and pointing at D's own S1 placement rates, already published per class as `a_i`. The reviewer's alternative — reading S1 rather than the primary on the new-keyed side of rows 2 and 3 — is declined: it contradicts §5.3 (ii)'s registered asymmetry, gives "new-keyed" two referents inside one four-row table, and changes which populations get which registered outcome. Row 3's condition, `arm_d_outcome()`, the S10 intersection and row 2's gloss are all untouched and correct. No cut, threshold, class, endpoint, N, decision-table row or published §5.4 figure moves for any of the three |
| `analysis/diversity.py` | `16bad4a911ef49b8cc03fcda4ecbfe15f813eba067799c9017e7ba39be5ebf68` | `harness/census.py` | `911eb25773923789e5ddeae20f0bfa68032f932ae9c62fd7e9a21ad8aa8b73ea` | promoted from a post-hoc script to a registered secondary: parameterized by the arm's edge set and family, distances bucketed as §4.5 registers, no clock and no randomness. Round 5 finding 9: X3 publishes the full distinct-value distribution and arm D's old-edge table at the unstated 40/70, X4 publishes the signature groups |

**This table is machine-read, and its columns answer to different
authorities.** This file is editable in *this* study, so it cannot be the
authority for what the inherited bytes were. `harness/integrity.py` therefore,
in order: verifies Study 011's `PINS.json` and `PORTS.md` against the digests
§2.2 registers; verifies Study 010's `PROTOCOL-LOCK.json` against the digest
*011* pins for it; verifies **this file** against the digest
`harness/PINS.json` records for it, so the change list cannot be rewritten
after the review; and then binds each row: tier 1 (the first three rows) to
010's lock on the source side, tier 2 (the probe prompt) to 011's `PINS.json`
on both sides, tier 3 (the three 011-adapted files) to the destination cells
of **011's own PORTS.md** on the source side and to this table on the
destination side, and the four untiered rows to the working files of the
recorded commit. It also requires the destination set to be exactly the
eleven files above, so a deleted row refuses rather than quietly dropping a
check.

## The [D-14] mirror diff, published verbatim

`diff studies/010-blinded-oracle/harness/policy_mirror.py studies/012-policy-perturbation/harness/policy_mirror.py`:

```diff
7a8,32
>
> PORTED FROM Study 010's locked `harness/policy_mirror.py`
> (276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba) with ONE
> enumerated change, registered as [D-14] in §2.2 and published in
> `harness/PORTS.md`: **the two threshold comparisons read `T_low` and `T_high`
> from the arm's `ARM.json` instead of the literals 40 and 70.** The module is
> otherwise line-for-line 010's.
>
> Why one module and not five. Study 010's locked mirror encodes 40 and 70 as
> literals and therefore cannot serve arm D, whose thresholds are 45 and 72. The
> registered resolution is that exactly ONE mirror artifact exists, at one
> destination digest, and each arm's behaviour is keyed to a file that is already
> pinned by sha256 before any call (`arms/<X>/ARM.json`) rather than to unpinned
> code. §6 C8 clause 6 runs the 280-cell landmark grid against this module at its
> registered destination digest, instantiated at each arm's registered pair, and
> requires every arm's verdict vector to equal arm A's elementwise.
>
> Registered property, asserted by `harness/tests/test_mirror.py`: at
> (T_low, T_high) = (40, 70) this module's `verdict()` agrees with Study 010's
> locked module on every cell of the landmark grid — the parameterization changes
> what the comparisons READ, and nothing about what they DECIDE.
>
> There are no defaults on the threshold parameters. A caller that does not say
> which arm it is scoring gets a TypeError, not arm A's numbers: a silent default
> here would let a slot of arm D be labelled at (40, 70) with nothing refusing.
15,16c40,42
< def verdict(vendor: dict) -> str:
<     """The one outcome POLICY.md P1-P5 assigns to a schema-valid vendor."""
---
> def verdict(vendor: dict, t_low, t_high) -> str:
>     """The one outcome POLICY.md P1-P5 assigns to a schema-valid vendor, at
>     this arm's registered thresholds."""
22c48
<     if score >= 70:
---
>     if score >= Decimal(t_high):
24c50
<     if vendor["handlesPersonalData"] and score >= 40:
---
>     if vendor["handlesPersonalData"] and score >= Decimal(t_low):
30c56,62
<     """Does a vendor fall in a FAMILY.json mutation's affected class?"""
---
>     """Does a vendor fall in a FAMILY.json mutation's affected class?
>
>     Unchanged from 010's locked bytes, and deliberately NOT parameterized: a
>     predicate carries its own numbers, instantiated per arm by §2.3's schema in
>     that arm's own `FAMILY.json`. Threading the arm's pair through here as well
>     would give one class two sources of truth.
>     """
```

The functional change is three lines — the signature and the two comparisons —
and everything else is docstring. `harness/tests/test_mirror.py` asserts the
registered agreement with 010's locked module at (40, 70) over the full grid,
and §2.4's negative control besides.

## The wrapper: §2.7's three differences, one registered repair, and one deliberate non-difference

`transcription/authoring_call.sh` is Study 011's wrapper with exactly the
three registered differences — plus the one repair registered at the end of
this section, which is a line of 011's made to mean what 011 meant by it and
none of the three:

1. **the arm id and the arm's prompt path are arguments** —
   `authoring_call.sh <scratch-parent> <slot-dir> <pins-json> <arm-id>
   <arm-prompt-path> [codex-binary]` — and the wrapper writes into
   `arms/<ARM>/authoring/run-NNN/`. The prompt-digest gate is arm-keyed
   (`pins.arms.<ARM>.promptSha256`), an unregistered arm id refuses, a probe
   call passes the literal `none` and stamps `arm: null`, and the wrapper
   itself checks the slot path really is under `arms/<ARM>/authoring/` — so
   §2.7's sentence is true of the wrapper, not only of the driver's
   bookkeeping;
2. **`arm` and `armPromptSha256` are stamped into `CALL.json`**, so a slot
   names the arm it was made under and the exact prompt bytes it was made
   with, and §3.3's `arm-mismatch` is a per-slot check;
3. **its scratch, isolated home and per-run binary directory are named
   `s012-…`** (with the arm id in the name, so five arms' same-numbered runs
   cannot collide under one scratch parent).

Rounds 8, 9 and 10, finding 6 all strengthen the first difference's guard
rather than adding one. Round 8 replaced a comparison of the parent and grandparent
basenames with the whole of §2.7's trailing shape, so `/tmp/C/authoring/run-001`
for arm C and an unrestricted slot name both refuse before anything is called.
Round 9 finished the job: a suffix is not a location, and four trailing
components still accepted `<anywhere>/arms/C/authoring/run-001` under any
absolute root — something §2.7's sentence does not say and [D-23]'s driver
never produces. `$SLOT` must now EQUAL
`$STUDY/arms/<ARM>/authoring/run-NNN`, for the `$STUDY` this script already
resolves from its own location before it does anything else. Equality subsumes
the absoluteness test and refuses embedded traversal; and a `pwd -P`
comparison refuses an `arms`, `<ARM>` or `authoring` component that is a
symlink out of the study, which no comparison of the path's own text can see.
This takes **no new argument and no new environment member**: §2.7's three
differences are unchanged and `batch.py`'s environment contract stays 011's
four.

Round 10 finished *that* job. The physical comparison ran after a single
`mkdir -p "$STUDY/arms/<ARM>/authoring"`, and `mkdir -p` **follows** a replaced
component: with `arms` a symlink out of the study it created two directories
under the foreign target and only then was refused — beneath a comment
asserting that the block "creates nothing outside the study", on precisely the
case the comparison exists for. The registered branch now **resolves before it
creates**, descending the three components below `$STUDY` and making each only
after the one above it has resolved to itself, so a refused path leaves no
directory behind outside the study and that sentence is true of a replaced
component rather than only of the textual refusals. The refusal names the
component it stopped at. A DANGLING symlink at any of the three is refused by
name too, where `mkdir -p` used to fail and `set -e` kill the run with no
`refused:` line — the same `-e` OR `-L` reading the file already applies one
level down at the slot path. The descent is racy in principle — a component
could be swapped between its `cd` and the next `mkdir` — and that is
deliberately not chased: §7 and §9 decline a concurrent adversary on the
operator's own machine, and this is a guard against a tree that is not the
shape §2.7 says it is, not against a process racing this one. The probe
branch's `mkdir -p "$(dirname "$SLOT")"`
is 011's line for the capture directory the driver names and is deliberately
**not** changed: the claim registered here is about the registered branch, and
widening it would be a new claim rather than a repair. Asserted by
`harness/tests/test_batch.py`'s
`test_a_replaced_ancestor_is_refused_before_anything_is_created`, over both
earlier components and the dangling one; round 9's case plants its symlink at
the FINAL component, where `mkdir -p` onto an existing directory creates
nothing, so it could not see this and its assertions are unchanged.

**The one repair, registered here rather than carried.** Study 011's wrapper
reads the repository root as `GIT_ROOT="$(cd "$(git -C "$STUDY" rev-parse
--show-toplevel)" && pwd -P)"` — one line, with the `rev-parse` nested inside
the `cd`. A failed `rev-parse` yields the empty string, `cd ""` succeeds, and
the outer substitution returns `pwd -P`: the CALLER's directory, with status 0,
which the scratch check below then compares against. This study reads the
toplevel first and refuses an empty one. It is the only line of the isolation
invocation that is not 011's byte-for-byte, and it is **not a fourth §2.7
difference**: §2.7's differences are this study's arguments, stamps and naming
— the ways its cell differs from 011's — and a refusal on a study that is not
in a worktree is none of those. Nor is it reachable: the study is a git-tracked
directory in this repository, and `fixtures.standin_study()` runs `git init` so
the suite's stand-in has production's shape, so over every input the README
procedure or the harness suite can supply, 011's wrapper and this one behave
identically. Round 9 made the repair while proving the anchor and recorded it
in `PREREG-REVIEW.md`; round 10, finding 6 found that **this** file — the diff
carrier §2.7 designates — did not carry it, and that is what this paragraph
fixes. The count of permitted differences stays **three**, and §2.7 says the
same in its own words. Asserted by `harness/tests/test_batch.py`'s
`test_a_study_outside_a_worktree_refuses_rather_than_degrading`, which runs the
wrapper from a stand-in study with no worktree and requires the refusal before
any call: until round 10 this was the one refusal line in the wrapper that no
test anywhere reached.

Round 8's rationale for the weaker anchor named [D-23]'s patched population
root as forcing it — the harness tests move that root to drive the real
wrapper against a stand-in tree, and an absolute anchor would have refused
every test slot. It did not force it. The tests now give their stand-in tree
its own study root instead (`fixtures.standin_study()`: the committed wrapper
reached through a symlink, so the bytes that run are the committed bytes and
only the path they are invoked by moves, plus a symlinked harness and a git
repo so the wrapper's own worktree checks see production's shape). The test
moves `$STUDY`; it does not weaken the wrapper for tests or hand it an input
production would not give it.

What the guard still does not establish, said plainly rather than left to be
inferred: the **scheduled index**. The wrapper is told the arm and the slot
path and nothing about §2.8's order, because §2.7 caps its differences at
three and `harness/batch.py` registers the environment contract as 011's four,
"unchanged and not extended"; the index is checked driver-side by
`stamp_slot()` and again by the scorer's `schedule-mismatch` over the retained
bytes. That is scope, not a gap. One caveat travels with the anchor and is
recorded here rather than papered over: the driver derives its root with
`abspath` while the wrapper anchors with `pwd -P`, so a checkout reached
through a symlinked path would refuse every slot rather than run one. The
study's paths are their own physical paths, and for a guard fail-closed is the
right direction to diverge in.

**The non-difference, adjudicated.** An earlier §2.9 sentence had the wrapper
write `SLOT-MANIFEST.json`, while §2.7 caps the wrapper's permitted
differences at exactly three; round 3's review held the registration's letter
over this file's rationalization (finding 5), and the maintainer's
disposition amended the registration to the design with the stronger
argument: the **driver** (`harness/batch.py`) seals every slot immediately
after the wrapper returns, on every exit path including refusals, because
the wrapper is **not the last writer into a refused slot** — `REFUSAL.json`
and the schedule stamps are the driver's — and a wrapper-side seal would
cover every slot except exactly the ones whose retained bytes explain a
failure, while the pipeline-invalid rate is an endpoint (§4.4). §2.9 now
says so in its own words; the seal is taken after the refusal record and the
schedule stamps are written and before the ledger record is appended.

## The three 011-adapted files, taken as 011 left them

`harness/records_compile.py` is byte-identical to 011's (which parameterized
the output root over 010's original — that parameter is exactly what a per-run
throwaway compile needs, so nothing further changed).

`harness/transcript_check.py` keeps 011's check logic — the `response_item`
whitelist, the inert-`reasoning` rule, the leak denylist, the golden allowlist
comparison, the completion byte binding, the `turn_context` model/cwd binding,
the integer-exit-0 rule, duplicate-key rejection — and changes ONE subject:
gate 2's registered prompt is **the arm's** `PROMPT.txt` bytes (§3.1 gate 2),
with an `arm` label threaded through so a refusal names the arm. A slot whose
transcript carries another arm's prompt is refused here and scored
`arm-mismatch` by the scorer, not by this module.

`transcription/authoring_call.sh` — above.

## The four files from 011's own harness

`harness/integrity.py`, `harness/batch.py`, `harness/score_rates.py` and
`harness/census.py` (from 011's `analysis/diversity.py`) are adaptations of
files **no lock ever pinned** — 011's §7 says so plainly. Their source cells
above bind them to the recorded commit's working files; their registered
change scopes are in the table and in §2.2; and their correctness rests on
cross-vendor review of the diffs plus C3's two replication controls, which run
the ported counting and the ported census over retained bytes whose answers
are already published (010's profile `(2, 2, 2, 4, 1, 1)` over 16 accepted;
011's census headline `(2, 6, 2, 24, 26, 2)` over 784).

## What was NOT ported, and why

Everything that existed to make one unrepeatable draw trustworthy, and
everything that needed an evaluator — the same list as 011's port, for the
same reasons: `harness/study.py`, `harness/gate.py`, the fabrication gate, the
acquisition proxy, the beacon/Rekor/witness machinery, the packs and controls.
Study 012 never runs jpack, draws nothing, and counts rates over five cells.

Also not ported: 011's `harness/batch.py` **verbatim** — its single-arm slot
layout (`authoring/run-NNN` at the study root) does not exist here; the
five-arm layout is a registered change, not an accident of porting.

## New here, not ported

`arms/` (twenty files assembled from Appendix A by `harness/arm_assembly.py`,
each digest reproducible from the appendix's own bytes and pinned in
`harness/PINS.json`), `harness/arm_assembly.py` itself (this study's own
assembler, reviewed as its own artifact), `harness/PINS.json`, and
`harness/tests/`. `MIRROR-AGREEMENT.md` and `analysis/mirror2_<arm>.py` are
commissioned artifacts under §6 C10 — pre-assigned readers, every attempt
retained — and are not ports of anything.
