"""Build the two ledger strata for one policy: history decided under the pack.

A ledger is a matrix (matrixVersion "3") whose rows are cases decided under
the ORIGINAL pack -- the expectation of every row is what that pack decided,
never what any draft produces. Two strata:

- `literal` -- the literal-adjacent stratum: the runtime's own `packs suggest`
  candidates (every literal, one unit either side, midpoints, one unit outside
  the outermost, one pointer moved at a time from the base row; evidence
  candidates) decided under the pack. One ledger per policy, deterministic.
- `random-<n>-<seed>` -- the random stratum: n cases drawn by a seeded
  generator over the pack's own pointer domains (an ordered literal's pointer
  discrete-uniform over the lattice [0, 2*max] at the literal's precision;
  enum literals plus one value outside the domain, weighted as one more
  member; applicability pointers inside the domain the pack applies to;
  booleans; evidence present/absent), decided under the pack. A draw the
  runtime refuses, or one the pack does not apply to, is not a decision and
  is dropped and redrawn; a generator that cannot fill the ledger fails the
  construction rather than returning a short one. Seeds 101-130 are reserved
  for the registered attempt and refused elsewhere.

Run: python harness/build_ledgers.py POLICY [--n 5 10 20 50] [--seeds 30] [--seed-base 1] --out DIR
"""
import argparse
import copy
import json
import random
import re
import tempfile
from pathlib import Path

import attempt
import jp

STUDY = Path(__file__).resolve().parent.parent
POLICIES = STUDY / "fixtures" / "policies"
ORDERED = {"greater-than", "greater-than-or-equal", "less-than", "less-than-or-equal"}
RESERVED_SEEDS = (101, 130)
SIZES = (5, 10, 20, 50)


def load_policy(name):
    pack = json.loads((POLICIES / (name + ".pack.json")).read_text())
    base = json.loads((POLICIES / (name + ".base.json")).read_text())
    return pack, base


def conditions(node, out):
    if not isinstance(node, dict):
        return
    op = node.get("op")
    if op == "fact":
        out.append(node)
    for child in node.get("conditions", []) or []:
        conditions(child, out)
    if "condition" in node:
        conditions(node["condition"], out)


def pointer_domains(pack):
    """Every fact pointer the pack compares, with its literal domain."""
    nodes = []
    conditions(pack.get("applicability"), nodes)
    for r in pack.get("rules", []):
        conditions(r.get("when"), nodes)
    for e in pack.get("exceptions", []):
        conditions(e.get("when"), nodes)
    domains = {}
    for c in nodes:
        d = domains.setdefault(c["path"], {"ordered": [], "enum": []})
        if c["operator"] in ORDERED:
            d["ordered"].append(c["value"])
        elif c["operator"] == "in":
            d["enum"].extend(c["value"])
        else:
            d["enum"].append(c["value"])
    return domains


def set_pointer(facts, pointer, value):
    parts = [p for p in pointer.split("/") if p]
    node = facts
    for p in parts[:-1]:
        node = node.setdefault(p, {})
    node[parts[-1]] = value


def get_pointer(facts, pointer):
    node = facts
    for p in [p for p in pointer.split("/") if p]:
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node


def decimals_of(literal):
    return len(literal.split(".")[1]) if "." in literal else 0


def applicability_pointers(pack):
    nodes = []
    conditions(pack.get("applicability"), nodes)
    return {c["path"] for c in nodes}


def random_case(rng, pack, base, domains):
    facts = copy.deepcopy(base["facts"])
    applicable = applicability_pointers(pack)
    for pointer, d in domains.items():
        if pointer in applicable and d["enum"]:
            # a ledger holds the decisions a pack made: its applicability facts
            # are drawn from the domain the pack applies to, never outside it
            values = [json.loads(x) for x in dict.fromkeys(json.dumps(v) for v in d["enum"])]
            set_pointer(facts, pointer, rng.choice(values))
            continue
        if d["ordered"]:
            # discrete uniform over the lattice at the literal's precision:
            # every value in [0, 2L] is drawn with probability 1/(2L+1) in units
            places = max(decimals_of(x) for x in d["ordered"])
            units = max(int(round(float(x) * 10 ** places)) for x in d["ordered"]) * 2
            v = rng.randint(0, max(units, 1))
            text = str(v) if places == 0 else ("%0*d" % (places + 1, v))[:-places] + "." + ("%0*d" % (places + 1, v))[-places:]
            set_pointer(facts, pointer, text)
        elif d["enum"]:
            choices = list(dict.fromkeys(json.dumps(x) for x in d["enum"]))
            values = [json.loads(x) for x in choices]
            if all(isinstance(v, bool) for v in values):
                set_pointer(facts, pointer, rng.choice([True, False]))
            else:
                # one value outside the domain, weighted as one more member
                pick = rng.randrange(len(values) + 1)
                set_pointer(facts, pointer, values[pick] if pick < len(values) else "other-%d" % rng.randrange(1000))
    evidence = {}
    for req in pack.get("evidenceRequirements", []):
        evidence[req["id"]] = rng.choice(["present", "absent"])
    return facts, evidence


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def row(rid, origin, facts, evidence, decided):
    return {"id": rid, "origin": origin, "facts": facts, "evidenceAvailability": evidence,
            "supportedExtensions": [], "expectedDisposition": decided["disposition"]}


def literal_ledger(name, pack, base, root):
    doc = jp.suggest(root, name, base_row=None)
    rows = []
    dropped = 0
    for c in doc["candidates"]:
        facts = deep_merge(base["facts"], c["facts"])
        evidence = dict(base["evidenceAvailability"])
        evidence.update(c.get("evidenceAvailability", {}))
        decided = jp.decide(root, name, facts, evidence)
        if decided["refused"]:
            dropped += 1
            continue
        rows.append(row(re.sub(r"[^A-Za-z0-9._-]", "-", c["id"])[:120], "literal", facts, evidence, decided))
    return {"matrixVersion": "3", "cases": rows}, dropped


def random_ledger(name, pack, base, root, n, seed):
    rng = random.Random("021:%s:%d:%d" % (name, n, seed))
    domains = pointer_domains(pack)
    rows = []
    dropped = 0
    while len(rows) < n:
        if dropped >= 10 * n:
            raise RuntimeError("random ledger %s n=%d seed=%d: %d draws refused or not applicable; the generator does not fit this pack" % (name, n, seed, dropped))
        facts, evidence = random_case(rng, pack, base, domains)
        decided = jp.decide(root, name, facts, evidence)
        # a ledger holds the decisions the pack made: a refused draw, and a
        # draw the pack does not apply to, is not a decision and is dropped
        if decided["refused"] or decided["disposition"].get("kind") == "not-applicable":
            dropped += 1
            continue
        rows.append(row("r%d-%d-%03d" % (n, seed, len(rows)), "random-%d-%d" % (n, seed), facts, evidence, decided))
    return {"matrixVersion": "3", "cases": rows}, dropped


def write_new(path, text):
    """An output is written once: an existing file is refused, never overwritten."""
    with open(path, "x") as f:
        f.write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("policy")
    ap.add_argument("--n", nargs="*", type=int, default=[5, 10, 20, 50])
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--seed-base", type=int, default=1, help="the first seed; pilots drew 1..30, the registered attempt draws 101..130")
    ap.add_argument("--out", required=True)
    ap.add_argument("--reserved", action="store_true", help="draw the seeds reserved for the registered attempt (101-130): requires --out to be a valid, active REGISTERED attempt root (harness/attempt.py); refused otherwise, and required for them")
    args = ap.parse_args()
    seeds = list(range(args.seed_base, args.seed_base + args.seeds))
    reserved = set(range(RESERVED_SEEDS[0], RESERVED_SEEDS[1] + 1))
    if args.reserved:
        if set(seeds) != reserved:
            raise SystemExit("--reserved draws exactly seeds %d-%d" % RESERVED_SEEDS)
        problems, _ = attempt.registered_context_problems(args.out)
        if problems:
            raise SystemExit("reserved seeds need a valid registered attempt at %s:\n  " % args.out + "\n  ".join(problems))
    elif reserved.intersection(seeds):
        raise SystemExit("seeds %d-%d are reserved for the registered attempt (harness/run_attempt.py)" % RESERVED_SEEDS)
    pack, base = load_policy(args.policy)
    out = Path(args.out) / args.policy
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        root = jp.project(tmp, args.policy, pack)
        ledger, dropped = literal_ledger(args.policy, pack, base, root)
        write_new(out / "literal.matrix.json", json.dumps(ledger, indent=1))
        print("literal: %d rows (%d candidates refused)" % (len(ledger["cases"]), dropped))
        for n in args.n:
            for seed in seeds:
                ledger, dropped = random_ledger(args.policy, pack, base, root, n, seed)
                write_new(out / ("random-%d-%d.matrix.json" % (n, seed)), json.dumps(ledger, indent=1))
        print("random: n in %s x %d seeds" % (args.n, args.seeds))


if __name__ == "__main__":
    main()
