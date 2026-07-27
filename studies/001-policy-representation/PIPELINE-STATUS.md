# Pipeline status — what runs today

Handover state as of **2026-07-27, after the four parallel pieces (parser, pack,
harness, redaction operator) were integrated and the two missing pieces
(`pipeline/derive.py`, arm A-prime's prose) were built.**

Blunt on purpose: everything below is either **verified by running it**, or
listed as a gap. Nothing here is aspirational.

**Headline:** the chain now runs end to end — parse → derive → validate → redact
→ derive → evaluate → score — and every stage is deterministic. Arm B has been
run for real over the whole corpus; its accuracy is 57.9% (80.1% on the subset it
can decide) and the reason it cannot decide the rest is a missing constant, not a
missing rule. See §7 G-1. No prompt arm has been run against a real model beyond
the two-instance Codex pilot in §6.

> **Interpreter.** The system Python here is 3.8 and **cannot run this pipeline**
> (`X | None` annotations, `:=` in comprehension guards). Use 3.10+. Everything
> below was run with `/home/onword/.pyenv/versions/3.12.11/bin/python3`
> (`export PYENV_VERSION=3.12.11` also works).

---

## 1. Substrate — verified

| Check | Result |
| --- | --- |
| `rulearena/fetch.sh` clones at the pinned commit and verifies the SHA | run |
| Pinned commit | `3b9e2256294644beca66732babc5e1055855a576` |
| Licence | MIT, copied to `rulearena/LICENSE-RuleArena`; fetched, never vendored |
| Checkout treated as read-only | yes — nothing under `rulearena/checkout/` was modified |

## 2. Parser — verified, 100% coverage

`python pipeline/parse_nba.py --checkout rulearena/checkout --out pipeline/out/facts --strict`

| Check | Result |
| --- | --- |
| Instances parsed | **216 / 216 (100%)** — comp_0 = 81, comp_1 = 89, comp_2 = 46 |
| Source sentences consumed | **2,793 / 2,793**, zero unparsed residue |
| Operations parsed | 536 / 536 |
| JSON numbers anywhere under `facts` | **0** — every value is a JPS-grammar decimal string |
| Instances with a documented ambiguity caveat | 8 / 216, listed in `pipeline/PARSE-COVERAGE.md` §5 |
| LLM involved in extraction | **none** — anchored regular expressions only |
| Determinism | two fresh runs byte-identical, and byte-identical to the committed `out/facts` |
| `--strict` exit code | 0 |

## 3. Derived-fact preprocessor — new, verified

`python pipeline/derive.py --facts pipeline/out/facts --out pipeline/out/facts --strict`

This is the piece that did not exist before this session and was the critical
path: the pack requires 124 `/facts/derived/*` fields and the parser deliberately
emits `derived: {}`.

| Check | Result |
| --- | --- |
| Always-present booleans emitted on every instance | **39 / 39** |
| Distinct contract fields emitted at least once | **123 / 124** |
| Emitted values that are not a JSON boolean or a JPS decimal string | **0** |
| Instances with at least one omitted conditional field | 95 / 216 |
| Omitted-field events | 354 across 27 fields |
| The one field never emitted anywhere | `ratio-non-qualifying-veteran-free-agent-first-year-salary-to-minimum-annual-salary` |
| Determinism | two runs byte-identical |
| Idempotence | re-running over its own output is a no-op |
| Constants | taken from RuleArena's own prompt preamble (`nba/auto_test.py`) plus the CBA's percentages; pinned by a test that greps the checkout |

An omitted field is **not** a bug: `COVERAGE.md` §4 fixes the discipline
absent ⇒ `unknown` ⇒ escalate. Omitting is how the preprocessor says "I do not
know", and it is always preferred to inventing a number. Full accounting,
including the two constants that genuinely do not exist anywhere in the
benchmark, is in **`pipeline/DERIVED.md`**.

## 4. Pack — verified, with one large caveat

`judgment-pack spec validate packs/nba-transaction-legality.json` → **exit 0**
(`judgment-pack 0.2.0`, JPS `0.1.0-draft`, bundle sha256 `abc3d337…`).

| Property | Value |
| --- | --- |
| Outcomes | `legal`, `illegal` |
| Rules | 61, plus 1 exception (`provision-outside-pack-scope`) |
| Coverage of the benchmark's `relevant_rules` vocabulary | **61 / 61 (100%)** |
| `/facts/derived/*` fields required | **124** |
| Authored from | `nba/reference_rules.txt` + the rule-name list only; no instance, gold answer, or answer distribution read |

**The 124 derived fields are the finding, not a footnote.** JPS compares facts
and has no arithmetic, so every computed quantity the CBA needs must be supplied
to the pack rather than derived by it. That number is the honest measure of how
much of this decision the format cannot express on its own, and it belongs in the
report whatever the arms show. §7 G-2 sharpens it: 13 of those fields are not
arithmetic at all but legal characterisation.

## 5. Redaction — verified, and materially changed by running it after `derive.py`

`python pipeline/redact.py --facts pipeline/out/facts --out pipeline/out/twins --seed 20260727`

The redaction author flagged that `facts.derived` was empty when they ran, so
guard G4's supersession check had nothing to fire against, and asked for a re-run
once the preprocessor existed. Re-running changes the output:

| | before `derive.py` | after `derive.py` |
| --- | --- | --- |
| Pairs emitted | 216 (432 twins) | 216 (432 twins) |
| Instances skipped / orphan twins | 0 / 0 | 0 / 0 |
| Weak pairs (excluded from primary) | 0 | **3** |
| Strong pairs | 216 (37 universal / 179 localized) | 213 (36 universal / 177 localized) |
| Distinct fact roles deleted | 23 | **12** |
| Documents with empty `facts.derived` | 216 | **0** |

Top deleted roles now: `player.prior_team` 58, `player.contract.signed_year` 52,
`operation.new_contract.change_direction` 32,
`operation.new_contract.increase_rate` 26, `operation.team` 24.

Leak control: each twin carries a `render_policy` naming pointers a prompt
renderer must **not** show. 86 pairs echo their deleted value in those
render-excluded fields, so honouring the policy is load-bearing. As of this
session the harness honours it — it did not before (§6, mismatch 1).

Determinism: two runs byte-identical.

**`derive.py` must then be run a second time, over the twins:**

`python pipeline/derive.py --facts pipeline/out/twins --out pipeline/out/twins`

Without it the redaction is invisible to arm B. See §6, mismatch 4.

## 6. Harness — runs on mock for all three arms, and on the real runtime for arm B

### 6.1 Interface mismatches found by wiring the pieces together, and fixed

Four real defects, all fixed this session. Each would have corrupted the analysis
silently.

**1. The harness rendered every fact the render policy forbids.**
`arms.redact_gold` removed only `gold`. It ignored the `render_policy` that
`redact.py` stamps into every twin, so every prompt would have carried
`facts.operations[].raw` (RuleArena's original English — 86 pairs provably echo
their deleted value there), `provenance.raw`, the `redaction` record itself
(which names the deleted pointer **and its deleted value**), and
`expected_decision` (literally the answer).
*Fix:* `arms.apply_render_policy` prunes every excluded RFC 6901 pointer prefix
and glob; `redact_gold` delegates to it; `canonical_facts_json` uses it.
Documents that declare no policy fall back to dropping `/gold` and
`/provenance`. Verified: none of `gold`, `provenance`, `raw`, `redaction`,
`expected_decision`, `removed_value` survives into the rendered facts, and
`facts_sha256` is identical across all three arms for every row.

**2. The scorer collapsed each twin pair into one instance.** `redact.py`
deliberately gives both twins the same `instance_id` and distinguishes them by
`twin_id`. `run.py` already handled this (it writes `row_id`), but `score.py`
keyed both `load_results` and `by_id` on `instance_id`.
*Fix:* `score.py` keys on `row_id` / `arms.instance_key`, and raises if two
documents still collide.

**3. The scorer treated both twins as should-escalate.** `should_escalate`
returned `True` for anything with a truthy `redaction` member — and the
*answerable* twin carries one too (it records what its counterpart lost). Gold
for escalation was therefore an all-ones vector.
*Fix:* `variant` and `expected_decision` are consulted first, then
`redaction.applied`. `base_instance_id` now prefers `pair_id`.

**4. `facts.derived` was carried over from the answerable twin, making the
redaction invisible to arm B.** The pack reads `/facts/derived/*` and nothing
else; `redact.py` deliberately never deletes a derived field. Net effect: **all
216 pairs had byte-identical `facts.derived`** and both twins always evaluated
identically.
*Fix:* run `derive.py` a second time over `out/twins`, recomputing each twin's
derived block from its own surviving raw facts. **90 of 216 pairs now differ**,
and arm B's escalation recall on the smoke slice rose from 0.375 to 0.500. The
residual 126 pairs are gap G-4.

Two further bugs had already been found and fixed by the harness author in an
earlier session and are recorded here for completeness: `run.py` used to load the
sidecar `manifest.json` as if it were an instance, and rows used to be keyed by
`instance_id` alone.

A fifth issue was a missing artifact rather than a mismatch: **arm A-prime had no
prose to run against.** `run.py --arm Aprime` requires `--pack-prose FILE` and no
such file existed. `packs/render_prose.py` now generates it mechanically from the
pack — the right way round, since a hand-written restatement would be a second
act of authorship and would confound the control A-prime exists to provide.

### 6.2 Real backend history

- **Codex (`gpt-5.6-sol`), arm A, one twin pair** (earlier session) — 2/2 parsed,
  0 errors, both matched expectation: answerable → `illegal` (gold), redacted →
  `cannot_decide`. **n = 2. Plumbing validation, no evidence about any
  hypothesis.**
- **Anthropic and Codex were not run in this integration session** (no
  credentials assumed, and cost). Forbidden by the integration brief.

### 6.3 Arm B against the real runtime, whole corpus (432 twins)

One `judgment-pack experimental evaluate` per twin.

| Variant | `illegal` | `legal` | `unresolved` → `cannot_decide` | correct |
| --- | ---: | ---: | ---: | ---: |
| answerable (n = 216) | 133 | 23 | 60 | **125 / 216 = 57.9%** |
| redacted (n = 216) | 102 | 22 | 92 | **92 / 216 = 42.6%** |
| both | 235 | 45 | 152 | **217 / 432 = 50.2%** |

On the 156 answerable instances the pack actually decided, accuracy is
**125 / 156 = 80.1%**. Confusion on the answerable half:

| | got `illegal` | got `legal` | got `cannot_decide` |
| --- | ---: | ---: | ---: |
| gold `illegal` (n = 179) | 115 | 13 | 51 |
| gold `legal` (n = 37) | 18 | 10 | 9 |

Escalation 2×2 over the full corpus: 92 true escalations, 60 false escalations,
124 missed → precision 0.605, recall 0.426, F1 0.500.

**Engine refusals: 0.** All 432 calls returned `status: "evaluated"` and exited 0.

### 6.4 The single-pair smoke test

```
$ judgment-pack experimental evaluate packs/nba-transaction-legality.json \
      --facts pipeline/out/twins/comp_0-002__answerable.json --format json
  status      : evaluated
  kind        : outcome    outcomeId: illegal
  fired rules : ['defer-compensation-38-year-old']
  unknown     : []
  gold        : answer=true -> expected "illegal"                  MATCH

$ judgment-pack experimental evaluate packs/nba-transaction-legality.json \
      --facts pipeline/out/twins/comp_0-002__redacted.json --format json
  deleted     : /facts/operations/0/team   (role operation.team)
  status      : evaluated
  kind        : unresolved   reasons: ["unknown"]   handoff: requested
  fired rules : ['non-taxpayer-mid-level-exception', 'nontaxpayer-mid-level-exception']
  unknown     : ['non-taxpayer-mid-level-exception-hard-cap-first-apron-level',
                 'nontaxpayer-mid-level-exception-hard-cap-first-apron-level',
                 'defer-compensation-38-year-old']
  expected    : "cannot_decide"                                    MATCH
```

### 6.5 End-to-end mock run, all three arms

16 twins (`comp_0#000`–`comp_0#007`, both variants), 2 trials, seed 7, 500
bootstrap resamples. **The mock backend is a sha256-derived stub, not a model:
the A and A-prime columns measure plumbing and nothing else.** Arm B ignores
`--backend` and calls the real runtime, so its column is a real result on a small
slice.

```
## Accuracy and consistency

| condition                           | accuracy | 95% CI          | pass^k | 95% CI          | parse-ok | engine-refusal |
|-------------------------------------|---------:|-----------------|-------:|-----------------|---------:|---------------:|
| A::mock::mock/deterministic-v1      |    0.312 | [0.156, 0.500]  |  0.188 | [0.030, 0.375]  |    0.969 |          0.000 |
| Aprime::mock::mock/deterministic-v1 |    0.250 | [0.062, 0.438]  |  0.188 | [0.000, 0.375]  |    0.938 |          0.000 |
| B::mock::judgment-pack-runtime      |    0.500 | [0.250, 0.750]  |  0.500 | [0.250, 0.750]  |    1.000 |          0.000 |

## Citation quality vs gold relevant_rules

| condition                           | precision | recall |    F1 | 95% CI (F1)     | micro F1 |
|-------------------------------------|----------:|-------:|------:|-----------------|---------:|
| A::mock::mock/deterministic-v1      |     0.057 |  0.015 | 0.023 | [0.006, 0.046]  |    0.030 |
| Aprime::mock::mock/deterministic-v1 |     0.073 |  0.016 | 0.026 | [0.006, 0.050]  |    0.030 |
| B::mock::judgment-pack-runtime      |     0.562 |  0.101 | 0.170 | [0.094, 0.248]  |    0.189 |

## Escalation on redacted twins (full 2x2)

| condition                           | should & did | should-not but did | should but did not | neither | precision | recall |    F1 | 95% CI (F1)    |
|-------------------------------------|-------------:|-------------------:|-------------------:|--------:|----------:|-------:|------:|----------------|
| A::mock::mock/deterministic-v1      |            1 |                  2 |                 15 |      14 |     0.333 |  0.062 | 0.105 | [0.000, 0.320] |
| Aprime::mock::mock/deterministic-v1 |            0 |                  1 |                 16 |      15 |     0.000 |  0.000 | 0.000 | [0.000, 0.000] |
| B::mock::judgment-pack-runtime      |            8 |                  6 |                  8 |      10 |     0.571 |  0.500 | 0.533 | [0.182, 0.824] |

## Paired differences vs baseline A::mock::mock/deterministic-v1

| condition                           | d accuracy | 95% CI          | P(d>0) | d pass^k | 95% CI          | d citation F1 | 95% CI          | d escalation F1 | 95% CI          |
|-------------------------------------|-----------:|-----------------|-------:|---------:|-----------------|--------------:|-----------------|----------------:|-----------------|
| Aprime::mock::mock/deterministic-v1 |     -0.062 | [-0.219, 0.062] |  0.140 |    0.000 | [-0.188, 0.188] |         0.003 | [-0.023, 0.030] |          -0.105 | [-0.320, 0.000] |
| B::mock::judgment-pack-runtime      |      0.188 | [-0.156, 0.531] |  0.816 |    0.312 | [-0.062, 0.625] |         0.147 | [ 0.073, 0.219] |           0.428 | [-0.016, 0.800] |
```

Artifacts: `results/smoke-{A,Aprime,B}-mock.jsonl`, `results/smoke-report.{md,json}`.

Every result row records `row_id`, `instance_id`, `variant`, model id and params,
`facts_sha256`, `prompt_sha256`, the harness commit, and whether the tree was
dirty.

Test suite: **141 tests, all passing** on CPython 3.12.11 —
`test_parse_nba.py` 26, `test_redact.py` 27, `test_derive.py` 44,
`test_harness.py` 44.

---

## 7. Gaps — every one of them, bluntly

**G-1. The pack cannot decide 28% of the corpus, and the reason is a missing
constant, not a missing rule.** 60 of 216 answerable instances resolve to
`unresolved`. Almost all trace to the Minimum Player Salary / Minimum Annual
Salary schedule, which appears in *neither* `reference_rules.txt` *nor*
RuleArena's stipulation block — it is nowhere in the pinned checkout. 77 of 216
instances contain at least one contract stated as "minimum applicable player
salary"; a preprocessor that refuses to invent the figure cannot compute those
teams' post-transaction salaries, so the fields are omitted, the rules go
`unknown`, and the instance escalates. Models in arm A face the same deficit and
paper over it by treating minimum contracts as immaterial; the pack cannot,
because JPS has no "immaterial". **Report this as an expressiveness result; do
not fix it by inventing a number.** Detail: `pipeline/DERIVED.md` §3, gap G-MIN.

**G-2. `derive.py` is doing legal characterisation, and arm B's score partly
measures `derive.py` rather than the pack.** 13 of the 39 always-present booleans
name *which Salary Cap Exception a transaction invokes*. RuleArena's prose never
states one; working it out is the reasoning the benchmark tests. JPS 0.1.0-draft
cannot express the selection (choosing "the lowest tier whose limb covers the
amount" needs comparison against a computed limb), so it lives in `derive.py` as
readings R5–R7 (`python pipeline/derive.py --readings`). The same derived block
goes to all three arms, so the *comparison* is unbiased — but the absolute arm-B
number is not a clean measure of the pack. `pipeline/DERIVED.md` §4 says this at
length; any write-up must repeat it.

**G-3. 18 false `illegal` verdicts on gold-legal instances, undiagnosed.** Arm B
calls 18 of the 50 gold-legal answerable instances illegal. Most likely cause is
G-2: an over-eager exception assignment (e.g. the Non-Taxpayer Mid-Level assigned
to a team that in fact had Room) makes a limit rule fire. Someone should walk
those 18 traces.

**G-4. The redaction is still invisible to arm B on 126 of 216 pairs.**
`redact.py` chooses what to delete in terms of *raw* fact roles read off
RuleArena's rule text. The pack reads only `/facts/derived/*`. After the second
derive pass 90 pairs have a derived block that actually changes; on the other 126
the deleted raw fact feeds no emitted derived field, so arm B evaluates both
twins identically and structurally cannot escalate — while arms A and A-prime,
which see the raw facts, are measured on all 216. **This asymmetry is not
fixed.** Fix direction: have `redact.py` prefer candidate roles that provably
feed at least one emitted derived field, which needs a role → derived-field map
that does not exist yet.

**G-5. No prompt arm has been run against a real model at scale.** Arms A and
A-prime have been exercised only on the mock backend plus the n = 2 Codex pilot.
The Codex backend's author documents two caveats that still stand: no seed or
temperature is exposed, so it is not deterministic, and the CLI loads its own
bundled skill descriptions and keeps a shell tool even in the read-only sandbox.
The Anthropic backend has never been executed and raises at construction without
`ANTHROPIC_API_KEY` rather than falling back.

**G-6. Arm A-prime's prose is machine-generated and has never been read by a
human.** `packs/render_prose.py` projects the pack into 53 KB of numbered
paragraphs. Faithful by construction, but not *good* prose: conditions render as
long boolean chains. If the intent of A-prime is "a human carefully analysed the
policy", a reviewer must decide whether a mechanical projection satisfies that or
whether it makes A-prime an unrealistically weak control. Flagging, not deciding.

**G-7. The eligibility gate has not been computed.** The preregistration requires
freezing the eligible-instance set **before** any scored run. Not done.

**G-8. The pack has not been hashed into `packs/`.** The preregistration requires
the hash committed before the first run. The runtime reports bundle sha256
`abc3d3371db5be6c0b63639d399fbe42e3f3e136a162d8d6c2b50503634bbe70`; it is not yet
recorded as a committed artifact.

**G-9. The preregistered outcome map is not pinned.** Arm B ran without
`--outcome-map`, so `legal`/`illegal` resolved by exact match against the shared
vocabulary. Correct today only because the pack's outcome ids happen to equal the
study's decision labels. The real run should pass an explicit `--outcome-map` so
a future rename fails loudly.

**G-10. Evidence requirements are never exercised.** The pack declares three, all
`required: false`; no run passes `--evidence`. The `missing-required-evidence`
escalation trigger is dead code in this study.

**G-11. Arm B's condition key is misleading.** `run.py --arm B --backend mock`
records `backend: "mock"` while calling the runtime, producing
`B::mock::judgment-pack-runtime`. Harmless but confusing in a report table;
consider a `--backend none` alias.

**G-12. Two rule-identifier spellings fire together.** The pack encodes both
`non-taxpayer-mid-level-exception` and `nontaxpayer-mid-level-exception` (and the
hard-cap variants) because RuleArena's gold column spells them both ways. Both
fire on the same facts, so arm B emits duplicate citations. `score.py` normalises
rule ids to lowercase alphanumerics, which collapses the pair, so the metric is
unaffected — but a raw trace looks odd.

**G-13. 8 instances rest on parser ambiguities that nothing resolves.** 4 trades
state no destination team; 4 three-team trades have an unresolved asset binding.
`derive.py` omits every dependent quantity (reading R9), so those instances
escalate. Neither the parser nor the preprocessor guesses, and the benchmark's
prose does not disambiguate.

**G-14. `results/` currently holds only mock output.** `results/smoke-*.jsonl`
and `results/smoke-report.*` are from this integration run and should be deleted
or moved before the real run; they are not preregistered artifacts.

---

## 8. Reproducing everything above

Run from `studies/001-policy-representation`. `PY` is a Python 3.10+ interpreter.

```bash
PY=/home/onword/.pyenv/versions/3.12.11/bin/python3

rulearena/fetch.sh

# 1. parse
$PY pipeline/parse_nba.py --checkout rulearena/checkout --out pipeline/out/facts --strict

# 2. derive, pass 1 (in place; feeds redact.py's supersession guard G4)
$PY pipeline/derive.py --facts pipeline/out/facts --out pipeline/out/facts \
    --report pipeline/out/derive-report.json --strict

# 3. validate the pack
judgment-pack spec validate packs/nba-transaction-legality.json      # exit 0

# 4. redact
$PY pipeline/redact.py --facts pipeline/out/facts --out pipeline/out/twins --seed 20260727

# 5. derive, pass 2 (per twin; NOT optional -- see section 6.1, mismatch 4)
$PY pipeline/derive.py --facts pipeline/out/twins --out pipeline/out/twins \
    --report pipeline/out/derive-report-twins.json

# 6. render arm A-prime's prose from the pack
$PY packs/render_prose.py --pack packs/nba-transaction-legality.json \
    --out packs/nba-transaction-legality.prose.txt

# 7. run the three arms (mock; substitute --backend anthropic|codex + --model for real runs)
$PY harness/run.py --arm A      --backend mock --instances pipeline/out/twins \
    --trials 2 --seed 7 --out results/A-mock.jsonl
$PY harness/run.py --arm Aprime --backend mock --instances pipeline/out/twins \
    --trials 2 --seed 7 --pack-prose packs/nba-transaction-legality.prose.txt \
    --out results/Aprime-mock.jsonl
$PY harness/run.py --arm B      --backend mock --instances pipeline/out/twins \
    --trials 2 --seed 7 --pack packs/nba-transaction-legality.json \
    --out results/B-mock.jsonl

# 8. score
$PY harness/score.py --instances pipeline/out/twins \
    --results results/A-mock.jsonl results/Aprime-mock.jsonl results/B-mock.jsonl \
    --baseline "A::mock::mock/deterministic-v1" --bootstrap 2000 \
    --out-md results/report.md --out-json results/report.json

# tests
$PY -m pytest pipeline/tests harness/tests -q     # 141 passed

# supporting reads
$PY pipeline/derive.py --readings                 # numbered readings R1-R10
```

Determinism checks that were actually performed (`diff -r` between two runs, all
clean): parser, derive over facts, derive over twins, redact. Derive was
additionally checked for idempotence by running it over its own output.

`pipeline/out/` is generated and gitignored — every byte is reproducible from the
pinned commit plus the scripts above. The DOI'd corpus release will include the
generated artifacts; the repository does not carry them.

| Path | Produced by | Contents |
| --- | --- | --- |
| `pipeline/out/facts/comp_*.json`, `index.json` | `parse_nba.py` then `derive.py` pass 1 | 216 facts documents with `facts.derived` filled |
| `pipeline/out/derive-report.json` | `derive.py` pass 1 | constants used, field presence, omission counts, per-instance omissions |
| `pipeline/out/twins/*__{answerable,redacted}.json`, `manifest.json` | `redact.py` then `derive.py` pass 2 | 432 twins with per-twin derived blocks |
| `pipeline/out/derive-report-twins.json` | `derive.py` pass 2 | same diagnostics over the twins |
| `packs/nba-transaction-legality.prose.txt` | `render_prose.py` | arm A-prime's policy text (tracked) |
| `results/*` | `run.py`, `score.py` | result rows and the scored report |

## 9. Files changed or added by this integration

| File | Change |
| --- | --- |
| `pipeline/derive.py` | **new** — the derived-fact preprocessor |
| `pipeline/DERIVED.md` | **new** — the derived-field contract as implemented, and every gap in it |
| `pipeline/tests/test_derive.py` | **new** — 44 tests |
| `packs/render_prose.py` | **new** — arm A-prime prose renderer |
| `packs/nba-transaction-legality.prose.txt` | **new** — its output |
| `harness/arms.py` | render policy honoured; `apply_render_policy` and `instance_key` added; `redact_gold` delegates |
| `harness/score.py` | rows and instances keyed by `row_id`/`twin_id`; `should_escalate` reads `variant`/`expected_decision`; `base_instance_id` prefers `pair_id` |
| `PIPELINE-STATUS.md` | rewritten (this file) |

No file under `rulearena/checkout/` was touched. Nothing was committed.
