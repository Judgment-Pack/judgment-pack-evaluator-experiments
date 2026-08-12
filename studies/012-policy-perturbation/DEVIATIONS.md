# DEVIATIONS.md — Study 012

Departures from `PREREGISTRATION.md` as it was frozen, recorded under §7. One
entry. Nothing here changes a rate, a level, a contrast, or the §5.3 decision
row; all four are computed from the retained bytes by `harness/score_rates.py`.

## 1. The filesystem filled during the batch, and two slots were lost to it

**What happened.** The batch began at 00:17:55Z on 2026-08-11 (a driver-side
stamp; the earliest *retained* stamp is 00:17:56Z) and the host's
filesystem reached zero free bytes at approximately 01:53Z, with 130 slots
recorded. The cause was the batch's own scratch, not the study: §2.7 gives every
slot an isolated home and a per-run binary directory, so each of the 131 slots
attempted so far had copied the ~42 MB pinned `codex` binary — about 5.5 GB of
scratch against 15 MB of retained study bytes. The driver died writing the
ledger.

**What it cost.** Two consecutive slots, at global indices 130 and 131:

| global | arm | slot | scorer `code` | driver `batchCode` | cause |
|---|---|---|---|---|---|
| 130 | E | `arms/E/authoring/run-026` | `call-nonzero-exit` (exit status 101) | `preflight-refused` | `session.jsonl` truncated mid-write; `transcript_check` could not parse it |
| 131 | C | `arms/C/authoring/run-027` | `session-count` | `session-count` | the run did not produce exactly one new session |

*(Corrected 2026-08-11: an earlier version of this table gave slot 130's code as
`preflight-refused` alone. That is the driver's ledger label; the scorer, which
recomputes admission from the retained bytes, records it as `call-nonzero-exit`.
`RESULTS.json` carries both, as `code` and `batchCode`. The distinction matters
because a reader cross-checking the table against `crossArm.invalidCodes` will
not find a `preflight-refused` key there.)*

Both are environmental. Neither is a fact about the model, the policy, or the
arm it fell in.

**What was done.** Disposable scratch was cleared, the scratch parent was
re-created outside every worktree and re-checked against
`transcript_check.LEAK_TOKENS`, and the batch was resumed with `--resume`, which
verified the recorded 130-slot prefix against §2.8's registered order slot for
slot before creating anything. Slot 131 had in fact run before the crash — only
its ledger append was interrupted — so `reconcile_ledger` completed its record
from its existing seal rather than re-running it, and **the remaining 19 slots
were executed**: 130 recorded + 1 recovered + 19 run = 150. One of those 19,
global index 144 (`arms/E/authoring/run-029`), was refused by the scorer as
`transcript-refused`. The batch reached 150 of 150 with 30 slots in every arm,
and every slot began and
completed within 2026-08-11 UTC — `schedule.utcDay.oneDayEstablished` is `true`,
`crossedMidnight` is `false`, and no slot lacked a readable stamp.

**What was deliberately NOT done.** The two refused slots were retained and not
re-run. Deleting retained bytes to improve a published number is the failure
mode nineteen review rounds were spent making impossible, and an environmental
refusal is still something that happened. They are scored `pipeline-invalid`
under §4.4, which is a registered endpoint. They appear in `RESULTS.json`'s
`crossArm.invalidCodes` under their **scorer** codes — `call-nonzero-exit: 1`
and `session-count: 1` — beside the six `transcript-refused` slots the scorer
found by recomputing admission from the retained bytes rather than trusting the
driver's ledger. That is the whole of `invalidCodes`: 1 + 1 + 6 = 8, and
142 + 8 = 150. *(Corrected 2026-08-11: an earlier version implied slot 130 would
be found there under `preflight-refused`, which is not a key in that object.)*

**Two registered mechanisms held under the failure, and are recorded as having
held.** The ledger survived intact at 130 records with no stale `.partial`,
because round 16 finding 3 replaced a `tempfile.mkstemp` temporary with an
`O_EXCL` atomic write and added a preflight gate against a stale residue. And
every retained byte landed in a `freeze.excluded` path, so the frozen tree
manifest never moved: `harness/integrity.py` verifies
`sha256:9fa37a51…` before and after.
