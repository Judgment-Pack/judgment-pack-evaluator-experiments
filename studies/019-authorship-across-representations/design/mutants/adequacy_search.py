#!/usr/bin/env python3
"""Study 019 adequacy search (design-time, deterministic).

PREREGISTRATION SS4 adequacy rule: every mutant is either killed by gold (non-empty
witness set) or registered as dropped with its mechanism. This script does step 1 of
that gate mechanically for the empty-witness remainder of both arms: it enumerates a
dense derived input space and reports, per mutant, the inputs where the mutant's
SCORED SURFACE output differs from its reference's.

What this script is and is not
------------------------------
* It is a WITNESS SEARCH. It says WHERE a mutant is distinguishable from its
  reference. It never says what the policy requires at that input: the gold
  expectation for any row authored from a witness is derived by hand from
  POLICY-DRAFT.md with a clause citation (gold_author.py v0.1 section).
* Arm B (Rego) is searched with the pinned OPA binary itself: reference and mutant
  are loaded into one process (the mutant's `package study` is textually renamed to
  `package study_mut` for the search only) and a comprehension reports the differing
  rows. No model of Rego is involved.
* Arm A (JPS) is searched with a transcription of JPS Core 0.2.0-draft SS7 (condition
  interpretation) and SS8 (resolution model) written below, because the pinned jpack
  CLI evaluates one facts document per process (~19 ms) and the sweep is 419,904
  cells per mutant. The transcription is VALIDATED against the pinned binary before
  it is used (--validate: the 76 gold rows plus a seeded random sample of the dense
  space, on the reference pack and on every searched mutant), and EVERY witness it
  reports is re-confirmed by running the pinned binary on the mutant and on the
  reference at that input. A "no witness anywhere" verdict for arm A therefore rests
  on the transcription plus its validation sample, which is stated as such in
  ADEQUACY.md.

Dense derived space (419,904 cells), per the adequacy work list:
  sanctions   CLEAR | MATCH | UNKNOWN                                   (3)
  country     LOW | MEDIUM | HIGH | omitted                             (4)
  risk        every band boundary (40/70/90) at -1, at, +1, plus the
              domain endpoints 0 and 100, plus omitted                  (12)
  spend       every band boundary (100000.00/500000.00/2000000.00) at
              -0.01, at, +0.01, plus the domain endpoints 0.00 and
              10000000.00, plus omitted                                 (12)
  newVendor / critical / prior      yes | no | omitted                  (3 each)
  finEvidence / insurance           present | absent | omitted          (3 each)
The space carries no malformed or out-of-range values: the registered projection
(POLICY-DRAFT.md, "Scored surface") admits exactly these states.

Registered exclusion X1 is applied to CANDIDACY: a cell in the X1 class can never be
a gold row (check_gold.py asserts this), so it cannot be a killing witness. X1 cells
are still evaluated and counted, so a mutant distinguishable ONLY inside X1 is
reported as such rather than silently dropped.

Usage:
  python3 adequacy_search.py --validate      # transcription vs pinned jpack
  python3 adequacy_search.py --search        # both arms -> adequacy_search.json
  python3 adequacy_search.py --confirm       # re-run pinned binaries on the witnesses
  python3 adequacy_search.py --witnesses     # recompute witness sets over gold.json
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal
from itertools import product
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
REF = os.path.join(DESIGN, "reference")
GOLD = os.path.join(DESIGN, "gold")
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"
JPACK = os.environ.get("JPACK_BIN", SCRATCH + "/pins/jpack/jpack")
OPA = os.environ.get("OPA_BIN", SCRATCH + "/pins/opa/opa_linux_amd64_static")
CAPS = os.environ.get("OPA_CAPS", SCRATCH + "/pins/opa/caps-filtered.json")
WORKDIR = os.environ.get("ADQ_WORK", SCRATCH + "/adq")

# --------------------------------------------------------------------------------------
# The dense derived space
# --------------------------------------------------------------------------------------
RISK = ["0", "39", "40", "41", "69", "70", "71", "89", "90", "91", "100", None]
SPEND = ["0.00", "99999.99", "100000.00", "100000.01", "499999.99", "500000.00",
         "500000.01", "1999999.99", "2000000.00", "2000000.01", "10000000.00", None]
COUNTRY = ["LOW", "MEDIUM", "HIGH", None]
SANCTIONS = ["CLEAR", "MATCH", "UNKNOWN"]
TRI = ["yes", "no", None]
EV = ["present", "absent", None]
KEYS = ("sanctions", "country", "risk", "spend", "newVendor", "critical", "prior",
        "finEvidence", "insurance")


def space():
    """Deterministic enumeration order; the cell index in this order is the cell id."""
    for sa in SANCTIONS:
        for co in COUNTRY:
            for ri in RISK:
                for sp in SPEND:
                    for nv in TRI:
                        for cr in TRI:
                            for pr in TRI:
                                for fe in EV:
                                    for ins in EV:
                                        yield {"sanctions": sa, "country": co, "risk": ri,
                                               "spend": sp, "newVendor": nv, "critical": cr,
                                               "prior": pr, "finEvidence": fe,
                                               "insurance": ins}


def in_x1(i):
    """Registered arm-A inexpressibility class X1 (POLICY-DRAFT.md reference-build results;
    the same predicate check_gold.py asserts over gold.json)."""
    if i["newVendor"] != "yes" or i["risk"] is None:
        return False
    if not (40 <= int(i["risk"]) < 70):
        return False
    low_unread = i["country"] == "LOW" and i["spend"] is None
    cn_small = (i["country"] is None and i["spend"] is not None
                and Decimal(i["spend"]) <= Decimal("100000.00"))
    return low_unread or cn_small


# --------------------------------------------------------------------------------------
# Arm A: JPS Core 0.2.0-draft SS7 + SS8 transcription
# --------------------------------------------------------------------------------------
DEC = re.compile(r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$")
MISSING = object()


def _resolve(pointer, doc):
    if pointer == "":
        return doc
    cur = doc
    for tok in pointer.split("/")[1:]:
        tok = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict) and tok in cur:
            cur = cur[tok]
        else:
            return MISSING
    return cur


def _cond(c, facts, ev):
    """SS7. Returns True / False / None (unknown)."""
    op = c["op"]
    if op == "literal":
        return bool(c["value"])
    if op == "all":                                     # SS7.1 strong conjunction
        vals = [_cond(x, facts, ev) for x in c["conditions"]]
        if any(v is False for v in vals):
            return False
        return True if all(v is True for v in vals) else None
    if op == "any":                                     # SS7.2 strong disjunction
        vals = [_cond(x, facts, ev) for x in c["conditions"]]
        if any(v is True for v in vals):
            return True
        return False if all(v is False for v in vals) else None
    if op == "not":                                     # SS7.3
        v = _cond(c["condition"], facts, ev)
        return None if v is None else (not v)
    if op == "evidence-present":                        # SS7.5
        s = ev.get(c["evidenceRequirement"], "unknown")
        return True if s == "present" else (False if s == "absent" else None)
    if op == "fact":                                    # SS7.4
        val = _resolve(c["path"], facts)
        oper = c["operator"]
        if val is MISSING:
            return None
        if oper in ("equals", "not-equals"):
            eq = (type(val) is type(c["value"])) and val == c["value"]
            return eq if oper == "equals" else (not eq)
        if oper == "in":
            return any((type(val) is type(x)) and val == x for x in c["value"])
        operand = c["value"]
        if not (isinstance(val, str) and DEC.match(val)):
            return None
        if not (isinstance(operand, str) and DEC.match(operand)):
            return None
        a, b = Decimal(val), Decimal(operand)
        return {"greater-than": a > b, "greater-than-or-equal": a >= b,
                "less-than": a < b, "less-than-or-equal": a <= b}[oper]
    raise ValueError("unhandled op " + op)


def jps_resolve(pack, facts, ev):
    """SS8 resolution model. Returns the scored surface: (kind_or_outcome, sorted reasons)."""
    reasons = set()
    # SS8 step 1: applicability omitted -> true (the packs declare none).
    app = pack.get("applicability")
    if app is not None:
        v = _cond(app, facts, ev)
        if v is False:
            return ("not-applicable", ["not-applicable"])
        if v is None:
            return ("unresolved", ["unknown"])
    # step 2: required evidence
    states = []
    for r in pack.get("evidenceRequirements", []):
        if r.get("required"):
            s = ev.get(r["id"], "unknown")
            states.append(True if s == "present" else (False if s == "absent" else None))
    if any(s is False for s in states):
        reasons.add("missing-required-evidence")
    elif any(s is None for s in states):
        reasons.add("unknown")
    # steps 3-4: exceptions
    suppressed, forced, escalate = set(), set(), False
    for x in pack.get("exceptions", []):
        v = _cond(x["when"], facts, ev)
        if v is None:
            if x.get("onUnknown", "ignore") == "escalate":
                reasons.add("unknown")
            continue
        if v is not True:
            continue
        eff = x["effect"]
        if eff == "suppress-rule":
            suppressed.add(x["targetRule"])
        elif eff == "force-outcome":
            forced.add(x["outcome"])
        elif eff == "escalate":
            escalate = True
            reasons.add("exception-escalation")
    # step 5
    if len(forced) > 1:
        reasons.add("conflict")
    if reasons:
        return ("unresolved", sorted(reasons))
    # step 6
    if len(forced) == 1:
        return ("outcome", next(iter(forced)))
    # steps 7-8: rules
    candidates = set()
    for rule in pack.get("rules", []):
        if rule["id"] in suppressed:
            continue
        v = _cond(rule["when"], facts, ev)
        if v is True:
            candidates.add(rule["outcome"])
        elif v is None and rule.get("onUnknown", "ignore") == "escalate":
            reasons.add("unknown")
    if len(candidates) > 1:
        reasons.add("conflict")
    if reasons:                                          # step 8 blocking
        return ("unresolved", sorted(reasons))
    # step 9
    if len(candidates) == 1:
        return ("outcome", next(iter(candidates)))
    # step 10
    if "fallbackOutcome" in pack:
        return ("outcome", pack["fallbackOutcome"])
    return ("unresolved", ["no-match"])


def jps_trace(pack, facts, ev):
    """The per-rule / per-exception condition vector, for locating the cells where a mutant's
    EDIT IS LIVE (its rule or exception evaluates differently from the reference's) even
    though the disposition is unchanged. Those cells are where an equivalence claim is
    actually at risk, so they are the cells the pinned engine is asked to adjudicate."""
    return (tuple(_cond(r["when"], facts, ev) for r in pack.get("rules", [])),
            tuple(_cond(x["when"], facts, ev) for x in pack.get("exceptions", [])))


def jps_project(i):
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


def sim_a(pack, i):
    facts, ev = jps_project(i)
    return jps_resolve(pack, facts, ev)


def jpack_eval(packpath, i):
    """The pinned jpack CLI, same flags as check_gold.py."""
    facts, ev = jps_project(i)
    os.makedirs(WORKDIR, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WORKDIR) as td:
        f, e = os.path.join(td, "f.json"), os.path.join(td, "e.json")
        json.dump(facts, open(f, "w"))
        json.dump(ev, open(e, "w"))
        p = subprocess.run([JPACK, "experimental", "evaluate", packpath,
                            "--facts", f, "--evidence", e, "--format", "json"],
                           capture_output=True, text=True, cwd=td)
        if not p.stdout.strip():
            raise RuntimeError("jpack: " + p.stderr.strip()[:300])
        d = json.loads(p.stdout)["disposition"]
    if d["kind"] == "outcome":
        return ("outcome", d["outcomeId"])
    return (d["kind"], sorted(d.get("reasons", [])))


def scored(res):
    """Normalize both engines' answers onto the E1 scored surface."""
    kind, payload = res
    if kind == "outcome":
        return ("outcome", payload, ())
    return (kind, None, tuple(payload))


# --------------------------------------------------------------------------------------
# Arm B: the pinned OPA binary, reference and mutant in one process
# --------------------------------------------------------------------------------------
def opa_project(i):
    v = {}
    if i["risk"] is not None:
        v["riskScore"] = json.loads(i["risk"])
    if i["spend"] is not None:
        v["requestedSpend"] = json.loads(i["spend"])
    for src, dst in [("sanctions", "sanctionsStatus"), ("country", "countryRisk"),
                     ("newVendor", "newVendor"), ("critical", "criticalSupplier"),
                     ("prior", "priorEnforcement")]:
        if i[src] is not None:
            v[dst] = i[src]
    ev = {}
    if i["finEvidence"] is not None:
        ev["financial-evidence"] = i["finEvidence"]
    if i["insurance"] is not None:
        ev["insurance-certificate"] = i["insurance"]
    return {"vendor": v, "evidence": ev}


OPA_DIFF_QUERY = ("[[i, a, b] | some i, row in data.rows; "
                  "a := data.study.decision with input as row; "
                  "b := data.study_mut.decision with input as row; a != b]")
OPA_ONE_QUERY = ("[[i, b] | some i, row in data.rows; "
                 "b := data.study_mut.decision with input as row]")


def opa_run(mutant_path, rows_path, query, extra_ref=True):
    os.makedirs(WORKDIR, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WORKDIR) as td:
        mut = os.path.join(td, "mut.rego")
        src = open(mutant_path).read()
        assert "\npackage study\n" in src, mutant_path
        open(mut, "w").write(src.replace("\npackage study\n", "\npackage study_mut\n", 1))
        cmd = [OPA, "eval", "--format", "json", "--fail", "--strict-builtin-errors",
               "--capabilities", CAPS, "--timeout", "600s"]
        if extra_ref:
            cmd += ["--data", os.path.join(REF, "refB", "policy.rego")]
        cmd += ["--data", mut, "--data", rows_path, query]
        p = subprocess.run(cmd, capture_output=True, text=True,
                           env=dict(os.environ, TZ="UTC"), cwd=td)
        if p.returncode != 0 and not p.stdout.strip():
            raise RuntimeError("opa: " + p.stderr.strip()[:300])
        return json.loads(p.stdout)["result"][0]["expressions"][0]["value"]


# --------------------------------------------------------------------------------------
# Validation of the arm-A transcription against the pinned binary
# --------------------------------------------------------------------------------------
def load_manifests():
    a = json.load(open(os.path.join(HERE, "refA", "MANIFEST.json")))
    b = json.load(open(os.path.join(HERE, "refB", "MANIFEST.json")))
    return a, b


def validate(sample_n=120, seed=19):
    cells = list(space())
    rng = random.Random(seed)
    sample = [cells[k] for k in rng.sample(range(len(cells)), sample_n)]
    gold = json.load(open(os.path.join(GOLD, "gold.json")))["rows"]
    goldcells = [r["inputs"] for r in gold]
    mana, _ = load_manifests()
    targets = [("reference", os.path.join(REF, "refA", "pack.json"))]
    targets += [(m["id"], os.path.join(HERE, "refA", m["id"] + ".json"))
                for m in mana if m["notAdequate"]]
    bad, checked = [], 0
    for name, path in targets:
        pack = json.load(open(path))
        cs = goldcells + sample if name == "reference" else sample[:40]
        for c in cs:
            got, want = scored(sim_a(pack, c)), scored(jpack_eval(path, c))
            checked += 1
            if got != want:
                bad.append({"target": name, "cell": c, "sim": got, "engine": want})
    print(f"validate: {checked} checked evaluations, {len(bad)} disagreements")
    for b in bad[:10]:
        print("  DISAGREE", b)
    out = {"checkedEvaluations": checked, "disagreements": bad, "sampleN": sample_n,
           "seed": seed, "targets": [t[0] for t in targets]}
    json.dump(out, open(os.path.join(HERE, "adequacy_validation.json"), "w"),
              indent=1, sort_keys=True)
    return 1 if bad else 0


# --------------------------------------------------------------------------------------
# Search
# --------------------------------------------------------------------------------------
CELLS = None
REFOUT = None
MAXW = 8


def _init_a():
    global CELLS, REFOUT
    CELLS = list(space())
    refpack = json.load(open(os.path.join(REF, "refA", "pack.json")))
    REFOUT = [scored(sim_a(refpack, c)) for c in CELLS]


def _search_a(mid):
    pack = json.load(open(os.path.join(HERE, "refA", mid + ".json")))
    wit, x1only, ndiff, nx1 = [], 0, 0, 0
    for k, c in enumerate(CELLS):
        got = scored(sim_a(pack, c))
        if got == REFOUT[k]:
            continue
        ndiff += 1
        if in_x1(c):
            nx1 += 1
            continue
        if len(wit) < MAXW:
            wit.append({"cellIndex": k, "inputs": c,
                        "reference": list(REFOUT[k][:2]) + [list(REFOUT[k][2])],
                        "mutant": list(got[:2]) + [list(got[2])]})
    return {"id": mid, "diffCells": ndiff, "diffCellsInX1": nx1,
            "diffCellsOutsideX1": ndiff - nx1, "witnesses": wit}


def search_a():
    mana, _ = load_manifests()
    ids = [m["id"] for m in mana if m["notAdequate"]]
    _init_a()
    with Pool(int(os.environ.get("ADQ_JOBS", "12")), initializer=_init_a) as pool:
        res = pool.map(_search_a, ids)
    return {r["id"]: r for r in res}


def _search_b(mid):
    rows_path = os.path.join(WORKDIR, "rows_dense.json")
    diffs = opa_run(os.path.join(HERE, "refB", mid + ".rego"), rows_path, OPA_DIFF_QUERY)
    cells = list(space())
    wit, nx1 = [], 0
    for idx, a, b in diffs:
        c = cells[idx]
        if in_x1(c):
            nx1 += 1
            continue
        if len(wit) < MAXW:
            wit.append({"cellIndex": idx, "inputs": c, "reference": a, "mutant": b})
    return {"id": mid, "diffCells": len(diffs), "diffCellsInX1": nx1,
            "diffCellsOutsideX1": len(diffs) - nx1, "witnesses": wit}


def search_b():
    _, manb = load_manifests()
    ids = [m["id"] for m in manb["mutants"] if m.get("notAdequate")]
    os.makedirs(WORKDIR, exist_ok=True)
    rows_path = os.path.join(WORKDIR, "rows_dense.json")
    json.dump({"rows": [opa_project(c) for c in space()]}, open(rows_path, "w"))
    with Pool(int(os.environ.get("ADQ_JOBS", "8"))) as pool:
        res = pool.map(_search_b, ids)
    return {r["id"]: r for r in res}


def confirm(report):
    """Re-run the pinned jpack binary on EVERY arm-A witness the transcription reported, on
    the mutant and on the reference. A witness the pinned engine does not reproduce is a
    transcription defect and fails the run."""
    out = []
    refpack = os.path.join(REF, "refA", "pack.json")
    for mid, r in sorted(report["armA"].items()):
        for w in r["witnesses"]:
            got_ref = list(scored(jpack_eval(refpack, w["inputs"])))
            got_mut = list(scored(jpack_eval(os.path.join(HERE, "refA", mid + ".json"),
                                             w["inputs"])))
            got_ref = got_ref[:2] + [list(got_ref[2])]
            got_mut = got_mut[:2] + [list(got_mut[2])]
            out.append({"id": mid, "cellIndex": w["cellIndex"],
                        "engineReference": got_ref, "engineMutant": got_mut,
                        "distinguished": got_ref != got_mut,
                        "simAgreesReference": got_ref == w["reference"],
                        "simAgreesMutant": got_mut == w["mutant"]})
    return out


# --------------------------------------------------------------------------------------
# Witness-set recomputation over gold.json (both arms, pinned binaries)
# --------------------------------------------------------------------------------------
LIVE_N = 120


def _drops_a(mid):
    """For an arm-A mutant with no witness in the sweep: enumerate the cells where its edit is
    LIVE (condition vector differs from the reference's) and hand a deterministic sample of
    them to the pinned engine on both packs. The engine, not the transcription, then says
    whether the two are distinguishable there."""
    pack = json.load(open(os.path.join(HERE, "refA", mid + ".json")))
    refpack = json.load(open(os.path.join(REF, "refA", "pack.json")))
    live = []
    for k, c in enumerate(CELLS):
        facts, ev = jps_project(c)
        if jps_trace(pack, facts, ev) != jps_trace(refpack, facts, ev):
            live.append(k)
    step = max(1, len(live) // LIVE_N)
    sample = live[::step][:LIVE_N]
    refpath = os.path.join(REF, "refA", "pack.json")
    mutpath = os.path.join(HERE, "refA", mid + ".json")
    diffs = []
    for k in sample:
        a, b = scored(jpack_eval(refpath, CELLS[k])), scored(jpack_eval(mutpath, CELLS[k]))
        if a != b:
            diffs.append({"cellIndex": k, "inputs": CELLS[k],
                          "engineReference": list(a[:2]) + [list(a[2])],
                          "engineMutant": list(b[:2]) + [list(b[2])]})
    return {"id": mid, "liveCells": len(live), "engineCheckedCells": len(sample),
            "engineDifferences": diffs}


def drops_a():
    """Engine-backed evidence under the arm-A no-witness verdicts."""
    report = json.load(open(os.path.join(HERE, "adequacy_search.json")))
    ids = [k for k, v in sorted(report["armA"].items()) if not v["diffCellsOutsideX1"]]
    _init_a()
    with Pool(int(os.environ.get("ADQ_JOBS", "12")), initializer=_init_a) as pool:
        res = pool.map(_drops_a, ids)
    bad = [r for r in res if r["engineDifferences"]]
    json.dump({"mutants": res, "liveCellSampleSize": LIVE_N},
              open(os.path.join(HERE, "adequacy_drops.json"), "w"), indent=1, sort_keys=True)
    tot = sum(r["engineCheckedCells"] for r in res)
    print(f"drops: {len(ids)} arm-A no-witness mutants; {tot} live-edit cells adjudicated by "
          f"the pinned engine; {len(bad)} mutants distinguishable there")
    for r in bad[:10]:
        print("  DISTINGUISHABLE", r["id"], r["engineDifferences"][0])
    return 1 if bad else 0


ONUNKNOWN_DROPS = ["r-d1", "r-d6a", "r-d6b-insured", "r-d6b-uninsured", "r-d6c", "r-d7"]


def mechanisms():
    """Mechanical check of the two mechanisms the arm-A onUnknown-flip drops rest on. A
    condition vector cannot show these: `onUnknown` is not part of any condition, so the
    live-edit trace is silent on them and they are checked here directly, over the same
    dense space.

      (1) never-unknown-rule: the rule's condition is never `unknown` (r-d1).
      (2) reason-set idempotence: wherever the rule's condition IS unknown and the rule is
          actually evaluated (no evidence/exception block, no forced outcome, not
          suppressed), r-d8 is unknown and unsuppressed as well -- and r-d8 already carries
          `onUnknown: escalate`, so the flipped rule's escalate can only re-record the
          `unknown` token SS8 already keeps in a de-duplicated set.

    A nonzero count for either is a witness the sweep should have found; it fails the run.
    """
    pack = json.load(open(os.path.join(REF, "refA", "pack.json")))
    rules = pack["rules"]
    idx = {r["id"]: n for n, r in enumerate(rules)}
    counts = {rid: {"unknownCells": 0, "unknownAndEvaluated": 0, "notCoveredByD8": 0}
              for rid in ONUNKNOWN_DROPS}
    for c in space():
        facts, ev = jps_project(c)
        # SS8 steps 2-6: is the rule stage reached at all, and with what suppressions?
        blocked = False
        for r in pack["evidenceRequirements"]:
            if r.get("required") and ev.get(r["id"], "unknown") != "present":
                blocked = True
        suppressed, forced = set(), set()
        for x in pack["exceptions"]:
            v = _cond(x["when"], facts, ev)
            if v is None:
                if x.get("onUnknown", "ignore") == "escalate":
                    blocked = True
                continue
            if v is not True:
                continue
            if x["effect"] == "suppress-rule":
                suppressed.add(x["targetRule"])
            elif x["effect"] == "force-outcome":
                forced.add(x["outcome"])
            elif x["effect"] == "escalate":
                blocked = True
        vals = [_cond(r["when"], facts, ev) for r in rules]
        d8_unknown = vals[idx["r-d8"]] is None and "r-d8" not in suppressed
        for rid in ONUNKNOWN_DROPS:
            if vals[idx[rid]] is not None:
                continue
            counts[rid]["unknownCells"] += 1
            if blocked or len(forced) == 1 or rid in suppressed:
                continue
            counts[rid]["unknownAndEvaluated"] += 1
            if not d8_unknown:
                counts[rid]["notCoveredByD8"] += 1
    json.dump(counts, open(os.path.join(HERE, "adequacy_mechanisms.json"), "w"),
              indent=1, sort_keys=True)
    bad = [k for k, v in counts.items() if v["notCoveredByD8"]]
    if counts["r-d1"]["unknownCells"]:
        bad.append("r-d1 (condition is unknown somewhere)")
    print("mechanisms:", json.dumps(counts, sort_keys=True))
    print(f"mechanisms: {len(bad)} unexplained")
    return 1 if bad else 0


def witness_sets():
    gold = json.load(open(os.path.join(GOLD, "gold.json")))["rows"]
    mana, manb = load_manifests()
    # arm A: pinned jpack per (mutant, row)
    outA = {}
    want = {r["id"]: (("outcome", r["expect"]["disposition"], ())
                      if r["expect"]["disposition"] != "unresolved"
                      else ("unresolved", None, tuple(sorted(r["expect"]["reasons"]))))
            for r in gold}
    args = [(m["id"], os.path.join(HERE, "refA", m["id"] + ".json")) for m in mana]
    with Pool(int(os.environ.get("ADQ_JOBS", "12"))) as pool:
        for mid, ws in pool.starmap(_witness_a, [(a, b, gold, want) for a, b in args]):
            outA[mid] = ws
    # arm B: one OPA process per mutant over all gold rows
    os.makedirs(WORKDIR, exist_ok=True)
    rows_path = os.path.join(WORKDIR, "rows_gold.json")
    json.dump({"rows": [opa_project(r["inputs"]) for r in gold]}, open(rows_path, "w"))
    ids = [m["id"] for m in manb["mutants"] if m.get("status") != "dropped"]
    outB = {}
    with Pool(int(os.environ.get("ADQ_JOBS", "8"))) as pool:
        for mid, ws in pool.starmap(_witness_b, [(i, rows_path, gold, want) for i in ids]):
            outB[mid] = ws
    json.dump({"armA": outA, "armB": outB},
              open(os.path.join(HERE, "adequacy_witnesses.json"), "w"),
              indent=1, sort_keys=True)
    print(f"witness sets: armA {sum(1 for v in outA.values() if v)}/{len(outA)} killed, "
          f"armB {sum(1 for v in outB.values() if v)}/{len(outB)} killed")


def _witness_a(mid, path, gold, want):
    ws = []
    for r in gold:
        got = scored(jpack_eval(path, r["inputs"]))
        if got != want[r["id"]]:
            ws.append(r["id"])
    return mid, ws


def _witness_b(mid, rows_path, gold, want):
    vals = opa_run(os.path.join(HERE, "refB", mid + ".rego"), rows_path, OPA_ONE_QUERY,
                   extra_ref=False)
    ws = []
    for idx, v in vals:
        r = gold[idx]
        got = (("outcome", v["disposition"], ()) if v["disposition"] != "unresolved"
               else ("unresolved", None, tuple(sorted(v["reasons"]))))
        if got != want[r["id"]]:
            ws.append(r["id"])
    return mid, ws



# --------------------------------------------------------------------------------------
# Registered drops: mutant -> (mechanism class, mechanism). Every entry is a mutant the
# sweep found NOWHERE distinguishable from its reference over the 419,904-cell dense space
# (X1 cells included: none of them is X1-only). The mechanism is the reason the edit cannot
# change the scored surface; it is stated in terms of the pack/policy, not of gold.
# --------------------------------------------------------------------------------------
DROPS = {
 # ---- arm A -------------------------------------------------------------------------
 "m-a-006": ("same-outcome-overlap",
   "r-d6b-insured's lower spend edge is relaxed onto $500,000.00. The only cells it newly "
   "admits (CLEAR, LOW, risk<40, spend exactly $500,000.00) are already r-d6a's, and both "
   "rules name `approve`, so the candidate set is unchanged (SS8 step 9: multiple true rules "
   "naming one outcome are compatible). The one exception that suppresses r-d6a (D5) "
   "suppresses r-d6b-insured too, so no cell suppresses one without the other."),
 "m-a-046": ("same-outcome-overlap",
   "Same cells as m-a-006 by the threshold form of the edit (500000.00 -> 499999.99): the "
   "newly admitted cell is r-d6a's and both rules name `approve`."),
 "m-a-017": ("same-outcome-overlap",
   "r-o1-review is widened to risk exactly 70. There r-d8 already fires, and r-o1-review "
   "also names `review`: same-outcome overlap, no conflict, same candidate set."),
 "m-a-067": ("same-outcome-overlap",
   "Threshold form of m-a-017 (70 -> 71): the widened cells are r-d8's and both name "
   "`review`."),
 "m-a-069": ("same-outcome-overlap",
   "r-o1-review is widened to spend exactly $100,000.01, where r-d8 fires and also names "
   "`review`."),
 "m-a-056": ("same-outcome-overlap",
   "r-d6c is widened to risk exactly 39, where r-d6a already approves (D6c's spend ceiling "
   "$100,000.00 lies inside D6a's $500,000.00). Where O1 suppresses r-d6c the widened rule "
   "is suppressed with it; where D5 suppresses r-d6a it suppresses r-d6c too."),
 "m-a-024": ("shadowed-cascade-branch",
   "The edit relaxes the D6b-insured COPY inside r-d8's `not(any ...)` onto spend exactly "
   "$500,000.00. At every such cell the D6a copy in the same `any` is already true, so the "
   "disjunction is true either way (SS7.2), the negation is false either way, and r-d8's "
   "condition value is unchanged on all 419,904 cells (live-edit cells: 0)."),
 "m-a-027": ("shadowed-cascade-branch",
   "As m-a-024 for the D6b-uninsured copy; the D6a copy dominates the same cells "
   "(live-edit cells: 0)."),
 "m-a-082": ("shadowed-cascade-branch",
   "As m-a-024 by the threshold form (500000.00 -> 499999.99); dominated by the D6a copy "
   "(live-edit cells: 0)."),
 "m-a-088": ("shadowed-cascade-branch",
   "As m-a-027 by the threshold form; dominated by the D6a copy (live-edit cells: 0)."),
 "m-a-092": ("shadowed-cascade-branch",
   "The D6c copy inside the cascade is widened to risk exactly 39, where the D6a copy is "
   "already true (D6c's spend ceiling lies inside D6a's) (live-edit cells: 0). The REGION is "
   "reachable and gold visits it (d6a-39-50k, d6a-500k*); what is unreachable is any effect "
   "of the edit."),
 "m-a-103": ("never-unknown-rule",
   "Kleene-monotone onUnknown flip. r-d1's condition reads only /vendor/sanctionsStatus, "
   "which the registered projection always supplies as a present string (UNKNOWN is a value, "
   "not an omission), so the condition is never `unknown` and `onUnknown` is never consulted: "
   "0 unknown cells of 419,904 (adequacy_mechanisms.json)."),
 "m-a-107": ("reason-set-idempotence",
   "onUnknown flip on r-d6a. Wherever r-d6a's condition is unknown AND the rule stage is "
   "reached at all (no evidence/exception block, no forced outcome, not suppressed), r-d8 is "
   "unknown and unsuppressed too, because its negation cascade carries a copy of the same "
   "conjuncts: 972 such cells, 0 uncovered. r-d8 already carries `onUnknown: escalate`, and "
   "SS8 keeps reasons as a de-duplicated set, so the flip can only re-record `unknown`."),
 "m-a-108": ("reason-set-idempotence",
   "As m-a-107 for r-d6b-insured: 432 unknown-and-evaluated cells, 0 uncovered by r-d8."),
 "m-a-109": ("reason-set-idempotence",
   "As m-a-107 for r-d6b-uninsured: 432 unknown-and-evaluated cells, 0 uncovered by r-d8."),
 "m-a-110": ("reason-set-idempotence",
   "As m-a-107 for r-d6c: 456 unknown-and-evaluated cells, 0 uncovered by r-d8."),
 "m-a-111": ("reason-set-idempotence",
   "As m-a-107 for r-d7: 540 unknown-and-evaluated cells, 0 uncovered by r-d8."),
 # ---- arm B -------------------------------------------------------------------------
 "m-b-007": ("ladder-order-masked",
   "D6b's lower spend edge is relaxed onto $500,000.00, but the D6a rung above it consumes "
   "spend <= $500,000.00 with risk < 40 in LOW first, so the widened rung is never reached."),
 "m-b-010": ("ladder-order-masked", "As m-b-007, D6b's absent-certificate rung."),
 "m-b-013": ("ladder-order-masked", "As m-b-007, D6b's unreported-availability rung."),
 "m-b-033": ("ladder-order-masked",
   "Threshold form of m-b-007 (500000 -> 499999.99) on the insured rung: the cell it adds is "
   "consumed by the D6a rung above."),
 "m-b-039": ("ladder-order-masked", "As m-b-033, absent-certificate rung."),
 "m-b-045": ("ladder-order-masked", "As m-b-033, unreported-availability rung."),
 "m-b-145": ("ladder-order-masked",
   "Deleting `spend > 500000` widens the D6b insured rung down to spend 0, but the D6a rung "
   "above already consumes spend <= $500,000.00 at risk < 40 in LOW."),
 "m-b-150": ("ladder-order-masked", "As m-b-145, absent-certificate rung."),
 "m-b-155": ("ladder-order-masked", "As m-b-145, unreported-availability rung."),
 "m-b-049": ("ladder-order-masked",
   "D6c's risk floor drops to 39, but the D6a rung above consumes risk < 40 with spend "
   "<= $500,000.00, which contains D6c's spend <= $100,000.00."),
 "m-b-159": ("ladder-order-masked",
   "Deleting `risk >= 40` widens D6c to all risk < 70; the sub-region risk < 40 is consumed "
   "by the D6a rung above (same containment as m-b-049)."),
 "m-b-132": ("entailed-guard",
   "`v_sanctions == \"CLEAR\"` deleted from a rung BELOW the D1 and D2 rungs of the same "
   "`else` chain: control reaches it only when sanctions is neither MATCH nor UNKNOWN, and "
   "the registered projection admits exactly {CLEAR, MATCH, UNKNOWN} as a present string, so "
   "the deleted conjunct is entailed there."),
 "m-b-134": ("entailed-guard", "As m-b-132 (D4 rung)."),
 "m-b-137": ("entailed-guard", "As m-b-132 (D5 rung)."),
 "m-b-138": ("entailed-guard", "As m-b-132 (D6a rung)."),
 "m-b-142": ("entailed-guard", "As m-b-132 (D6b insured rung)."),
 "m-b-147": ("entailed-guard", "As m-b-132 (D6b absent-certificate rung)."),
 "m-b-152": ("entailed-guard", "As m-b-132 (D6b unreported-availability rung)."),
 "m-b-157": ("entailed-guard", "As m-b-132 (D6c rung)."),
 "m-b-162": ("entailed-guard", "As m-b-132 (D7 rung)."),
 "m-b-166": ("entailed-guard",
   "As m-b-132 for the D8 rung; the deletion additionally makes D8 total and shadows the "
   "backstop rung below it, which the registered three-state sanctions domain already made "
   "unreachable."),
 "m-b-062": ("entailed-guard",
   "`fin_state == \"present\"` deleted from a decision-ladder rung below the two P1 rungs, "
   "which return for `absent` and for `OMITTED`: the conjunct is entailed below them. This "
   "is the ledger's inert-O3-conjunct row, now measured as an unkillable mutant."),
 "m-b-084": ("entailed-guard", "As m-b-062 (O3 rung)."),
 "m-b-088": ("entailed-guard", "As m-b-062 (U1 singleton rung)."),
 "m-b-090": ("entailed-guard", "As m-b-062 (U1 otherwise rung)."),
 "m-b-083": ("duplicated-test",
   "Inverting `fin_state == \"present\"` makes the entrypoint O3 rung unsatisfiable below "
   "P1, so control falls to the U1 rungs, whose `determine` carries its own O3 rung with the "
   "same test: the same disposition is issued one rung later."),
 "m-b-085": ("duplicated-test",
   "Inverting `v_spend != null` makes the entrypoint O3 rung unsatisfiable (a null spend "
   "never exceeds 2,000,000 under OPA's total value ordering), so control falls to U1, whose "
   "`determine` re-tests O3 over the spend candidate list and issues the same disposition."),
 "m-b-086": ("entailed-guard",
   "Deleting `v_spend != null` is inert because a null spend compares below every number "
   "under OPA's total ordering, so `v_spend > 2000000` is already false there. The guard "
   "documents an intent the language enforces anyway."),
 "m-b-060": ("duplicated-test",
   "The entrypoint O3 rung's threshold is shifted, but where the shifted rung stops firing "
   "(HIGH, readable spend exactly $2,000,000.01) U1's singleton path re-issues the same "
   "escalation through `determine`'s own O3 rung, whose threshold this edit does not touch."),
 "m-b-124": ("unreachable-default",
   "`default decision` swap. The decision ladder ends in an unconditional `else`, so the "
   "registered default is never consulted. The default is a registered arm-C convention "
   "(the only default preserving D2); in a build whose ladder is total, its mutants are "
   "unkillable by construction."),
 "m-b-125": ("unreachable-default", "As m-b-124 (disposition member of the same default)."),
 "m-b-171": ("entailed-guard",
   "`count(u1_determinations) != 1` deleted from the ladder's final `else`, which is reached "
   "only when the rung above it failed `count == 1`: the guard is entailed."),
 "m-b-174": ("equivalent-fallthrough",
   "Deleting `determine`'s D2 rung leaves sanctions UNKNOWN to fall past every CLEAR-guarded "
   "rung to the ladder's backstop, which carries the same value, unresolved{no-match}."),
 "m-b-185": ("unreachable-rung",
   "Deleting `determine`'s backstop rung is inert: D1, D2 and D8 are jointly total over the "
   "registered three-state sanctions domain, so the backstop is unreachable."),
}


def update_manifests():
    """Write the adequacy disposition into both MANIFESTs (shapes unchanged: refA is a list,
    refB is an object with a `mutants` list)."""
    w = json.load(open(os.path.join(HERE, "adequacy_witnesses.json")))
    gold = json.load(open(os.path.join(GOLD, "gold.json")))
    goldids = [r["id"] for r in gold["rows"]]
    goldsha = _sha256(os.path.join(GOLD, "gold.json"))
    added = set(goldids) - set(json.load(open(os.path.join(HERE, "v0_row_ids.json"))))
    stamp = {"gate": "adequacy (PREREGISTRATION SS4), 2026-08-15",
             "goldVersion": gold["goldVersion"], "goldRows": len(goldids),
             "goldSha256": goldsha,
             "search": "adequacy_search.py --search over 419,904 dense derived cells"}

    mana = json.load(open(os.path.join(HERE, "refA", "MANIFEST.json")))
    for m in mana:
        _stamp(m, w["armA"].get(m["id"], []), added, stamp)
    json.dump(mana, open(os.path.join(HERE, "refA", "MANIFEST.json"), "w"),
              indent=1, sort_keys=True)

    manb = json.load(open(os.path.join(HERE, "refB", "MANIFEST.json")))
    for m in manb["mutants"]:
        if m.get("status") == "dropped":
            continue
        _stamp(m, w["armB"].get(m["id"], []), added, stamp)
    manb["gold"] = {"path": "gold/gold.json", "goldVersion": gold["goldVersion"],
                    "rows": len(goldids), "sha256": goldsha,
                    "referenceReproducesGold": True, "referenceGoldMismatches": []}
    ew = [m for m in manb["mutants"] if m.get("notAdequate")]
    manb["counts"]["emptyWitness"] = len(ew)
    for cls, blk in manb["counts"]["perClass"].items():
        blk["emptyWitness"] = len([m for m in ew if m["mutationClass"] == cls])
    manb["adequacyGate"] = dict(stamp, killed=len([m for m in manb["mutants"]
                                                   if m.get("witnessSet")]),
                                dropped=len(ew))
    json.dump(manb, open(os.path.join(HERE, "refB", "MANIFEST.json"), "w"),
              indent=1, sort_keys=True)
    valid_b = [m for m in manb["mutants"] if m.get("status") == "valid"]
    print(f"manifests updated: armA {sum(1 for m in mana if m['witnessSet'])}/{len(mana)} "
          f"killed; armB {manb['adequacyGate']['killed']}/{len(valid_b)} killed")


def _sha256(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _stamp(m, ws, added, stamp):
    m["witnessSet"] = sorted(ws)
    m["witnessCount"] = len(ws)
    m["notAdequate"] = not ws
    adq = dict(stamp)
    if ws:
        adq["disposition"] = "killed-by-gold"
        adq["killingRowsAddedAtThisGate"] = sorted(set(ws) & added)
    else:
        cls, mech = DROPS[m["id"]]
        adq["disposition"] = "dropped"
        adq["dropMechanismClass"] = cls
        adq["dropMechanism"] = mech
        adq["searchResult"] = ("no cell of the dense derived space distinguishes this mutant "
                               "from its reference on the scored surface (X1 cells included)")
    m["adequacy"] = adq



def update_registry():
    """Recompute arm A's REGISTRY.json aggregates from the pinned engine over the new gold:
    per-class empty-witness counts, the witness-cell census (what the mutant says at each
    killing row) and the conflict-only list (mutants killed only through the engine's
    structural conflict detection), which SS4 requires reported with and without."""
    gold = json.load(open(os.path.join(GOLD, "gold.json")))["rows"]
    mana = json.load(open(os.path.join(HERE, "refA", "MANIFEST.json")))
    reg = json.load(open(os.path.join(HERE, "refA", "REGISTRY.json")))
    want = {r["id"]: (("outcome", r["expect"]["disposition"], ())
                      if r["expect"]["disposition"] != "unresolved"
                      else ("unresolved", None, tuple(sorted(r["expect"]["reasons"]))))
            for r in gold}
    args = [(m["id"], os.path.join(HERE, "refA", m["id"] + ".json"), m["witnessSet"])
            for m in mana]
    with Pool(int(os.environ.get("ADQ_JOBS", "12"))) as pool:
        cells = dict(pool.starmap(_census_a, [(i, p, ws, gold, want) for i, p, ws in args]))
    census, conflict_only = {}, []
    for m in mana:
        vals = cells[m["id"]]
        for v in vals.values():
            census[v] = census.get(v, 0) + 1
        if vals and all(v == "unresolved:conflict" for v in vals.values()):
            conflict_only.append(m["id"])
    reg["goldRows"] = len(gold)
    reg["witnessCellCensus"] = dict(sorted(census.items(), key=lambda kv: -kv[1]))
    reg["conflictOnlyMutants"] = sorted(conflict_only)
    empty = [m for m in mana if m["notAdequate"]]
    reg["totals"]["emptyWitness"] = len(empty)
    for cls, blk in reg["classCounts"].items():
        blk["emptyWitness"] = len([m for m in empty if m["class"] == cls])
    reg["adequacyGate"] = {
        "gate": "adequacy (PREREGISTRATION SS4), 2026-08-15",
        "goldVersion": json.load(open(os.path.join(GOLD, "gold.json")))["goldVersion"],
        "killed": len(mana) - len(empty), "dropped": len(empty),
        "dropMechanismClasses": sorted({DROPS[m["id"]][0] for m in empty}),
        "note": ("witness sets recomputed on the pinned engine over gold 0.1-draft; every "
                 "drop carries its mechanism in MANIFEST.json and mutants/ADEQUACY.md")}
    json.dump(reg, open(os.path.join(HERE, "refA", "REGISTRY.json"), "w"),
              indent=1, sort_keys=True)
    print(f"registry: {len(mana) - len(empty)} killed, {len(empty)} dropped, "
          f"conflict-only {len(conflict_only)}")


def _census_a(mid, path, ws, gold, want):
    rows = {r["id"]: r for r in gold}
    out = {}
    for rid in ws or []:
        k, o, rs = scored(jpack_eval(path, rows[rid]["inputs"]))
        out[rid] = f"outcome:{o}" if k == "outcome" else f"{k}:{'+'.join(rs)}"
    return mid, out



def _killcensus_a(mid):
    """Every distinct scored output the mutant produces at a non-X1 cell where it differs
    from the reference. If that set is {unresolved:conflict}, NO gold row can kill this
    mutant except through the engine's structural conflict detection -- the SS4 quantity that
    must be reported with and without engine-supplied kills."""
    pack = json.load(open(os.path.join(HERE, "refA", mid + ".json")))
    seen = {}
    for k, c in enumerate(CELLS):
        got = scored(sim_a(pack, c))
        if got == REFOUT[k] or in_x1(c):
            continue
        key = f"outcome:{got[1]}" if got[0] == "outcome" else f"{got[0]}:{'+'.join(got[2])}"
        seen[key] = seen.get(key, 0) + 1
    return {"id": mid, "mutantOutputsAtWitnessCells": dict(sorted(seen.items())),
            "conflictOnlyByConstruction": list(seen) == ["unresolved:conflict"]}


def killcensus():
    report = json.load(open(os.path.join(HERE, "adequacy_search.json")))
    ids = [k for k, v in sorted(report["armA"].items()) if v["diffCellsOutsideX1"]]
    _init_a()
    with Pool(int(os.environ.get("ADQ_JOBS", "12")), initializer=_init_a) as pool:
        res = pool.map(_killcensus_a, ids)
    json.dump(res, open(os.path.join(HERE, "adequacy_killcensus.json"), "w"),
              indent=1, sort_keys=True)
    co = [r["id"] for r in res if r["conflictOnlyByConstruction"]]
    print(f"killcensus: {len(res)} newly killable arm-A mutants; "
          f"{len(co)} distinguishable ONLY as unresolved{{conflict}} anywhere: {co}")



def _sim2(mid):
    """Re-run one arm-A no-witness verdict with the INDEPENDENT SS7/SS8 transcription written
    for the reference build (reference/refA/jps_sim.py, a different author-side artifact from
    this file's transcription). Agreement of two independently written transcriptions, each
    validated against the pinned binary, is what a negative claim over 419,904 cells can be
    given short of 419,904 process launches."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "jps_sim", os.path.join(REF, "refA", "jps_sim.py"))
    sim2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim2)
    tri = {"present": sim2.T, "absent": sim2.F, None: sim2.U}
    pack = json.load(open(os.path.join(HERE, "refA", mid + ".json")))
    refpack = json.load(open(os.path.join(REF, "refA", "pack.json")))
    diffs = 0
    for c in CELLS:
        facts, _ = jps_project(c)
        ev = {"financial-evidence": tri[c["finEvidence"]],
              "insurance-certificate": tri[c["insurance"]]}
        if sim2.evaluate_cell(pack, facts, ev) != sim2.evaluate_cell(refpack, facts, ev):
            diffs += 1
    return {"id": mid, "differingCellsSecondTranscription": diffs}


def crosscheck():
    report = json.load(open(os.path.join(HERE, "adequacy_search.json")))
    ids = [k for k, v in sorted(report["armA"].items()) if not v["diffCellsOutsideX1"]]
    _init_a()
    with Pool(int(os.environ.get("ADQ_JOBS", "12")), initializer=_init_a) as pool:
        res = pool.map(_sim2, ids)
    bad = [r for r in res if r["differingCellsSecondTranscription"]]
    json.dump(res, open(os.path.join(HERE, "adequacy_crosscheck.json"), "w"),
              indent=1, sort_keys=True)
    print(f"crosscheck: {len(res)} arm-A drops re-run with reference/refA/jps_sim.py over "
          f"{len(CELLS)} cells each; {len(bad)} disagree with the drop verdict")
    for r in bad:
        print("  DISAGREES", r)
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--drops", action="store_true")
    ap.add_argument("--mechanisms", action="store_true")
    ap.add_argument("--manifests", action="store_true")
    ap.add_argument("--registry", action="store_true")
    ap.add_argument("--killcensus", action="store_true")
    ap.add_argument("--crosscheck", action="store_true")
    ap.add_argument("--witnesses", action="store_true")
    a = ap.parse_args()
    rc = 0
    if a.validate:
        rc |= validate()
    if a.search:
        report = {"space": {"cells": 12 * 12 * 4 * 3 * 3 * 3 * 3 * 3 * 3,
                            "risk": RISK, "spend": SPEND, "country": COUNTRY,
                            "sanctions": SANCTIONS},
                  "armA": search_a(), "armB": search_b()}
        json.dump(report, open(os.path.join(HERE, "adequacy_search.json"), "w"),
                  indent=1, sort_keys=True)
        na = sum(1 for r in report["armA"].values() if r["diffCellsOutsideX1"])
        nb = sum(1 for r in report["armB"].values() if r["diffCellsOutsideX1"])
        print(f"search: armA {na}/{len(report['armA'])} distinguishable outside X1; "
              f"armB {nb}/{len(report['armB'])}")
    if a.confirm:
        report = json.load(open(os.path.join(HERE, "adequacy_search.json")))
        c = confirm(report)
        json.dump(c, open(os.path.join(HERE, "adequacy_confirm.json"), "w"),
                  indent=1, sort_keys=True)
        bad = [x for x in c if not (x["distinguished"] and x["simAgreesReference"]
                                    and x["simAgreesMutant"])]
        print(f"confirm: {len(c)} witnesses re-run on the pinned engine, {len(bad)} unconfirmed")
        for x in bad[:10]:
            print("  UNCONFIRMED", x)
        rc |= 1 if bad else 0
    if a.drops:
        rc |= drops_a()
    if a.mechanisms:
        rc |= mechanisms()
    if a.witnesses:
        witness_sets()
    if a.manifests:
        update_manifests()
    if a.registry:
        update_registry()
    if a.killcensus:
        killcensus()
    if a.crosscheck:
        rc |= crosscheck()
    sys.exit(rc)


if __name__ == "__main__":
    main()
