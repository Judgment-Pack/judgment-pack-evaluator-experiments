#!/usr/bin/env python3
"""Study 019 E4 — arm A (JPS) adequacy mutant generator.

DETERMINISTIC. Re-running on an unchanged reference pack reproduces byte-identical
m-a-NNN.json files and MANIFEST.json. No timestamps, no randomness, no wall-clock.

One mutant = ONE semantic edit, labelled with its registered class (BRIEF §4.4 /
POLICY-DRAFT design notes). Registered classes generated here:

  1 operator-flip    each ordered comparison, >= <-> > and <= <-> <, one per mutant
  2 boundary-shift   each threshold literal +/-1 at its scale (risk +/-1, spend +/-0.01)
  3 onUnknown-flip   each rule's and each exception's onUnknown, ignore <-> escalate
  4 outcome-swap     each rule's outcome (approve->review, review->approve,
                     enhanced-review->review, reject->review), one per rule
  5 required-flip    financial-evidence required true -> false
  6 effect-swap      each exception's effect to a registered alternative
  7 cascade-deletion each top-level disjunct of the D8 negation cascade, plus the
                     O1 companion rule

SUPPRESS-RULE NON-SWAP (registered, class 6). The `suppress-rule` exceptions
(x-o1-first-engagement and the seven x-d5-suppress-* exceptions) are NOT effect-swapped.
`suppress-rule` carries a `targetRule` member and no `outcome`; `force-outcome` carries an
`outcome` and no `targetRule`; `escalate` carries neither. Every swap out of `suppress-rule`
therefore changes the effect discriminator AND adds/drops a sibling member that the effect
governs, which is two semantic edits under this study's one-edit rule (the brief's own
example). Swaps INTO an effect whose required sibling is a mechanical consequence of the
discriminator are single edits and are generated: force-outcome -> escalate (the now-illegal
`outcome` member is dropped, adding nothing) and escalate -> force-outcome with the
registered outcome `review`. The eight suppress-rule exceptions are recorded here, in
REGISTRY.json, and in the printed summary as class-6 non-members with this reason.

Scored surface ("alignment scope"): kind + outcomeId + reasons ONLY. `handoff` is excluded.

Validation: `jpack spec validate` (semantic layer). A mutant that fails is DROPPED with a
recorded dropCode; it is never silently discarded.

Witness set: the gold row ids on which the mutant's alignment-scope output differs from the
UNMUTATED reference's alignment-scope output on the same row (not from gold — the reference
is the baseline, per §4.4's "disagrees with its own unmutated reference"). An empty witness
set is KEPT and flagged notAdequate: the gold adequacy gate needs a killing row for it, or a
registered drop at prereg time.

Usage: python3 gen_mutants.py [--jobs N]
"""
import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.normpath(os.path.join(HERE, "..", ".."))
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"
JPACK = os.environ.get("JPACK_BIN", SCRATCH + "/pins/jpack/jpack")
REF_PACK = os.path.join(DESIGN, "reference", "refA", "pack.json")
GOLD = os.path.join(DESIGN, "gold", "gold.json")

ORDERED = {"greater-than-or-equal", "greater-than", "less-than-or-equal", "less-than"}
OP_FLIP = {
    "greater-than-or-equal": "greater-than",
    "greater-than": "greater-than-or-equal",
    "less-than-or-equal": "less-than",
    "less-than": "less-than-or-equal",
}
# scale of each numeric fact pointer: (decimal exponent string, step)
SCALES = {
    "/vendor/riskScore": ("1", "1"),
    "/vendor/requestedSpend": ("0.01", "0.01"),
}
OUTCOME_SWAP = {
    "approve": "review",
    "review": "approve",
    "enhanced-review": "review",
    "reject": "review",
}
UNKNOWN_FLIP = {"ignore": "escalate", "escalate": "ignore"}
SUPPRESS_NON_SWAP_REASON = (
    "suppress-rule cannot be swapped in one semantic edit: every target effect requires "
    "adding or dropping the sibling member the effect governs (targetRule vs outcome), "
    "which is a second edit. Registered non-member of class effect-swap."
)


# ---------------------------------------------------------------- pack addressing

def cond_steps(node, steps, out):
    """Depth-first, array order. Yields (steps, node) for every ordered comparison."""
    if isinstance(node, dict) and node.get("operator") in ORDERED:
        out.append((list(steps), node))
    op = node.get("op") if isinstance(node, dict) else None
    if op in ("all", "any"):
        for i, c in enumerate(node.get("conditions", [])):
            cond_steps(c, steps + [("conditions", i)], out)
    elif op == "not":
        cond_steps(node.get("condition", {}), steps + [("condition", None)], out)


def resolve(root, steps):
    node = root
    for key, idx in steps:
        node = node[key] if idx is None else node[key][idx]
    return node


def steps_str(steps):
    return "".join(f".{k}[{i}]" if i is not None else f".{k}" for k, i in steps)


def ordered_comparisons(pack):
    """Deterministic enumeration: rules in array order, then exceptions in array order;
    within each, the condition tree depth-first in array order."""
    locs = []
    for i, r in enumerate(pack["rules"]):
        out = []
        cond_steps(r["when"], [], out)
        for steps, node in out:
            locs.append({
                "root": [("rules", i), ("when", None)],
                "steps": steps,
                "label": f"rules[{i}]({r['id']}).when{steps_str(steps)}",
                "node": node,
            })
    for j, x in enumerate(pack["exceptions"]):
        out = []
        cond_steps(x["when"], [], out)
        for steps, node in out:
            locs.append({
                "root": [("exceptions", j), ("when", None)],
                "steps": steps,
                "label": f"exceptions[{j}]({x['id']}).when{steps_str(steps)}",
                "node": node,
            })
    return locs


def shift(value, path, sign):
    step = Decimal(SCALES[path][1])
    exp = Decimal(SCALES[path][0])
    return str((Decimal(value) + sign * step).quantize(exp))


# ---------------------------------------------------------------- mutant construction

def build_mutants(pack):
    """Returns an ordered list of {class, edit, pack} dicts. Order is fixed by class
    (1..7) and, within a class, by the deterministic enumeration above."""
    out = []
    locs = ordered_comparisons(pack)

    # (1) operator-flip
    for loc in locs:
        old = loc["node"]["operator"]
        new = OP_FLIP[old]
        m = copy.deepcopy(pack)
        resolve(m, loc["root"] + loc["steps"])["operator"] = new
        out.append({"class": "operator-flip",
                    "edit": f"{loc['label']}.operator: {old} -> {new}",
                    "pack": m})

    # (2) boundary-shift
    for loc in locs:
        path = loc["node"]["path"]
        old = loc["node"]["value"]
        for sign, tag in ((1, "+"), (-1, "-")):
            new = shift(old, path, sign)
            m = copy.deepcopy(pack)
            resolve(m, loc["root"] + loc["steps"])["value"] = new
            out.append({"class": "boundary-shift",
                        "edit": f"{loc['label']}.value: {old} -> {new} ({tag}1 at scale)",
                        "pack": m})

    # (3) onUnknown-flip -- rules then exceptions, array order
    for member in ("rules", "exceptions"):
        for i, item in enumerate(pack[member]):
            old = item["onUnknown"]
            new = UNKNOWN_FLIP[old]
            m = copy.deepcopy(pack)
            m[member][i]["onUnknown"] = new
            out.append({"class": "onUnknown-flip",
                        "edit": f"{member}[{i}]({item['id']}).onUnknown: {old} -> {new}",
                        "pack": m})

    # (4) outcome-swap -- one per rule
    for i, r in enumerate(pack["rules"]):
        old = r["outcome"]
        new = OUTCOME_SWAP[old]
        m = copy.deepcopy(pack)
        m["rules"][i]["outcome"] = new
        out.append({"class": "outcome-swap",
                    "edit": f"rules[{i}]({r['id']}).outcome: {old} -> {new}",
                    "pack": m})

    # (5) required-flip -- financial-evidence required true -> false
    for i, e in enumerate(pack["evidenceRequirements"]):
        if e["id"] != "financial-evidence":
            continue
        m = copy.deepcopy(pack)
        m["evidenceRequirements"][i]["required"] = False
        out.append({"class": "required-flip",
                    "edit": f"evidenceRequirements[{i}](financial-evidence).required: true -> false",
                    "pack": m})

    # (6) effect-swap -- force-outcome <-> escalate only; suppress-rule registered non-member
    for j, x in enumerate(pack["exceptions"]):
        if x["effect"] == "force-outcome":
            m = copy.deepcopy(pack)
            m["exceptions"][j]["effect"] = "escalate"
            m["exceptions"][j].pop("outcome", None)
            out.append({"class": "effect-swap",
                        "edit": (f"exceptions[{j}]({x['id']}).effect: force-outcome -> escalate "
                                 f"(the outcome member the discriminator governs is dropped)"),
                        "pack": m})
        elif x["effect"] == "escalate":
            m = copy.deepcopy(pack)
            m["exceptions"][j]["effect"] = "force-outcome"
            m["exceptions"][j]["outcome"] = "review"
            out.append({"class": "effect-swap",
                        "edit": (f"exceptions[{j}]({x['id']}).effect: escalate -> force-outcome "
                                 f"(outcome review, the member the discriminator governs)"),
                        "pack": m})
        # suppress-rule: see SUPPRESS_NON_SWAP_REASON

    # (7) cascade-deletion -- D8's negation cascade disjuncts, then the O1 companion rule
    d8_i = next(i for i, r in enumerate(pack["rules"]) if r["id"] == "r-d8")
    # locate the `not(any(...))` cascade inside r-d8's `when` deterministically
    cascade_steps = None
    stack = [([], pack["rules"][d8_i]["when"])]
    while stack:
        steps, node = stack.pop(0)
        if node.get("op") == "not" and node.get("condition", {}).get("op") == "any":
            cascade_steps = steps + [("condition", None)]
            break
        if node.get("op") in ("all", "any"):
            for k, c in enumerate(node.get("conditions", [])):
                stack.append((steps + [("conditions", k)], c))
        elif node.get("op") == "not":
            stack.append((steps + [("condition", None)], node["condition"]))
    assert cascade_steps is not None, "D8 negation cascade not found"
    cascade = resolve(pack["rules"][d8_i]["when"], cascade_steps)
    n_disj = len(cascade["conditions"])
    for k in range(n_disj):
        m = copy.deepcopy(pack)
        target = resolve(m, [("rules", d8_i), ("when", None)] + cascade_steps)
        removed = target["conditions"].pop(k)
        out.append({"class": "cascade-deletion",
                    "edit": (f"rules[{d8_i}](r-d8).when{steps_str(cascade_steps)}.conditions[{k}] "
                             f"deleted (top-level disjunct of the D8 negation cascade; "
                             f"{disjunct_tag(removed)})"),
                    "pack": m})
    # the O1 companion rule. Deleting a rule requires dropping the exception whose
    # targetRule names it -- a dangling targetRule is not a pack, so the removal of
    # x-d5-suppress-o1-review is mechanical housekeeping of the same single edit, and is
    # named in the edit string.
    o1_i = next(i for i, r in enumerate(pack["rules"]) if r["id"] == "r-o1-review")
    m = copy.deepcopy(pack)
    del m["rules"][o1_i]
    orphans = [x["id"] for x in m["exceptions"] if x.get("targetRule") == "r-o1-review"]
    m["exceptions"] = [x for x in m["exceptions"] if x.get("targetRule") != "r-o1-review"]
    out.append({"class": "cascade-deletion",
                "edit": (f"rules[{o1_i}](r-o1-review) deleted (the O1 companion review rule; "
                         f"dangling targetRule references dropped with it: "
                         f"{', '.join(orphans) or 'none'})"),
                "pack": m})
    return out


def disjunct_tag(node):
    """Stable human tag for a deleted cascade disjunct: its fact pointers in order."""
    bits = []

    def walk(n):
        if not isinstance(n, dict):
            return
        if n.get("op") == "fact":
            bits.append(f"{n['path']} {n['operator']} {n.get('value')}")
        elif n.get("op") == "evidence-present":
            bits.append(f"evidence-present {n['evidenceRequirement']}")
        for c in n.get("conditions", []):
            walk(c)
        if "condition" in n:
            walk(n["condition"])

    walk(node)
    return "; ".join(bits)


# ---------------------------------------------------------------- engine plumbing

def gold_payload(i):
    """Project a gold row's inputs into (facts, evidence) EXACTLY as gold/check_gold.py
    jpack_eval does."""
    vendor = {}
    for src, dst in [("risk", "riskScore"), ("spend", "requestedSpend"),
                     ("sanctions", "sanctionsStatus"), ("country", "countryRisk"),
                     ("newVendor", "newVendor"), ("critical", "criticalSupplier"),
                     ("prior", "priorEnforcement")]:
        if i[src] is not None:
            vendor[dst] = i[src]
    ev = {}
    if i["finEvidence"] is not None:
        ev["financial-evidence"] = i["finEvidence"]
    if i["insurance"] is not None:
        ev["insurance-certificate"] = i["insurance"]
    return {"vendor": vendor}, ev


def alignment_scope(payload):
    """kind + outcomeId + reasons ONLY. handoff excluded."""
    d = payload.get("disposition")
    if d is None:
        return ("refused", payload.get("error", {}).get("class", "unknown-error"), [])
    return (d["kind"], d.get("outcomeId"), sorted(d.get("reasons", [])))


_W = {}


def _init(rows):
    """Per-worker: one temp cwd (no jpack.json), 76 facts/evidence file pairs written once."""
    td = tempfile.mkdtemp(dir=SCRATCH, prefix="mut-")
    _W["td"] = td
    _W["rows"] = rows
    for n, r in enumerate(rows):
        facts, ev = gold_payload(r["inputs"])
        with open(os.path.join(td, f"f{n}.json"), "w") as fh:
            json.dump(facts, fh)
        with open(os.path.join(td, f"e{n}.json"), "w") as fh:
            json.dump(ev, fh)
    _W["env"] = {k: v for k, v in os.environ.items() if k != "JPACK_CONFIG"}


def _validate(pack_path, cwd, env):
    p = subprocess.run([JPACK, "spec", "validate", pack_path, "--format", "json"],
                       capture_output=True, text=True, cwd=cwd, env=env)
    if p.returncode == 0:
        return True, None
    code = None
    try:
        j = json.loads(p.stdout or "{}")
        errs = j.get("errors") or j.get("findings") or []
        if errs and isinstance(errs, list) and isinstance(errs[0], dict):
            code = errs[0].get("code") or errs[0].get("rule") or errs[0].get("message")
        code = code or j.get("code")
    except Exception:
        pass
    if not code:
        code = ((p.stdout or "") + (p.stderr or "")).strip().splitlines()
        code = code[0][:200] if code else f"exit-{p.returncode}"
    return False, f"spec-validate-invalid: {code}"


def _eval_all(pack_path, cwd, env, rows):
    outs = []
    for n in range(len(rows)):
        p = subprocess.run([JPACK, "experimental", "evaluate", pack_path,
                            "--facts", os.path.join(cwd, f"f{n}.json"),
                            "--evidence", os.path.join(cwd, f"e{n}.json"),
                            "--format", "json"],
                           capture_output=True, text=True, cwd=cwd, env=env)
        try:
            payload = json.loads(p.stdout)
        except Exception:
            payload = {"error": {"class": f"no-payload-exit-{p.returncode}"}}
        outs.append(alignment_scope(payload))
    return outs


def run_one(job):
    """job = (mid, mclass, edit, pack_json_text). Returns the manifest entry fields."""
    mid, mclass, edit, text = job
    td, env, rows = _W["td"], _W["env"], _W["rows"]
    pack_path = os.path.join(td, "pack.json")
    with open(pack_path, "w") as fh:
        fh.write(text)
    ok, code = _validate(pack_path, td, env)
    if not ok:
        return mid, False, code, None
    return mid, True, None, _eval_all(pack_path, td, env, rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    args = ap.parse_args()

    pack = json.load(open(REF_PACK))
    rows = json.load(open(GOLD))["rows"]

    mutants = build_mutants(pack)
    jobs = []
    for n, m in enumerate(mutants, start=1):
        mid = f"m-a-{n:03d}"
        text = json.dumps(m["pack"], indent=2, ensure_ascii=False) + "\n"
        with open(os.path.join(HERE, mid + ".json"), "w") as fh:
            fh.write(text)
        jobs.append((mid, m["class"], m["edit"], text))

    # baseline: the unmutated reference over the same 76 rows
    _init(rows)
    ok, code = _validate(REF_PACK, _W["td"], _W["env"])
    if not ok:
        print(f"FATAL: reference pack does not validate: {code}", file=sys.stderr)
        sys.exit(2)
    base = _eval_all(REF_PACK, _W["td"], _W["env"], rows)

    # sanity: the reference must reproduce gold on the alignment scope
    ref_mismatch = []
    for r, got in zip(rows, base):
        want = (("outcome", r["expect"]["disposition"], [])
                if r["expect"]["disposition"] != "unresolved"
                else ("unresolved", None, sorted(r["expect"]["reasons"])))
        if got != want:
            ref_mismatch.append(r["id"])

    with Pool(args.jobs, initializer=_init, initargs=(rows,)) as pool:
        results = dict((mid, (v, c, o)) for mid, v, c, o in pool.map(run_one, jobs, chunksize=1))

    manifest = []
    cell_census = {}
    conflict_only = []
    for mid, mclass, edit, _ in jobs:
        validates, code, outs = results[mid]
        entry = {"id": mid, "class": mclass, "edit": edit, "validates": validates,
                 "witnessSet": [], "notAdequate": False}
        if not validates:
            entry["dropCode"] = code
            entry["witnessSet"] = None
            entry["notAdequate"] = None
        else:
            ws_n = [n for n in range(len(rows)) if outs[n] != base[n]]
            entry["witnessSet"] = [rows[n]["id"] for n in ws_n]
            entry["notAdequate"] = (len(ws_n) == 0)
            # census of what the MUTANT says on its own witness cells: a cell killed by a
            # structural `conflict` is a different kind of evidence from one killed by a
            # differing determination, and only the latter is likely to pair cross-arm.
            kinds = []
            for n in ws_n:
                k, oid, reasons = outs[n]
                lab = f"{k}:{oid}" if k == "outcome" else f"{k}:{'+'.join(reasons)}"
                kinds.append(lab)
                cell_census[lab] = cell_census.get(lab, 0) + 1
            if kinds and set(kinds) == {"unresolved:conflict"}:
                conflict_only.append(mid)
        manifest.append(entry)

    with open(os.path.join(HERE, "MANIFEST.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    counts = {}
    for e in manifest:
        c = counts.setdefault(e["class"], {"generated": 0, "valid": 0, "dropped": 0,
                                           "emptyWitness": 0})
        c["generated"] += 1
        if e["validates"]:
            c["valid"] += 1
            if e["notAdequate"]:
                c["emptyWitness"] += 1
        else:
            c["dropped"] += 1

    registry = {
        "arm": "A (JPS pack)",
        "reference": os.path.relpath(REF_PACK, HERE),
        "goldRows": len(rows),
        "scoredSurface": "kind + outcomeId + reasons (alignment scope); handoff excluded",
        "witnessBaseline": "the unmutated reference pack's alignment-scope output per gold row",
        "referenceReproducesGold": not ref_mismatch,
        "referenceMismatchRows": ref_mismatch,
        "classCounts": counts,
        "totals": {
            "generated": len(manifest),
            "valid": sum(1 for e in manifest if e["validates"]),
            "dropped": sum(1 for e in manifest if not e["validates"]),
            "emptyWitness": sum(1 for e in manifest if e["notAdequate"] is True),
        },
        "witnessCellCensus": dict(sorted(cell_census.items(), key=lambda kv: (-kv[1], kv[0]))),
        "conflictOnlyMutants": conflict_only,
        "conflictNote": (
            "`conflict` is a fifth unresolved reason token, unreachable in the unmutated "
            "reference and absent from gold/check_gold.py's registered reason set. A witness "
            "cell carrying it kills structurally (two rules of different outcome now both "
            "fire) rather than by a differing determination. Arm B (Rego ladder) has no "
            "conflict detection, so these cells are the likeliest source of §4.4 unpairable "
            "mutants; the count is published rather than smoothed."),
        "effectSwapNonMembers": {
            "exceptionIds": [x["id"] for x in pack["exceptions"]
                             if x["effect"] == "suppress-rule"],
            "reason": SUPPRESS_NON_SWAP_REASON,
        },
    }
    with open(os.path.join(HERE, "REGISTRY.json"), "w") as fh:
        json.dump(registry, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"reference reproduces gold on the alignment scope: "
          f"{'yes' if not ref_mismatch else 'NO -> ' + ', '.join(ref_mismatch)}")
    print(f"{'class':<18}{'gen':>5}{'valid':>7}{'dropped':>9}{'empty-witness':>15}")
    for c in ["operator-flip", "boundary-shift", "onUnknown-flip", "outcome-swap",
              "required-flip", "effect-swap", "cascade-deletion"]:
        v = counts.get(c, {"generated": 0, "valid": 0, "dropped": 0, "emptyWitness": 0})
        print(f"{c:<18}{v['generated']:>5}{v['valid']:>7}{v['dropped']:>9}"
              f"{v['emptyWitness']:>15}")
    t = registry["totals"]
    print(f"{'TOTAL':<18}{t['generated']:>5}{t['valid']:>7}{t['dropped']:>9}"
          f"{t['emptyWitness']:>15}")
    print()
    print("effect-swap registered non-members (suppress-rule): "
          + ", ".join(registry["effectSwapNonMembers"]["exceptionIds"]))
    print("  " + SUPPRESS_NON_SWAP_REASON)
    for e in manifest:
        if not e["validates"]:
            print(f"DROPPED {e['id']} [{e['class']}] {e['dropCode']} :: {e['edit']}")
    for e in manifest:
        if e["notAdequate"]:
            print(f"EMPTY-WITNESS {e['id']} [{e['class']}] {e['edit']}")


if __name__ == "__main__":
    main()
