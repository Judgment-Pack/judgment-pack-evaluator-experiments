#!/usr/bin/env python3
"""Pre-freeze unit tests, on DISJOINT throwaway fixtures only: nothing here
evaluates pack C, pack D, or a frozen record (PREREGISTRATION.md §10)."""
from __future__ import annotations
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
LINE = os.path.dirname(os.path.dirname(STUDY))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LINE, "acquisition-proxy"))

import attest  # noqa: E402
import gate as study_gate  # noqa: E402
import pnf_check  # noqa: E402
import study  # noqa: E402

THROWAWAY = {
    "caseId": "t-1",
    "vendor": {"legalName": "Throwaway Ltd", "sanctionsHit": False, "riskScore": "33"},
    "decision": {"outcome": "clear", "decidedBy": "reviewer-t", "decidedAt": "2026-07-01T00:00:00Z"},
}


def acquire_throwaway(root: str, record: dict) -> tuple[str, bytes, list[dict]]:
    records_dir = os.path.join(root, "records")
    os.makedirs(records_dir)
    with open(os.path.join(records_dir, record["caseId"] + ".json"), "w") as handle:
        json.dump(record, handle)
    store = os.path.join(root, "store")
    key = os.urandom(32)
    key_path = os.path.join(root, "key")
    with open(key_path, "wb") as handle:
        handle.write(key)
    env = {name: os.environ[name] for name in ("PATH", "HOME") if name in os.environ}
    env["RECORDS_DIR"] = records_dir
    proxy = subprocess.Popen(
        [sys.executable, os.path.join(LINE, "acquisition-proxy", "attest.py"),
         "wrap", store, key_path, "--authority", study.AUTHORITY, "--",
         sys.executable, os.path.join(STUDY, "source", "record_source.py")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env, text=True)

    def call(message):
        proxy.stdin.write(json.dumps(message) + "\n")
        proxy.stdin.flush()
        return json.loads(proxy.stdout.readline())

    call({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})
    reply = call({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                  "params": {"name": study.TOOL, "arguments": {"caseId": record["caseId"]}}})
    assert reply.get("result", {}).get("caseId") == record["caseId"], reply
    proxy.stdin.close()
    proxy.wait(timeout=30)
    session = os.listdir(os.path.join(store, "receipts"))[0]
    return store, key, [{"caseId": record["caseId"], "sessionId": session, "callIndex": 0}]


class PNF(unittest.TestCase):
    def test_the_registered_rule_passes_and_only_it(self):
        rule = json.load(open(os.path.join(STUDY, "transcription", "record.rule.json")))
        pnf_check.check(rule)
        for mutate in (
            lambda r: r["clauses"][0].update(when={"op": "equals", "field": "/x", "to": 1}),
            lambda r: r["clauses"][0]["claim"]["facts"].append(
                {"pointer": "/vendor/extra", "from": "/decision/outcome"}),
            lambda r: r.update(parameters={}),
            lambda r: r["clauses"][0]["claim"].update(extra=True),
            lambda r: r["clauses"][0]["claim"]["facts"][1].update(
                {"from": "/vendor/oracleRisk"}),
        ):
            bad = copy.deepcopy(rule)
            mutate(bad)
            with self.assertRaises(pnf_check.PNFError):
                pnf_check.check(bad)


class Gate(unittest.TestCase):
    def test_a_faithful_row_is_admitted_and_a_tampered_one_is_not(self):
        with tempfile.TemporaryDirectory() as root:
            store, key, refs = acquire_throwaway(root, THROWAWAY)
            rule = study_gate.frozen_rule()
            row, lineage = study_gate.reconstruct_row(
                store, key, refs[0]["sessionId"], 0, rule, study.AUTHORITY)
            matrix = {"matrixVersion": "1", "cases": [row]}
            study_gate.admit_matrix(matrix, refs, store, key, study.AUTHORITY,
                                    study.sha256_file(study_gate.RULE_PATH))
            self.assertEqual(lineage["caseId"], "t-1")
            # A transcriber that emitted a different expectation is refused —
            # this is what makes control rows untamperable.
            tampered = copy.deepcopy(matrix)
            tampered["cases"][0]["expectedDisposition"]["outcomeId"] = "reject"
            with self.assertRaises(study_gate.GateError):
                study_gate.admit_matrix(tampered, refs, store, key, study.AUTHORITY,
                                        study.sha256_file(study_gate.RULE_PATH))
            # And so is an extra member, which jpack's strict matrix would
            # also refuse; the gate refuses it first.
            extra = copy.deepcopy(matrix)
            extra["cases"][0]["acquisitionStatus"] = "resolved"
            with self.assertRaises(study_gate.GateError):
                study_gate.admit_matrix(extra, refs, store, key, study.AUTHORITY,
                                        study.sha256_file(study_gate.RULE_PATH))

    def test_metamorphic_record_metadata_reaches_no_fact(self):
        with tempfile.TemporaryDirectory() as root:
            mutated = copy.deepcopy(THROWAWAY)
            mutated["decision"]["outcome"] = "reject"
            mutated["decision"]["decidedBy"] = "reviewer-x"
            store, key, refs = acquire_throwaway(root, mutated)
            rule = study_gate.frozen_rule()
            row, _ = study_gate.reconstruct_row(
                store, key, refs[0]["sessionId"], 0, rule, study.AUTHORITY)
            self.assertEqual(row["facts"], {"vendor": {"sanctionsHit": False, "riskScore": "33"}})
            self.assertEqual(row["expectedDisposition"]["outcomeId"], "reject")


class Mechanics(unittest.TestCase):
    def test_apply_patch_requires_the_preimage(self):
        pack = {"rules": [{"when": {"op": "x"}}]}
        with self.assertRaises(study.StudyError):
            study.apply_patch(pack, [{"path": "/rules/0/when/op", "old": "y", "new": "z"}])
        patched = study.apply_patch(pack, [{"path": "/rules/0/when/op", "old": "x", "new": "z"}])
        self.assertEqual(patched["rules"][0]["when"]["op"], "z")
        self.assertEqual(pack["rules"][0]["when"]["op"], "x")

    def test_acquisition_check_binds_artifact_to_record(self):
        with tempfile.TemporaryDirectory() as root:
            store, key, refs = acquire_throwaway(root, THROWAWAY)
            # The frozen-record equality is checked against the study's own
            # records dir, so a throwaway case id must be refused there —
            # which is the binding working, exercised without frozen fixtures.
            with self.assertRaises((study.StudyError, FileNotFoundError)):
                study.check_acquisition(store, key, refs)
            ok, findings = attest.verify(store, key, expected_authority=study.AUTHORITY)
            self.assertTrue(ok, findings)


if __name__ == "__main__":
    unittest.main()
