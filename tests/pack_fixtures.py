"""Packs reconstructed solely from the reference texts for evaluator tests."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def appendix_pack() -> dict[str, Any]:
    """Return the minimal reconstructed pack described in DECISIONS.md decision 17."""

    return {
        "specVersion": "0.1.0-draft",
        "id": "https://example.test/packs/data-request-intake-triage",
        "version": "1.0.0",
        "title": "Data request intake triage",
        "decision": {
            "intent": "Triage a data request.",
            "question": "How should this request proceed?",
        },
        "applicability": {
            "op": "fact",
            "path": "/request/type",
            "operator": "equals",
            "value": "data-access",
        },
        "evidenceRequirements": [
            {
                "id": "intake-form",
                "description": "Completed intake form.",
                "required": True,
            },
            {
                "id": "sponsor-endorsement",
                "description": "Sponsor endorsement.",
                "required": True,
            },
        ],
        "outcomes": [
            {"id": "decline-redirect", "label": "Decline and redirect"},
            {"id": "clarify-return", "label": "Return for clarification"},
            {"id": "proceed", "label": "Proceed"},
        ],
        "rules": [
            {
                "id": "decline-hard-fail",
                "description": "Decline an inappropriate request.",
                "when": {
                    "op": "fact",
                    "path": "/request/appropriateness",
                    "operator": "equals",
                    "value": "hard-fail",
                },
                "outcome": "decline-redirect",
                "onUnknown": "ignore",
            },
            {
                "id": "clarify-incomplete-or-pending",
                "description": "Return incomplete or pending requests.",
                "when": {
                    "op": "any",
                    "conditions": [
                        {
                            "op": "fact",
                            "path": "/request/completeness",
                            "operator": "equals",
                            "value": "incomplete",
                        },
                        {
                            "op": "fact",
                            "path": "/request/appropriateness",
                            "operator": "equals",
                            "value": "pending",
                        },
                    ],
                },
                "outcome": "clarify-return",
                "onUnknown": "ignore",
            },
            {
                "id": "proceed-complete-pass",
                "description": "Proceed with complete and appropriate requests.",
                "when": {
                    "op": "all",
                    "conditions": [
                        {
                            "op": "fact",
                            "path": "/request/completeness",
                            "operator": "equals",
                            "value": "complete",
                        },
                        {
                            "op": "fact",
                            "path": "/request/appropriateness",
                            "operator": "equals",
                            "value": "pass",
                        },
                    ],
                },
                "outcome": "proceed",
                "onUnknown": "ignore",
            },
        ],
        "exceptions": [
            {
                "id": "embargo-force-decline",
                "description": "Do not release embargoed information to unauthorized recipients.",
                "when": {
                    "op": "fact",
                    "path": "/request/embargoedInformationToUnauthorizedRecipients",
                    "operator": "equals",
                    "value": True,
                },
                "effect": "force-outcome",
                "outcome": "decline-redirect",
                "onUnknown": "ignore",
            }
        ],
        "fallbackOutcome": "clarify-return",
        "escalation": {
            "triggers": [
                "not-applicable",
                "missing-required-evidence",
                "unknown",
                "conflict",
                "no-match",
            ],
            "target": {"kind": "queue", "name": "Data governance review"},
        },
    }


def base_pack() -> dict[str, Any]:
    return {
        "specVersion": "0.1.0-draft",
        "id": "https://example.test/packs/base",
        "version": "1.0.0",
        "title": "Base",
        "decision": {"intent": "Test.", "question": "Which outcome?"},
        "outcomes": [
            {"id": "outcome-a", "label": "A"},
            {"id": "outcome-b", "label": "B"},
            {"id": "outcome-c", "label": "C"},
        ],
        "rules": [
            {
                "id": "rule-a",
                "description": "Default test rule.",
                "when": {"op": "literal", "value": False},
                "outcome": "outcome-a",
                "onUnknown": "ignore",
            }
        ],
    }


def cloned(pack: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(pack)
