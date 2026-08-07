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
never in CI** (repo rule). Only the deterministic controls and fixtures
run in CI.

The steps, in registered order (the harness sources carry the exact
invocations, `harness/PORTS.md` records what each ported file changed, and
`harness/PINS.json` is the registry every step reads):

1. **Ported-bytes check** — every ported file against Study 010's locked
   digests, and 010's `PROTOCOL-LOCK.json` against its own pinned digest.
   Deterministic, offline, runs in CI.
2. **Harness tests** — the synthetic fixtures, the replication control
   against 010's published profile, and the Clopper–Pearson test vectors.
   Deterministic, offline, runs in CI.
3. **Golden-context recapture** (`harness/batch.py capture-golden`, run
   **twice** with a scratch parent) — both captures must agree before
   anything else runs; the agreed capture and its digest are committed.
4. **Isolation negative control** — one deliberately non-isolated capture,
   which is expected to fail the golden match (§6, C7).
5. **The batch** (`harness/batch.py`) — 50 sequential slots into
   `transcription/authoring/run-NNN/` (the driver's default, Study 010's
   slot shape). It retains bytes; it computes no coverage.
6. **The scorer** (`harness/score_rates.py`) — admission, compilation,
   classification, rates, and intervals, into `RESULTS.json`. It refuses
   until the batch is terminal.
7. `ANALYSIS.md`, then post-run cross-vendor adversarial review.

The scratch parent must resolve outside every git worktree and carry no
leak token (a path containing `jpack`, for instance, is refused).

Ordering rule, per `PREREGISTRATION.md` §2.4: N is fixed at 50 before the
batch, there is no data-dependent stopping, and no slots may be added
after any rate has been computed. A short batch is reported as a shortfall
with its completed count.

## Reading order

1. [`PREREGISTRATION.md`](PREREGISTRATION.md) — §1 the question, §2 the
   one cell and its pins, §3 admission and the invalid-run rule, §4 the
   endpoints and the exact interval procedure, §5 the confidence-score
   mapping, §6 the controls, §7 what is enforced, recorded, and not
   prevented, §9 bounds.
2. [`DEVIATIONS.md`](DEVIATIONS.md) — empty until something departs.
3. `RESULTS.json` and `ANALYSIS.md` — do not exist yet.

Byte-lineage, not truth: this study measures whether independently
authored records *reach* registered boundary classes with correct labels.
It does not establish that the records are true, and it makes no
conformance claim of any kind.
