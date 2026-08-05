#!/usr/bin/env python3
"""Pre-freeze unit tests, on DISJOINT throwaway fixtures only: nothing here
evaluates pack C, pack D, or an authored record with the evaluator; patch
application and predicate checks are pure JSON mechanics."""
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
import policy_mirror  # noqa: E402
import records_compile  # noqa: E402
import study  # noqa: E402
import transcript_check  # noqa: E402

THROWAWAY = {
    "caseId": "t-1",
    "vendor": {"legalName": "Throwaway Ltd", "sanctionsHit": False,
               "registeredCountry": "NL", "handlesPersonalData": False,
               "riskScore": "33"},
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
    env["RECORDS_DIRS"] = records_dir
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


def vendor(sanctions=False, country="NL", personal=False, score="33") -> dict:
    return {"legalName": "V", "sanctionsHit": sanctions, "registeredCountry": country,
            "handlesPersonalData": personal, "riskScore": score}


class Mirror(unittest.TestCase):
    def test_the_mirror_states_the_policy(self):
        cases = [
            (vendor(sanctions=True, score="1"), "reject"),
            (vendor(country="SY", score="1"), "reject"),
            (vendor(country="KP", personal=True, score="99"), "reject"),
            (vendor(score="70"), "manual-review"),
            (vendor(score="70.1"), "manual-review"),
            (vendor(personal=True, score="40"), "manual-review"),
            (vendor(personal=True, score="69.9"), "manual-review"),
            (vendor(personal=True, score="39.9"), "clear"),
            (vendor(personal=False, score="69.9"), "clear"),
            (vendor(personal=False, score="1"), "clear"),
        ]
        for subject, expected in cases:
            self.assertEqual(policy_mirror.verdict(subject), expected, subject)

    def test_every_family_predicate_reads_only_facts(self):
        family = study.family()
        matches = {
            0: (vendor(score="70"), vendor(score="70.5")),
            1: (vendor(score="70.5"), vendor(score="71")),
            2: (vendor(personal=True, score="40.5"), vendor(personal=False, score="40.5")),
            3: (vendor(personal=True, score="55"), vendor(personal=True, score="70")),
            4: (vendor(country="SY", score="5"), vendor(country="IR", score="5")),
            5: (vendor(personal=True, score="39.5"), vendor(personal=True, score="40")),
        }
        for mutation in family["mutations"]:
            inside, outside = matches[mutation["index"]]
            self.assertTrue(policy_mirror.predicate_matches(mutation["predicate"], inside),
                            mutation["index"])
            self.assertFalse(policy_mirror.predicate_matches(mutation["predicate"], outside),
                             mutation["index"])

    def test_the_controls_intersect_no_predicate_and_are_wrong(self):
        family = study.family()
        for name in ("k-wrong-1", "k-wrong-2"):
            record = json.load(open(os.path.join(STUDY, "controls", name + ".json")))
            self.assertNotEqual(record["decision"]["outcome"],
                                policy_mirror.verdict(record["vendor"]))
            for mutation in family["mutations"]:
                self.assertFalse(policy_mirror.predicate_matches(
                    mutation["predicate"], record["vendor"]), mutation["index"])


class Tables(unittest.TestCase):
    def test_the_sampled_class_derives_unresolved_and_nothing_else_moves(self):
        family = study.family()
        boundary = family["mutations"][0]
        row = study.table_entry(vendor(score="70"), boundary)
        self.assertEqual(row["underC"], study.wrapper("manual-review"))
        self.assertEqual(row["underD"], study.unresolved(["no-match"]))
        untouched = study.table_entry(vendor(score="71"), boundary)
        self.assertEqual(untouched["underC"], untouched["underD"])

    def test_mutation_three_splits_by_personal_data(self):
        inverted = study.family()["mutations"][3]
        personal = study.table_entry(vendor(personal=True, score="55"), inverted)
        impersonal = study.table_entry(vendor(personal=False, score="55"), inverted)
        self.assertEqual(personal["underD"], study.unresolved(["no-match"]))
        self.assertEqual(impersonal["underD"], study.unresolved(["conflict"]))
        self.assertEqual(personal["underC"], study.wrapper("manual-review"))
        self.assertEqual(impersonal["underC"], study.wrapper("clear"))

    def test_every_family_patch_applies_and_changes_the_pack(self):
        correct = json.load(open(os.path.join(STUDY, "packs/vendor-screening-correct.pack.json")))
        family = study.family()
        for mutation in family["mutations"]:
            patched = study.apply_patch(correct, mutation["patch"])
            self.assertNotEqual(patched, correct, mutation["index"])


class Compiler(unittest.TestCase):
    def wrap(self, elements) -> tuple[dict, list]:
        accepted, ledger, _ = records_compile.compile_records(json.dumps(elements))
        return accepted, ledger

    def record(self, case_id="a-vendor", **kwargs) -> dict:
        record = copy.deepcopy(THROWAWAY)
        record["caseId"] = case_id
        record["vendor"].update(kwargs)
        return record

    def test_acceptance_and_every_drop_code(self):
        good = self.record()
        accepted, ledger = self.wrap([good])
        self.assertEqual(list(accepted), ["a-vendor"])
        self.assertEqual(ledger, [(0, "a-vendor", "")])
        drops = [
            ({"caseId": "x"}, "schema"),
            (self.record(riskScore="070"), "decimal-form"),
            (self.record(riskScore="7.50"), "decimal-form"),
            (self.record(registeredCountry="nl"), "country-form"),
            (self.record(registeredCountry="NLD"), "country-form"),
            (self.record(case_id="Bad_Id"), "id-form"),
            (self.record(case_id="k-fake"), "id-form"),
            ({**good, "decision": {**good["decision"], "outcome": "escalate"}}, "outcome-value"),
        ]
        for element, code in drops:
            accepted, ledger = self.wrap([element])
            self.assertEqual(accepted, {}, code)
            self.assertEqual(ledger[0][2], code)
        accepted, ledger = self.wrap([good, good])
        self.assertEqual(len(accepted), 1)
        self.assertEqual(ledger[1][2], "duplicate-id")

    def test_extraction_ignores_prose_and_refuses_non_arrays(self):
        accepted, _, span = records_compile.compile_records(
            "Sure! Here are the records:\n%s\nHope that helps." % json.dumps([self.record()]))
        self.assertEqual(list(accepted), ["a-vendor"])
        self.assertGreater(span[0], 0)
        accepted, _, _ = records_compile.compile_records(
            "See [1] for context.\n%s" % json.dumps([self.record()]))
        self.assertEqual(list(accepted), ["a-vendor"])
        with self.assertRaises(records_compile.CompileError):
            records_compile.compile_records("no array here")
        # The registered rule is positional, not semantic: the widest
        # parseable array in {"cases": []} is the empty one.
        accepted, ledger, _ = records_compile.compile_records('{"cases": []}')
        self.assertEqual((accepted, ledger), ({}, []))

    def test_duplicate_object_keys_disqualify_the_candidate(self):
        good = json.dumps([self.record()])
        poisoned = '[{"caseId": "x", "caseId": "y"}]\n' + good
        accepted, _, _ = records_compile.compile_records(poisoned)
        self.assertEqual(list(accepted), ["a-vendor"])
        with self.assertRaises(records_compile.CompileError):
            records_compile.compile_records('[{"caseId": "x", "caseId": "y"}]')

    def test_rendering_is_deterministic_and_complete(self):
        raw = json.dumps([self.record(), {"caseId": "b"}, self.record(case_id="b-vendor")])
        accepted, ledger, span = records_compile.compile_records(raw)
        first = records_compile.render(accepted, ledger, span)
        second = records_compile.render(accepted, ledger, span)
        self.assertEqual(first, second)
        self.assertIn("records/a-vendor.json", first)
        self.assertIn("records/b-vendor.json", first)
        table = first["RECORDS.md"].decode()
        self.assertIn("| 1 | — | dropped: schema |", table)
        self.assertIn("Selected array span: characters 0-%d of %d" % (len(raw), len(raw)), table)


class Transcript(unittest.TestCase):
    def session(self, root: str, tool_use=False, prompt=None) -> tuple[str, str, str]:
        prompt = prompt if prompt is not None else open(
            os.path.join(STUDY, "transcription", "PROMPT.txt"), encoding="utf-8").read()
        completion = json.dumps([{"caseId": "z"}])
        entries = [
            {"type": "session_meta", "payload": {"session_id": "t"}},
            {"type": "response_item", "payload": {"type": "message", "role": "user",
                                                  "content": [{"type": "input_text", "text": "boilerplate"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user",
                                                  "content": [{"type": "input_text", "text": prompt}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "assistant",
                                                  "content": [{"type": "output_text", "text": "working"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "assistant",
                                                  "content": [{"type": "output_text", "text": completion}]}},
        ]
        if tool_use:
            entries.insert(3, {"type": "response_item",
                               "payload": {"type": "function_call", "name": "shell"}})
        session_path = os.path.join(root, "session.jsonl")
        with open(session_path, "w") as handle:
            for entry in entries:
                handle.write(json.dumps(entry) + "\n")
        completion_path = os.path.join(root, "completion.txt")
        with open(completion_path, "wb") as handle:
            handle.write(completion.encode())
        call_path = os.path.join(root, "CALL.json")
        with open(call_path, "w") as handle:
            json.dump({"exitStatus": 0}, handle)
        return session_path, completion_path, call_path

    def test_the_binding_admits_the_faithful_retention_only(self):
        prompt_path = os.path.join(STUDY, "transcription", "PROMPT.txt")
        with tempfile.TemporaryDirectory() as root:
            session, completion, call = self.session(root)
            transcript_check.check(session, prompt_path, completion, call)
            self.assertEqual(transcript_check.extract_completion(session),
                             open(completion).read())
            with open(completion, "ab") as handle:
                handle.write(b"tampered")
            with self.assertRaises(transcript_check.TranscriptError):
                transcript_check.check(session, prompt_path, completion, call)
        with tempfile.TemporaryDirectory() as root:
            session, completion, call = self.session(root, tool_use=True)
            with self.assertRaises(transcript_check.TranscriptError):
                transcript_check.check(session, prompt_path, completion, call)
        with tempfile.TemporaryDirectory() as root:
            session, completion, call = self.session(root, prompt="something else")
            with self.assertRaises(transcript_check.TranscriptError):
                transcript_check.check(session, prompt_path, completion, call)


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
            lambda r: r["clauses"][0]["claim"]["facts"][3].update(
                {"from": "/vendor/oracleRisk"}),
            lambda r: r["clauses"][0]["claim"]["facts"].pop(1),
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
            self.assertEqual(row["facts"], {"vendor": {
                "sanctionsHit": False, "registeredCountry": "NL",
                "handlesPersonalData": False, "riskScore": "33"}})
            self.assertEqual(row["expectedDisposition"]["outcomeId"], "reject")


class Mechanics(unittest.TestCase):
    def test_apply_patch_requires_the_preimage(self):
        pack = {"rules": [{"when": {"op": "x"}}]}
        with self.assertRaises(study.StudyError):
            study.apply_patch(pack, [{"path": "/rules/0/when/op", "old": "y", "new": "z"}])
        patched = study.apply_patch(pack, [{"path": "/rules/0/when/op", "old": "x", "new": "z"}])
        self.assertEqual(patched["rules"][0]["when"]["op"], "z")
        self.assertEqual(pack["rules"][0]["when"]["op"], "x")

    def test_the_draw_index_recomputes_and_rejects_bad_widths(self):
        preimage, index = study.draw_index("ab" * 32, "cd" * 20, "ef" * 32)
        self.assertTrue(preimage.startswith(b"study-010-draw-v1\n"))
        self.assertIn(index, range(6))
        again, same = study.draw_index("ab" * 32, "cd" * 20, "ef" * 32)
        self.assertEqual((preimage, index), (again, same))
        with self.assertRaises(study.StudyError):
            study.draw_index("ab" * 31, "cd" * 20, "ef" * 32)
        with self.assertRaises(study.StudyError):
            study.draw_index("ab" * 32, "cd" * 19, "ef" * 32)

    def test_acquisition_check_binds_artifact_to_record(self):
        with tempfile.TemporaryDirectory() as root:
            store, key, refs = acquire_throwaway(root, THROWAWAY)
            # The frozen-record equality is checked against the study's own
            # record dirs, so a throwaway case id must be refused there —
            # which is the binding working, exercised without frozen fixtures.
            with self.assertRaises((study.StudyError, FileNotFoundError)):
                study.check_acquisition(store, key, refs)
            ok, findings = attest.verify(store, key, expected_authority=study.AUTHORITY)
            self.assertTrue(ok, findings)


if __name__ == "__main__":
    unittest.main()
