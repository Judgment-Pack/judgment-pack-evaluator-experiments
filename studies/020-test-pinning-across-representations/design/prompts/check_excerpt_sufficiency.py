#!/usr/bin/env python3
"""Study 019 excerpt-sufficiency check -- DESIGN DRAFT, NOT REGISTERED.

BRIEF.md section 3 makes excerpt parity a SUFFICIENCY criterion, not a size criterion:

    every language construct used by that arm's frozen reference implementation must
    appear in that arm's excerpt, and the reference may use no construct absent from
    the excerpt.

This script derives each reference's construct inventory MECHANICALLY from the reference
artifact itself (never from a hand-kept list -- a hand-kept list is a claim about the
reference, not a measurement of it) and asserts every construct is present in that arm's
excerpt. Exit nonzero on any miss; print the inventory either way.

  arm A     inventory = every JPS member name the pack declares, every condition `op`,
            every ordered/equality `operator`, every `onUnknown` value, every exception
            `effect`, every evidence-requirement `kind`, every escalation target `kind`.
  arms B/C  inventory = every Rego keyword the reference uses, plus every built-in it
            calls (detected by matching `name(` against the pinned capabilities list --
            so a built-in the reference uses cannot escape the check by being unlisted).
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, ".."))
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"
CAPS = os.environ.get("OPA_CAPS", os.path.join(SCRATCH, "pins", "opa", "caps-filtered.json"))

PACK = os.path.join(DESIGN, "reference", "refA", "pack.json")
REGO = os.path.join(DESIGN, "reference", "refB", "policy.rego")
JPS_EXCERPT = os.path.join(HERE, "generated", "JPS-EXCERPT.md")
REGO_EXCERPT = os.path.join(HERE, "generated", "REGO-EXCERPT.md")

REGO_KEYWORDS = ["package", "import", "default", "if", "else", "in", "some", "every",
                 "not", "contains", "with", "as", "null", "true", "false"]


def arm_a_inventory(pack):
    inv = set()

    def members(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                inv.add("member:%s" % k)
                members(v, path + "/" + k)
        elif isinstance(obj, list):
            for v in obj:
                members(v, path)

    members(pack)
    for r in pack.get("rules", []) + pack.get("exceptions", []):
        if "onUnknown" in r:
            inv.add("onUnknown:%s" % r["onUnknown"])
        if "effect" in r:
            inv.add("effect:%s" % r["effect"])

    def conds(c):
        if not isinstance(c, dict):
            return
        if "op" in c:
            inv.add("op:%s" % c["op"])
        if "operator" in c:
            inv.add("operator:%s" % c["operator"])
        for k in ("conditions", "condition"):
            v = c.get(k)
            if isinstance(v, list):
                for x in v:
                    conds(x)
            elif isinstance(v, dict):
                conds(v)

    for r in pack.get("rules", []) + pack.get("exceptions", []):
        conds(r.get("when"))
    for er in pack.get("evidenceRequirements", []):
        if "kind" in er:
            inv.add("evidenceKind:%s" % er["kind"])
    tgt = (pack.get("escalation") or {}).get("target") or {}
    if "kind" in tgt:
        inv.add("escalationTargetKind:%s" % tgt["kind"])
    for t in (pack.get("escalation") or {}).get("triggers", []):
        inv.add("trigger:%s" % t)
    return inv


SYNTAX_PATTERNS = {
    "syntax::=": r":=",
    "syntax:comprehension": r"[\[{][^\n]*\|",
    "syntax:function-rule": r"(?m)^\s*\w+\([A-Za-z_][^)\n]*\)\s*(:=|=|if\b|\{)",
}


def present(construct, excerpt):
    """True iff the excerpt documents this construct. Syntax constructs are matched by
    their shape; every other construct by its own identifier, on word boundaries."""
    if construct in SYNTAX_PATTERNS:
        return re.search(SYNTAX_PATTERNS[construct], excerpt) is not None
    token = construct.split(":", 1)[1]
    return re.search(r"(?<![A-Za-z0-9_-])%s(?![A-Za-z0-9_-])" % re.escape(token),
                     excerpt) is not None


def strip_rego_comments(text):
    """Remove `#` comments outside string literals: a construct named only in a comment is
    not a construct the reference uses."""
    out = []
    for line in text.split("\n"):
        in_str, esc, cut = False, False, None
        for i, ch in enumerate(line):
            if esc:
                esc = False
                continue
            if ch == "\\" and in_str:
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if ch == "#" and not in_str:
                cut = i
                break
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def arm_rego_inventory(text, builtin_names):
    text = strip_rego_comments(text)
    inv = set()
    words = set(re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", text))
    for kw in REGO_KEYWORDS:
        if re.search(r"(?<![A-Za-z0-9_.])%s(?![A-Za-z0-9_])" % re.escape(kw), text):
            inv.add("keyword:%s" % kw)
    for name in builtin_names:
        if re.search(r"(?<![A-Za-z0-9_.])%s\s*\(" % re.escape(name), text):
            inv.add("builtin:%s" % name)
    # rule shapes that are constructs in their own right
    if re.search(r"^\s*\w+\s*:=", text, re.M):
        inv.add("syntax::=")
    if re.search(r"[\[{][^\n]*\|", text):        # array / set / object comprehension
        inv.add("syntax:comprehension")
    if re.search(r"^\s*\w+\([^)]*\)\s*:?=", text, re.M):
        inv.add("syntax:function-rule")
    if "rego.v1" in text or "import rego.v1" in text:
        inv.add("import:rego.v1")
    _ = words
    return inv


def check(name, inventory, excerpt_path):
    with open(excerpt_path, encoding="utf-8") as fh:
        excerpt = fh.read()
    missing = sorted(c for c in inventory if not present(c, excerpt))
    print("%s: %d constructs derived from the reference, %d missing from the excerpt"
          % (name, len(inventory), len(missing)))
    for c in sorted(inventory):
        print("    %-40s %s" % (c, "MISSING" if c in missing else "ok"))
    return missing


def main():
    with open(PACK) as fh:
        pack = json.load(fh)
    with open(REGO, encoding="utf-8") as fh:
        rego = fh.read()
    with open(CAPS) as fh:
        builtin_names = [b["name"] for b in json.load(fh).get("builtins", [])]

    miss_a = check("arm A (JPS)", arm_a_inventory(pack), JPS_EXCERPT)
    print()
    miss_bc = check("arms B/C (Rego)", arm_rego_inventory(rego, builtin_names), REGO_EXCERPT)

    total = len(miss_a) + len(miss_bc)
    print("\nSUFFICIENCY: %s (%d missing)" % ("PASS" if total == 0 else "FAIL", total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
