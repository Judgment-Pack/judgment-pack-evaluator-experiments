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

The **six** files taken from Study 012 answer to **012's own PORTS.md
destination cells**, which is a stronger binding than a commit: 012 published a
digest for each of them and this study's source cells must equal it. The
seventh file (`harness/make_manifest.py`, from Study 014) is bound to that
commit and to nothing older, because Study 014 pins none of its own harness
sources — §7 states what that costs, and cross-vendor review of the diff is what
covers it.

**This is a PARTIAL port and the table says so per row.** Destinations that
carry a subset of their source's bytes say so in their own cell, and every
deferred piece is listed in `harness/SCAFFOLD.md` by name and by source line
range: a partial row is not a licence to defer silently, and the freeze cannot
happen while any of them is open. `harness/batch.py` is no longer one of them —
SCAFFOLD items D1–D8 and G1–G2 have landed and its cell enumerates them.

**One row can carry more than one source, and this table says where and why.**
`harness/integrity.py`'s `REQUIRED_PORTS` fixes the destination set at exactly
the five files it names (it must grow to the seven this table now carries —
SCAFFOLD item M1), and `verify_chain()` resolves a row's source-side
authority *by its destination* — so a second row naming `harness/batch.py` as
its destination refuses, whatever it names as its source. Four functions Study
012 kept in `harness/score_rates.py` are nevertheless carried into
`harness/batch.py` (`C7_OUTCOMES`, `session_identity()`, `collect_slots()`,
`c7_record_shape_problems()`), because each is a precondition of the CALLS and
this study's scorer did not exist when the driver needed them. Their
provenance — source path, source digest, and what changed — is therefore
recorded **inside the row that owns the destination** rather than in a row of
its own. That is a real limitation of the table's shape, stated here rather
than worked around silently: a round that wants `harness/score_rates.py` on its
own row has to widen `REQUIRED_PORTS`, which moves `harness/integrity.py`'s own
destination digest and is a change to a reviewed file, not a bookkeeping edit.

**Two authorities, not one.** A row in the table below is a CROSS-STUDY port:
bytes inherited from another study, bound on both sides. Code assembled from
THIS study's own `design/` prototypes is a different thing and gets a different
treatment — the prototype's path and sha256 are cited in the assembled module's
own docstring, and the module says which line ranges it carried. The design
prototypes are this study's working code and were run against the real engines;
they are not another study's published bytes, so a two-sided row would claim an
inheritance that does not exist. The five assembled modules and their
prototypes are listed under "Assembled from this study's design prototypes"
below.

## The table

| source | source sha256 | destination (in this study) | destination sha256 | changed |
|---|---|---|---|---|
| `transcription/authoring_call.sh` | `d8877f3d78af54a7c43b8c53571b76ac4e0d540048f57ddcdaa7826f3c6b3fee` | `harness/authoring_call.sh` | `d5ab1a13d7fe8d0b16b3d0a7c3a8295d9a1b77af3911a23ea789c8eeef7bd739` | **complete port, four registered differences.** (1) three arms A/B/C and `s019-…` scratch, home and per-run binary names; (2) the **registered per-call timeout ceiling**: `timeout --signal=TERM --kill-after=<grace> <ceiling>` is the outermost thing the scrubbed environment runs, the ceiling and the grace are read from `harness/PINS.json` (`batch.callTimeoutSeconds`, `batch.timeoutKillAfterSeconds`) and validated **before** the call, `CALL.json` gains `timeoutSeconds`, `timeoutKillAfterSeconds` and `timedOut`, and a ceiling hit exits **12** — its own status, and its branch is the FIRST of the three refusal branches, ahead of the session-count one as well as the generic nonzero one, because a call terminated at the ceiling frequently produces no session at all and 012's ordering would have filed exactly those runs as `slot-shape`: both codes are APPARATUS, so no denominator moves, but the registered per-arm timeout rate is what a control gate reads and undercounting it would let a batch pass a cap it breached (verified against a stand-in study and a stand-in CLI: exit 12, `timedOut: true`, the ceiling and the grace stamped); (3) a **null registry model refuses**: the model is named by explicit flag at batch time and is null in the registry until then, and a null member reaches the shell as the string `None`, which `-m` would accept as a model name; (4) the wrapper lives in `harness/` rather than `transcription/` — `$STUDY` is the parent of the script's own directory, the same expression at either location, so the anchor and every guard built on it are unchanged. The prompt-digest gate is **carried, not new**: per arm, read from `arms.<ARM>.promptSha256`, refusing an unregistered arm id and another arm's bytes; only the accepted id set changes. Everything else is 012's byte-for-byte, including the resolve-before-create descent, the slot-path equality guard, the credential traps and the worktree repair. **A fifth registered difference (SCAFFOLD G3): the scratch-path leak screen reads `harness/leak_tokens.py`'s `SCRATCH_TOKENS` instead of `transcript_check.LEAK_TOKENS`.** The policy half of that list is DERIVED from the stimulus slice of the frozen-candidate prose by three registered rules — the prose's own bold and backticked terms, its clause ids, and the threshold numerals of comparison sentences together with their spellings — and `leak_tokens.check_power()` requires the derived list to catch every witness sentence the SOURCE'S OWN MARKUP identifies while a scrambled list of the same size catches strictly fewer. What the wrapper screens with is the UNION of the derived policy vocabulary and the design-time INSTRUMENT vocabulary (jpack, the preregistration, the mutant machinery), so the list can only grow and the screen can only tighten; `leak_tokens.check_negative_corpus()` proves no derived token fires on any name this wrapper constructs, over every arm and every registered slot index. The screen's SITE, its refusal text and its exit status are unchanged, and no other line of the file moves |
| `harness/batch.py` | `6ee3bf3e2b217257fe38976df4610461c9ed9866db485678348b3ad8036fdcf3` | `harness/batch.py` | `3c400d433c1f42a1b0d68b198db8670ae3e9f88c117dc41bff91d27824de9421` | **the schedule core, the code partition and the whole calling half.** Carried and edited: the registered-call-order constants (012 lines 341–375) and `williams()`/`schedule()`/`schedule_entries()`/`slot_path()` (012 lines 515–616). Changed: `ARMS = ("A","B","C")`, so `POSITIONS` 3, `SEQUENCES` 6, `RUNS_PER_ARM` 50, `REGISTERED_SLOTS` 150, all derived and none transcribed; **the schedule re-derived for three arms** as eight whole blocks of the six Williams sequences plus a registered two-sequence tail (50 rounds, because 50 is not a multiple of 6), with `derive_order()` performing the exhaustive 720 × 30 search that establishes the registered order attains the arithmetic FLOOR of both spreads — exact balance being unavailable at 3 arms over 50 rounds — and `schedule()` refusing an expansion that is not at that floor; `balance()` added as the counters both the search and the harness test read; `CALL_TIMEOUT_SECONDS = 2700` and `TIMEOUT_KILL_AFTER_SECONDS`; `WRAPPER_EXIT_MEANINGS` extended with status 12; and `APPARATUS_CODES`/`AUTHORING_CODES`/`CODE_PARTITION` — §1a's partition as a named constant, built rather than written out so a code on both sides refuses at import. **The calling half is now carried too** — SCAFFOLD items D1–D8 and G1–G2, ported by copy-and-edit from the 012 line ranges SCAFFOLD names: `check_registry()`/`verify_ported_bytes()` (638–741), `preflight()`/`require_freeze()` (742–870), `invoke()`/`stamp_slot()`/`refuse_slot()` (988–1124), the slot files, `files_digest()` and `seal_slot()` (1125–1284), the ledger records, chain, prefix and `write_ledger()` (1285–1488), `verify_seal_of()`/`slot_outcome()`/`slots_on_disk()`/`reconcile_ledger()` (1489–1719), `run_batch()` (1720–1831), the golden capture (871–910 and 1832–2078), the isolation negative control (911–987 and 2079–2235), and the shortfall surface with `main()` (2236–2507). Changed, beyond the five above: **(6)** `require_freeze()` gates on the REGISTERED LABEL RULE — every freeze pin non-null via `integrity.study_label()` AND the preregistration digest — where 012 read one member, because Study 014's round 3 found a registered run reachable with only the preregistration digest filled; **(7)** the no-new-slots marker is `ATTEMPT_ROOT` (`results/primary-attempt-001`, the root the scorer refuses to overwrite) and not a `RESULTS.json`; **(8)** `WRAPPER_CODES` is DERIVED from `WRAPPER_EXIT_MEANINGS` rather than written out beside it, which is the third branch SCAFFOLD records as owed — status 12 cannot be mapped in one table and missing from the other; **(9)** the atomic-write temporary keeps 012's registered constant path `arms/BATCH.json.partial` and needs NO exclusion entry here, because ADR 0004's exact-set manifest reaches no byte under `arms/` — `tests/test_batch.py` asserts both halves rather than leaving the second to be assumed; **(10)** four functions are carried from Study 012's `harness/score_rates.py` (sha256 `f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336`, 012's own destination digest for it): `C7_OUTCOMES` verbatim, `session_identity()` verbatim, `collect_slots()` with `ScoreError` becoming `BatchError` and the five-arm prose generalized, and `c7_record_shape_problems()` verbatim — see the note above the table for why they have no row of their own, and note that `harness/score.py` must read all four from here exactly as it must read `CODE_PARTITION` from here; **(11)** `require_lawful_destination()` is rewritten for ADR 0004: 012 asked whether a destination lay inside a registered `freeze.excluded` TREE, this registry has no such member, and the rule is therefore computed from `make_manifest`'s own constants — a destination is lawful when writing into it cannot add a covered entry — with 012's device/inode `_identity_overlap()` fail-closed clause carried unchanged; **(12)** `STUDY_CLI_STANDIN` names a CLI when `--cli-override` does not, resolved once per command by `resolve_cli()` so preflight's digest gate, the invocation and the ledger header see one value — it removes no gate, and `tests/test_batch.py` asserts it refuses under the committed registry; **(13)** 012's `verify_chain()` over the ledger is renamed `verify_ledger_chain()`, because this module imports `integrity`, whose `verify_chain()` is the PORT chain, and two functions of that name over two chains in one namespace is a name a reader has to disambiguate every time; **(14)** the module keeps a `plan` subcommand — the command it had while the calling half was unported — because it is the one way to read the registered order without a registry, a wrapper or a call. Carried unchanged and named so a reader does not have to diff for them: the `__main__`-guarded safe-import-path and untracked-source tripwires (012 lines 214–272), which refuse today for SCAFFOLD item T3's reason. **Still not carried:** anything that scores — admission, the rates, the verdicts and every `score_rates` surface beyond the four functions above |
| `harness/integrity.py` | `98e11a14f931e47ece6b5c975afe46a18ef784d8824785fab8632083c5014af1` | `harness/integrity.py` | `d0dbca3a255a38fce383d5cd1bce8d85736d48da9d5e1a80f3f5740393dce3f8` | **PARTIAL — the chain, the interpreter, the unreviewed-bytes gate, the label rule.** Carried **verbatim** (byte-sliced from the source, not retyped): `IntegrityError`, `digest()`, `_refuse_duplicate_keys()`, `load_json()`, `bare()`, `parse_ports()` and the `ROW` regex (012 lines 169–219); `verify_interpreter()` (1142–1160); `_code_equal()`, `_const_equal()`, `verify_bytecode()` (1163–1346); `_refuse_unsafe_import_path()` (1386–1414) — including its references to Study 012's README steps, which this study's runbook has not been written yet (SCAFFOLD item R5). Rewritten for the one-level chain: `verify_chain()` keeps every idiom of 012's — the unfinished-port placeholder scan — whose token is deliberately not quoted here, because this file is one of the two the scan reads and quoting it refuses the port, as it did once while this row was being written —, the registry's own `pinnedFrom` members checked against review-bound constants, the exact destination set, per-row source and destination digests — and drops the two levels this study does not have; the source-side authority is 012's own PORTS.md destination cell per row, and the one untiered row is bound to the recorded commit. New: `study_label()`, `freeze_pin_state()`, `unfilled_pins()` (the registered label rule, decided in one place) and `verify_manifest()`. **Not carried, deliberately:** the arm-artifact checks (C8), the family schema (C9), the clean-room mirror gate (C10), the 280-cell landmark grid, the policy parser, `sigma`, the census helpers — none of them names anything in this study — and the `[D-20]` whole-tree git manifest, superseded by ADR 0004's exact-set manifest, because carrying both would give one study two manifests that could disagree. Imports dropped with them: `itertools`, `importlib.util` at module scope, `Counter`, `Decimal`. **SCAFFOLD item M1, points 2 and 3 (closed here):** `REQUIRED_PORTS` registers SEVEN destinations rather than five — the two scorer modules below are as loud an addition as a deletion would be, which is the whole point of an exact set — and `TIER1_TWELVE_PATHS` gains `harness/e4lib/stats.py` -> 012's `harness/score_rates.py` and `harness/e4lib/census.py` -> 012's `harness/census.py`, so both rows are bound to 012's OWN destination cells exactly as the other four are. 012's source cell for its census (`analysis/diversity.py`, Study 011) is one level further back than this one-level chain reaches and is deliberately not read. Three head comments change `four` to `six` with it |
| `harness/transcript_check.py` | `64542bc5d6d8f6682a29dee870aa07feb5757db3941c48af581a974c2423a5b2` | `harness/transcript_check.py` | `9dd321348b0e1595d7eef620c3155d840f98b4d531d92655fc949185064f586d` | **complete port, no check logic changed.** The `response_item` whitelist, the terminal-prompt rule, the leak denylist mechanism, the golden allowlist comparison, the completion byte binding, the `turn_context` model/cwd binding, the integer-exit-0 rule and duplicate-key rejection are 010's through 011 and 012, unchanged. Two SUBJECTS change: `LEAK_TOKENS` is this study's vocabulary (representations, scored surface, mutant machinery, policy domain) and not 012's policy-family vocabulary; and the arm label is one of A/B/C. The token list is design-time and is marked `GATE(pre-freeze)` in the module docstring and in SCAFFOLD.md item G3: it must be re-derived from the frozen policy prose and the naming appendix, with a committed checker shown to have power on mutated inputs |
| `harness/score_rates.py` | `f4d4463f081439f147a341bb38d8a6b709b3860f73f6f4e524234a180ec23336` | `harness/e4lib/stats.py` | `c26fa5a586be593218b16bdc5e6955267c72a6c4f21f2d284326a4e3338f635b` | **PARTIAL — the interval arithmetic only, plus this study's contrast.** Carried with their arithmetic unchanged: `ALPHA`, `BISECTIONS`, `_tail_ge()`, `_tail_le()`, `_bisect()` (the registered 200-halving bisection, fixed iteration count and exact comparison, so the same inputs give the same bits on any platform), `clopper_pearson()`, `lower_bound()`, `upper_bound()`, `probability_at_least()`, `rate_block()`, and **`REGISTERED_VECTORS` verbatim, all three rows** — 012's n = 30 and n = 25 are retained as PORT CONTROLS against numbers a predecessor already published, and its n = 50 row is this study's own per-arm denominator (§2 "Batch shape"). `harness/tests/test_score_stats.py` reproduces every published bound to the four decimals 012 printed; a drift in this arithmetic stops a previous study's number reproducing and the suite says so before anything is scored. **Not carried:** `HIGH_CUT`, `LOW_CUT`, `high_threshold()`, `low_threshold()` — Study 011 §5's review-depth cuts, reported by 012 as a product quantity and naming nothing in this study — and the whole of 012's scoring, population, census and record-compilation surface, which is about arms, policies and mirrors. Changed: `ValueError` becomes `StatsError` with a NAMED CODE as the message's first word (`CP-NO-TRIALS`, `CP-NOT-A-COUNT`), because this study's refusals are read by a scorer that publishes them and an unnamed refusal is a string. **Added below the port banner, from THIS study's design prototype `design/mutants/oc_table.py` (sha256 `4707e50cee46a1a922f4202911efbfae311c6a20ddae0c96d1d0846c549cd131`, cited in the module docstring as assembled-from-design lineage rather than as a cross-study port):** `z2_table()`, `tail_coefficients()`, `sup_tail_numerator()`, `sup_le_alpha()` and `critical_level()` carried, plus `critical_level_at()` (memoised, so the two registered contrasts at one N read the same c\*), `excludes_zero()` (Reading 1 — the Δ₀ = 0 inversion, which is the whole of what §5's decision reads), `tau_cut()` (§5's operative INTEGER cut, derived from the paired count at run time rather than transcribed) and `interval_endpoints()`, a REFUSING STUB raising `FM-ENDPOINTS-UNPORTED` because the Δ₀ sweep that produces the reported endpoints is not ported and §10 commits to publishing every interval (SCAFFOLD item S7) |
| `harness/census.py` | `911eb25773923789e5ddeae20f0bfa68032f932ae9c62fd7e9a21ad8aa8b73ea` | `harness/e4lib/census.py` | `d5b2093815218f78988610d5372df7632c768b7f0bcb584b538e861ed04a5b23` | **PARTIAL — the machinery, not the endpoints.** §5 registers E5 as "012's census machinery, ported", so this is the sixth row SCAFFOLD item S6 owed. Carried verbatim: `_token()` (012 lines 237-241), `show_signature()` (226-235), `cover_greedily()` (251-269), and `_x4()`'s `signature()` grouping (515-541) as `signature_groups()` with its ordering key unchanged — descending by run count, then by the rendering, "so the order is a fact about the data and not about a hash", which is what 012's round-5 finding 9 forced into existence. Changed, and it is a behaviour change rather than a rename: `show_multiset()` sorted by `Decimal(value)` because 012's values were risk scores; this study's are outcome tokens, so it sorts by the rendered string and a numeric sort that would raise is gone. **Not carried, because they name Study 012's stimulus and nothing here:** `_policy_mirror()`, `edges()`, `embargoed()`, `score()`, `band()`, `profile()`, `probe()`, `probe_exact()`, `deciding_clause()`, `clause_text()`, `show_probe()`, `_near_edge_row()`, and X1-X6 (`_x1()`…`_x6()`) with 012's `render_markdown()` — 012 censused vendor records a model wrote inside a completion under one arm's thresholds, and this study's authors emit a policy and a test suite, so there is no `vendor` record to bucket and carrying them would give this study six endpoints it did not register. **New, and only §5's two registered rows:** `encoding_key()`, `pairwise_disagreement()`, `census()` and a small `render_markdown()`; the stimulus is a PARAMETER rather than a module constant (012 read the arm's `FAMILY.json`), so the machinery cannot silently run on the wrong grid. Carried unchanged from 012's own port decisions: **no publisher and no `__main__`** (the only publisher in this study is `harness/score.py`) and **no interval** (case-level counts inside one completion are not independent trials). `registered_stimulus()` is a REFUSING STUB raising `E5-STIMULUS-UNREGISTERED`: §9 puts the census on a different stimulus from the E4 rates and no such grid is registered, so running the census on the gold grid because it is the grid to hand would manufacture exactly the tradeoff statement §9 forbids (SCAFFOLD item S6) |
| `harness/make_manifest.py` | `660a350ad8a647a2df9fea443af273c8c20480bd276c5a74336e345a86cadb81` | `harness/make_manifest.py` | `40cf9b4c4756e105bd2a2515941c732c0e73784f036e00ce006b9ed21d221e02` | **complete port, ADR 0004 applied.** From Study **014** (no lock, no pin: bound to the recorded commit alone). `REGISTERED_DOCUMENTS` is this study's registered set; `EXCLUDED_DOCUMENTS` gains **`DEVIATIONS.md` and `README.md`** — ADR 0004's named exclusions, excluded by construction and asserted by `harness/tests/test_manifest.py` **while both files exist**, so the assertion has power rather than guarding an absent path — and keeps 014's `harness/PINS.json` linear-anchor exclusion; `EXCLUDED_ARTIFACTS` names the manifest itself; the covered set adds `harness/*.sh` and `harness/PORTS.md`; and `pending_documents()` plus a `--freeze` flag are new, because several registered documents do not exist yet pre-freeze and a set discovered by globbing at freeze time is not a registered set — `--freeze` refuses while any is pending. 014's `EXCLUDED_FIXTURE_ROOTS` and its `fixtures/` and `adapter/` globs are dropped: this study has neither tree. **SCAFFOLD item M1, point 4 (closed here):** `manifest_entries()` globs `harness/e4lib/*.py` as well, because the scorer's ten modules decide every published rate and ten reviewed sources outside the exact-set manifest is the hole ADR 0004's manifest exists to close. The glob is ONE level, like the other three, so a nested package added later must be registered rather than swept in |

**This table is machine-read, and its columns answer to different
authorities.** This file is editable in *this* study, so it cannot be the
authority for what the inherited bytes were. `harness/integrity.py` therefore,
in order: verifies Study 012's `harness/PINS.json` against the digest it pins
for it; verifies Study 012's `harness/PORTS.md` against the digest **012's own
registry** records under `ownPorts`; verifies **this file** against the digest
`harness/PINS.json` records for it, so the change list cannot be rewritten
after the review; and then binds each row — the six Study 012 rows to 012's
own destination cells on the source side and to this table on the destination
side, the Study 014 row to the recorded commit's working file. It also requires
the destination set to be exactly the seven files above, so a deleted row
refuses rather than quietly dropping a check.

**Two rows are AHEAD of their registry, deliberately and in the registered
order.** `harness/SCAFFOLD.md`'s freeze-fill step 6 says "`PORTS.md` before
`PINS.json`, always: the registry pins the ports table and never the reverse."
The two new rows therefore land here first, and three things move after them
and are owed by name in `harness/SCAFFOLD.md` item M1: `PINS.json`'s
`ownPorts.sha256` (which pins this file and no longer matches),
`integrity.REQUIRED_PORTS` and `integrity.TIER1_TWELVE_PATHS` (which register
the exact destination set and its 012-side paths), and
`harness/STUDY-MANIFEST.sha256`. Until they do, `integrity.verify_chain()`
REFUSES — which is the correct state, not a broken one: `harness/score.py`
files that refusal as a pipeline problem and the attempt is pipeline-invalid,
so nothing is adjudicated against an unpinned ports table.

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
records compiler, and all of `score_rates.py` and `census.py` EXCEPT the two
partial rows above — 012's scoring, population, ledger-reconciliation and
record-compilation surface, and its X1–X6 census endpoints. This study's
stimulus is a contest policy in three representations, its oracle is a gold
suite plus two reference implementations, and its endpoint is what an authored
test suite kills — none of that machinery names anything here.

Also not ported: Study 012's `harness/tests/` — its fixtures are about arms,
policies and mirrors. This study's suite is new, and small on purpose.

## Assembled from this study's design prototypes

These modules are not cross-study ports and have no row in the table: they are
this study's own `design/` code, carried into the harness with its line ranges
named in the assembled module's docstring together with the prototype's path
and sha256. The prototypes were run against the real pinned engines during the
design phase, which is why they are carried rather than re-authored — but they
are this study's bytes, and a two-sided row would claim an inheritance from
another study that does not exist.

| assembled module | design prototype | prototype sha256 |
|---|---|---|
| `harness/e4lib/extract.py` | `design/pilot/pilot_run.py` (81–86, 181–216) | `09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295` |
| `harness/e4lib/admit.py` | `design/pilot/pilot_run.py` (242–275, 276–315) | `09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295` |
| `harness/e4lib/engines.py` | `design/pilot/pilot_run.py` (217–229, 232–241, 316–414); `design/mutants/e4_score.py` (337–374); `design/gold/check_gold.py` (the floor-gate invocation) | `09da06b3…`; `beb42b39…`; `a3aa62ea51491f370f4423f4945b79aa9bae06d03dd60489b9c8952ec6e9294b` |
| `harness/e4lib/e4.py` | `design/mutants/e4_score.py` (152–194, 195–231, 232–245, 295–308, 310–336, 375–384, 556–654) | `beb42b3903284dc2c33baff33000325814a1e53171d8268ca4d56820e4f995fb` |
| `harness/e4lib/stats.py` (contrast half only) | `design/mutants/oc_table.py` (141–275) | `4707e50cee46a1a922f4202911efbfae311c6a20ddae0c96d1d0846c549cd131` |
| `harness/leak_tokens.py` | `design/POLICY-DRAFT.md` — the STIMULUS SLICE the source itself marks off (`## Vendor Approval Policy` … `## Design notes (not part of the stimulus)`), read as prose and not as code | `bc6eeff9e18e144e055e32f85402ad4c47b1c05b64743cfbc1a6f4012fb0ad40` |

`harness/leak_tokens.py` is the odd one in that table and says so: its
"prototype" is the stimulus PROSE, not design code. SCAFFOLD item **G3** requires
`LEAK_TOKENS` to be re-derived from the frozen policy text rather than curated,
with a committed checker showing the list has power on mutated inputs, so the
module is the derivation: three registered rules over the slice the source marks
off for itself (bold and backticked terms; clause ids; the threshold numerals of
comparison sentences and their spellings), one admissibility filter that
publishes every drop with its reason, and three checks — `check_power()` (every
witness sentence the source's own markup identifies is caught, a scrambled list
of the same size catches strictly fewer, the empty list none),
`check_rederivation()` (move a threshold in the source and the derived list moves
with it) and `check_negative_corpus()` (no derived token fires on any name the
wrapper builds). The digest above is the source's at derivation time and
`report()["source"]["sha256"]` recomputes it; `policy/POLICY.md` supersedes the
draft at the freeze with no edit to the module, because `SOURCES` is ordered.
`harness/transcript_check.py`'s tuple is still the design-time list and
`design_time_gap()` computes, rather than remembers, what the freeze must copy
across.

`harness/e4lib/decision.py` is assembled from a PROGRAM SHAPE rather than from a
prototype — Studies 015–018's `decide()`, generalised from an if-ladder to an
ordered table, for the reason its docstring gives (Study 018's round-8 finding 1
was a decision rule whose code and whose registration disagreed, and a ladder
gives nothing to enumerate). Its authority is `PREREGISTRATION.md` §5's own
bytes, which `harness/tests/test_score_decision.py` reads directly.

## New here, not ported

`harness/PINS.json`, `harness/PORTS.md`, `harness/SCAFFOLD.md`,
`harness/STUDY-MANIFEST.sha256`, `harness/e4lib/__init__.py`,
`harness/score.py`'s own publishing surface (the argument surface, the attempt
record, the population rule, the E1/E2/E3/E4 aggregations and the rendered
report), and `harness/tests/` (`test_schedule.py`, `test_manifest.py`,
`test_pins.py`, `test_partition.py`, `test_score_stats.py`,
`test_score_extract.py`, `test_score_admit.py`, `test_score_engines.py`,
`test_score_e4.py`, `test_score_decision.py`, `test_score_census.py`,
`test_score_attempt.py`, `test_score_pipeline.py`).

`test_score_pipeline.py` is the one module that invokes the real engines, and it
SKIPS unless `JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` hash to the pins — §7 forbids
invoking `jpack` or `opa` in CI, so skipping there is the registered behaviour.
It exists because SCAFFOLD item T1 records the precise failure mode of
hand-verification: "which is evidence and not a suite: nothing in the repository
re-runs it."

Still **not written**: the driver's calling half (SCAFFOLD items D1–D8), the
golden-context capture and the isolation negative control (G1–G2), and the
three refusing stubs named in the table above and in SCAFFOLD items S6, S7
and S9.
