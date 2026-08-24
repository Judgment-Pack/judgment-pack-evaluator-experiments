# Arm prompt materials — design record (DESIGN DRAFT, nothing here is registered)

Written 2026-08-15 for the **calibration pilots**. These materials are inputs to a labelled,
non-citable pilot (BRIEF §4.2). They are not the frozen prompts; the frozen prompts are
assembled by the ported 012 `arm_assembly.py` at preregistration time, from files with their
own digests in `harness/PINS.json`.

## 1. Assembly

    prompt(arm) = [policy prose stimulus] + [naming appendix] + [arm suffix materials]

joined by `\n\n---\n\n`, built by `pilot/assemble_prompt.py`:

| Arm | Suffix materials, in order |
|---|---|
| A | `generated/JPS-EXCERPT.md`, `ARM-A-INSTRUCTIONS.md` |
| B | `generated/REGO-EXCERPT.md`, `REGO-TASK-HEAD.md`, `generated/ARM-B-CONTRACT.md`, `REGO-TASK-TAIL.md` |
| C | `generated/REGO-EXCERPT.md`, `REGO-TASK-HEAD.md`, `ARM-C-CONVENTION.md`, `REGO-TASK-TAIL.md` |

Assembled sizes (2026-08-15): **A 84,289 B**, **B 204,333 B**, **C 206,686 B**.

Two mechanical rules the assembler enforces:

- **Stimulus slice.** The prose is `POLICY-DRAFT.md` from `## Vendor Approval Policy` to the
  rule before `## Design notes (not part of the stimulus)`. The draft's status header and its
  design notes never enter a prompt: they name the panel findings, the reference build's
  encoding decisions (V6, S1-vs-S2), the registered X1 exclusion and the ledger rows — every
  one of which is an answer.
- **Comment strip.** HTML comments are removed from every material file. The headers labelling
  these files DESIGN DRAFT, and the fairness rule each was written under, are HTML comments
  precisely so they cannot reach a model.

`B` and `C` share `REGO-TASK-HEAD.md` and `REGO-TASK-TAIL.md` as **one file each**, so the two
Rego arms cannot drift apart anywhere except the inserted contract/convention block. That is
the registered reading of the B-vs-C contrast, enforced by file layout rather than by care.

## 2. The fairness rule these materials were written under

> The materials teach the LANGUAGE and the REQUIRED OUTPUT FORM. They must never hint at the
> policy's solution structure: no worked example from the policy's domain, no threshold from
> the policy, no clause name, no encoding pattern the policy's clauses would need.

Enforced, not just asserted, by `check_prompt_materials.py` (run of 2026-08-15: **PASS**):

1. **Fairness screen** — a token scan of every material for the policy's domain words, its
   input-value literals (`CLEAR`, `MATCH`, `UNKNOWN`, `LOW`, `MEDIUM`, `HIGH`, case-sensitive),
   its six numeric thresholds and its fifteen clause labels.
2. **Appendix consistency** — every value the result contract pins is one the shared naming
   appendix already pins (plus `unresolved`, which is the contract's own and appears in no
   appendix list).
3. **Contract parity** — arm C's embedded schema equals `RESULT-CONTRACT.schema.json`, and arm
   B's prose contract is exactly what `deformalize_contract.py` emits from that schema.
4. **Shared-part parity** — the two Rego arms' head and tail are single shared files.
5. **Toy validity** — every toy artifact embedded in the materials is executed: the toy pack
   validates under the pinned `jpack` (and its toy matrix runs 3/3 rows green under
   `packs test`); the toy Rego policy, its toy test file and arm C's convention snippet all
   pass `opa check --strict` under the pinned capabilities, and the toy tests pass `opa test`.
   A toy that does not run teaches a shape that does not work.
6. **Marker parity** — the marker rule the materials state is the rule `pilot_run.py`
   implements, read from `pilot_run.ARM_MARKERS` rather than restated.

Both toy examples are the same unrelated domain (renewing a library loan), which shares no
input, no threshold and no clause shape with the contest policy.

**Deliberately withheld from every arm**, because each would be a solution hint: any example
of an exception that suppresses a rule (that is exactly the registered O1 encoding), any
negation-cascade or catch-all example, any `onUnknown` guidance beyond the specification's own
text, and any statement about which clause governs where two could. Arm A's toy shows one
`force-outcome` exception only; the specification above it documents the other two effects.

## 3. What each arm is told beyond its language

| | A | B | C |
|---|---|---|---|
| Result shape | fixed by the specification (§8.3 disposition) | prose contract | JSON Schema contract |
| Catch-all convention | **prohibition**: do not declare `fallbackOutcome` | — | **prescription**: `default decision := {"disposition": "unresolved", "reasons": ["no-match"]}` |
| Precedence discipline | — | — | C2 (exactly one determination; make precedence explicit) |
| Unresolved discipline | in the specification | in the contract's value list | C3/C4 (a value, not an absence; carry all grounds) |
| Test artifact reference | maintainer-authored matrix format | upstream `policy-testing.md` | upstream `policy-testing.md` |

The `fallbackOutcome` prohibition and C's registered default are the two halves of one
registered asymmetry-ledger row (POLICY-DRAFT design notes: "arm A's counterpart is the
*prohibition* on declaring `fallbackOutcome`, B/C-favorable"). They are stated here so a
reader can see the shape of the asymmetry without reading the ledger: **C is handed the
catch-all; A is forbidden the shortcut and must reach `no-match` structurally.**

## 4. Open items for the maintainer and the review round

- **~~OPEN-1~~ — DECIDED 2026-08-18 (maintainer), closing round-1 finding R1-17.** The
  tension this item raised was real and the decision went the other way from the
  recommendation: rather than narrow the formality claim, **the formality claim is deleted**.
  BRIEF §3's "B and C differ in formality only" is withdrawn; A−C is registered as a
  **bundled** representation-plus-convention treatment, the estimand is the bundle's effect,
  and **no attribution of any part of an A−C result to any component of the bundle** —
  representation, result schema, or any individual convention — is licensed
  (`../../PREREGISTRATION.md` §1, §5, §9). The original statement is kept below the strike
  because it is what the notes said at the time.

  > BRIEF §3 says B and C "differ in formality only", and also that C carries a full
  > judgment convention B does not have. As built, the B→C step changes **two** things: the
  > contract's formality *and* the presence of C1–C5. Either the claim is narrowed ("the
  > contract differs in formality only; C additionally carries the convention"), or the
  > convention is itself de-formalized into B — which would make C's treatment the schema
  > alone, i.e. v1's design, which review already rejected as motivated. Recommend narrowing
  > the claim in the preregistration; flagged, not decided here.
- **OPEN-2 (duplication).** The result contract restates the four determination ids and the
  four ground tokens that the shared naming appendix already pins. This is duplication, but
  the alternative — a schema deferring to prose for its value lists — removes exactly the
  formality that distinguishes C from B. Mitigation implemented: check 2 above fails if any
  contract value is not an appendix-pinned identifier, so the two cannot drift.
- **OPEN-3 (prompt cost).** The B/C prompt is ~2.4× arm A's (204 KB vs 84 KB) and ~50k tokens.
  At N=50/arm this is the dominant token cost of the study and it is *load-bearing*: shrinking
  the Rego excerpt would break the derivation rule (named pages **in full**) and hand the
  fairness argument to the reviewer. Budget it; do not trim it.
- **OPEN-4 (matrix reference authorship).** Arm A's matrix format reference is
  maintainer-authored because the matrix has no normative document. It is format-only prose,
  but it is the one piece of arm-A language teaching not derived from an upstream source, and
  the cross-vendor reviewer's excerpt veto should be pointed at it explicitly.
- **OPEN-5 (arm A output-form burden).** Arm A must emit a valid JSON *document* by hand
  inside a fenced block; a single trailing comma is `unparseable` with no repair. Arm B/C's
  artifact is a program, where a comparable slip is a `rego_parse_error` — the same drop code,
  and the pilot must report the two rates side by side so the review can see whether the
  extraction layer is measuring authorship or typing.

## 5. Files

| File | Role |
|---|---|
| `NAMING-APPENDIX.md` | shared, pre-existing; not duplicated by anything here |
| `ARM-A-INSTRUCTIONS.md` | arm A task, pack rules, matrix format, toy, output form |
| `REGO-TASK-HEAD.md` | arms B+C shared task, rules, toy |
| `generated/ARM-B-CONTRACT.md` | arm B contract (generated; do not hand-edit) |
| `ARM-C-CONVENTION.md` | arm C contract (schema) + conventions C1–C5 |
| `REGO-TASK-TAIL.md` | arms B+C shared output form |
| `RESULT-CONTRACT.schema.json` | the single source of the contract |
| `deformalize_contract.py` | schema → B's prose, the registered de-formalization |
| `derive_excerpts.py` | both excerpts, from the pins |
| `check_excerpt_sufficiency.py` | BRIEF §3 sufficiency criterion |
| `check_prompt_materials.py` | the six checks in §2 |
| `EXCERPT-DERIVATION.md` | the two derivation rules, pins, digests, sufficiency result |
| `generated/EXCERPT-PROVENANCE.json` | per-source commit + sha256 |
| `upstream/opa/` | the fetched upstream page bytes, so the build is offline-reproducible |
