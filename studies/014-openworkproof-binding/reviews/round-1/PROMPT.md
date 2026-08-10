# Round 1 prompt — pre-freeze adversarial review

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol, reasoning effort ultra, read-only sandbox.
Working directory: the evaluator-experiments checkout. The prompt below is verbatim.

---

You are the pre-freeze cross-vendor adversarial reviewer for Study 014 in this repository
(`studies/014-openworkproof-binding/`). Your review decides whether the preregistration
can freeze. You have no stake in the study passing; your job is to find the ways it could
mislead, overclaim, or be gamed, before it becomes governing.

Study question: can an independently developed execution-verification protocol
(OpenWorkProof) bind an executed action to the exact JPS judgment that authorized it,
strongly enough that an offline third party detects substitution, drift, replay, and
execution mismatch — with every detection attributable to exactly one layer (OWP verifier
unchanged / adapter binding / pinned-evaluator replay)?

Read, at minimum:
- `studies/014-openworkproof-binding/PREREGISTRATION.md` (the registered protocol,
  including the [D-1]..[D-4] decision register addressed to you)
- `studies/014-openworkproof-binding/adapter/SPEC.md` (commitment schema, two binding
  points, verification ceremony with exact verdict codes, disposition-to-action map)
- `studies/014-openworkproof-binding/harness/MATRIX.json` (37 registered cells with
  per-layer expectations; two registered expected-undetected)
- `studies/014-openworkproof-binding/harness/PINS.json`, `README.md`, `DEVIATIONS.md`
- The adapter and harness code: `adapter/commitment.py`, `adapter/verify.py`,
  `harness/owpflow.py`, `harness/build_fixtures.py`, `harness/score.py`,
  `harness/run_verify.py`, `harness/tests/test_study.py`
- The two retained pilots under `pilots/` (pilot-01 recorded a falsified registry
  expectation, corrected pre-freeze; pilot-02 is green)
- For upstream ground truth: the pinned OpenWorkProof clone at
  /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/f2eafbc8-b181-4342-a4eb-57c608f6db04/scratchpad/OpenWorkProof
  (commit 8eeca6f; models.py, signing.py, policy.py, acceptance.py, evidence.py,
  composition.py) — verify claims about OWP against its source, not the study's prose.
- For repo convention: `studies/013-agent-eval-forge-integration/` (the previous study
  under this regime) and `.github/workflows/ci.yml`.

Attack, at minimum:
1. Endpoint gaming: can R1 "hold" while the binding is actually weak? Are the registered
   expectations self-fulfilling anywhere (the same code path authoring fixtures and
   verdicts)? Is the validity/detection channel separation real in `score.py`?
2. The commitment schema: missing fields whose absence hides an attack; fields bound
   without justification; digest/canonicalization mistakes (JCS vs exact-bytes conventions
   are mixed by design — is every boundary correct?).
3. The ceremony: ordering exploits (first-failure-wins hiding a second, worse failure);
   the a04-tampered lesson generalized — are other registered codes unreachable under the
   implemented order?
4. The disposition-to-action map and its totality clause ([D-2]): is `manual-review`
   registered non-executable defensible, and does any C-cell attribution depend on it?
5. The resigned-variant threat model: the study holds all six work-order keys. Which
   claims silently depend on the attacker NOT holding a key, and is that stated?
6. The two expected-undetected cells (e18, e22) and [D-3]: is registering them undetected
   honest boundary-mapping or an excuse? Could a cheap additional commitment catch them,
   and would adding it change the study's claim?
7. Upstream fidelity: does `harness/owpflow.py` build chains a real OWP deployment could
   have produced, or fixture-shaped ones that flatter the verifier? Check the recorded
   constructibility refusals (e21, f23, f25) against OWP source.
8. Claim/non-claim discipline: README + PREREGISTRATION §9 versus what the matrix can
   actually support; any place "binding/lineage, not truth" slips.
9. Determinism and integrity machinery: build-time entropy pin (PINS
   `buildTimeEntropyPin`), manifest coverage, the SPEC/code vocabulary sync test — can
   any of it be satisfied vacuously?
10. The [D-1] and [D-4] register items.

Output format, exactly:
- Numbered findings `R1-<n>`, each with severity BLOCKER / MAJOR / MINOR, the file and
  section, the failure mode in one paragraph, and a concrete fix.
- Then explicit answers to [D-1]..[D-4].
- Then a one-line verdict: `freezable as written`, `freezable after listed fixes`, or
  `not freezable as written`.
Do not summarize the study back to me; findings only. Verify before asserting: every
claim about code or upstream behavior must cite a path (and line where useful) you read.
