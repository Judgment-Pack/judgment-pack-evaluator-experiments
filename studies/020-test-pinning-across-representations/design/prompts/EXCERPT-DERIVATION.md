# Language-excerpt derivation rules (DESIGN DRAFT, not registered)

BRIEF.md §3: *"every language construct used by that arm's frozen reference implementation
must appear in that arm's excerpt, and the reference may use no construct absent from the
excerpt — asserted by a freeze test. The Rego excerpt is derived by a registered rule from
the official OPA docs at a pinned commit (named pages in full, not maintainer-curated
slices); the cross-vendor reviewer holds an explicit veto over both excerpts."*

Both excerpts are produced by `derive_excerpts.py`. Neither is ever hand-edited; the check is
`check_excerpt_sufficiency.py`, which derives each construct inventory **from the reference
artifact itself** rather than from a hand-kept list.

## Rule A — arm A (Judgment Pack)

Two documents, **each verbatim and in full**, from the `judgment-pack-spec` working tree at
commit `c2faf4937037ae88b57fdb3e297f9aafefed3997`:

| Source | Bytes | Edits |
|---|---|---|
| `spec/judgment-pack-core.md` (JPS Core 0.2.0-draft) | 51,391 | none |
| `schema/judgment-pack-core.schema.json` | 14,268 | none (wrapped in a fenced `json` block) |

The schema is in the excerpt because of a measured failure, not a preference: with the prose
alone, the sufficiency check of 2026-08-15 failed on `op` and `evidenceRequirement` — the
specification defines the model in prose but does not spell every JSON member of the carrier.
Both documents are normative artifacts of the same pinned release (§1.1's precedence list), so
including both keeps the rule at document granularity rather than becoming a curated slice.

**Not in the excerpt, and why:** the runtime's own docs (`docs/building-with-packs.md`, the
`packs test` / `packs suggest` workflow) are excluded — the study measures **single-shot
authorship**, and a document teaching an authoring loop is out of the system boundary
(BRIEF §3). The one consequence is recorded as a ledger row below.

## Rule B — arms B and C (Rego), byte-identical between the two arms

Named pages, **each in full**, from `open-policy-agent/opa` at commit
`16b5a013726fff3c2197f98ac4afcd6d2218588a`:

| Source | Bytes |
|---|---|
| `docs/docs/policy-language.md` | 117,709 |
| `docs/docs/policy-reference/index.md` | 10,837 |
| `docs/docs/policy-reference/keywords/if.md` | 1,210 |
| `docs/docs/policy-reference/keywords/contains.md` | 1,249 |
| `docs/docs/policy-reference/keywords/default.md` | 547 |
| `docs/docs/policy-reference/keywords/every.md` | 1,118 |
| `docs/docs/policy-reference/keywords/some.md` | 528 |
| `docs/docs/policy-reference/keywords/not.md` | 3,649 |
| `docs/docs/policy-reference/keywords/import.md` | 3,595 |
| `docs/docs/policy-testing.md` | 17,929 |

Plus one **generated** section: the built-in function signatures, produced from the pinned
capabilities file the checker and evaluator are both run with. This is not a curation choice —
the OPA documentation renders its built-in tables from an MDX component
(`<BuiltinTable category=.../>`), so the signatures are not present in the page sources at
all. Generating them from the pin has a second, deliberate effect: the excerpt states exactly
which built-ins the capability gate admits, which the author would otherwise have to guess.

Scaffolding strip (the only edit to any upstream page, applied mechanically):
front matter; `import … from "@site/…";` lines; self-closing MDX component tags, each
replaced by a visible one-line marker naming the component removed.

## Sufficiency check — run of 2026-08-15

`check_excerpt_sufficiency.py`: **PASS**.

- arm A: 54 constructs derived from `reference/refA/pack.json` — every root and object member
  name, all five condition ops (`fact`, `all`, `any`, `not`, `evidence-present`), all five
  operators, both `onUnknown` values, all three exception effects, the evidence-requirement
  `kind`, the escalation target `kind`, and the three escalation triggers — **0 missing**.
- arms B/C: 12 constructs derived from `reference/refB/policy.rego` after comment stripping —
  `package`, `default`, `if`, `else`, `in`, `some`, `null`, `:=`, comprehension, function
  rule, `count`, `object.get` — **0 missing**.

Two facts the check surfaced and the preregistration should carry:

1. The reference Rego uses **no** `every`, `not`, `with`, `contains` or `import` in code —
   those tokens appear only in its comments. A construct inventory taken from raw text (the
   obvious implementation) would have over-claimed the excerpt's necessary surface by five
   constructs. The inventory is taken after comment stripping.
2. Sufficiency is directional. It says the excerpt *covers* the reference. It does not say the
   two excerpts are comparable in size or completeness — they are not: 66 KB of a **complete**
   small language versus 189 KB of a **fragment** of a large one. BRIEF §6 already registers
   that asymmetry as a mechanism running *against* the training-prevalence gradient, and this
   build is the measurement of it.

## Ledger rows this derivation adds (candidates for the §2.3 asymmetry ledger)

- **B/C-favorable.** `opa test` has an upstream normative page (`policy-testing.md`) that
  enters arm B/C's excerpt under the derivation rule. The arm-A test matrix is a *runtime
  convention* with no specification page at all, so its format reference in
  `ARM-A-INSTRUCTIONS.md` is **maintainer-authored** — the one part of arm A's language
  teaching that is not an upstream document. Written from the matrix section of the runtime's
  `docs/building-with-packs.md`, format only, no authoring advice.
- **A-favorable.** Arm A's excerpt is the *entire* normative definition of its language, and
  its artifact is schema-checked JSON. No Rego excerpt of any size is the whole of Rego.
- **Neutral, worth stating.** The built-in list handed to B/C is exactly the admitted set, so
  a B/C author cannot lose a run to a built-in they had no way to know was denied. Arm A has
  no analogous failure mode (its pack declares no functions), so this is a floor removed from
  one arm only.
