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

`policy/POLICY.md` is deliberately **not** copied: the prompt's digest
already covers the exact policy bytes the model receives, and a second copy
could drift from them. Its 010 digest is
`e46f8c48a76566390b54f59d7dc3c1db5ecd30916af21307944737b5b6735f1f`,
recorded for a reader checking the inlining. The inlining relation is stated
exactly rather than as "verbatim", because it is not quite byte-equality:
010's `POLICY.md` ends in a newline and the prompt is passed with **no**
trailing newline, so **`POLICY.md`'s bytes with its final LF removed appear
as a contiguous span of `PROMPT.txt`**. A harness test asserts exactly that
(`harness/tests/test_controls.py`, `InlinedPolicy`). Nothing about 010/011
comparability turns on it — the prompt itself is byte-identical and pinned on
both sides — but "verbatim" was technically false and is not a thing to leave
standing in a file that governs.

Three files are ported **with changes**, because this study runs fifty runs
where 010 ran one. Each records its 010 base digest and its complete change
list in `harness/PORTS.md`, and each is pinned at its own digest before the
batch (§2.6). A change may not touch check semantics; the pre-freeze review
verifies that against the diff. Of the three, `records_compile.py` is the one
control C3 replicates against 010's published numbers (§6 C3) — the compiler,
the mirror and the class arithmetic, on 010's retained completion.
`transcript_check.py` is exercised by the admission tests and, on real bytes,
by §3.2's golden procedure; `authoring_call.sh` is exercised by the
wrapper-driven harness tests. No control claims more than that.

Every digest in both tables is verified **in code, before anything runs**,
and each side is checked against the authority that side actually answers to
(§6 C1). `harness/PORTS.md` is an editable file in *this* study, so it cannot
be the authority for what 010's bytes were; `studies/010-blinded-oracle/PROTOCOL-LOCK.json`
is, and its own digest is pinned in `harness/PINS.json`. So
`harness/integrity.py`, in this order: verifies 010's lock against that pin;
reads the lock's `lockedInputs` map; requires every source in `PORTS.md` to be
locked there and both the file in `studies/010-blinded-oracle/` and the source
digest `PORTS.md` records to equal **the lock's** digest for it; requires every
destination here to equal the digest `PORTS.md` records; and requires the three
**byte-identical** ports above to equal 010's *locked* digest as well, so that
claim is a checked relation rather than a prose column. `harness/batch.py` runs
all of it before it creates a slot and `harness/score_rates.py` before it reads
one.

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
hashes to exactly that digest **and reports exactly that version string,
both checked before the call is made**. An earlier draft read `--version`
only afterwards, which made a drifted CLI something the scorer noticed on a
call already spent; the sentence below says the study does not run with a
substitute, and a gate that fires after the fact is not that. If
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
  (`$HOME/.codex/auth.json` → `<isolated home>/.codex/auth.json`) where one
  exists. The fresh `HOME` is not decoration: 010's fifth pre-freeze review
  found empirically that with the operator's real home every skill directory
  under `~/.agents/skills` reaches the model. `--ignore-user-config` alone
  does not close that path. The copy is **deleted when the slot is sealed**
  and `CALL.json` records both the copy and the deletion: fifty runs must not
  leave fifty copies of a live credential under one scratch parent;
- **`--ignore-user-config`** and an explicit **`-m gpt-5.6-sol`**;
- the environment scrubbed with `env -i` down to `PATH`, `HOME`, `TMPDIR`,
  `CODEX_HOME`, each **constructed rather than inherited**. `PATH` is six
  fixed system directories plus one per-run directory holding a single
  symlink to the pinned binary: no `$HOME` expansion, nothing of the parent
  `PATH`. (010's wrapper wrote `PATH=…:$HOME/.local/bin`, which the *outer*
  shell expands, so its "scrubbed" child `PATH` ended in the operator's real
  home — on this machine a directory that also holds an executable named
  `jpack`, one of the leak tokens the same wrapper screens the scratch path
  for.) `TMPDIR` is a directory inside that run's own scratch, never the
  shared `/tmp`: the pinned CLI's sandbox is writable at
  `[workdir, /tmp, $TMPDIR]`, so a shared `TMPDIR` would put every other
  run's tree inside this run's writable set. `CALL.json` records the exact
  values, so a published slot shows what the child actually had; what `/tmp`
  itself still exposes is stated in §7;
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
   binary to use — the binary's digest and the CLI's version string are still
   checked against the registry **before the call**, so pointing it at another
   binary requires a registry that names that digest, which the batch registry
   never does; the interpreter must be the implementation and version series
   the registry pins; and the registry's own sha256 is recorded in `CALL.json`
   as `pinsSha256`, so a run made under a substituted registry is identifiable
   from the slot rather than only from the operator's shell history (§2.6);
4. it names its scratch, its isolated home and its per-run binary directory
   `s011-…` instead of `s010-…`;
5. it distinguishes its failure modes by exit status (pre-flight refusal
   with no slot left behind; a call that exited non-zero; a call that
   produced other than exactly one **new** session) so §3.3's partition can
   be applied per slot, and it records the slot's UTC start and end and the
   **recursive pre-call inventory** of the isolated home in `CALL.json`
   (§6, C6);
6. a missing operator credential is recorded rather than fatal, so the
   wrapper's own tests can run without one — and, per §6 C6, so can the
   study: the recorded inventory is `['.codex', '.codex/auth.json']` when a
   credential was copied and `['.codex']` when there was none, and both are
   admissible;
7. the credential copy is **deleted** after the call terminates and the slot
   is sealed, and `credentialRemoved` records it; traps on `EXIT`, `INT`,
   `TERM` and `HUP` remove the copy on the abnormal paths too. §2.5 names
   exactly which deaths that covers and which it cannot;
8. `PATH` and `TMPDIR` are constructed rather than inherited, and their
   values — not only their names — are recorded in `CALL.json` (§2.2);
9. the run's session is identified as the **new** `*.jsonl` under the run's
   `CODEX_HOME` (the set difference across the call) rather than as the only
   one in the tree. In the isolated case the before-set is empty and this is
   010's rule unchanged; it exists so that §6 C7, which runs against the
   operator's real `.codex`, can reach its registered comparison instead of
   refusing on a session count;
10. `ISOLATION=operator-home` runs §6 C7 and nothing else: it refuses any
    prompt but the probe, copies and deletes no credential, and takes no
    inventory of the operator's home. `harness/batch.py
    capture-isolation-negative` is its only caller;
11. it stamps into `CALL.json` the digest of the golden capture the driver
    verified at preflight (`goldenSha256`, empty for the probe calls, which
    precede the golden). §3.2's "a capture derived after the batch cannot be
    substituted" is then a per-slot check rather than an assertion about
    ordering: a re-pinned capture makes every slot `golden-mismatch`.

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

At **V = 50** the exact intervals of §4.3 are: k = 50 → [0.9289, 1.0000];
k = 40 → [0.6628, 0.8997]; k = 25 → [0.3553, 0.6447]; k = 1 → [0.0005,
0.1065]; k = 0 → [0.0000, 0.0711]. That is the resolution this study buys,
stated now so nobody reads more precision into a rate than 50 runs supply.

**That table is denominated in V, not in N, and V = N − I is data.** Every
rate in §4.1–§4.3 is computed over the valid runs, so the intervals above
are the ones this study gets **only if no run is pipeline-invalid** — and
S8 exists precisely because I may not be 0. At V = 45 a perfect class is
bounded below at 0.9213 rather than 0.9289 and a half-covered class carries
roughly ±0.15; at V = 40, 0.9119 and ±0.16. (Both are the root of
`p^V = 0.025`, and a harness test asserts that the bounds in this sentence
and in §9 are the ones this study's own interval code computes. An earlier
draft carried two four-decimal values the scorer never agreed with, which is
the direction of error that matters least and is still a registered claim the
code does not support.) No table here is a promise about
the published intervals: `RESULTS.json` carries k and V for every rate and
the bounds recompute from them.

**Shortfall rule.** If the batch cannot complete all 50 slots — quota
exhaustion, transport collapse, loss of the environment — the driver
writes `SHORTFALL.json` naming the reason and the completed slot count S
*before* anything is scored, and the headline reports "S of 50 slots
completed" with the shortfall stated. Rates are then computed over the
valid runs among the S completed slots. Two things bound that rule
mechanically: `batch.py shortfall` **refuses** when the slots present are
not fewer than the registered N (a declaration cannot unblock a full or
over-full batch), and the scorer requires the declaration's recorded count
to equal the contiguous slots actually present. What it does **not** bound:
a batch that dies mid-way still leaves a slot per index, because the driver
retains a refusal record and advances (§7's retry rule), so the common
shape of "the environment died" is a full batch with a high pipeline-invalid
rate rather than a shortfall. The shortfall path is therefore mostly the
**deliberate stop**, and §7 records that honestly rather than presenting it
as involuntary.

**Resume after a crash.** `batch.py run --start K` continues at slot K. The
ledger `BATCH.json` holds one append-only record per slot and a resumed
invocation **merges** into it, refusing if it would overlap a slot the
ledger already records; a partially written slot is never re-run (exclusive
creation) and its state is recorded in `DEVIATIONS.md`.

**Prohibited, without exception:** computing any rate before the batch is
sealed; adding slots after any rate has been computed; running a second
batch and pooling it with this one; recomputing a published rate on a
different population. A second batch, if ever run, is a separate study
with its own registration, and this study's numbers are not amended by it.
Mechanically: the driver cannot compute coverage at all — admission, the
compiler, the classifier, and the rates all live behind the scorer
(`harness/score_rates.py`), which refuses unless the batch is terminal
(exactly N slots, or a matching `SHORTFALL.json`, never both); the driver
refuses to create a slot once `RESULTS.json` exists; and the scorer has
**no flag that writes a rate table anywhere else and no flag that names any
input either** — the registered command takes the slot directory and an
optional record-emission directory, every other argument refuses, and
`RESULTS.json` and `RATES.md` go to the study root or nowhere, so seeing the
rates always arms the guard. The emission directory is required to be disjoint
from the slot tree, so publishing the rates cannot also add a slot to the
population they were computed over. What remains possible and is not prevented: the operator reading
a `completion.txt` by eye mid-batch, and stopping the batch for that reason
under a shortfall declaration. §7 says so.

### 2.5 What each slot retains

The driver retains, per slot: `CALL.json` (argv, cwd, isolated home and
`CODEX_HOME`, the environment's names **and values**, model, CLI identity
and binary digest, integer exit status, new-session count, slot index, UTC
start/end, the recursive pre-call inventory of the isolated home, whether the
credential was copied and removed, and the digests of the **registry**
(`pinsSha256`) and the **golden capture** (`goldenSha256`) this run was made
under), `stdout.raw`, `stderr.raw`, `session.jsonl`, `context.json` (the
normalized pre-prompt context digests), `completion.txt` (written **only**
when the process exited 0), and the wrapper's exit status mapped to a
transport-level refusal code — in the slot's own `REFUSAL.json` when it is
not 0, and in the batch ledger `BATCH.json`, which holds one append-only
record per slot and is merged rather than rewritten by a resumed run. Nothing
in that set is a judgment.

**What a slot retains when the wrapper refused before calling.** Wrapper exit
1 is a pre-flight refusal that leaves no `CALL.json`; the driver still creates
the slot and writes `REFUSAL.json`, so the population has no invisible
members. Such a slot has **no clock** — the wrapper records `startedAt` and
`endedAt` in `CALL.json` and the ledger deliberately carries none — and it
scores `slot-shape`. §4.4 S9 is denominated accordingly.

**Which deaths the credential cleanup covers, exactly.** The seal path removes
the copy and records `credentialRemoved`; traps cover `EXIT` (which includes a
`set -e` death and a failing helper), `INT`, `TERM` and `HUP`. A signal
delivered to the wrapper's process group — the ordinary Ctrl-C, the ordinary
`kill` — is therefore cleaned up. Two things are **not** covered and no
process can cover them: `SIGKILL` and power loss run no handler at all. The
residual is one file, `<isolated home>/.codex/auth.json`, under the operator's
own scratch parent, and the remedy is the operator's: after a `SIGKILL` or a
crash, delete the scratch parent's leftovers by hand. A harness test kills a
wrapper mid-call with `SIGTERM` and requires the copy to be gone; nothing
claims more than that.

The scorer then derives, from those retained bytes alone: the §3 admission
verdict and its refusal code, the compiled `records/` and `RECORDS.md`,
and the per-class classification. Everything it derives is recomputable by
anyone from the published slot — which is the point of keeping the
judgment out of the driver.

All 50 slots are committed, invalid ones included (§8) — roughly 90 KB per
slot.

What is **not** retained and not published: the per-run scratch trees and
isolated homes under the operator's scratch parent. They are the model's
workspace and the session store, both already represented in the slot by
`session.jsonl` and the recorded paths, and they stay on the operator's disk
until removed by hand. The one thing the wrapper does clean is the credential
copy, deleted per run (§2.2), so a full batch does not leave fifty live
credentials behind.

### 2.6 The batch registry

`harness/PINS.json` is the run-time registry: the codex binary digest,
CLI version and model; the digests of `transcription/PROMPT.txt`,
`transcription/PROBE-PROMPT.txt` and `FAMILY.json`; N; the interpreter; the
recorded operator assent for §6 C7; and the recaptured golden context's
digest, which is `null` until §3.2's capture is taken and registered.
Registered here as requirements on it: it records the digest this
preregistration has at the freeze (so a post-freeze edit is detectable),
and it records — by pointing at `harness/PORTS.md` — the digest of every
ported file in §2.1 together with its 010 base digest.

**The committed `harness/PINS.json` is the registry of record, and that is
enforced per run.** The **driver** takes `--pins`, because the harness tests
drive the real wrapper against a stand-in binary and a stand-in binary needs a
registry naming its digest. The **scorer does not**: the registered scoring
command takes no registry, family, prompt or golden path at all, and derives
each of them from the harness's own location (§7). Both halves of that are
needed, and the second was added after review found the first insufficient on
its own. Per run: the wrapper records the sha256 of the registry it ran under
in `CALL.json` (`pinsSha256`), the scorer **computes the committed
`harness/PINS.json`'s digest itself**, and any slot whose stamp differs is
`registry-mismatch`, pipeline-invalid (§3.3). Per population: N, the class
definitions, the model, the binary and the prompt all come from the committed
registry and the committed files, because there is no argument through which
another one could arrive — a supplied registry identical to the committed one
except for `batch.runs` would otherwise have defined the denominator of
everything published, while every per-slot stamp still matched. A registry that
renames the model or the binary is refused per slot on those members too, and
one that changes N is refused by terminality before a slot is read (§2.4).

One ordering consequence, registered rather than discovered: **`PINS.json` is
not edited between the batch and the scoring.** The freeze digest is filled at
the freeze, the golden digest before slot 1, and after that the file stands —
any later edit makes every slot `registry-mismatch`, which is a loud refusal
and not a silent redefinition, but it is still a refusal, and `DEVIATIONS.md`
is where an unavoidable one would be recorded.

What each of those pins does at run time, all of it in code:

- the driver refuses to call anything whose binary digest or reported CLI
  version is not the pinned one, refuses to make any call while
  `preregistration.sha256` is `null` or does not match this file, and refuses
  to create **any** slot while `golden.sha256` is `null` or the file at the
  golden path does not hash to it (§3.2);
- the scorer refuses to score against a prompt, family or golden capture whose
  bytes are not the pinned ones, and refuses while `preregistration.sha256` is
  `null` or this file's bytes are not the frozen ones. The null case is a
  refusal and not a skip: a registry merged with its null intact would leave
  the freeze check permanently unarmed, which is exactly the shape of
  unenforced claim §7 exists to refuse;
- both refuse unless the running interpreter is the implementation and version
  **series** the registry pins, and the wrapper refuses before it calls
  anything if `PYTHON_BIN` is not (`README.md`'s runbook names the interpreter
  explicitly through `$PY` for that reason, and so does §3.2 and §6 C7). The patch level is recorded and not required: CI pins the series
  and resolves whatever patch release is current, and this study's arithmetic
  is exact rationals and integer combinatorics;
- both refuse if any file in `harness/PORTS.md`'s table, on either side, or
  010's `PROTOCOL-LOCK.json`, is not at its recorded digest (§6 C1);
- `batch.py capture-isolation-negative` refuses unless the registry records
  the operator's assent as granted (§6 C7).

The registry and `PORTS.md` are committed before the batch begins, and the
golden digest is committed before slot 1.

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

1. Run

   ```sh
   "$PY" harness/batch.py capture --scratch-parent DIR
   ```

   `$PY` is the registered interpreter, as in `README.md`'s runbook
   (`PY=$(command -v python3.12)`). A bare `harness/batch.py` runs under
   whatever the shebang resolves — on the machine this study was written on,
   CPython 3.8 — and every command here refuses under an unregistered
   interpreter, so the command as written has to name it.

   which makes **two** probe calls into `controls/recapture/attempt-1/`
   (`capture-001`, `capture-002`) and then derives the capture from them.
   Two is a floor and it is enforced where the derivation happens, not only
   where the calls are made: `capture --runs 1` refuses before it spends a
   call, and the derivation itself refuses fewer than two agreeing capture
   slots however it is invoked (`--min-slots 1` included). One capture cannot
   show that a context reproduces, and a context that might vary run to run is
   not an allowlist.
   Two capture slots are also required to be two **calls**. The rule's meaning
   is that two independent probe invocations reproduced the same context, and
   counting slots does not say that: a copied slot, or one call's transcript
   retained under two names, agrees with itself perfectly. The derivation
   therefore refuses when any two capture slots share any of the raw retained
   evidence that identifies a call — the `session.jsonl` bytes, the session id
   the transcript records for itself, or the `CALL.json`'s own start, end,
   working directory and isolated home. Deliberately raw: the *normalized*
   context digests are what two honest independent calls are supposed to share,
   and checking those for distinctness would refuse exactly the outcome the
   recapture exists to demonstrate.
   Each capture call uses the §2.2 invocation exactly — fresh `HOME`, fresh
   `CODEX_HOME`, `env -i`, exclusive scratch, stdin closed, pinned binary
   and model — with one substitution: the prompt is the registered **probe
   prompt**, `transcription/PROBE-PROMPT.txt`, whose bytes are exactly
   `Reply with exactly one word: ready` (no trailing newline). (The second
   half alone, for the case where the calls were made and the derivation was
   not, is `"$PY" harness/batch.py capture-golden --slots DIR --out PATH`, and
   it takes `--pins PATH` like every other `batch.py` command (the scorer takes
   none at all, §7). `--out` has no default, so a derivation never lands at the registered path by
   accident; it refuses a directory holding batch slots, so a golden capture
   can never be derived from the batch's own runs; it refuses any capture slot
   whose `CALL.json` does not record a **probe** call at the pinned probe-prompt
   digest, because a directory name is not evidence of which prompt was
   answered; and it runs the same ported-bytes, interpreter and freeze
   preflight the command that makes the calls runs, because this half derives
   the artifact every later admission is checked against.)
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
   the first batch slot runs**.

   Exactly how much of that ordering is checked, because the halves differ.
   **Checked:** `batch.py` refuses to create **any** slot while the golden file
   is absent, while the registry's digest is `null`, or while the two disagree,
   and the scorer refuses on the same three conditions; those three bind the
   golden *file* to the pin. What binds each *run* to that file is the digest
   the driver stamps into every slot's `CALL.json` (§2.3 item 11), so a capture
   derived after the batch and re-pinned cannot re-admit the runs it was derived
   to fit — the file matches the new pin, and every slot now names a capture
   that is not it, which is `golden-mismatch` (§3.3). And a capture cannot be
   registered after a rate exists without the attempt being visible: the driver
   refuses to create a slot once `RESULTS.json` exists, so a golden that entered
   the registry afterwards has no slots stamped with it. **Not checked:** that
   either file was *committed*. This study has no lock-commit machinery and
   compares nothing to a `HEAD` blob (§7); committing both before slot 1 is
   ledger discipline this file records, not an ordering the driver enforces.
   That is the difference between an ordering this file asserts and one a
   reader checks per slot. Not
   identical → the batch does not start; the discrepancy and its diagnosis
   are recorded in `DEVIATIONS.md`, and the recapture may be repeated after
   the environmental cause is fixed — the repeat runs the same command and
   lands in `controls/recapture/attempt-2/`, so no capture is ever
   overwritten and every attempt is published (§8). No registered-prompt
   data exists at that point, so this cannot be a data-dependent choice.
4. The recaptured capture is compared against 010's pinned golden
   (`4ff544de…`) and the comparison — equal or not, and where it differs —
   is reported in `ANALYSIS.md`. Neither outcome gates anything; it is
   simply information about how stable this context is across
   environments.
5. Both capture runs retain their `context.json` and `CALL.json`; they are
   published under `controls/recapture/attempt-N/` and are **not** batch
   slots and never enter any denominator.

### 3.3 Invalid runs, and the two kinds of failure

A run that fails admission or regeneration is an **invalid run**: counted,
reported with its refusal code, and excluded from the rate denominators of
§4. The invalid-run rate is itself an endpoint (§4.4, S8) — a confidence
score needs the authoring-failure rate as much as the coverage rates.

The distinction that decides every denominator, registered here because
getting it wrong would bias every rate upward:

- **pipeline-invalid** (excluded from denominators). The *apparatus or the
  transport* failed and the run says nothing about authorship.
- **authoring-empty** (**valid**, counted, coverage zero in every class).
  The evidence is admissible and the compiler ran, but the author produced
  nothing usable: the completion contains **no parseable JSON array**, or
  every element was dropped, or accepted records exist but none is
  policy-concordant. These are authorship outcomes. Excluding them would
  quietly condition every rate on the author having succeeded, which is
  not the quantity §1 asks for.

The partition is registered **exhaustively**, code by code: this table is
every outcome `harness/score_rates.py` can assign to a run, and a harness
test parses it out of this file and diffs it against both the scorer's own
`CODE_PARTITION` table and the codes its `admit()` and `score_run()` can
actually return. A code in one and not the others is a test failure, so
this list cannot drift from the counting.

| outcome | partition |
| --- | --- |
| `slot-symlink` | pipeline-invalid |
| `slot-irregular` | pipeline-invalid |
| `slot-shape` | pipeline-invalid |
| `call-unreadable` | pipeline-invalid |
| `model-mismatch` | pipeline-invalid |
| `binary-mismatch` | pipeline-invalid |
| `cli-mismatch` | pipeline-invalid |
| `registry-mismatch` | pipeline-invalid |
| `golden-mismatch` | pipeline-invalid |
| `isolation-unproven` | pipeline-invalid |
| `session-count` | pipeline-invalid |
| `call-nonzero-exit` | pipeline-invalid |
| `no-session` | pipeline-invalid |
| `no-completion` | pipeline-invalid |
| `no-context` | pipeline-invalid |
| `transcript-refused` | pipeline-invalid |
| `context-mismatch` | pipeline-invalid |
| `completion-unreadable` | pipeline-invalid |
| `compile-refused` | pipeline-invalid |
| `regeneration-mismatch` | pipeline-invalid |
| `refusal-conflict` | pipeline-invalid |
| `scorer-error` | pipeline-invalid |
| *(no code, no parseable array)* | **authoring-empty — valid, in every denominator, covering nothing** |
| *(no code)* | **valid** |

Eight of those need their registration stated rather than implied, because
they are gates §3.1's list does not name:

- `slot-symlink` and `slot-irregular` — **a slot tree holds regular files and
  directories only.** Every entry beneath the slot, and the slot itself, is
  classified by `lstat` **before anything in the tree is opened**, and anything
  that is not a regular file or a directory scores the run pipeline-invalid
  before any other check runs: a symlink under `slot-symlink`, and every other
  type — FIFO, socket, character or block device, door, or an entry that cannot
  be stat'd — under `slot-irregular`. Two codes because they say different
  things; one rule because the rule is about the slot tree and not about any
  file name. The general rule is registered rather than the narrow one because
  the narrow one is how this was found. A link is a retained byte the slot does
  not contain, so the published evidence is not the evidence that was counted,
  and a link makes a file's *existence* conditional on its target — a
  **dangling** `REFUSAL.json` answers an existence check with "no refusal", and
  a slot the batch terminated is counted as one it never touched. A FIFO,
  socket or device is not retained evidence at all, and it does something
  worse: `open()` on a FIFO **blocks**, so a scorer that read one would hang
  over the whole batch instead of refusing one slot. That is why the type is
  decided by `lstat` and why this check is first. Study 010's seal used the
  same rule, and it is stated here as a property of the slot tree;
- an entry named `run-NNN` claims a slot index **whatever its type**, and is
  scored rather than skipped: a directory, a link, a FIFO or a plain file all
  enter the tree as slots and are refused under the code their type earns.
  Skipping them punched a hole in the contiguous indices and refused the whole
  scoring, where the name is what claimed the index and the name is what has to
  answer for it;
- `context-mismatch` — the retained `context.json` must be what
  `session.jsonl` recomputes. A slot whose two artifacts disagree is not
  evidence about authorship;
- `cli-mismatch` — §3.1 gate 8's binary pin, applied to the recorded CLI
  version string as well as the digest;
- `registry-mismatch` — the run's recorded `pinsSha256` is not the digest of
  the committed `harness/PINS.json` (§2.6). The cell is the registry the runs
  were *made under*, and a run made under another one is a run in another
  cell, whatever that registry says;
- `golden-mismatch` — the run's recorded `goldenSha256` is not the capture
  this scoring is using (§3.2). It is the code a post-batch capture produces,
  which is why the recapture's ordering is checkable and not merely
  registered;
- `isolation-unproven` — §6 C6's per-run evidence, absent or contradicted;
- `refusal-conflict` — the batch recorded a refusal for this slot and the
  retained bytes nevertheless admit it. This is not a retreat from "the
  scorer never trusts the batch's refusal record": the scorer still
  recomputes admission from the bytes and never lets a `REFUSAL.json` make
  an inadmissible run look examined. It refuses the *contradiction* — a slot
  the wrapper says it failed to complete and whose bytes look complete is a
  slot whose provenance is unexplained, and an unexplained slot is not a
  sample. It is the one code that can fire on bytes that would otherwise
  pass, and it is registered here so that it appears in S8's histogram as
  something a reader was warned about.

Also registered: `records_compile`'s "no parseable array" refusal
classifies the run **authoring-empty and valid**; every other compiler
error classifies it **pipeline-invalid**. The driver records the raw
refusal text either way.

`scorer-error` is §7's totality rule: an unexpected exception during one
slot's admission becomes that slot's recorded verdict rather than the end
of the scoring. It should never fire, and if it does the study says so in
the histogram instead of dying.

**Totality covers the batch's own refusal evidence too**, and it is registered
here because an earlier draft read `REFUSAL.json` *outside* the total path and
the table above was therefore not exhaustive. Every per-slot JSON the scorer
reads — `CALL.json`, `context.json`, and `REFUSAL.json` — is read inside that
path and through the duplicate-key-rejecting loader. A `REFUSAL.json` that is
missing is a slot the batch did not refuse. A `REFUSAL.json` that exists and
is **malformed, truncated, duplicate-keyed, of the wrong type, or carries no
refusal code** is unusable refusal evidence: the slot scores `scorer-error`,
pipeline-invalid, with the error retained, and the scoring of every other slot
continues. It is deliberately not treated as "no refusal": the file's presence
means the batch terminated that slot, and a slot whose termination is
unexplained is not a sample. The batch writes a code on every refusal it
records, so an honest slot never reaches this.

**A `REFUSAL.json` that is a symlink or a FIFO is not read at all**: the slot
is already refused `slot-symlink` or `slot-irregular` above, and the refusal
record is read only from a slot whose tree is regular files and directories.
That ordering is the point. The strict loader in the paragraph above runs only
when the file *exists*, and a dangling link does not exist by that test — so
before this rule the one shape that made a batch-terminated slot look untouched
was the one shape the strict loader never saw; and a FIFO by that test exists,
after which `open()` would never return. The general rule refuses both without
having to anticipate either.

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
result. Denominators are identical across classes by construction, and the
scorer asserts it: it collects the six `trials` values it just wrote and
refuses the whole scoring unless the set is exactly `{V}`.

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

**The frozen interval scope**, stated as one list because two defensible
readings are still two: an interval is computed and published for every rate
whose denominator is V or N — the six primary rates (§4.2); the raw, Q and
Q-only per-class intersections (S1, S2); the all-six rate (S3); and the
pipeline-invalid rate (S8). It is **not** computed for the mislabel share
`s_i`, whose denominator is the runs that reached the class rather than the
valid runs, nor for any record-level pooled quantity, because records within
a run are not independent (S5). A harness test walks `RESULTS.json` and
requires the set of blocks carrying `ci95` to be exactly that list, so this
scope is checked rather than described.

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
  count, and the drop-code histogram; plus totals and, for each of those four
  counts, the per-run minimum, mean and maximum over the valid runs
  (`records.acceptedPerRun`, `hPerRun`, `qPerRun`, `droppedPerRun` in
  `RESULTS.json`, and a row each in `RATES.md`). All four ranges are emitted:
  an earlier draft registered them and the scorer emitted one.
- **S5 — label accuracy.** Pooled `|H| / (|H| + |Q|)` over all valid runs,
  and the per-run mean and range **over the valid runs with at least one
  accepted record** (`|H| + |Q| > 0`). That denominator is registered rather
  than left to be discovered: a run whose author produced no policy-concordant
  record has no label accuracy at all, and averaging it in as 0 would be
  inventing one. `RESULTS.json` publishes both counts —
  `labelAccuracy.perRunTrials` and `perRunExcluded` — so the exclusion is
  visible beside the mean rather than implied by it. The pooled figure is
  descriptive only: records within a run share an author turn and are not
  independent, so no interval is attached to it.
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
  the histogram of refusal codes over §3.3's registered code table.
  Reported in the headline beside the coverage rates, never as a footnote.
  At `rho ≥ 0.10` it also raises §5's stated caution over the whole batch —
  a caution, not a tier change.
- **S9 — wall clock.** Per-slot UTC start and end, and their difference,
  retained in each slot's `CALL.json`; descriptive, and the scorer never reads
  them, so `RESULTS.json` stays byte-stable. **Its denominator is stated
  rather than assumed:** S9 is defined over the slots that reached the call —
  those with a `CALL.json`. A wrapper pre-flight refusal (exit 1) is a
  registered outcome that leaves a `REFUSAL.json` and no clock (§2.5), and the
  ledger deliberately carries none, so those slots have no start, end or
  duration and `ANALYSIS.md` reports S9 as "over the M of N slots that reached
  the call", with N − M named. Claiming a duration for every counted slot
  would be claiming a number that was never recorded.

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
assigned from the classes its facts fall in, inversely to those classes'
blind coverage rates.

**Per class**, the tier is decided by **one quantity in one unit**: the exact
Clopper–Pearson lower bound of §4.3, written `L_i`.

| Condition on class i | Tier |
| --- | --- |
| `L_i ≥ 0.80` | **LIGHT** — spot review of rows in this class |
| otherwise, `L_i ≥ 0.40` | **STANDARD** — sampled human review |
| `L_i < 0.40` | **FULL** — human review of every row in this class |

**Per row, the composition rule**, registered because the per-class table
alone is not a function on rows. §4.1 says the classes are **not disjoint**
(010's `ANALYSIS.md` says so; a non-embargoed row at risk exactly 70 matches
classes 0 and 1), and a row can also match none of them. Two clauses close
both cases:

1. a row matching **several** classes takes the **strictest** of their tiers
   (FULL > STANDARD > LIGHT). Review depth is a floor on effort, and the
   class with the worst blind coverage is the one that says how much of this
   row nobody looked at;
2. a row matching **no** registered class takes **FULL**. This study measured
   six predicates and establishes nothing about a row outside all of them,
   and the conservative reading of "nothing is known here" is full review.

This is `harness/score_rates.row_review_tier()`, with harness tests on both
clauses, so the mapping's total-ness is checked rather than asserted. No row
is scored in *this* study — it computes per-class tiers only — so the
function is the registration of the product rule, not a step in the batch.

*Why one criterion and not two.* An earlier draft conjoined a point
estimate (`c_i ≥ 0.90`) with a bound (`≥ 0.80`). That is not a frozen
threshold: the operative cut **in observed-coverage units** was then a
function of V, which is data — `c ≥ 0.92` at V = 50, `c ≥ 0.933` at V = 45,
`c ≥ 0.95` at V = 40 — so the registered 0.90 was inert and the boundary
moved as pipeline-invalid runs accumulated. A bound already carries the
sample size. One cut on the bound is fixed before the batch in the unit it
is stated in, and that is the whole rule.

**One escalation, on distinct evidence.** If `s_i ≥ 0.20` (S2), class i
escalates exactly one step (LIGHT → STANDARD → FULL; FULL is terminal).
Reaching a class with the wrong label is worse than not reaching it: an
absent expectation is a gap, a wrong one is an assertion.

**The pipeline-invalid rate escalates nothing.** If `rho ≥ 0.10` (S8),
`ANALYSIS.md` and `RATES.md` carry a **stated caution over the whole
batch** — this authoring pipeline failed often enough that every rate is
read under it — and no class's tier changes. The earlier draft escalated
every class on `rho`, which charged one event twice: pipeline-invalid runs
leave the denominator, so they have *already* shrunk V and widened every
interval, and `L_i` has already fallen for it. The caution is the honest
place to put the remaining information.

**What this mapping can and cannot resolve at N = 50.** Registered here,
computed exactly with this study's own interval code and asserted by a
harness test, so the mapping's power is not left to a reader's intuition.
At V = 50 the LIGHT cut is reached first at **k = 46** (`L = 0.8077`;
k = 45 gives `L = 0.7819`), i.e. at an observed 0.92, and the STANDARD cut
at **k = 28** (`L = 0.4125`; k = 27 gives `L = 0.3932`), i.e. at 0.56.
Given a class whose *true* coverage is p, the probability this mapping
calls it LIGHT is:

| true p | P(tier = LIGHT) at V = 50 |
| --- | --- |
| 0.85 | 0.1121 |
| 0.90 | 0.4312 |
| 0.95 | 0.8964 |
| 0.99 | 0.9999 |

Plainly: **at N = 50 this mapping is coarse.** A class that genuinely
reaches its boundary nine runs in ten is called LIGHT less than half the
time, and a conservative exact bound is why. The operator fixed N = 50 with
that limitation stated — the batch is quota-bound, and the shortfall rule
covers a short one — so the study reports the tiers this cut produces and
does not move the cut afterwards. Anyone who needs a LIGHT/STANDARD
boundary resolved near p = 0.90 needs a larger N, and that is a different
study.

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

**C1 — ported bytes match 010's lock.** The name of this control is a claim
about *010's lock*, so the check is ordered to make it one. `harness/PORTS.md`
is an editable file in **this** study: a table checked only against itself
authenticates whatever its editor wrote, and changing one byte of
`policy_mirror.py` together with that row's two digit cells would move every
`c_i` and every §5 tier with nothing refusing. `harness/integrity.py`
therefore, in this order:

1. verifies `../010-blinded-oracle/PROTOCOL-LOCK.json` against the digest
   `harness/PINS.json` pins for it, `4966aa82…` — first, because everything
   below reads that file, and because 010's lock does not digest itself;
2. reads that lock's `lockedInputs` map and requires every source
   `harness/PORTS.md` names to be locked in it;
3. for every row, requires **both** the source file in
   `studies/010-blinded-oracle/` **and** the source digest `PORTS.md` records
   to equal the digest **the lock** records. The source column answers to
   010's lock, never to the row it sits in;
4. requires every destination file here to equal the digest `PORTS.md`
   records — `PORTS.md` is this study's change list, and an adapted port has
   nothing older to be checked against;
5. requires the three **byte-identical** ports of §2.1 to equal 010's *locked*
   digest as well, so "byte-identical" is a checked relation between this
   study's file and 010's lock rather than a claim in a prose column;
6. requires the table to name exactly the six ported files, so a deleted row
   is a refusal rather than a check silently dropped;
7. re-checks the prompt, probe prompt and family against `harness/PINS.json`,
   and the running interpreter against its `python` member (§2.6).

Any mismatch refuses. It runs in CI (the Study 011 job in
`.github/workflows/ci.yml`) **and as a precondition of the batch and the
scorer**: `batch.preflight()` calls it before it creates a slot and
`score_rates.score()` before it reads one. That is the check that closes the
gap C1–C7 otherwise left wide open — an uncommitted one-line edit to
`policy_mirror.verdict` after CI last ran would move every rate, and nothing
at run time would notice.

What C1 does **not** do, stated so §7 cannot claim it: it compares no file
to a git `HEAD` blob — this study has no lock-commit machinery — and
`harness/PORTS.md` is itself unpinned. What rests on `PORTS.md` alone is now
exactly one thing: the **destination** digests of the three **adapted** ports,
whose bytes are this study's own and have no older authority. Those rest on
review, on the enumerated change list in §2.3 and `PORTS.md`, and on C3, which
runs the adapted compiler and the mirror over 010's retained completion and
requires 010's published profile back.

**C2 — family/pack coherence.** Two clauses, both of them 010's, and both
needing only the pack bytes and the patch:

1. every `FAMILY.json` mutation's `patch` preimage must be present,
   byte-exact, at its JSON pointer in Study 010's pack C (read in place at
   the pinned digest, §2.1), and the six `index` members must be contiguous
   0–5;
2. every mutation, applied to pack C, must **change** it. A patch whose
   result equals pack C plants nothing, and a class named after a defect
   that does not exist measures nothing. 010 ran this clause inside its lock
   gate; an earlier draft of this study dropped it, and it is restored here.

This is the family-applies check reproduced **without an evaluator**: this
study applies no patch in anger and produces no pack D. What it bounds is
honest and limited — it bounds what a *patch* can mean. A class in this
study is a `predicate`, and no pack-side check constrains the predicate;
that is C3's and C4's job.

**C3 — replication control against Study 010's published profile.** The
ported compiler, the ported mirror, and this study's class arithmetic are
run over 010's retained `completion.txt` (digest pinned in §2.1) and must
reproduce 010's published table exactly:

```
accepted = 16, |H| = 16, |Q| = 0
H ∩ class counts = (2, 2, 2, 4, 1, 1)
Q ∩ class counts = (0, 0, 0, 0, 0, 0)
```

These are the values `../010-blinded-oracle/ANALYSIS.md` published. The
test refuses on any difference. It is the check that this study's
**counting** code — compiler, mirror, class arithmetic — means the same
thing its predecessor's did, on the bytes 010 actually retained.

Its scope is exactly that, and no more: C3 does **not** exercise
`transcript_check.py` or `authoring_call.sh`. The transcript binding is
exercised by the admission tests (tool-use payloads, a turn after the
registered prompt, a paraphrased pre-prompt context, duplicate keys) and,
on real bytes from this environment, by §3.2's golden procedure, which runs
the ported checker's normalization and comparison over two real captures
before the batch. The wrapper is exercised by the wrapper-driven harness
tests, which run the real `bash`, the real `env -i`, and the real slot
retention against a stand-in CLI. The registered prompt's own transcript
shape first meets the ported gate on batch slot 1, and that is a stated
consequence of §3.2's probe-prompt choice, not an oversight: running the
registered prompt before the batch would show the operator a coverage
profile first.

**C4 — synthetic fixture with a known coverage profile.** In
`harness/tests/fixtures.py`, hand-authored completions committed as
Python constants whose expected output — accepted ids, drop codes, H/Q
membership, and per-class coverage — is registered in the same committed
module (`PROFILE_A`, `PROFILE_B`, `DROP_HISTOGRAM`), with the replication
expectation additionally pinned in `harness/PINS.json`. The §4.3 interval
vectors are registered in `harness/tests/test_intervals.py` (`REGISTERED`)
and the end-to-end rate, interval and tier expectations over a whole
stand-in batch in `harness/tests/test_batch.py`; all three files are
committed, and this sentence names where each lives rather than claiming
they share one module. CI runs compiler → classifier → scorer over them and
requires equality. The fixtures are constructed to make a silent miscount
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
admission check requires — every clause below is a `isolation-unproven`
refusal in `score_rates.admit()`, not a description of what the wrapper
writes. (An earlier draft checked four booleans, a non-empty home and the
inventory, and nothing else: a slot with every environment member deleted and
`credentialRemoved` false stayed admitted while this list claimed otherwise.
The clauses are checks on the wrapper's own record — §7 says plainly that
`CALL.json` is self-reported — but a record that contradicts the registered
invocation is not evidence of it, and that much is checkable):

- `isolation: isolated` — the C7 control's mode never enters a denominator;
- the resolved isolated `HOME`, and a `CODEX_HOME` that is that home's own
  `.codex`. "Resolved" is checked as far as a recorded string can be: absolute
  and already in normal form, so a relative path, a `..`, or a doubled
  separator refuses rather than giving one directory two names the clauses
  below would fail to relate;
- a working directory, likewise resolved, that is neither the isolated home
  itself nor inside it nor a parent of it: the model's workspace is not the
  home it was given. (`cwd == home` is stated because it was the case the
  nesting test missed — it tested strict descent in both directions and a
  directory is not a strict descendant of itself.);
- the environment's names being exactly `PATH`, `HOME`, `TMPDIR`,
  `CODEX_HOME`, and its **values** being one non-empty string each, with
  `HOME` and `CODEX_HOME` agreeing with the paths the same record reports;
- a child `PATH` of exactly the six registered system directories plus one
  per-run binary directory, which must be absolute and **outside the isolated
  home** — the defect §2.2 records in 010's wrapper, whose "scrubbed" child
  `PATH` ended in the operator's real home, is a refusal here;
- a `TMPDIR` inside that run's own working directory and not `/tmp`;
- `stdin` recorded closed;
- `credentialRemoved` exactly when `credentialCopied`: a copy made and not
  removed is a live credential left on disk, and a removal recorded without a
  copy is a record of nothing;
- the **recursive pre-call inventory** of the isolated home — every path
  beneath it, relative and sorted — which must be exactly
  `['.codex', '.codex/auth.json']` when a credential was copied and exactly
  `['.codex']` when there was none to copy. Both branches carry
  information, and a `config.toml`, an `AGENTS.md`, or a skills tree
  anywhere in the isolated home refuses the run. (An earlier draft counted
  only the *top-level* entries after creating `.codex`, which is the
  constant 1 in every case: it could see neither the credential nor
  pollution, and on a machine with no operator credential it made every
  slot `isolation-unproven`. The recursive list is what makes this evidence
  rather than a tautology, and the harness tests exercise both branches and
  four polluted ones.);
- the **new-session set**, which must contain exactly one `*.jsonl` created
  by this call — recorded and required as the **integer** 1, since Python
  considers `True == 1` and a slot recording `newSessionCount: true` was
  recording nothing counted;
- the scratch path, screened for leak tokens and required to resolve
  outside every git worktree;
- `context.json`, whose digests must equal the registered golden.

The golden match is the operative evidence: a leaked skill, config, or
`AGENTS.md` changes the pre-prompt context, and any change refuses.

**C7 — the isolation gate's power, demonstrated not assumed.** Before the
batch, one capture is run **deliberately without isolation**:

```sh
"$PY" harness/batch.py capture-isolation-negative --scratch-parent DIR
```

which makes ONE call with the operator's real `HOME` and its `.codex` as
`CODEX_HOME`, everything else as registered, using the probe prompt (never
the registered prompt). The registered expectation: it **fails** the golden
match. Registering the outcomes before the batch is what keeps this a control
rather than a decision, and there are **three** of them, because a call can
fail to produce anything comparable:

| outcome | meaning | exit |
| --- | --- | --- |
| `refused` | the golden match failed — the registered expectation | 0 |
| `matched` | the non-isolated call reproduced the golden context: the gate has no demonstrated power against home leakage here. Recorded in `ANALYSIS.md` as a stated limitation; the batch proceeds unchanged | 0 |
| `no-context` | the call produced no comparable context at all, so neither comparison happened and the gate's power is undemonstrated | **non-zero** |

`no-context` exits non-zero deliberately: a control that did not run is not a
step that was done, and an earlier draft returned success for it. Its verdict
is still retained, so the failure is on disk rather than only in a shell's
exit status, and `ANALYSIS.md` reports the gate's power as undemonstrated.

Three things make it executable as written rather than only registered:
the wrapper takes `ISOLATION=operator-home` (§2.3 item 10), so no
digest-pinned file has to be edited to run it; the run's session is
identified by difference (§2.3 item 9), so the operator's real `.codex` —
which on this machine holds hundreds of transcripts — does not refuse the
control on a session count *before* the comparison it exists to make; and
the comparison itself is ordered so that its verdict is the recorded
outcome.

**Retention is done by code, not by care.** `controls/isolation-negative/`
receives `VERDICT.json` (the outcome, the refusal message, the golden digest,
and the digests of everything deleted) and a `CALL.json` **stripped** of every
member that names or enumerates the operator's environment — `home`,
`codexHome`, `cwd`, `environment`, `environmentValues`,
`isolatedHomeInventory`, `operatorHomeSkillsPresent` — with the stripped list
recorded; **and `context.json` (the digests) whenever the call produced a
comparable context**, which is to say in both outcomes that reach a
comparison. So: three files under `refused` and `matched`, two under
`no-context`, and the outcome member says which. (The earlier "exactly three
files" was false in the third case, which is the sort of sentence that is
easier to correct than to be right about by luck.)

The call is made into a scratch directory outside the study; `session.jsonl`,
`stdout.raw` and `stderr.raw` are digested and **deleted by the driver**, and
the scratch slot is removed — and the removal is **verified**, not attempted.
If the slot survives, the control refuses and names the path, because
"deleted by the driver" is a claim about the disk and an ignore-errors removal
would make it a claim about the call that was made. A harness test inspects
every retained byte and fails on any path into the stand-in operator home, any
skill name, or the credential; another requires the refusal when the removal
does not take.

**Operator assent: granted**, recorded in `harness/PINS.json`
(`isolationNegative.operatorAssent`), and `batch.py
capture-isolation-negative` refuses unless it says so. This is the one
registered step that deliberately exposes the operator's real environment
to the pinned CLI, which is why assent is a recorded precondition rather
than an understanding. Had it been withheld, that would have been recorded
in `DEVIATIONS.md`, the control skipped, and the gate's power recorded in
`ANALYSIS.md` as undemonstrated — the batch is unaffected either way.

## 7. What is enforced, what is recorded, what is not prevented

Scoped to *this* design. This study has **no publication ordering, no
transparency log, and no beacon**, and needs none: 010 required them
because one unrepeatable sample had to be shown unsteerable against a
future event. Here there is no draw and no prediction — the endpoint is a
rate over slots that anyone with the pinned binary can re-run. So this
section is about isolation, ledger discipline, and exactly what a
re-runner can and cannot check.

**Mechanically enforced** (a violation refuses, or the run is scored
pipeline-invalid). Every item below names code that runs in the batch, in
the scorer, or in both — nothing here is a description of intent:

- the ported-byte digest table with every **source** bound to Study 010's own
  `PROTOCOL-LOCK.json` (itself pinned) and the three byte-identical ports bound
  to it on the destination side too, checked by `harness/integrity.py` before
  the driver creates a slot and before the scorer reads one (C1);
- the codex binary digest and the CLI version string, both **before the call**,
  and the model name;
- the registered interpreter (implementation and version series), refused by
  the wrapper before it calls anything and by the batch and the scorer before
  they run (§2.6);
- the registry of record, per run AND per population. Per run: every run
  records the sha256 of the registry it was made under, the scorer computes the
  committed `harness/PINS.json`'s digest itself, and any other run is
  `registry-mismatch` (§2.6). Per population: **the registered scoring
  interface is `score_rates.score_registered()`, which the `score_rates.py
  score` command calls and nothing else does, and it takes the slot directory
  and an optional record-emission directory and nothing else.** The registry,
  the family, the prompt, the golden capture and the study root the tables are
  written to are all derived from the harness's own location; the command's
  argument parser accepts `--slots` and `--emit-records` and **refuses every
  other argument** rather than ignoring it, since a silently dropped flag is
  how a stale command line lies about what it ran; and the scorer reads no
  environment at all, with a harness test asserting that of its source. That
  second half is what closes a registry identical to the committed one except
  for `batch.runs`, which redefined N — and therefore every denominator — while
  each slot's stamp still matched.
- the publication boundary itself: `_write_outputs()` is **module-private, has
  no output-directory parameter, and is called only by `score_registered()`, on
  the results it computed in the same call**, so no results dict crosses a
  public boundary into publication — there is no public writer to hand one to.
  The `registry_sha256` override on `score()`, `score_run()` and `admit()` is
  for library callers whose slots were made under a stand-in registry (the
  wrapper-driven tests); `score()` records it in `cell.registryOverride`, and
  the writer refuses results carrying one. It does not stop there, because
  trusting one mutable member of an ordinary dict is what the previous draft
  did: the writer re-derives the committed registry's digest, the registered N,
  and the prompt, family, golden, preregistration, model, CLI and binary pins
  from the study tree, and refuses unless the results agree with every one. So
  a results dict edited to hide its override is still refused, on what the tree
  says rather than on what the dict says. What none of that covers, stated here
  rather than left implied: a caller who edits `score_rates.py` or rebinds its
  module constants in process. No check inside a file defends that file, this
  study's own harness is not digest-pinned (only the six ported files are, C1),
  and the ceiling is the one the "deliberately not claimed" paragraph below
  states — re-runnability, not proof. That ceiling is stated once, here;
- a slot tree of regular files and directories only, decided by `lstat` before
  anything in the tree is opened: any symlink in a slot, dangling or not, under
  any name, scores that slot `slot-symlink`, and any FIFO, socket, device or
  other non-regular entry scores it `slot-irregular` — both pipeline-invalid,
  both before any other check, and both before the batch's own `REFUSAL.json`
  is read (§3.3). A FIFO is checked by type rather than opened because `open()`
  on one does not return;
- `--emit-records DIR` disjoint from the slot tree — not equal to it, not
  inside it, not containing it — checked before anything is scored or written,
  so emitting the derived record trees cannot add a slot to the population that
  was just published (§8);
- the recapture derived from at least two **distinct sessions**, checked on the
  raw retained evidence — transcript bytes, session id, and the call record's
  own clock, working directory and home — so a copied capture slot or a
  transcript retained twice refuses the derivation instead of agreeing with
  itself; from **probe** calls at the pinned probe-prompt digest, checked per
  capture slot rather than inferred from the directory's name; and under the
  same ported-bytes, interpreter and freeze preflight the calls run, in
  `capture-golden` and `shortfall` as well as in `capture` and `run`, so no
  step that feeds the published arithmetic can be taken under an unregistered
  interpreter or against an unfrozen preregistration (§3.2, §2.4);
- the preregistration's freeze digest as a precondition of the **calls** as
  well as the scoring, and refused while it is null rather than skipped;
- the per-run fresh `HOME`/`CODEX_HOME`; the `env -i` scrub with a `PATH`
  and `TMPDIR` constructed rather than inherited; the exclusive
  leak-token-free scratch outside every worktree; closed stdin;
- C6's recursive isolated-home inventory, in both the credential and
  no-credential branches; C6's environment clauses one by one — the
  `CODEX_HOME` under the isolated home, the un-nested working directory, the
  four environment names and their values, the six-system-directory `PATH`
  with its per-run binary directory outside the home, the per-run `TMPDIR`,
  closed stdin, and `credentialRemoved` exactly when `credentialCopied`; and
  the exactly-one-**new**-session requirement;
- the transcript whitelist, terminal-prompt rule, leak denylist, model/cwd
  binding — **every** `turn_context` that names a model or a working directory
  must name this call's, not merely one of them — integer exit 0, and
  completion byte-binding (§3.1);
- the golden context match on every slot; the recapture required to agree
  across at least two captures from distinct sessions, enforced both before
  the calls and at the derivation; **and the golden capture bound to its pin and to
  every run** — the driver refuses to create any slot while
  `PINS.golden.sha256` is null or does not match the file at the golden
  path, the scorer refuses on the same conditions, every slot records the
  capture digest its batch verified, and a slot naming any other capture is
  `golden-mismatch`. So a capture derived after the batch — including one
  derived from the batch's own slots, which `capture-golden` refuses outright
  — cannot re-admit a run;
- compiler regeneration with byte equality and the exact file set;
- slot exclusivity (a slot directory is created once and never re-run),
  contiguous slot indices, and a ledger that a resumed run merges into and
  refuses to overwrite;
- the §3.3 valid/invalid partition and the population filter, both in code
  (C5), with the registered code table diffed against the code by a test;
- the equality of the six denominators, asserted by the scorer (§4.2);
- the scorer's totality — every per-slot artifact it reads, `REFUSAL.json`
  included, is read inside the total path and through the duplicate-key
  loader, so a malformed, truncated, wrong-typed or codeless one yields that
  slot's own pipeline-invalid verdict and never a bare exception that would
  stop the scoring of every other slot. (A **missing** `REFUSAL.json` is not in
  that list and is not a refusal: absence means the batch did not refuse the
  slot, exactly as §3.3 says.) (§3.3);
- the batch/score separation: the driver cannot compute coverage; the
  scorer refuses unless the batch is terminal (exactly N slots XOR a
  matching shortfall declaration, never both, never over-full); the driver
  refuses new slots once `RESULTS.json` exists; the registered scoring command
  is the only publisher and can write a rate table nowhere but the study root;
  and a planned slot that already exists — including one that exists only as a
  **dangling symlink**, which an existence test calls absent and `mkdir` calls
  present — refuses the batch through that registered path instead of ending it
  in an uncaught exception;
- `batch.py capture-isolation-negative` refuses without recorded operator
  assent; its retention set is built by code rather than by care, and it
  verifies that the scratch slot it deleted is gone rather than ignoring the
  errors of the attempt (C7).

**Deliberately not claimed.** This study has **no lock-commit machinery**,
by design: nothing here compares a worktree file to its `HEAD` blob, and no
pinned input is required to equal a committed blob. An earlier draft
claimed that and had no implementation. What this study's integrity rests
on instead is the digest table above (whose source side and byte-identical
destinations are bound to Study 010's own locked values, checked at run
time), ledger discipline (every slot published, invalid ones included, with
the batch ledger merged not overwritten), and re-runnability: anyone with the
pinned binary can run the registered call again and check the rates.
`harness/PORTS.md` is itself unpinned, and what rests on it alone is exactly
the destination digests of the three **adapted** ports — bytes that are this
study's own and have no older authority to answer to (C1).

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
slot index is refused by exclusive creation, and a batch resumed after a
crash (`--start K`) merges into the append-only ledger rather than
replacing it, refusing any slot the ledger already records — so the record
of what was attempted survives the interruption that made a resume
necessary.

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
not controlled (§2.1); **that the operator did not read a `completion.txt`
by eye during the batch** — the artifacts make it possible, the design
forbids computing rates rather than reading files, and no mechanism here
can close it; and, following from that, **that a declared shortfall was
involuntary** — `batch.py shortfall` checks that the batch is genuinely
short and that no rate has been published, and it cannot check why the
operator stopped. §2.4 states both plainly and `PINS.json`'s batch note
claims only the mechanical guards.

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
- **A credential copy surviving a `SIGKILL` or a power loss.** The wrapper
  removes its copy on the seal path and on `EXIT`, `INT`, `TERM` and `HUP`;
  no process can handle `SIGKILL`, and none survives a power cut. The residual
  is one file under the operator's own scratch parent, and §2.5 states it and
  the manual remedy rather than claiming the copy dies "however the wrapper
  dies", which the earlier draft did and which a `SIGKILL` disproved.
- **Per-run isolation limits.** A fresh `HOME` and `CODEX_HOME` close the
  paths 010 found empirically (user config, `AGENTS.md`, `~/.agents`
  skills). They do not close provider-side state: if the pinned CLI's
  backend carries any cross-session memory keyed to the credential, the 50
  runs are not independent in the way this study assumes, and neither the
  transcript nor the context digests would show it. C6 and C7 demonstrate
  *local* isolation only. S6 (distinct outputs) is the one observable that
  would hint at correlation, which is why it is reported before the rates
  when it is non-trivial.
- **What `/tmp` still exposes.** The pinned CLI's sandbox is writable at
  `[workdir, /tmp, $TMPDIR]`. This study gives each run its own `workdir`
  and its own `TMPDIR` inside that workdir, so no run's `TMPDIR` is another
  run's, but `/tmp` itself remains in the writable set on this platform and
  the CLI offers no flag to remove it. If the operator's scratch parent is
  under `/tmp` — the layout Study 010 used — then every other run's scratch
  tree, and every run's isolated home, is *reachable* from inside a run's
  sandbox. Three things bound what that can mean and none of them removes
  it: the transcript whitelist refuses any run that used a tool at all, so
  a run that actually reached another run's tree cannot enter a
  denominator; the credential copy is deleted when each slot is sealed, so
  what is reachable is a spent scratch tree rather than a live credential;
  and the recommended scratch parent is outside `/tmp`. The residual is
  real and is stated here rather than in a footnote — and note the cost it
  imposes even when it does not bite: a run refused as `transcript-refused`
  leaves the denominator, so the rates are conditional on the author having
  happened not to use a tool.
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

**Publication commitment.** Everything is published regardless of outcome.
Stated as what is *retained*, not as a file list every slot is promised to
have, because a slot cannot publish an artifact its run never produced and an
earlier draft promised one that could not exist:

- all 50 raw slot directories (or S under the shortfall rule), **including
  every invalid one**, with every byte the run left in them and nothing
  removed. For a run that reached the call that is `CALL.json`,
  `session.jsonl`, `stdout.raw`, `stderr.raw`, `context.json` and — on exit 0 —
  `completion.txt`; a wrapper pre-flight refusal reached no call and leaves
  `REFUSAL.json` alone (§2.5), and a run that failed mid-way leaves whatever it
  got to plus its `REFUSAL.json`. Nothing in the tree is `.gitignore`d: the
  repository ignores `__pycache__/` and `.pytest_cache/` and nothing else;
- the per-run admission verdict, refusal code, counts and class classification
  the scorer derives from those bytes, for **every** slot, in `RESULTS.json`'s
  `runs` array — that part is promised for all of them, because it is derived
  and not retained;
- the compiled `records/` and `RECORDS.md` for the valid runs whose completion
  held a parseable JSON array, emitted by `score_rates.py score
  --emit-records DIR` into a directory outside the slot tree. A run with no
  parseable array has no compiled tree — that is what `authoring-empty` means
  (§3.3) — and an invalid run's completion is not compiled at all. Every slot's
  `completion.txt` is published either way, so any reader can run the compiler
  over it themselves;
- every recapture attempt's captures, under `controls/recapture/attempt-N/`,
  and the C7 negative control's retained files (verdict and stripped call
  record always, context digests when the call produced them, per §6 C7 — the
  transcript is digested, deleted by the driver, and never published);
- `RESULTS.json` and `RATES.md`, both written by the registered scoring
  command into the study root, with every rate's integers and bounds, and
  `ANALYSIS.md` leading with the six rates and `rho` whatever they are — a class covered
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
of §2.4 are the resolution, and they are denominated in V: **if no run is
pipeline-invalid**, a perfect class is bounded below at 0.9289 and a
half-covered class carries ±0.14; at V = 45 those become 0.9213 and about
±0.15, at V = 40, 0.9119 and ±0.16. So this study can separate "reliably
covered" from "rarely covered" and cannot resolve much finer than that —
and §5 says exactly what that costs its own product decision: a class whose
true coverage is 0.90 is called LIGHT 43% of the time.

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
