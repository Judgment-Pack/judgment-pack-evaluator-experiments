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
ported-bytes check, the replication control, the fixtures, the interval
vectors, and the wrapper-driven batch tests against a stand-in CLI.

The steps, in registered order, with the argv each one actually takes.
`DIR` is a scratch parent that resolves **outside every git worktree** and
carries no leak token (a path containing `jpack`, for instance, is
refused); `harness/PINS.json` is the registry every step reads.

```sh
cd studies/011-authorship-coverage-rates

# 1. Ported bytes (§6 C1). Deterministic, offline, also a precondition of
#    steps 3-6: batch.py and score_rates.py run this check themselves.
python3 harness/integrity.py

# 2. The harness suite: fixtures, replication control, interval vectors,
#    admission codes, and the batch driver against a stand-in CLI.
python3 -m pytest harness/tests -q

# 3. The golden-context recapture (§3.2). ONE command, which makes TWO
#    probe calls into controls/recapture/attempt-1/ and derives the
#    capture only if they agree.
python3 harness/batch.py capture --scratch-parent DIR
#    Then put the printed digest into harness/PINS.json golden.sha256 and
#    COMMIT both. Until that is done, step 5 refuses to create any slot and
#    step 6 refuses to score. If the two captures disagree, fix the cause
#    and run the same command again: it lands in attempt-2.

# 4. The isolation negative control (§6 C7), operator assent recorded in
#    harness/PINS.json. One probe call with the real HOME, expected to FAIL
#    the golden match; it retains three files and deletes the transcript.
python3 harness/batch.py capture-isolation-negative --scratch-parent DIR

# 5. The batch: 50 sequential slots into transcription/authoring/run-NNN/.
#    It retains bytes; it computes no coverage.
python3 harness/batch.py run --scratch-parent DIR
#    A dry run first, which creates nothing:
python3 harness/batch.py run --scratch-parent DIR --dry-run
#    After a crash, resume at slot K (the ledger is merged, not replaced):
python3 harness/batch.py run --scratch-parent DIR --start K --runs M
#    A batch that cannot finish, declared BEFORE anything is scored:
python3 harness/batch.py shortfall --slots transcription/authoring \
        --reason "why it could not finish"

# 6. The scorer: admission, compilation, classification, rates, intervals.
#    Writes RESULTS.json and RATES.md to the study root — there is no
#    --out, by design (§2.4) — and the optional per-slot record trees §8
#    publishes.
python3 harness/score_rates.py score --slots transcription/authoring \
        --emit-records records

# 7. ANALYSIS.md, then post-run cross-vendor adversarial review.
```

Ordering rules, per `PREREGISTRATION.md` §2.4 and §3.2, all of them checked
in code: N is fixed at 50 in the registry before the batch; no slot is
created before the golden capture is registered and committed, or after
`RESULTS.json` exists; a shortfall may not be declared over a batch that is
not short; and the scorer refuses unless the batch is terminal — exactly N
slots, or a shortfall declaration whose count is the slots present, never
both. What is **not** prevented, and is stated rather than papered over:
the operator reading a `completion.txt` by eye mid-batch (§7).

## Reading order

1. [`PREREGISTRATION.md`](PREREGISTRATION.md) — §1 the question, §2 the
   one cell and its pins, §3 admission and the invalid-run rule, §4 the
   endpoints and the exact interval procedure, §5 the confidence-score
   mapping, §6 the controls, §7 what is enforced, recorded, and not
   prevented, §9 bounds.
2. [`harness/PORTS.md`](harness/PORTS.md) — what each ported file changed,
   at which digest; the table `harness/integrity.py` reads.
3. [`DEVIATIONS.md`](DEVIATIONS.md) — empty until something departs.
4. `RESULTS.json`, `RATES.md` and `ANALYSIS.md` — do not exist yet.

Byte-lineage, not truth: this study measures whether independently
authored records *reach* registered boundary classes with correct labels.
It does not establish that the records are true, and it makes no
conformance claim of any kind.
