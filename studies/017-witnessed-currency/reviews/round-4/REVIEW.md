# Round-4 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-11. Verdict: **freezable after listed fixes** (4 RESOLVED, 3 PARTIALLY RESOLVED, 1 NOT RESOLVED, 1 new BLOCKER).

> Note: the reviewer's citations were emitted as links to absolute worktree paths; they are
> normalized here to bare file references. The finding prose is otherwise verbatim.

## Confirmation

- R3-1 — PARTIALLY RESOLVED — The separate evidence map covers h01–h09, the reviewer-authored block remains byte-identical, and each field is adjudicated as `witness:<field>`; the registered triples `(comparisonPerformed, validSightings, unattributedSightings)` are correctly h01 `(true,2,0)`, h02 `(false,1,1)`, h03 `(false,2,0)`, h04 `(false,2,0)`, h05–h07 `(true,2,0)`, h08 `(true,1,0)`, and h09 `(false,0,0)`. The file is declared a freeze pin, but R4-1 prevents confirming pin-before-execution. ([evidence registry], [authored constructions], [round-2 original], [freeze-pin registration], [adjudication])
- R3-2 — RESOLVED — Every live claim now limits witness-3’s unpinned status to the locked-replication stratum and explicitly records h02 as unpinned and h03/h04 as pinned. ([PREREGISTRATION.md:106], [PINS.json:14], [sighting.py:16])
- R2-1 residual — RESOLVED — The committed regression checks the named floor and count floor separately and confirms the foreign-series record is never compared; production attribution skips it before updating either `attributed_keys` or `valid`. ([test_study.py:205], [verify_witness.py:269], [STUDY-MANIFEST.sha256:30])
- R1-1 residual — PARTIALLY RESOLVED — The governing preregistration now accurately matches the bootstrap—equivalent caches are accepted and only import-eligible divergent caches are refused—but the pin-registry note, upstream-loader docstring, and cache-test docstring still falsely claim that any cache is refused; narrow those three statements. ([PREREGISTRATION.md:77], [score.py:40], [PINS.json:3], [upstream016.py:73], [test_study.py:113])
- R1-2 residual — RESOLVED — Dependency enforcement refuses an absent imported module, a module without `__file__`, and an imported path absent from that exact distribution’s file inventory. ([score.py:247], [score.py:270], [score.py:278])
- R1-6 residual — RESOLVED — The pair floor now counts only closed-schema records naming the cell’s series and verifying under a configured pinned key before applying the configured minimum. ([score.py:407], [verify_witness.py:151])
- R1-9 residual — NOT RESOLVED — Section 5 correctly names the structured registries and `witness:<field>` channels, but the latest published matrix remains five-column, while the current generator adds a sixth header yet emits five-cell rows without reading `witnessEvidence`; render the three values, add a column-shape/content regression, and publish a fresh matrix. ([PREREGISTRATION.md:195], [DETECTION-MATRIX.md:6], [score.py:702])
- R1-13 residual — RESOLVED — The mutation regression individually covers all four registered seed labels, and production enforcement derives from each registered value while checking its builder constant. ([PINS.json:16], [test_study.py:194], [score.py:306])

## New findings

- R4-1 — BLOCKER — `harness/score.py` holdout gate / `harness/build_fixtures.py` context gate: `matrixHoldoutEvidence` is a new freeze pin, but both execution gates still enumerate the old pins, and a missing evidence file silently loads as `{}`. With the five old pins filled and the evidence pin null, the run is merely labeled PILOT, null-pin enforcement is skipped, and the holdout can execute with outcome-only adjudication—allowing structured expectations to be selected after observation. Require every freeze pin before construction, make missing or coverage-invalid evidence terminal, bind/recheck its digest in the holdout context, and add a one-null-pin-at-a-time regression. ([score.py:115], [score.py:793], [score.py:798], [build_fixtures.py:304], [score.py:601])

freezable after listed fixes
