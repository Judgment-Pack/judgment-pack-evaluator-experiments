# Round 2 prompt — post-rebuild adversarial review

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, sandboxed
(workspace-write in a scratch directory; the study tree and the pinned upstream clone are read by
absolute path and never written). Working commit recorded with the round output. The prompt below
is verbatim.

---

You are the round-2 pre-freeze cross-vendor adversarial reviewer for Study 015 in the
judgment-pack evaluator-experiments repository, checked out read-only at <repo>
(`studies/015-cloudflare-os-boundary/`). Round 1 returned DO-NOT-FREEZE with 7 blockers and 6
majors; the study has been rebuilt around them. Your review decides whether the preregistration
can now freeze. You have no stake in the study passing.

Start from [`PREREG-REVIEW.md`](PREREG-REVIEW.md), which claims a disposition for every round-1
finding. **Your first job is to audit those claims**: for each of the 14 rows, decide whether the
fix is real, complete, and correctly described, or whether it is cosmetic, partial, or has
introduced a new defect. Three rows claim that independent source verification *corrected the
reviewer* or *refuted the study's own earlier finding* — check those against the pinned source
yourself and say plainly if the study is wrong.

Note in particular:
- the study withdrew its own recorded "backend typecheck is not reproducible" finding after
  running the compiler, and now binds fixtures to the server-side `ActionRecord`;
- it withdrew the `d01` endpoint as not source-reachable (the pinned MCP connector opts out of
  simulation and sets `awaitDecision: true`), keeping `simulationBasis` registered but exercised
  by no endpoint;
- it replaced final-snapshot drain replay with a **stage-time witness** plus a queue
  reconstruction from the ledger's own timestamps, on the argument that `appliedAt` is a
  resolution stamp set on both approve and reject;
- it added an independent derivation oracle so the ceremony no longer trusts the bridge's own
  commitment for the action's identity.

Read, at minimum: `PREREGISTRATION.md`, `adapter/SPEC.md` (especially §0a's provenance table and
§5's ordering), `harness/MATRIX.json` (27 cells, `matrixVersion` 2), `harness/MATRIX-HOLDOUT.json`
and `reviews/round-1/MATRIX-HOLDOUT.authored.json` (the reviewer's authored file, preserved), the
adapter and harness code (`adapter/commitment.py`, `adapter/verify.py`, `harness/score.py`,
`harness/build_fixtures.py`, `harness/typecheck.py`, `harness/cf_runner.py`, `probes/*.ts`,
`harness/tests/*.py`), `harness/PINS.json`, `README.md`, `DEVIATIONS.md`, and the retained pilots.
For upstream ground truth use the pinned clone at <upstream> (commit b2a51b5) — verify every claim
about the platform against its source, not the study's prose.

Attack, at minimum:
1. **The derivation oracle.** It is now the study's central defence. Can a coherent store writer
   still produce an accepted history whose action is not the one the judgment authorizes? Is the
   derived/contextual split correct — is anything in `CONTEXTUAL_ACTION_FIELDS` actually derivable,
   or anything in `DERIVED_ACTION_FIELDS` not?
2. **The stage-time witness.** It is retained instrumentation the platform does not keep, and the
   attacker controls the store. Can a witness be forged consistently with the ledger's timestamps
   so an unlawful drain replays clean? Is the pendingness reconstruction (`createdAt <= t` and not
   resolved at `t`) actually sound against the pinned drainer, including the `continue` branch and
   multi-pass/single-flight behaviour?
3. **Evidence backing.** Retaining artifacts gives the digest a preimage. Does that actually
   defeat the round-1 laundering attack, or merely move it (e.g. retain the approval bytes *as*
   the artifact)? Is the study's claim about what backing does and does not establish still exact?
4. **`not-engaged` and the upstream layer's honesty.** Is the renaming substantive or cosmetic?
   Can `upstream: pass` still be misread as platform endorsement anywhere in the documents?
5. **Suppressed codes.** Adjudication is still on the first code. Does publishing the rest
   actually cure the round-1 concern, or does the *choice of order* still determine what a reader
   sees as the finding?
6. **The holdout.** Fixtures are now constructed pre-freeze from reviewer prose written before
   those fixtures existed. Is any construction a misreading of the authored text, or built in a
   way that biases its outcome? Is the mechanical migration (`cf`→`upstream`, `pass`→`not-engaged`)
   defensible, or does it revise an expectation? Is the separation from R1 airtight?
7. **The provenance table (SPEC §0a).** Check it row by row against pinned source. Anything
   overstated as stock-observable, or understated as instrumentation?
8. **New surface, new defects.** The rebuild added ~5 verdict codes, 4 cells, and a new retained
   artifact. Are the new codes reachable only through the implemented order? Do the two new
   controls actually prove what they claim? Does anything the rebuild introduced create a fresh
   gaming path?
9. **Claim discipline after the rewrite.** README + PREREGISTRATION §9 versus what the 27 cells
   can support; the corrected validation claim; anywhere a platform-runtime claim sneaks back in.

Then answer [D-6], [D-7] and [D-8] in the preregistration's decision register.

If — and only if — you judge the study freezable, say so explicitly. If you author additional
holdout cells, keep them disjoint from both existing strata and note that they are round-2
authored; do not revise the round-1 holdout. Do not execute anything; static review only.

Write your review as:
1. verdict: FREEZE / FREEZE-AFTER-CHANGES / DO-NOT-FREEZE
2. an audit table of the 14 round-1 dispositions: real / partial / cosmetic / wrong, with reasons
3. numbered new findings, each with severity, exact file and claim, and remedy
4. answers to [D-6]..[D-8]
5. anything you checked and found sound

End with the literal line: CODEX-015-R2-DONE
