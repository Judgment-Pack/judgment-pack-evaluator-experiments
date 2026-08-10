# Round 3 prompt — post-rebuild adversarial review

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed
(workspace-write in a scratch directory; the study tree and the pinned upstream clone are read by
absolute path and never written). Study tree reviewed at commit `bc28d9c`. The prompt below is
verbatim.

---

You are the round-3 pre-freeze cross-vendor adversarial reviewer for Study 015 in the
judgment-pack evaluator-experiments repository, checked out read-only at <repo>
(`studies/015-cloudflare-os-boundary/`). Rounds 1 and 2 both returned DO-NOT-FREEZE (7 and 5
blockers). The study has been rebuilt twice. Your review decides whether it can now freeze. You
have no stake in it passing, and you should be more suspicious, not less, of a study that has
been reworked this heavily — churn creates defects.

Start from `PREREG-REVIEW.md`, which now claims a disposition for all 14 round-1 findings and all
11 round-2 findings. **Audit the round-2 table specifically**: for each of its 11 rows, is the fix
real, complete, and correctly described, or cosmetic, partial, or newly broken? Round 2 marked
three round-1 dispositions "wrong"; check whether the round-3 state has actually repaired those
or merely re-described them.

Note what the study claims to have done since round 2:
- **Blocker 1**: subject identity for cardinality is now the tool, resource and exact arguments
  the map *derives*, not a store-chosen digest label; `unbound-execution` counts effects against
  authorized applications; `serverTrust` became derived.
- **Blocker 2**: the whole scenario was re-rendered at the pinned **MCP Portal** connector
  (`MCP_PORTAL_TRUST_ANNOTATIONS=true`), on the finding that the generic connector hardwires
  `byo` and cannot host an auto-approvable write. Identifiers, action-kind tags, `describeCall`
  prose, `awaitDecision` and explicit `autoApprovable` are claimed to be what that connector
  emits.
- **Blocker 3**: the drain verdict is narrowed to *consistency with a self-asserted witness*,
  with the queue reconstructed from ledger timestamps; `pendingAt` now refuses unusable or
  contradictory stamps; attribution is compared against the pinned drainer's own.
- **Blocker 4**: the evidence-backing claim is narrowed to *retained-preimage consistency*, with
  the laundering limitation stated in code and in the SPEC.
- **Blocker 5**: the holdout has its own typecheck scope, gate, runner batch and verdict, and is
  mandatory once frozen.
- `simulationBasis` and its verdict code were **removed entirely**.

Read, at minimum: `PREREGISTRATION.md`, `adapter/SPEC.md`, `harness/MATRIX.json`
(27 cells, `matrixVersion` 3), `harness/MATRIX-HOLDOUT.json` and
`reviews/round-1/MATRIX-HOLDOUT.authored.json`, all of `adapter/`, `harness/` and `probes/`,
`harness/PINS.json` (which now classifies every member as SCORER/CI/DESCRIPTIVE), `README.md`,
`DEVIATIONS.md`, the four retained pilots, and both prior reviews under `reviews/`.
For upstream ground truth use the pinned clone at <upstream> (commit b2a51b5).

Attack, at minimum:
1. **The re-rendered scenario.** Verify against `gatekeeper-mcp-portal/` that the registered
   resource URL, wire tool names, action-kind tags, and every `ActionDescription` field are what
   that connector actually emits — including the fixtures' `describeCall` prose byte-for-byte and
   the portal's binding/grant model. Is the portal genuinely configurable to `vetted` in a way a
   real deployment could reach? Does any fixture still contain a shape no connector produces?
2. **The derivation oracle after the change.** Can a coherent store writer still produce an
   accepted history whose executed action is not the authorized one — via arguments the map
   derives but the store renders differently, a second gatekeeper, a call the subject filter
   misses, or effects that evade the counting?
3. **Removal damage.** `simulationBasis` was deleted from the schema, the checks and the
   fixtures. Did that leave a hole (e.g. a staged call's own basis field now unchecked, or a
   holdout cell whose construction assumed it)?
4. **The narrowed claims.** Are they narrowed *everywhere*, or does an old strong form survive in
   some document? Specifically the drain verdict, evidence backing, "every non-null pin", the
   typecheck surface, and any residual platform-endorsement language.
5. **The holdout.** Is the isolation now airtight (typecheck scope, gate, runner batch, verdict,
   and the mandatory-once-frozen rule)? Are the constructions still faithful to the authored
   prose? Is the disclosed `h08` adaptation handled honestly?
6. **New defects from churn.** The study has been rewritten twice; look for dead code,
   contradictions between documents, tests that assert nothing, expectations that drifted from
   constructions, and stale citations. Check the SPEC's numbered ceremony against the
   implementation order and the registry's counts against the actual cells.
7. **Claim discipline overall.** README + PREREGISTRATION §9 against what 27 cells can support.

Then answer: **can this freeze?** If yes, say so explicitly and name anything that must be
corrected in the same commit. If no, give the blockers. If you author additional holdout cells,
keep them disjoint from both strata and mark them round-3 authored; do not revise the round-1
holdout. Do not execute anything; static review only.

Write your review as:
1. verdict: FREEZE / FREEZE-AFTER-CHANGES / DO-NOT-FREEZE
2. an audit table of the 11 round-2 dispositions: real / partial / cosmetic / wrong, with reasons
3. numbered new findings with severity, exact file and claim, and remedy
4. anything you checked and found sound
5. an explicit statement of what a reader may conclude from this study if it freezes as-is

End with the literal line: CODEX-015-R3-DONE
