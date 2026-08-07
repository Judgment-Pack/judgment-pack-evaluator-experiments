# Preregistration — Study 011: coverage rates for blinded record authorship

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review;
governing thereafter.**

**Nothing has run.** No authoring call has been made for this study, no
batch exists, no completion has been read, no rate has been computed. Every
number below is either a pin copied from Study 010's locked artifacts, a
registered test vector for the interval arithmetic, or a threshold chosen
before any data exists. When the batch runs, results go to `RESULTS.json`
and `ANALYSIS.md`; departures from this file go to `DEVIATIONS.md`. After
the freeze this file is never edited.

Predecessor: [`studies/010-blinded-oracle`](../010-blinded-oracle/) —
its `PREREGISTRATION.md` is the source of every ported gate and every
pinned byte, its `ANALYSIS.md` §"What follows" states the question this
study answers, and its `DEVIATIONS.md` §1 is the reason §2 forbids the
operator from reading a completion before the batch is sealed. Tracker:
evaluator-experiments issue #23, whose final comment registers this
mandate — per-class coverage *rates* over many runs of Study 010's
registered authoring call, needing none of that study's draw machinery.

## 1. The question

Study 010 asked whether a record set authored without sight of the pack
*can* reach the boundary a defect hides in. One registered call reached all
six pre-committed classes: an existence result. This study asks the
frequency question that an existence result cannot answer:

> For each pre-committed family class, how often does an independent
> authoring call — the same registered call, same prompt, same model — produce a
> record set whose **correctly labelled** records reach that class?

The answer is six rates with intervals, plus the rate at which the
authoring call fails to produce a usable record set at all. Both high and
low rates are findings. There is **no pass/fail**, no hypothesis, no
contest arm, and nothing to falsify: this is estimation. A class covered
in 4 runs out of 50 is exactly as publishable as one covered in 50 of 50,
and §8 commits to publishing whatever comes out.

Why the rates matter beyond this study: a confidence score for
independently authored or transcribed matrix rows needs to know which
classes blind authorship reliably reaches (light human review suffices)
and which it rarely reaches (full human review). §5 registers that mapping
*before* the data, so it is applied rather than fitted.

What the rates are a property of, stated once so it is not overread: **one
prompt × one model × one policy × one family**, executed on one machine on
one day. Not "independent authorship" in general. Byte-lineage, not truth,
unchanged.

## 2. The one cell

One experimental cell. Nothing varies across runs except the model's own
sampling.

### 2.1 Pinned by digest from Study 010's locked artifacts

Every input a run's meaning depends on comes from
`studies/010-blinded-oracle/` and is pinned by the sha256 that study's
`PROTOCOL-LOCK.json` registered. Three files are copied **byte-identically**
and must hash to 010's locked values:

| Ported byte-identically | sha256 (010's locked value) |
| --- | --- |
| `transcription/PROMPT.txt` | `a68dad107dc5d250a399f6a6ac43c8d06d4894d06fb21022ea7819188510d3a2` |
| `FAMILY.json` | `7c3c49e60bd3284885beaec9a08a94d0eab5798b5de4e7edf1ac10c53f5eb25f` |
| `harness/policy_mirror.py` | `276b5f7383e8ce51b5862bcfa7f1b2fa6d930b9a5d1d03b50354e09e271031ba` |

`policy/POLICY.md` is deliberately **not** copied: `PROMPT.txt` inlines the
policy verbatim, so the prompt's digest already covers the exact policy
bytes the model receives, and a second copy could drift from them. Its 010
digest is
`e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f`,
recorded for a reader checking the inlining.

Three files are ported **with changes**, because this study runs fifty runs
where 010 ran one. Each records its 010 base digest and its complete change
list in `harness/PORTS.md`, and each is pinned at its own digest before the
batch (§2.6). A change may not touch check semantics; the pre-freeze review
verifies that against the diff, and control C3 tests it end to end against
010's published numbers.

| Ported with enumerated changes | 010 base sha256 | Registered scope of the change |
| --- | --- | --- |
| `harness/transcript_check.py` | `42d977c40eed333531c096b9cdba75ac2ecceed5845dd3151f1dc010129bea9d` | the golden-context path becomes a **required** argument (010's optional default is gone) and the allowlist call is unconditional; no check logic changes |
| `harness/records_compile.py` | `e58edce30e549953b5263db2e9c230604f9192d060cbde9387585e0679671698` | `compile`/`verify` take an output root so each run compiles into its own directory; no extraction, admission, or drop-code changes |
| `transcription/authoring_call.sh` | `3b8909aae9b0ec2d52f8b8c780c3c6a544f4405dc7d31fd1becf485fcdae251d` | §2.3 |

Four digests are pinned as **references to files this study reads but does
not copy**:

| Reference | sha256 | Why |
| --- | --- | --- |
| `../010-blinded-oracle/PROTOCOL-LOCK.json` | `4966aa821325417f2cbce24a1a6ce7a10a45eefcbe2ec8fc16a4b2f1113543b1` | 010's lock does not digest itself; this pin is what makes the tables above checkable against a fixed authority rather than a mutable file |
| `../010-blinded-oracle/transcription/authoring/call-1/completion.txt` | `45deb69ea7a0d10aa43b2ec00ad623c11e3d77a15ece11c0ee220c7836c81677` | input to the replication control (§6, C3) |
| `../010-blinded-oracle/packs/vendor-screening-correct.pack.json` | `e9abfcc96f6cf558222ea85d6f33246c7f7872ac0dcb7b0e49ea73cc6394d92f` | input to the family/pack coherence control (§6, C2). No pack is evaluated or mutated here, so it is read in place rather than copied |
| `../010-blinded-oracle/transcription/GOLDEN-CONTEXT.json` | `4ff544de5edf716aeaabb3560bf22767919537f9759133740e3ab22c259ac843` | **not** a gate here; recorded so §3.2's recapture can be compared against it |

The model, the CLI, and the binary are pinned to 010's locked values:

```
model            gpt-5.6-sol
CLI              codex-cli 0.145.0
binary sha256    a2a05dafaa1acb002a45eaec0a462de5b13694fcfcd7bc43305f14781ce7be14
```

The wrapper refuses to run a slot unless the codex binary it resolves
hashes to exactly that digest and reports exactly that version string. If
the local binary has drifted by the time the batch runs, the
study **does not run with a substitute**: the drift is recorded in
`DEVIATIONS.md` and the study is either re-registered against the new pin
or abandoned. A rate measured on a different binary is a different study.
*(Observation at draft time, not a lock: the binary present in this
environment matches the pin.)*

Sampling parameters are **not** pinned beyond the CLI defaults under
`--ignore-user-config`: this CLI exposes no temperature or seed control at
`codex exec`, so the sampling configuration is whatever 0.145.0 defaults
to. It is recorded (CLI version, binary digest, argv) and not controlled.
§7 repeats this as a limitation.

### 2.2 Per-run isolation

Exactly Study 010 §4's isolation, minus its single-slot rule. Per run:

- a **fresh `HOME`** and a **fresh `CODEX_HOME` beneath it**, both created
  for that run alone, carrying only a copy of the credential
  (`$HOME/.codex/auth.json` → `<isolated home>/.codex/auth.json`). The
  fresh `HOME` is not decoration: 010's fifth pre-freeze review found
  empirically that with the operator's real home every skill directory
  under `~/.agents/skills` reaches the model. `--ignore-user-config` alone
  does not close that path;
- **`--ignore-user-config`** and an explicit **`-m gpt-5.6-sol`**;
- the environment scrubbed with `env -i` down to `PATH`, `HOME`, `TMPDIR`,
  `CODEX_HOME`;
- an **exclusively created scratch directory** for that run, whose
  resolved path lies outside every git worktree and contains no token from
  the ported `transcript_check.LEAK_TOKENS` list (which is why the batch
  refuses a scratch parent such as a path containing `jpack`);
- the prompt passed as the byte-exact contents of `transcription/PROMPT.txt`
  (no trailing newline), **stdin closed** (`< /dev/null`);
- `--sandbox workspace-write -c 'mcp_servers={}'`, as 010.

Isolation is **demonstrated per run, not asserted** — §6, control C6,
registers the per-run evidence, and C7 registers a negative control whose
job is to show the gate has power.

### 2.3 The wrapper is an adaptation, not a byte-identical port

`transcription/authoring_call.sh` is derived from 010's wrapper (base
digest pinned above). The invocation itself — fresh `HOME` and
`CODEX_HOME`, `env -i`, exclusive leak-token-free scratch outside every
worktree, `--ignore-user-config`, explicit model, binary-digest check,
byte-exact prompt, closed stdin — is 010's, unchanged. The permitted
differences are exactly these, and `harness/PORTS.md` carries the diff:

1. it takes the **slot directory** as an argument and writes there, instead
   of the single `transcription/authoring/call-1/`;
2. it **drops 010's single-slot refusal** ("the one authoring call has
   already been made"); each slot directory is still exclusive-create and
   never re-run (§7);
3. it reads its pins from the batch registry (§2.6) instead of
   `PROTOCOL-LOCK.json`, and may be told which interpreter and which codex
   binary to use — the binary's digest is still checked against the
   registry, so pointing it at another binary requires a registry that
   names that digest, which the batch registry never does;
4. it names its scratch and isolated home `s011-…` instead of `s010-…`;
5. it distinguishes its failure modes by exit status (pre-flight refusal
   with no slot left behind; a call that exited non-zero; an isolated home
   holding other than exactly one session) so §3.3's partition can be
   applied per slot, and it records the slot's UTC start and end and the
   pre-call inventory of the isolated home in `CALL.json` (§6, C6);
6. a missing operator credential is recorded rather than fatal, so the
   wrapper's own tests can run without one.

It **does not** retry, judge a completion, compile records, or decide
admissibility: it retains bytes and exits with a code. Because it is
adapted rather than ported, the review that freezes this preregistration
reviews it as its own artifact.

### 2.4 Sample size, ordering, and the shortfall rule

**N = 50** slots, fixed before the batch, executed **sequentially** in
index order 1…50 by the batch driver (`harness/batch.py`) — never in
parallel. Sequential execution keeps the independence premise as simple as
it can be; parallel calls would share provider-side backpressure and
correlate in ways nothing here could measure. All 50 slots are begun and
completed within **one UTC
calendar day**; spilling past midnight is a `DEVIATIONS.md` entry, not a
stopping rule.

At N = 50 the exact intervals of §4.3 are: k = 50 → [0.9289, 1.0000];
k = 40 → [0.6628, 0.8997]; k = 25 → [0.3553, 0.6447]; k = 1 → [0.0005,
0.1065]; k = 0 → [0.0000, 0.0711]. That is the resolution this study buys,
stated now so nobody reads more precision into a rate than 50 runs supply.

**Shortfall rule.** If the batch cannot complete all 50 slots — quota
exhaustion, transport collapse, loss of the environment — the driver
writes `SHORTFALL.json` naming the reason and the completed slot count S
*before* anything is scored, and the headline reports "S of 50 slots
completed" with the shortfall stated. Rates are then computed over the
valid runs among the S completed slots.

**Prohibited, without exception:** computing any rate before the batch is
sealed; adding slots after any rate has been computed; running a second
batch and pooling it with this one; recomputing a published rate on a
different population. A second batch, if ever run, is a separate study
with its own registration, and this study's numbers are not amended by it.
Mechanically, the driver cannot compute coverage at all — admission, the
compiler, the classifier, and the rates all live behind the scorer
(`harness/score_rates.py`), which refuses unless the batch manifest is
terminal (50 slots present, or `SHORTFALL.json` written), and the driver
refuses to create a slot once `RESULTS.json` exists. What remains possible
and is not prevented: the operator reading a `completion.txt` by eye
mid-batch. §7 says so.

### 2.5 What each slot retains

The driver retains, per slot: `CALL.json` (argv, cwd, isolated home,
environment allowlist, model, CLI identity and binary digest, integer exit
status, session count, slot index, UTC start/end, pre-call home
inventory), `stdout.raw`, `stderr.raw`, `session.jsonl`, `context.json`
(the normalized pre-prompt context digests), `completion.txt` (written
**only** when the process exited 0), and the wrapper's exit status mapped
to a transport-level refusal code. Nothing in that set is a judgment.

The scorer then derives, from those retained bytes alone: the §3 admission
verdict and its refusal code, the compiled `records/` and `RECORDS.md`,
and the per-class classification. Everything it derives is recomputable by
anyone from the published slot — which is the point of keeping the
judgment out of the driver.

All 50 slots are committed, invalid ones included (§8) — roughly 90 KB per
slot.

### 2.6 The batch registry

`harness/PINS.json` is the run-time registry: the codex binary digest,
CLI version and model; the digests of `transcription/PROMPT.txt` and
`FAMILY.json`; N; the interpreter; and the recaptured golden context's
digest, which is `null` until §3.2's capture is taken and registered.
Registered here as requirements on it: it records the digest this
preregistration has at the freeze (so a post-freeze edit is detectable),
and it records — directly or by pointing at `harness/PORTS.md` — the
digest of every ported file in §2.1 together with its 010 base digest.
The driver refuses to call anything whose binary digest is not the pinned
one; the scorer refuses to score against a prompt or family whose bytes
are not the pinned ones. The registry and `PORTS.md` are committed before
the batch begins.

## 3. Admission per run

Every gate below is Study 010's, ported and unchanged, **except** the
golden pre-prompt context, which 010 pinned to *its* environment and this
study must recapture for *this* one (§3.2). The whole point of the gates
is that a run counts as an authoring sample only if the retained evidence
shows the registered prompt was answered, once, by the pinned model, with
nothing else in the context.

### 3.1 The ported gates

`harness/transcript_check.py` (ported; the only change is §2.1's required
golden path). A run is **admissible** iff all hold:

1. **Transcript whitelist.** Every `response_item` payload is either a
   `message` with role user, developer, or assistant carrying only
   role-appropriate content items, or an **inert `reasoning` item** (one
   bearing any of `name`, `arguments`, `input`, `output`, `call_id`,
   `content`, `tool`, `tool_name`, `result` refuses). ANY other payload
   type — every call form, call output, tool role, attachment, or unknown
   type — refuses. Transcript lines are parsed with duplicate-key
   rejection.
2. **Registered prompt terminal.** Exactly one user message equals
   `PROMPT.txt`'s bytes, and no user or developer message follows it.
3. **Golden context.** The pre-prompt context reproduces this study's
   `transcription/GOLDEN-CONTEXT.json` exactly — count, roles, order, and
   normalized digests and lengths of every message before the prompt.
   Normalization is the ported one: environment paths, timestamps, dates
   and session UUIDs replaced, NFKC applied, zero-width characters
   stripped. This is an allowlist and it is what a denylist could never
   be: a paraphrase, a homoglyph, or a base64 blob need not contain a
   banned word to leak, but each changes the context and any change
   refuses.
4. **Leak denylist** (defence in depth, for a clearer refusal message):
   no pre-prompt message and no call working directory contains a token
   from the ported `LEAK_TOKENS`.
5. **Model and cwd binding.** `turn_context`, where present, names
   `gpt-5.6-sol` and the call's own working directory.
6. **Exit 0.** `CALL.json` records integer exit status 0 (a JSON boolean
   is not an integer here), and exactly one new session file exists in the
   isolated home.
7. **Completion binding.** At least one assistant message follows the
   prompt, and `completion.txt`'s bytes equal the last one's concatenated
   `output_text`.
8. **Binary pin.** `CALL.json`'s recorded binary digest and CLI version
   equal §2.1's pins.

**Compiler regeneration.** `harness/records_compile.py` (ported; the only
change is §2.1's per-run output root) turns `completion.txt` into that
run's `records/` and `RECORDS.md` with no
operator judgment: largest-span JSON array extraction with a strict
duplicate-key-rejecting decoder, then per-element admission in the
registered order `schema`, `decimal-form`, `country-form`, `id-form`,
`outcome-value`, `timestamp-form`, `duplicate-id`, first failing check
naming the drop code, no repair of any kind. `verify` then regenerates
everything from the retained completion bytes and requires byte equality,
the exact file-name set, and regular files only.

Study 010's environment-specific golden capture is **not** ported as a
gate; 010's `regions_check.py`, its 44-probe battery, and every draw,
publication, and ledger gate are not ported at all, because no evaluator,
no pack disposition, and no draw exist in this study (§8).

### 3.2 The registered pre-batch golden recapture

010's golden context was captured on a different machine, under a
different `HOME` layout, and its digests are not this environment's. The
recapture procedure is registered here, in full, before the batch:

1. Run the capture step (`harness/batch.py capture-golden`) **twice**. Each
   capture run uses the §2.2 invocation exactly — fresh `HOME`, fresh
   `CODEX_HOME`, `env -i`, exclusive scratch, stdin closed, pinned binary
   and model — with one substitution: the prompt is the registered **probe
   prompt**, `transcription/PROBE-PROMPT.txt`, whose bytes are exactly
   `Reply with exactly one word: ready` (no trailing newline).
2. The probe prompt, not the registered prompt, is used **deliberately**.
   The pre-prompt context precedes the prompt and does not depend on it —
   that is why it can be pinned at all — and using the registered prompt
   would show the operator two coverage profiles before the batch, which
   is exactly the cost Study 010's `DEVIATIONS.md` §1 records. The probe
   text carries no `LEAK_TOKENS` token; the model's answer to it is
   irrelevant and is discarded.
3. The two captures must produce **identical** normalized context lists
   (`contextVersion`, and every entry's role, order, sha256, and length).
   Identical → the capture is written to
   `transcription/GOLDEN-CONTEXT.json`, its digest replaces the `null` in
   the batch registry's `golden.sha256`, and both are committed **before
   the first batch slot runs**. Not identical → the batch does not start;
   the discrepancy and its diagnosis are recorded in `DEVIATIONS.md`, and
   the recapture
   may be repeated after the environmental cause is fixed. No
   registered-prompt data exists at that point, so this cannot be a
   data-dependent choice.
4. The recaptured capture is compared against 010's pinned golden
   (`4ff544de…`) and the comparison — equal or not, and where it differs —
   is reported in `ANALYSIS.md`. Neither outcome gates anything; it is
   simply information about how stable this context is across
   environments.
5. Both capture runs retain their `context.json` and `CALL.json`; they are
   published under `controls/recapture/` and are **not** batch slots and
   never enter any denominator.

### 3.3 Invalid runs, and the two kinds of failure

A run that fails admission or regeneration is an **invalid run**: counted,
reported with its refusal code, and excluded from the rate denominators of
§4. The invalid-run rate is itself an endpoint (§4.4, S8) — a confidence
score needs the authoring-failure rate as much as the coverage rates.

The distinction that decides every denominator, registered here because
getting it wrong would bias every rate upward:

- **pipeline-invalid** (excluded from denominators). The *apparatus or the
  transport* failed and the run says nothing about authorship: nonzero
  exit, zero or multiple new sessions, any §3.1 whitelist/terminal/golden/
  denylist/model/cwd/completion-binding violation, a binary-pin mismatch,
  or a compiler failure of the regeneration kind (byte inequality,
  file-set mismatch, I/O error).
- **authoring-empty** (**valid**, counted, coverage zero in every class).
  The evidence is admissible and the compiler ran, but the author produced
  nothing usable: the completion contains **no parseable JSON array**, or
  every element was dropped, or accepted records exist but none is
  policy-concordant. These are authorship outcomes. Excluding them would
  quietly condition every rate on the author having succeeded, which is
  not the quantity §1 asks for.

So: `records_compile`'s "no parseable array" refusal classifies the run
**authoring-empty and valid**; every other compiler error classifies it
**pipeline-invalid**. The driver records the raw refusal text either way.

Let **N** be the slots executed (50, or S under §2.4's shortfall), **I**
the pipeline-invalid runs, and **V = N − I** the valid runs. V is the
denominator of every rate in §4.1–§4.3.

## 4. Endpoints

Estimation only. **No hypothesis test, no p-value, no multiplicity
correction** — there is no test to correct. The six class intervals are
marginal 95% intervals; they are not a simultaneous 95% region and no
joint coverage is claimed.

### 4.1 The sets, per valid run

Computed by the scorer (`harness/score_rates.py`) over that run's compiled
records only — no evaluator, no pack disposition, jpack never runs:

- **A** — the run's accepted records (the compiler's output set).
- **H** — records in A whose recorded `decision.outcome` equals
  `policy_mirror.verdict(record.vendor)`. This is Study 010's H, unchanged.
- **Q** — A \ H: records reaching a class with their own label wrong.
  Retained as data, never dropped, never counted in H.
- **class_i**, i ∈ 0…5 — the records in A satisfying `FAMILY.json`
  mutation i's `predicate` under the ported
  `policy_mirror.predicate_matches`. The classes are **not disjoint**
  (010's ANALYSIS.md says so: indexes 0 and 1 can share members, 2's
  members recur in 3); coverage is non-emptiness per predicate, not a
  partition.

There are no controls in the record sets here (010's `k-wrong-*` exist to
exercise an evaluator's gates; no evaluator runs).

### 4.2 Primary endpoint

For each i ∈ 0…5:

```
k_i = |{ valid runs r : H(r) ∩ class_i(r) ≠ ∅ }|
c_i = k_i / V
```

reported as the exact fraction `k_i/V`, as a decimal to 3 places, and with
the §4.3 interval. Six numbers with six intervals; that is the study's
result. Denominators are identical across classes by construction and the
scorer asserts it.

### 4.3 Clopper–Pearson 95% intervals, normatively

Exact binomial-tail bisection. Registered so that a reader can recompute
every published bound from `RESULTS.json`'s integers alone, and so that
the arithmetic cannot drift with a platform's libm:

```
alpha         = Fraction(1, 40)                         # 0.025, one tail of a two-sided 95%
tail_ge(k,n,p) = sum over j = k..n of  C(n,j) * p^j * (1-p)^(n-j)
tail_le(k,n,p) = sum over j = 0..k of  C(n,j) * p^j * (1-p)^(n-j)

lower(k,n) = 0.0  if k == 0  else  bisect(lambda p: tail_ge(k,n,p) <  alpha)
upper(k,n) = 1.0  if k == n  else  bisect(lambda p: tail_le(k,n,p) >  alpha)

bisect(pred):                       # pred is monotone: true on [0,root), false after
    lo, hi = 0.0, 1.0
    repeat EXACTLY 200 times:       # fixed iteration count, no early exit
        mid = (lo + hi) / 2.0       # IEEE-754 double
        if pred(mid): lo = mid
        else:         hi = mid
    return lo
```

Registered numerics, all of which the CI test asserts:

- `C(n,j)` is `math.comb` — exact integers, never a float factorial.
- The tail sums are evaluated in `fractions.Fraction`: `p` is a
  double and therefore an exact binary rational, `Fraction(p)` converts it
  losslessly, and each comparison against `Fraction(1,40)` is an **exact
  rational comparison**. No floating-point `pow`, no libm, no accumulated
  rounding, no seed — the procedure is deterministic and platform-independent.
  (The brief's "fixed-seed intervals" phrasing does not apply: there is no
  randomness here to seed. See the divergence note at the end of §4.5.)
- Terms are summed in ascending `j` order. Bisection bounds are the closed
  unit interval; the returned bound is within one double-precision ulp of
  the exact root. Bounds are published to 4 decimals; `RESULTS.json`
  carries the full float and the integers `k` and `n`.
- **Registered test vectors** (n = 50, 4 dp), asserted by the harness tests
  in CI:
  `k=0 → [0.0000, 0.0711]`, `k=1 → [0.0005, 0.1065]`,
  `k=25 → [0.3553, 0.6447]`, `k=40 → [0.6628, 0.8997]`,
  `k=45 → [0.7819, 0.9667]`, `k=50 → [0.9289, 1.0000]`.

Intervals are computed for the six primary rates, for the all-six rate
(S3), and for the pipeline-invalid rate (S8). They are **not** computed
for record-level pooled quantities, because records within a run are not
independent (§4.4, S5).

### 4.4 Secondary endpoints (all descriptive; all published)

- **S1 — raw intersection rate.** `a_i = |{r : A(r) ∩ class_i ≠ ∅}| / V`:
  the class was reached by *some* accepted record, label irrelevant. The
  gap `a_i − c_i` is the label tax.
- **S2 — reached-but-mislabelled, per class.** `q_i = |{r : Q(r) ∩ class_i
  ≠ ∅}| / V`, and the **mislabel share**
  `s_i = |{r : A∩class_i ≠ ∅ and H∩class_i = ∅}| / |{r : A∩class_i ≠ ∅}|`
  (defined as 0 when the denominator is 0) — runs that reached the class
  *only* with a wrong label. This is Study 010's authoring-label-failure
  mode measured as a rate, and §5 escalates review depth on it.
- **S3 — coverage breadth per run.** The distribution over 0…6 of the
  number of classes a run covers (H-based), with counts, mean, and the
  all-six rate `c_all = |{r : all six covered}| / V` with an interval.
- **S4 — record volumes.** Per valid run: `|A|`, `|H|`, `|Q|`, the dropped
  count, and the drop-code histogram; plus totals and per-run ranges over
  the batch.
- **S5 — label accuracy.** Pooled `|H| / (|H| + |Q|)` over all valid runs,
  and the per-run mean and range. Pooled figure is descriptive only:
  records within a run share an author turn and are not independent, so no
  interval is attached to it.
- **S6 — distinct outputs.** The number of distinct `sha256(completion.txt)`
  across valid runs and the size of the largest identical group.
  Identical completions across runs are **data, not defects** — but if
  they occur they weaken the independence premise the rates rest on, so
  every rate in this study is read alongside this count, and `ANALYSIS.md`
  reports it before the rates if the largest identical group exceeds one.
- **S7 — coverage against run index.** Per class, the ordered 0/1 sequence
  over valid runs retained in `RESULTS.json`, plus first-half and
  second-half counts. A drift check, **descriptive only**: no test, no
  trend statistic, no conclusion drawn from it beyond "the sequence is
  published".
- **S8 — the pipeline-invalid rate.** `rho = I / N`, with an interval, and
  the histogram of refusal codes. Reported in the headline beside the
  coverage rates, never as a footnote.
- **S9 — wall clock.** Per-slot UTC start/end and duration, retained;
  descriptive.

### 4.5 What is reported, and how

`RESULTS.json` carries, for every rate, the integer numerator, the integer
denominator, the float point estimate, and both bounds — so every published
decimal is recomputable from integers. `ANALYSIS.md` leads with the six
per-class rates and `rho`, states S6 before any rate if outputs repeated,
and applies §5's mapping without adjusting it.

*Divergence from the design brief, recorded here rather than discovered
later:* the brief's build plan says "scorer with fixed-seed intervals".
The registered interval procedure is exact and deterministic and has no
random component, so there is nothing to seed. No bootstrap is used
anywhere in this study.

## 5. The confidence-score mapping, registered before the data

This is the product linkage the rates exist for. The thresholds below are
frozen now, before any run. The study **applies** this mapping to the
observed rates; it does not fit, tune, or re-cut it afterwards. If the
tiers it produces look wrong, they are published as computed and the
disagreement is recorded in `ANALYSIS.md` as a limitation of the mapping —
not repaired by moving a threshold.

Review depth for an independently authored or transcribed matrix row is
assigned by the class its facts fall in, inversely to that class's blind
coverage rate:

| Condition on class i | Tier |
| --- | --- |
| `c_i ≥ 0.90` **and** interval lower bound `≥ 0.80` | **LIGHT** — spot review of rows in this class |
| otherwise, `c_i ≥ 0.50` | **STANDARD** — sampled human review |
| `c_i < 0.50` | **FULL** — human review of every row in this class |

Two registered escalations, each moving a class exactly one step
(LIGHT → STANDARD → FULL; FULL is terminal):

1. **Mislabel escalation.** If `s_i ≥ 0.20` (S2), class i escalates one
   step. Reaching a class with the wrong label is worse than not reaching
   it: an absent expectation is a gap, a wrong one is an assertion.
2. **Pipeline escalation.** If `rho ≥ 0.10` (S8), **every** class
   escalates one step. An authoring pipeline that fails one run in ten
   needs supervision regardless of what it covers when it succeeds.

Study 010 §10's prediction, registered here as a stated prior and not as a
hypothesis under test: the policy text names 70, 40, and the embargo list,
so stated-boundary classes (0, and by proximity 1 and 2) are the plausible
LIGHT candidates, while the unstated interior band (5), the membership
literal (4), and the off-by-one bands (1, 2) are where misses were
predicted. The study reports what happens; the prior earns nothing.

**Explicit non-claim.** This mapping is a registered sketch, not a
validated instrument. Nothing in this study establishes that following it
produces any particular residual error rate, on this policy or any other.
It is registered before the data for one reason only: so the rates cannot
be used to invent a mapping that flatters them.

## 6. Controls and counting integrity

Two lessons from this line's own history govern this section. Study 008:
verify an independence premise **from source** before freezing it, and add
controls that bound what an endpoint can mean. Study 001 `DEVIATIONS.md`
§2: a preregistration constrains what you may claim, it does not check
that the claim was computed on the population it names — the scorer must
enforce the population itself.

**C1 — ported bytes match 010's lock.** A check recomputes the sha256 of
every byte-identical port and requires equality with §2.1's first table;
recomputes the sha256 of every adapted port and requires equality with the
digest `harness/PORTS.md` records for it, alongside the 010 base digest
that file also records; and requires
`../010-blinded-oracle/PROTOCOL-LOCK.json` itself to hash to `4966aa82…`
(010's lock does not digest itself, so without this pin the tables'
authority would be a mutable file). Any mismatch refuses. It runs in CI
and as a precondition of the batch and the scorer.

**C2 — family/pack coherence.** Every `FAMILY.json` mutation's `patch`
preimage must be present, byte-exact, at its JSON pointer in Study 010's
pack C (read in place at the pinned digest, §2.1), and the six `index`
members must be contiguous 0–5. This is the family-applies check 010 ran
inside its lock gate, reproduced here **without an evaluator**: it needs
only the pack bytes and the patch, and this study applies no patch and
produces no pack D. It bounds what a class can mean — a predicate whose
mutation no longer applies to the pack it was written against would be
measuring nothing.

**C3 — replication control against Study 010's published profile.** The
ported compiler, mirror, predicates, and this study's classifier are run
over 010's retained `completion.txt` (digest pinned in §2.1) and must
reproduce 010's published table exactly:

```
accepted = 16, |H| = 16, |Q| = 0
H ∩ class counts = (2, 2, 2, 4, 1, 1)
Q ∩ class counts = (0, 0, 0, 0, 0, 0)
```

These are the values `../010-blinded-oracle/ANALYSIS.md` published. The
test refuses on any difference. It is the end-to-end check that this
study's counting code means the same thing its predecessor's did.

**C4 — synthetic fixture with a known coverage profile.** In
`harness/tests/fixtures.py`, hand-authored completions committed as
Python constants whose expected output — accepted ids, drop codes, H/Q
membership, per-class coverage, and the resulting rates and bounds — is
registered in the same committed module, with the replication
expectation additionally pinned in `harness/PINS.json`; CI runs
compiler → classifier → scorer over them and requires equality. The fixtures are constructed to make a silent miscount
impossible to hide, and must contain at least:

- one element exercising **each** drop code (`schema`, `decimal-form`,
  `country-form`, `id-form`, `outcome-value`, `timestamp-form`,
  `duplicate-id`);
- at least one class reached **only** by a mislabelled record — so a
  scorer that conflates A with H fails the fixture rather than inflating
  `c_i` in the batch;
- at least one class reached by **no** record, so a scorer that credits
  coverage by default fails;
- at least two synthetic runs, one of them `authoring-empty` and one
  `pipeline-invalid`, so the population arithmetic (V, I, rho) and the
  §4.3 intervals are exercised at known `k` and `n`;
- the §4.3 registered test vectors, asserted to 4 decimals.

**C5 — the population filter is in code, not in the operator's head.**
The scorer reads every slot, computes each run's admission verdict and the
valid population itself with the §3.3 rule, and refuses if any slot lacks
a terminal outcome or if the slot indices are not exactly the contiguous
range 1…N. `RESULTS.json` prints the numerator and denominator of every
rate. No rate may be computed by any other path, and no rate is reported
without its denominator beside it. This is the Study 001 §2 lesson taken
literally: the endpoint's population is the scorer's job, not the
author's.

**C6 — isolation demonstrated per run.** Each slot retains, and the
admission check requires: the resolved isolated `HOME` and `CODEX_HOME`
paths; the **pre-call inventory** of the isolated home, which must be
exactly the copied credential and nothing else; the **post-call new-file
set**, which must contain exactly one `*.jsonl`; the scratch path,
screened for leak tokens and required to resolve outside every git
worktree; and `context.json`, whose digests must equal the recaptured
golden. The golden match is the operative evidence: a leaked skill,
config, or `AGENTS.md` changes the pre-prompt context, and any change
refuses.

**C7 — the isolation gate's power, demonstrated not assumed.** Before the
batch, one capture is run **deliberately without isolation** — the
operator's real `HOME`, everything else as registered, using the probe
prompt (never the registered prompt). The registered expectation: it
**fails** the golden match. Retained under
`controls/isolation-negative/`: the context digests, the refusal message,
and `CALL.json` — **not** `session.jsonl`, which would publish an
inventory of the operator's own environment. If it does *not* fail, then
the golden gate has no demonstrated power against home leakage in this
environment; that is recorded in `ANALYSIS.md` as a stated limitation and
the batch proceeds unchanged. Registering both outcomes before the batch
is what keeps this a control rather than a decision. Because this is the
one registered step that deliberately exposes the operator's real
environment to the pinned CLI, it runs only with the operator's explicit
assent; if assent is withheld, that is recorded in `DEVIATIONS.md`, the
control is skipped, and the gate's power is recorded in `ANALYSIS.md` as
undemonstrated — the batch itself is unaffected either way.

## 7. What is enforced, what is recorded, what is not prevented

Scoped to *this* design. This study has **no publication ordering, no
transparency log, and no beacon**, and needs none: 010 required them
because one unrepeatable sample had to be shown unsteerable against a
future event. Here there is no draw and no prediction — the endpoint is a
rate over slots that anyone with the pinned binary can re-run. So this
section is about isolation, ledger discipline, and exactly what a
re-runner can and cannot check.

**Mechanically enforced** (a violation refuses, or the run is scored
pipeline-invalid): the ported-byte digest table and 010's lock digest
(C1); the codex binary digest, CLI version string, and model name; the
per-run fresh `HOME`/`CODEX_HOME`, `env -i` scrub, exclusive
leak-token-free scratch outside every worktree, and closed stdin; the
pre-call home inventory and single-new-session requirement (C6); the
transcript whitelist, terminal-prompt rule, leak denylist, model/cwd
binding, integer exit 0, and completion byte-binding (§3.1); the
recaptured golden context match on every slot, with the recapture itself
required to agree across two independent captures before the batch (§3.2);
compiler regeneration with byte equality and the exact file set; slot
exclusivity (a slot directory is created once and never re-run) and
contiguous slot indices; the §3.3 valid/invalid partition and the
population filter, both in code (C5); the scorer's totality — a malformed
or missing slot artifact yields a recorded pipeline-invalid verdict, never
a bare exception; the batch/score separation (the driver cannot compute
coverage; the scorer refuses before the manifest is terminal; the driver
refuses new slots once `RESULTS.json` exists); the batch registry (§2.6)
pinning this file's post-freeze digest and every ported file's digest,
with each pinned input required to equal both its worktree bytes and its
HEAD blob.

**The retry rule, registered, and why it differs from 010.** A slot is
created exactly once and **never re-run**. A call that fails at transport —
nonzero exit, no session, a truncated stream — is **retained as an invalid
run**, and the batch simply advances to the next slot index; it does not
end the study. 010 forbade any successor to a failed call because a
retained transcript from a killed call would let an operator read the
answer and try again, and its single claim rested on one completion. That
reasoning does not transfer: here every slot's outcome is published,
invalid ones included, and the invalid rate is itself an endpoint, so
there is no favourable completion to shop for. What must be protected
instead is **the denominator**, and that is done by fixing N in advance,
creating slots exclusively and contiguously, forbidding top-ups after any
rate is computed (§2.4), and publishing every slot. Re-running an existing
slot index is refused by exclusive creation.

**Recorded but not proven:** that the retained slots are ALL the
invocations that occurred — an off-ledger call leaves no slot, exactly as
in 010; that `CALL.json`'s self-reported fields describe the process that
ran (the wrapper computes them and the wrapper's bytes are pinned, but the
operator runs the wrapper; only the model, the working directory, and the
pre-prompt context are independently corroborated, by the transcript's own
`turn_context` and the golden capture); the batch's wall-clock times and
same-day execution — nothing external timestamps this study, because
nothing needs to be shown to precede anything; the CLI's sampling
configuration, which is recorded as a version and a binary digest and is
not controlled (§2.1); that the operator did not read a `completion.txt`
during the batch — the artifacts make it possible and the design forbids
computing rates, not reading files.

**Not prevented:**

- **Discarding a batch and starting over.** Nothing external binds this
  study to the batch it publishes. An operator could run 50 slots, dislike
  the rates, delete the directory, and run 50 more. Slot exclusivity and
  contiguity prevent editing *within* a published batch, not replacing
  one. There is no cryptographic remedy here, and inventing one would be
  theatre: this study's integrity rests on ledger discipline, on
  publishing every raw slot, and on the fact that **anyone with the pinned
  binary can re-run the registered call and check the rates themselves**.
  Replication, not proof. That is the honest ceiling and it is stated in
  `ANALYSIS.md` too.
- **Contamination through the public repository.** `FAMILY.json`,
  `POLICY.md`, `PROMPT.txt`, and Study 010's records have been public in
  this repository since 010 merged (2026-08-06). The prompt names no
  mutation, no threshold beyond what the policy text itself states, and no
  pack; the transcript whitelist mechanically excludes tool use, so no
  run can *retrieve* the repository during authoring. What cannot be
  excluded is that a model snapshot has seen this material in training.
  This study cannot measure that, and the limitation stands as stated.
- **Prior-context leakage that reproduces the golden capture byte for
  byte.** The allowlist refuses any change to the pre-prompt context; it
  cannot refuse a leak that produces no change.
- **Per-run isolation limits.** A fresh `HOME` and `CODEX_HOME` close the
  paths 010 found empirically (user config, `AGENTS.md`, `~/.agents`
  skills). They do not close provider-side state: if the pinned CLI's
  backend carries any cross-session memory keyed to the credential, the 50
  runs are not independent in the way this study assumes, and neither the
  transcript nor the context digests would show it. C6 and C7 demonstrate
  *local* isolation only. S6 (distinct outputs) is the one observable that
  would hint at correlation, which is why it is reported before the rates
  when it is non-trivial.
- **One prompt, one model, one policy, one family, one day.** Every rate
  is conditional on all of them. Nothing here estimates a rate for a
  different prompt phrasing, a different vendor's model, a real policy, or
  a different defect family — and §5's tiers inherit exactly the same
  conditionality.

## 8. Out of scope, and the publication commitment

**Out of scope:** other models and other vendors (no second vendor
credential exists in this environment); prompt variants and phrasing
sensitivity; sampling-parameter sweeps (the CLI exposes none at
`codex exec`); real operational records — these are invented case files
from a model asked to imagine a diligent office and explicitly asked for
borderline cases, and the production distribution is unknown and untested
here; any evaluator or runtime behaviour (jpack never runs, no pack is
evaluated, no disposition is produced); any draw, beacon, transparency
log, or one-shot machinery; validation of §5's mapping; and everything
Study 010 §10 and Study 009 §11 excluded. No conformance claim of any
kind is made, here or anywhere in this repository.

**Publication commitment.** Everything is published regardless of outcome:

- all 50 raw slots (or S under the shortfall rule), **including every
  invalid one**, with `CALL.json`, `session.jsonl`, `stdout.raw`,
  `stderr.raw`, `context.json`, `completion.txt`, the compiled `records/`
  and `RECORDS.md`, and the per-run admission verdict, refusal code, and
  class classification the scorer derives from them;
- both recapture captures and the C7 negative control (digests and
  refusal only, per §6);
- `RESULTS.json` with every rate's integers and bounds, and `ANALYSIS.md`
  leading with the six rates and `rho` whatever they are — a class covered
  in 2 runs of 50 is published as 2/50 with its interval, in the headline,
  not in an appendix;
- `DEVIATIONS.md` for every departure from this file, written as it
  happens;
- a post-run cross-vendor adversarial review with per-finding dispositions,
  as this line's regime requires.

No slot is deleted. No rate is recomputed on a different population after
the fact. If the study is abandoned before the batch — pin drift, failed
recapture — that is published too, in `DEVIATIONS.md`, with the reason.

## 9. Bounds

Fifty samples of one prompt against one model under one policy, on one
machine, on one day, with one defect family of six classes. The intervals
of §2.4 are the resolution: at N = 50 a perfect class is bounded below at
0.93 and a half-covered class carries ±0.14, so this study can separate
"reliably covered" from "rarely covered" and cannot resolve much finer
than that.

The family is public before authoring and has been since Study 010 merged;
the policy text itself names 70, 40, and the embargo list, so
stated-boundary classes are expected to be easy and the informative
classes are the unstated interior band (5), the membership literal (4),
and the off-by-one bands (1, 2). A high rate on class 0 would be close to
tautological; a high rate on class 5 would not.

Coverage here means *a correctly labelled record whose facts fall in a
registered predicate* — nothing more. It does not mean the record is
true, that the office it describes exists, that the label was reasoned to
rather than guessed, or that a real transcription pipeline would produce a
similar distribution. It does not measure whether an evaluator would then
surface the defect: 010 established that leg, and this study does not
re-run it. The rates are a property of the pinned tuple in §2.1 and expire
with it — a new CLI build, a new model snapshot, or a re-phrased prompt
requires a new study, not an extrapolation.

Byte-lineage, not truth, unchanged.
