# Round 4 prompt — decide the two open limitations, and decide freezability

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed
(workspace-write in a scratch directory; the study tree and the pinned upstream clone are read by
absolute path and never written). Study tree reviewed at commit `73496c2`. The prompt below is
verbatim.

---

You are the round-4 pre-freeze cross-vendor adversarial reviewer for Study 015 in the
judgment-pack evaluator-experiments repository, checked out read-only at <repo>
(`studies/015-cloudflare-os-boundary/`). Rounds 1, 2 and 3 all returned DO-NOT-FREEZE (7, 5 and
4 blockers). You have no stake in it passing, and a study on its fourth round deserves more
scepticism, not less: heavy rework is itself a defect source, and a maintainer who has absorbed
three rounds may be converging on *plausible* rather than *correct*.

Your job has three parts, in this order.

**(A) Verify round 3's fixes are real, not re-described.** `PREREG-REVIEW.md`'s round-3 table
claims each of R3-1..R3-4 and the two residual majors is fixed, partially fixed, or open. Audit
every row against the code. Round 3's own text is at `reviews/round-3/REVIEW.md`. In particular:
- R3-1: the authorization *scope* is now claimed to be tool+resource, not the derived arguments,
  and not conditioned on executability. Can a call, application or effect against the governed
  tool/resource still escape the count — under an inaction commitment, with changed arguments,
  through a second gatekeeper, through a differently-rendered ledger row, or by any other route?
- R3-2: identifier uniqueness and ledger `resourceUrl`/`actionKind.label` corroboration are
  claimed. Are they actually enforced on every path that matters, and is the *declared*
  limitation (no unique call→effect lineage) stated where a reader would rely on it?
- R3-4: `pendingAt` is claimed to enforce strict lifecycle equivalence and attribution is claimed
  mandatory. Construct source-impossible ledger shapes and say whether each is refused, excluded,
  or accepted. Does SPEC §5 now actually contain the normative limitation paragraph the
  disposition says it does?

**(B) Decide the two limitations the study declared open rather than fixed.** For each, say
whether it is (i) acceptable to freeze with, provided it is registered as a non-claim; (ii) must
be fixed before freezing; or (iii) fatal to a claim the study makes elsewhere:
1. **No unique call→effect lineage.** Retained effect attestations carry no call or ledger
   identity, so `unbound-execution` is a cardinality argument. Is there a construction where
   correct cardinality coexists with a substituted or misattributed effect, and does any study
   claim depend on lineage the ceremony does not have?
2. **Fixtures are not constructed through the connector's real path.** The builder calls
   `describeCall` directly with reconstructed inputs (portal scope label, bare endpoint) rather
   than driving `gatekeeper-mcp-portal`'s facet/session path. Verify against pinned source
   whether the reconstructed inputs are exactly what that path supplies for this deployment, and
   whether any remaining fixture field is still not connector-producible. Is direct construction
   with verified inputs sufficient for what the study claims, or does the claim require the real
   path?

**(C) Decide freezability, explicitly.** If the study can freeze, say FREEZE and name anything
that must be corrected in the same commit. If not, give the blockers. Consider the whole record:
three prior rounds, a parallel self-audit that independently found several round-3 blockers, four
withdrawn study claims, and R1's standing as a *locked regression endpoint* with the prospective
content in the reviewer-authored holdout.

Read at minimum: `PREREGISTRATION.md`, `adapter/SPEC.md`, `adapter/verify.py`,
`adapter/commitment.py`, `harness/score.py`, `harness/build_fixtures.py`, `harness/typecheck.py`,
`probes/*.ts`, `harness/tests/*.py`, `harness/MATRIX.json`, `harness/MATRIX-HOLDOUT.json`,
`harness/PINS.json`, `PREREG-REVIEW.md`, `DEVIATIONS.md`, `README.md`, and all three prior
reviews. Upstream ground truth: the pinned clone at <upstream> (commit b2a51b5), especially
`packages/gatekeeper-mcp-portal/`, `packages/mcp-shared/` and
`packages/workshop-backend/src/overseer.ts`.

Also check, because churn breeds these: dead code, documents contradicting each other or the
implementation, tests asserting less than their names claim, registry expectations that drifted
from their constructions, and any claim in `README.md` or PREREGISTRATION §9 that 27 cells cannot
support.

Do not execute anything; static review only. Do not author holdout cells unless you find a gap
the existing eight do not cover, and mark any you write as round-4 authored.

Write your review as:
1. verdict: FREEZE / FREEZE-AFTER-CHANGES / DO-NOT-FREEZE
2. audit of round 3's six dispositions: real / partial / cosmetic / wrong, with reasons
3. your decision on each of the two open limitations, with reasoning
4. numbered new findings with severity, exact file and claim, and remedy
5. anything you checked and found sound
6. one paragraph: what a reader may legitimately conclude from this study if it freezes as-is

End with the literal line: CODEX-015-R4-DONE
