# Round-2 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-11. Verdict: **DO NOT FREEZE** (3 RESOLVED, 9 PARTIALLY RESOLVED, 1 NOT RESOLVED, 1 new MAJOR + 1 new MINOR; 10-cell holdout set authored).

> Note: citations normalized from absolute worktree paths; the finding prose is otherwise verbatim.

## Confirmation

- R1-1 — PARTIALLY RESOLVED — Integrity/availability failures now produce `transition-unavailable` and cannot compose to `usable`; however, authenticated nonmembership for a never-bound digest under `position-window` still returns and composes to `usable`. [transition.py], [run_verify.py]
- R1-2 — PARTIALLY RESOLVED — Cited-prefix membership now calls the pinned upstream fold, but the decision logic still contradicts it: the reinstated real binding cited at position 5 is labeled unsupported, while a never-bound digest is `usable`. [transition.py], [verify_currency.py], [transition.py]
- R1-3 — RESOLVED — Holdout validation, comparison, output names, and divergence channels now use exactly nullable `citedPosition`/`retiredAtPosition` and `transition:<field>`. [score.py]
- R1-4 — PARTIALLY RESOLVED — The rule and verdict detail are accurately renamed and narrowed, but the executable usage example still names nonexistent `div-run-to-expiry`, so the rename is not throughout. [SPEC.md], [transition.py], [run_verify.py]
- R1-5 — PARTIALLY RESOLVED — The creation-time code is gone, but the SPEC still defines its replacement only as an at/after-departure condition, and the evaluator emits it for a reinstated position the upstream fold says is supported. [SPEC.md], [transition.py]
- R1-6 — PARTIALLY RESOLVED — The analytic limitation is present, but the rejected ownership, placement, “picking is not its job,” and “measures both” conclusions remain elsewhere. [PREREGISTRATION.md], [README.md], [SPEC.md]
- R1-7 — PARTIALLY RESOLVED — Exact window-form validation and rejection vectors are fixed, but the false claim that rules are configuration rather than hard-coded paths remains. [transition.py], [test_transition.py], [SPEC.md]
- R1-8 — RESOLVED — The backdated alias is registered byte-identical, classified descriptive, and excluded from R1 and endpoint totals. [MATRIX.json], [MATRIX.json], [score.py]
- R1-9 — RESOLVED — The mint-time duplicate is registered as a non-counted demonstration; a manifest-hash scan found all 11 remaining endpoint tuples unique. The only additional equality is the explicitly declared control copy `pos-current-stop`/`unchanged`. [MATRIX.json], [STUDY-MANIFEST.sha256], [build_fixtures.py]
- R1-10 — PARTIALLY RESOLVED — Structured evidence now affects `decide()`, but formal R1 still names only layer outcomes and the renderer still publishes stale Study 017 witness triples instead of transition positions. [PREREGISTRATION.md], [score.py], [score.py], [DETECTION-MATRIX.md]
- R1-11 — PARTIALLY RESOLVED — The matrix now states four configured evaluations, three exact outcomes, two permits and two refusals, but the README still promises “four different” usability answers. [MATRIX.json], [README.md]
- R1-12 — RESOLVED — The test now compares every cell file, including `citation.json`, and asserts the exact difference set is `{ruleconfig.json}`. [test_study.py], [build_fixtures.py]
- R1-13 — NOT RESOLVED — The builder still hard-codes the seed label, scoring accepts any nonempty replacement without fixture-key correspondence, and PINS still calls `checkpoint.py` build-path-only while scoring loads it with `build=True`. [build_fixtures.py], [score.py], [PINS.json]

## New findings

- R2-1 — MAJOR — `rule/SPEC.md` §§3–4; `rule/transition.py` stop-at-retirement branch — Every authenticated exact-tuple nonmembership becomes `not-usable-version-retired`, although Study 016 establishes only nonmembership: a wrong digest for a currently supported version and a never-seen version both receive the false retirement code. Rename the rule/code to snapshot nonmembership, or require prefix evidence of prior exact support and departure and add a separate never-supported code; register wrong-digest and never-seen controls. [transition.py], [Study 016 SPEC.md]
- R2-2 — MINOR — `PREREGISTRATION.md` §§1a, 4 — The preregistration still registers 18 cells, four positive controls, one negative control and 13 endpoints; the current matrix/pilot has 19 cells, six control gates, 11 endpoints, one descriptive cell and one demonstration. Reconcile the counts and add a role-count consistency assertion derived from the matrix. [PREREGISTRATION.md], [RESULTS.json]

## Holdout set (authored by the round-2 reviewer)

```json
{
  "reviewer": "codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), round 2",
  "cells": [
    {
      "id": "h01",
      "category": "G-currency-gate-and-multicycle",
      "variant": "registry",
      "role": "control-gate",
      "attackerCapability": "none",
      "registeredAbsences": [
        "citation"
      ],
      "construction": "Using the pinned Study 016 registry writer, the authority derived from PINS.json registryAuthority.authoritySeedLabel, build_fixtures.SERIES_ID, DIGEST_A and DIGEST_B, build [add 4.0.0/DIGEST_A, add 9.0.0/DIGEST_B, retire 4.0.0, reinstate 4.0.0, retire 4.0.0, add 10.0.0/DIGEST_B, reinstate 4.0.0], using build_fixtures.event defaults. Retain the full position-7 snapshot and a SERIES_ID trust configuration pinned to that authority and head 1; commit to (SERIES_ID, 4.0.0, DIGEST_A), omit citation.json, and configure stop-at-retirement with both window fields null.",
      "expected": {
        "currency": "pass",
        "transition": "usable"
      },
      "note": "All-pass brittleness control: the upstream fold makes the twice-reinstated immutable binding current, while a rule that does not read a citation tolerates its registered absence and publishes citedPosition=null, retiredAtPosition=null (../016-policy-currency-anchor/registry/SPEC.md §§1,3; rule/transition.py stop-at-retirement branch)."
    },
    {
      "id": "h02",
      "category": "G-currency-gate-and-multicycle",
      "variant": "tampered",
      "role": "endpoint",
      "attackerCapability": "tamper",
      "registeredAbsences": [
        "citation"
      ],
      "construction": "Construct h01, then in retained snapshot.json change only attestation.signature's first character to the next character modulo the standard base64 alphabet \"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/\"; leave its signed payload, all checkpoints, commitment, trust configuration, absent citation and stop-at-retirement configuration unchanged.",
      "expected": {
        "currency": "fail:snapshot-signature-invalid",
        "transition": "unavailable"
      },
      "note": "The citation-independent stop rule cannot turn an unauthenticated but otherwise current multi-cycle view into usable; the currency gate fires first and publishes citedPosition=null, retiredAtPosition=null (../016-policy-currency-anchor/registry/SPEC.md §3 step 4; rule/transition.py ADJUDICABLE_CURRENCY gate)."
    },
    {
      "id": "h03",
      "category": "F-upstream-fold",
      "variant": "registry",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use h01's unmodified full position-7 history, snapshot and trust configuration, but commit to version 4.0.0 with digest \"sha256:\" + SHA-256(UTF-8 \"018/round-2-holdout-never-bound\"); retain a SERIES_ID citation to head 4 and configure position-window with windowPositions=10 and windowDuration=null.",
      "expected": {
        "currency": "fail:not-current-at-snapshot",
        "transition": "not-usable:not-usable-cited-state-not-supported"
      },
      "note": "Reinstatement restores only the digest originally bound by add: the never-bound tuple remains unsupported at citedPosition=4 with retiredAtPosition=null, and “never entered” must not be treated as “never left” (../016-policy-currency-anchor/registry/SPEC.md §1; ../016-policy-currency-anchor/registry/verify_currency.py fold_supported; rule/SPEC.md §3)."
    },
    {
      "id": "h04",
      "category": "F-upstream-fold",
      "variant": "registry",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Using the registered authority, SERIES_ID, DIGEST_A and DIGEST_B, build H=[add 7.0.0/DIGEST_A, retire 7.0.0, add 20.0.0/DIGEST_B, reinstate 7.0.0, retire 7.0.0, reinstate 7.0.0, add 21.0.0/DIGEST_B, retire 7.0.0, add 22.0.0/DIGEST_B, add 23.0.0/DIGEST_B, add 24.0.0/DIGEST_B], using build_fixtures.event defaults. Retain the full position-11 snapshot and matching SERIES_ID trust configuration, commit to (7.0.0, DIGEST_A), cite head 6, and configure grandfather-on-cited-support.",
      "expected": {
        "currency": "fail:not-current-at-snapshot",
        "transition": "usable"
      },
      "note": "A cited prefix reached by a second reinstatement is supported even after a later departure, while structured evidence reports citedPosition=6 and the most recent retiredAtPosition=8 (../016-policy-currency-anchor/registry/verify_currency.py fold_supported; rule/transition.py _supported_at/_left_position and grandfather branch)."
    },
    {
      "id": "h05",
      "category": "F-upstream-fold",
      "variant": "citation",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use exactly h04's commitment, full position-11 H snapshot, trust configuration and grandfather-on-cited-support configuration; change only citation.json to cite head 5, the retired gap between the reinstatements at positions 4 and 6.",
      "expected": {
        "currency": "fail:not-current-at-snapshot",
        "transition": "not-usable:not-usable-cited-state-not-supported"
      },
      "note": "The immutable binding is absent during that retired gap, so the exact refusal is cited-state-not-supported with citedPosition=5 and the full history's most recent retiredAtPosition=8 (../016-policy-currency-anchor/registry/SPEC.md §1; rule/transition.py grandfather branch)."
    },
    {
      "id": "h06",
      "category": "W-position-window",
      "variant": "config",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use exactly h04's commitment, full position-11 H snapshot, trust configuration and head-6 citation; configure position-window with windowPositions=3 and windowDuration=null.",
      "expected": {
        "currency": "fail:not-current-at-snapshot",
        "transition": "usable"
      },
      "note": "The positional window is inclusive at its bound: 11-8=3 positions elapsed since the most recent departure, so a window of 3 permits and publishes citedPosition=6, retiredAtPosition=8 (rule/SPEC.md §§3,5; rule/transition.py position-window branch)."
    },
    {
      "id": "h07",
      "category": "W-position-window",
      "variant": "config",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use byte-identical commitment, full position-11 H snapshot, trust configuration and head-6 citation from h06; change only ruleconfig.json from windowPositions=3 to windowPositions=2, retaining windowDuration=null.",
      "expected": {
        "currency": "fail:not-current-at-snapshot",
        "transition": "not-usable:not-usable-window-elapsed"
      },
      "note": "With the same most-recent-departure evidence, three elapsed positions exceed a window of 2, so only the configured bound changes the result; evidence remains citedPosition=6, retiredAtPosition=8 (rule/SPEC.md §§3,5; rule/transition.py position-window branch)."
    },
    {
      "id": "h08",
      "category": "S-per-series-discipline",
      "variant": "registry",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Using one registered authority, build [SERIES_ID:add 20.0.0/DIGEST_B, OTHER_SERIES_ID:add 7.0.0/DIGEST_A, OTHER_SERIES_ID:retire 7.0.0, SERIES_ID:add 7.0.0/DIGEST_A, OTHER_SERIES_ID:reinstate 7.0.0, SERIES_ID:retire 7.0.0]. Retain the full position-6 snapshot; make the trust configuration, commitment and grandfather-on-cited-support rule all name SERIES_ID; make the SERIES_ID citation point to global head 2.",
      "expected": {
        "currency": "fail:not-current-at-snapshot",
        "transition": "not-usable:not-usable-cited-state-not-supported"
      },
      "note": "An identical tuple added for another series at the cited prefix does not support SERIES_ID; the target-series binding enters at 4 and leaves at 6, yielding citedPosition=2, retiredAtPosition=6 (../016-policy-currency-anchor/registry/SPEC.md §§2-3; ../016-policy-currency-anchor/registry/verify_currency.py fold_supported; rule/transition.py _supported_at)."
    },
    {
      "id": "h09",
      "category": "G-currency-gate-and-series",
      "variant": "registry",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [
        "citation"
      ],
      "construction": "Build a three-event snapshot [OTHER_SERIES_ID:add 7.0.0/DIGEST_A, OTHER_SERIES_ID:retire 7.0.0, OTHER_SERIES_ID:reinstate 7.0.0] under the registered authority. Pin its authority and genesis in a trust configuration for SERIES_ID, commit to (SERIES_ID, 7.0.0, DIGEST_A), omit citation.json, and configure SERIES_ID stop-at-retirement with both window fields null.",
      "expected": {
        "currency": "fail:series-unknown-at-snapshot",
        "transition": "unavailable"
      },
      "note": "An authenticated history with no target-series events is not the adjudicable not-current answer; the currency gate withholds even the citation-independent stop rule and publishes citedPosition=null, retiredAtPosition=null (../016-policy-currency-anchor/registry/SPEC.md §§3-4; rule/transition.py ADJUDICABLE_CURRENCY gate)."
    },
    {
      "id": "h10",
      "category": "S-per-series-discipline",
      "variant": "citation",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Build [SERIES_ID:add 20.0.0/DIGEST_B, SERIES_ID:add 7.0.0/DIGEST_A, OTHER_SERIES_ID:add 7.0.0/DIGEST_A] under the registered authority and retain the full position-3 snapshot with matching SERIES_ID trust configuration and a commitment to (SERIES_ID, 7.0.0, DIGEST_A). Configure grandfather-on-cited-support for SERIES_ID, but construct citation.json with OTHER_SERIES_ID and the real position-3 head digest.",
      "expected": {
        "currency": "pass",
        "transition": "unavailable"
      },
      "note": "A real head digest does not make a foreign-series citation evidence for the committed series; refusal precedes folding and publishes citedPosition=null, retiredAtPosition=null (rule/SPEC.md §3 steps 1 and 4; rule/transition.py citation-series check)."
    }
  ]
}
```

DO NOT FREEZE
