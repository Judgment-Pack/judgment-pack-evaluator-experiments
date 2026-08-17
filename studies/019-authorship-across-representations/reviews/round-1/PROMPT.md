# Review round 1 — prompt (verbatim)

You are the cross-vendor adversarial reviewer required by this program's interim review
regime (RFC 0009): a non-Anthropic model reviewing a preregistration before its freeze.
Your findings will be committed verbatim and dispositioned one by one in writing; the
freeze cannot happen until a later round of this review returns exactly `freezable as
written`.

The study is `studies/019-authorship-across-representations/` in this repository. Its
question: within the registered JPS-expressible policy fragment, under single-shot
authorship, does the representation a model authors in (Judgment Pack vs raw Rego vs Rego
under a prescribed judgment convention) change what its accompanying test suite pins down —
measured as mutation-kill rates against registered single-edit mutants.

## Read

- `PREREGISTRATION.md` — the governing draft. Read it first and completely.
- `design/POLICY-DRAFT.md` — the contest policy (stimulus prose + design notes).
- `design/BRIEF.md`, `design/PANEL-FINDINGS.md`, `design/POLICY-PANEL-FINDINGS.md` — the
  design-phase record.
- `design/gold/` — `gold_author.py`, `gold.json`, `check_gold.py`, `GOLD-NOTES.md`.
- `design/cleanroom/` — `DECISIONS.md`, `DISPOSITION.md`, `oracle.py`, `check_oracle.py`.
- `design/reference/` — `AGREEMENT.md`, `OFFGOLD-CERT.md`, `refA/REPORT.md`,
  `refB/REPORT.md`, the reference implementations.
- `design/mutants/` — `ADEQUACY.md`, `E4-NOTES.md`, `OC-TABLE.md`, both `MANIFEST.json`
  files, `refA/REGISTRY.json`, the generators, `e4_score.py`, `oc_table.py`.
- `design/prompts/` and `design/pilot/` — the arm materials, naming appendix, assembler,
  driver; `design/pilots/2026-08-15-calibration-pilot-01/NOTE.md` and the SCORE files.
- `design/TOOLCHAIN-NOTES.md`.
- `harness/` — `PINS.json`, `PORTS.md`, `SCAFFOLD.md`, `score.py`, `batch.py`,
  `authoring_call.sh`, `e4lib/`, `tests/` including `E2E-SMOKE.md`.

## Verify against source, not trust

- Every `PORTS.md` row, two-sided, including the source cells against
  `studies/012-policy-perturbation/harness/`'s own lock.
- The §5 statistical constants against `design/mutants/OC-TABLE.md` AND
  `harness/e4lib/stats.py` — the code, not the prose.
- The X1 class definition across `PREREGISTRATION.md` §4, `design/gold/check_gold.py`,
  `harness/score.py`, and `design/reference/OFFGOLD-CERT.md`.
- The gold digests across both mutant MANIFESTs and `design/gold/gold.json`.
- Every count the preregistration asserts (rows, mutants, pairs, cells) against the
  artifact that carries it.

## Scrutinise

1. The §1a population rule against the scorer's code partition: construct an authoring
   failure that leaves the denominator, or an apparatus failure that stays in it.
2. The E4 chain end to end — extraction, admission, identity control, X1 filter, pairing,
   τ cut, engine-supplied-kill separation: find a way a weak suite scores high-kill or a
   correct suite scores zero.
3. The §5 decision rule: ordered, exhaustive, last row always matches? Find an outcome
   reaching two rows, or none.
4. The design-provenance disclosures: is any pilot-informed choice (the E4 pivot, τ, δ)
   under-disclosed or under-mitigated?
5. Cross-arm fairness: the prompts, the contracts, the byte asymmetry, the asymmetry
   ledger, the arm-C convention — find a choice that predetermines the contrast.
6. The gold/oracle chain: find a circularity the stated ceilings do not already carry.
   Include the A1 record (the confirmed risk-40 cliff) and the adequacy dispositions
   (C1–C5): is any drop mechanism wrong?
7. X1 and the off-gold certificate: find a number the exclusion leaks into that it should
   not touch; judge the input-domain closure for the screening result.
8. The statistics: the FM-score construction, the meshes (Δ₀ denominator 100, 48
   bisections), unequal-N, fixed-sequence gatekeeping, the OC table's power claims —
   against the implementations.
9. The frozen-reader standard: a reader holding only the immutable-candidate files after
   the freeze — find a sentence they would read that the artifacts contradict.

## Holdout

This study's reviewer-authored prospective content is a **sealed mutant set** (§1a, §4):
authored by you in a later round, committed verbatim, first executed at the primary
attempt, scored "as authored". State whether you are prepared to author it. **Do not
author mutants this round.**

## Output

Numbered findings `R1-<n>`: severity BLOCKER / MAJOR / MINOR, file/section, a
one-paragraph failure mode, and a concrete fix. Cite the file you read for every claim. A
clean pass on an area is a finding only if you can defend having actually worked it. Then
one line, exactly one of: `freezable as written`, `freezable after listed fixes`,
`DO NOT FREEZE`.
