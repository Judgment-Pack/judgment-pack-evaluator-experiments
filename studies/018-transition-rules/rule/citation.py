"""Deterministic writers for the citation and the rule configuration.

Build path only. The evaluator (`rule/transition.py`) never imports this
module and recomputes everything from retained bytes.

A **citation** is the construction a reader proposed publicly on the Study 016
announcement thread: the deciding artifact records the registry head it
validated against. It is unsigned here on purpose — this study measures what a
transition rule can compute from it, and the registered backdating cell shows
that signing it would change nothing, because the party that would sign is the
party that chooses what to cite.
"""

import json


def citation_bytes(*, series_id, cited_head):
    return json.dumps(
        {"citationVersion": "1", "seriesId": series_id, "citedHead": cited_head},
        indent=2, ensure_ascii=False,
    ).encode("utf-8")


def ruleconfig_bytes(*, series_id, rule, window_positions=None, window_duration=None):
    return json.dumps(
        {
            "ruleConfigVersion": "1",
            "seriesId": series_id,
            "rule": rule,
            "windowPositions": window_positions,
            "windowDuration": window_duration,
        },
        indent=2, ensure_ascii=False,
    ).encode("utf-8")
