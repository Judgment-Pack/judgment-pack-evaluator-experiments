"""Walk every input row in RFC 0006's non-normative appendix table."""

from __future__ import annotations

import pytest

from jps_evaluator import evaluate
from tests.pack_fixtures import appendix_pack


PRESENT = {"intake-form": "present", "sponsor-endorsement": "present"}


def facts(
    *,
    request_type: str | None = "data-access",
    completeness: str | None = None,
    appropriateness: str | None = None,
    embargo: bool | None = None,
) -> dict:
    request = {}
    if request_type is not None:
        request["type"] = request_type
    if completeness is not None:
        request["completeness"] = completeness
    if appropriateness is not None:
        request["appropriateness"] = appropriateness
    if embargo is not None:
        request["embargoedInformationToUnauthorizedRecipients"] = embargo
    return {"request": request}


def expected(kind, *, outcome_id=None, reasons=(), handoff="none"):
    result = {
        "kind": kind,
        "reasons": list(reasons),
        "handoff": handoff,
        "experimental": True,
        "conformanceClaim": "none",
    }
    if outcome_id is not None:
        result["outcomeId"] = outcome_id
    return result


CASES = [
    (
        "1",
        facts(request_type="dataset-deletion"),
        PRESENT,
        expected(
            "not-applicable", reasons=("not-applicable",), handoff="requested"
        ),
    ),
    (
        "2",
        facts(request_type=None),
        PRESENT,
        expected("unresolved", reasons=("unknown",), handoff="requested"),
    ),
    (
        "3",
        facts(completeness="complete", appropriateness="hard-fail", embargo=False),
        PRESENT,
        expected("outcome", outcome_id="decline-redirect"),
    ),
    (
        "4",
        facts(completeness="incomplete", appropriateness="pass", embargo=False),
        PRESENT,
        expected("outcome", outcome_id="clarify-return"),
    ),
    (
        "5",
        facts(completeness="complete", appropriateness="pending", embargo=False),
        PRESENT,
        expected("outcome", outcome_id="clarify-return"),
    ),
    (
        "6",
        facts(completeness="complete", appropriateness="pass", embargo=False),
        PRESENT,
        expected("outcome", outcome_id="proceed"),
    ),
    (
        "7a",
        facts(completeness="complete", appropriateness="pass", embargo=False),
        {"intake-form": "present", "sponsor-endorsement": "unknown"},
        expected("unresolved", reasons=("unknown",), handoff="requested"),
    ),
    (
        "7b",
        facts(completeness="complete", appropriateness="pass", embargo=False),
        {"intake-form": "present", "sponsor-endorsement": "absent"},
        expected(
            "unresolved",
            reasons=("missing-required-evidence",),
            handoff="requested",
        ),
    ),
    (
        "8",
        facts(completeness="complete", appropriateness="pass", embargo=True),
        PRESENT,
        expected("outcome", outcome_id="decline-redirect"),
    ),
    (
        "9",
        facts(completeness="incomplete", appropriateness="hard-fail", embargo=False),
        PRESENT,
        expected("unresolved", reasons=("conflict",), handoff="requested"),
    ),
]


@pytest.mark.parametrize("_name,input_facts,evidence,disposition", CASES, ids=[c[0] for c in CASES])
def test_appendix_row(_name, input_facts, evidence, disposition):
    assert evaluate(appendix_pack(), input_facts, evidence) == disposition
