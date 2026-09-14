"""Plant one mechanical defect in a pack, every way the pack admits it.

Nine classes, each applied at every site the pack offers; a class the pack
has no site for yields no instance. Every instance is validated by the
runtime (`jpack spec validate`) and dropped, with a note, if the perturbed
document is not a valid pack. The classes:

  D1 threshold-up        an ordered literal moved up by a quarter (at least one unit)
  D2 threshold-down      an ordered literal moved down by a quarter (at least one unit)
  D3 boundary-flip       greater-than-or-equal <-> greater-than (and the less-than pair)
  D4 comparison-reversed greater-than* <-> less-than*, or-equal kept
  D5 outcome-swapped     a rule's outcome replaced by another of the pack's outcomes
  D6 condition-dropped   one condition removed from an `all` of two or more
  D7 enum-member-replaced one member of an `in` list, or an `equals` literal, replaced by a value outside the domain
  D8 exception-effect-changed  escalate -> force-outcome (first other outcome), force-outcome -> escalate
  D9 fallback-changed    fallbackOutcome replaced by another of the pack's outcomes

Run: python harness/plant.py POLICY --out DIR
"""
import argparse
import copy
import json
import subprocess
import tempfile
from decimal import Decimal
from pathlib import Path

import jp

STUDY = Path(__file__).resolve().parent.parent
POLICIES = STUDY / "fixtures" / "policies"
ORDERED_UP = {"greater-than": "greater-than-or-equal", "greater-than-or-equal": "greater-than",
              "less-than": "less-than-or-equal", "less-than-or-equal": "less-than"}
REVERSED = {"greater-than": "less-than", "less-than": "greater-than",
            "greater-than-or-equal": "less-than-or-equal", "less-than-or-equal": "greater-than-or-equal"}


def walk(node, path, out):
    """Every condition node with a JSON-pointer-like path into the pack."""
    if not isinstance(node, dict):
        return
    out.append((path, node))
    for i, child in enumerate(node.get("conditions", []) or []):
        walk(child, path + ["conditions", i], out)
    if "condition" in node:
        walk(node["condition"], path + ["condition"], out)


def sites(pack):
    found = []
    walk(pack.get("applicability"), ["applicability"], found)
    for i, r in enumerate(pack.get("rules", [])):
        walk(r.get("when"), ["rules", i, "when"], found)
    for i, e in enumerate(pack.get("exceptions", [])):
        walk(e.get("when"), ["exceptions", i, "when"], found)
    return found


def at(doc, path):
    node = doc
    for p in path:
        node = node[p]
    return node


def moved(literal, factor):
    d = Decimal(literal)
    places = -d.as_tuple().exponent if d.as_tuple().exponent < 0 else 0
    unit = Decimal(1).scaleb(-places)
    delta = (d * Decimal(factor)).quantize(unit)
    if abs(delta) < unit:
        delta = unit if Decimal(factor) > 0 else -unit
    return str((d + delta).quantize(unit))


def instances(pack):
    outcomes = [o["id"] for o in pack.get("outcomes", [])]
    out = []

    def emit(cls, site, mutate):
        doc = copy.deepcopy(pack)
        mutate(doc)
        out.append({"class": cls, "site": site, "pack": doc})

    for path, node in sites(pack):
        label = "/".join(str(p) for p in path)
        if node.get("op") == "fact" and node.get("operator") in ORDERED_UP:
            lit = node["value"]
            emit("D1", label, lambda d, path=path, lit=lit: at(d, path).__setitem__("value", moved(lit, "0.25")))
            emit("D2", label, lambda d, path=path, lit=lit: at(d, path).__setitem__("value", moved(lit, "-0.25")))
            emit("D3", label, lambda d, path=path: at(d, path).__setitem__("operator", ORDERED_UP[at(d, path)["operator"]]))
            emit("D4", label, lambda d, path=path: at(d, path).__setitem__("operator", REVERSED[at(d, path)["operator"]]))
        if node.get("op") == "fact" and node.get("operator") == "in" and path[0] != "applicability":
            for i, member in enumerate(node["value"]):
                emit("D7", label + "[%d]" % i, lambda d, path=path, i=i: at(d, path)["value"].__setitem__(i, "outside-the-domain"))
        if node.get("op") == "fact" and node.get("operator") == "equals" and isinstance(node.get("value"), str) and path[0] != "applicability":
            emit("D7", label, lambda d, path=path: at(d, path).__setitem__("value", "outside-the-domain"))
        if node.get("op") == "all" and len(node.get("conditions", [])) >= 2:
            for i in range(len(node["conditions"])):
                emit("D6", label + "[%d]" % i, lambda d, path=path, i=i: at(d, path)["conditions"].pop(i))
    for i, r in enumerate(pack.get("rules", [])):
        current = r.get("outcome")
        for other in outcomes:
            if other != current:
                emit("D5", "rules/%d:%s->%s" % (i, current, other), lambda d, i=i, other=other: d["rules"][i].__setitem__("outcome", other))
                break
    for i, e in enumerate(pack.get("exceptions", [])):
        if e.get("effect") == "escalate":
            emit("D8", "exceptions/%d:escalate->force" % i, lambda d, i=i: (d["exceptions"][i].__setitem__("effect", "force-outcome"), d["exceptions"][i].__setitem__("outcome", outcomes[0])))
        elif e.get("effect") == "force-outcome":
            emit("D8", "exceptions/%d:force->escalate" % i, lambda d, i=i: (d["exceptions"][i].__setitem__("effect", "escalate"), d["exceptions"][i].pop("outcome", None)))
    if pack.get("fallbackOutcome"):
        for other in outcomes:
            if other != pack["fallbackOutcome"]:
                emit("D9", "fallbackOutcome:%s->%s" % (pack["fallbackOutcome"], other), lambda d, other=other: d.__setitem__("fallbackOutcome", other))
                break
    return out


def valid(pack):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "pack.json"; f.write_text(json.dumps(pack))
        proc = subprocess.run([jp.JPACK, "spec", "validate", str(f)], capture_output=True, text=True)
        return proc.returncode == 0, proc.stderr.strip()[:200] or proc.stdout.strip()[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policy")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    pack = json.loads((POLICIES / (args.policy + ".pack.json")).read_text())
    out = Path(args.out) / args.policy / "defects"
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for k, inst in enumerate(instances(pack)):
        ok, note = valid(inst["pack"])
        entry = {"id": "%s-%02d" % (inst["class"], k), "class": inst["class"], "site": inst["site"], "valid": ok}
        if ok:
            (out / (entry["id"] + ".pack.json")).write_text(json.dumps(inst["pack"], indent=1))
        else:
            entry["note"] = note
        index.append(entry)
    (out / "INDEX.json").write_text(json.dumps(index, indent=1))
    from collections import Counter
    print("%s: %d instances (%d valid) %s" % (args.policy, len(index), sum(e["valid"] for e in index), dict(Counter(e["class"] for e in index if e["valid"]))))
    for e in index:
        if not e["valid"]:
            print("  dropped", e["id"], e["site"], e["note"][:100])


if __name__ == "__main__":
    main()
