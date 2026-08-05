#!/usr/bin/env python3
"""The study's fabrication gate (PREREGISTRATION.md §6, inherited from Study
009's repaired form): complete-row admission from the verified artifact, with
the rule loaded from the freeze and no rule or params argument exposed.

For each row the gate: verifies the store (via fabrication-gate admit(),
which runs attest.verify first), recomputes the claim from the retained
artifact bytes with derive.derive_canonical under the freeze-verified rule
and literal {} params, applies the registered outcome wrapper itself to the
artifact's decision.outcome, and requires the emitted matrix row to equal —
member for member, with no extras — what that reconstruction says it must
be. A transcriber that emitted anything else fails here, control rows
included. Acquisition status and lineage go to a sidecar, never the matrix:
jpack's MatrixCase is strict and an extra member would make it unloadable.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
LINE = os.path.dirname(os.path.dirname(STUDY))
sys.path.insert(0, os.path.join(LINE, "fabrication-gate"))
sys.path.insert(0, os.path.join(LINE, "derivation-rule"))
sys.path.insert(0, os.path.join(LINE, "acquisition-proxy"))

import attest  # noqa: E402,F401 - imported for side effects fabrication relies on
import derive  # noqa: E402
import pnf_check  # noqa: E402

import importlib.util as _importlib_util

def _load_fabrication():
    spec = _importlib_util.spec_from_file_location(
        "fabrication_gate", os.path.join(LINE, "fabrication-gate", "gate.py"))
    module = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fabrication = _load_fabrication()

RULE_PATH = os.path.join(STUDY, "transcription", "record.rule.json")


class GateError(Exception):
    pass


def frozen_rule(expected_digest: str | None = None) -> dict:
    """The rule, loaded from the tree, PNF-checked, and digest-asserted."""
    data = open(RULE_PATH, "rb").read()
    if expected_digest is not None:
        actual = "sha256:" + hashlib.sha256(data).hexdigest()
        if actual != expected_digest:
            raise GateError("the rule on disk is not the frozen rule: %s" % actual)
    rule = json.loads(data)
    pnf_check.check(rule)
    return rule


def wrapper(outcome_id: str) -> dict:
    """The registered outcome shape — applied by the gate, never trusted."""
    return {"kind": "outcome", "outcomeId": outcome_id, "reasons": [], "handoff": {"state": "none"}}


def reconstruct_row(store_root: str, key: bytes, session: str, call_index: int,
                    rule: dict, authority: str) -> tuple[dict, dict]:
    """(the one admissible row, its lineage) for a verified artifact."""
    admitted = fabrication.admit(store_root, key, session, call_index, rule, {},
                                 expected_authority=authority)
    artifact_path = os.path.join(
        store_root, "artifacts", admitted["lineage"]["resultDigest"].split(":", 1)[1])
    artifact_bytes = open(artifact_path, "rb").read()
    artifact = json.loads(artifact_bytes)
    recomputed = json.loads(derive.derive_canonical(rule, artifact, {}))
    for member in ("facts", "evidenceAvailability", "acquisitionStatus"):
        if recomputed[member] != admitted[member]:
            raise GateError("admit() and the recomputation disagree on %s" % member)
    case_id = artifact.get("caseId")
    outcome = (artifact.get("decision") or {}).get("outcome")
    if not isinstance(case_id, str) or not isinstance(outcome, str):
        raise GateError("the artifact carries no caseId/decision.outcome to bind")
    row = {
        "id": case_id,
        "origin": "transcribed:%s@%s" % (case_id, admitted["lineage"]["resultDigest"]),
        "facts": recomputed["facts"],
        "evidenceAvailability": {},
        "expectedDisposition": wrapper(outcome),
    }
    lineage = dict(admitted["lineage"])
    lineage["caseId"] = case_id
    lineage["acquisitionStatus"] = recomputed["acquisitionStatus"]
    lineage["ruleDigest"] = "sha256:" + hashlib.sha256(open(RULE_PATH, "rb").read()).hexdigest()
    lineage["claimDigest"] = "sha256:" + hashlib.sha256(
        derive.derive_canonical(rule, artifact, {})).hexdigest()
    return row, lineage


def admit_matrix(matrix: dict, refs: list[dict], store_root: str, key: bytes,
                 authority: str, rule_digest: str) -> list[dict]:
    """Hold every emitted row to its reconstruction; return the lineages."""
    rule = frozen_rule(rule_digest)
    cases = matrix.get("cases")
    if matrix.get("matrixVersion") != "1" or not isinstance(cases, list):
        raise GateError("the emitted matrix is not the documented shape")
    if len(cases) != len(refs):
        raise GateError("row count %d != reference count %d" % (len(cases), len(refs)))
    lineages = []
    by_case = {ref["caseId"]: ref for ref in refs}
    for row in cases:
        # References are consumed: a duplicated row id, like an omitted one,
        # leaves the accounting wrong and is refused.
        ref = by_case.pop(row.get("id"), None)
        if ref is None:
            raise GateError("row %r has no unconsumed verified reference" % row.get("id"))
        expected, lineage = reconstruct_row(
            store_root, key, ref["sessionId"], ref["callIndex"], rule, authority)
        # Canonical BYTES, not Python equality: False == 0 in Python, and the
        # evaluator would see the difference this comparison must not miss.
        if attest.canon(row) != attest.canon(expected):
            raise GateError(
                "row %r differs from its reconstruction:\nemitted  %s\nadmitted %s"
                % (row.get("id"), json.dumps(row, sort_keys=True), json.dumps(expected, sort_keys=True)))
        lineages.append(lineage)
    if by_case:
        raise GateError("rows missing for verified references: %s" % sorted(by_case))
    return lineages
