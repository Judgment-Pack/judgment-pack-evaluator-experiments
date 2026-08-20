# V7 — completeness, re-derived over the frozen gold grid

**Registered obligation** (`design/POLICY-DRAFT.md`, verification row V7; enforced by
`harness/make_manifest.py` since round 7, finding R7-9): re-derive the completeness
argument mechanically over the gold grid — the reference build's 236,196-cell derived-space
sweep is evidence, not the registered artifact — asserting exactly one governing clause per
cell under the earliest-clause tie-break, and asserting that the former X1 region is
**covered**, because an exclusion that once existed stays falsifiable.

## The derivation, run at the freeze

`design/gold/check_gold.py` over `gold/GOLD.json` (sha256
`6a41174bc6765781d4eae6eec610994240173fcdf97d442c8aeef6ce63bb9cc3` — the same digest every
record of both mutant manifests carries as `goldSha256`), under CPython 3.12.11 with both
pinned engines (`jpack` 0.17.0, OPA 1.19.0):

    117 rows; 0 failures (0 floor-gate); registered exclusion classes 0;
    rows inside the retired X1 region 5

The checker asserts, per row: structural validity (unique ids, valid dispositions, sorted
reason tokens, reasons empty iff outcome); citation of its governing clause(s) under the
**earliest-clause tie-break** — the tie-break is authored into every multi-clause row's
`cite` by `design/gold/gold_author.py` and validated against the clause table, so a row
citing a later clause where an earlier one governs is a checker failure, not a style
choice; boundary witnesses — every numeric literal exercised at the literal and at an
adjacent value; and the floor gate — **both** pinned engines reproduce every row's
disposition, so the 0-failure line above is a statement about 234 engine evaluations, not
about prose.

## The former X1 region is covered, not excluded

The registered exclusion set is **empty** — X1 was retired by round-1 finding R1-2, which
tested the inexpressibility claim instead of arguing it (`reference/refA/PACK-CHANGE-001.md`).
The five rows the checker counts inside the former region are, by id:

    x1r-low-spend-unreadable-40, x1r-low-spend-unreadable-69,
    x1r-country-unreadable-100k, x1r-country-unreadable-40, x1r-country-unreadable-69

Each is an ordinary gold row: cited, boundary-witnessed, floor-gated on both engines. A
future edit that quietly re-excludes the region has to delete named rows from the frozen
suite, which the study manifest pins.

## What this document does not claim

The one-clause-per-cell property is asserted over the **117 gold rows**, which are the
registered scoring surface — not over the 236,196-cell derived space, whose sweep lives in
`controls/off-gold-equivalence.json` as the two references' agreement and is a statement
about the references, not about gold. The two artifacts answer different questions and
neither stands in for the other.

Reproduce: `cd design/gold && check_gold.py` under the pinned interpreter with
`JPACK_BIN`/`OPA_BIN` set to the pinned binaries.
