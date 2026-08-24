# Pre-freeze review record — Study 020

Interim review regime (RFC 0009): the preregistration must carry a recorded cross-vendor
adversarial review — a non-Anthropic model — with a written maintainer disposition per
finding, before the freeze. Rounds land under `reviews/round-N/{PROMPT.md,REVIEW.md}`,
verbatim, with dispositions here. The freeze requires a final round verdict of exactly
`freezable as written`.

**The round-state block, and what reads it (ADR 0005, decision 2 — registered for this study
from day one rather than adopted mid-regime as it was in Study 019).** The lifecycle of a
round is DATA, held once, here, in the fenced JSON block below: per round its number, its
state (`complete`, `awaiting-review`, `awaiting-response`), the verdict it returned, its
severity counts and its finding-id range. **Two** front doors — `README.md` and
`PREREGISTRATION.md` — each carry ONE sentence rendered from this block by
`harness/render_round_status.py`, and the currency suite requires that rendered string of each
of them VERBATIM. (Study 019 had three front doors; its third, `design/POLICY-DRAFT.md`, has no
020 analogue, because 020's policy prose is ported frozen rather than drafted here.) The block
itself is cross-checked STRUCTURALLY against the tree: the `reviews/round-N/` directories, each
verbatim review's finding ids, and this record's own disposition tables and severity columns.
The prose tables below stay for human readers and are **not parsed for their meaning** — the
truth of free prose rests where it rests in every predecessor study, on review. Run
`harness/render_round_status.py --write` when the block moves; the ceremony commit is then
mechanical.

**Two registered facts about the block's current state.**

1. **It is empty of rounds, and that is a legal state here.** No review round has opened. Study
   019's renderer refuses a zero-round block (`the block registers no rounds`) because 019 first
   wrote its block after round 1 already existed. **020's port permits and renders the
   empty-of-rounds block**; every other refusal in that parser — duplicate members at every
   depth, closed object shapes, the closed verdict vocabulary bound to the review prompt's output
   line, the single-open-round rule, 1..N contiguity, and the marker-span reading — ports
   unchanged. The change is registered in `PREREGISTRATION.md` §7, delta 10.
2. **The rendered sentences on the two front doors are hand-written today, and are marked for
   mechanical regeneration.** `harness/render_round_status.py` is 019 machinery and arrives with
   the harness port. Until it does, each front door's sentence is hand-written to be
   byte-identical to what this block renders. **The first act of the harness port is
   `render_round_status.py --write`**, after which the sentences are machine-produced and the
   currency suite holds them verbatim. A hand-written status sentence is exactly the failure mode
   ADR 0005 registers against; it is tolerated only while the renderer does not exist in this
   tree, and it is a `GATE(pre-freeze)` that it stops being hand-written.

<!-- ROUND-STATE-BLOCK
{
 "blockVersion": 1,
 "rounds": [
  {
   "number": 1,
   "state": "awaiting-response",
   "verdict": "DO NOT FREEZE",
   "severities": {
    "BLOCKER": 13,
    "MAJOR": 9,
    "MINOR": 1
   },
   "findings": {
    "first": 1,
    "last": 23
   }
  }
 ]
}
ROUND-STATE-BLOCK -->

## Rounds

| Round | State | Verdict | BLOCKER | MAJOR | MINOR | Findings |
|---|---|---|---|---|---|---|
| 1 | awaiting-response | DO NOT FREEZE | 13 | 9 | 1 | R1-1 … R1-23 |

**Round 1 opened 2026-08-24** on the filled draft (the sweep run, §2.1 filled at `low` /
N = 60, the gate-5 extension landed, the rates published): `reviews/round-1/PROMPT.md`
committed verbatim, this block moved to `awaiting-review`, both front doors re-rendered.
Reviewer: codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only
sandbox, invoked over this repository checkout with the prompt's bytes on stdin.

**Round 1 returned 2026-08-24, the same day: `DO NOT FREEZE`, 13 BLOCKER / 9 MAJOR /
1 MINOR (R1-1 … R1-23)**, committed verbatim at `reviews/round-1/REVIEW.md`. The reviewer
independently reconciled the whole port chain (46 rows, 382 artifacts), the sweep ledgers
and every §2.1 figure, and the study's registered counts before finding against the tree —
the verdict is carried by the findings, not by drift in what was checked. The reviewer is
prepared to author the fresh sealed mutant set in a later round and authored none in this
one. Dispositions follow below as the maintainer's written response; the round closes when
every finding carries one.

## Dispositions

*(One section per round, one written maintainer disposition per finding, landing here when the
round's review does. A round is CLOSED when a written disposition per finding is on the record;
a round whose prompt is committed while its review has not landed is open in the other
direction. The lifecycle is a state read from the round's own artifacts and compared to the
block member-by-member; exactly one round — the highest — may be open.)*

## Round 1 — 2026-08-24

**`DO NOT FREEZE`, 13 BLOCKER / 9 MAJOR / 1 MINOR.** The verbatim review is
`reviews/round-1/REVIEW.md`; the reviewer independently reconciled the port chain, the sweep
ledgers, the §2.1 figures and every registered count before finding, and is prepared to author
the sealed mutant set in a later round. Dispositions land row by row below; a placeholder cell
is a finding the maintainer has not yet answered, and the round stays open until none remains.

| Finding | Severity | Disposition |
|---|---|---|
| R1-1 | BLOCKER | — |
| R1-2 | BLOCKER | — |
| R1-3 | BLOCKER | — |
| R1-4 | BLOCKER | — |
| R1-5 | BLOCKER | — |
| R1-6 | MAJOR | — |
| R1-7 | MAJOR | — |
| R1-8 | MAJOR | — |
| R1-9 | BLOCKER | — |
| R1-10 | BLOCKER | — |
| R1-11 | MAJOR | — |
| R1-12 | BLOCKER | — |
| R1-13 | BLOCKER | — |
| R1-14 | MAJOR | — |
| R1-15 | BLOCKER | — |
| R1-16 | BLOCKER | — |
| R1-17 | BLOCKER | — |
| R1-18 | BLOCKER | — |
| R1-19 | MAJOR | — |
| R1-20 | MAJOR | — |
| R1-21 | MAJOR | — |
| R1-22 | MAJOR | — |
| R1-23 | MINOR | — |
