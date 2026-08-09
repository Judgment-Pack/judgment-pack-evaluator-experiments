You are the cross-vendor adversarial reviewer for a pre-freeze preregistration review (round 1) of Study 013 in the judgment-pack-evaluator-experiments repository. Your working directory is the study: studies/013-agent-eval-forge-integration.

Your task: try to break PREREGISTRATION.md as a governing document before it freezes. Read it fully, plus README.md, CLASSIFICATION.md, UPSTREAM.md, scenarios/mutations/MATRIX.json, scenarios/jps/cases.json, harness/PINS.json, and inspect harness/*.py and agents/*.py as needed to verify that the prereg's descriptions match the code. The pilots under pilots/ are harness validation; you may consult them to check that numbers quoted in the docs match retained artifacts.

Probe specifically:
1. R1's falsifiability and the §5 decision rule: is every outcome covered, is "pipeline-invalid" exploitable as an escape hatch, can a divergence be argued away after the fact?
2. Circularity: the goldens are produced by the same pinned evaluator Arm B runs; the oracle decider reads the registered expectations; layer G uses the study's own mapper to define expected actions. Which of these are legitimate by design and which threaten the claim — and does the prereg say so honestly?
3. Detection-layer definitions J/F/G: crisp enough that an observed detection cannot be re-attributed after the fact?
4. The registered-invisible matrix cells (m02/f01, m08/t04, m08/t08): is reporting them as findings sound?
5. Pins: anything material left unpinned (transitive venv deps, the driver's own behavior, prompt fixtures for the gated RQ3 phase)?
6. Collision with Study 012 as described: any overlooked overlap?
7. Claims/non-claims: any sentence a hostile reader could quote as an efficacy or conformance claim?
8. Cohort 1's endpoint: is "integration validation" operationalized or is it vibes?
Also flag outright errors: file references that do not exist, numbers that do not match retained artifacts, code/doc mismatches.

Output: numbered findings, each with severity (BLOCKER / MAJOR / MINOR / NOTE), file and section, the problem in one or two sentences, and a concrete suggested change. Do not pad the list with things that are fine. End with a one-paragraph verdict: is this preregistration freezable once the findings are addressed, and which findings must land before freeze. Do not modify any files.
