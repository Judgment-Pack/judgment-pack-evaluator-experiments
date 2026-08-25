"""ROUND-1 FINDING R1-13's integration test: the scorer's records reach the
sealed holdout THROUGH THE PRODUCTION PATH, with no fabricated dict anywhere.

The finding: `score_run()` wrote `identityPass` while `reviewer.execute()`
selected `referenceIdentityPass`, so the fresh sealed set would have executed
against ZERO production runs in every arm — and 94 reviewer tests passed,
because every one of them hand-wrote the key the consumer reads. This file is
the test that could not have passed: a REAL `score_run()` output, admitted and
reference-identity-passing against the pinned engines, must be scored by
`reviewer.execute()` — and the module-level skip that hides
`test_score_pipeline.py` in most environments (an absent arm-B pilot fixture)
is deliberately not inherited, because arm A alone is enough to bind the
producer to the consumer.

This file lives beside `test_score_reviewer.py` rather than inside it so the
schema-validation cases there (which still fabricate records ON PURPOSE, to
drive the refusals) stay visibly separate from the one case that must not."""

import json
import os

import pytest

import score
from e4lib import e4
from e4lib import engines
from e4lib import reviewer

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
DESIGN = os.path.join(STUDY, "design")
GOLD = os.path.join(DESIGN, "gold", "gold.json")
REF_A = os.path.join(DESIGN, "reference", "refA", "pack.json")


def _skip_reason():
    if not os.environ.get("JPACK_BIN") or not os.environ.get("OPA_BIN"):
        return "the pinned binaries are not present (§7 forbids invoking " \
               "them in CI)"
    for path in (GOLD, REF_A):
        if not os.path.isfile(path):
            return "the design fixture %s is absent" % os.path.relpath(
                path, STUDY)
    return None


pytestmark = pytest.mark.skipif(_skip_reason() is not None,
                                reason=_skip_reason() or "")


def _pins():
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _arm_a_completion(gold, rows=3):
    cases = []
    for row in gold[:rows]:
        facts, evidence = engines.facts_documents(row["inputs"])
        expected = ({"kind": "unresolved",
                     "reasons": sorted(row["expect"]["reasons"])}
                    if row["expect"]["disposition"] == "unresolved"
                    else {"kind": "outcome",
                          "outcomeId": row["expect"]["disposition"]})
        cases.append({"id": row["id"], "facts": facts,
                      "evidenceAvailability": evidence,
                      "expectedDisposition": expected})
    matrix = json.dumps({"matrixVersion": "2", "cases": cases}, indent=1)
    with open(REF_A, encoding="utf-8") as handle:
        pack = handle.read()
    return "PACK:\n```json\n%s\n```\n\nMATRIX:\n```json\n%s\n```\n" % (pack,
                                                                       matrix)


def test_a_real_scored_run_is_executed_by_the_sealed_holdout(tmp_path):
    """Producer to consumer with production bytes in between. Mutation checks,
    both of which were LIVE defects: rename either side's identity member and
    the schema refusal fires here (never a silent zero-run execution); make
    `reviewer.execute()` skip an eligible run and the short-execution refusal
    fires."""
    tools = engines.Toolchain(_pins()).require()
    with open(GOLD, "rb") as handle:
        gold = json.loads(handle.read().decode("utf-8"))["rows"]
    context = {"gold": gold, "mutants": {"jps": [], "rego": []},
               "pairedIds": {"jps": set(), "rego": set()}, "pairedCount": 0,
               "engineSupplied": {"jps": (), "rego": ()}, "classes": [],
               "referenceA": REF_A,
               "referenceB": os.path.join(DESIGN, "reference", "refB",
                                          "policy.rego")}
    slot = {"arm": "A", "slotIndex": 1, "globalIndex": 1, "round": 1,
            "position": 1, "present": True, "code": None,
            "durationSeconds": 1.0,
            "completion": _arm_a_completion(gold)}
    run = score.score_run(tools, "A", slot, context, str(tmp_path))
    assert run["code"] is None
    assert run["referenceIdentityPass"] is True, (
        "the production record must carry the registered member name")
    assert "identityPass" not in run, (
        "the superseded 019 spelling must not survive in a 020 record")
    sealed = {"version": reviewer.SET_VERSION, "manifestSha256": "0" * 64,
              "mutants": [{"id": "RV-JPS-001", "language": "jps",
                           "path": REF_A, "sha256": "0" * 64}],
              "count": 1, "executed": False}
    out = reviewer.execute(tools, sealed, {"A": [run]}, context, ["A"],
                           {"A": "jps"}, str(tmp_path))
    assert out["perArm"]["A"]["scoredRuns"] == 1
    assert out["perArm"]["A"]["eligibleRuns"] == 1
    assert out["perArm"]["A"]["perRun"][0]["run"] == run["run"]
    # The reference pack IS the sealed "mutant" here, so the identity-passing
    # suite must fail to kill it — a survived outcome, which also proves the
    # engine actually ran rather than the row being presumed.
    assert out["perArm"]["A"]["perRun"][0]["survived"] == ["RV-JPS-001"]
    assert sealed["executed"] is True
    assert sealed["attempted"] is True


def test_an_unanswered_engine_excludes_the_run_and_fails_the_gate(
        tmp_path, monkeypatch):
    """ROUND-1 FINDING R1-1, end to end: a validator timeout during admission
    codes the run `engine-invocation-refused`, and the exclusion reaches §6's
    gate through the scoring-apparatus ledger. Mutation checks: file the state
    as an authoring code again and the first assertion fails; drop the
    invocation list from the gate's conjunction and the second does."""
    with open(GOLD, "rb") as handle:
        gold = json.loads(handle.read().decode("utf-8"))["rows"]
    context = {"gold": gold, "referenceA": REF_A}
    slot = {"arm": "A", "slotIndex": 1, "globalIndex": 1, "round": 1,
            "position": 1, "present": True, "code": None,
            "durationSeconds": 1.0,
            "completion": _arm_a_completion(gold)}
    monkeypatch.setattr(engines, "jpack_json",
                        lambda *a, **k: (None, 124, "", "",
                                         engines.invocation_refusal(124,
                                                                    False)))
    run = score.score_run(None, "A", slot, context, str(tmp_path))
    assert run["code"] == "engine-invocation-refused"
    assert run["admitted"] is False
    assert "engine-timeout" in run["invocationRefusal"]
    gate = score._engine_execution_gate(
        {"A": []}, {"A": [{"run": run["run"],
                           "refusal": run["invocationRefusal"]}]})
    assert gate["held"] is False
    assert gate["invocationRefusalCount"] == 1


def test_a_record_missing_the_registered_member_is_fatal(tmp_path):
    """R1-13's schema validation, driven: the exact drift that happened —
    a record carrying the 019 spelling — refuses loudly instead of skipping."""
    sealed = {"version": reviewer.SET_VERSION, "manifestSha256": "0" * 64,
              "mutants": [], "count": 0, "executed": False}
    legacy = {"run": "run-001", "identityPass": True,
              "suitePath": str(tmp_path / "suite.json")}
    with pytest.raises(reviewer.ReviewerSetError,
                       match="REVIEWER-RECORD-SCHEMA"):
        reviewer.execute(None, sealed, {"A": [legacy]}, {}, ["A"],
                         {"A": "jps"}, str(tmp_path))


def test_an_aborted_execution_cannot_run_again(tmp_path):
    """`attempted` marks the once-only promise at entry; `executed` only on
    completion. A crashed first execution must refuse a second, and must not
    read as completed."""
    sealed = {"version": reviewer.SET_VERSION, "manifestSha256": "0" * 64,
              "mutants": [], "count": 0, "executed": False}
    bad = {"run": "run-001"}
    with pytest.raises(reviewer.ReviewerSetError):
        reviewer.execute(None, sealed, {"A": [bad]}, {}, ["A"],
                         {"A": "jps"}, str(tmp_path))
    assert sealed.get("attempted") is True
    assert sealed.get("executed") is False
    with pytest.raises(reviewer.ReviewerSetError,
                       match="REVIEWER-SET-RE-EXECUTED"):
        reviewer.execute(None, sealed, {"A": []}, {}, ["A"],
                         {"A": "jps"}, str(tmp_path))
