# Ports — what Study 011 took from Study 010, and what changed

Study 011 runs Study 010's registered authoring call many times and counts
coverage. The semantics it counts with — the policy mirror, the record
compiler, the transcript binding, the prompt, the mutation family — are
Study 010's, and they are taken as **bytes**, not as a description. This file
records where each came from, at which digest, and exactly what was changed.

Every source digest below is the file's sha256 in
`studies/010-blinded-oracle/`, and each equals the digest
`studies/010-blinded-oracle/PROTOCOL-LOCK.json` registered for it at lock time.
Worktree and `HEAD` blob were compared by hand and matched for every source
file at the commit this port was taken from — a recorded observation about that
commit, not a check anything re-runs (PREREGISTRATION.md §7 says so, and no
code in this study compares a file to a git blob):

```
commit 9063be5d0d0d42b52477f0968ace2e616ac97086
```

A reader re-checks the whole table with

```sh
sha256sum studies/010-blinded-oracle/harness/policy_mirror.py \
          studies/010-blinded-oracle/harness/records_compile.py \
          studies/010-blinded-oracle/harness/transcript_check.py \
          studies/010-blinded-oracle/transcription/authoring_call.sh \
          studies/010-blinded-oracle/transcription/PROMPT.txt \
          studies/010-blinded-oracle/FAMILY.json
diff studies/010-blinded-oracle/harness/records_compile.py \
     studies/011-authorship-coverage-rates/harness/records_compile.py
```

## The table

| source (in `studies/010-blinded-oracle/`) | source sha256 | destination (in this study) | destination sha256 | changed |
|---|---|---|---|---|
| `harness/policy_mirror.py` | `276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba` | `harness/policy_mirror.py` | `276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba` | no — byte-identical |
| `harness/records_compile.py` | `e58edce30e549953b5263db2e9c230604f9192d060cbde9387585e0679671698` | `harness/records_compile.py` | `6de92175b3f93d563b7e79c60a2e3fd641d96f40cc594fb8c3753c3655c90a1c` | output root parameterized |
| `harness/transcript_check.py` | `42d977c40eed333531c096b9cdba75ac2ecceed5845dd3151f1dc010129bea9d` | `harness/transcript_check.py` | `0c9d7c798fc8738acb05dada3230251c9fba6109e15ed5b6b5ee8a4b2e708218` | golden source parameterized and required; the cwd binding holds every turn context, not one of them |
| `transcription/authoring_call.sh` | `3b8909aae9b0ec2d52f8b8c780c3c6a544f4405dc7d31fd1becf485fcdae251d` | `transcription/authoring_call.sh` | `6e1239f3ea425669e88878dc2b4d3f6eb41ff9ffe859c76479c9bb8dea41a90e` | slot, pins, prompt kind, interpreter and CLI parameterized; interpreter and CLI version checked BEFORE the call; PATH/TMPDIR constructed; recursive home inventory; registry and golden digests stamped per run; credential deleted (seal path plus EXIT/INT/TERM/HUP traps); new-session diff; C7 mode |
| `transcription/PROMPT.txt` | `a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2` | `transcription/PROMPT.txt` | `a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2` | no — byte-identical |
| `FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | `FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | no — byte-identical |

The two byte-identical harness/data files are pinned again in
`harness/PINS.json`, and `score_rates.py` refuses to score against a prompt or
family whose bytes are not those digests. `policy_mirror.py`'s digest equality
is its own check: nothing about the reference semantics was reinterpreted.

**This table is machine-read, and its two columns answer to two different
authorities.** This file is editable in *this* study, so it cannot be the
authority for what Study 010's bytes were: an editor who changes a port here
need only change that row's digit cells to keep the table self-consistent.
`harness/integrity.py` therefore, in order: verifies
`studies/010-blinded-oracle/PROTOCOL-LOCK.json` against the digest
`harness/PINS.json` records in `pinnedFrom.fileSha256` **first**; reads that
lock's `lockedInputs` map; requires every **source** above to be locked there
and both 010's file and this table's source cell to equal **the lock's**
digest; requires every **destination** to equal the digest this table records;
requires the three byte-identical ports to equal 010's *locked* digest on the
destination side too, so "no — byte-identical" is a checked relation and not a
prose cell; and requires the destination set to be exactly those six files, so
a deleted row refuses rather than quietly dropping a check. It also checks the
running interpreter against the registry's `python` member.

`batch.py` runs all of it before it creates a slot, `score_rates.py` before it
reads one, and CI runs the whole harness suite (PREREGISTRATION.md §6 C1).
Editing a port therefore means editing this table in the same commit — and for
the three adapted ports, that table entry is the only record, which is why
§2.3's change list is enumerated and why C3 re-runs the adapted compiler and
mirror against Study 010's published profile.

## What changed, file by file

### `harness/policy_mirror.py` — nothing

Copied byte for byte, docstring included; its section references are Study
010's, and the digest above proves the copy. Study 011 uses both of its
functions: `verdict()` splits accepted records into H and Q, and
`predicate_matches()` decides class membership from a FAMILY.json predicate.

### `harness/records_compile.py` — the output root is an argument

Study 010 owned one `records/` directory and one `RECORDS.md` at the study
root, so the module hard-coded them. Study 011 compiles one tree **per run**,
so:

- the module-level `HERE`, `STUDY`, `RECORDS_DIR` and `RECORDS_MD` constants
  are gone;
- `cmd_compile(raw_path, out_root)` and `cmd_verify(raw_path, out_root)` take
  the output root, and the CLI usage grew a third argument;
- the module docstring says what this study does and does not use it for.

Nothing else moved: extraction (widest parseable array, strict decoder,
duplicate-key and non-JSON-constant rejection), the admission order and its
seven drop codes, `records_md()`, `render()`, and the byte-exact
`read_completion()` are the same lines. `diff` over the two files shows only
the docstring, the constants, and those signatures.

### `harness/transcript_check.py` — the golden capture is an argument, and required

The check logic is unchanged: the `response_item` whitelist, inert-`reasoning`
rule, the exactly-one-registered-prompt and prompt-terminal rules, the leak
denylist, the golden allowlist comparison, the completion byte binding, the
`turn_context` model/cwd binding, the integer-exit-0 rule, and duplicate-key
rejection on every transcript line.

What changed:

- `check()`'s signature is `(session, prompt, completion, call, golden_path,
  model=None)`. Study 010 had `golden_path=None` last, because its single call
  site always passed the one locked capture; here `golden_path` is a required
  positional argument, and the `if golden_path is not None` guard around
  `check_golden()` is gone. A caller cannot omit the allowlist by leaving a
  default in place.
- the `turn_context` **cwd** binding requires EVERY named working directory to
  be the call's own, where 010 required the call's cwd to appear among them.
  Membership admitted a transcript carrying a second `turn_context` for a
  foreign workspace, so PREREGISTRATION.md §3.1 gate 5 ("`turn_context`, where
  present, names … the call's own working directory") was true of the set and
  not of its members. The model clause was already written this way; the two now
  read alike.
- the module docstring records the port and the reason, and names the command
  that takes the recapture (`batch.py capture`).

**Why the golden source had to move.** A golden capture pins one machine's
codex boilerplate — its permission text, its agent identity, its plugin list,
normalized. Study 010's capture is that study's environment; here it would
refuse every honest run. Study 011 therefore recaptures its own before the
batch, with `batch.py capture`, which runs at least two probe-prompt calls
(fewer refuses, both before the calls and at the derivation) and requires
their pre-prompt contexts to reproduce identically after normalization,
refusing any capture carrying a leak token before the prompt. That is Study 010's
own capture procedure (§4: "captured from two independent real runs that
reproduced identically"), repeated rather than inherited. The gate itself is
not relaxed: a run whose pre-prompt context differs from the capture in count,
role, order, or normalized digest is an invalid run, code `transcript-refused`.

### `transcription/authoring_call.sh` — the slot, the pins, the interpreter, the CLI

The invocation is Study 010's, element for element — with the two values noted
below (`PATH` and `TMPDIR`) constructed rather than inherited, which is a
change to what the child gets, not to the shape of the call: `env -i` down to
`PATH`, `HOME`, `TMPDIR` and `CODEX_HOME`; a fresh `HOME` with a fresh
`CODEX_HOME` beneath it; `--ignore-user-config`; an explicit `-m <pinned model>`;
`--sandbox workspace-write -c 'mcp_servers={}'`; an exclusively created scratch
directory checked to be outside every git worktree and free of leak tokens; the
codex binary required to match the pinned digest; the prompt passed as
`PROMPT.txt`'s exact bytes with stdin closed; `completion.txt` extracted only
from a process that exited 0; the same retained slot files.

What changed:

- **arguments**: `authoring_call.sh <scratch-parent> <slot-dir> <pins-json>
  [codex-binary]`. Study 010 hard-coded `call-1` and read
  `PROTOCOL-LOCK.json`; this study runs N calls and registers its pins in
  `harness/PINS.json`. The slot is still created exclusively — an existing
  slot refuses — so no slot is ever written twice. The existence test is
  `-e` OR `-L`: a dangling symlink at the slot path is absent to `-e` and
  present to `mkdir`, and 010's test would have let the wrapper die in `mkdir`
  under `set -e` instead of refusing.
- **exit codes** are distinct so the driver can record why a run failed:
  `0` complete, `1` pre-flight refusal, `10` the call exited non-zero (slot
  retained), `11` other than one session in the isolated home (slot retained).
  Study 010 exited 0 after a non-zero call and let admission catch it; the
  batch needs the difference at the moment it happens.
- **prompt digest**: the wrapper checks the prompt file against the pinned
  digest before calling anything. Study 010 got this from its lock
  verification.
- **prompt kind**: `PROMPT_KIND=registered` (default) uses
  `transcription/PROMPT.txt`; `PROMPT_KIND=probe` uses
  `transcription/PROBE-PROMPT.txt` for the golden recapture, whose own digest
  the registry pins. The recapture uses the probe deliberately: the pre-prompt
  context does not depend on the prompt, and running the registered prompt
  before the batch would show coverage profiles first — the cost Study 010's
  `DEVIATIONS.md` §1 records. `CALL.json` records which kind ran and that
  prompt's digest.
- **interpreter and CLI version, both as PRE-call gates**: helper steps run
  `$PYTHON_BIN` (default `python3`), which must be the implementation and
  version series `harness/PINS.json` pins, checked before anything is called;
  `codex --version` is read from the resolved binary rather than from `PATH`,
  **before** the authoring call, and a version that is not the pinned string
  refuses instead of being recorded for the scorer to reject afterwards.
- **registry and golden digests, stamped per run**: `CALL.json` records
  `pinsSha256` (the registry this run was made under) and `goldenSha256` (the
  golden capture the driver verified at preflight, empty for the probe calls).
  The scorer computes the committed registry's digest itself and refuses any
  other, and refuses any slot naming a capture that is not the one it is
  scoring under — codes `registry-mismatch` and `golden-mismatch`.
- **credential**: `$HOME/.codex/auth.json` is copied when it exists and
  `credentialCopied` records whether it did (Study 010 assumed it), and the
  copy is **deleted** once the call has terminated and the slot is sealed,
  with `credentialRemoved` recording it. Traps on `EXIT`, `INT`, `TERM` and
  `HUP` remove it on the abnormal paths; `SIGKILL` and power loss run no
  handler and PREREGISTRATION.md §2.5 states that residual rather than
  claiming the copy dies however the wrapper dies. Fifty runs must not leave
  fifty copies of a live credential under one scratch parent; only a copy this
  wrapper made is ever removed.
- **slot identity and wall clock**: `CALL.json` gains `slot`, `slotIndex`,
  `startedAt` and `endedAt` (UTC). The scorer never reads them, so
  `RESULTS.json` stays byte-stable; they are retained per slot as descriptive
  evidence.
- **isolation, recorded per run**: `CALL.json` gains
  `isolatedHomeInventory` — the RECURSIVE listing of the isolated home,
  relative paths, sorted — and `operatorHomeSkillsPresent`. The fresh HOME
  is the fix Study 010 found empirically (skills under `$HOME/.agents` reach
  the model), and this study demonstrates the exclusion per run rather than
  asserting it once, with the golden allowlist as the check that bites
  hardest. `score_rates.admit()` requires the inventory to be exactly
  `['.codex', '.codex/auth.json']` with a credential and `['.codex']`
  without one.
- **environment, constructed not inherited**: `PATH` is six fixed system
  directories plus one per-run directory holding a single symlink to the
  pinned binary, and `TMPDIR` is a directory inside that run's own scratch.
  Study 010's line was
  `PATH="/usr/local/sbin:…:/bin:$HOME/.local/bin" … TMPDIR=/tmp`, where
  `$HOME` is expanded by the OUTER shell — so its "scrubbed" child PATH
  ended in the operator's real home, and every run shared one writable
  `TMPDIR`. `CALL.json` gains `environmentValues` (the exact strings) and
  `codexHome`, so a published slot shows what the child actually had.
- **new-session identification**: the run's transcript is the `*.jsonl`
  under the run's `CODEX_HOME` that was **not there before the call** (set
  difference), rather than the only one in the tree. In the isolated case
  the before-set is empty and this is 010's rule unchanged; it exists so the
  §6 C7 negative control, which runs against the operator's real `.codex`,
  can reach its registered golden comparison instead of refusing on a count
  of pre-existing sessions.
- **`ISOLATION=operator-home`**: the §6 C7 negative control, and nothing
  else. It refuses any prompt but the probe, copies and removes no
  credential, takes no inventory of the operator's home, and records
  `isolation` and `homeIsolated: false` in `CALL.json`.
  `harness/batch.py capture-isolation-negative` is its only caller; it
  retains the verdict and a stripped call record always and the context
  digests when the call produced them, deletes the transcript itself, and
  verifies the deletion.

### `FAMILY.json`, `transcription/PROMPT.txt` — copied, not edited

`PROMPT.txt` is the cell; it inlines `policy/POLICY.md`, so no separate policy
file is copied. `FAMILY.json` is read for its six `predicate` members only:
Study 011 applies no patch, builds no pack D, and evaluates no pack.

## What was NOT ported, and why

Everything that existed to make **one unrepeatable draw** trustworthy, and
everything that needed an evaluator:

- `harness/study.py`, `harness/gate.py`, `harness/pnf_check.py`,
  `transcription/transcribe.py`, `source/record_source.py`, `controls/`,
  `packs/` — the arms, the fabrication gate, the PNF projection, the
  acquisition proxy and the controls all belong to the evaluation Study 010
  ran. Study 011 never runs jpack.
- the beacon, the Rekor publication, the witness keys, `DRAW.json`,
  `DEFECT.json`, `FREEZE.json`, and the single-slot zero-retry rule — a rate
  study needs sample size and a preregistered analysis instead (issue #23's
  registered next step says so explicitly).
- `harness/regions_check.py` — it compares the pinned runtime's disposition of
  pack C to the mirror over 44 probes. There is no pack here, so the check has
  nothing to run against; the mirror's agreement with the policy is instead
  exercised directly in `harness/tests/test_coverage_profile.py`.
- `transcription/GOLDEN-CONTEXT.json` — deliberately not inherited, for the
  reason given above.

## New here, not ported

`transcription/PROBE-PROMPT.txt` (the recapture's prompt, pinned in the
registry), `harness/PINS.json`, `harness/batch.py`, `harness/score_rates.py`,
`harness/integrity.py`, and `harness/tests/`. None of them existed in Study
010: it made one call and scored one draw, and this study makes fifty and
counts rates. They are reviewed as their own artifacts, not as ports.
`integrity.py` in particular exists because a digest table that only pytest
checks is not a precondition of anything.

## Registered differences in behaviour

Two, both consequences of counting rates instead of making a draw:

1. **A failed run does not end the study.** The batch terminates that slot with
   a `REFUSAL.json` and continues. Study 010's zero-retry rule protected a
   single completion whose transcript an operator must not be able to read and
   re-roll; here every invocation leaves its own slot, no slot is rewritten,
   and the authoring-failure rate is one of the reported endpoints.
2. **Compiler regeneration has no committed tree to compare against.** Study
   010 compared its committed `records/` to what the retained completion
   compiles to. Study 011 compiles each run into a throwaway directory and runs
   the ported `verify` against it — byte equality, the exact file set, regular
   files only — and publishes a digest of the compiled tree per run, so a
   reader recomputes rather than trusts. A failure is the invalid-run code
   `regeneration-mismatch`.
