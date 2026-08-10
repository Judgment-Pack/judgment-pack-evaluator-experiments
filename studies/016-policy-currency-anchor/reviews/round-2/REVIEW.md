# Round-2 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-10. Verdict: **freezable after listed fixes** (8 RESOLVED, 7 PARTIALLY RESOLVED, 1 new MINOR; 10-cell holdout stratum authored).

## Confirmation

- R1-1 — PARTIALLY RESOLVED — `harness/upstream014.py`: every cached/fresh load checks module identity, origin, and bytes and rejects pre-existing shared-name entries, but bare imports can still execute an earlier `sys.path` shadow before the post-import rejection; absolute-path private-alias loading remains required.
- R1-2 — PARTIALLY RESOLVED — `harness/MATRIX.json`, `PREREGISTRATION.md`, `harness/build_fixtures.py`: the row is renamed, descriptive, and excluded from credit, but the preregistration still names `cur-authz-rollback-accepted` and calls e22 a rollback, while builder prose/identifiers retain rollback terminology.
- R1-3 — PARTIALLY RESOLVED — `registry/verify_currency.py`, `harness/run_verify.py`, `studies/014-openworkproof-binding/adapter/verify.py`, `registry/SPEC.md`: snapshot attacks now land in the vocabulary, including duplicates, signed version 2, malformed minimum pins, non-canonicalizable values, and boolean integers; however raw `trustconfig.json` still passes through ordinary last-wins `json.loads`, so duplicate configuration members can pass contrary to the strict-input promise.
- R1-4 — PARTIALLY RESOLVED — `harness/score.py`, `harness/MATRIX.json`, `PREREGISTRATION.md`, `README.md`: the current pair is a real fork, wording is narrowed, and the stateful arm is registered, but the scorer establishes “same authority” only by comparing the expressly unauthenticated `authorityKeyId` label rather than the pinned public keys and common target tuple.
- R1-5 — RESOLVED — `registry/verify_currency.py`, `registry/checkpoint.py`, `registry/SPEC.md`, `harness/MATRIX.json`: the input is `minimumHeadPin`, consistently described as caller-provisioned prior-acceptance state; verifier persistence and atomic high-water updates are expressly not claimed.
- R1-6 — RESOLVED — `registry/verify_currency.py`, `registry/SPEC.md`: verification uses the pinned key and one code, `snapshot-signature-invalid`; the unauthenticated key-id label affects detail only.
- R1-7 — PARTIALLY RESOLVED — `registry/verify_currency.py`, `harness/tests/test_registry.py`: all three limits and `snapshot-limits-exceeded` are enforced with one-past tests, but the required exact-at-limit registered vectors are absent.
- R1-8 — RESOLVED — `harness/MATRIX.json`, `harness/build_fixtures.py`, `PREREGISTRATION.md`: genuine BINDING- and REPLAY-failure controls were added, and the claim is narrowed to positive compatibility plus aliveness rather than replication of Study 014’s mutation stratum.
- R1-9 — RESOLVED — `harness/MATRIX.json`, `harness/score.py`, `PREREGISTRATION.md`: the byte-identical endpoint duplication is removed; `cur-concurrent-set` is counted once and carries one scored and one analytic reading.
- R1-10 — RESOLVED — `registry/verify_currency.py`, `harness/PINS.json`, `harness/score.py`, `harness/MATRIX.json`: trust is series-bound, both genesis roots are registered and recomputed, and the unknown-series cell honestly uses the second root as a config variant.
- R1-11 — PARTIALLY RESOLVED — `harness/score.py`, `harness/MATRIX-HOLDOUT.json`: a post-freeze empty holdout is terminal-refused, but the current file remains empty and every nonempty holdout is still refused because construction, adjudication, and separate reporting machinery has not landed.
- R1-12 — PARTIALLY RESOLVED — `harness/score.py`, `harness/PINS.json`: marker, terminal, and successful records carry `pinsRawSha256`, and `SystemExit` is terminal-recorded and re-raised; however the scorer hashes and parses separate reads of PINS, and PINS still falsely says every attempt record carries `pinsSha256`.
- R1-13 — RESOLVED — `registry/verify_currency.py`, `registry/SPEC.md`, `harness/tests/test_registry.py`: repeated `add` never reactivates; only `reinstate` can re-enter a retired binding.
- R1-14 — RESOLVED — `harness/score.py`, `harness/PINS.json`: both keypairs, key IDs, public keys, and genesis heads are mechanically re-derived and compared before adjudication.
- R1-15 — PARTIALLY RESOLVED — `PREREGISTRATION.md`, `registry/SPEC.md`, `README.md`: governing prose is corrected, but README still says a judgment “authorized” an executed action and describes the class as a version “no longer in force.”

## New findings

- R2-1 — MINOR — `PREREGISTRATION.md` §1a: it says the locked matrix contains 20 cells, while §4 and `harness/MATRIX.json` establish 22, leaving the registered denominator contradictory. Fix: change 20 to 22 and add or derive a consistency assertion for published counts.

## Holdout stratum (authored by the round-2 reviewer)

```json
{
  "reviewer": "codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), round 2",
  "cells": [
    {
      "id": "h01",
      "category": "V-trust-configuration",
      "variant": "config",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use the baseline chain, the authority-signed [add 0.1.0 digest-A] snapshot, and its normal trust configuration; in the retained trustconfig.json bytes replace the single \"minimumHeadPin\": null member with two consecutive identical \"minimumHeadPin\": null members, change no other byte, and regenerate only the attempt-local manifest.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "unavailable"
      },
      "note": "Duplicate configuration members are malformed even when last-wins parsing would preserve baseline semantics; strict configuration refusal must precede membership."
    },
    {
      "id": "h02",
      "category": "O-first-failure",
      "variant": "tampered",
      "role": "endpoint",
      "attackerCapability": "tamper",
      "registeredAbsences": [],
      "construction": "Copy the baseline composition; in snapshot.json replace only attestation.payload.position's integer 1 with the JSON boolean true, leaving its signature, every checkpoint, and the trust configuration unchanged, then regenerate only the attempt-local manifest.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "fail:snapshot-chain-inconsistent"
      },
      "note": "Closed-schema validation must reject the boolean integer before the now-stale attestation signature can claim first failure."
    },
    {
      "id": "h03",
      "category": "O-first-failure",
      "variant": "resigned",
      "role": "endpoint",
      "attackerCapability": "authority-key",
      "registeredAbsences": [],
      "construction": "Use the baseline chain. With the study authority key build the presented registry [add 0.1.0 digest-A, retire 0.1.0, add 0.1.0 digest-B], where digest-A and digest-B are the registered v0.1.0 and v0.2.0 pack digests, and snapshot all three checkpoints. Separately build the sibling prefix [add 0.1.0 digest-A, add 0.2.0 digest-B]; use its position-2 checkpointDigest as minimumHeadPin.head with position 2 in an otherwise normal expense-series trust configuration.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "fail:snapshot-behind-pinned-minimum-head"
      },
      "note": "The step-6 sibling-head mismatch must win before step 7 reaches the authority-signed binding rebound."
    },
    {
      "id": "h04",
      "category": "R-lifecycle",
      "variant": "resigned",
      "role": "endpoint",
      "attackerCapability": "authority-key",
      "registeredAbsences": [],
      "construction": "Use the baseline chain. With the study authority key build and attest the two-event registry [add 0.1.0 digest-A, add 0.1.0 digest-B], using the registered v0.1.0 and v0.2.0 pack digests respectively; configure the correct expense series, authority key, first-checkpoint genesis, and no minimum head pin.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "fail:binding-rebound"
      },
      "note": "Binding immutability applies while a version is still active, not only after retirement."
    },
    {
      "id": "h05",
      "category": "X-layer-composition",
      "variant": "resigned",
      "role": "endpoint",
      "attackerCapability": "full-keys",
      "registeredAbsences": [],
      "construction": "Use all six retained chain artifacts from the built neg-replay chain. Attach an authority-signed snapshot over [add 0.1.0 digest-A, add 0.2.0 digest-B, retire 0.1.0] and the normal expense-series trust configuration rooted at its first checkpoint; make no other edit.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "fail:replay-executable-mismatch",
        "currency": "fail:not-current-at-snapshot"
      },
      "note": "The forged replay tuple and retired pack membership must be attributed independently when both failures coexist."
    },
    {
      "id": "h06",
      "category": "I-identity-binding",
      "variant": "chain",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use all six retained artifacts from the built successor chain carrying pack 0.2.0 digest-B. Attach the authority-signed one-checkpoint registry [add 0.1.0 digest-A] and its normal expense-series trust configuration with no minimum head pin.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "fail:not-current-at-snapshot"
      },
      "note": "Currency must read the successor identity from the signed binding point rather than inherit the baseline identity from the registry or cell plumbing."
    },
    {
      "id": "h07",
      "category": "L-supported-set-boundary",
      "variant": "registry",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use the baseline chain. With build_registry create exactly 512 expense-series add events: first add 0.1.0 with digest-A, then add the 511 distinct versions 9.0.1 through 9.0.511, each also bound to digest-A; snapshot all records and use the correct authority, first-record genesis, expense series, and no minimum head pin.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "pass"
      },
      "note": "A supported set exactly at MAX_SUPPORTED_SET is valid; only member 513 is over the registered bound."
    },
    {
      "id": "h08",
      "category": "L-checkpoint-boundary",
      "variant": "registry",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use the baseline chain. With build_registry create exactly 1024 checkpoints: first add expense-series 0.1.0 digest-A, then add 1023 distinct other-policy versions 1.0.1 through 1.0.1023 using the registered other-series digest; snapshot all records and use the expense-series authority and first-record genesis with no minimum head pin.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "pass"
      },
      "note": "A structurally valid snapshot exactly at MAX_CHECKPOINTS must pass while unrelated-series entries leave target-series membership unchanged."
    },
    {
      "id": "h09",
      "category": "L-snapshot-byte-boundary",
      "variant": "artifact",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Copy the baseline composition and append ASCII space bytes after the complete snapshot.json JSON value until the retained snapshot is exactly 1048576 bytes; alter no JSON value, signature, trust configuration, or chain artifact, and regenerate only the attempt-local manifest.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "pass"
      },
      "note": "The exact MAX_SNAPSHOT_BYTES boundary is inclusive, and semantically inert JSON whitespace must not create a detection."
    },
    {
      "id": "h10",
      "category": "control-positive",
      "variant": "artifact",
      "role": "control-gate",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Copy the baseline composition and replace every checkpoint and attestation authorityKeyId label in snapshot.json with harness/PINS.json registryAuthority.foreignKeyId; touch no signed payload, signature, digest, trust-configuration, or chain byte, and regenerate only the attempt-local manifest.",
      "expected": {
        "owp": "pass",
        "binding": "pass",
        "replay": "pass",
        "currency": "pass"
      },
      "note": "This is the holdout's all-pass brittleness control: the explicitly unauthenticated labels are detail-only, while every cryptographically meaningful byte remains valid."
    }
  ]
}
```

freezable after listed fixes
