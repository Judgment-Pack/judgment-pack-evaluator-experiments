"""Replay every ledger against every planted defect, and read the profile.

For each (defect instance, ledger) the perturbed pack and the ledger are
declared in a project of their own and `packs test` runs; the cell records
whether the replay caught the defect (one or more mismatched rows), how many
rows disagreed, and the profile's threshold report -- from which the
registered line-moved signature is computed:

  line-moved signature := exactly one threshold pointer carries disagreeing
  rows at all, and on that pointer every disagreeing row lies strictly on
  ONE side of the literal (below xor above), none at it. Read across origins.

A replay with no threshold pointer disagreeing but rows mismatched is
"caught, off-threshold". A pack with no threshold has no signature to carry.

Run: python harness/replay.py POLICY --ledgers DIR --defects DIR --out FILE
"""
import argparse
import json
import tempfile
from pathlib import Path

import jp


def signature(profile):
    """The registered line-moved signature, read per POINTER across origins.

    A pack may compare one pointer against several literals (a rule's guard
    and an exception's mirror), and the profile lists one entry per literal;
    the rows that disagree are the same rows counted against each. So: the
    signature holds iff exactly one pointer carries disagreeing rows, and at
    at least one of that pointer's literals every disagreeing row lies
    strictly on one side of it (below xor above) and none at it.
    """
    if not profile or not profile.get("thresholds"):
        return {"applicable": False}
    per_pointer = {}
    for t in profile["thresholds"]:
        below = sum(o["below"]["disagreeing"] for o in t["origins"])
        at = sum(o["at"]["disagreeing"] for o in t["origins"])
        above = sum(o["above"]["disagreeing"] for o in t["origins"])
        if below + at + above:
            per_pointer.setdefault(t["pointer"], []).append({"literal": t["literal"], "below": below, "at": at, "above": above})
    one = len(per_pointer) == 1
    sided = one and any(e["at"] == 0 and ((e["below"] > 0) != (e["above"] > 0)) for e in next(iter(per_pointer.values())))
    return {"applicable": True, "lineMoved": bool(one and sided), "disagreeing": per_pointer}


def replay(policy, pack, ledger):
    with tempfile.TemporaryDirectory() as tmp:
        root = jp.project(tmp, policy, pack, matrix=ledger)
        report = jp.test(root)
    entry = report["packs"][0]
    summary = entry.get("summary", {})
    return {"status": entry.get("status"), "rows": summary.get("total"), "mismatched": summary.get("mismatched", 0),
            "caught": (summary.get("mismatched", 0) or 0) > 0, "signature": signature(entry.get("profile"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policy")
    ap.add_argument("--ledgers", required=True)
    ap.add_argument("--defects", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ledgers = sorted(Path(args.ledgers).glob("*.matrix.json"))
    index = json.loads((Path(args.defects) / "INDEX.json").read_text())
    cells = []
    for d in index:
        if not d["valid"]:
            continue
        pack = json.loads((Path(args.defects) / (d["id"] + ".pack.json")).read_text())
        for l in ledgers:
            ledger = json.loads(l.read_text())
            r = replay(args.policy, pack, ledger)
            r.update({"defect": d["id"], "class": d["class"], "site": d["site"], "ledger": l.stem.replace(".matrix", "")})
            cells.append(r)
    Path(args.out).write_text(json.dumps(cells, indent=1))
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
