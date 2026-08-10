# Round 5 prompt — confirm round 4's closures, and decide freezability

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed. Study tree
reviewed at commit `2ad43ed`. The prompt below is verbatim.

---

You are the round-5 pre-freeze cross-vendor adversarial reviewer for Study 015 in the
judgment-pack evaluator-experiments repository, checked out read-only at <repo>
(`studies/015-cloudflare-os-boundary/`). Rounds 1–4 returned DO-NOT-FREEZE with 7, 5, 4 and 4
blockers. All of round 4's are now claimed closed. You have no stake in it passing; a study on
its fifth round has had many chances to converge on *plausible* rather than *correct*, and your
job is to tell those apart.

**(A) Verify round 4's closures.** `PREREG-REVIEW.md`'s round-4 table claims each of R4-1..R4-6
fixed, mostly fixed, or open. Round 4's own text is at `reviews/round-4/REVIEW.md`. Audit each:

- **R4-1 (governed inventory).** Calls, ledger applications and effects are claimed to share one
  tool/resource-scoped inventory, with applications inventoried from the ledger itself. Can any
  governed call, application or effect still escape — under inaction, with changed arguments,
  via a second gatekeeper, via an orphan row, via duplicate identities, or otherwise?
- **R4-4 (lineage).** Effect attestations now carry `gatekeeperId`/`action` and
  `unbound-execution` joins on that identity. Is the substituted-causation construction really
  refused now? Is the identity itself forgeable in a way that matters, and is its instrumentation
  status stated where a reader would rely on it?
- **R4-2 (lifecycle).** A new binding code `ledger-lifecycle-invalid` is claimed to validate every
  action record's lifecycle tuple for every cell. Work through your own round-4 table of nine
  accepted shapes and say which are now refused and which still pass. Two remedies are declared
  still open (witness schema validation; joining the real private connector row) — confirm they
  are declared where it matters and not implied to be done.
- **R4-3 (fixtures).** Every ledger row's prose is claimed generated from its own tool and
  arguments; `b04`/`h04` are claimed to use a second portal deployment with its own scope and
  wire tool; `o01` is claimed to carry a genuine read-path observation; obstruction calls carry
  `rejected`; manual approvals store `autoApproved:false`. Verify each against pinned source, and
  in particular verify that `h03` and `h04` are now faithful to the reviewer-authored prose in
  `reviews/round-1/MATRIX-HOLDOUT.authored.json` **without** their registered expectations having
  been touched.
- **R4-5 / R4-6.** Wording items. Are the remaining absolutes now true, or still false?

**(B) Attack the new surface.** The rebuild added a verdict code, an effect identity, a connector
outcome value, a second portal deployment, and regenerated every fixture. Look for: dead code;
documents contradicting the implementation; the SPEC's numbered ceremony versus `BINDING_CHECKS`;
registry expectations drifted from constructions; tests asserting less than their names claim;
and any new gaming path the identity join or the ledger-scoped application inventory opens.

**(C) Decide freezability, explicitly.** If it can freeze, say FREEZE and name anything that must
be corrected in the same commit. If not, give the blockers and say plainly whether you believe
they are convergent (each round narrower) or whether the study has a structural problem that more
rounds will not fix. That judgement is the most useful thing you can give.

Read at minimum: `PREREGISTRATION.md`, `adapter/SPEC.md`, `adapter/verify.py`,
`adapter/commitment.py`, `harness/score.py`, `harness/build_fixtures.py`, `harness/typecheck.py`,
`probes/*.ts`, `harness/tests/*.py`, `harness/MATRIX.json`, `harness/MATRIX-HOLDOUT.json`,
`reviews/round-1/MATRIX-HOLDOUT.authored.json`, `harness/PINS.json`, `PREREG-REVIEW.md`,
`DEVIATIONS.md`, `README.md`, and all four prior reviews. Upstream ground truth: the pinned clone
at <upstream> (commit b2a51b5).

Do not execute anything; static review only.

Write your review as:
1. verdict: FREEZE / FREEZE-AFTER-CHANGES / DO-NOT-FREEZE
2. audit of round 4's six dispositions: real / partial / cosmetic / wrong, with reasons
3. numbered new findings with severity, exact file and claim, and remedy
4. convergent or structural — your judgement, with reasoning
5. one paragraph: what a reader may legitimately conclude from this study if it freezes as-is

End with the literal line: CODEX-015-R5-DONE
