# Maintainer rulings on design brief v2 (2026-08-23)

Recorded against `BRIEF.md` v2's open M-items; each cites the brief's own argument where
the ruling adopts it. M-1 was answered 2026-08-22 (**BOTH**; the two-tier footing stands).

| M | Ruling |
|---|---|
| M-8 / M-20 | **The sweep decides, and the two are decided together as the brief requires.** The pre-pilot effort sweep (27 calls, §8's dual pricing) runs first; the registered compute condition is chosen from its result and priced at its own durations, with the per-setting abort rule printed. No condition is committed before the sweep reports. |
| M-13 | **Adopted as recommended.** The suite-against-own-policy score is registered as a reported quantity that R1's construct statement is conditioned on — one extra engine invocation per run, and a registered change to what "identity" means, named as such. |
| M-14 | **Work, not a ruling — executed before registration.** A focused forensic read of `arms/B/authoring/run-011/` against a perfect arm-B run decides the collapse mechanism; its verdict is appended to this file when it lands and the prompt's wire-form section inherits whatever it names. |
| M-15 | **Publish first.** The 019 R2 amendment (the arm-labelled quantities, their provenance, and the standing no-decision-reads-them clause) lands on 019's record before 020's preregistration is drafted. "A direction computed and then withheld is a direction published" — the record is made honest before anything registers on top of it. |
| M-16(d) | **The three L2c ceilings are accepted as registered ceilings**, stated in the preregistration in the brief's own words; L3's presence beside L2c is the mitigation. |
| M-18 / M-26 | **Rename.** R1's sentence names the measured construct: **witness-input coverage against the shared reference**. "Pinning power" survives only as motivation prose; §1 and §11 carry the construct statement; no headline uses the old name. |
| M-21 | **Accepted.** The honesty table (16/2 split, the ITT-only exception, the 66–68 % null-rejection figure) is a mandatory reprint in the preregistration. |
| M-22 | **Accepted and printed.** Tier C's conservatism against effects running through suite size is stated in §11 as a designed property, not discovered in results. |
| M-23 | **Option (a): no author-side gate.** The threat it names is caught deterministically by the prompt/prose/reference digest pins; an uncertifiable gate is not registered as if certified. |
| M-24 | **As drafted.** The effort pin is registered as a `CALL.json` self-report where no transcript witness exists, with `reasoning_output_tokens` entering C4 as a band — a pin nobody can check is a recorded intention, and the preregistration says so. |
| M-25 | **The witness-resolution step at pin time, as drafted**, settles the sweep's pin state; the sweep runs before the effort value exists and is registered accordingly. |

Rulings on the construct (M-18/M-26), the condition (M-8/M-20), and the amendment (M-15)
were put to the maintainer as explicit forks and answered 2026-08-23; the remainder adopt
the brief's recommendations as a block, so ruled and so recorded.

## M-14 verdict (2026-08-23, forensic read complete — a third mechanism, proven both ways)

Neither candidate. **One Rego language-semantics error — `"key" in object` tests values,
not keys — is the arm-B/C E1 collapse.** The presence test gating U1 (`"riskScore" in
input.vendor`) is false even when the member is present, so every input is judged
unreadable, the candidate sweep fires on every row, and the grid almost never collapses
to a singleton → `unresolved:[unknown]`. Evidence, bidirectional: run-011 reproduces
RESULTS.json exactly (31/86/0); repairing only that operator takes it to 117/117 and,
across all 40 affected runs, makes 26 perfect and improves 32; mutating the correct
idiom out of 8 perfect runs collapses 8/8 to the exact observed signature including the
`eval_conflict_error` pattern. Discriminator: 40 of 76 B+C policies use bare-object
`in` → zero perfect; all 22 perfect runs avoid it. The ROW-ERRORs are the same bug's
conflict face (B 94%, C 100% — and C's 89 are a single run), not a second mechanism.
Counterfactual E1 under this one repair: **B 0.267 → 0.800, C 0.467 → 0.767 — both hold
the 0.6 floor.** Three corrections to the brief's framing are recorded with it: run-011
carries zero ROW-ERRORs; arm C's are one run's; the dominant class is the all-unknown
collapse (25 of 37 failing runs).

**Design consequence, measured not argued:** neither of 020's planned repairs touches
this — the wire-form contract was already stated and followed, and the prompt's bundled
Rego reference already flags the exact trap (`"foo" in {"foo": 1} # false`) yet it fired
in 40 of 76 runs. More prose is demonstrated ineffective. The preregistration must
therefore decide an **engine-level or admission-level guard** (a lint-style presence-
idiom check, or a registered authoring-checklist admission step requiring
`object.keys`/`object.get(...) != null` for presence), registered with its own power
analysis; and the arm-A/arm-B asymmetry note belongs in the ledger — arm A's format has
no analogous single-operator trap on this surface, and its near-miss profile (92% row
accuracy, zero faults) stands unexplained by this mechanism. All of this is Tier-D
material: descriptive, direction-free, and no decision reads it.
