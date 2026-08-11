# Round-2 review (verbatim)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra, read-only sandbox.
Run: 2026-08-11. Verdict: **freezable after listed fixes** (5 RESOLVED, 9 PARTIALLY RESOLVED, 1 new BLOCKER + 1 new MINOR; 9-cell holdout set authored).

> Tooling note: as in round 1, a first attempt at this round was refused by the reviewer's
> provider-side content filter and returned nothing; the prompt was rephrased in plainer
> peer-review register and re-run. An empty output was never treated as a review.

## Findings (verbatim, unedited)

## Confirmation

- R1-1 — PARTIALLY RESOLVED — Exact-source loading now protects Study 016, and `cache_from_source` correctly identifies the plain-import cache, but Study 017 modules execute before the check; additionally, unchecked-hash bytecode with a mismatching stored hash is accepted by CPython but skipped as harmless by the checker. (`harness/upstream016.py:72-105`; `harness/score.py:37-44,163-212,580`; `/home/onword/.pyenv/versions/3.12.11/lib/python3.12/importlib/_bootstrap_external.py:1080-1114`)
- R1-2 — PARTIALLY RESOLVED — Dependency names, versions, and distribution roots are checked, but `cryptography` and `rfc8785` execute before that check, and neither imported-module origins nor code bytes are authenticated; same-version modified or shadowed code remains possible. (`harness/PINS.json:32-37`; `harness/score.py:37-44,215-246`)
- R1-3 — PARTIALLY RESOLVED — The governing path single-reads, stamps, parses, and binds the upstream mapping before loading, closing the original live-reread case; however, `bind_pins()` stores and returns a mutable dictionary and `pinned_files()` exposes it directly, so mutation can still make the bound mapping differ from the stamped bytes. (`harness/score.py:521-552`; `harness/upstream016.py:36-58,61-69,87-94`)
- R1-4 — PARTIALLY RESOLVED — Both the layer and pair checker now associate records by signature verification, and rerunning the round-1 identity case with unpinned, arbitrary, or other-pinned string labels preserved `fail:snapshot-conflicts-with-witnessed-head`; only malformed label shape affects schema validity. Omitted, non-verifying, and never-pinned records are honestly registered, and same-series `requiredWitnesses` cases refuse—but a required key’s foreign-series record bypasses that bound, as R2-1 records. (`witness/verify_witness.py:151-168,243-285`; `harness/score.py:320-356`; `witness/SPEC.md:69-81,100-109`)
- R1-5 — RESOLVED — The revision now calls this the same threat class, expressly disclaims replaying Study 016’s four-layer add-versus-retire cells, and uses the internal split-view/zero-sighting comparison where only sightings differ. (`README.md:17-20`; `PREREGISTRATION.md:115-122,143-151`; `harness/build_fixtures.py:164-173,193-195`; `../016-policy-currency-anchor/harness/MATRIX.json:103-121`)
- R1-6 — PARTIALLY RESOLVED — Current pair bytes validate, and `validated:false` is now terminal pipeline-invalid; key pinning, uniqueness, and own-view head correspondence are checked, but cross-cell series equality is absent and “satisfies the enforcement floor” merely tests `minimumSightings >= 1`, not whether retained valid records meet that floor. (`harness/score.py:312-384,588-597`; `harness/tests/test_study.py:97-109`)
- R1-7 — RESOLVED — The revision consistently describes one additional pinned conflicting record reaching the comparator, treats the pair as an argument for non-collusion, and disclaims measuring organizational independence. (`README.md:21-26`; `harness/MATRIX.json:46-64`; `PREREGISTRATION.md:132-146`)
- R1-8 — PARTIALLY RESOLVED — The causal claims are narrowed to zero-sighting enforcement and positional prefix coverage, but the governing preregistration still names the removed `wit-retention-horizon` cell and other retired identifiers. (`PREREGISTRATION.md:46-55,160-183,207-210`; `harness/MATRIX.json:86-104`)
- R1-9 — PARTIALLY RESOLVED — The three structured fields are returned and retained in `RESULTS.json`, but per-cell expected field values are not adjudicated and `detection_matrix_markdown()` still publishes only outcome strings. (`witness/verify_witness.py:84-93,273-321`; `harness/score.py:387-419,463-500`; `pilots/2026-08-11-build-pilot-02/DETECTION-MATRIX.md:6-43`)
- R1-10 — RESOLVED — Recency is an explicit two-valued configuration policy; the registered arms use identical commitment, snapshot, trust configuration, and sightings bytes, differing only between `ignore` and `refuse-behind`, with the expected pass/refusal outcomes. (`witness/verify_witness.py:71,131-148,297-321`; `harness/build_fixtures.py:199-205`; `harness/MATRIX.json:106-117`)
- R1-11 — RESOLVED — Every attributed record is examined and registered conflict-over-behind precedence is order-independent, including the reversed-order regression. (`witness/SPEC.md:85-92`; `witness/verify_witness.py:287-317`; `harness/tests/test_witness.py:141-156`)
- R1-12 — RESOLVED — Byte inputs and nested commitment shape are guarded, conversions are exception-bounded, and the original malformed shapes remain inside the registered vocabulary. (`witness/verify_witness.py:193-241,293-295`; `harness/tests/test_witness.py:159-176`)
- R1-13 — PARTIALLY RESOLVED — All four keys are now derived from the registered seed labels and each label is compared with its builder constant, but the requested committed mutation regression for every label is absent. (`harness/score.py:263-290`; `harness/tests/test_study.py:77-86,118-133`)
- R1-14 — RESOLVED — Both reserved upstream module names are preflighted before the first module executes, and later build-path loading retains its own foreign-module refusal. (`harness/upstream016.py:134-160`)
- R1-15 — PARTIALLY RESOLVED — The verifier module has the requested narrow wording, but the registered witness specification still says an exchanged accepted head “IS a sighting” and that one mechanism models both witnessing and gossip—the exact overclaim under review. (`witness/verify_witness.py:3-11`; `witness/SPEC.md:32-35`)

## New findings

- R2-1 — BLOCKER — `witness/verify_witness.py`, attribution/enforcement: `attributed_keys` is updated before series scoping, so a valid signature from a required key over an unrelated series satisfies `requiredWitnesses`. Reproduced with zero same-series sightings: WITNESS returned `pass`, `comparisonPerformed:false`, and `validSightings:0`. This defeats the claimed per-series named-witness suppression bound. Move the owner update inside the matching-series branch and add the executed case as a locked regression expecting `fail:witness-required-absent`. (`witness/verify_witness.py:243-285`; `witness/SPEC.md:38-58,79-81,100-106`; `harness/MATRIX.json:80-84`)
- R2-2 — MINOR — `PREREGISTRATION.md`, §§1a/4b/7: the governing document says the locked matrix has 14 cells while later saying 18, and still names removed controls including `neg-sighting-forged`, `neg-unpinned-conflict`, and `wit-retention-horizon`. Reconcile the count and identifiers with the pinned 18-cell matrix before freeze. (`PREREGISTRATION.md:61-70,124-130,157-170,205-211`; `harness/MATRIX.json:1-9,124`)

## Holdout set (authored by the round-2 reviewer)

```json
{
  "reviewer": "codex-cli 0.145.0 / gpt-5.6-sol (OpenAI), round 2",
  "cells": [
    {
      "id": "h01",
      "category": "A-association-and-enforcement",
      "variant": "sightings",
      "role": "control-gate",
      "attackerCapability": "delivery",
      "registeredAbsences": [],
      "construction": "Using the registered Study 017 series, DIGEST_A/B, authority, w1 and w2, build and present [add 1.0.0 DIGEST_A, add 1.1.0 DIGEST_B] with a commitment to (1.0.0, DIGEST_A). Have w1 sign the true head at position 1 and w2 sign the true head at position 2, then swap only the two records' witnessKeyId strings. Configure both public keys, minimumSightings 2, requiredWitnesses [w1,w2], recencyPolicy ignore.",
      "expected": {
        "currency": "pass",
        "witness": "pass"
      },
      "note": "All-pass brittleness control: signature attribution must recover both real owners despite swapped descriptive labels and satisfy both floors, with comparisonPerformed=true, validSightings=2 and unattributedSightings=0 (witness/verify_witness.py:243-321; ../016-policy-currency-anchor/registry/SPEC.md:137-168)."
    },
    {
      "id": "h02",
      "category": "A-association-and-enforcement",
      "variant": "sightings",
      "role": "endpoint",
      "attackerCapability": "delivery",
      "registeredAbsences": [],
      "construction": "Build views A=[add 1.0.0 DIGEST_A, add 1.1.0 DIGEST_B] and C=[add 1.0.0 DIGEST_A, add 2.0.0 DIGEST_C], present C, and commit to (1.0.0, DIGEST_A). Configure pinned w1 and w2, minimumSightings 1, requiredWitnesses [w2], recencyPolicy ignore. Retain w1's valid record of C head@2 plus a record of A head@2 signed by unpinned w3 whose descriptive witnessKeyId is deterministically replaced by w2's key id.",
      "expected": {
        "currency": "pass",
        "witness": "fail:witness-required-absent"
      },
      "note": "A fresh unpinned signature and a claimed pinned identity must neither enter comparison nor satisfy the named floor; w1 satisfies only the count floor (witness/SPEC.md:69-81,100-120; witness/verify_witness.py:243-285)."
    },
    {
      "id": "h03",
      "category": "E-enforcement-order",
      "variant": "config",
      "role": "endpoint",
      "attackerCapability": "delivery",
      "registeredAbsences": [],
      "construction": "Present the valid two-position A view with the current (1.0.0, DIGEST_A) commitment. Pin w1, w2 and w3; retain matching same-series records w1@1 and w2@2; set minimumSightings 3, requiredWitnesses [w3], and recencyPolicy ignore.",
      "expected": {
        "currency": "pass",
        "witness": "unavailable"
      },
      "note": "When both enforcement clauses are unsatisfied, the registered count-floor check comes first: two valid sightings against a floor of three yield unavailable before the named-witness check (witness/SPEC.md:79-84,111-120; witness/verify_witness.py:273-285)."
    },
    {
      "id": "h04",
      "category": "E-enforcement-interaction",
      "variant": "config",
      "role": "endpoint",
      "attackerCapability": "delivery",
      "registeredAbsences": [],
      "construction": "Present the valid two-position A view with the current (1.0.0, DIGEST_A) commitment. Pin w1, w2 and w3; retain matching same-series records from w1 at position 1 and w3 at position 2; set minimumSightings 2, requiredWitnesses [w2], and recencyPolicy ignore.",
      "expected": {
        "currency": "pass",
        "witness": "fail:witness-required-absent"
      },
      "note": "Two records satisfy the count floor but cannot substitute for the specifically named absent witness, so the named-floor code must be exact (witness/SPEC.md:50-58,79-81,117; witness/verify_witness.py:273-285)."
    },
    {
      "id": "h05",
      "category": "R-recency-policy",
      "variant": "config",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Build [add 1.0.0 DIGEST_A, add 1.1.0 DIGEST_B, add 2.0.0 DIGEST_C], present its position-2 prefix, and commit to (1.0.0, DIGEST_A). Retain w1's matching head@2 and w2's actual extension head@3; pin and require both keys, set minimumSightings 2 and recencyPolicy ignore. This cell and h06 use byte-identical commitment, snapshot, trust configuration and sightings.",
      "expected": {
        "currency": "pass",
        "witness": "pass"
      },
      "note": "The ignore arm must accept a genuine beyond-end record after both enforcement floors pass, while publishing comparisonPerformed=true and validSightings=2 (witness/SPEC.md:50-58,82-92; witness/verify_witness.py:287-321)."
    },
    {
      "id": "h06",
      "category": "R-recency-policy",
      "variant": "config",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Use exactly h05's commitment, position-2 snapshot, trust configuration, ordered sightings, pinned keys, minimumSightings 2 and requiredWitnesses [w1,w2]; change only recencyPolicy from ignore to refuse-behind.",
      "expected": {
        "currency": "pass",
        "witness": "fail:snapshot-behind-witnessed-head"
      },
      "note": "Over identical evidence, only the configured refuse-behind arm may turn the extension sighting into the registered recency failure (witness/SPEC.md:54-58,90-92,120; witness/verify_witness.py:297-321)."
    },
    {
      "id": "h07",
      "category": "O-semantic-precedence",
      "variant": "sightings",
      "role": "endpoint",
      "attackerCapability": "authority-key",
      "registeredAbsences": [],
      "construction": "Build A=[add 1.0.0 DIGEST_A, add 1.1.0 DIGEST_B], sibling C=[add 1.0.0 DIGEST_A, add 2.0.0 DIGEST_C], and extension A3=[add 1.0.0 DIGEST_A, add 1.1.0 DIGEST_B, add 2.0.0 DIGEST_C]. Present A at position 2 with the current (1.0.0, DIGEST_A) commitment. Retain in this order w2's A3 head@3, then w1's conflicting C head@2; pin and require both, minimumSightings 2, recencyPolicy refuse-behind.",
      "expected": {
        "currency": "pass",
        "witness": "fail:snapshot-conflicts-with-witnessed-head"
      },
      "note": "After both records are attributed, the in-range conflict must outrank the earlier-listed beyond-end condition independently of retained order (witness/SPEC.md:85-92; witness/verify_witness.py:287-317)."
    },
    {
      "id": "h08",
      "category": "X-layer-composition",
      "variant": "tampered",
      "role": "endpoint",
      "attackerCapability": "tamper",
      "registeredAbsences": [],
      "construction": "Build and present valid A=[add 1.0.0 DIGEST_A, add 1.1.0 DIGEST_B] with the current (1.0.0, DIGEST_A) commitment and w2's matching head@2 record; pin and require w2 with minimumSightings 1 and recencyPolicy ignore. In retained snapshot.json flip only the first base64 character of checkpoint record 2's signature to another base64 alphabet character, leaving its checkpoint payload, stored digest, head attestation and every witness byte unchanged.",
      "expected": {
        "currency": "fail:snapshot-signature-invalid",
        "witness": "pass"
      },
      "note": "WITNESS compares checkpoint content identity and must not launder or duplicate CURRENCY's independent authority-signature check (witness/SPEC.md:85-87,122-128; ../016-policy-currency-anchor/registry/SPEC.md:147-168,195-204)."
    },
    {
      "id": "h09",
      "category": "F-structured-evidence-and-series",
      "variant": "sightings",
      "role": "endpoint",
      "attackerCapability": "none",
      "registeredAbsences": [],
      "construction": "Present the valid two-position A view with the current (1.0.0, DIGEST_A) commitment. Configure only w2 for the Study 017 series, minimumSightings 0, requiredWitnesses [], recencyPolicy ignore; retain one schema-valid record signed by w2 over series https://example.com/judgment-packs/other-policy, using A's head digest and position 2 and leaving its descriptive key id correct.",
      "expected": {
        "currency": "pass",
        "witness": "pass"
      },
      "note": "A cryptographically attributed but foreign-series record is not a comparison input: the pass must publish comparisonPerformed=false, validSightings=0 and unattributedSightings=0 rather than resemble h01's sighting-backed pass (witness/verify_witness.py:243-292; witness/SPEC.md:65-84)."
    }
  ]
}
```

DO NOT FREEZE
