#!/usr/bin/env python3
"""Render the judgment pack's semantic content as prose, for arm A-prime.

WHAT THIS DOES
--------------
Arm A-prime gives a model "the same disambiguation work as the pack, none of the
pack machinery".  For that arm to be a fair control it must carry *exactly* the
pack's semantic content -- no more, no less -- so the prose is generated
mechanically from ``nba-transaction-legality.json`` rather than written by hand.
A hand-written restatement would be a second act of authorship and would confound
the comparison it exists to protect.

Every rule becomes one numbered paragraph: its plain-language description, the
fully expanded condition, the outcome it produces, what happens when a fact is
unknown, and its rule identifier (so the arm can cite in the same vocabulary as
the others).  Exceptions, the fallback outcome, the escalation policy and the
evidence requirements are rendered the same way.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
* It adds no rule, removes none, and changes no effect.  It is a projection of
  the JSON, not an interpretation of it.
* It does not paraphrase the CBA.  Rule descriptions and rationales are copied
  verbatim from the pack.
* It does not mention JPS, packs, runtimes or evaluation machinery: arm A-prime
  is prose policy, and naming the machinery would leak the treatment.

CLI
---
    python render_prose.py [--pack PACK.json] [--out FILE.txt]

Deterministic: same pack in, same bytes out.  Python 3.10+, stdlib only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

OPERATOR_PHRASE = {
    "equals": "is",
    "not-equals": "is not",
    "in": "is one of",
    "not-in": "is not one of",
    "greater-than": "is greater than",
    "greater-than-or-equal": "is at least",
    "less-than": "is less than",
    "less-than-or-equal": "is at most",
    "exists": "is present",
    "not-exists": "is absent",
}


def humanise_path(pointer: str) -> str:
    """'/facts/derived/uses-bi-annual-exception' -> 'uses bi annual exception'."""
    tail = pointer.rsplit("/", 1)[-1]
    return tail.replace("-", " ").replace("_", " ")


def render_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ", ".join(render_value(v) for v in value)
    if value is None:
        return "null"
    return str(value)


def render_condition(node: Mapping[str, Any], depth: int = 0) -> str:
    op = node.get("op")
    if op == "fact":
        phrase = OPERATOR_PHRASE.get(node.get("operator", ""), node.get("operator", "?"))
        subject = humanise_path(node.get("path", ""))
        if node.get("operator") in ("exists", "not-exists"):
            return "%s %s" % (subject, phrase)
        return "%s %s %s" % (subject, phrase, render_value(node.get("value")))
    if op in ("all", "any"):
        joiner = " AND " if op == "all" else " OR "
        parts = [render_condition(c, depth + 1) for c in node.get("conditions", [])]
        text = joiner.join(parts)
        return "(%s)" % text if depth and len(parts) > 1 else text
    if op == "not":
        inner = node.get("condition") or (node.get("conditions") or [{}])[0]
        return "NOT (%s)" % render_condition(inner, depth + 1)
    return json.dumps(node, sort_keys=True)


def render(pack: Mapping[str, Any]) -> str:
    lines: List[str] = []
    add = lines.append

    add(pack.get("title", "Policy"))
    add("=" * len(pack.get("title", "Policy")))
    add("")
    decision = pack.get("decision") or {}
    if decision.get("question"):
        add("QUESTION: %s" % decision["question"])
    if decision.get("intent"):
        add("INTENT: %s" % decision["intent"])
    add("")

    add("POSSIBLE ANSWERS")
    for o in pack.get("outcomes") or []:
        add("* %s (%s): %s" % (o.get("label", o.get("id")), o.get("id"), o.get("description", "")))
    if pack.get("fallbackOutcome"):
        add("* If no numbered provision below is triggered, the answer is \"%s\"."
            % pack["fallbackOutcome"])
    add("")

    add("HOW TO HANDLE A FACT YOU DO NOT HAVE")
    esc = pack.get("escalation") or {}
    add(esc.get("message", "Escalate.").strip())
    add("If a provision below is marked ESCALATE-IF-UNKNOWN and you cannot "
        "determine one of the facts it depends on, do not guess: the answer is "
        "that the question cannot be decided on the facts supplied.")
    add("")

    exceptions = pack.get("exceptions") or []
    if exceptions:
        add("SCOPE EXCLUSIONS")
        for e in exceptions:
            add("* %s" % (e.get("description") or e.get("id")))
            add("  Applies when: %s." % render_condition(e.get("when") or {}))
            add("  Effect: %s." % e.get("effect", "escalate"))
        add("")

    add("PROVISIONS")
    add("Each provision below is a violation detector. If its condition holds, "
        "the answer is \"illegal\" and the provision's identifier should be cited.")
    add("")
    sources = {s.get("id"): s for s in (pack.get("sources") or [])}
    for i, rule in enumerate(pack.get("rules") or [], 1):
        add("%d. %s" % (i, rule.get("description", "").strip()))
        add("   Condition: %s." % render_condition(rule.get("when") or {}))
        add("   Then the answer is: %s." % rule.get("outcome", "illegal"))
        if rule.get("onUnknown") == "escalate":
            add("   ESCALATE-IF-UNKNOWN.")
        if rule.get("rationale"):
            add("   Basis: %s" % rule["rationale"].strip())
        refs = [sources.get(r, {}).get("title") or r for r in (rule.get("sourceRefs") or [])]
        if refs:
            add("   Source: %s" % "; ".join(refs))
        add("   Identifier to cite: %s" % rule.get("id"))
        add("")

    reqs = pack.get("evidenceRequirements") or []
    if reqs:
        add("SUPPORTING RECORDS THAT WOULD NORMALLY BE CONSULTED")
        for r in reqs:
            add("* %s: %s (%s)" % (r.get("id"), r.get("description", ""),
                                   "required" if r.get("required") else "advisory"))
        add("")

    add("SOURCES")
    for s in pack.get("sources") or []:
        bits = [s.get("title") or s.get("id")]
        if s.get("citation"):
            bits.append(s["citation"])
        if s.get("uri"):
            bits.append(s["uri"])
        add("* %s" % " - ".join(str(b) for b in bits))
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack", type=Path, default=here / "nba-transaction-legality.json")
    ap.add_argument("--out", type=Path,
                    default=here / "nba-transaction-legality.prose.txt")
    args = ap.parse_args(argv)
    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    text = render(pack)
    args.out.write_text(text, encoding="utf-8")
    print("rules rendered : %d" % len(pack.get("rules") or []))
    print("characters     : %d" % len(text))
    print("output         : %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
