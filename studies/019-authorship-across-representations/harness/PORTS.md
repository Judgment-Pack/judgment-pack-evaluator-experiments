# Ports — what Study 019 takes, from where, and what changed

Study 019 runs one authoring call three ways and compares what each
representation's accompanying test suite pins down. The machinery it counts
with is inherited as **bytes**, not as descriptions, through a two-level chain
(PREREGISTRATION.md §7): this file records every port, its digest on both
sides, and exactly what was changed. `harness/integrity.py` machine-reads the
table below and binds each row **to the authority that row actually has**
before any call is made and before anything is scored.

The chain, with every link a pinned digest including both ends:

```
this file                            (pinned in harness/PINS.json at port time)
    -> Study 012's harness/PINS.json     cff265e7…  (pinned in harness/integrity.py and in PINS.json)
       Study 012's harness/PORTS.md      e754a583…  (the digest 012's OWN registry pins for it,
                                                     not one this study chooses)
```

The port was taken at commit

```
commit 019c95be9e86c575878015954dfec17e4f84e683
```

The four files taken from Study 012 answer to **012's own PORTS.md destination
cells**, which is a stronger binding than a commit: 012 published a digest for
each of them and this study's source cells must equal it. The fifth file
(`harness/make_manifest.py`, from Study 014) is bound to that commit and to
nothing older, because Study 014 pins none of its own harness sources —
§7 states what that costs, and cross-vendor review of the diff is what covers
it.

**This is a PARTIAL port and the table says so per row.** Two destinations
carry a subset of their source's bytes, named here and enumerated in
`harness/SCAFFOLD.md`, because this gate's brief was a correct testable core
rather than a complete driver. A partial row is not a licence to defer
silently: every deferred piece is listed in SCAFFOLD.md by name and by source
line range, and the freeze cannot happen while any of them is open.

## The table

| source | source sha256 | destination (in this study) | destination sha256 | changed |
|---|---|---|---|---|
| `transcription/authoring_call.sh` | `d8877f3d78af54a7c43b8c53571b76ac4e0d540048f57ddcdaa7826f3c6b3fee` | `harness/authoring_call.sh` | `164a75df05446fc9e94659838e6ed4bf3bf2df9c2caf67b14f64d9d6dbd67256` | **complete port, four registered differences.** (1) three arms A/B/C and `s019-…` scratch, home and per-run binary names; (2) the **registered per-call timeout ceiling**: `timeout --signal=TERM --kill-after=<grace> <ceiling>` is the outermost thing the scrubbed environment runs, the ceiling and the grace are read from `harness/PINS.json` (`batch.callTimeoutSeconds`, `batch.timeoutKillAfterSeconds`) and validated **before** the call, `CALL.json` gains `timeoutSeconds`, `timeoutKillAfterSeconds` and `timedOut`, and a ceiling hit exits **12** — its own status, and its branch is the FIRST of the three refusal branches, ahead of the session-count one as well as the generic nonzero one, because a call terminated at the ceiling frequently produces no session at all and 012's ordering would have filed exactly those runs as `slot-shape`: both codes are APPARATUS, so no denominator moves, but the registered per-arm timeout rate is what a control gate reads and undercounting it would let a batch pass a cap it breached (verified against a stand-in study and a stand-in CLI: exit 12, `timedOut: true`, the ceiling and the grace stamped); (3) a **null registry model refuses**: the model is named by explicit flag at batch time and is null in the registry until then, and a null member reaches the shell as the string `None`, which `-m` would accept as a model name; (4) the wrapper lives in `harness/` rather than `transcription/` — `$STUDY` is the parent of the script's own directory, the same expression at either location, so the anchor and every guard built on it are unchanged. The prompt-digest gate is **carried, not new**: per arm, read from `arms.<ARM>.promptSha256`, refusing an unregistered arm id and another arm's bytes; only the accepted id set changes. Everything else is 012's byte-for-byte, including the resolve-before-create descent, the slot-path equality guard, the credential traps and the worktree repair |
| `harness/batch.py` | `6ee3bf3e2b217257fe38976df4610461c9ed9866db485678348b3ad8036fdcf3` | `harness/batch.py` | `9c9122f54a51f2decf70d60e6a1ebcb2d0c96dbc872626c6f5a2d9598ad5e36e` | **PARTIAL — the schedule core and the code partition only.** Carried and edited: the registered-call-order constants (012 lines 341–375) and `williams()`/`schedule()`/`schedule_entries()`/`slot_path()` (012 lines 515–616). Changed: `ARMS = ("A","B","C")`, so `POSITIONS` 3, `SEQUENCES` 6, `RUNS_PER_ARM` 50, `REGISTERED_SLOTS` 150, all derived and none transcribed; **the schedule re-derived for three arms** as eight whole blocks of the six Williams sequences plus a registered two-sequence tail (50 rounds, because 50 is not a multiple of 6), with `derive_order()` performing the exhaustive 720 × 30 search that establishes the registered order attains the arithmetic FLOOR of both spreads — exact balance being unavailable at 3 arms over 50 rounds — and `schedule()` refusing an expansion that is not at that floor; `balance()` added as the counters both the search and the harness test read; `CALL_TIMEOUT_SECONDS = 2700` and `TIMEOUT_KILL_AFTER_SECONDS`; `WRAPPER_EXIT_MEANINGS` extended with status 12; and `APPARATUS_CODES`/`AUTHORING_CODES`/`CODE_PARTITION` — §1a's partition as a named constant, built rather than written out so a code on both sides refuses at import. **Not carried:** preflight, the golden recapture, slot creation and sealing, `SLOT-MANIFEST.json`, the chained ledger, resume, shortfall, reconciliation, the isolation negative control, and every `score_rates` dependency — SCAFFOLD.md items D1–D8. The module's own docstring says it is partial, and its `main()` publishes the plan rather than pretending to run one |
| `harness/integrity.py` | `98e11a14f931e47ece6b5c975afe46a18ef784d8824785fab8632083c5014af1` | `harness/integrity.py` | `5ceae5567d3a6e32d3fc51a8eb5c26b8afc93ce1b29ff5b5489f3bcbd1d7a0c1` | **PARTIAL — the chain, the interpreter, the unreviewed-bytes gate, the label rule.** Carried **verbatim** (byte-sliced from the source, not retyped): `IntegrityError`, `digest()`, `_refuse_duplicate_keys()`, `load_json()`, `bare()`, `parse_ports()` and the `ROW` regex (012 lines 169–219); `verify_interpreter()` (1142–1160); `_code_equal()`, `_const_equal()`, `verify_bytecode()` (1163–1346); `_refuse_unsafe_import_path()` (1386–1414) — including its references to Study 012's README steps, which this study's runbook has not been written yet (SCAFFOLD item R5). Rewritten for the one-level chain: `verify_chain()` keeps every idiom of 012's — the unfinished-port placeholder scan — whose token is deliberately not quoted here, because this file is one of the two the scan reads and quoting it refuses the port, as it did once while this row was being written —, the registry's own `pinnedFrom` members checked against review-bound constants, the exact destination set, per-row source and destination digests — and drops the two levels this study does not have; the source-side authority is 012's own PORTS.md destination cell per row, and the one untiered row is bound to the recorded commit. New: `study_label()`, `freeze_pin_state()`, `unfilled_pins()` (the registered label rule, decided in one place) and `verify_manifest()`. **Not carried, deliberately:** the arm-artifact checks (C8), the family schema (C9), the clean-room mirror gate (C10), the 280-cell landmark grid, the policy parser, `sigma`, the census helpers — none of them names anything in this study — and the `[D-20]` whole-tree git manifest, superseded by ADR 0004's exact-set manifest, because carrying both would give one study two manifests that could disagree. Imports dropped with them: `itertools`, `importlib.util` at module scope, `Counter`, `Decimal` |
| `harness/transcript_check.py` | `64542bc5d6d8f6682a29dee870aa07feb5757db3941c48af581a974c2423a5b2` | `harness/transcript_check.py` | `9dd321348b0e1595d7eef620c3155d840f98b4d531d92655fc949185064f586d` | **complete port, no check logic changed.** The `response_item` whitelist, the terminal-prompt rule, the leak denylist mechanism, the golden allowlist comparison, the completion byte binding, the `turn_context` model/cwd binding, the integer-exit-0 rule and duplicate-key rejection are 010's through 011 and 012, unchanged. Two SUBJECTS change: `LEAK_TOKENS` is this study's vocabulary (representations, scored surface, mutant machinery, policy domain) and not 012's policy-family vocabulary; and the arm label is one of A/B/C. The token list is design-time and is marked `GATE(pre-freeze)` in the module docstring and in SCAFFOLD.md item G3: it must be re-derived from the frozen policy prose and the naming appendix, with a committed checker shown to have power on mutated inputs |
| `harness/make_manifest.py` | `660a350ad8a647a2df9fea443af273c8c20480bd276c5a74336e345a86cadb81` | `harness/make_manifest.py` | `3cfd52dea764a2aa196fa1f867cdf9e696e40cc0af13dbbf627129c123f86e34` | **complete port, ADR 0004 applied.** From Study **014** (no lock, no pin: bound to the recorded commit alone). `REGISTERED_DOCUMENTS` is this study's registered set; `EXCLUDED_DOCUMENTS` gains **`DEVIATIONS.md` and `README.md`** — ADR 0004's named exclusions, excluded by construction and asserted by `harness/tests/test_manifest.py` **while both files exist**, so the assertion has power rather than guarding an absent path — and keeps 014's `harness/PINS.json` linear-anchor exclusion; `EXCLUDED_ARTIFACTS` names the manifest itself; the covered set adds `harness/*.sh` and `harness/PORTS.md`; and `pending_documents()` plus a `--freeze` flag are new, because several registered documents do not exist yet pre-freeze and a set discovered by globbing at freeze time is not a registered set — `--freeze` refuses while any is pending. 014's `EXCLUDED_FIXTURE_ROOTS` and its `fixtures/` and `adapter/` globs are dropped: this study has neither tree |

**This table is machine-read, and its columns answer to different
authorities.** This file is editable in *this* study, so it cannot be the
authority for what the inherited bytes were. `harness/integrity.py` therefore,
in order: verifies Study 012's `harness/PINS.json` against the digest it pins
for it; verifies Study 012's `harness/PORTS.md` against the digest **012's own
registry** records under `ownPorts`; verifies **this file** against the digest
`harness/PINS.json` records for it, so the change list cannot be rewritten
after the review; and then binds each row — the four Study 012 rows to 012's
own destination cells on the source side and to this table on the destination
side, the Study 014 row to the recorded commit's working file. It also requires
the destination set to be exactly the five files above, so a deleted row
refuses rather than quietly dropping a check.

## The schedule, and why it is a floor rather than a balance

Study 012's 150 slots were 30 rounds of five arms, and its registered order was
*exactly* balanced: every arm in every within-round position exactly six times,
every ordered pair adjacent exactly six times within rounds. None of that
survives three arms:

* 50 slots per arm over 3 within-round positions is 16⅔ — no integer;
* 149 directed transitions over 6 ordered pairs is 24⅚ — no integer;
* 50 rounds is not a multiple of the 6 Williams sequences, so the batch cannot
  be whole blocks of the table.

What is registered instead is the **arithmetic floor of both spreads**, and it
is established rather than asserted. `derive_order()` enumerates all 720
orderings of W1…W6 against all 30 ordered two-sequence tails, discards every
order in which an arm immediately follows itself, and returns the
lexicographically-least of those minimizing (position spread, transition
spread). The answer is

```
block order  W1 W2 W3 W4 W6 W5   (eight times, rounds 1-48)
tail         W4 W6                (rounds 49-50)
spreads      position 1, transition 1 — the floor
```

and `harness/tests/test_schedule.py` asserts that the registered constants ARE
that answer. If a better order existed the search would find it and the test
would fail, rather than a worse order passing under an adjective. The published
properties, all re-derived by the test from the expansion's own counters:

| property | registered value |
|---|---|
| slots per arm | 50, all three equal |
| position counts | every (arm, position) cell 16 or 17; each arm 17, 17, 16 |
| self-successions | 0 — no arm ever immediately follows itself |
| within-round directed transitions | 100 |
| round-boundary transitions | 49 |
| total directed transitions | 149; five ordered pairs 25 times, one 24 — spread 1 |

## The timeout ceiling, and which side of §1a it is on

Study 012 registered no per-call ceiling and its wrapper ran unbounded. This
study registers **2700 s** (PREREGISTRATION.md §2 "Batch shape"), and three
files have to agree about it or the study has three ceilings: the registry
carries the number, the wrapper reads it from the registry and enforces it, and
the driver classifies on its own constant. `harness/tests/test_schedule.py`
asserts the registry's two values equal `batch.py`'s two constants.

Its SIDE is the load-bearing part. A timeout is an **apparatus** failure:
pipeline-invalid, excluded from every rate's denominator, reported with its own
rate and interval, and a per-arm timeout rate above the registered cap is a
control-gate failure adjudicating R1 in neither direction. §1a records why this
is registered in code rather than left to the driver — the design-phase pilot
driver mis-filed timeouts as an authoring code, which silently moves a run out
of the excluded set and into the denominator of every rate.
`harness/tests/test_partition.py` asserts the side against §1a's own list, and
asserts that no wrapper exit status maps to an authoring code.

One residual, stated rather than hidden: `timeout` returns 124 when TERM
sufficed and 137 (128+9) when the KILL was needed, and a 137 produced by
something else — an OOM kill, say — would be recorded here as a ceiling hit.
That misreading costs a code and never a denominator, because a nonzero exit is
an apparatus failure too.

## What was NOT ported, and why

Everything Study 012 built for a policy-perturbation design: the five arms'
`POLICY.md`/`FAMILY.json`/`ARM.json` artifacts and their assembler, the single
registered mirror and its clean-room second mirrors, the landmark grid, the
census over mutation classes, the records compiler, `score_rates.py` entire.
This study's stimulus is a contest policy in three representations, its oracle
is a gold suite plus two reference implementations, and its endpoint is what an
authored test suite kills — none of that machinery names anything here.

Also not ported: Study 012's `harness/tests/` — its fixtures are about arms,
policies and mirrors. This study's suite is new, and small on purpose.

## New here, not ported

`harness/PINS.json`, `harness/PORTS.md`, `harness/SCAFFOLD.md`,
`harness/STUDY-MANIFEST.sha256` and `harness/tests/` (four modules:
`test_schedule.py`, `test_manifest.py`, `test_pins.py`, `test_partition.py`).
`harness/score.py`, the per-language admission layer, the two-engine execution
layer, the alignment map and the mutant/kill machinery are **not written yet**
and are assembled from the design prototypes — SCAFFOLD.md items S1–S6.
