# Study 011 — coverage rates for blinded record authorship

**Status: DRAFT. Nothing has run.** No authoring call, no batch, no rate.
[`PREREGISTRATION.md`](PREREGISTRATION.md) is a draft until it is frozen by
merge after pre-freeze cross-vendor review; it governs thereafter, and
[`DEVIATIONS.md`](DEVIATIONS.md) records every departure from it.

## What it is

Study 010 ran one blinded authoring call and found it covered **6 of 6**
pre-committed defect classes — an existence result. This study turns that
into a frequency: **50 independent runs of Study 010's registered
authoring call**, byte-exact prompt, same pinned binary and model, fresh
`HOME`/`CODEX_HOME`/scratch per call, and for each of the six classes the
rate at which a run produces a correctly labelled record reaching it, with
exact Clopper–Pearson 95% intervals.

One cell, no arms, no hypothesis test — estimation. Both high and low
rates are findings, and the rate at which the authoring call fails
outright is an endpoint too. The rates are what a confidence score for
independently authored matrix rows can calibrate against: which rows need
light review, which need full review. That mapping is registered in
`PREREGISTRATION.md` §5 **before** the data, so it is applied rather than
fitted.

## How it relates to what came before

- [`009-transcribed-oracle-matrix`](../009-transcribed-oracle-matrix/) —
  established the transcription pipeline as a constructed existence
  witness, with records written by the person who planted the defect.
- [`010-blinded-oracle`](../010-blinded-oracle/) — removed that
  circularity: records authored by a different vendor's model that never
  saw a pack, a defect drawn by a beacon that had not yet occurred when
  the records were published. Result `caught`, 6/6 coverage. Its
  `ANALYSIS.md` states plainly that this is **not a rate**, and its
  "What follows" section registers this study.
- **This study** ports 010's prompt (which inlines the policy), family,
  mirror, compiler, and transcript gates by digest — byte-identically
  where it can, with an enumerated change list where fifty runs need what
  one did not — and drops everything that existed to make
  one unrepeatable draw trustworthy: no beacon, no transparency log, no
  single-slot rule, no evaluator. Coverage is computed by the ported
  policy mirror over compiled records; jpack never runs.
- Tracker: evaluator-experiments **issue #23**, whose final comment
  registers exactly this mandate and notes that a rates study needs sample
  size and a preregistered analysis instead of the draw machinery.

## How to run it, once frozen

The batch is API-dependent and non-deterministic, so it runs **manually,
never in CI**. The deterministic controls and fixtures do run in CI: the
`study-011-harness` job in `.github/workflows/ci.yml` runs the whole
`harness/tests` suite on Python 3.12, and that suite includes the
ported-bytes check against Study 010's lock, the replication control, the
fixtures, the interval vectors, the registered-illustration check on this
study's own prose, and the wrapper-driven batch tests against a stand-in CLI.

**The interpreter is a pin, not a detail.** `harness/PINS.json` registers
CPython 3.12, and the harness reads that member: `harness/integrity.py`,
`harness/batch.py` and `harness/score_rates.py` refuse under another
implementation or version series, and the wrapper refuses before it calls
anything if `PYTHON_BIN` is not the registered one. A bare `python3` is
whatever the shell resolves — on the machine this study was written on, 3.8 —
so every command below names the interpreter explicitly through `$PY`, and
`$PY` is set to the registered build's **absolute path** rather than to a
shim name that may not resolve.

The steps, in registered order, with the argv each one actually takes.
`DIR` is a scratch parent that resolves **outside every git worktree** and
carries no leak token (a path containing `jpack`, for instance, is
refused); `harness/PINS.json` is the registry every step reads.

```sh
cd studies/011-authorship-coverage-rates

# 0. The registered interpreter, BY ABSOLUTE PATH. Every command below runs
#    under it, and the harness refuses if it is not CPython 3.12. It is the
#    absolute path and not `command -v python3.12` because on this machine
#    that resolves to a pyenv shim that then reports "python3.12: command not
#    found" — a runbook whose step 0 does not execute is not a runbook.
PY=/home/onword/.pyenv/versions/3.12.11/bin/python3 && "$PY" -V

# 1. Ported bytes (§6 C1), Study 010's lock, and the interpreter.
#    Deterministic, offline, and also a precondition of steps 3-6:
#    batch.py and score_rates.py run this same check themselves.
"$PY" harness/integrity.py

# 2. The harness suite: fixtures, replication control, interval vectors,
#    admission codes, and the batch driver against a stand-in CLI.
"$PY" -m pytest harness/tests -q

# 3. Freeze the preregistration: put its sha256 into harness/PINS.json
#    preregistration.sha256 and COMMIT. Nothing below will make a call or
#    compute a rate while that member is null (§2.6).
sha256sum PREREGISTRATION.md

# 4. The golden-context recapture (§3.2). ONE command, which makes TWO
#    probe calls into controls/recapture/attempt-1/ and derives the
#    capture only if they agree; one call cannot derive one.
"$PY" harness/batch.py capture --scratch-parent DIR
#    Then put the printed digest into harness/PINS.json golden.sha256 and
#    COMMIT both. Until that is done, step 6 refuses to create any slot and
#    step 7 refuses to score. If the two captures disagree, fix the cause
#    and run the same command again: it lands in attempt-2.
#    From here on, harness/PINS.json is not edited again: the batch stamps
#    its digest into every slot, and a later edit refuses the scoring (§2.6).

# 5. The isolation negative control (§6 C7), operator assent recorded in
#    harness/PINS.json. One probe call with the real HOME, expected to FAIL
#    the golden match; it retains its verdict and a stripped call record
#    (plus the context digests when there are any) and deletes the
#    transcript. It exits non-zero if it reached neither comparison.
"$PY" harness/batch.py capture-isolation-negative --scratch-parent DIR

# 6. The batch: 50 sequential slots into transcription/authoring/run-NNN/.
#    It retains bytes; it computes no coverage. THE DRY RUN COMES FIRST —
#    it creates nothing, and running it after the real batch would only
#    refuse because the slots already exist.
"$PY" harness/batch.py run --scratch-parent DIR --dry-run
"$PY" harness/batch.py run --scratch-parent DIR
#    After a crash, resume at slot K (the ledger is merged, not replaced).
#    Omit --runs: the registered N is the LAST slot index, so this runs the
#    remaining 51-K slots. --runs M is accepted and refused before any call
#    when K+M-1 > 50.
"$PY" harness/batch.py run --scratch-parent DIR --start K
#    A batch that cannot finish, declared BEFORE anything is scored:
"$PY" harness/batch.py shortfall --slots transcription/authoring \
        --reason "why it could not finish"

# 7. The scorer: admission, compilation, classification, rates, intervals.
#    This command IS the registered scoring interface
#    (score_rates.score_registered), and it is the only thing that publishes.
#    --slots and --emit-records are its WHOLE argument surface: the registry,
#    the family, the prompt, the golden capture and the study root are derived
#    from the harness's own location, and any other argument REFUSES rather
#    than being ignored (§7). --emit-records must name a directory outside the
#    slot tree. It writes RESULTS.json and RATES.md to the study root.
"$PY" harness/score_rates.py score --slots transcription/authoring \
        --emit-records records

# 8. ANALYSIS.md, then post-run cross-vendor adversarial review.
```

Ordering rules, per `PREREGISTRATION.md` §2.4, §2.6 and §3.2.

**Checked in code**, and a violation refuses: N is fixed at 50 in the registry
before the batch; no call is made while the preregistration's freeze digest is
unregistered or does not match; no slot is created while `golden.sha256` is
null or the file at the golden path does not hash to it, or after
`RESULTS.json` exists; a shortfall may not be declared over a batch that is not
short; and the scorer refuses unless the batch is terminal — exactly N slots,
or a shortfall declaration whose count is the slots present, never both. Two of
those are checked **per slot** rather than by ordering alone: every run records
the registry and the golden capture it was made under, so a capture derived
after the batch makes those runs pipeline-invalid instead of redefining what
they meant. And the registered scoring command takes no path but the slot tree,
so a registry cannot be substituted into the counting at all.

**Ledger discipline, recorded and not checked**: that the golden capture and
the registry were *committed* before slot 1. This study has no lock-commit
machinery and compares nothing to a `HEAD` blob — §7 says so under
"deliberately not claimed" — so the file-to-pin binding and the per-slot stamp
are what a reader can check, and the commit is what the study records. The
other thing **not** prevented, stated rather than papered over: the operator
reading a `completion.txt` by eye mid-batch (§7).

## Reading order

1. [`PREREGISTRATION.md`](PREREGISTRATION.md) — §1 the question, §2 the
   one cell and its pins, §3 admission and the invalid-run rule, §4 the
   endpoints and the exact interval procedure, §5 the confidence-score
   mapping, §6 the controls, §7 what is enforced, recorded, and not
   prevented, §9 bounds.
2. [`harness/PORTS.md`](harness/PORTS.md) — what each ported file changed,
   at which digest; the table `harness/integrity.py` reads. Its **source**
   column is checked against Study 010's own `PROTOCOL-LOCK.json`, not
   against itself, so editing a port and its row together still refuses.
3. [`DEVIATIONS.md`](DEVIATIONS.md) — empty until something departs.
4. `RESULTS.json`, `RATES.md` and `ANALYSIS.md` — the run's outputs (the
   study ran 2026-08-07; 49 of 50 slots valid, every class covered).
5. [`DIVERSITY.md`](DIVERSITY.md) — the post-hoc diversity census a reader's
   question prompted: how much variety sits behind 49/49. Every table
   regenerates from `analysis/diversity.py`.

Byte-lineage, not truth: this study measures whether independently
authored records *reach* registered boundary classes with correct labels.
It does not establish that the records are true, and it makes no
conformance claim of any kind.
