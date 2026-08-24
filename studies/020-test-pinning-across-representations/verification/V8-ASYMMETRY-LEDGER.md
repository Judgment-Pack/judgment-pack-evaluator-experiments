# V8 — the asymmetry ledger, re-derived from the two reference implementations

**Registered document.** `design/POLICY-DRAFT.md`'s open item **V8**: *"re-derive the
asymmetry ledger from the two reference implementations, with its final balance stated"*
(`harness/SCAFFOLD.md` step 2b; `harness/make_manifest.py`'s `REGISTERED_DOCUMENTS`).
`make_manifest.py --check` names this file while it is absent and `--freeze` refuses on it.

This document does three things and no fourth. It **collects** every asymmetry the design
phase registered, with its source citation. It **re-derives** what is derivable against the
committed reference bytes, and labels every row either `verified-against-bytes` or
`registered-prose-only` — never both, never neither. It **states the final balance** as the
registration reads it. No row is invented; no registered row is dropped. One registered row
(**V8-15**) does not survive re-derivation on its stated magnitude, and it is carried with
that failure recorded rather than deleted.

---

## Provenance

The two reference implementations this ledger is re-derived from, and the policy draft that
declares the obligation:

| artifact | sha256 |
|---|---|
| `design/reference/refA/pack.json` (arm A reference, JPS pack) | `db9776070fbf5e193443ffb1f371b2524b4662f0877868306323b5c9e3701853` |
| `design/reference/refB/policy.rego` (arm B/C reference, Rego v1) | `1f2e1ad1d423240dd262852f19057a8e906387d5a1b71db8b8a15bc010fc12e2` |
| `design/POLICY-DRAFT.md` (declares V8; carries the ledger rows) | `c4a533cab4dc6b6fa5e5f3b92d999ebf130cfbfaa5811ace49087c16612173bc` |

`refA/pack.json`'s digest is the **post-repair** one `reference/refA/PACK-CHANGE-001.md`
records (`956ceebb…` → `db977607…`, the X1 repair of 2026-08-18);
`refB/policy.rego` is unchanged across that repair, exactly as the change record states.
The chain therefore re-derives clean: this ledger is written against the same two byte
sequences the change record, the agreement report and the off-gold certificate name.

Supporting artifacts cited by row, with the digests they were read at:

| artifact | sha256 |
|---|---|
| `PREREGISTRATION.md` | `47240377ab7506dcc36af0afb31dc13ee8b57c14a77539856029e21fa4a8b054` |
| `design/BRIEF.md` | `5de39b5d13beec587c6f31e008bee5017362ec356c31681652d37e405ea49bf2` |
| `design/PANEL-FINDINGS.md` | `35dd74e447f97972b1cdd5bda36b4daa498ff7df3c537aac61c396c591f5cec4` |
| `design/POLICY-PANEL-FINDINGS.md` | `206fa78194ff351057ca8e89ef615260f8ba00cdfb25e74d65f4425ef2fe9480` |
| `design/reference/refA/REPORT.md` | `2520a6c4c034c302dcf8a15defc0aa864ee18e696c8a25a62c7a327795019459` |
| `design/reference/refA/PACK-CHANGE-001.md` | `73f94f84d93fae07e026536522761137fb3e6f071e51ba0e48989bdce856850d` |
| `design/reference/refB/REPORT.md` | `21107a1b5ed60f29b57e1b4aac8ca1f08c4f6a5e68c2bb2de25dfc4a0cb9de25` |
| `design/mutants/ADEQUACY.md` | `8a79398ab7e19369b7a971904b8d47eb03623f4e2969163ca18604e1793fb988` |
| `design/mutants/refA/MANIFEST.json` | `2a7a6ad2642544c445415ba083ba591e4b134a6a7a8ff1a575c7ff3ddbbbe4c1` |
| `design/mutants/refB/MANIFEST.json` | `bf3995defe7b779acd19006aa6befecd67d2b7a8661cdd8f4ad7a2f13c1db8c8` |
| `design/mutants/adequacy_region_lemma_price.json` | `6f058f765f3fd67384288cd1d39d0467c832d4ae1c4050bd05da4c5cf04a6e2f` |
| `design/mutants/adequacy_pairing.json` | `888f7779e126a19716e34b9c260081cd4eb013d607f2b1ba010e67aafdb4f015` |
| `design/prompts/PROMPT-NOTES.md` | `e12d2c580fcd8fb3499659dc62afc2fbc5ff89c26517c6afa483bee73e42fc39` |
| `design/prompts/generated/JPS-EXCERPT.md` | `6b2b6c6713eefa5dbf89f535e5e3098c29454fc077c7c08cc8523dc22d424248` |
| `design/prompts/generated/REGO-EXCERPT.md` | `8a77ab7e5a3ee933bbc4a248916dedfa4d5c56344934e3a15fe3a6a637edae91` |

**Sources swept for rows**, per the registered definition: `design/POLICY-DRAFT.md` (V8
bullet and design notes), `design/BRIEF.md` §2.3/§3/§4.2, `design/PANEL-FINDINGS.md`,
`design/POLICY-PANEL-FINDINGS.md`, `design/reference/refA/PACK-CHANGE-001.md` §4.2,
`design/reference/refA/REPORT.md`, `design/reference/refB/REPORT.md`,
`design/mutants/ADEQUACY.md` (caveats C1–C6, the `subsumed-region-lemma` class, the
engine-supplied kill counts), `design/prompts/PROMPT-NOTES.md`, and `PREREGISTRATION.md`
§1/§3/§4/§4b/§5/§9. **§4b was swept and yields no arm-asymmetry row**: it partitions
*review findings* into the registered surface and the review-support apparatus, not
representations into advantaged and disadvantaged. Its bearing on this document is that it
places `verification/V8-ASYMMETRY-LEDGER.md` on the **registered** side — a finding against
this ledger is answered, not recorded as an advisory.

**Direction vocabulary.** `A-favorable` = the construct costs arm A less than arms B/C.
`B/C-favorable` = it costs arms B/C less than arm A. `neutral-to-A-unfavorable` is one
row's own registered wording and is kept verbatim. `neutral` = an asymmetry that exists but
is removed from the scored surface by a registered rule enforced in code. `unsigned` = the
registration deliberately publishes the asymmetry without asserting a direction. Where a
registered source signs a row, that sign is used; where the source names a row without
signing it, the direction is derived from the cited material and the row's detail says so.

---

## The ledger

| Row | Asymmetry | Direction | Source citation | Re-derivation status |
|---|---|---|---|---|
| **V8-01** | Engine-supplied conflict detection, **authoring face**: two true rules naming different outcomes are `unresolved{conflict}` in arm A; the same stray rung in a B/C `else` chain is silently shadowed and usually still correct. Same-outcome overlap (D3∩D4) is *not* a conflict. | `neutral-to-A-unfavorable` (registered sign, re-signed from the brief's `A-favorable`) | `BRIEF.md` §2.3 (original, A-favorable); `POLICY-PANEL-FINDINGS.md` regoFair #3 (mis-signed); `POLICY-DRAFT.md` "Panel-verified engine facts" — *"conflict detection is neutral-to-A-unfavorable on this policy and the ledger signs it accordingly"* | verified-against-bytes |
| **V8-02** | Engine-supplied conflict detection, **mutation-detection face**: **27** JPS mutants are killable only through the engine's structural `unresolved{conflict}`, against a **registered empty class (0)** for Rego. Reported both included and excluded. | `A-favorable` | `PREREGISTRATION.md` §4, §9; `ADEQUACY.md` "Kill counts with and without the engine-supplied kills §4 requires" | verified-against-bytes |
| **V8-03** | Strong-Kleene semantics plus per-rule `onUnknown` perform U1's counterfactual dependency analysis **structurally** in arm A; arm B/C hand-build the whole quantification. This is the **A1 uniform-U1 burden**: v0.2 deleted O2's carve-out so U1 governs uniformly, which cost the Rego reference its entrypoint O2 rung and forced O3 into U1's quantification. | `A-favorable` (derived — the V8 bullet names the row without signing it) | `POLICY-DRAFT.md` V8 bullet ("A1's uniform-U1 burden") and "Adjudication A1"; `POLICY-PANEL-FINDINGS.md` regoFair #3 row (1), LARGE; `refB/REPORT.md` encoding decisions §1 and §3 + the appended adjudication note | verified-against-bytes |
| **V8-04** | The §8.2 **evidence document** gives arm A an engine-supplied tri-state channel ("omitted key = unknown"); Rego has no such channel, so B/C fold availability into ordinary facts and hand-implement the tri-state. Consequence: "evidence-mechanism confusion" is a structurally **arm-A-only** E3 category, marked within-arm-only in the scorer. | `A-favorable` | `BRIEF.md` §2.3; `PANEL-FINDINGS.md` #7(c); `POLICY-DRAFT.md` feature matrix "Tri-state evidence (§8.2 document)" | verified-against-bytes |
| **V8-05** | P1's two distinct evidence reasons come free from §8 step 2, and D2's `no-match` free at step 10, in arm A. | `A-favorable` (small — the panel's own sizing) | `POLICY-PANEL-FINDINGS.md` regoFair #3 rows (2) and (3) | verified-against-bytes |
| **V8-06** | `else`/`default` give **ordered precedence for free** in Rego while JPS Core forbids rule priority, so arm A hand-writes D8's negation cascade, re-stating every excluded rule's literals. The negation count is a registered arm-A covariate. | `B/C-favorable` | `BRIEF.md` §2.3 and §4.2; `PANEL-FINDINGS.md` #7(b); `POLICY-DRAFT.md` feature matrix "Ladder pinned in prose"; `refB/REPORT.md` encoding decision §1 | verified-against-bytes (magnitude restated: **7** disjuncts, not the panel's "six") |
| **V8-07** | D5's cross-outcome exclusion is inexpressible as a condition in arm A (Kleene monotonicity), so it costs a **suppress-rule family** — one suppression per rule D5 displaces; in Rego it is a single rung placed above the approval rungs. | `B/C-favorable` | `refA/REPORT.md` encoding decision (2) — *"an asymmetry-ledger row (B/C-favorable) the notes do not yet carry"*; `PACK-CHANGE-001.md` §1 (the eighth and ninth members) | verified-against-bytes (magnitude restated on **both** sides: **9** suppressions, not seven; **0** negated conjuncts in Rego, not one) |
| **V8-08** | O1's `suppress-rule` needs a **region-scoped companion review rule** in arm A — suppressing a rule does not falsify its condition inside another rule's negation cascade, so the naive encoding turns the O1 region into `no-match`. In Rego it is one conjunct plus the else-chain. | `B/C-favorable` | `POLICY-PANEL-FINDINGS.md` regoFair #10 — *"register it explicitly as an asymmetry-ledger row (free in B/C: one `not newvendor_yes` conjunct plus the else-chain)"*; `POLICY-DRAFT.md` feature matrix "Exception: suppress-rule" and "Panel-verified engine facts" | verified-against-bytes |
| **V8-09** | **The former X1 region (V8 new row 1).** The natural arm-A encoding cannot express the region under any `onUnknown` assignment; expressing it costs **a derived region lemma the prose never states**. Arms B/C need no such lemma — a total function answers the region directly. A **cost row, not a fragment boundary**: the inexpressibility finding is withdrawn. | `B/C-favorable` | `POLICY-DRAFT.md` V8 bullet and the X1 retirement note; `PACK-CHANGE-001.md` §4.2 — *"a real asymmetry-ledger row against arm A"*; `refA/REPORT.md` correction header | verified-against-bytes |
| **V8-10** | **The inert O3 conjunct (V8 new row 3).** O3's "and financial evidence is available (P1)" conjunct — the sentence added to restore P1's reason purity in arm A — is *behaviourally inert* in a ladder, because the P1 rung short-circuits first. A prose sentence that exists solely to make a correct JPS pack reachable, and costs a Rego author nothing. | `B/C-favorable` | `POLICY-DRAFT.md` "Ledger row (B/C-favorable, from the build)"; `refB/REPORT.md` §5 and "Irreducible mismatches"; `ADEQUACY.md` `entailed-guard` (financial-evidence sub-form) — *"the asymmetry ledger's inert O3 conjunct row, now measured"* | verified-against-bytes |
| **V8-11** | **Numerics, re-scoped.** The brief registered "native numerics" as B/C-favorable; OPA 1.19.0 numerics are exact big-rationals so all six thresholds compare exactly in *both* arms and the row is smaller than registered. What survives is the arm-A **wire-form hazard**: ordered comparisons are defined only over decimal strings, and a JSON number or a leading-zero string yields `unknown` everywhere, with no B/C counterpart. | `B/C-favorable` (magnitude re-scoped by the panel) | `BRIEF.md` §2.3 (original); `POLICY-PANEL-FINDINGS.md` regoFair #3 (re-scoping); `POLICY-DRAFT.md` "Panel-verified engine facts" and the per-arm wire-form statements | verified-against-bytes |
| **V8-12** | The `fallbackOutcome` **prohibition** in arm A against arm C's **prescribed** `default decision := UNRESOLVED{no-match}` — the two halves of one registered row. C is handed the catch-all; A is forbidden the shortcut and must reach `no-match` structurally. A prohibition is the harder instruction to follow from prose. | `B/C-favorable` | `POLICY-DRAFT.md` "Scored surface" — *"(asymmetry-ledger row, B/C-favorable)"*; `POLICY-PANEL-FINDINGS.md` regoFair #— (default value); `PROMPT-NOTES.md` §3; `PREREGISTRATION.md` §3 | verified-against-bytes |
| **V8-13** | **C2.** Arm C's prescribed `default decision` is made **untestable by the shape the same prescription produces**: a total ladder never consults its default, so its mutants are unkillable by construction. Signed in `ADEQUACY.md` as *"the mirror image of arm A's inert-O3-conjunct row"* — so the cost falls on arms B/C. | `A-favorable` | `ADEQUACY.md` caveat **C2** — *"**Ledger row**: a prescribed convention that the shape the same prescription produces makes untestable"* | verified-against-bytes |
| **V8-14** | **The subsumed region lemma (V8 new row 4; C6).** `r-o1-wide-low` strictly contains `r-o1-review`; both say `review`, both `onUnknown: ignore`, and D5 suppresses them together — so `r-o1-review` is behaviourally inert and **nine** of its mutants are unkillable by any gold suite in any arm. **Gross class size: 9; marginal to the X1 repair: 6; already unkillable before it: 3.** Its one edit that widens *out* of the containing region, `m-a-076`, is killed. | `B/C-favorable` (an arm-A-reference-shape cost with no arm-B counterpart), **endpoint-neutral by exclusion** — an empty witness set never pairs, so the nine are not in the E4 denominator | `POLICY-DRAFT.md` V8 bullet (labelled form, verbatim); `ADEQUACY.md` `subsumed-region-lemma` and caveat **C6**; `adequacy_region_lemma_price.json`; `PREREGISTRATION.md` §9 | verified-against-bytes |
| **V8-15** | **C1.** Ten arm-B drops hold **only because the sanctions domain is closed** — sound relative to the registered input domain, and they would not survive a domain change. No arm-A counterpart is recorded. | `unsigned` (arm-B-side instrument-scope caveat; `ADEQUACY.md` does not sign it as a ledger row) | `ADEQUACY.md` caveat **C1**; `reviews/round-1/REVIEW.md` **R1-3** | **verified-against-bytes — FAILS on its stated count.** The class C1 itself describes has **11** members, not ten. See the detail below; the row is carried, not deleted. |
| **V8-16** | **C3.** One arm-B drop (`m-b-086`) is a **language artifact**: the guard is inert only because OPA's total value ordering already makes `null > 2000000` false. The guard is documentation, not behaviour; the policy text has no view on it. | `unsigned` (arm-B-side instrument-scope caveat) | `ADEQUACY.md` caveat **C3**; `ADEQUACY.md` `entailed-guard` (last sub-form) | verified-against-bytes |
| **V8-17** | **C4.** Arm A's five `reason-set-idempotence` drops are **relative to the reference's shape** — unkillable because `r-d8` carries `onUnknown: escalate` and its cascade is unknown wherever those rules are unknown, a consequence of the S1 encoding the reference build selected over S2. Under a different admissible encoding they might be killable. | `unsigned` (arm-A-side instrument-scope caveat; same family as C6, but not signed as a ledger row) | `ADEQUACY.md` caveat **C4** | verified-against-bytes |
| **V8-18** | **C5.** Arm A's **negative** adequacy claims are **transcription-borne** (a §7/§8 re-implementation, validated against the pinned engine on sampled evaluations and reproduced by a second independent transcription), while arm B's search is **engine-borne**. The residual is named rather than smoothed: no artifact provides 419,904 × 17 process launches of the pinned binary. | `unsigned` (an asymmetry in evidential basis, not in authoring cost) | `ADEQUACY.md` caveat **C5**; `ADEQUACY.md` round-3 "Method" — *"same engine-borne arm-B search, same transcription-plus-validation for arm A"* | registered-prose-only |
| **V8-19** | The **E2 authoring-outcome partition is arm-structural**: four of the six registered codes are reachable in arm A, five in arms B/C. `schema-invalid-pack` cannot arise in B/C; `opa-check-failed` and `v0-syntax` cannot arise in A. | `neutral` — the asymmetry is real and is **refused in code** rather than scored across arms | `PREREGISTRATION.md` §1a and §5 ("arm-structural categories within-arm-only, enforced in the scorer"); `BRIEF.md` §2.3 and §3 | verified-against-bytes |
| **V8-20** | The **handoff / escalation-target** member exists in arm A and **has no Rego counterpart to align**, so it is excluded from every endpoint; O3's queue name is routing information, scoreable only at the document level, and is not scored. | `neutral` — removed from the scored surface by the registered endpoint scope rule | `BRIEF.md` §2.3 endpoint scope rule; `POLICY-DRAFT.md` "Scored surface"; ADR-0025's own reasoning | verified-against-bytes |
| **V8-21** | `applicability` is **forbidden by the naming appendix**, so the `not-applicable` kind is unreachable and needs no alignment cell — an arm-A-only output kind removed by prescription rather than aligned. | `neutral` — removed by the naming appendix and asserted by the admission layer | `POLICY-DRAFT.md` "Scored surface"; `design/prompts/NAMING-APPENDIX.md` | verified-against-bytes |
| **V8-22** | **The two arms' kill denominators are different sizes and their rates are quantised on different lattices.** The two integer cuts are published side by side and **nothing reconciles them**. | `unsigned` (registered as irreconcilable) | `PREREGISTRATION.md` §9 and §4; `adequacy_pairing.json` | verified-against-bytes |
| **V8-23** | **Prompt byte asymmetry**: A 84,289 B; B 204,333 B; C 206,686 B — the B/C prompt is ~2.4× arm A's. Registered as *the cost of full-page parity*, published beside every result, and folded into the A−C bundle rather than corrected. | `unsigned` — published as a registered cost, not as an advantage either way | `PREREGISTRATION.md` §2 and §9; `PROMPT-NOTES.md` §1 and OPEN-3 | verified-against-bytes |
| **V8-24** | **Reference-excerpt asymmetry**: the JPS excerpt is 66,060 B, the Rego excerpt 191,115 B (2.89×). Registered as a named threat with the affordable control — an **excerpt-provenance rule** (each arm's excerpt is the normative reference text for its language, selected by a registered mechanical rule, not curated) — because "byte counts published as part of the fairness commitment" does not equalize instructional quality. | `unsigned` — a registered threat under a provenance-rule control | `PANEL-FINDINGS.md` (Study 001 reconciliation finding); `PREREGISTRATION.md` §3 ("Excerpt parity is full-verbatim, not curated"); `PROMPT-NOTES.md` §5 | verified-against-bytes |
| **V8-25** | **OPEN-4.** Arm A's matrix-format reference is **maintainer-authored** because the matrix has no normative document; arms B/C's excerpts are upstream bytes with per-source commit and digest. The one piece of arm-A language teaching not derived from an upstream source. | `unsigned` — registered as the place to point the cross-vendor reviewer's excerpt veto | `PROMPT-NOTES.md` OPEN-4; `generated/EXCERPT-PROVENANCE.json` | verified-against-bytes |
| **V8-26** | **OPEN-5.** Arm A must emit a valid JSON **document** by hand — a single trailing comma is `unparseable` with no repair; arms B/C's artifact is a **program**, where a comparable slip is a `rego_parse_error`. The same registered drop code covers both, and the two rates must be reported side by side so review can see whether the extraction layer is measuring authorship or typing. | `B/C-favorable` (derived from the item's own content) | `PROMPT-NOTES.md` OPEN-5; `PREREGISTRATION.md` §1a; `harness/e4lib/admit.py` (`unparseable-artifact`) | partially verified-against-bytes — the shared-code half is verified; the rate comparison is prospective |
| **V8-27** | **The system-boundary rule** ("in-system = what the pinned binary does at evaluation time") is stated once and applied to all arms — and it strips arm A of `packs test`/`packs suggest` (ADR-0023/0024), the parts of the JPS system whose stated purpose is exactly the authoring reliability this study measures, while stripping B/C of `opa check`/`opa fmt` loops and the Rego editing ecosystem. The panel signed the net as running **against arm A**. | `B/C-favorable` (panel-signed), registered as **bounded by §9's non-claim** rather than corrected: no outcome is evidence about tooled authoring workflows | `BRIEF.md` §2.3 and §3; `PANEL-FINDINGS.md` #8; `PREREGISTRATION.md` §3 and §9 | registered-prose-only |
| **V8-28** | **Authoring-time asymmetry, 2–3×.** Pilot call durations: arm A 26–40 min, arms B/C 10–18 min. Registered as descriptive R2 data, never adjudicated — *"it is data, not noise"*. | `B/C-favorable` on cost; descriptive only | `PREREGISTRATION.md` §5 and §2; `design/pilots/2026-08-15-calibration-pilot-01/NOTE.md` | verified-against-bytes |
| **V8-29** | **Training prevalence.** The public Rego corpus is vast; the JPS corpus is this program. v1's asymmetric reading rule ("an A win despite the gradient is strong evidence; a Rego-arm win is ambiguous") was found unfalsifiable in the preferred direction and **deleted**; no gradient instrument is registered. | `unsigned` **by registration** — *"No direction of any result separates representation quality from training familiarity … both directions are reported as confounded"* | `BRIEF.md` §6; `PANEL-FINDINGS.md` BLOCKER #3; `PREREGISTRATION.md` §9 | registered-prose-only (the absence of a gradient measurement *is* the registration) |
| **V8-30** | **The measured fragment is arm A's expressive envelope**, selected by no other criterion — the contest is played on arm A's home field, and the constraint's cost is recorded where no endpoint reads it. | `A-favorable` **by construction**, registered as a §9 non-claim bounding generalization (nothing generalizes to business judgments at large), paired with the joint-reading prohibition pinned as a `CORRECTION.md` target | `PREREGISTRATION.md` §9; `BRIEF.md` §2.1; `PANEL-FINDINGS.md` (fidelity-benchmark finding) | registered-prose-only |
| **V8-31** | **A−C is a bundled treatment and nothing inside the bundle is separable.** Arm C differs from arm B in representation-adjacent formality *and* in substantive content (default decision, totality, explicit precedence, unresolved handling, grounds behaviour), and the arms' prompt exposures differ in bytes. The "B and C differ in formality only" claim is **withdrawn**. | *reading rule — no direction.* This is the rule under which every row above is read. | `PREREGISTRATION.md` §1, §3, §9; `PROMPT-NOTES.md` OPEN-1 (decided 2026-08-18, closing round-1 R1-17) | verified-against-bytes (artifact level) |

### Direction tally

| direction | rows | ids |
|---|---|---|
| `A-favorable` | **6** | V8-02, V8-03, V8-04, V8-05, V8-13, V8-30 |
| `B/C-favorable` | **11** | V8-06, V8-07, V8-08, V8-09, V8-10, V8-11, V8-12, V8-14, V8-26, V8-27, V8-28 |
| `neutral-to-A-unfavorable` | **1** | V8-01 |
| `neutral` (real, refused in code / off the scored surface) | **3** | V8-19, V8-20, V8-21 |
| `unsigned` (registered, direction deliberately not asserted) | **9** | V8-15, V8-16, V8-17, V8-18, V8-22, V8-23, V8-24, V8-25, V8-29 |
| reading rule (no direction) | **1** | V8-31 |
| **total** | **31** | |

### Re-derivation tally

| status | rows |
|---|---|
| `verified-against-bytes` | **25** (V8-01 … V8-14, V8-16, V8-17, V8-19 … V8-25, V8-28, V8-31) |
| `verified-against-bytes` — **FAILS** | **1** (V8-15) |
| partially verified-against-bytes | **1** (V8-26) |
| `registered-prose-only` | **4** (V8-18, V8-27, V8-29, V8-30) |

---

## Re-derivation detail

Every claim below was read out of the committed bytes at the digests in the provenance
table. Counts marked *(pack)* come from `refA/pack.json`, *(rego)* from `refB/policy.rego`,
and *(manifest)* from the two mutant MANIFESTs.

**V8-01.** *(pack)* `r-d3` (`risk >= 90` → `reject`) and `r-d4` (`HIGH` ∧ `risk >= 70` →
`reject`) overlap and **no exception excludes either from the other** — same-outcome overlap
is compatible at §8 step 9, exactly as the panel measured. The nine `x-d5-suppress-*`
exceptions exist precisely because a *cross-outcome* overlap would be a conflict. So on this
policy the engine's conflict detection removes no authoring burden from arm A; its live
effect is that a stray extra arm-A rule becomes a row error where a stray B/C rung is
shadowed. The brief's original A-favorable sign does not survive; `POLICY-DRAFT.md` already
carries the corrected sign, and this row reprints it rather than re-flipping it.

**V8-02.** *(manifest)* `refA/MANIFEST.json` carries `engineSuppliedKill: true` on exactly
**27** of its 183 records (`m-a-003, 005, 008, 009, 012, 014, 022, 038, 046, 048, 049, 051,
053, 057, 059, 062, 063, 067, 069, 071, 073, 076, 082, 086, 087, 120, 169`).
`refB/MANIFEST.json` carries `engineSuppliedKill` **false on all 185** records, with the
registered reason stamped in `engineSuppliedKillNote`: *"false on every valid Rego mutant BY
CONSTRUCTION: the reference is a total decision ladder with no structural conflict
detection."* **27 against 0**, re-derived.

**V8-03.** *(pack)* U1 has no representation in the pack at all: it is carried entirely by
`onUnknown` — **12 rules `ignore`, `r-d8` `escalate`**, `x-o3-large-exposure` `escalate`,
every other exception `ignore`. *(rego)* U1 costs a second **total** function `determine`
(**15 rungs**: head + 14 `else`), three hand-authored candidate lists with an
interval-coverage argument, a set comprehension, and a `count(...) == 1` test, plus a
**5-rung** entrypoint ladder. The A1 adjudication is visible in the bytes: the entrypoint
carries no O2 rung, and the comment at lines 259–265 records why — *"O2 therefore lives only
inside `determine`."* One honest note: `refB/REPORT.md`'s encoding-decision §1 lists **six**
entrypoint rungs; the committed module has five, because the same report's appended
adjudication note records the O2 rung's removal. The report is internally reconciled; its
§1 enumeration is stale against its own §"Adjudication note", and the bytes agree with the
note.

**V8-04.** *(pack)* two `evidenceRequirements` — `financial-evidence` (`required: true`) and
`insurance-certificate` (`required: false`) — read by `evidence-present` conditions: a
distinct input channel with engine-supplied tri-state. *(rego)* no such channel exists;
`fin_state` and `ins_state` are `object.get(input, ["evidence", …], "OMITTED")` sentinel
reads folded into ordinary facts, and the tri-state is realized by hand at entrypoint rungs
1–2 and `determine` rungs 8–10. The within-arm-only consequence is enforced in code, not
prose: `harness/score.py`'s `e3_taxonomy()` is called per arm and never over pooled runs,
and `harness/e4lib/admit.py`'s `ARM_REACHABLE_CODES` makes `admit()` refuse to return a code
its own arm cannot reach.

**V8-05.** *(pack)* `financial-evidence` with `required: true` produces **both** P1 limbs —
absent → `missing-required-evidence`, unreported → `unknown` — with no rule authored for
either; and with no `fallbackOutcome` declared, `no-match` is reached at §8 step 10.
*(rego)* the same two limbs cost entrypoint rungs 1 and 2, and `no-match` costs a `determine`
rung (D2), a backstop rung, and the `default` line.

**V8-06.** *(pack)* `r-d8`'s condition is `all(sanctions == CLEAR, not(any(…)))` where the
`any` carries **seven** disjuncts — D3, D4, D6a, D6b-insured, D6b-uninsured, D6c, D7 — each
re-stating the literals of the rule it excludes. *(rego)* the same precedence is rung order
in a 15-rung `else` chain with **zero** negation conjuncts; the report states rung order *is*
clause precedence and discharges the earliest-clause tie-break for free.
`POLICY-PANEL-FINDINGS.md` described a "six-disjunct negation cascade" for v0's C8; the
committed reference carries seven, because D6b's limb split in two. Magnitude restated,
direction unchanged.

**V8-07.** *(pack)* **nine** `x-d5-suppress-*` exceptions: `-d6a`, `-d6b-insured`,
`-d6b-uninsured`, `-d6c`, `-d7`, `-o1-review`, `-d8`, `-o1-wide-low`, `-o1-wide-spend`. The
build report's encoding decision (2) says *seven*, which was true of the pre-repair pack;
`PACK-CHANGE-001.md` §1 adds the eighth and ninth explicitly, and the committed bytes carry
nine. *(rego)* D5 is **one rung** (line 106–109, `v_prior == "yes"` → `reject`) placed above
every approval rung; the only two occurrences of `v_prior` in the module are its reader and
that positive test. So the build report's *"one `not prior_yes` conjunct in Rego"* is not
what the committed Rego does either — it needs **no conjunct at all**, rung order alone. The
row holds *a fortiori*: both stated magnitudes were wrong in the direction that understates
the asymmetry.

**V8-08.** *(pack)* O1 costs **six pack members of its own**: `x-o1-first-engagement`
(suppress `r-d6c`), the companion `r-o1-review`, and — after the X1 repair —
`r-o1-wide-low`, `r-o1-wide-spend`, `x-o1-suppress-d8-low`, `x-o1-suppress-d8-spend`. It
additionally causes three of V8-07's nine D5 suppressions (`x-d5-suppress-o1-review`,
`-o1-wide-low`, `-o1-wide-spend`), which exist only because those O1 rules do; they are
counted once, under V8-07, and are not re-counted here. *(rego)* one conjunct,
`v_new != "yes"` (line 162), plus D8's catch-all rung.

**V8-09.** *(pack)* `r-o1-wide-low` = `all(CLEAR, country == LOW, risk >= 40, risk < 70,
newVendor == yes)` → `review`, and `r-o1-wide-spend` = `all(CLEAR, risk >= 40, risk < 70,
spend <= 100000.00, newVendor == yes)` → `review`, both `onUnknown: ignore`, both present
with exactly the conditions `PACK-CHANGE-001.md` §1 tabulates. **Neither corresponds to any
clause of the prose**: each is a derived consequence an author must reason out (O1 removes
D6c, and inside the named region nothing else can reach the request). The repair's
mechanism is likewise in the bytes: `r-d8` carries **three** suppressions —
`x-d5-suppress-d8` (D5's, from encoding decision (2)) and the two region-scoped
`x-o1-suppress-d8-low` / `x-o1-suppress-d8-spend` — which remove D8's escalate-on-unknown
*only inside the region where the answer cannot depend on the unreadable member*, leaving
`r-d8` untouched everywhere else. *(rego)* no counterpart exists or is needed — `determine` is total and the region is answered through
D8's rung under U1's quantification. The digest chain re-derives: `db977607…` is the
post-repair pack, `1f2e1ad1…` the unchanged Rego, exactly as the change record states.

**V8-10.** *(pack)* `x-o3-large-exposure` carries `{"op": "evidence-present",
"evidenceRequirement": "financial-evidence"}` as its **fourth conjunct** — load-bearing,
because §8 accumulates reasons across steps and without it P1's reason set leaks.
*(rego)* `determine`'s O3 rung carries `fin_state == "present"` (line 72), and it is
**structurally entailed wherever it is evaluated**: `determine` is reached on the scored
entrypoint only through rungs 4 and 5, both of which already require `fin_state == "present"`,
and rungs 1 and 2 have consumed `"absent"` and `"OMITTED"` above them. So the conjunct cannot
change any result — inertness re-derived from the module's own control flow, not taken on the
report's word. Independently measured: *(manifest)* four arm-B mutants deleting a
financial-evidence guard (`m-b-062`, `m-b-084`, `m-b-088`, `m-b-090`) are unkillable and
dropped `entailed-guard`, which `ADEQUACY.md` names as this ledger row *"now measured"*.

**V8-11.** *(pack)* every ordered comparison is against a decimal **string** — `"90"`,
`"70"`, `"40"`, `"100000.00"`, `"500000.00"`, `"2000000.00"`. *(rego)* every comparison is
against a JSON **number** — `90`, `70`, `40`, `100000`, `500000`, `2000000`. The naming
appendix pins arm A's wire form ("decimal **strings** — integer scale for risk, two decimals
for spend, no leading zeros"), and `refB/REPORT.md` §6 records that the projection splices
the canonical decimal strings in unquoted so no float touches a value and all six thresholds
compare exactly. Both halves of the panel's re-scoping hold against the bytes: parity on
threshold exactness, no B/C counterpart for the arm-A hazard.

**V8-12.** *(pack)* `fallbackOutcome` is **absent** from the pack's top-level members
(`decision, description, escalation, evidenceRequirements, exceptions, id, metadata,
outcomes, rules, specVersion, title, version`), and `no-match` is reached structurally.
*(rego)* line 21 carries `default decision := {"disposition": "unresolved", "reasons":
["no-match"]}` verbatim as prescribed. `PROMPT-NOTES.md` §3's table confirms the two halves
are handed to the arms as a prohibition (A), nothing (B), and a prescription (C).

**V8-13.** *(manifest)* exactly two records carry `dropMechanismClass:
unreachable-default` — `m-b-124` and `m-b-125`. *(rego)* the mechanism is in the bytes:
`determine`'s last rung (line 182) is unconditional, so the ladder is total and the
registered default is never consulted; `refB/REPORT.md` records that deleting the `default`
line leaves 0 undefined results under `--fail` across all 2,540 cells.

**V8-14.** *(pack)* the subsumption is literal-for-literal: `r-o1-review`'s condition set is
`{CLEAR, LOW, risk >= 40, risk < 70, spend <= 100000.00, newVendor == yes}` and
`r-o1-wide-low`'s is the same set **minus** the spend conjunct — a strict subset. Both name
`review`; both carry `onUnknown: ignore`; both are suppressed by the D5 family
(`x-d5-suppress-o1-review`, `x-d5-suppress-o1-wide-low`). *(manifest)* exactly nine records
carry `dropMechanismClass: subsumed-region-lemma` — `m-a-016, 017, 018, 075, 077, 078, 079,
080, 183`. `adequacy_region_lemma_price.json` carries `grossClassSize: 9`,
`marginalToRepairCount: 6`, the three pre-existing ids (`m-a-017`, `m-a-077`, `m-a-079`) and
`boundaryEditsOnTheRuleKilled: ["m-a-076"]`. **The registered labelled sentence reproduces
exactly**: *"Gross class size: 9; marginal to the X1 repair: 6; already unkillable before it:
3."*

**V8-15 — the failure.** `ADEQUACY.md` C1 states *"**ten** arm-B drops hold only because the
sanctions domain is closed"* and then defines the class as *"every `entailed-guard` drop of a
`v_sanctions == "CLEAR"` conjunct (and `m-b-166`, `m-b-185`)"*. Against the committed
manifest the class it defines has **eleven** members. The `entailed-guard` sanctions-guard
sub-form has ten — `m-b-132, 134, 137, 138, 142, 147, 152, 157, 162, 166` — and `m-b-166` is
**already one of those ten**, so the parenthetical adds only `m-b-185`, whose
`unreachable-rung` drop `ADEQUACY.md` itself justifies by *"D1, D2 and D8 are jointly total
over the registered three-state sanctions domain"* — i.e. by the same domain closure.
10 + 1 = **11**. Round-1 finding **R1-3** states the identical arithmetic (*"C1 covers 11
such Rego drops, not the stated ten, while C2–C5 otherwise match their recorded scope
caveats"*); the round-1 disposition closed R1-3 at the X1 filter rather than at this count,
and `ADEQUACY.md`'s round-3 section then recorded *"their scope caveats C1–C3 stand
unchanged"*. **The row's mechanism and its direction are unaffected; only the stated
magnitude is wrong, by one.** It is carried here with the correction beside it, per the
registered rule that a registered row failing re-derivation is stated, not deleted. C2, C3,
C4 and C5 re-derive against the manifests as recorded.

**V8-16.** *(manifest)* `m-b-086` carries `dropMechanismClass: entailed-guard`, and
`ADEQUACY.md`'s `entailed-guard` section separates it as *"whose guard is entailed by OPA's
total value ordering rather than by the ladder (see caveat C3)"*. Exactly one such drop.
*(rego)* the guard is `v_spend != null` at line 255, in the entrypoint O3 rung.

**V8-17.** *(manifest)* exactly five records carry `dropMechanismClass:
reason-set-idempotence`. *(pack)* the mechanism is in the bytes: `r-d8` carries `onUnknown:
escalate` while every other rule carries `ignore`, and D8's cascade re-reads each approval
rule's literals across its seven disjuncts — the S1 shape the reference build selected over
S2.

**V8-18.** `ADEQUACY.md`'s round-3 Method states the asymmetry in its own words — *"same
engine-borne arm-B search, same transcription-plus-validation for arm A"* — and C5 names the
residual. Re-reading a method statement is not re-derivation, so this row is labelled
`registered-prose-only`; the artifact counts it rests on (1,717 checked evaluations, 88
confirmed witnesses, 1,800 live-edit cells adjudicated, 0 crosscheck disagreements) are
committed and were not re-run here.

**V8-19.** `harness/e4lib/admit.py`'s `ARM_REACHABLE_CODES` gives arm A four codes
(`no-marker-block`, `unparseable-artifact`, `schema-invalid-pack`, `unreadable-output-shape`)
and arms B/C five (the first two, plus `v0-syntax`, `opa-check-failed`,
`unreadable-output-shape`), and the module states that `admit()` *"refuses to return a code
its own arm cannot reach — an arm-structural category leaking across arms would make the E2
table compare two different partitions."*

**V8-20.** *(pack)* `escalation` declares `triggers: [missing-required-evidence, unknown,
no-match]` and `target: {kind: queue, name: vendor-compliance-desk}`. *(rego)* no counterpart
member exists. *(manifest)* `refB/MANIFEST.json`'s `scoredSurface` records the alignment
scope as *"kind + outcomeId + reasons … the Rego entrypoint value {disposition, reasons} is
entirely in scope"* — the arm-A-only member is outside it.

**V8-21.** `NAMING-APPENDIX.md` line 33: *"Do not use the `applicability` member."*
*(pack)* the reference declares no `applicability` member.

**V8-22.** `adequacy_pairing.json`: arm A **183** valid / 157 adequate / 26 empty-witness /
**69 paired** / 88 unpairable, integer cut **66** (0.956522 of 69); arm B **184** valid / 150
adequate / 34 empty-witness / **62 paired** / 88 unpairable, integer cut **59** (0.951613 of
62). Different denominators, different lattices, both cuts derived at the same τ = 0.95 —
re-derived exactly as §9 registers them, with nothing reconciling them.

**V8-23.** The committed pilot prompts measure **84,289 / 204,333 / 206,686** bytes
(`design/pilots/2026-08-15-calibration-pilot-01/prompt-{A,B,C}.txt`), byte-for-byte the
values `PREREGISTRATION.md` §2 and `PROMPT-NOTES.md` §1 publish. B/A = 2.42×, C/A = 2.45×,
C − B = 2,353 B.

**V8-24.** `generated/JPS-EXCERPT.md` = **66,060 B**; `generated/REGO-EXCERPT.md` =
**191,115 B** — 2.89×. `EXCERPT-PROVENANCE.json` records the derivation rule and per-source
commit and digest for each: arm A's is *"the JPS Core specification document and its
normative JSON Schema, each verbatim and in full"* (51,391 B + 14,268 B at commit
`c2faf493…`), arms B/C's the twelve named OPA doc pages at the pinned tag.

**V8-25.** `EXCERPT-PROVENANCE.json` carries upstream commit + digest provenance for the two
**derived excerpts** and for nothing else; `ARM-A-INSTRUCTIONS.md` (9,435 B), which carries
the matrix-format reference, is committed with no upstream provenance record — because there
is no upstream document for it. The asymmetry is exactly as OPEN-4 states it.

**V8-26.** `admit.py`'s `unparseable-artifact` row is genuinely shared: arm A *"the block is
not JSON"*, arms B/C *"`opa check` fails with only `rego_parse_error`, AND the same bytes
also fail under `--v0-compatible`"*. So the code half of the row — one registered drop code
covering both slips — is verified. The rate comparison OPEN-5 demands is prospective and
cannot be re-derived pre-freeze.

**V8-28.** `design/pilots/2026-08-15-calibration-pilot-01/NOTE.md` records *"Durations: arm A
1559–2408s per call; arms B/C 624–1101s"* — 26.0–40.1 min against 10.4–18.4 min, which is
where §2's published figures and §5's "2–3×" come from. Re-derived from the committed pilot
record.

**V8-31.** The bundle is visible in the committed materials: `generated/ARM-B-CONTRACT.md` is
**1,139 B** of result-shape-only floor contract against `ARM-C-CONVENTION.md`'s **3,954 B** of
schema plus five substantive conventions, while B and C share `REGO-TASK-HEAD.md` and
`REGO-TASK-TAIL.md` as **single files each**, so the two Rego arms cannot drift apart
anywhere except the inserted block. `PROMPT-NOTES.md` OPEN-1 records the decision that
deleted the formality-only claim (2026-08-18, closing round-1 R1-17), and
`PREREGISTRATION.md` §1 registers the bundle in its place.

---

## THE FINAL BALANCE

Stated as the registration reads it, not as a score.

### 1. The ledger does not balance, and it is not claimed to

**Eleven signed rows run B/C-favorable against six signed A-favorable**, with one further
row — engine-supplied conflict detection — carrying its registered sign
`neutral-to-A-unfavorable` after the design phase flipped it away from the brief's original
`A-favorable`. Three rows are asymmetries that are real and **refused in code** rather than
scored across arms; nine are registered and published with **no direction asserted**; one is
the reading rule the rest are read under.

`BRIEF.md` §2.3 offered two ways to discharge the imbalance: *"a registered balance
criterion over the ledger, or the imbalance stated as a non-claim bounding R1."*
`POLICY-PANEL-FINDINGS.md` regoFair #3 held that the second was **not sufficient here**,
because *"an A-unfavorable structural imbalance plus a directional hypothesis R1 (A>B) makes
an unsupported result uninterpretable rather than merely bounded."* Neither option was taken
as offered. What the preregistration does instead is remove the premise the objection rests
on: **R1 is registered two-sided and non-directional** — *"the A−C difference interval
excludes zero at two-sided α = 0.05 … this registration presupposes no direction"*, direction
reported as observed, an interval straddling zero returning INDETERMINATE and licensing
nothing. An A-unfavorable structural imbalance cannot make an *unsupported preferred
direction* uninterpretable when no direction is preferred. The imbalance is neither
corrected nor argued away; it is published, and the hypothesis is shaped so that it bounds
scope rather than poisoning inference.

### 2. Which arm each class favors

- **Engine-supplied semantics (V8-02 … V8-05) favor arm A**, and the largest of them —
  strong-Kleene plus per-rule `onUnknown` performing U1's counterfactual dependency analysis
  structurally — is the one where the panel's careful hand-written Rego single pass got the
  answer wrong. Registered as in-system by the system-boundary rule, *in both directions*.
- **Encoding cost in the references (V8-06 … V8-12) runs against arm A on every row** — the
  seven-disjunct negation cascade, the nine-member D5 suppression family, O1's eight-member
  companion apparatus, the derived region lemma, the inert O3 conjunct, the wire-form hazard,
  the `fallbackOutcome` prohibition. **This class carries the residual imbalance, and it is
  the class the contest policy chose.** Three of the four rows the V8 bullet names as new
  live here (V8-09, V8-10, V8-14), and all three run the same way.
- **Instrument-level rows (V8-13 … V8-22) are mixed and mostly neutralized in code.** The two
  that are signed are each other's mirror image by the study's own words: C2 costs arms B/C a
  convention its own prescribed shape makes untestable (A-favorable); C6 costs arm A nine
  mutants no suite in any arm can kill (B/C-favorable) — and C6's nine are **not in the E4
  denominator**, because an empty witness set never pairs. The rest are arm-scoped caveats on
  the adequacy gate's basis, carried unsigned.
- **Stimulus and exposure (V8-23 … V8-28) are published unsigned or against arm A.** The byte
  and excerpt asymmetries are the registered cost of full-verbatim parity — deliberately not
  equalized, because shrinking the Rego excerpt would break the derivation rule and hand the
  fairness argument to the reviewer. The two authoring-artifact rows and the system-boundary
  row run against arm A; the authoring-time row runs against arm A on cost and is descriptive
  only.
- **Registered non-claims (V8-29, V8-30) hold the two largest unmeasured asymmetries**, and
  they point in opposite directions: training prevalence favors the Rego arms and is
  registered as **confounded in both directions with no gradient instrument**; the fragment
  itself is arm A's expressive envelope and is registered as a **bound on generalization**.
  Neither has a magnitude, and neither may be given one from this study.

### 3. What the bundled-estimand registration means for reading all of it

**Every row in this ledger is a component of a bundle**, and `PREREGISTRATION.md` §1 and §9
register that *"no attribution of any part of an A−C result to any component of the bundle —
representation, result schema, or any individual convention — is licensed"*. That prohibition
governs this document as much as the prompt materials it covers.

So the ledger's registered function is **scope, not mechanism**. It fixes, before the batch,
what the contest policy made each representation pay for, so that a result cannot be
re-explained afterwards by an asymmetry nobody had written down. A reader may use it to bound
what an A−C or A−B result is a result *about*: the bundles as authored, over a policy whose
asymmetries are the thirty-one listed here, inside a fragment selected by arm A's expressive
envelope, with prompt exposures differing by 2.4× as the registered cost of parity. A reader
may **not** use it to attribute an observed difference to any row in it — not to the negation
cascade, not to the region lemma, not to the prescribed default, not to the engine's
conflict detection. The rows are the registered *content* of the treatments, and the
treatments are compared whole.

The corollary the registration is explicit about: **an unsupported R1 is not evidence that
the asymmetries cancelled**, and a supported R1 in either direction is not evidence that any
one of them did the work.

### 4. The one row that failed

**V8-15 (`ADEQUACY.md` caveat C1) does not survive re-derivation on its stated magnitude.**
The caveat says ten arm-B drops depend on the closed sanctions domain; the class it defines
has eleven. The mechanism, the direction and the caveat's consequence are unaffected — the
drops are sound relative to the registered input domain and would not survive a domain
change, exactly as recorded. Round-1 **R1-3** found the same arithmetic and it was closed at
a different cause. The row is carried here with its correction beside it rather than
adjusted or deleted, per the registered rule that a registered row failing re-derivation is
stated.

Three further registered magnitudes were restated against the bytes without changing any
row's direction, and all three had **understated** the asymmetry they describe: the D5
suppression family is nine members, not seven (V8-07); the Rego side of that same row needs
no negated conjunct at all, not one (V8-07); and D8's negation cascade carries seven
disjuncts, not six (V8-06). `refB/REPORT.md`'s six-rung entrypoint enumeration is stale
against its own appended adjudication note, and the bytes agree with the note (V8-03).

### 5. Balance, in one sentence

**The ledger runs against arm A on encoding cost and for arm A on engine-supplied semantics
and on the choice of fragment; it is registered as unbalanced, published in full, read under
a two-sided hypothesis and a bundled estimand, and it licenses no attribution of any result
to any row in it.**
