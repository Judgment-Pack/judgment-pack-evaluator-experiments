"""The execution layer's own arithmetic — wire forms, payload reading, the canary.

Section 7 forbids invoking `codex`, `jpack` or `opa` in CI, so what is exercised
here is everything the layer decides BEFORE and AFTER a subprocess: how an input
point becomes a wire document, how a payload becomes a scored-surface tuple, and
what the capabilities gate concludes from a check's exit status. The flags
themselves are pinned by `design/TOOLCHAIN-NOTES.md` and re-verified at attempt
time, and `test_the_registered_flags_are_carried_verbatim` asserts the argv this
module would build rather than running it.
"""
import json

from e4lib import engines


class StubTools:
    jpack = "/pins/jpack"
    opa = "/pins/opa"
    caps = "/pins/caps.json"


# --- the wire forms ---------------------------------------------------------

def test_facts_documents_drop_unreadable_members_rather_than_nulling_them():
    """An OMITTED member is the wire form of "unreadable / unreported", and
    section 4's input-domain closure turns on that being a distinct state."""
    facts, evidence = engines.facts_documents(
        {"risk": "55", "spend": None, "country": "LOW", "finEvidence": "present",
         "insurance": None})
    assert facts == {"vendor": {"riskScore": "55", "countryRisk": "LOW"}}
    assert evidence == {"financial-evidence": "present"}


def test_the_rego_input_splices_numbers_exactly_from_the_decimal_strings():
    """Round-tripping `500000.01` through a float would put a binary
    approximation on one side of a `>` the policy tests — the silent boundary
    flip the mutant classes exist to detect."""
    document = engines.render_rego_input({"risk": "40", "spend": "500000.01",
                                          "country": "LOW"})
    assert '"requestedSpend": 500000.01' in document
    assert '"riskScore": 40' in document
    parsed = json.loads(document)
    assert parsed["vendor"]["requestedSpend"] == 500000.01
    assert parsed["evidence"] == {}


def test_the_rego_input_quotes_strings_and_omits_unreadables():
    document = engines.render_rego_input({"sanctions": "CLEAR",
                                          "country": None,
                                          "insurance": "absent"})
    parsed = json.loads(document)
    assert parsed["vendor"] == {"sanctionsStatus": "CLEAR"}
    assert parsed["evidence"] == {"insurance-certificate": "absent"}


def test_the_two_wire_forms_carry_the_same_members():
    """One naming appendix, two representations: a member present in one wire
    form and absent from the other would make the arms answer different
    questions."""
    inputs = {"risk": "40", "spend": "1.00", "sanctions": "CLEAR",
              "country": "LOW", "newVendor": "yes", "critical": "no",
              "prior": "no", "finEvidence": "present", "insurance": "present"}
    facts, evidence = engines.facts_documents(inputs)
    rendered = json.loads(engines.render_rego_input(inputs))
    assert set(facts["vendor"]) == set(rendered["vendor"])
    assert set(evidence) == set(rendered["evidence"])


# --- the scored surface -----------------------------------------------------

def test_scope_str_spells_every_scored_surface_shape():
    assert engines.scope_str(("outcome", "approve", ())) == "outcome:approve"
    assert engines.scope_str(("unresolved", None, ("no-match", "unknown"))) == \
        "unresolved:[no-match,unknown]"
    assert engines.scope_str(("ROW-ERROR", "engine-timeout", ())) == \
        "ROW-ERROR:engine-timeout"
    assert engines.scope_str(None) == "<unreadable-expectation>"


def test_a_pack_payload_becomes_the_scored_surface_and_nothing_else(monkeypatch,
                                                                    tmp_path):
    """`handoff` and `trace[]` are outside every endpoint (section 5) and are
    not read at all, so no later filter can forget to drop them."""
    monkeypatch.setattr(engines, "jpack_json", lambda *a, **k: (
        {"status": "evaluated",
         "disposition": {"kind": "outcome", "outcomeId": "review",
                         "reasons": []},
         "handoff": {"state": "pending", "target": "committee"},
         "trace": [{"rule": "r-d3"}]}, 0, "", ""))
    assert engines.eval_pack(StubTools(), "pack.json", {}, {},
                             str(tmp_path)) == ("outcome", "review", ())


def test_a_refused_evaluation_is_a_row_error_with_its_class(monkeypatch,
                                                            tmp_path):
    monkeypatch.setattr(engines, "jpack_json", lambda *a, **k: (
        {"status": "refused", "error": {"class": "facts-schema"}}, 1, "", ""))
    assert engines.eval_pack(StubTools(), "pack.json", {}, {},
                             str(tmp_path)) == ("ROW-ERROR", "facts-schema", ())


def test_a_non_json_payload_is_a_row_error_not_a_crash(monkeypatch, tmp_path):
    monkeypatch.setattr(engines, "jpack_json", lambda *a, **k: (None, 5, "", ""))
    assert engines.eval_pack(StubTools(), "pack.json", {}, {},
                             str(tmp_path))[1] == "non-json-payload"
    monkeypatch.setattr(engines, "jpack_json", lambda *a, **k: (None, 124, "", ""))
    assert engines.eval_pack(StubTools(), "pack.json", {}, {},
                             str(tmp_path))[1] == "engine-timeout"


def test_an_unresolved_pack_answer_sorts_its_reasons(monkeypatch, tmp_path):
    monkeypatch.setattr(engines, "jpack_json", lambda *a, **k: (
        {"status": "evaluated",
         "disposition": {"kind": "unresolved",
                         "reasons": ["unknown", "no-match"]}}, 0, "", ""))
    assert engines.eval_pack(StubTools(), "pack.json", {}, {}, str(tmp_path)) \
        == ("unresolved", None, ("no-match", "unknown"))


def test_a_rego_answer_becomes_the_same_three_tuple(monkeypatch, tmp_path):
    payload = json.dumps({"result": [{"expressions": [{"value": {
        "disposition": "review", "reasons": []}}]}]})
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (0, payload, ""))
    assert engines.eval_rego(StubTools(), "policy.rego", {}, str(tmp_path)) == \
        ("outcome", "review", ())


def test_a_rego_contract_violation_is_a_row_error(monkeypatch, tmp_path):
    payload = json.dumps({"result": [{"expressions": [{"value": {
        "disposition": 7, "reasons": []}}]}]})
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (0, payload, ""))
    assert engines.eval_rego(StubTools(), "policy.rego", {},
                             str(tmp_path))[1] == "contract-shape"
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (0, "{}", ""))
    assert engines.eval_rego(StubTools(), "policy.rego", {},
                             str(tmp_path))[1] == "undefined"


def test_rego_error_codes_are_recorded_and_message_prose_is_not(monkeypatch,
                                                                tmp_path):
    payload = json.dumps({"errors": [
        {"code": "eval_conflict_error", "message": "upstream prose"}]})
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (1, payload, ""))
    observed = engines.eval_rego(StubTools(), "policy.rego", {}, str(tmp_path))
    assert observed == ("ROW-ERROR", "eval_conflict_error", ())
    assert "upstream prose" not in engines.scope_str(observed)


# --- the flags, and the canary ----------------------------------------------

def test_the_registered_flags_are_carried_verbatim(monkeypatch, tmp_path):
    captured = {}

    def capture(argv, cwd, timeout=engines.ENGINE_TIMEOUT_S):
        captured["argv"] = argv
        return 0, "{}", ""
    monkeypatch.setattr(engines, "_run", capture)
    engines.eval_rego(StubTools(), "policy.rego", {}, str(tmp_path))
    argv = captured["argv"]
    for flag in ("eval", "--format", "json", "--fail", "--strict-builtin-errors",
                 "--capabilities", "--timeout"):
        assert flag in argv
    assert argv[-1] == engines.REGO_ENTRYPOINT
    assert "exec" not in argv, "opa exec does not accept --capabilities at v1.19.0"


def _opa_test(monkeypatch, tmp_path, code, out="", err=""):
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (code, out, err))
    return engines.opa_test(StubTools(), "p.rego", "s.rego", str(tmp_path))


def test_opa_test_reads_the_result_document_and_not_the_exit_status(monkeypatch,
                                                                    tmp_path):
    """ROUND-1 R1-8's enforcing test at the engine layer.

    The old table said exit 1 was a test failure and exit 2 an error; measured
    on the pinned OPA v1.19.0 it is the other way round, and
    `design/TOOLCHAIN-NOTES.md` ("a failing test exits **2**") and §2 were right
    all along. Nothing is keyed on the status now regardless: the result
    document is what says whether a test FAILED, and the exit status is carried
    only as a record."""
    passing = json.dumps([{"package": "data.s_test", "name": "test_ok"}])
    failing = json.dumps([{"package": "data.s_test", "name": "test_ok",
                           "fail": True}])
    errored = json.dumps([{"package": "data.s_test", "name": "test_ok",
                           "error": {"code": "eval_conflict_error"}}])
    # The same document under BOTH exit statuses gives the same answer: the
    # status is not consulted.
    for code in (0, 1, 2, 77):
        assert _opa_test(monkeypatch, tmp_path, code,
                         passing)["status"] == engines.TEST_PASS
        assert _opa_test(monkeypatch, tmp_path, code,
                         failing)["status"] == engines.TEST_FAILED
        assert _opa_test(monkeypatch, tmp_path, code,
                         errored)["status"] == engines.TEST_ERRORED


def test_opa_test_routes_every_non_suite_outcome_away_from_the_suite(monkeypatch,
                                                                     tmp_path):
    """A load/parse/compile failure emits no result list, a harness timeout
    emits nothing at all, and unreadable stdout is neither. None of the three is
    evidence about a suite, and `TEST_SUITE_STATUSES` is the two that are."""
    assert _opa_test(monkeypatch, tmp_path, 1, "", "1 error occurred")["status"] \
        == engines.TEST_INVOCATION_REFUSED
    assert _opa_test(monkeypatch, tmp_path, 124)["status"] == engines.TEST_TIMEOUT
    assert _opa_test(monkeypatch, tmp_path, 0, "{not a list}")["status"] \
        == engines.TEST_UNREADABLE
    assert engines.TEST_SUITE_STATUSES == (engines.TEST_PASS,
                                           engines.TEST_FAILED)


def test_opa_test_names_the_failing_tests_and_counts_them(monkeypatch, tmp_path):
    document = json.dumps([
        {"package": "data.s_test", "name": "a"},
        {"package": "data.s_test", "name": "b", "fail": True},
        {"package": "data.s_test", "name": "c", "fail": True}])
    record = _opa_test(monkeypatch, tmp_path, 2, document)
    assert record["tests"] == 3
    assert record["failed"] == ["data.s_test.b", "data.s_test.c"]
    assert record["errored"] == []
    assert record["exitCode"] == 2


def test_opa_test_asks_for_the_machine_readable_format(monkeypatch, tmp_path):
    seen = {}

    def capture(argv, cwd, timeout=None):
        seen["argv"] = argv
        return 0, "[]", ""

    monkeypatch.setattr(engines, "_run", capture)
    engines.opa_test(StubTools(), "p.rego", "s.rego", str(tmp_path))
    assert "--format" in seen["argv"]
    assert seen["argv"][seen["argv"].index("--format") + 1] == "json"


def test_opa_parse_asks_the_pinned_binary_for_the_syntax_tree(monkeypatch,
                                                              tmp_path):
    """Round-1 R1-3: arms B/C's case inputs are enumerated from the parser's own
    tree, and parsing is a syntax operation that takes no capabilities file."""
    seen = {}

    def capture(argv, cwd, timeout=None):
        seen["argv"] = argv
        return 0, "{}", ""

    monkeypatch.setattr(engines, "_run", capture)
    code, raw = engines.opa_parse(StubTools(), "s.rego", str(tmp_path))
    assert code == 0 and raw == b"{}"
    assert seen["argv"][1:] == ["parse", "--format", "json", "s.rego"]
    assert "--capabilities" not in seen["argv"]


def test_the_canary_gate_passes_only_when_the_canary_is_refused(monkeypatch,
                                                               tmp_path):
    """"The canary passed" reads both ways in English, and section 5 spells the
    FAILURE as "capabilities canary passes" — so the record says `refused`."""
    monkeypatch.setattr(engines, "opa_check",
                        lambda *a, **k: (1, ["rego_type_error"]))
    assert engines.capabilities_canary(StubTools(), str(tmp_path))["refused"]
    monkeypatch.setattr(engines, "opa_check", lambda *a, **k: (0, []))
    assert not engines.capabilities_canary(StubTools(), str(tmp_path))["refused"]


def test_the_canary_source_lives_in_this_reviewed_module():
    """A gate whose probe is a data file can be defanged by editing a fixture."""
    assert "time.now_ns" in engines.CANARY_REGO
    assert "import rego.v1" in engines.CANARY_REGO
