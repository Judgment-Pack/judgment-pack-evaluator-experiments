#!/usr/bin/env python3
"""Study 019 pilot self-test fixture builder -- DESIGN-TIME, NON-CITABLE HARNESS-VALIDATION
TOOLING. NOT the registered study harness.

Writes MOCK completions (no model is called) into a pilot output directory so the whole
pilot path -- marker extraction, admission, per-row evaluation, scoring -- can be exercised
end to end before any real pilot call is made. The positive controls copy the frozen-design
reference artifacts (reference/refA/pack.json, reference/refB/policy.rego) verbatim inside
the registered marker/fence form; they MUST score perfect=true. The negative controls
exercise every ordered drop code and the row-failure path.

Usage:  python3 make_mock_runs.py --outdir <dir>
Then:   python3 pilot_run.py score --arm A --outdir <dir>
"""

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, ".."))
REFA = os.path.join(DESIGN, "reference", "refA", "pack.json")
REFB = os.path.join(DESIGN, "reference", "refB", "policy.rego")

PREAMBLE = (
    "Here is my reading of the policy, then the two artifacts.\n\n"
    "I worked the clauses in the order the policy states and encoded each one.\n"
    "A draft I discarded is shown first so the extractor's last-marker rule is exercised.\n\n"
    "PACK:\n\n```json\n{ \"this\": \"is a discarded earlier draft\" }\n```\n\n"
    "That draft was wrong, so here are the final artifacts.\n\n"
)

MOCK_MATRIX = {
    "matrixVersion": "2",
    "cases": [
        {
            "id": "mock-row-1",
            "facts": {"vendor": {"riskScore": "10", "requestedSpend": "1000.00",
                                 "sanctionsStatus": "CLEAR", "countryRisk": "LOW",
                                 "newVendor": "no", "criticalSupplier": "no",
                                 "priorEnforcement": "no"}},
            "evidenceAvailability": {"financial-evidence": "present"},
            "expectedDisposition": {"kind": "outcome", "outcomeId": "approve",
                                    "reasons": [], "handoff": {"state": "none"}},
        },
        {
            "id": "mock-row-2",
            "facts": {"vendor": {"riskScore": "10", "requestedSpend": "1000.00",
                                 "sanctionsStatus": "CLEAR", "countryRisk": "LOW",
                                 "newVendor": "no", "criticalSupplier": "no",
                                 "priorEnforcement": "no"}},
            "evidenceAvailability": {"financial-evidence": "absent"},
            "expectedDisposition": {"kind": "unresolved",
                                    "reasons": ["missing-required-evidence"],
                                    "handoff": {"state": "requested",
                                                "triggeredBy": ["missing-required-evidence"]}},
        },
    ],
}

MOCK_TESTS = """package study_test

import data.study
import rego.v1

base := {
	"vendor": {
		"riskScore": 10,
		"requestedSpend": 1000,
		"sanctionsStatus": "CLEAR",
		"countryRisk": "LOW",
		"newVendor": "no",
		"criticalSupplier": "no",
		"priorEnforcement": "no",
	},
	"evidence": {"financial-evidence": "present"},
}

test_low_risk_small_spend_is_approved if {
	study.decision.disposition == "approve" with input as base
}

test_absent_financial_evidence_blocks if {
	d := study.decision with input as object.union(base, {"evidence": {"financial-evidence": "absent"}})
	d.disposition == "unresolved"
	d.reasons == ["missing-required-evidence"]
}
"""


def write_run(outdir, arm, slot, completion):
    d = os.path.join(outdir, "arm-%s" % arm, "run-%s" % str(slot).zfill(3))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "completion.txt"), "w") as fh:
        fh.write(completion)
    with open(os.path.join(d, "exit.txt"), "w") as fh:
        fh.write("0\n")
    with open(os.path.join(d, "CALL.json"), "w") as fh:
        json.dump({"harness": "make_mock_runs.py (MOCK, no model call)",
                   "arm": arm, "slot": str(slot).zfill(3)}, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return d


def arm_a_completion(pack_text, matrix_obj):
    return (PREAMBLE
            + "PACK:\n\n```json\n" + pack_text.rstrip("\n") + "\n```\n\n"
            + "MATRIX:\n\n```json\n" + json.dumps(matrix_obj, indent=2) + "\n```\n")


def arm_rego_completion(policy_text, tests_text):
    return ("Here is the policy and its test suite.\n\n"
            + "POLICY:\n\n```rego\n" + policy_text.rstrip("\n") + "\n```\n\n"
            + "TESTS:\n\n```rego\n" + tests_text.rstrip("\n") + "\n```\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    with open(REFA) as fh:
        pack_text = fh.read()
    with open(REFB) as fh:
        policy_text = fh.read()

    # ---- arm A ----------------------------------------------------------------
    # 001 positive control: the reference pack, verbatim, in the registered form.
    write_run(args.outdir, "A", 1, arm_a_completion(pack_text, MOCK_MATRIX))
    # 002 no-marker
    write_run(args.outdir, "A", 2,
              "I cannot produce a pack for this policy.\n\n```json\n{}\n```\n")
    # 003 unparseable
    write_run(args.outdir, "A", 3,
              "PACK:\n\n```json\n{ \"specVersion\": \"0.2.0-draft\", oops\n```\n\n"
              "MATRIX:\n\n```json\n{}\n```\n")
    # 004 invalid-artifact (parses, not a conformant pack)
    write_run(args.outdir, "A", 4,
              "PACK:\n\n```json\n{\"specVersion\": \"0.2.0-draft\", \"id\": \"x\"}\n```\n")
    # 005 admitted but wrong: D3's boundary operator mutated (>= 90 becomes > 90)
    pack = json.loads(pack_text)
    for rule in pack["rules"]:
        if rule["id"] == "r-d3":
            for cond in rule["when"]["conditions"]:
                if cond.get("path") == "/vendor/riskScore":
                    cond["operator"] = "greater-than"
    write_run(args.outdir, "A", 5,
              arm_a_completion(json.dumps(pack, indent=2), MOCK_MATRIX))

    # ---- arms B and C ---------------------------------------------------------
    for arm in ("B", "C"):
        write_run(args.outdir, arm, 1, arm_rego_completion(policy_text, MOCK_TESTS))
    # B 002 unparseable (opa check reports only rego_parse_error)
    write_run(args.outdir, "B", 2,
              "POLICY:\n\n```rego\npackage study\n\ndecision := {\n```\n\n"
              "TESTS:\n\n```rego\npackage study_test\n```\n")
    # B 003 admitted but wrong: the same boundary mutation, in Rego
    assert "risk >= 90" in policy_text
    write_run(args.outdir, "B", 3,
              arm_rego_completion(policy_text.replace("risk >= 90", "risk > 90"), MOCK_TESTS))
    # B 004 invalid-artifact via the capability gate (the canary: a denied builtin).
    # This is the negative control showing the gate has power, not just that it is passed.
    write_run(args.outdir, "B", 4,
              arm_rego_completion(
                  "package study\n\nimport rego.v1\n\n"
                  "decision := {\"disposition\": \"review\", \"reasons\": []} if {\n"
                  "\ttime.now_ns() > 0\n}\n", MOCK_TESTS))

    print("mock runs written under %s" % os.path.abspath(args.outdir))


if __name__ == "__main__":
    main()
