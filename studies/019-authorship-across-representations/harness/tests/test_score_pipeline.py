"""The assembled pipeline, end to end, against the REAL pinned engines.

Every other `test_score_*` module stubs the subprocess, because section 7 says
"CI runs the deterministic controls only" and "the batch never runs in CI".
This module is the other half of that discipline: `harness/SCAFFOLD.md` item T1
records the exact failure mode of hand-verification —

    "which is evidence and not a suite: nothing in the repository re-runs it"

— so the hand-verification that admitted a reference pack through the real
`jpack`, evaluated 105 gold rows, ran the identity control through the real
`opa test`, and watched the `v0-syntax` discriminator fire on a real v0 policy is
written down HERE, where something re-runs it.

It SKIPS unless `JPACK_BIN`, `OPA_BIN` and `OPA_CAPS` are set AND hash to the
digests `harness/PINS.json` pins. Skipping is the correct CI behaviour and not a
weakness: an unpinned binary must never satisfy this suite, and the skip reason
names the pin that was not met.

The fixtures are the DESIGN artifacts — `design/reference/refA/pack.json`,
`design/reference/refB/policy.rego`, `design/gold/gold.json` and one pilot
suite. They are non-citable as study data (BRIEF.md 4.2) and nothing here cites
them: what is asserted is that the HARNESS works, never a rate.
"""
import json
import os

import pytest

import score
from e4lib import e4
from e4lib import engines

DESIGN = os.path.join(score.STUDY, "design")
PILOT_SUITE = os.path.join(
    DESIGN, "pilots", "2026-08-15-calibration-pilot-01", "arm-B", "run-005",
    "secondary.rego")


def _pins():
    with open(score.PINS_PATH, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _skip_reason():
    pins = _pins()
    tools = engines.Toolchain(pins)
    if tools.problems:
        return "the pinned engines are not available: " + tools.problems[0]
    for path in (os.path.join(DESIGN, "gold", "gold.json"),
                 os.path.join(DESIGN, "reference", "refA", "pack.json"),
                 os.path.join(DESIGN, "reference", "refB", "policy.rego"),
                 PILOT_SUITE):
        if not os.path.isfile(path):
            return "the design fixture %s is absent" % os.path.basename(path)
    return None


pytestmark = pytest.mark.skipif(_skip_reason() is not None,
                                reason=_skip_reason() or "")


@pytest.fixture(scope="module")
def tools():
    return engines.Toolchain(_pins()).require()


@pytest.fixture(scope="module")
def gold():
    with open(os.path.join(DESIGN, "gold", "gold.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))["rows"]


@pytest.fixture(scope="module")
def context(gold):
    return {"gold": gold, "mutants": {"jps": [], "rego": []},
            "pairedIds": {"jps": set(), "rego": set()}, "pairedCount": 0,
            # Section 4's engine-supplied-kill split, empty here because this
            # fixture carries no mutants: the scorer takes the list from the
            # frozen manifests and `kill_rates()` splits the paired subset on
            # it, so the member is REQUIRED rather than defaulted — a context
            # without it is a scorer that would silently publish one column.
            "engineSupplied": {"jps": (), "rego": ()},
            "referenceA": os.path.join(DESIGN, "reference", "refA", "pack.json"),
            "referenceB": os.path.join(DESIGN, "reference", "refB",
                                       "policy.rego")}


def slot(arm, completion, index=1):
    return {"arm": arm, "slotIndex": index, "globalIndex": index, "round": index,
            "position": 1, "present": True, "code": None,
            "durationSeconds": 1.0, "completion": completion}


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def arm_a_completion(gold, rows=3):
    """A reference pack plus a matrix drawn from the gold rows themselves — the
    identity control must pass on it by construction, which is what makes a
    FAILURE here a harness defect rather than an authoring outcome."""
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
    matrix = json.dumps({"matrixVersion": 2, "cases": cases}, indent=1)
    pack = read(os.path.join(DESIGN, "reference", "refA", "pack.json"))
    return "PACK:\n```json\n%s\n```\n\nMATRIX:\n```json\n%s\n```\n" % (pack,
                                                                       matrix)


def arm_rego_completion():
    policy = read(os.path.join(DESIGN, "reference", "refB", "policy.rego"))
    suite = read(PILOT_SUITE)
    return "POLICY:\n```rego\n%s\n```\n\nTESTS:\n```rego\n%s\n```\n" % (policy,
                                                                        suite)


# --- the control gate -------------------------------------------------------

def test_the_capabilities_canary_is_refused_by_the_pinned_capabilities(tools,
                                                                       tmp_path):
    """Section 2, re-verified at attempt time: "the `time.now_ns` canary must be
    refused". A canary that compiled would mean the capabilities file constrains
    nothing."""
    canary = engines.capabilities_canary(tools, str(tmp_path))
    assert canary["refused"] is True
    assert canary["errorCodes"] == ["rego_type_error"]


# --- arm A, whole ------------------------------------------------------------

def test_arm_a_admits_evaluates_and_passes_identity(tools, gold, context,
                                                    tmp_path):
    run = score.score_run(tools, "A", slot("A", arm_a_completion(gold)),
                          context, str(tmp_path))
    assert run["code"] is None
    assert run["admitted"] is True
    assert run["goldFailures"] == []
    assert run["goldPerfect"] is True
    assert run["identityPass"] is True
    assert run["caseCount"] == 3
    assert run["kill"]["paired"] == 0


def test_arm_a_evaluates_every_gold_row(tools, gold, context, tmp_path):
    """The E1 denominator is the whole gold suite, not a sample of it."""
    run = score.score_run(tools, "A", slot("A", arm_a_completion(gold)),
                          context, str(tmp_path))
    assert len(gold) > 100
    assert run["goldPerfect"] is True


def test_a_non_json_pack_is_the_unparseable_authoring_code(tools, context,
                                                           tmp_path):
    run = score.score_run(tools, "A", slot("A", "PACK:\n```json\n{ nope\n```\n"),
                          context, str(tmp_path))
    assert run["code"] == "unparseable-artifact"
    assert run["admitted"] is False


def test_a_schema_invalid_pack_is_the_schema_code(tools, context, tmp_path):
    """The real `jpack spec validate`, read through the payload's `status` and
    never through the exit code (section 2)."""
    run = score.score_run(tools, "A",
                          slot("A", 'PACK:\n```json\n{"specVersion": "0.2.0-draft"}\n```\n'),
                          context, str(tmp_path))
    assert run["code"] == "schema-invalid-pack"
    assert run["admissionDetail"]["validateStatus"] != "valid"


# --- arms B/C, whole ---------------------------------------------------------

def test_arm_b_admits_evaluates_and_passes_identity(tools, context, tmp_path):
    run = score.score_run(tools, "B", slot("B", arm_rego_completion()),
                          context, str(tmp_path))
    assert run["code"] is None
    assert run["admitted"] is True
    assert run["goldFailures"] == []
    assert run["identityPass"] is True


def test_the_v0_discriminator_fires_against_the_real_pinned_opa(tools, context,
                                                                tmp_path):
    """Section 2 pins Rego v1 in the prompt AND the invocation, so a v0 policy is
    a registered authoring outcome distinct from a garbled one. The
    discriminator is two compilations of the same bytes and no string matching
    on upstream's message prose."""
    run = score.score_run(tools, "C",
                          slot("C", "POLICY:\n```rego\npackage study\np[x] { x := 1 }\n```\n"),
                          context, str(tmp_path))
    assert run["code"] == "v0-syntax"
    assert run["admissionDetail"]["checkErrorCodes"] == ["rego_parse_error"]
    assert run["admissionDetail"]["v0CompatibleExit"] == 0


def test_a_type_error_is_the_opa_check_code_not_the_v0_one(tools, context,
                                                           tmp_path):
    run = score.score_run(
        tools, "B",
        slot("B", "POLICY:\n```rego\npackage study\nimport rego.v1\n"
                  "p if { nosuchbuiltin(1) }\n```\n"),
        context, str(tmp_path))
    assert run["code"] == "opa-check-failed"


# --- the kill machinery, against a real mutant -------------------------------

def test_a_real_rego_mutant_is_killed_by_the_reference_suite(tools, tmp_path):
    """`opa test <mutant> <suite>` exits nonzero and the class is recorded."""
    mutant = os.path.join(DESIGN, "mutants", "refB", "m-b-001.rego")
    if not os.path.isfile(mutant):
        pytest.skip("design mutant m-b-001.rego is absent")
    killed, detail = e4.kill_arm_rego(tools, mutant, PILOT_SUITE, str(tmp_path))
    assert detail["class"] in ("pass", "test-failure", "error")
    assert killed == (detail["exitCode"] != 0)


def test_the_reference_policy_is_not_killed_by_its_own_suite(tools, tmp_path):
    """The identity control's other side: a suite that killed the unmutated
    reference would be pinning something the reference does not do."""
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    killed, detail = e4.kill_arm_rego(tools, reference, PILOT_SUITE,
                                      str(tmp_path))
    assert killed is False and detail["exitCode"] == 0


# --- the reference-vs-gold floor gate, RUN (SCAFFOLD item S10) ---------------

def test_the_floor_gate_runs_over_both_references_and_holds(tools, gold,
                                                            tmp_path):
    """Section 4's floor gate and section 6's first control row, executed rather
    than asserted. It was stamped `held: true` with a note while it was unwired,
    and section 6 exists to prevent exactly that: a gate that reports its own
    success is not a gate.

    Both references, every gold row, through the same two invocations every
    other number in an attempt is produced by."""
    gate = score.references_reproduce_gold(
        tools, gold,
        os.path.join(DESIGN, "reference", "refA", "pack.json"),
        os.path.join(DESIGN, "reference", "refB", "policy.rego"),
        str(tmp_path))
    assert gate["rows"] == len(gold)
    assert gate["failureCount"] == 0, gate["failures"][:3]
    assert gate["held"] is True


def test_the_floor_gate_fails_closed_against_a_reference_that_disagrees(
        tools, gold, tmp_path):
    """The gate has power: a MUTANT standing in for the arm-B reference makes it
    fail, and it names the rows and the reference rather than a boolean."""
    mutant = os.path.join(DESIGN, "mutants", "refB", "m-b-001.rego")
    if not os.path.isfile(mutant):
        pytest.skip("design mutant m-b-001.rego is absent")
    gate = score.references_reproduce_gold(
        tools, gold,
        os.path.join(DESIGN, "reference", "refA", "pack.json"),
        mutant, str(tmp_path))
    assert gate["held"] is False
    assert gate["failureCount"] > 0
    assert {failure["reference"] for failure in gate["failures"]} == {"B"}
