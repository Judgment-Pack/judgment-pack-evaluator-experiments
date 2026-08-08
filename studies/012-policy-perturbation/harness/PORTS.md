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
| `transcription/authoring_call.sh` | `6e1239f3ea425669e88878dc2b4d3f6eb41ff9ffe859c76479c9bb8dea41a90e` | `transcription/authoring_call.sh` | `bac41d3a960a82e32ec009f493d8153c280fa2591c6abd29e66deb3aa7fe1f04` | §2.7's three permitted differences and nothing else — see below |
| `harness/integrity.py` | `7cecea4b0e86c0f7593d8fe9caaa3e4770aa1ec829b0cda574668449acae2a1c` | `harness/integrity.py` | `fb0c62b009c1de7b77849d137ab0ae68019262affd759fcf16e1a77bb97fb08b` | the three-level chain above; the per-arm artifact checks of §6 C8 and C9; the C10 gate; the [D-20] tree manifest |
| `harness/batch.py` | `fb513e9f30cc28dcb3748b502e679fea6ec9270d15b730334ac01936f0b1deb7` | `harness/batch.py` | `8db070843b6e0dc3ebe1bdedc46ca8dead105688f7e4dd31fcf10f63e25eac4a` | §2.8's registered carryover-balanced call order and its global index; per-arm slot roots; the arm and schedule stamps; the chained ledger and per-slot manifests of §2.9; resume by global index [D-22]; the shortfall surface [D-23] |
| `harness/score_rates.py` | `b8239532d1a796b593a602c55126f0a1a363ffce325c8804581727aef2f81984` | `harness/score_rates.py` | `091265103cf52dcf0fb0f7a97e5b5544805a8cc30c7c2e8a87a8d92b8bfb8447` | per-arm scoring against that arm's mirror instantiation and family; the §5 level and contrast verdicts; the §4.5 census; the §4.6 old-edge cross-scoring; the §3.3 partition with `arm-mismatch` and `schedule-mismatch`; the [D-21] stopping rule |
| `analysis/diversity.py` | `16bad4a911ef49b8cc03fcda4ecbfe15f813eba067799c9017e7ba39be5ebf68` | `harness/census.py` | `fdb8ac0967e0baec29e78ea27a1af4c18b3336fa8de929d218c91802e1110de7` | promoted from a post-hoc script to a registered secondary: parameterized by the arm's edge set and family, distances bucketed as §4.5 registers, no clock and no randomness. Round 5 finding 9: X3 publishes the full distinct-value distribution and arm D's old-edge table at the unstated 40/70, X4 publishes the signature groups |

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

## The wrapper: §2.7's three differences, and one deliberate non-difference

`transcription/authoring_call.sh` is Study 011's wrapper with exactly the
three registered differences:

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
