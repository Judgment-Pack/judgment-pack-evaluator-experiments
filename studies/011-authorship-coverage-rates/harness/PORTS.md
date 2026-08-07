# Ports — what Study 011 took from Study 010, and what changed

Study 011 runs Study 010's registered authoring call many times and counts
coverage. The semantics it counts with — the policy mirror, the record
compiler, the transcript binding, the prompt, the mutation family — are
Study 010's, and they are taken as **bytes**, not as a description. This file
records where each came from, at which digest, and exactly what was changed.

Every source digest below is the file's sha256 in
`studies/010-blinded-oracle/`, and each equals the digest
`studies/010-blinded-oracle/PROTOCOL-LOCK.json` registered for it at lock time.
Worktree and `HEAD` blob were compared and matched for every source file at the
commit this port was taken from:

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
| `harness/transcript_check.py` | `42d977c40eed333531c096b9cdba75ac2ecceed5845dd3151f1dc010129bea9d` | `harness/transcript_check.py` | `632edad6b215782deac090b22db08d00ebc9b061f6f0992df2a04c45a2e41209` | golden source parameterized and required |
| `transcription/authoring_call.sh` | `3b8909aae9b0ec2d52f8b8c780c3c6a544f4405dc7d31fd1becf485fcdae251d` | `transcription/authoring_call.sh` | `5b5cedfc6f6539e1c9509f1e72f85671c29c94b46d5935adc49221753cf6f36c` | slot, pins, prompt kind, interpreter and CLI parameterized |
| `transcription/PROMPT.txt` | `a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2` | `transcription/PROMPT.txt` | `a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2` | no — byte-identical |
| `FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | `FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` | no — byte-identical |

The two byte-identical harness/data files are pinned again in
`harness/PINS.json`, and `score_rates.py` refuses to score against a prompt or
family whose bytes are not those digests. `policy_mirror.py`'s digest equality
is its own check: nothing about the reference semantics was reinterpreted.

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
- the module docstring records the port and the reason.

**Why the golden source had to move.** A golden capture pins one machine's
codex boilerplate — its permission text, its agent identity, its plugin list,
normalized. Study 010's capture is that study's environment; here it would
refuse every honest run. Study 011 therefore recaptures its own before the
batch, with `batch.py capture`, which runs two probe-prompt calls and requires
their pre-prompt contexts to reproduce identically after normalization,
refusing any capture carrying a leak token before the prompt. That is Study 010's
own capture procedure (§4: "captured from two independent real runs that
reproduced identically"), repeated rather than inherited. The gate itself is
not relaxed: a run whose pre-prompt context differs from the capture in count,
role, order, or normalized digest is an invalid run, code `transcript-refused`.

### `transcription/authoring_call.sh` — the slot, the pins, the interpreter, the CLI

The invocation is Study 010's, element for element: `env -i` down to `PATH`,
`HOME`, `TMPDIR` and `CODEX_HOME`; a fresh `HOME` with a fresh `CODEX_HOME`
beneath it; `--ignore-user-config`; an explicit `-m <pinned model>`;
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
  slot refuses — so no slot is ever written twice.
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
- **interpreter**: helper steps run `$PYTHON_BIN` (default `python3`);
  `codex --version` is read from the resolved binary rather than from `PATH`.
- **credential**: `$HOME/.codex/auth.json` is copied when it exists and
  `credentialCopied` records whether it did. Study 010 assumed it.
- **slot identity and wall clock**: `CALL.json` gains `slot`, `slotIndex`,
  `startedAt` and `endedAt` (UTC). The scorer never reads them, so
  `RESULTS.json` stays byte-stable; they are retained per slot as descriptive
  evidence.
- **isolation, recorded per run**: `CALL.json` gains
  `isolatedHomeEntriesBefore` and `operatorHomeSkillsPresent`. The fresh HOME
  is the fix Study 010 found empirically (skills under `$HOME/.agents` reach
  the model), and this study demonstrates the exclusion per run rather than
  asserting it once — with the golden allowlist as the check that actually
  bites.

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
and `harness/tests/`. None of them existed in Study 010: it made one call and
scored one draw, and this study makes fifty and counts rates. They are reviewed
as their own artifacts, not as ports.

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
