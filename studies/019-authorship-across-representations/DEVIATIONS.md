# Deviations — Study 019

Deviations from the frozen preregistration land here with a reason and a date — never by
editing the preregistration or any frozen artifact. The freeze commit is
51cae0225ea2e9e5679c8e496b39a62e93385278 (PR #69, 2026-08-20).

(none)

## D-1 (2026-08-21) — the prompt reaches codex by stdin, because exec cannot carry it

**What broke.** At batch slots 1–29 of the primary batch (launched 2026-08-20, the
maintainer's explicit go), every arm-B and arm-C call died before codex started:
`/usr/bin/env: Argument list too long`. The wrapper passed the whole prompt as ONE argv
string; Linux caps a single exec argument at 128KiB (`MAX_ARG_STRLEN`). Arm A's registered
prompt is 84,289 bytes and fits; B's (204,333) and C's (206,686) cannot fit, on any Linux,
under any setting — the failure is structural, not environmental. The pre-freeze end-to-end
smoke ran with a stand-in CLI and never pushed a 200KiB argv through a real exec, so the
defect was unreachable until the registered batch itself.

**The ledger cost, retained as it stands.** 29 records: 9 arm-A calls clean, 10 B and 10 C
refused `slot-shape` (wrapper exit 11, codex never invoked, no quota spent). The ledger is
append-only and these records STAND; under §1a they are apparatus failures, excluded from
every denominator, and unequal realised denominators are the registered case (§5's
inversion at realised n). Slot run-010 (arm A) was killed mid-call when the operator
stopped the batch on diagnosis; it left no CALL.json and no seal, so it cannot be
completed by `reconcile_ledger()`'s crash rule — its partial remains (stdout.raw,
stderr.raw) are retained verbatim at `controls/deviation-D1-run-010-killed/` and the slot
directory is removed from `arms/` so resume's ledger/slot bijection holds. run-010's
GLOBAL INDEX is consumed: the registered order continues at the next unrecorded index.

**The fix, and why it is byte-exact by construction.** The pinned codex reads instructions
from stdin when no prompt argument is given ("Reading prompt from stdin..."), and a live
shape test showed the stdin prompt lands in the transcript as the SAME terminal
`message/user` with the same bytes, after the same pre-prompt boilerplate — so the golden
binding and the prompt-digest gate are unchanged in meaning. The wrapper now redirects the
REGISTERED PROMPT FILE into the call (`< "$PROMPT_FILE"`) instead of interpolating a shell
string into argv: the kernel streams the file's exact bytes, the `$(cat …)`/`printf x`
trailing-newline idiom (port difference 8) becomes unnecessary on the call path, and a
prompt of any registered size passes. `CALL.json`'s `stdin` member — previously
`"closed (/dev/null)"` — now records `"the exact bytes of <prompt file>, piped"`, and its
`argv` member no longer lists a prompt placeholder argument. No check bound the old
literal; the schema carries the member either way.

**The anchor cost, named plainly.** `harness/authoring_call.sh` is a frozen, ported,
manifest-covered file; editing it after the freeze changes bytes the freeze commit
anchored. The repair is recorded here — the append-after-freeze channel that exists for
exactly this — and the chain is re-bound in the registered anchor order: the PORTS.md
destination digest for the wrapper row, `ownPorts.sha256`, the regenerated
STUDY-MANIFEST, and `studyManifest.sha256`. The preregistration's own bytes are untouched
and its pin unchanged. A reader comparing the attempt's tree to the freeze commit will
find exactly these files different, and this entry is the account.

**What this deviation does not touch.** No prompt byte, no gold byte, no mutant, no
reference, no scoring rule, no decision row. The batch resumed at the next unrecorded
index under the fixed wrapper; every subsequent slot's admission is recomputed from its
retained bytes by the scorer, which trusts no wrapper record.

## D-2 (2026-08-21) — the freeze-time gates leave `manifest_problems()`, because they made the protocol impossible

**What broke.** The resumed batch (D-1) refused at start: `integrity.verify()` reported
"arms/A/authoring exists and the preregistration registers that NO authoring run exists at
the freeze". The no-prior-attempt and no-prior-authoring validators (round-9 R9-2, round-10
R10-1) were wired inside `manifest_problems()`, which `integrity.verify()` calls at every
driver start and at the attempt itself. As wired, the registered post-freeze protocol was
impossible: a crashed batch could never resume — the ledger it must continue is the "prior
authoring" the gate refuses — and the scorer would have refused every COMPLETED batch for
existing. Like D-1, this was unreachable before a real post-freeze batch: the smoke drove a
stand-in study, and every pre-freeze `verify()` ran on a tree with no batch to refuse.

**The fix.** `freeze_gate_problems()` is called from its REGISTERED seats and no longer
from inside `manifest_problems()`. The registered sentence (R8-2/R8-8/R9-2/R10-1) names
`--check` and `--freeze`: `--freeze` already calls the validators directly before writing
(unchanged), `--freeze-gates` is unchanged, and `--check` now adds them explicitly. What
changes is exactly one thing: `integrity.verify()` — the driver's start check and the
scorer's input gate — no longer runs freeze-MOMENT validators at post-freeze moments.

**The anchor cost.** `harness/make_manifest.py` and `harness/tests/test_batch.py` (the
stand-in CLI now reads stdin, per D-1) are frozen covered files; the chain is re-bound in
the anchor order as with D-1. Recorded here; the tree diff against the freeze commit is
the sum of D-1 and D-2 and nothing else.

## D-3 (2026-08-21) — four slots lost to the operator's own disk janitor

During the batch, the machine's root filesystem twice approached full (D-2's
resume was itself preceded by an ENOSPC crash at run-018 B, whose ledger record
`reconcile_ledger()` completed from the slot's seal exactly as designed). The
operator ran a cleanup loop over the wrapper's scratch parent to keep the batch
alive. Its second revision kept only the single newest scratch entry — but the
wrapper creates TWO directories per slot (`s019-bin-…` and `s019-home-…`, the
latter holding CODEX_HOME and its session files), so the loop deleted the LIVE
slot's session directory mid-call on four slots — **run-038 A and all three
arms of round 42** (run-042 A, B and C; B's ledger record landed after the
loop was already fixed, but its call ran inside the same window). Codex ran and answered; the wrapper then found zero new session
files and refused `slot-shape` (exit 11), which is the correct reading of the
evidence it had. The loop's third revision keeps the four newest entries.

These four records stand as §1a apparatus failures like every other: excluded
from all denominators, counted in the timeout/apparatus rates the control gates
read. They are recorded in this entry because their cause was the operator's
recovery tooling, not the apparatus itself — a reader reconciling refusal
causes should not go hunting in the wrapper for a defect that is not there.

## D-4 (2026-08-21) — the batch crossed the UTC day, as D-1's direct consequence

§2 registers all slots within one UTC calendar day and states in the same
sentence that crossing midnight is a DEVIATIONS entry, not a stopping rule.
This is that entry: slots 1–29 ran on 2026-08-20 UTC (the false start D-1
records); the stop, the wrapper repair and the resume put slots 30–150 on
2026-08-21 UTC. The batch is otherwise the registered order, sequential, one
call at a time, 150 of 150 in the ledger with every record chained and sealed.
