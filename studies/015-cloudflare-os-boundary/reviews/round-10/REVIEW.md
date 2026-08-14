# Round 10 review — verbatim

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, workspace-write
sandbox (scratch), study tree reviewed at commit 1ee1ca1. Verdict: DO-NOT-FREEZE on one
finding (R10-1, count-bound licences; R9-2 RESOLVED; Ruling 1 ACCEPTABLE, Ruling 2
LAWFUL). Dispositions: PREREG-REVIEW.md round-10 section; fix landed as b223a40.

---

R9-1 — NOT RESOLVED: The nine prose repairs are sound; FSTRING_MIDDLE extraction, joined runs with `\x00`, the 21-row 12/9 table, and the narrowed semantic scope check out. `verify.py`’s executable token stream and docstring-stripped AST are identical to its parent. However, licences are count-bound, not occurrence-bound; see R10-1.

R9-2 — RESOLVED: The manifest replaces exactly the six covered-file digests changed by `cb48421`; `1ee1ca1` touches only excluded review records, and `test_study_manifest_is_exact` passes.

Ruling 1 — ACCEPTABLE: The registered lexical narrowness plus semantic review loop is an honest closure model. Refusing bare `admits` or `produces` would reject legitimate apparatus vocabulary, and the asserted historical arithmetic correctly exposes rather than conceals the uncovered cases.

Ruling 2 — LAWFUL: `verify.py:887-902` states cited, source-level necessary constraints. Section 9 disclaims positive reachability of complete modeled histories, not derivation from pinned source. Those sentences need not be rewritten.

R10-1 — BLOCKER — Offending: `test_study.py:345-460,794-817,923-941`, especially the three-occurrence SPEC licence at `:399-408`. Contradiction: deleting the legitimate `retryability` header at `SPEC.md:68` and inserting `External state is not retryable.` within the unchanged anchor window preserves three matches; the real adjudicator returns `([], [])`. Thus a known forbidden formulation can replace an allowed occurrence despite the claim at `test_study.py:823-827` that reintroduction is mechanically impossible. Proposed fix: register one-to-one fingerprints for each licensed occurrence—surface, phrase, locator and exact normalized passage/context—and add this delete-one/add-one substitution regression.

do not freeze

The tree otherwise shows zero drift, exactly 198 tests collect, and all runnable checks passed; nine Node cases were blocked only by the known sandbox `spawnSync git EPERM`. But R10-1 is a direct surviving form of R9’s licence-shadowing blocker, so the occurrence identities must be fixed before freezing.

CODEX-015-R10-DONE
