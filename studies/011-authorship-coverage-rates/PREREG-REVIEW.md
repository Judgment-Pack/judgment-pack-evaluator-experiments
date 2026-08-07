# Pre-freeze adversarial review — Study 011

This file is the complete pre-freeze review record for Study 011. It records
every adversarial round the preregistration and its harness were put through
before any freeze decision: who reviewed, by what method, the verdict verbatim
where one exists, every finding faithfully summarized, and what was done about
each one — with the commit that implemented it. Nothing is discarded: the
rounds that were killed mid-run by the reviewing vendor's content filter are
recorded here with what they did and did not reach, alongside the rounds that
completed.

**Bottom line, stated honestly.**

- **Four completed adversarial rounds.** One three-lens Claude (Opus) critic
  panel and three completed cross-vendor rounds (OpenAI Codex, `gpt-5.6-sol`).
  Each returned a rejection: REJECT for freeze, then REVISE, REVISE, REVISE.
- **Every finding is closed with a disposition.** 32 + 16 + 3 + 11 + 9 = **71
  dispositioned findings**, none disputed, each mapped to the commit that
  implemented it. Every revision round was re-attacked before commit by an
  independent Claude (Opus) checker running the reviewer's own probes; each
  checker's verdict is recorded below with its residuals.
- **The statistics have been independently re-derived clean, repeatedly.** The
  registered Clopper–Pearson vectors, the tier cutpoints (LIGHT first at
  k=46/50, STANDARD first at k=28/50) and the §5 operating-characteristics
  table (0.1121 / 0.4312 / 0.8964 / 0.9999) were recomputed from scratch by
  the cross-vendor reviewer in **five** rounds — the three completed ones and
  both killed ones, each of which got that far before dying — and again by
  each of the four Claude checkers, twice with exact-rational implementations
  importing no study code. Every derivation matched. No numerical finding above
  "minor" has ever been raised, and the one minor numeric error found (§2.4/§9's
  0.9209/0.9114 illustrations) was corrected to 0.9213/0.9119 and pinned by a
  test.
- **BUT the round-4 closures have no COMPLETED cross-vendor verification.**
  Commit `118699c` closed the nine round-4 findings and was re-verified by an
  independent Claude checker — but the fifth cross-vendor round, which existed
  to check exactly that work, was killed by the reviewing vendor's content
  filter before it could assemble findings or a verdict. Three rounds at this
  depth have now been killed the same way (rounds 3, 5-first-attempt and 6
  below). The transcripts are retained; no run was discarded or re-rolled for
  a friendlier answer.
- **One item from a killed round, closed in the commit that adds this file.**
  Before it died, round 6 narrated and reproduced a defect that was open at
  `118699c`: the emission-target disjointness guard resolves `realpath` on
  both sides, which closes symlink aliases but not two *mount* names for one
  directory (this machine exposes `/tmp` a second time under
  `/mnt/wslg/distro/tmp`). The reviewer verified `os.path.samefile()` proves
  the two paths are the same population while the guard's string comparison
  passes. It never became a numbered finding and carries no reviewer severity
  beyond the word "blocker" in the reviewer's own narration. It is recorded in
  full below. **Disposition:** accepted and fixed in the same commit that adds
  this record — `_check_records_target()` now also compares filesystem
  identity (device and inode) against each side's existing-ancestor chain
  (`_identity_overlap()`), the mount-blind twin of the lexical containment
  test; pinned by a live test using the reviewer's own alias where the
  machine exposes one, and by an unconditional unit test of the mechanism
  (`test_batch.py`, `EmissionMountIdentity`). §2.4 and §7 state the
  identity comparison alongside the resolved-path one.

The freeze decision therefore rests with the maintainer, on a record that is
complete about what was checked, what was closed, and what could not be
checked. That is what this review regime is for: it does not produce a
certificate, it produces an accounting.

**Drafting model:** Anthropic Claude Opus (Claude Code), 2026-08-06/07.
**Reviewing models:** Anthropic Claude Opus (three-lens critic panel, Claude
Code subagents) for round 1; OpenAI `gpt-5.6-sol` via OpenAI Codex v0.145.0
(`codex exec`, sandbox `workspace-write [workdir, /tmp, $TMPDIR]`, approval
`never`, reasoning effort `ultra`) for rounds 2–6.

**Commit chain under review** (branch `study-011-coverage-rates`):

| commit | date | what it is | suite |
|---|---|---|---|
| `160c16e` | 2026-08-06 21:31 | the draft under round-1 review | 65 |
| `e2509f5` | 2026-08-06 23:09 | round-1 revision (panel, 32 findings) | 65 → 94 |
| `f917ea7` | 2026-08-07 00:43 | round-2 revision (cross-vendor 1, 16 findings) | 94 → 133 |
| `b345aa0` | 2026-08-07 01:27 | round-3 closure (killed round's 3 gaps) | 133 → 139 |
| `34416f8` | 2026-08-07 02:54 | round-4 revision (cross-vendor 3, 11 findings) | 139 → 153 |
| `118699c` | 2026-08-07 04:15 | round-5 revision (cross-vendor 4, 9 findings) | 153 → 163 |

Suite counts are quoted from the commit messages and confirmed against them.
The current suite was run for this record: **163 passed in 92.58s** on CPython
3.12.11, with `harness/integrity.py` green.

---

# Round 1 — three-lens Claude (Opus) critic panel

**Basis:** commit `160c16e` (the first draft). **Date:** 2026-08-06.
**Reviewer:** Anthropic Claude Opus, three independent lenses run in parallel
as Claude Code subagents, each attacking the committed tree and each required
to reproduce every claim rather than assert it. **Result: REJECT for freeze —
32 findings, 23 of them serious (6 blocker, 17 material, 9 minor).**

**Method.** Each lens read the preregistration, the harness and the tests, then
ran its own probes: the committed wrapper was executed twice against the tests'
stand-in CLI in both credential branches; a one-character drift was introduced
into a throwaway copy of the "byte-identical" `policy_mirror.py` and re-scored;
the golden capture was derived from the batch's own run slots; the registered
recapture command was executed literally; and the Clopper–Pearson vectors were
re-derived with independent exact-rational implementations sharing no code with
`score_rates.py`. The committed tree was left untouched (`git status` clean,
65/65 still passing).

## Verdicts (verbatim, per lens)

Lens 1 (statistics and endpoints):

> REJECT for freeze — two blockers and three material findings, all
> reproducible against the committed draft (which I left untouched; `git
> status` clean, 65/65 tests still pass).

Lens 2 (port fidelity and control sufficiency), closing sentence:

> Recommend rejection at this round — the blocker and the C6/C7 findings all
> change bytes the freeze would otherwise make permanent.

Lens 3 (execute-as-written and enforcement honesty):

> REJECT for freeze. The harness is well-built and the suite is green (65
> passed), but three defects break the culture bar outright.

## What the panel confirmed rather than assumed

Recorded because it bounds what the findings mean: the Clopper–Pearson
registration (§4.3) reproduced exactly under an independent exact-rational
implementation, including the k=0/k=n closed forms and the fixed-halving
determinism recipe; every §4.4 endpoint S1–S9 was traced to a retained
artifact; the probe-prompt recapture premise was checked empirically against
Study 010's retained `session.jsonl` (the four pre-prompt items are CLI
boilerplate, so "context does not depend on the prompt" holds for this CLI);
the three byte-identical ports hashed to Study 010's locked values and both
adapted ports' diffs were read hunk by hunk with no unregistered semantic
change; and §7's independence and contamination disclosures were judged honest
rather than overclaimed.

## Findings and dispositions

The panel's 32 findings were dispositioned in commit `e2509f5`; **none was
disputed** ("every finding reproduced as described"). Several are the same
defect seen from different lenses — 1/11/18 are one defect, 7/10/27 another,
9/19 another, 13/21 another — and are dispositioned as one change each.

| # | sev | finding | disposition | commit |
|---|---|---|---|---|
| 1 | blocker | C6's isolation evidence is a constant: `isolatedHomeEntriesBefore` counts the `.codex` dir the wrapper just made, so it reads 1 in both branches; and `admit()` scores every slot `isolation-unproven` on a credential-less host | **FIXED.** Wrapper records a recursive sorted relative `isolatedHomeInventory`; `admit()` requires exactly `['.codex','.codex/auth.json']` with a credential and `['.codex']` without. Both branches carry information; pollution refuses; the `assertLessEqual(...,1)` tautology test is gone | `e2509f5` |
| 2 | blocker | Four §6/§7 "mechanically enforced" claims are implemented nowhere: the ported-byte digest table as a precondition, worktree≡HEAD-blob, the post-freeze preregistration digest, and §4.2's asserted equal denominators | **FIXED, all four.** New `harness/integrity.py` verifies the whole table on both sides plus 010's `PROTOCOL-LOCK` and the PINS digests, called by `batch.preflight()` and `score_rates.score()`; the HEAD-blob claim is **deleted** and replaced by an explicit "deliberately not claimed" paragraph; the scorer verifies `preregistration.sha256` when non-null; the scorer refuses unless the six class `trials` values are exactly `{V}` | `e2509f5` |
| 3 | material | §5's LIGHT boundary is not frozen — conjoining `c ≥ 0.90` with `CI lower ≥ 0.80` makes the operative threshold a function of V; the 0.90 clause is inert and the study is under-powered for its own decision | **FIXED.** One criterion per tier: exact CP lower bound alone (LIGHT ≥ 0.80, STANDARD ≥ 0.40); the ρ double-charge removed to a single batch-wide `pipelineCaution`; §5 states the cutpoints (k=46, k=28) and commits the P(LIGHT|p) table at V=50 (0.1121/0.4312/0.8964/0.9999) with a plain statement of what N=50 cannot resolve | `e2509f5` |
| 4 | material | The shortfall rule is not free of data-dependence and both guards against a data-dependent N are bypassable with the harness's own flags | **FIXED as far as mechanizable, stated honestly where not.** `--out` removed from the scorer; `declare_shortfall` refuses at ≥ N; terminal gate is exactly-N XOR a declaration matching the contiguous slots. §2.4 now says the registered involuntary causes mostly cannot produce a shortfall, and §7 lists "that a declared shortfall was involuntary" under recorded-but-not-proven | `e2509f5` |
| 5 | material | The advertised resolution is quoted at N=50 but every rate is denominated in V = N − I; §9's headline claims hold only if I = 0 | **FIXED (honesty item).** §2.4's table relabelled V=50 with the V-denomination stated and figures recomputed at V=45 and V=40; §9 rewritten the same way and pointed at §5's operating characteristics | `e2509f5` |
| 6 | minor | §3.3's pipeline-invalid enumeration is not exhaustive over the codes `admit()` can return; `refusal-conflict` is registered nowhere | **FIXED.** §3.3 carries an exhaustive machine-readable table (all 18 codes then extant, plus the two no-code outcomes); the four gates §3.1's iff-list omits are each registered with rationale. A test parses the table out of the preregistration, diffs it against `CODE_PARTITION`, and diffs both against an AST walk of the codes the source can return | `e2509f5` |
| 7 | minor | C7 is registered in detail but has no executable path; performing it as written requires editing a digest-pinned artifact | **FIXED.** `batch.py capture-isolation-negative --scratch-parent DIR`, using a new registered `ISOLATION=operator-home` wrapper mode; no pinned artifact needs editing, the mode is registered in §2.3 and `PORTS.md`, digest re-pinned | `e2509f5` |
| 8 | minor | The registered recapture remedy cannot be run into the registered directory, and `BATCH.json` is overwritten wholesale on `--start` resume | **FIXED, both halves.** `capture` writes into `controls/recapture/attempt-N/` picking the next unused N; `BATCH.json` becomes `batchVersion 2`, append-only per slot, and a resume merges and refuses any slot already recorded | `e2509f5` |
| 9 | blocker | The registered golden-recapture command cannot perform it: `capture-golden` runs no calls, takes no `--scratch-parent`, refuses on re-run — §3.2 is not executable as written | **FIXED.** §3.2 step 1 registers the real command, `harness/batch.py capture --scratch-parent DIR` (one invocation, two probe calls, derive only if they agree); `capture-golden --slots --out` is named as the derivation half alone. README, `PINS.json`, both docstrings aligned | `e2509f5` |
| 10 | material | C7 has no code path, and run as registered the wrapper refuses on session count before any golden comparison, so neither registered outcome can occur; its retention rule exists only in prose | **FIXED.** The wrapper identifies the run's transcript by set difference across the call, so C7 reaches its comparison; the driver orders checks so the comparison verdict is the recorded outcome; retention is code — only `context.json`, `VERDICT.json` and a stripped `CALL.json` are written, the rest digested and deleted, scratch slot removed | `e2509f5` |
| 11 | material | (same defect as 1, from the wrapper/scorer seam) | **FIXED — same change as 1.** §2.3 item 6's "a missing credential is recorded rather than fatal" is now true of scoring too; a wrapper-driven test proves a credential-less machine's slot is admitted | `e2509f5` |
| 12 | material | §2.1's claim that C3 tests the adapted ports "end to end" is false — C3 exercises only `records_compile` + `policy_mirror` + class arithmetic | **FIXED by narrowing (operator decision).** §2.1 no longer claims end-to-end; it names `records_compile.py` as what C3 replicates and says where `transcript_check.py` and the wrapper are exercised instead, and states as a consequence that the registered prompt's transcript shape first meets the ported gate on slot 1. **NOT ADOPTED, deliberately:** the reviewer's extra control running the ported checker over 010's retained call-1 artifacts (the operator chose to narrow rather than couple to 010's session bytes) | `e2509f5` |
| 13 | material | The "no slot after a rate has been computed" gate is defeated by the scorer's own `--out` flag | **FIXED.** `--out` removed from `score_rates.main()`; outputs always go to the study root; passing `--out` is an explicit refusal. Serialization factored into `write_outputs()` so the determinism test can still score into throwaway dirs | `e2509f5` |
| 14 | material | C1 runs only in pytest, not "as a precondition of the batch and the scorer"; §7's worktree≡HEAD-blob has no implementation | **FIXED.** `integrity.py` is called by `batch.preflight()` and `score_rates.score()` as well as CI; §6 C1 rewritten to state exactly what it checks and what it does not. The named scenario — a one-line edit to `policy_mirror.verdict` after CI last ran — now refuses both, proven on a tampered copy | `e2509f5` |
| 15 | minor | C2 reproduces only half of 010's family-applies check — the "the mutation actually changes the pack" clause is dropped | **FIXED.** `FamilyCoherence` gains the dropped clause (each patch applied to pack C must change it); §6 C2 registers both clauses and corrects the overstatement — the control bounds what a *patch* can mean, while a class is a predicate C3/C4 constrain | `e2509f5` |
| 16 | minor | §4.2 says the scorer asserts equal denominators; no such assertion exists | **FIXED.** `score()` collects the six `trials` and raises unless the set is exactly `{V}`; §4.2 describes the assertion rather than asserting construction | `e2509f5` |
| 17 | minor | C4 registers that expected rates and bounds live in the fixtures module; they do not | **FIXED.** §6 C4 names where each expectation actually lives: profiles/drop histogram in `fixtures.py`, the §4.3 vectors in `test_intervals.py`, end-to-end rate/interval/tier expectations in `test_batch.py`, replication pinned in `PINS.json` | `e2509f5` |
| 18 | blocker | (same defect as 1, stated as the no-credential branch being unsatisfiable) | **FIXED — same change as 1.** Both branches demonstrated admitted; `fixtures.build_slot` no longer hardcodes the old field | `e2509f5` |
| 19 | blocker | (same defect as 9) | **FIXED — same change as 8/9.** Prereg, README, `PINS.json`, `PORTS.md`, `batch.py`, `score_rates.py` and `transcript_check.py` now all say `capture` | `e2509f5` |
| 20 | blocker | The golden capture — the gate §6 calls operative — is never bound to its pin and can be manufactured from the batch's own slots (`PINS.golden.sha256` null, never written or verified) | **FIXED.** Bound at both ends: `batch.preflight()` refuses to create any slot unless the golden exists, the pin is non-null and they match; `verify_preconditions()` refuses on the same three before reading a slot; `capture-golden` refuses any directory holding `run-NNN` slots. Four refusal tests including the reviewer's post-hoc derivation | `e2509f5` |
| 21 | material | (same defect as 13) | **FIXED — same change as 13.** No flag writes a rate table outside the study root, so seeing the rates always arms the guard; §2.4 states it that way | `e2509f5` |
| 22 | material | `preflight()` never checks that the golden context exists, so skipping the recapture spends all 50 calls before anything refuses | **FIXED.** `preflight()` calls `require_golden()` before any slot is created; the three-stage test (no golden → refused, no slots; capture taken but pin null → refused; pin registered → slot created) covers it | `e2509f5` |
| 23 | material | The shortfall can never fire for the failure modes it names — continue-on-failure always presents 50 slots | **FIXED as an honesty item.** §2.4 states that a mid-way environment death leaves a full batch with a high pipeline-invalid rate rather than a shortfall, and that the shortfall path is therefore mostly the deliberate stop; §7 records the involuntariness as unproven. The mechanizable guards were added under 4 and 31; the ρ side-effect is fixed under 3 | `e2509f5` |
| 24 | material | `env -i` allowlist: `$HOME` is expanded by the outer shell, so the "scrubbed" child PATH ends in the operator's real `~/.local/bin`, which holds a `jpack` executable | **FIXED, with a flagged strengthening of the operator's decision.** The decision said "plus the resolved directory of the pinned binary" — which on this machine is the very directory holding `jpack`. Implemented instead: a per-run directory holding one symlink to the digest-checked binary, PATH = six fixed system dirs + that directory, deleted after the call. `CALL.json` records `environmentValues` so a published slot shows what the child had | `e2509f5` |
| 25 | material | `TMPDIR=/tmp` is passed unconditionally and the CLI's sandbox writes to `/tmp`, so with a `/tmp`-rooted scratch parent each run's sandbox contains all prior runs' state | **PARTLY FIXED, remainder stated.** TMPDIR is now inside that run's own scratch. What cannot be fixed — the pinned CLI keeps `/tmp` writable with no flag to remove it — is a §7 bullet of its own, with the three things that bound it and the cost the finding identified (the rates are conditional on the author not having used a tool) | `e2509f5` |
| 26 | material | "runs in CI" is false — the repo runs no Study 011 job — and C1 is not a precondition of anything | **FIXED.** A `study-011-harness` job added to CI (integrity + pytest); README's "runs in CI" sentences name that job; C1 also became a run-time precondition under 14 | `e2509f5` |
| 27 | material | (same defect as 7/10) | **FIXED — same implementation.** README step 4 gives the real argv; the "not `session.jsonl`" rule is enforced by code rather than by hand | `e2509f5` |
| 28 | material | No registered resume path after a mid-batch crash, and resuming destroys `BATCH.json`'s record of earlier slots | **FIXED.** Append-only per-slot records; `--start K` merges and refuses any slot already recorded; §2.4 documents the resume path and README shows the argv | `e2509f5` |
| 29 | material | 50+ copies of the operator's live credential are left on disk and nothing cleans the scratch parent | **FIXED for the credential; the rest stated.** The wrapper deletes the copy after the call and records `credentialRemoved`, only ever removing a copy it made. A sentinel-scanning test finds no credential anywhere after a batch, both captures and C7. §2.5 registers that scratch trees are not published and not deleted | `e2509f5` |
| 30 | minor | `capture-golden`'s default `--out` writes into the committed tree and then permanently blocks the registered recapture | **FIXED.** `--out` has no default and refuses without it; a test asserts the refusal and that the registered path is not created | `e2509f5` |
| 31 | minor | `SHORTFALL.json` is a universal bypass of the terminal gate, including for an over-full batch | **FIXED.** `declare_shortfall` refuses when slots present are not fewer than N; the terminal gate refuses an over-full batch, a mismatched declaration, and the both-present case. Three tests | `e2509f5` |
| 32 | minor | README's run sequence names bare script names, a required flag with no default, and outputs the sequence never produces | **FIXED.** The runbook is a runnable block with the real argv of every step in order; outputs name `RESULTS.json` and `RATES.md`; `--emit-records` is named as what produces §8's per-slot `records/`; `conftest.py`'s inaccurate HOME comment replaced by a precise statement | `e2509f5` |

## Independent checker (Claude Opus), before commit

Verdict, verbatim opening:

> CONFIRMED DISCHARGED — 13 of the 14 assigned findings are fully discharged
> against the current tree; 1 (index 28) is discharged on the normal path but
> re-demonstrable on an abnormal-exit path. I re-attempted every original
> defect with the panel's own repro approach and could not reproduce any
> blocker. Full suite: 93 passed (was 65 before the revision), 47.7s.

The checker independently recomputed the C3 replication (accepted 16, H 16,
Q 0, per-class 2,2,2,4,1,1) from Study 010's retained completion and the
registered CP vectors, and confirmed the port digests unchanged. It edited no
file in the study tree. It raised three new defects, none blocking:

- **(a) minor, numeric.** §2.4/§9's "0.9209" (V=45) and "0.9114" (V=40) are
  wrong; the study's own interval code gives 0.9213 and 0.9119. *(Independently
  found by the cross-vendor reviewer in round 2 as finding 14, and corrected
  there.)*
- **(b) minor.** A wrapper death between the credential copy and its removal
  leaves the copy on disk and mislabels the half-slot's exit as
  `preflight-refused`. *(Closed in `e2509f5` itself by the EXIT trap plus a
  wrapper-death test; extended to INT/TERM/HUP in round 2, finding 7.)*
- **(c) observation, already self-disclosed.** Forging only the destination
  column of a `PORTS.md` row makes `integrity.py` accept a drifted file even on
  a row marked byte-identical. *(Closed in round 2, finding 1, by the
  `BYTE_IDENTICAL` rule binding both sides to Study 010's lock.)*

The panel found `93 passed` at check time; the committed revision landed at
**94**, the figure in `e2509f5`'s message and the figure the round-2 reviewer
independently reproduced.

---

# Round 2 — cross-vendor review 1 (COMPLETED)

**Basis:** commit `e2509f5`. **Dates:** review 2026-08-06, revision committed
2026-08-07. **Reviewer:** OpenAI `gpt-5.6-sol` via Codex v0.145.0, `codex exec`,
sandbox `workspace-write`, reasoning effort ultra. Transcript retained at
`scratchpad/codex-review-011.txt` (198,599 tokens; exit 0).

**Method** (from the prompt, retained in the transcript): execute-as-written
walkthrough of the preregistration and README; an enforcement-honesty audit of
every §7 "mechanically enforced" claim; the one-byte-drift attack on a
throwaway copy; independent re-derivation of the CP vectors and the §5 table;
the isolation story end to end; and verification of the byte-identical ports
against Study 010's `PROTOCOL-LOCK.json` with every hunk of the two adapted
ports read against 010's originals.

## Verdict (verbatim)

> Verdict: **REVISE**. I found five blockers, seven material findings, and four
> minor findings. The committed study tree was never modified.

and, closing:

> **REVISE.** The correct Clopper–Pearson arithmetic, clean adapted ports,
> passing 94-test suite, and successful simple drift refusal are not enough to
> freeze. The current harness can authenticate altered port semantics without
> consulting Study 010's locked input map, redefine the cell through alternate
> pins, accept a one-run or post-batch golden that changes admission, and crash
> or silently mispartition on malformed refusal evidence. Those are
> freeze-blocking failures in the study's core lineage, population, and
> execute-as-written guarantees.

## What the reviewer found clean (finding 17, severity none)

The required destination-only one-byte attack worked (batch and scorer both
exit 1, no slot, no results); all six Study 010 source bytes and the
corresponding commit blobs matched their lock entries; 011's prompt, family and
mirror are byte-identical to 010's; every diff hunk of both adapted ports was
the registered change and nothing more; C3 still reproduced 16/16/0 with class
counts (2,2,2,4,1,1); the literal invalid-code set matched the prose and
`CODE_PARTITION`; apart from S9 every registered endpoint was reconstructible
from retained data; **94 passed in 52.35s**; and the CP vectors, the k=46/k=28
cutpoints and the P(X≥46) operating characteristics all reproduced under
independent arithmetic.

## Findings and dispositions

All sixteen fixed in `f917ea7`; **none disputed**.

| # | sev | finding | disposition | commit |
|---|---|---|---|---|
| 1 | blocker | C1 does not bind the ports to Study 010's lock — `integrity.py` compares 010's current sources to the editable `PORTS.md`, never to `lockedInputs`. A coordinated edit of 010 + 011 + the row's two digest cells passed integrity, batch dry-run and scorer | **FIXED.** Order reversed: `PROTOCOL-LOCK.json` verified against `PINS.pinnedFrom.fileSha256` **first**, then every `PORTS.md` source row must equal the lock's digest on both the file and the table's own cell; new `BYTE_IDENTICAL` rule binds the three byte-identical destinations to the lock too. Four tests including the reviewer's exact attack | `f917ea7` |
| 2 | blocker | Alternate `--pins` registries redefine the entire cell (a probe published `model: alien-model`, `registeredRuns: 1`), and `preregistration.sha256: null` is treated as permission to skip the freeze check | **FIXED.** The wrapper stamps `pinsSha256` into `CALL.json`; the scorer computes the committed registry's digest itself (`REGISTRY_OF_RECORD`, no flag) and scores any other slot `registry-mismatch`. A null `preregistration.sha256` is now a refusal in **both** batch preflight and scorer preconditions. Five tests | `f917ea7` |
| 3 | blocker | One capture passes the registered two-capture golden gate (`capture --runs 1` derived a golden from a single slot) | **FIXED.** `MIN_CAPTURE_SLOTS = 2` enforced at the derivation (`capture_golden`), not only at the calls; `--runs 1` and `--min-slots 1` both refuse. Three tests | `f917ea7` |
| 4 | blocker | A post-batch golden changes which runs are valid — the scorer reads only the current golden against the current mutable pin; a slot went valid 0 → 1 | **FIXED.** The batch passes the preflight-verified digest to the wrapper, which stamps it per slot; `admit()` refuses any slot whose stamp is not the golden being scored under (`golden-mismatch`, checked before the transcript gate). Test reproduces the attack and shows valid 4 → 0 | `f917ea7` |
| 5 | blocker | Malformed `REFUSAL.json` defeats scorer totality: a directory raised `IsADirectoryError`, `[]`/`null` raised `AttributeError`, and `{}` / `{"code": null}` let an otherwise honest run enter V as valid | **FIXED.** `batch_refusal_code()` reads the file through the duplicate-key-rejecting loader **inside** `score_run`'s total path; every malformed shape scores `scorer-error` (pipeline-invalid, enumerated) and the rest of the tree still scores. The `{}` and `{"code": null}` cases are now refusals: an unexplained termination is not a sample. Three tests, nine shapes | `f917ea7` |
| 6 | material | C6's advertised environment admission checks are absent — `admit()` never validates `codexHome`, `environment`, `environmentValues`, `stdin`, `credentialRemoved`, PATH construction, TMPDIR placement or scratch relationships | **FIXED.** New `check_environment()` makes every C6 clause an `isolation-unproven` refusal, including a child PATH of exactly the six system dirs plus one absolute per-run binary dir outside the home (010's actual defect), TMPDIR inside the run's own scratch, stdin closed, and `credentialRemoved` exactly when `credentialCopied`. §6 C6 rewritten as the enforced list with the honest caveat that these are checks on a self-reported record | `f917ea7` |
| 7 | material | Credential cleanup does not cover every exit path — SIGKILL to the process group left the copy; "however it dies" is false | **FIXED, with the claim corrected.** Traps on EXIT/INT/TERM/HUP through one idempotent remover, each handler exiting 128+signal; §2.5 names exactly which deaths are covered and states SIGKILL and power loss as unpreventable with the manual remedy; §7 gains the residual as its own "not prevented" bullet | `f917ea7` |
| 8 | material | C7 can return success outside its registered outcomes (a `no-context` call returned 0 with two files, violating "exactly three files"), and cleanup uses `ignore_errors=True` without verifying absence | **FIXED.** `no-context` becomes a third registered outcome returning non-zero; retention stated exactly (verdict + stripped `CALL.json` always, `context.json` when the call produced one); deletion is verified after `rmtree` and refuses naming the path. Two tests | `f917ea7` |
| 9 | material | The registered interpreter is not the README interpreter — `PINS.json` registers CPython 3.12.11, no code reads it, and bare `python3` here is 3.8.20 | **FIXED.** `PINS.json` gains a `series` member read by new `verify_interpreter()`, run inside `integrity.verify()` so preflight, scorer and the standalone check all enforce it; the wrapper checks `$PYTHON_BIN` before calling anything; README gains step 0 and every command runs `"$PY"`. Patch level deliberately not enforced, stated in §2.6 | `f917ea7` |
| 10 | material | README's dry-run sequence is reversed — the real 50-run command precedes the "dry run first" command | **FIXED.** Dry run precedes the batch with the reason in a comment; runbook renumbered 0–8 with the freeze step and the "PINS.json is not edited after this point" note | `f917ea7` |
| 11 | material | S9 is not estimable for every counted slot — a wrapper exit-1 slot has `REFUSAL.json` only, and the ledger deliberately carries no clock | **CLAIM FIXED** (the §7 discipline). §4.4 S9 registers its denominator explicitly — the slots that reached the call — and requires the analysis to report "over the M of N slots that reached the call" with N−M named. §2.5 gains the matching retention paragraph. No code claims a duration never recorded | `f917ea7` |
| 12 | material | The row-level tier mapping is not a total function: classes overlap, no composition rule, no default for a row matching none | **FIXED in code and prose.** §5 registers two clauses — strictest tier among matched classes; FULL for a row matching none — implemented as `row_review_tier()`, which also refuses an unregistered tier. §5 states that this study scores no rows: the function is the registration of the product rule. Four tests including the reviewer's risk-70 example | `f917ea7` |
| 13 | minor | CLI version is not a pre-call gate — `--version` is read only after the authoring call | **FIXED.** Read immediately after the digest check and before the call; any string but the pinned one exits 1. Test asserts exit 1, no slot, and via the stand-in's counter that no call was made | `f917ea7` |
| 14 | minor | The shortfall perfect-coverage illustrations are numerically wrong (0.9209/0.9114 should be 0.9213/0.9119) | **FIXED.** Both corrected in §2.4 and §9 and made non-regressible: `RegisteredIllustrations` asserts the code-computed four-decimal bounds for V ∈ {50,45,40} appear in the preregistration and that neither superseded value survives anywhere in it | `f917ea7` |
| 15 | minor | Interval-reporting scope is inconsistent between §4.3 and the scorer | **FIXED by choosing and registering the wider scope.** §4.3 registers one frozen list (every rate denominated in V or N; none for the mislabel share or record-level pooled quantities); a test walks `RESULTS.json` and requires the `ci95`-carrying set to be exactly that list | `f917ea7` |
| 16 | minor | "Policy inlined verbatim" is byte-inexact — `POLICY.md` ends in LF, the prompt carries those bytes with the final LF removed | **FIXED.** §2.1 states the exact relation; "verbatim" is gone; the note records that 010/011 comparability does not turn on it because the prompt is byte-identical and pinned on both sides. `InlinedPolicy` asserts all four facts | `f917ea7` |

## Independent checker (Claude Opus), before commit

> All five BLOCKERS from codex-review-011.txt are discharged against the current
> tree; the enforcement each one named is now real code that refuses under my
> own reproduction of the reviewer's attack.

The checker reproduced each blocker's attack on throwaway copies of **both**
study trees, spot-checked four materials with their original repros, ran the
suite green at 133, and independently reproduced the C3 profile, the CP vectors
(50-digit bisection, to 12 places), the k=46/k=28 cutpoints and the P(LIGHT|p)
table.

**One residual, recorded and not closed at that commit:**

> ONE RESIDUAL, material not blocking: PREREGISTRATION.md:397 and the
> corresponding §7 bullet claim that a registry 'that changes N is refused by
> terminality before a slot is read', but an alt registry differing only in
> batch.runs set equal to the slots actually on disk passes terminality and
> publishes (I got valid 1, registeredRuns 1, rate 1.0, ci95 [0.025, 1.0] from a
> single slot against a committed N=50).

This is the same defect the cross-vendor reviewer raised independently two
rounds later as round-4 finding 2 (blocker), and it is what forced the
structural change in `34416f8`. It is recorded here as evidence that the
checker layer catches what the round it belongs to does not.

---

# Round 3 — cross-vendor review 2 (KILLED BY THE VENDOR'S CONTENT FILTER)

**Basis:** commit `f917ea7`. **Date:** 2026-08-07. **Reviewer:** same
configuration. Transcript retained at `scratchpad/codex-review-011-r2.txt`
(744 KB; **236,858 tokens**; exit 1).

**How it ended.** The run was terminated by the reviewing vendor's content
filter, repeated verbatim at the tail of the transcript:

> ERROR: This content was flagged for possible cybersecurity risk. If this
> seems wrong, try rephrasing your request.

(followed by an enrollment link for the vendor's authorized-security program).
The flag fired while the reviewer was displaying diffs of its own throwaway
tamper probes — the one-byte drift in `policy_mirror.py` and the edited
`PORTS.md` digest rows. **No verdict was produced. No numbered findings were
produced.** The final task-list state shows four of six tracks complete:

```
✓ Inspect revision history, repository state, and governing docs
✓ Re-run and extend all five Round-1 attacks on throwaway copies
✓ Execute README and preregistration walkthrough against the commit
✓ Re-derive statistics and reconcile section 3.3 return-code partition
→ Audit new stamping/admit/lock-chain logic, tests, and Section 7 claims
• Run full suite and targeted probes; synthesize numbered findings and verdict
```

**What was recovered.** Three things, all in the retained transcript:

1. **The round-2 closures verified on their literal cases.** The five blockers'
   original attacks were re-run on throwaway copies and refused.
2. **Every registered statistic re-derived clean**, printed in the transcript:
   the six CP vectors at n=50; the perfect-coverage bounds at V=50/45/40
   (0.9289 / 0.9213 / 0.9119 — the corrected values); LIGHT first at k=46
   (L=0.80766, prior 0.78186); STANDARD first at k=28 (L=0.41254, prior
   0.39324); and P(LIGHT) = 0.1121 / 0.4312 / 0.8964 / 0.9999.
3. **Three neighboring defects**, named in the reviewer's last complete
   message (verbatim):

   > The literal regression cases now pass, but three neighboring variants do
   > not: alternate pins can publish a selected/reclassified population,
   > duplicated evidence passes the two-capture derivation, and a dangling
   > `REFUSAL.json` symlink is treated as "no refusal" and admits the slot. The
   > independent CP/tier/operating-characteristic re-derivation matches every
   > registered number.

**What was not recovered:** severities, file/line citations, the §7
line-by-line audit, the new-mechanism regression hunt, and the verdict. The
three defects were treated as blocker-class by the maintainer and closed
immediately.

## Findings and dispositions

Closed in `b345aa0`. Each gap was **reproduced first** on a throwaway copy
(`cp -r` into a scratch tree with a symlink to Study 010 so `integrity.verify`
resolved; the copy was deleted afterwards and the committed tree was never
written to during reproduction), with the pre-fix behaviour recorded.

| # | gap | reproduction before the fix | disposition | commit |
|---|---|---|---|---|
| 1 | A library-level registry parameter still reaches a published `RESULTS.json` | `score(..., registry_sha256=alien)` + `write_outputs(results, STUDY)` published a study-root `RESULTS.json` reading "valid=2 of 2" with the alien registry as the cell | **CLOSED.** `score_registered()` becomes the registered interface — no registry parameter, `main()` calls it and nothing else, the committed `PINS.json` digest computed inside, no environment read (asserted from source). The override survives only for library callers who do not publish: `score()` stamps `cell.registryOverride` and `write_outputs()` refuses — in the study root or anywhere else — both a result carrying an override and a dict that never came through `score()`. §7 states the ceiling (a source edit or in-process rebinding is not refusable by a check inside that file) | `b345aa0` |
| 2 | Duplicated capture evidence passes the two-capture derivation | `capture-golden` over `capture-001` copied to `capture-002` returned 0 and derived a golden from `['capture-001','capture-002']` | **CLOSED.** `require_distinct_sessions()` runs inside `capture_golden()` before the contexts are compared and refuses when any two capture slots share `session.jsonl` bytes, the transcript's own session id, or `CALL.json`'s `(startedAt, endedAt, cwd, home)`. Checked on **raw retained evidence only**, never on the normalized digests two honest independent calls are supposed to share. Both tests fail when the check is stubbed out | `b345aa0` |
| 3 | A dangling `REFUSAL.json` symlink is read as absence | dangling link → `valid=True, code=None, batchCode=None`; a symlinked `completion.txt` gave the misleading `no-completion` | **CLOSED with the general rule, not the narrow one.** New enumerated code `slot-symlink`; `symlinks_in()` walks the tree with `followlinks=False` so a dangling link arrives among the names; evaluated as `admit()`'s **first** check so no later gate can be steered by a link; `score_run()` reads `REFUSAL.json` only for a non-symlink slot; `collect_slots()` collects a symlinked `run-NNN` as a slot so it is named rather than punching a hole in contiguity | `b345aa0` |

**Note on verification for this round.** This round's closures were not put
through a separate Claude checker task; instead each gap was reproduced before
the fix and the invariants were re-verified after (C3 replication 16/16/0 with
per-class (2,2,2,4,1,1); the registered CP vectors and V=50 table; the
byte-identical port digests bound to 010's `PROTOCOL-LOCK.json` — 43 passed).
Independent verification arrived in the next round: the completed round-4
review re-ran all **eight** historical closures itself and reported them passed
(its finding 1, severity none).

---

# Round 4 — cross-vendor review 3 (COMPLETED)

**Basis:** commit `b345aa0`. **Date:** 2026-08-07. **Reviewer:** same
configuration. Transcript retained at `scratchpad/codex-review-011-r3.txt`
(516,595 tokens; exit 1 — the filter fired *after* the findings and verdict
were written, so the review is complete). The findings block is also extracted
at `scratchpad/review-011-r3-findings.txt`.

**Method:** re-run all eight historical closure cases on throwaway copies, then
probe the nearest variants the committed tests do not cover; hunt regressions
introduced by the two revision commits; end-to-end execute-as-written
walkthrough; independent statistics; §7 line-by-line.

## Verdict (verbatim)

> ## Verdict: REVISE
>
> The eight historical attacks are closed on their literal test cases, but the
> registry/publication closure fails immediately next door: the official
> scoring command can publish an alternate N and family, and the writer's
> mutable marker can be cleared without changing code. Those paths permit a
> meaningful-looking `RESULTS.json` that is not the registered study. The FIFO,
> resume, output-overlap, admission, and exact-command gaps independently
> prevent the preregistration from being executable exactly as written. Study
> 011 must not freeze at this commit.

## Clean checks recorded by the reviewer

Full suite **139 passed in 67.31s**; worktree clean; `integrity.py` green on
CPython 3.12.11; §3.3 complete at the code-table level (all 21 source-returned
refusal codes matching `CODE_PARTITION` and the prose table); no
capture-identity regression on the registered path (identical coarse timestamps
alone and a shared cwd alone do not collide — only an off-protocol pair sharing
the entire tuple is rejected); §7's "recorded but not proven" and "not
prevented" statements accurate across all ten listed items; and the full
statistical re-derivation matching (CP vectors, k=46 at L=0.8076572 with k=45 at
0.7818646, k=28 at 0.4125441 with k=27 at 0.3932420, and the P(LIGHT|p) table).
Finding 1 (severity **none**) records the eight literal closures passing:
`8 passed in 5.87s`.

## Findings and dispositions

Findings 2–12 closed in `34416f8`; **none disputed**. Finding 1 is the
severity-none record of the eight historical closures and needed no action
beyond preservation (the `slot-symlink` code and message were kept verbatim so
case 8 still closes on the same code).

| # | sev | finding | disposition | commit |
|---|---|---|---|---|
| 1 | none | All eight literal historical closures passed; statistics re-derived clean | **Untouched and re-verified.** The eight cases still pass; C3 and every §4.3/§5 value independently recomputed identical to the reviewer's table | — |
| 2 | **blocker** | The registered scoring command still accepts pins/family paths: a registry identical to the committed one except `batch.runs = 1` made the public scorer publish `registeredRuns: 1, valid: 1, registryOverride: null`; an alternate family likewise changed the published class definitions | **FIXED as directed.** `score_registered(slots_dir, records_dir=None)` takes no path but the slot tree; registry, family, prompt, golden and output root all derive from the module's own location. `_parse_score()` replaces `_argument()`: only `--slots` and `--emit-records` are accepted, an unknown argument refuses instead of being ignored, a flag given twice refuses, and each withdrawn flag (`--pins`, `--family`, `--prompt`, `--golden`, `--out`, `--registry-sha256`) names itself in the refusal. Two new tests including the reviewer's exact registry over a one-slot batch | `34416f8` |
| 3 | **blocker** | `write_outputs()` is not a publication boundary — it trusts the mutable dict member `cell.registryOverride`; setting it to `None` without editing or rebinding anything published both files to an arbitrary directory | **FIXED as directed.** Public `write_outputs`/`emit_records` deleted. `_write_outputs(results)` is module-private, has no output-directory parameter (study root fixed inside), and is called only by `score_registered()` on the result of the same call — asserted by an AST test over the source and by `assertFalse(hasattr(score_rates,'write_outputs'))`. It re-derives the committed registry digest, the registered N and every pin from the tree, so the reviewer's mutation is refused on **what the tree says**, not on a member | `34416f8` |
| 4 | material | "Regular files and directories only" checks only symlinks: a slot holding `unused.fifo` stayed valid, and a FIFO named `REFUSAL.json` blocked `open()` — `score_run()` was still alive after a second and had to be terminated | **FIXED.** `symlinks_in()` becomes `slot_irregularities()`; every entry and the slot root is classified by `os.lstat` **before anything is opened**; new enumerated `slot-irregular` covers FIFO, socket, character/block device, door and unstattable entries, with `slot-symlink` kept for links so historical case 8 is undisturbed. New tests place FIFOs at four paths and re-run each case in a child process with a 20s join to prove it returns | `34416f8` |
| 5 | material | A dangling planned-slot symlink crashes resume outside the registered refusal path — existence tests return false, then `os.makedirs()` raises an uncaught `FileExistsError`, leaving `BATCH.json` unadvanced | **FIXED.** `preflight()` uses `os.path.lexists()`, so the link is a slot that already exists and the batch refuses through the registered path before spending a call; `refuse_slot()` raises a `BatchError` rather than a bare `FileExistsError` if ever reached with a non-directory; the wrapper's own test gains `|| [ -L "$SLOT" ]`. Test asserts exit 1, link untouched, `BATCH.json` byte-identical, no new slot | `34416f8` |
| 6 | material | `--emit-records` can mutate the population after publishing it: `--emit-records <slots>/run-002` published, then created a phantom slot, after which re-scoring refused because a full batch and `SHORTFALL.json` coexisted | **FIXED as directed.** `_check_records_target()` requires the emission directory to be disjoint from the slot tree in both directions and runs **first** — before anything is scored and before results are written — so a bad target refuses the whole command rather than after publication. `_emit_records()` reads only each slot's `completion.txt` and writes only under the validated target. Test covers four bad targets | `34416f8` |
| 7 | material | Transcript cwd binding is weaker than registered — every named model must match, but cwd only has to appear *somewhere* in the set; a second `turn_context` naming `/wrong/foreign/cwd` left the slot valid | **FIXED by tightening the code** (the option that keeps §3.1 true as written): `check()` now requires `cwds == {call['cwd']}`, symmetrical with the model clause, and reports the offending set. `PORTS.md` records the change and the new digest | `34416f8` |
| 8 | material | Multiple C6 clauses accept contradictory evidence: `cwd == home` is missed because `_under()` tests strict descendants; relative paths are admitted despite the "resolved" claim; `newSessionCount: true` passes because `True == 1` | **FIXED, all three.** `_same()` added so `cwd == home` refuses in both directions; `_resolved()` requires home and cwd absolute and already normalized; `newSessionCount` must be the integer 1 with `isinstance(bool)` excluded. §6 C6 registers each of the three explicitly; three new tests | `34416f8` |
| 9 | material | The governing recapture commands and the recovery path are not executable as registered — §3.2 invokes `harness/batch.py` directly (shebang resolves 3.8.20 here) while `capture-golden` and `shortfall` bypass interpreter, freeze and integrity preflight entirely; two registered-prompt fixture slots renamed `capture-001/002` derived a golden under 3.8.20 | **FIXED.** §3.2 step 1, its parenthetical and §6 C7's command all read `"$PY" harness/batch.py …`; `capture_golden()` and `declare_shortfall()` now run `verify_ported_bytes()` and `require_freeze()`; `capture_golden()` also verifies per capture slot that `CALL.json` records `promptKind: probe` at the pinned probe digest, since a directory name is not evidence of which prompt was answered. Two new tests | `34416f8` |
| 10 | material | "Registered and committed before slot 1" is not mechanically enforced — `require_golden()` checks existence, non-null pin and digest equality only; commit-before-call is an operator instruction | **FIXED by splitting the claim.** The enforced half is kept and stated as such (pin non-null, file present, agreement, per-slot stamps, and the driver refusing a slot once results exist). The unenforceable half is rewritten honestly: §3.2 step 3 gains explicit "Checked" / "Not checked" paragraphs saying committing is ledger discipline the study records, not an ordering the driver enforces; README split the same way; the docstring says what it does not check | `34416f8` |
| 11 | material | The publication commitment cannot be fulfilled literally — a wrapper preflight refusal holds only `REFUSAL.json`, and `emit_records()` skips every invalid and no-parseable-array slot | **FIXED by making §8 match what the tree retains.** §8 commits to every raw slot directory with every byte the run left in it and nothing removed (naming the preflight case), the derived per-run verdict/code/counts/classification for every slot in `RESULTS.json`, and compiled `records/` + `RECORDS.md` for the valid parseable-array runs, emitted outside the slot tree, with the note that every slot's completion is published so a reader can compile it. The `.gitignore` claim was verified against the file | `34416f8` |
| 12 | minor | Four prose defects: S5's per-run mean/range does not say zero-record runs are excluded (the scorer excludes them); §7 says a "missing" `REFUSAL.json` yields pipeline-invalid while §3.3 and the code treat absence as no refusal; S4's promised aggregate ranges are not emitted; `PINS.json` still says C7 always retains three files | **FIXED, all four.** (a) §4.4 S5 registers the `|H|+|Q| > 0` restriction and the scorer publishes `perRunTrials`/`perRunExcluded`; (b) §7's totality bullet drops "missing" and gains the parenthetical; (c) S4's ranges are **emitted** rather than narrowed (`hPerRun`, `qPerRun`, `droppedPerRun` join `acceptedPerRun`, each a row in `RATES.md`); (d) `PINS.json`'s note matches §6 C7's three-outcome table. Four adjacent inaccuracies fixed in the same sentences | `34416f8` |

## Independent checker (Claude Opus), before commit

> All eleven round-3 findings (2-12) are closed in the current tree; each
> reviewer probe was reproduced on throwaway copies and now refuses. Full suite
> 153 passed in 76s (up from 139 — the round-4 fixes added 14 tests, none
> failing).

The checker re-derived C3 and every registered statistic independently (all
matching), walked §7 bullet by bullet against code, and made no git mutations.
It recorded three residuals, none reopening a finding: a §8 gloss that
mis-states what `authoring-empty` means; a README nit (`--emit-records` is also
a path); and an observation that reaching the underscore-private
`_write_outputs` **by name** with a dict agreeing with the committed tree on all
eight re-derived cell members *and* `registeredRuns` would write into the study
root — not any reviewer probe, and falsifying no §7 sentence, but recorded.
*(The next round's finding 7 attacked exactly that surface, and `118699c`
closed it by re-deriving the whole result from the tree.)*

**Incident recorded by the checker, reproduced here because nothing is
discarded:** while exercising finding 5's wrapper-level slot check from inside
a throwaway git worktree without `--cli-override`, the real pinned binary was on
PATH and **one registered-prompt call was actually spent against the real
model**. It landed in a throwaway slot outside the study tree; the checker
deleted it and its scratch without reading `completion.txt` and confirmed no
artifacts remain. The study tree was never touched (no authoring directory
exists; `git status` unchanged), so no batch, ledger or denominator is affected
— but §3.2 step 2 treats a pre-batch registered-prompt run as a cost worth
recording, so it is recorded.

---

# Round 5 — cross-vendor review 4 (first attempt KILLED; second attempt COMPLETED)

**Basis:** commit `34416f8`. **Date:** 2026-08-07.

## First attempt — killed, nothing recoverable

Transcript retained at `scratchpad/codex-review-011-r4.txt` (471 KB;
**109,765 tokens**; exit 1). The run died to the same filter:

> ERROR: This content was flagged for possible cybersecurity risk. If this
> seems wrong, try rephrasing your request.

preceded by a sandbox `CreateProcess` failure while the reviewer was copying the
study tree to a throwaway location. **No findings, no verdict, no partial
result of any value was produced** — the transcript ends inside the tree-copy
step of the documentation audit. Nothing from it is used anywhere in this
record. It is retained only as evidence that the attempt was made and not
re-rolled for a friendlier answer.

## Second attempt — READ-ONLY method, completed

Transcript retained at `scratchpad/codex-review-011-r4b.txt` (252,431 tokens;
exit 0). The method was deliberately changed to avoid the filter: **verification
by reading and by the committed suite, not by live modification.** The prompt
forbade modified copies of study files and probe scripts that alter tracked
content; the reviewer could run the suite, run read-only commands, and write
read-only analysis scripts. This is a weaker instrument than the
modification-based rounds — it cannot demonstrate an attack, only reason about
one — and the record should be read with that in mind. It nevertheless found two
blockers.

### Verdict (verbatim)

> ## Verdict — REVISE
>
> The green suite and correct arithmetic are not enough to freeze this commit.
> The registered scorer can still write through a symlink alias into its scored
> population, and the resume path can create slots beyond the fixed N; both can
> leave the retained tree unable to reproduce or publish the intended
> population. The remaining material findings also make several Section 7
> enforcement and Section 8 publication claims stronger than the code or tests
> support.

### Clean checks (findings 10 and 11, severity none)

Independent statistics from a standalone script importing no study code: the six
CP vectors; LIGHT first at k=46 (L45 = .7818646, L46 = .8076572); STANDARD first
at k=28 (L27 = .3932420, L28 = .4125441); P(LIGHT|p) = .1121/.4312/.8964/.9999.
Lineage and coherence: all six `PORTS` source/destination hashes and all four
referenced Study 010 hashes match; `integrity.py` green on CPython 3.12.11; the
current codex binary reports `codex-cli 0.145.0` and hashes to the registered
`a2a05d…be14`; the 22 §3.3 pipeline-invalid codes match the source return set and
`CODE_PARTITION`; the scorer's argv is exactly `--slots` plus optional
`--emit-records`, with unknown, duplicate and withdrawn flags refusing; full
suite **153 passed in 79.55s**.

### Findings and dispositions

All nine closed in `118699c`; **none disputed**. Every fix was
**mutation-checked** — reverting the code or the prose makes exactly the
intended test(s) fail.

| # | sev | finding | disposition | commit |
|---|---|---|---|---|
| 1 | **blocker** | `--emit-records` can still mutate the scored population through a symlink alias: `_check_records_target()` compares lexical `abspath`/`normpath` only, so `--slots /tmp/alias` with `--emit-records <real-tree>/run-051` passes, scores through the alias, publishes, then creates a real top-level slot. The committed test covers lexical equality/ancestor/descendant only | **FIXED.** The check resolves **both** sides with `os.path.realpath` before comparing (realpath resolves what exists and leaves a not-yet-created target lexical, so the check still runs before anything is written); `score_registered()` resolves the slot root **once at entry** and passes that one resolved path to the check, to `score()`, to `_write_outputs()` and to `_emit_records()`, which also resolves at its own entry. New test covers both directions plus the alias against itself, and shows the honest aliased case still emits. Mutation check: reverting realpath to abspath fails exactly this test | `118699c` |
| 2 | **blocker** | The resume interface can create an irrecoverably over-full batch: with `--runs` omitted the driver reloads the full registered N as a *count*, and `plan()` builds `range(start, start+runs)`, so `--start 3` after two runs plans 3–52; preflight imposes no `start + runs − 1 ≤ N` bound. README's `--runs M` never defines M | **FIXED.** `preflight()` refuses unconditionally when `start + runs − 1 >` the registry's `batch.runs` (whether or not `--runs` was given, and on the capture path too) and refuses `start < 1`; `main()` computes `runs = N − start + 1` when `--runs` is omitted. Two new tests: the plan after 2 slots is exactly `run-003..run-00N` and runs to a terminal, scoring batch; an over-full plan refuses **before any call**, pinned on the stand-in CLI's call counter being unmoved, the ledger byte-identical and no slot created | `118699c` |
| 3 | material | README's step-0 interpreter bootstrap does not execute — the pyenv shim reports `pyenv: python3.12: command not found`, so the runbook stops at step 0 | **FIXED.** Step 0 sets the registered **absolute** interpreter path (`…/.pyenv/versions/3.12.11/bin/python3`) with the reason in the comment; the interpreter paragraph and §3.2's parenthetical no longer print a shim name. Verified by executing the runbook as written: step 0 prints Python 3.12.11, integrity passes, pytest passes. The resume line is now `--start K` with the N-bound note | `118699c` |
| 4 | material | §6 C6 overstates admission enforcement: scratch-outside-worktrees is a wrapper gate never rechecked from retained evidence; the PATH binary-directory check rejects strict descendants of HOME but not equality; golden/context failures return other codes, not `isolation-unproven` | **FIXED per clause, favouring implementation where the evidence is recorded per slot.** *Implemented:* the PATH check now refuses when the directory **is** the isolated home as well as inside it; the leak-token half of the scratch clause is re-derived in admission from the recorded working directory. *Narrowed honestly:* the worktree-residence half stays a wrapper gate and §6 C6 says why (the scratch is deleted by scoring time, so no retained byte can answer it), and the session/golden/transcript clauses move to a second list naming their actual codes (`session-count`, `context-mismatch`, `transcript-refused`). Mutation check on both implemented clauses | `118699c` |
| 5 | material | §7's "byte-for-byte" golden residual is narrower than the actual gate — `normalize()` applies NFKC, deletes zero-width characters and replaces paths, dates, timestamps and UUIDs before hashing, so non-identical contexts within that class pass | **FIXED.** The "not prevented" bullet is retitled "…that reproduces the golden capture *after normalization*" and names the equivalence class exactly as the code implements it, plus why the class is deliberate (those members vary run to run and would otherwise refuse every honest run). Verified against `normalize`/`NORMALIZERS`; no other byte-identity claim about the context survives in the file | `118699c` |
| 6 | material | "Seeing rates always arms the guard" is false outside the CLI: public `score()` returns the complete rate dictionary without writing `RESULTS.json`, and preflight keys only on that file | **FIXED.** §2.4 states the mechanical truth — the driver's guard arms on `RESULTS.json` existing and the registered command is the only thing that writes it; a library caller can read six rates in process and publish nothing, which is recorded-not-prevented and is the same in-process ceiling §7 states once. The over-full path is closed mechanically by finding 2's N bound, and §2.4 says so | `118699c` |
| 7 | material | The private-writer negative test stops one mutation short — the forged-dictionary test leaves `registeredRuns=1`, so the writer refuses only on that one metadata mismatch; it re-derives no run rows, totals, class counts or rates | **FIXED.** `_write_outputs(results, slots_dir)` now re-derives the **whole** result by scoring the slot tree again through the registered derivation and refuses unless it is equal member for member, naming the differing member; the nine pin checks stay ahead of it. New test forges every population/cell member to committed-consistent values and mutates the arithmetic in seven independent places, refuses an entirely foreign scoring dressed in this cell's pins, and loops the eight re-derived pins plus `registeredRuns`. Mutation check: deleting the recomputation fails this test | `118699c` |
| 8 | material | §8's publication commitment is inaccurate and unpinned — "every slot's `completion.txt` either way" is contradicted by the section itself and by a test; `records/` + `RECORDS.md` is false for `[]` or all-dropped arrays; the publication test checks one output tree, not the prose (reverting §8 would leave the suite green) | **FIXED.** §8 registers the four shapes a slot can have, measured from the driver's own trees; the false promise is gone and named as the earlier error; `BATCH.json` and `SHORTFALL.json` are named beside the slots; the records bullet says `RECORDS.md` for every valid parseable-array run and `records/` only where a record was accepted. Two tests build all four shapes through the registered path and diff the parsed §8 table against the trees **in both directions**, and read the `.gitignore` claim off the file. Mutation check: adding a name §8 cannot retain, removing one it does, or adding a `.gitignore` line each fails | `118699c` |
| 9 | minor | Two advertised closure tests pin only neighbouring cases — "every irregular entry" uses four FIFOs (a socket-specific regression would pass), and the recovery test is success-then-success rather than failure-then-success | **FIXED.** (a) Every kind this environment can create is now built — four FIFOs (including the `REFUSAL.json` hang case with its child-process timeout), three UNIX sockets under the same shapes, and an unstattable entry — each asserted to refuse as `slot-irregular` naming its kind; the root-only kinds are pinned on the classifier itself by a new table test that also pins the unknown-type fallback. (b) The recapture test is rewritten to pin recovery: attempt-1's second probe fails, the command returns 1, attempt-1 is retained with its refusal and no golden is derived; the **same** command then succeeds into attempt-2 with attempt-1's evidence untouched. Mutation checks on both | `118699c` |

### Independent checker (Claude Opus), before commit

> CLOSED — all nine round-4b findings (2 blockers, 6 material, 1 minor) are
> closed in the current tree, each reproduced along the reviewer's own evidence
> path on throwaway material under /tmp. Full suite: 163 passed in 92.30s (up
> from the reviewer's 153; +10 new closure tests).

The checker re-ran `integrity.py`, the C3 replication and the CP-vector suite,
and **independently recomputed the registered CP vectors with a standalone
exact-rational script importing no study code** — matching exactly. Two findings
were verified by mutation rather than by reading: re-introducing §8's old
unconditional promise on a copy turns the suite red, and the forged-results path
is refused by a second independent derivation from the retained tree. No git
mutations.

Two notes it recorded, neither a defect: the residual disclosures now carry the
weight the code cannot (§2.4's library-caller route, §7's normalization
equivalence, §6 C6's wrapper-gated worktree clause) — the correct disposition,
but it means those three claims rest on prose accuracy rather than enforcement;
and finding 9(b)'s disagreeing-attempt-1 case is pinned by a separate
neighbouring test rather than folded into the recovery test.

---

# Round 6 — cross-vendor review 5 (KILLED BY THE VENDOR'S CONTENT FILTER)

**Basis:** commit `118699c` (HEAD). **Date:** 2026-08-07. **Reviewer:** same
configuration, **read-only method** (as round 5's second attempt). Transcript
retained at `scratchpad/codex-review-011-r5.txt` (502 KB; **172,835 tokens**;
exit 1).

This round existed to give the round-5 closures a completed cross-vendor
verification. It did not get there. The transcript ends with:

> ERROR: This content was flagged for possible cybersecurity risk. If this
> seems wrong, try rephrasing your request.

twice, followed by the session's rollout-recording failure. **No numbered
findings, no severities, no verdict were produced.** The read-only method did
not prevent the kill; it happened later in the run (172,835 tokens versus
109,765 for round 5's killed first attempt).

**What was recovered.** Two things:

1. **The statistics re-derived clean for the fifth time**, printed in the
   transcript: the six registered n=50 vectors; perfect-coverage lower bounds at
   V=50/45/40 (0.9289 / 0.9213 / 0.9119) with the half-widths; LIGHT first at
   k=46 (L = 0.8076572164, prior 0.7818646336); STANDARD first at k=28
   (L = 0.4125441229, prior 0.3932419761); P(LIGHT) = 0.1121 / 0.4312 / 0.8964 /
   0.9999.

2. **One reproduced defect, narrated but never assembled into a finding.** The
   reviewer's last complete narration:

   > The substantive path audit has now found a separate, reproducible blocker:
   > `realpath()` closes ordinary symlink aliases, but not two mount names for
   > the same directory. This environment exposes `/tmp` again under
   > `/mnt/wslg/distro/tmp`; the guard compares different strings even when
   > `os.path.samefile()` proves they are the same population. I'm reproducing
   > that independently and checking whether any test covers mount identity or
   > retargeting.

   Its reproduction is in the transcript: with `slots` under `/tmp` and the same
   directory reached through `/mnt/wslg/distro/tmp`, `os.path.samefile` is
   `True`, the two realpaths differ, and `_check_records_target(mounted, target)`
   printed `check=PASSED`. The follow-up probe — whether `_emit_records` then
   creates a phantom top-level slot in the scored population — printed
   `same_slots=True` and was cut off before its result.

**Status at HEAD: OPEN.** This was not closed in `118699c`, which predates the
round. The docstring of `_check_records_target` at HEAD confirms the guard is
`realpath`-based on both sides with no `samefile` or device/inode comparison, so
the described path is reachable on a machine with a bind mount. It carries no
reviewer-assigned severity beyond the word in the narration, and it was never
independently checked. It is the one item in this record that is named and not
disposed of.

---

# The filter kills — an operational record

Three of six review rounds were terminated by the reviewing vendor's content
filter rather than by the reviewer. The message was identical every time:

> ERROR: This content was flagged for possible cybersecurity risk. If this seems
> wrong, try rephrasing your request. To get authorized for security work, join
> the Trusted Access for Cyber program …

**What was attempted.**

| round | method | died at | what it reached |
|---|---|---|---|
| 3 | modification-based | 236,858 tokens | 4 of 6 tracks complete: five round-2 attacks re-run, walkthrough done, statistics re-derived, three neighboring defects named |
| 5 (first attempt) | modification-based | 109,765 tokens | nothing usable — died inside the tree-copy step |
| 6 | read-only | 172,835 tokens | statistics re-derived; one reproduced defect narrated; no findings assembled |

**Why the filter fires.** The work is adversarial by construction: the reviewer
is *asked* to tamper with digest tables on throwaway copies, forge registry
files, plant malformed evidence and demonstrate that a published result can be
manufactured. Round 3 died while displaying the diffs of its own tamper probes.
The read-only method adopted for rounds 5 and 6 was an attempt to reduce that
surface; it produced one completed round (5) and one kill (6), so it is a
mitigation rather than a fix — and it is a weaker instrument, since it can reason
about an attack but not demonstrate one.

**What was retained.** Every transcript, including the two that produced nothing
usable. No run was discarded, re-rolled, or re-prompted for a friendlier answer;
the retained set is the complete set of runs made. Where this record uses a
killed round, it says what was and was not recovered, and never attributes a
severity or a verdict the reviewer did not write.

**Why the record is still complete enough to decide on.**

- Every finding from every round that produced findings is closed, with a
  disposition and an implementing commit, and each closure was independently
  re-verified against the reviewer's own evidence path before commit.
- The eight historical closures from rounds 2 and 3 were re-verified by a
  *completed* cross-vendor round (round 4, finding 1) — so the killed round 3's
  work is not load-bearing on its own.
- The registered statistics — the part of the study a reader cannot re-derive
  without the harness — have now been recomputed from scratch by the reviewing
  vendor five times and by the drafting vendor's checkers four times, twice with
  exact-rational implementations importing no study code. Every derivation
  matched to the registered precision.
- The lineage claim — that the ported bytes are Study 010's — is checked by
  code on every run, against 010's `PROTOCOL-LOCK.json` rather than against this
  study's own table, and was independently verified by the reviewer in rounds 2,
  4 and 5.

**What the record does not support.**

- The round-5 closures (commit `118699c`, nine findings, 153 → 163 tests) have
  **no completed cross-vendor verification**. They have a mutation-checked test
  for each fix and an independent Claude checker's reproduction along the
  reviewer's own evidence paths — that is all.
- The mount-alias defect narrated in round 6 is open.
- Three §7 claims now rest on prose accuracy rather than enforcement (§2.4's
  library-caller route, §7's normalization equivalence class, §6 C6's
  wrapper-gated worktree clause), which the round-5 checker recorded as the
  correct disposition and a real limit.

A maintainer freezing at `118699c` is deciding to accept those three items. That
is a judgement the regime is designed to surface, not to make.

---

# State at HEAD

**HEAD:** `118699c` on `study-011-coverage-rates` — "Study 011: resolve aliases,
bound the resume, and finish the claims audit".

**Suite:** **163 passed in 92.58s** on CPython 3.12.11 (re-run for this record).
`harness/integrity.py` prints: *ported bytes verified: 7 files against
`harness/PORTS.md`, 6 sources against Study 010's lock
`sha256:4966aa8213…3543b1`, on CPython 3.12.11.*

**Invariants and where each is verified:**

| invariant | what it holds | verified by |
|---|---|---|
| **C3 replication** | This study's counting code means what Study 010's did: 010's retained completion, at its pinned digest, recompiles to 16 accepted, H=16, Q=0, per-class (2,2,2,4,1,1) | `harness/tests/test_coverage_profile.py::…::test_study_010s_retained_completion_reproduces_its_published_profile`, against the `replication` entry in `harness/PINS.json`. Independently recomputed by all four Claude checkers and by the cross-vendor reviewer in rounds 2 and 4 |
| **Clopper–Pearson vectors** | The registered exact intervals at n=50 (k = 0, 1, 25, 40, 45, 50) and the tier cutpoints (LIGHT first at k=46, STANDARD first at k=28) and the §5 P(LIGHT\|p) table | `harness/tests/test_intervals.py` (`REGISTERED` table, `ClopperPearson`, `ReviewTiers`, `RowComposition`). Independently re-derived by the cross-vendor reviewer in rounds 2, 3, 4, 5 and 6, and by all four Claude checkers — twice with exact-rational scripts importing no study code |
| **Lock-bound ports** | The six ported files answer to Study 010's `PROTOCOL-LOCK.json`, not to this study's own table: the lock is verified against `PINS.pinnedFrom.fileSha256` first, every source row must equal `lockedInputs`, and the three byte-identical ports must equal it on the destination side too | `harness/integrity.py` — run standalone, and as a precondition of `batch.preflight()`, `score_rates.score()`, `capture_golden()` and `declare_shortfall()`; plus `harness/tests/test_controls.py::PortedBytes` and `::PortedBytesAtRunTime`. Independently verified by the cross-vendor reviewer in rounds 2, 4 and 5 |

**Nothing has run.** No batch, no slot, no `RESULTS.json`. The preregistration
is still a draft; this file is the record on which the freeze decision is made.
