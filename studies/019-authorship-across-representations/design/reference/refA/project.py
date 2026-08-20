#!/usr/bin/env python3
"""The registered arm-A projection from one grid cell to the engine's two input
documents. A null grid member is OMITTED from the document it would ride in:
that is the registered encoding of "unreadable" (risk, spend, country) and of
"unreported" (the yes/no statuses and the two evidence availabilities)."""

FACT_KEYS = [
    ("risk", "riskScore"),
    ("spend", "requestedSpend"),
    ("sanctions", "sanctionsStatus"),
    ("country", "countryRisk"),
    ("newVendor", "newVendor"),
    ("critical", "criticalSupplier"),
    ("prior", "priorEnforcement"),
]

EVIDENCE_KEYS = [
    ("finEvidence", "financial-evidence"),
    ("insurance", "insurance-certificate"),
]


def facts_document(cell):
    vendor = {}
    for cell_key, fact_key in FACT_KEYS:
        if cell.get(cell_key) is not None:
            vendor[fact_key] = cell[cell_key]
    return {"vendor": vendor}


def evidence_document(cell):
    document = {}
    for cell_key, requirement in EVIDENCE_KEYS:
        if cell.get(cell_key) is not None:
            document[requirement] = cell[cell_key]
    return document


def evidence_tristate(cell):
    """The same evidence document as the simulator's tri-state map: an omitted
    key is unknown (engine.go decodeEvidence)."""
    from jps_sim import T, F, U
    state = {"financial-evidence": U, "insurance-certificate": U}
    for cell_key, requirement in EVIDENCE_KEYS:
        value = cell.get(cell_key)
        if value == "present":
            state[requirement] = T
        elif value == "absent":
            state[requirement] = F
    return state
