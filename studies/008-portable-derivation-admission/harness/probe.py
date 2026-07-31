"""EXPLORATORY probe — not a registered endpoint, not pooled with D1-D5.

The preregistration registered a specific risk: that short-circuit evaluation
could read strictly fewer pointers than the verifier requires, making the
mechanically-derived basis insufficient. D3 scored 24/24, but Study 007's corpus
contains no payload with `datedRecord: false`, which is the one shape that would
trigger the risk: the rule's type clause evaluates

    not(all[isTrue(/datedRecord), isDecimalString(/matchCount)])

and `all` short-circuits on a false `/datedRecord`, so `/matchCount` is never
read -- while Arm B's hand-curated type basis lists it unconditionally.

This probe constructs that payload and reports whether the arms diverge, so the
D3 result is read as corpus-contingent rather than unconditional.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study  # noqa: E402
from study import S007, RULE_PATH, load, portable, s007  # noqa: E402

PROBE_PAYLOAD = {
    "status": "found",
    "screenedLegalName": "Northwind Analytics Ltd",
    "observedAt": "2026-07-30T14:55:00Z",
    "datedRecord": False,          # the shape Study 007's corpus never contains
    "matchCount": "3",             # a *valid* decimal string, so only /datedRecord decides
    "recordId": "PROBE-NOT-DATED",
}


def main():
    document = load(S007 / "fixtures" / "cases.json")
    binding = load(S007 / "fixtures" / "binding-lock.json")
    key = (S007 / "fixtures" / "gateway.key").read_bytes().strip()
    rule = load(RULE_PATH)
    subject = document["request"]["legalName"]

    b = s007.derive_payload(PROBE_PAYLOAD, subject, document["asOf"], binding["maxAgeSeconds"])
    c = portable.derive(rule, PROBE_PAYLOAD, {
        "subject": subject, "asOf": document["asOf"],
        "maxAgeSeconds": binding["maxAgeSeconds"]})

    b_basis, c_basis = sorted(b["basis"]), sorted(c["basis"])
    claim_same = (b["facts"] == c["facts"]
                  and b["evidenceAvailability"] == c["evidenceAvailability"]
                  and b["acquisitionStatus"] == c["acquisitionStatus"])

    # Does the unchanged verifier reject Arm C's shorter basis? Build a minimal
    # attested store for the constructed payload using the fixture key.
    store = Path(study.STUDY) / "probe" / "gateway"
    artifact_digest = s007.digest(PROBE_PAYLOAD)
    receipt = {
        "arguments": {binding["subjectArgument"]: subject},
        "artifactDigest": artifact_digest,
        "bindingDigest": s007.digest(binding),
        "callIndex": 1, "cellId": "probe", "receiptVersion": "1", "repetition": 1,
        "retrievedAt": "2026-07-30T15:00:00Z", "server": binding["binding"]["server"],
        "sideEffect": "read", "sourceRef": binding["sourceRef"], "subject": subject,
        "tool": binding["binding"]["tool"],
    }
    receipt["attestation"] = s007.attest(receipt, key)
    receipt_digest = s007.digest(receipt)
    (store / "artifacts").mkdir(parents=True, exist_ok=True)
    (store / "receipts").mkdir(parents=True, exist_ok=True)
    (store / "artifacts" / (artifact_digest.split(":", 1)[1] + ".json")).write_text(
        s007.pretty(PROBE_PAYLOAD), encoding="utf-8")
    (store / "receipts" / (receipt_digest.split(":", 1)[1] + ".json")).write_text(
        s007.pretty(receipt), encoding="utf-8")

    envelopes = {
        "armB": study.envelope(b, b["basis"], binding, receipt_digest, artifact_digest, "probe"),
        "armC": study.envelope(c, c["basis"], binding, receipt_digest, artifact_digest, "probe"),
    }
    errors = {arm: s007.verify_candidate(env, store, document, binding, key)
              for arm, env in envelopes.items()}

    report = {
        "probe": "datedRecord-false (absent from Study 007's corpus)",
        "registeredRisk": "short-circuit evaluation reads fewer pointers than the verifier requires",
        "armB": {"reason": b["reason"], "basisPointers": b_basis, "errors": errors["armB"],
                 "admitted": not errors["armB"]},
        "armC": {"reason": c["reason"], "basisPointers": c_basis, "errors": errors["armC"],
                 "admitted": not errors["armC"]},
        "claimsAgree": claim_same,
        "basesAgree": b_basis == c_basis,
        "riskRealized": b_basis != c_basis or bool(errors["armC"]),
    }
    study.dump(Path(study.STUDY) / "PROBE.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
