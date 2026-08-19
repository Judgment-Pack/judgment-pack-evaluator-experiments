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

# The reviewer's R2-4 residual suite, retained as bytes so the probe in
# this file is the construction the review published and not a paraphrase.
DECOY_SUITE = 'package residual_dynamic_test\nimport rego.v1\n\ndecoy := {"vendor": {"sanctionsStatus": "CLEAR"}}\n\nmake_bad(nv) := {\n\t"vendor": {\n\t\t"sanctionsStatus": "CLEAR",\n\t\t"countryRisk": "LOW",\n\t\t"riskScore": 50,\n\t\t"requestedSpend": 50000,\n\t\t"newVendor": nv,\n\t\t"criticalSupplier": "no",\n\t\t"priorEnforcement": "no",\n\t},\n\t"evidence": {\n\t\t"financial-evidence": "present",\n\t\t"insurance-certificate": "present",\n\t},\n}\n\ntest_dynamic_case if {\n\tbuilt := make_bad(7)\n\tdata.study.decision == {"disposition": "approve", "reasons": []} with input as built\n}\n'
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
    # The REGISTERED spelling is the STRING (round-2 R2-6): the prompt says
    # "`matrixVersion`: the string `"2"`" and every real pilot matrix emits it.
    matrix = json.dumps({"matrixVersion": "2", "cases": cases}, indent=1)
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
    """ROUND-1 R1-8, against the real pinned binary: the KILL is an assertion
    failure in the result document, not a nonzero exit."""
    mutant = os.path.join(DESIGN, "mutants", "refB", "m-b-001.rego")
    if not os.path.isfile(mutant):
        pytest.skip("design mutant m-b-001.rego is absent")
    outcome, record = e4.kill_arm_rego(tools, mutant, PILOT_SUITE,
                                       str(tmp_path))
    assert outcome == e4.KILLED
    assert record["status"] == engines.TEST_FAILED
    assert record["failed"]
    # And the measured taxonomy: an ordinary test failure exits 2 on this
    # binary, which is what `design/TOOLCHAIN-NOTES.md` and §2 always said.
    assert record["exitCode"] == 2


def test_the_measured_opa_test_exit_taxonomy_is_the_registered_one(tools,
                                                                   tmp_path):
    """The empirical half of R1-8, settled on the pinned binary rather than
    argued: 0 = every test passed, 2 = at least one FAILED, 1 = the invocation
    never ran the tests. The code's old `{1: test-failure, 2: error}` table was
    the document that was wrong."""
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    broken = tmp_path / "broken_test.rego"
    broken.write_text("package broken_test\n{{{\n")
    assert e4.kill_arm_rego(tools, reference, PILOT_SUITE,
                            str(tmp_path))[1]["exitCode"] == 0
    refused = engines.opa_test(tools, reference, str(broken), str(tmp_path))
    assert refused["exitCode"] == 1
    assert refused["status"] == engines.TEST_INVOCATION_REFUSED
    # …and a compile failure is a REFUSAL, never a kill: under the old rule
    # "nonzero kills" this mutant would have been killed by a suite that never
    # ran a single assertion against it.
    assert e4.kill_arm_rego(tools, reference, str(broken),
                            str(tmp_path))[0] == e4.REFUSED


def test_the_reference_policy_is_not_killed_by_its_own_suite(tools, tmp_path):
    """The identity control's other side: a suite that killed the unmutated
    reference would be pinning something the reference does not do."""
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    outcome, record = e4.kill_arm_rego(tools, reference, PILOT_SUITE,
                                       str(tmp_path))
    assert outcome == e4.SURVIVED and record["exitCode"] == 0


def test_the_rego_case_inputs_are_enumerated_and_domain_checked(tools,
                                                                tmp_path):
    """ROUND-1 R1-3, against the REAL pilot suites: arms B/C used to receive no
    case-level validation at all, and the certificate's supplementary stratum
    measured 18,954 reference divergences outside the registered domain.

    The pilot's own suites are table-driven — `with input as tc.given` over a
    table whose evidence members are named constants — so both enumeration modes
    are exercised here, and both answers come from the pinned binary."""
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    named = e4.rego_case_signatures(tools, PILOT_SUITE, str(tmp_path),
                                    reference)
    assert len(named) > 20
    assert all(isinstance(signature, dict) for _name, signature in named)
    assert e4.domain_failures(named, "number") == []


def test_an_out_of_domain_rego_case_is_caught_and_named(tools, tmp_path):
    """A suite asserting about `sanctionsStatus` physically absent is asserting
    about the labelled supplementary stratum — the space where the two
    references stop agreeing."""
    suite = tmp_path / "off_domain_test.rego"
    suite.write_text(
        "package off_domain_test\n"
        "import rego.v1\n"
        "test_off if {\n"
        '  data.study.decision.disposition == "review" '
        'with input as {"vendor": {"riskScore": 50}}\n'
        "}\n")
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    named = e4.rego_case_signatures(tools, str(suite), str(tmp_path), reference)
    failures = e4.domain_failures(named, "number")
    assert len(failures) == 1
    assert failures[0]["got"] == e4.OUT_OF_DOMAIN
    assert any("sanctions is omitted" in problem
               for problem in failures[0]["problems"])


def test_a_prompt_conforming_matrix_is_the_one_the_loader_accepts(tools, gold,
                                                                  tmp_path):
    """ROUND-2 R2-6, against the prompt's own bytes.

    `design/prompts/ARM-A-INSTRUCTIONS.md` registers `matrixVersion` as the
    STRING "2", the arm-A excerpt's examples emit it, and so does every real
    pilot matrix. The loader registered the INTEGER, so a prompt-conforming
    matrix was refused as `unparseable-artifact` and scored zero — the primary
    endpoint was unreachable for arm A, exactly as R1-1's single cut made it
    unreachable for arms B and C. The old tests missed it because they were
    written against the loader rather than against the prompt."""
    instructions = read(os.path.join(DESIGN, "prompts",
                                     "ARM-A-INSTRUCTIONS.md"))
    assert '`matrixVersion`: the string `"2"`' in instructions
    assert e4.MATRIX_VERSION == "2"
    real = os.path.join(DESIGN, "pilots", "2026-08-15-calibration-pilot-01",
                        "arm-A", "run-008", "secondary.json")
    if os.path.isfile(real):
        _cases, note = e4.load_matrix(real)
        assert note["matrixVersion"] == "2"
    numeric = tmp_path / "as_the_loader_used_to_say.json"
    numeric.write_text(json.dumps({"matrixVersion": 2, "cases": []}))
    with pytest.raises(e4.MatrixError) as raised:
        e4.load_matrix(str(numeric))
    assert "registered spelling" in str(raised.value)


# --- ROUND-2 R2-3 and R2-4, against the pinned binary -----------------------

def test_an_evaluation_fault_on_a_mutant_refuses_and_is_not_a_kill(tools,
                                                                   tmp_path):
    """THE REVIEWER'S R2-3 PROBE, executed.

    `opa test` has no `--strict-builtin-errors` at v1.19.0, so a division by
    zero inside a test body is not an error: the expression is undefined, the
    body is undefined, and the test reports `fail: true` with no `error` member.
    A reference-passing test therefore "killed" every mutant that faulted it.
    Three policies here — the value the test expects, a zero that faults, and a
    value that simply disagrees — and the three answers must be
    survived / refused / killed."""
    suite = tmp_path / "fault_test.rego"
    suite.write_text("package study_test\nimport rego.v1\n"
                     "test_div if {\n  1 / data.study.denominator == 1\n}\n")
    answers = {}
    for label, value in (("reference", 1), ("faulting-mutant", 0),
                         ("disagreeing-mutant", 5)):
        policy = tmp_path / ("%s.rego" % label)
        policy.write_text("package study\nimport rego.v1\n"
                          "denominator := %d\n" % value)
        record = engines.opa_test(tools, str(policy), str(suite), str(tmp_path))
        outcome, _r = e4.kill_arm_rego(tools, str(policy), str(suite),
                                       str(tmp_path))
        answers[label] = (record["status"], outcome,
                          [f["fault"] for f in record["evaluationFaults"]])
    assert answers["reference"] == (engines.TEST_PASS, e4.SURVIVED, [])
    assert answers["faulting-mutant"] == (engines.TEST_ERRORED, e4.REFUSED,
                                          ["eval_builtin_error"])
    assert answers["disagreeing-mutant"] == (engines.TEST_FAILED, e4.KILLED, [])


def test_an_explicit_null_in_a_rego_case_is_out_of_domain(tools, tmp_path):
    """ROUND-2 R2-4, first half, through the pinned parser. A suite using
    `newVendor: null` passed domain validation and identity validation and
    killed four paired mutants."""
    suite = tmp_path / "explicit_null_test.rego"
    suite.write_text(
        "package explicit_null_test\nimport rego.v1\n"
        "test_null if {\n"
        '  data.study.decision.disposition == "approve" with input as '
        '{"vendor": {"sanctionsStatus": "CLEAR", "countryRisk": "LOW", '
        '"riskScore": 50, "requestedSpend": 50000, "newVendor": null, '
        '"criticalSupplier": "no", "priorEnforcement": "no"}, '
        '"evidence": {"financial-evidence": "present"}}\n'
        "}\n")
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    named = e4.rego_case_signatures(tools, str(suite), str(tmp_path), reference)
    failures = e4.domain_failures(named, "number")
    assert len(failures) == 1
    assert failures[0]["got"] == e4.OUT_OF_DOMAIN
    assert any("carrying a JSON null" in problem
               for problem in failures[0]["problems"])


def test_an_unrelated_decoy_literal_cannot_certify_a_dynamic_input(tools,
                                                                   tmp_path):
    """THE REVIEWER'S R2-4 SUITE, as written.

    The decoy makes the file's aggregate of input-shaped literals non-empty, so
    the enumeration accepted the suite and never validated the point the test
    actually asserts about — `newVendor: 7` — which then earned four paired
    kills. Enumeration is per term now: the term resolves or the suite is the
    registered authoring code."""
    suite = tmp_path / "residual_dynamic_test.rego"
    suite.write_text(DECOY_SUITE)
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    with pytest.raises(e4.MatrixError) as raised:
        e4.rego_case_signatures(tools, str(suite), str(tmp_path), reference)
    assert "does not stand in for them" in str(raised.value)


def test_the_real_pilot_suites_still_enumerate_under_the_per_term_rule(
        tools, tmp_path):
    """The per-term rule must not refuse the shapes real authored suites use: a
    `some name, tc in cases` table, package-level named constants, and a
    `decision_for(doc)` helper whose parameter is bound at its call sites."""
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    root = os.path.join(DESIGN, "pilots", "2026-08-15-calibration-pilot-01")
    suites = [os.path.join(root, arm, run, "secondary.rego")
              for arm in ("arm-B", "arm-C")
              for run in sorted(os.listdir(os.path.join(root, arm)))
              if os.path.isfile(os.path.join(root, arm, run,
                                             "secondary.rego"))]
    assert len(suites) >= 10
    for path in suites:
        named = e4.rego_case_signatures(tools, path, str(tmp_path), reference)
        assert len(named) > 20, path


def test_a_suite_whose_points_cannot_be_recovered_is_the_authoring_code(
        tools, tmp_path):
    """Never a silent pass: a suite that computes its inputs and leaves no
    literal and no resolvable rule behind is the registered authoring
    outcome."""
    suite = tmp_path / "opaque_test.rego"
    suite.write_text(
        "package opaque_test\n"
        "import rego.v1\n"
        "test_opaque if {\n"
        "  some k in numbers.range(1, 2)\n"
        "  built := {\"vendor\": {\"riskScore\": k}}\n"
        "  data.study.decision with input as built\n"
        "}\n")
    reference = os.path.join(DESIGN, "reference", "refB", "policy.rego")
    with pytest.raises(e4.MatrixError) as raised:
        e4.rego_case_signatures(tools, str(suite), str(tmp_path), reference)
    assert str(raised.value).startswith("E4-MATRIX-SCHEMA")


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
