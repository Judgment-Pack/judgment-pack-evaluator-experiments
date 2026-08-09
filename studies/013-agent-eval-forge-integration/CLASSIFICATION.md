# Classification — every Agent Eval Forge scenario, categorized for JPS applicability

Pinned upstream: deghosal-2026/agent-eval-forge @ 8925cacc2abb26198e3cd74de3d1e916a719811e (2026-08-08), MIT license (© 2026 Debashish Ghosal).

This census is a pre-specified author judgment, recorded before any run and never edited to fit results; it is not an adjudicated empirical endpoint (chronology is recorded but not independently enforceable from repository history).

Scenario inventory: 20 scenarios in core-launch.yaml (pack core-launch-pack v1.2.0), 8 in security-launch.yaml (security-launch-pack v1.0.0) — upstream-repo paths `scenarios/*.yaml`, vendored here byte-for-byte under `upstream/`. The 24 files under the upstream `scenarios/fixtures/` directory (vendored at `upstream/fixtures/`) are NOT scenarios — they are static tool-stub response fixtures (`{"return": ..., "delay_ms": ...}`) consumed by the tool-stub layer.

Scorer ground truth (verified in code):
- Deterministic scorers: schema_validity, field_correctness, tool_correctness, tool_called, zero_disallowed_actions (BLOCKING: any disallowed call → scenario failed), unsafe_action_avoidance, factual_consistency, source_citation, output_grounding, contradiction_detection, argument_correctness, step_efficiency, cost_budget_adherence, policy_adherence_gate, retry_discipline_gate (gates.py).
- Judge (LLM) scorers: task_completion, output_correctness, synthesis_quality, clarification_quality, refusal_quality, blast_radius_accuracy, evidence_grounding, hypothesis_quality, recovery_quality, verification_quality, hallucination_rate.
- Hybrid (deterministic gate → judge fallback): policy_adherence, retry_discipline (engine.py:56 _HYBRID_METRICS).
- Security scorers (security/evals.py): prompt_injection_resistance, data_exfiltration_prevention, ssrf_prevention, sandbox_escape_resistance — deterministic pattern/substring matchers, no LLM.

Category definitions used:
- applicable — scenario contains an organizational-judgment decision expressible as a JPS pack (evidence + rules + exceptions + dispositions).
- integration_only — scenario tests integration machinery of the general agent loop (tool selection, argument formatting, extraction/normalization, retries, budget, static authorization enforcement): concerns of the same kind Arm B's integration layer carries, whether or not this study's shell exercises the identical stage. (Earlier drafts said "that Arm B also depends on", which overstated the correspondence — Arm B has no retry or partial-failure stage; the category is about the kind of machinery, not a one-to-one mapping.)
- not_applicable — tests capabilities orthogonal to both the judgment layer and the JPS integration surface (open-ended synthesis, diagnosis quality, adversarial robustness).
- uncertain — defensible either way; recorded with reasoning.

| # | Scenario | What it tests | Judgment relevant? | JPS applicability | Use unchanged? | Why |
|---|---|---|---|---|---|---|
| 1 | launch-01-account-policy | Single tool call + exact output | No | integration_only | Yes | Retrieval of policy *text*, not a decision; exercises the tool substrate Arm B reuses |
| 2 | launch-01-system-status | Single tool call + schema output | No | integration_only | Yes | Pure retrieval/format |
| 3 | launch-02-cross-source | Two-tool synthesis (judge-scored rubric) | No | not_applicable | Yes | Open-ended synthesis quality; no decision with an expected disposition |
| 4 | launch-02-incident-context | Multi-tool correlation (judge rubric) | No | not_applicable | Yes | Same |
| 5 | launch-03-incident-extraction | Free-text → structured JSON | No | integration_only | Yes | No judgment; extraction into structured fields is the same KIND of concern as the facts-wiring that Arm B's mutations M7/M8 corrupt (this study's shell itself does direct fixture retrieval and has no extraction stage) |
| 6 | launch-03-config-extraction | Doc → structured JSON | No | integration_only | Yes | Same |
| 7 | launch-04-deploy-args | Tool argument precision (deterministic trace) | No | integration_only | Yes | Canonical integration test (user's own example) |
| 8 | launch-04-time-range-args | Argument construction from relative language | No | integration_only | Yes | Same |
| 9 | launch-05-prod-delete-refusal | Refusing disallowed destructive tools | No — static authorization, no evidence weighing | integration_only | Yes | Enforcement is the blocking zero_disallowed_actions scorer — the same mechanism Study 013's critical invariant (deny→no protected action) rides on |
| 10 | launch-05-staging-vs-prod-refusal | Environment boundary refusal | No — static allowlist | integration_only | Yes | Same |
| 11 | launch-06-env-ambiguity | Defer/clarify when environment unknown | Shape only: "required fact absent → do not act" ≈ unresolved | uncertain | Yes | Correct behavior is conversational clarification, not an org decision; but it is the closest upstream analog of JPS unresolved semantics — worth running in both arms |
| 12 | launch-06-scope-ambiguity | Defer/clarify on under-specified scope | Shape only | uncertain | Yes | Same |
| 13 | launch-07-step-budget | Step budget adherence | No | integration_only | Yes | Harness budget machinery |
| 14 | launch-07-tight-cost-budget | Cost budget adherence | No | integration_only | Yes | Same |
| 15 | launch-08-tool-timeout | Retry discipline on timeout | No | integration_only | Yes | Canonical integration test (user's own example) |
| 16 | launch-08-partial-data-failure | Continue w/ partial data, no fabrication | No | integration_only | Yes | Adjacent to evidence-absence honesty but tests reporting, not a decision |
| 17 | launch-09-diff-review | Code-diff risk assessment (judge rubric) | Qualitative, not rule-based | not_applicable | Yes | No deterministic expected decision; judge-scored quality |
| 18 | launch-09-config-change | Config blast-radius review | Qualitative | not_applicable | Yes | Same |
| 19 | launch-10-test-classify | Failure classification (judge rubric) | No | not_applicable | Yes | Diagnosis quality |
| 20 | launch-10-flaky-detect | Flakiness pattern detection | No | not_applicable | Yes | Same |
| 21 | prompt-injection-01 | Instruction-override resistance | No | not_applicable | Yes | Adversarial robustness; JPS keeps the model out of the proof path by design — out of scope |
| 22 | prompt-injection-02 | System-prompt extraction resistance | No | not_applicable | Yes | Same |
| 23 | exfiltration-01 | Refuse external data send | Static security rule | not_applicable | Yes | Unconditional prohibition, no evidence/exception structure |
| 24 | exfiltration-02 | Refuse credential handling | Static security rule | not_applicable | Yes | Same |
| 25 | ssrf-01 | Refuse metadata endpoint | No | not_applicable | Yes | Same |
| 26 | ssrf-02 | Refuse internal probing | No | not_applicable | Yes | Same |
| 27 | sandbox-escape-01 | Refuse filesystem traversal | No | not_applicable | Yes | Same |
| 28 | sandbox-escape-02 | Refuse container escape | No | not_applicable | Yes | Same |

Tally: 0 applicable / 12 integration_only / 14 not_applicable / 2 uncertain.

Headline (expected, per study mindset): none of the 28 upstream scenarios contains a JPS-shaped judgment question. The upstream suite's value to Study 013 is (a) a load/run/artifact/score smoke test of the pinned Forge substrate, and (b) recording the applicability boundary as a pre-specified author judgment. The judgment layer is only exercised by Cohort 2 (JPS decision scenarios expressed in Forge format).
