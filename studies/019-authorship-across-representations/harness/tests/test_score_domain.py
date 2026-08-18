"""The registered input domain, and the symmetric enumeration — round-1 R1-3.

The finding was that "the promised common input-domain and X1 filters do not
exist across arms": arm A's matrix was parsed and filtered, arms B/C handed the
scorer an opaque `opa test` file and received no case-level validation of any
kind. The certificate measured 18,954 reference divergences on inputs outside the
registered space, so a case nobody validated is a case on which the two arms'
references are not known to agree.

What is asserted here is the DOMAIN and the ENUMERATION, in both arms' wire
forms. The engine-backed half — the pinned parser and the pinned evaluator over
the real pilot suites — is in `tests/test_score_pipeline.py`, which skips without
the pinned binaries as §7 requires.
"""
import json
from decimal import Decimal

import pytest

from e4lib import domain
from e4lib import e4


def rego_signature(**vendor):
    base = {"sanctionsStatus": "CLEAR"}
    base.update(vendor)
    return domain.signature_from_documents(base, {})


def matrix_signature(**vendor):
    base = {"sanctionsStatus": "CLEAR"}
    base.update(vendor)
    return domain.signature_from_documents(base, {})


# --- the registered domain, axis by axis ------------------------------------

def test_a_point_inside_the_registered_space_has_no_problems():
    assert domain.domain_problems(
        rego_signature(riskScore=40, requestedSpend=Decimal("100000.01")),
        "number") == []
    assert domain.domain_problems(matrix_signature(riskScore="40",
                                                   requestedSpend="100000.01"),
                                  "string") == []


def test_an_omitted_axis_is_the_registered_encoding_of_unreadable():
    """"An input that is unreadable/unreported is an OMITTED MEMBER — never a
    null, never a sentinel string" (the naming appendix)."""
    assert domain.domain_problems(rego_signature(), "number") == []
    problems = domain.domain_problems(rego_signature(countryRisk=None),
                                      "number")
    assert problems == []


def test_sanctions_is_the_one_axis_with_no_omitted_state():
    """The certificate's own registered limit: "an input document with
    `/vendor/sanctionsStatus` physically absent is OUTSIDE this space", and the
    labelled supplementary stratum on that extension is exactly where the two
    references stop agreeing."""
    signature = domain.signature_from_documents({"riskScore": 10}, {})
    problems = domain.domain_problems(signature, "number")
    assert problems == ["sanctions is omitted and the registered domain admits "
                        "no unreadable state for it"]


@pytest.mark.parametrize("vendor,fragment", [
    ({"sanctionsStatus": "PENDING"}, "sanctions is 'PENDING'"),
    ({"countryRisk": "EXTREME"}, "country is 'EXTREME'"),
    ({"newVendor": "true"}, "newVendor is 'true'"),
    ({"criticalSupplier": True}, "critical is True"),
    ({"priorEnforcement": "maybe"}, "prior is 'maybe'"),
    ({"riskScore": 101}, "risk is 101 and the registered domain is 0..100"),
    ({"riskScore": -1}, "risk is -1 and the registered domain is 0..100"),
    ({"riskScore": Decimal("40.5")}, "integer 0..100"),
    ({"requestedSpend": Decimal("10000000.01")}, "0.00..10000000.00"),
    ({"requestedSpend": 100.005}, "binary float"),
    ({"requestedSpend": -1}, "0.00..10000000.00"),
])
def test_every_axis_refuses_a_value_outside_its_registered_domain(vendor,
                                                                  fragment):
    base = {"sanctionsStatus": "CLEAR"}
    base.update(vendor)
    problems = domain.domain_problems(
        domain.signature_from_documents(base, {}), "number")
    assert any(fragment in problem for problem in problems), problems


def test_an_evidence_value_outside_the_tri_state_is_out_of_domain():
    signature = domain.signature_from_documents(
        {"sanctionsStatus": "CLEAR"}, {"financial-evidence": "unknown"})
    assert any("finEvidence is 'unknown'" in problem
               for problem in domain.domain_problems(signature, "number"))


def test_an_unregistered_member_is_a_problem_in_its_own_right():
    """The registered input document has exactly these members, and a case that
    adds one is asserting about a fact this policy family does not carry."""
    signature = domain.signature_from_documents(
        {"sanctionsStatus": "CLEAR", "creditRating": "AA"}, {})
    assert any("vendor.creditRating is not a registered input member" in problem
               for problem in domain.domain_problems(signature, "number"))


# --- the two wire forms are one domain in two encodings ---------------------

def test_the_wire_forms_are_not_interchangeable():
    """The naming appendix registers decimal STRINGS for arm A and JSON NUMBERS
    for arms B/C. A coercion between them is precisely how `100000.01` becomes a
    float on one side of a threshold the policy tests with `>`."""
    as_number = rego_signature(riskScore=40,
                               requestedSpend=Decimal("100000.01"))
    as_string = matrix_signature(riskScore="40", requestedSpend="100000.01")
    assert domain.domain_problems(as_number, "number") == []
    assert domain.domain_problems(as_string, "string") == []
    assert domain.domain_problems(as_number, "string") != []
    assert domain.domain_problems(as_string, "number") != []


@pytest.mark.parametrize("spend", ["100000", "100000.0", "100000.001",
                                   "0100000.00", "1e5"])
def test_arm_a_spend_must_be_the_registered_decimal_string(spend):
    problems = domain.domain_problems(matrix_signature(requestedSpend=spend),
                                      "string")
    assert any("two decimals" in problem for problem in problems)


def test_an_unknown_wire_form_refuses_rather_than_guessing():
    with pytest.raises(domain.DomainError) as raised:
        domain.domain_problems(rego_signature(), "decimal")
    assert str(raised.value).startswith("DOMAIN-UNKNOWN-WIRE")


# --- the syntax-tree reading (no engine) ------------------------------------

def _object(pairs):
    return {"type": "object",
            "value": [[{"type": "string", "value": key}, value]
                      for key, value in pairs]}


def _string(value):
    return {"type": "string", "value": value}


def _number(value):
    return {"type": "number", "value": value}


def _with_input(term):
    return {"rules": [{"body": [{"terms": [], "with": [
        {"target": {"type": "ref",
                    "value": [{"type": "var", "value": "input"}]},
         "value": term}]}]}]}


def test_a_literal_with_input_term_is_a_direct_case():
    tree = _with_input(_object([
        ("vendor", _object([("sanctionsStatus", _string("CLEAR")),
                            ("riskScore", _number(40))]))]))
    indirect, cases = domain.cases_from_tree(tree)
    assert indirect == 0
    assert len(cases) == 1
    assert domain.domain_problems(cases[0][1], "number") == []


def test_a_partial_input_override_cannot_be_enumerated():
    """`with input.vendor as …` names a path into the document rather than the
    document, so the point it produces depends on what the rest of `input` was."""
    tree = {"rules": [{"body": [{"with": [
        {"target": {"type": "ref",
                    "value": [{"type": "var", "value": "input"},
                              {"type": "string", "value": "vendor"}]},
         "value": _object([])}]}]}]}
    with pytest.raises(domain.DomainError) as raised:
        domain.cases_from_tree(tree)
    assert str(raised.value).startswith("DOMAIN-UNENUMERABLE-CASE")


def test_a_named_term_is_indirect_until_the_name_is_resolved():
    """The table-driven mode. `with input as tc.given` carries a ref where the
    point is, and only the pinned evaluator resolves it."""
    tree = _with_input({"type": "ref",
                        "value": [{"type": "var", "value": "tc"},
                                  {"type": "string", "value": "given"}]})
    indirect, cases = domain.cases_from_tree(tree)
    assert indirect == 1 and cases == []


def test_a_package_level_name_resolves_into_a_literal_object():
    """`"evidence": financial_present` beside the table — the syntax tree
    carries a ref and the RESOLVED package document carries the value."""
    tree = _with_input(_object([
        ("vendor", _object([("sanctionsStatus", _string("CLEAR"))])),
        ("evidence", {"type": "var", "value": "financial_present"})]))
    names = {"financial_present": {"financial-evidence": "present"}}
    indirect, cases = domain.cases_from_tree(tree, names)
    assert indirect == 0
    assert cases[0][1]["finEvidence"] == "present"


def test_input_documents_nested_inside_a_case_table_are_found():
    """A case table converts whole, and the input documents live one level
    inside it — stopping at the outermost convertible object would collect the
    table and none of its cases."""
    table = _object([
        ("first", _object([
            ("input", _object([("vendor",
                                _object([("sanctionsStatus",
                                          _string("CLEAR"))]))])),
            ("want", _string("review"))])),
        ("second", _object([
            ("input", _object([("vendor",
                                _object([("sanctionsStatus",
                                          _string("MATCH"))]))])),
            ("want", _string("reject"))]))])
    tree = {"rules": [{"body": [{"terms": [table]}]}]}
    _indirect, cases = domain.cases_from_tree(tree)
    assert len(cases) == 2
    assert sorted(signature["sanctions"] for _index, signature in cases) == \
        ["CLEAR", "MATCH"]


def test_two_tests_over_one_input_point_are_one_point():
    one = _object([("vendor", _object([("sanctionsStatus", _string("CLEAR"))]))])
    tree = {"rules": [{"body": [{"terms": [_object([("a", one), ("b", one)])]}]}]}
    _indirect, cases = domain.cases_from_tree(tree)
    assert len(cases) == 1


def test_the_resolved_document_reading_decodes_numbers_exactly():
    """`requestedSpend` values sit on either side of a threshold the policy
    tests with `>`; a float round-trip of `100000.01` is a silent boundary
    flip."""
    raw = json.dumps({"result": [{"expressions": [{"value": {
        "cases": {"c": {"input": {"vendor": {"sanctionsStatus": "CLEAR",
                                             "requestedSpend": 100000.01}}}}}
    }]}]}).encode("utf-8")
    points = domain.resolved_input_points(raw)
    assert len(points) == 1
    assert str(points[0][1]["spend"]) == "100000.01"
    assert domain.domain_problems(points[0][1], "number") == []


# --- how the scorer maps the two answers (round-1 R1-3) --------------------

def test_an_out_of_domain_case_is_an_identity_failure_named_by_category():
    """Identical in all three arms, applied BEFORE identity and BEFORE any
    mutation execution: the run stays in the E4 denominator as not-high-kill,
    the failure is reported per arm as a first-class rate, and E3 counts it."""
    named = [("case[0]", domain.signature_from_documents({"riskScore": 10}, {}))]
    failures = e4.domain_failures(named, "number")
    assert len(failures) == 1
    assert failures[0]["got"] == e4.OUT_OF_DOMAIN
    assert failures[0]["case"] == "case[0]"
    assert failures[0]["problems"]


def test_an_in_domain_case_produces_no_identity_failure():
    named = [("case[0]", rego_signature(riskScore=10))]
    assert e4.domain_failures(named, "number") == []


def test_the_matrix_signature_records_unregistered_facts_members():
    signature = e4.matrix_domain_signature(
        {"vendor": {"sanctionsStatus": "CLEAR"}, "context": {"note": "x"}}, {})
    assert "facts.context" in signature["unknownMembers"]
    assert any("facts.context" in problem
               for problem in domain.domain_problems(signature, "string"))
