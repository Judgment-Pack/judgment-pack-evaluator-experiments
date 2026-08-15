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


def test_opa_test_labels_every_registered_exit_status(monkeypatch, tmp_path):
    for code, label in ((0, "pass"), (1, "test-failure"), (2, "error"),
                        (124, "timeout"), (77, "other")):
        monkeypatch.setattr(engines, "_run",
                            lambda *a, _code=code, **k: (_code, "", ""))
        assert engines.opa_test(StubTools(), "p.rego", "s.rego",
                                str(tmp_path)) == (code, label)


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
