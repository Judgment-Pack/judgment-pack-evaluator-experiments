"""Replay every ledger against every planted defect, and read the profile.

For each (defect instance, ledger) the perturbed pack and the ledger are
declared in a project of their own and `packs test` runs; the cell records
whether the replay caught the defect (one or more mismatched rows), how many
rows disagreed, and the profile's threshold report -- from which the
registered line-moved signature is computed:

  line-moved signature := exactly one threshold pointer carries disagreeing
  rows at all; at at least one of that pointer's literals every disagreeing
  row lies strictly on ONE side (below xor above), none at it; and every
  mismatched row of the replay is placed on that pointer -- the profile's
  buckets account for all of them. Read across origins.

A replay with no threshold pointer disagreeing but rows mismatched is
"caught, off-threshold". A pack with no threshold has no signature to carry.

Run: python harness/replay.py POLICY --ledgers DIR --defects DIR --out FILE
"""
import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path

import jp


def digest_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


ORDERED = {"greater-than", "greater-than-or-equal", "less-than", "less-than-or-equal"}


def threshold_boundaries(pack):
    """The boundaries the profile must report for this pack: its distinct
    (pointer, literal) ordered comparisons, over the applicability, the rules
    and the exceptions (runtime ADR-0034 groups coincident sites)."""
    found = set()

    def walk(node):
        if not isinstance(node, dict):
            return
        if node.get("op") == "fact" and node.get("operator") in ORDERED:
            found.add((node["path"], node["value"]))
        for child in node.get("conditions", []) or []:
            walk(child)
        if "condition" in node:
            walk(node["condition"])
    walk(pack.get("applicability"))
    for r in pack.get("rules", []):
        walk(r.get("when"))
    for e in pack.get("exceptions", []):
        walk(e.get("when"))
    return found


def expected_thresholds(pack):
    return len(threshold_boundaries(pack))


def get_pointer(facts, pointer):
    node = facts
    for p in [p for p in pointer.split("/") if p]:
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node


DECIMAL = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?")


def is_count(v, hi=None):
    """A count is an int (never a bool) at or above zero, and at most hi when given."""
    return type(v) is int and v >= 0 and (hi is None or v <= hi)


def expected_entries(cases, boundaries, mismatched_ids):
    """What the profile must report, recomputed from the ledger and the rows
    that mismatched: for every boundary (pointer, literal) and every origin of
    the ledger, the rows whose value at the pointer is a decimal string of
    Core section 2.2's grammar placed below, at or above the literal by
    mathematical value, and among them the rows that mismatched. An origin
    with no comparable row still reports its zero buckets (runtime
    ADR-0034); a row whose value is absent or not such a decimal sits in no
    bucket."""
    from decimal import Decimal
    origins = sorted({c.get("origin") for c in cases}, key=str)
    mismatched = set(mismatched_ids)
    out = {}
    for pointer, literal in boundaries:
        lit = Decimal(literal)
        per_origin = {o: {side: {"rows": 0, "disagreeing": 0} for side in ("below", "at", "above")} for o in origins}
        for c in cases:
            v = get_pointer(c.get("facts", {}), pointer)
            if not isinstance(v, str) or not DECIMAL.fullmatch(v):
                continue
            d = Decimal(v)
            side = "below" if d < lit else ("at" if d == lit else "above")
            bucket = per_origin[c.get("origin")][side]
            bucket["rows"] += 1
            if c.get("id") in mismatched:
                bucket["disagreeing"] += 1
        out[(pointer, literal)] = per_origin
    return out


def reconcile(entries, cases, mismatched_ids, boundaries=None):
    """Every retained entry must be exactly what the ledger and the mismatched
    rows imply (expected_entries), origin by origin and bucket by bucket --
    so the boundaries describe the same rows jointly, not each on its own.
    Returns the first inconsistency, or None."""
    bounds = boundaries if boundaries is not None else {(t.get("pointer"), t.get("literal")) for t in entries}
    expected = expected_entries(cases, bounds, mismatched_ids)
    seen = set()
    for t in entries:
        key = (t.get("pointer"), t.get("literal"))
        if key not in expected:
            return "entry %s at %s is not a boundary of the pack" % key
        seen.add(key)
        want = expected[key]
        reported = {o.get("origin") for o in t.get("origins", [])}
        if reported != set(want):
            return "entry %s at %s reports origins %s where the ledger holds %s" % (key + (sorted(map(str, reported)), sorted(map(str, want))))
        for o in t["origins"]:
            for side in ("below", "at", "above"):
                b = o.get(side, {})
                if not is_count(b.get("rows")) or not is_count(b.get("disagreeing"), b.get("rows")):
                    return "entry %s at %s, origin %s: %s is not a count" % (key + (o["origin"], side))
                if (b["rows"], b["disagreeing"]) != (want[o["origin"]][side]["rows"], want[o["origin"]][side]["disagreeing"]):
                    return "entry %s at %s, origin %s, %s: reports %d rows / %d disagreeing where the ledger and the mismatched rows give %d / %d" % (
                        key + (o["origin"], side, b["rows"], b["disagreeing"], want[o["origin"]][side]["rows"], want[o["origin"]][side]["disagreeing"]))
    if seen != set(expected):
        return "the entries do not cover every boundary of the pack"
    return None


def buckets_per_pointer(entries):
    """Sum each entry's origins into (pointer -> [literal, below, at, above]) -- the scorer recomputes this from retained evidence."""
    per_pointer = {}
    for t in entries:
        below = sum(o["below"]["disagreeing"] for o in t["origins"])
        at = sum(o["at"]["disagreeing"] for o in t["origins"])
        above = sum(o["above"]["disagreeing"] for o in t["origins"])
        if below + at + above:
            per_pointer.setdefault(t["pointer"], []).append({"literal": t["literal"], "below": below, "at": at, "above": above})
    return per_pointer


def signature_from_buckets(per_pointer, mismatched):
    """The rule over retained bucket counts: what the scorer recomputes from a record."""
    one = len(per_pointer) == 1
    entries = next(iter(per_pointer.values())) if one else []
    sided = one and any(e["at"] == 0 and ((e["below"] > 0) != (e["above"] > 0)) for e in entries)
    placed = one and mismatched is not None and all(e["below"] + e["at"] + e["above"] == mismatched for e in entries)
    return bool(one and sided and placed), bool(placed)


def signature(profile, mismatched=None, expected=None, origins=None, cases=None, mismatched_ids=None, boundaries=None):
    """The registered line-moved signature, read per POINTER across origins.

    A pack may compare one pointer against several literals (a rule's guard
    and an exception's mirror), and the profile lists one entry per literal;
    the rows that disagree are the same rows counted against each. So: the
    signature holds iff exactly one pointer carries disagreeing rows, and at
    at least one of that pointer's literals every disagreeing row lies
    strictly on one side of it (below xor above) and none at it.
    """
    if not isinstance(profile, dict):
        raise RuntimeError("the replay report carries no profile: the runtime did not report the history profile")
    # the runtime omits `thresholds` when the pack draws no line; the number
    # reported must be the number the pack draws, or the evidence is not the
    # pack's
    entries = profile.get("thresholds") or []
    if not isinstance(entries, list):
        raise RuntimeError("the profile's thresholds member is not a list")
    if expected is not None and len(entries) != expected:
        raise RuntimeError("the profile reports %d threshold entries where the pack draws %d" % (len(entries), expected))
    if not entries:
        return {"applicable": False, "thresholdEntries": 0}
    for t in entries:
        reported = {o.get("origin") for o in t.get("origins", [])}
        if not reported or (origins is not None and reported != set(origins)):
            raise RuntimeError("the profile's entry for %s at %s reports origins %s where the ledger holds %s" % (t.get("pointer"), t.get("literal"), sorted(reported), sorted(origins or [])))
    if cases is not None and mismatched_ids is not None:
        problem = reconcile(entries, cases, mismatched_ids, boundaries)
        if problem:
            raise RuntimeError("the profile does not agree with the ledger and the mismatched rows: " + problem)
    per_pointer = buckets_per_pointer(entries)
    # every mismatched row must be PLACED on that pointer: a row whose value
    # the profile could not compare sits in no bucket, and a signature over
    # the placed rows alone would say nothing about it
    line_moved, placed = signature_from_buckets(per_pointer, mismatched)
    # the profile's threshold entries are retained whole -- every boundary,
    # every origin, zero counts included -- so the scorer can rebuild the
    # judgment from evidence rather than trust the flags
    return {"applicable": True, "thresholdEntries": len(entries), "thresholds": entries, "lineMoved": line_moved, "placed": placed, "disagreeing": per_pointer}


def replay(policy, pack, ledger):
    with tempfile.TemporaryDirectory() as tmp:
        root = jp.project(tmp, policy, pack, matrix=ledger)
        report = jp.test(root)
    entry = report["packs"][0]
    summary = entry.get("summary") or {}
    if not isinstance(summary.get("total"), int) or not isinstance(summary.get("mismatched"), int) or entry.get("status") not in ("passed", "mismatch"):
        raise RuntimeError("replay of %s did not run to a verdict: status %r, summary %r" % (policy, entry.get("status"), summary))
    if summary["total"] != len(ledger["cases"]):
        raise RuntimeError("replay of %s read %d rows of a ledger of %d" % (policy, summary["total"], len(ledger["cases"])))
    if (entry["status"] == "mismatch") != (summary["mismatched"] > 0):
        raise RuntimeError("replay of %s reports status %s with %d mismatched" % (policy, entry["status"], summary["mismatched"]))
    # the rows that mismatched, named: the evidence every threshold entry is recomputed from
    rows = entry.get("rows")
    if not isinstance(rows, list) or len(rows) != summary["total"] or {r.get("id") for r in rows} != {c.get("id") for c in ledger["cases"]}:
        raise RuntimeError("replay of %s reports rows that are not the ledger's" % policy)
    mismatched_ids = sorted(r["id"] for r in rows if r.get("status") == "mismatch")
    if len(mismatched_ids) != summary["mismatched"] or any(r.get("status") not in ("passed", "mismatch") for r in rows):
        raise RuntimeError("replay of %s names %d mismatched rows where the summary counts %d" % (policy, len(mismatched_ids), summary["mismatched"]))
    origins = {c.get("origin") for c in ledger["cases"]}
    bounds = threshold_boundaries(pack)
    return {"status": entry["status"], "rows": summary["total"], "mismatched": summary["mismatched"], "mismatchedRows": mismatched_ids,
            "caught": summary["mismatched"] > 0,
            "signature": signature(entry.get("profile"), summary["mismatched"], len(bounds), origins, ledger["cases"], mismatched_ids, bounds)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policy")
    ap.add_argument("--ledgers", required=True)
    ap.add_argument("--defects", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--policy-pack", help="the UNPLANTED pack: replay it against every ledger and write <out>.gate.json (control gate G1)")
    ap.add_argument("--attempt-id", default=None, help="the attempt these records belong to, stamped into both files")
    args = ap.parse_args()
    ledgers = sorted(Path(args.ledgers).glob("*.matrix.json"))
    if args.policy_pack:
        original = json.loads(Path(args.policy_pack).read_text())
        gate = []
        for l in ledgers:
            r = replay(args.policy, original, json.loads(l.read_text()))
            gate.append({"ledger": l.stem.replace(".matrix", ""), "ledgerSha256": digest_of(l), "rows": r["rows"], "mismatched": r["mismatched"], "status": r["status"]})
        with open(args.out.replace(".json", ".gate.json"), "x") as f:
            f.write(json.dumps({"attemptId": args.attempt_id, "policyPackSha256": digest_of(args.policy_pack), "ledgers": gate}, indent=1))
        print("gate: %d ledgers, %d with a mismatch" % (len(gate), sum(1 for g in gate if g["mismatched"])))
    index = json.loads((Path(args.defects) / "INDEX.json").read_text())
    cells = []
    for d in index["instances"]:
        if not d["valid"]:
            continue
        defect_path = Path(args.defects) / (d["id"] + ".pack.json")
        pack = json.loads(defect_path.read_text())
        for l in ledgers:
            ledger = json.loads(l.read_text())
            r = replay(args.policy, pack, ledger)
            r.update({"defect": d["id"], "class": d["class"], "site": d["site"], "ledger": l.stem.replace(".matrix", ""),
                      "ledgerSha256": digest_of(l), "defectSha256": digest_of(defect_path)})
            cells.append(r)
    with open(args.out, "x") as f:
        f.write(json.dumps({"attemptId": args.attempt_id, "cells": cells}, indent=1))
    from collections import defaultdict
    by = defaultdict(list)
    for c in cells:
        by[(c["class"], c["ledger"].split("-")[0])].append(c)
    for (cls, stratum), cs in sorted(by.items()):
        caught = sum(c["caught"] for c in cs)
        moved = sum(1 for c in cs if c["caught"] and c["signature"].get("lineMoved"))
        print("%s %-8s cells=%3d caught=%3d line-moved-signature=%3d" % (cls, stratum, len(cs), caught, moved))


if __name__ == "__main__":
    main()
