#!/usr/bin/env python3
"""Study 019 gold checker (V7, design-time draft).

Asserts over gold.json: (1) structure — unique ids, valid dispositions, valid sorted reason
tokens, reasons empty iff outcome; (2) the registered X1 exclusion; (3) clause coverage —
every clause cited by at least one row; (4) boundary witnesses — every numeric literal is
exercised at the literal and at an adjacent value; (5) the floor gate — both pinned engines
(jpack 0.17.0 reference pack, OPA 1.19.0 reference policy) reproduce every row's
expectation exactly. Exit nonzero on any failure.
"""
import json, os, subprocess, sys, tempfile
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference")
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"
JPACK = os.environ.get("JPACK_BIN", SCRATCH + "/pins/jpack/jpack")
OPA = os.environ.get("OPA_BIN", SCRATCH + "/pins/opa/opa_linux_amd64_static")
CAPS = os.environ.get("OPA_CAPS", SCRATCH + "/pins/opa/caps-filtered.json")

OUTCOMES = {"approve", "review", "enhanced-review", "reject"}
REASONS = {"missing-required-evidence", "unknown", "no-match", "exception-escalation"}
CLAUSES = {"P1", "D1", "D2", "D3", "D4", "D5", "D6a", "D6b", "D6c", "D7", "D8",
           "O1", "O2", "O3", "U1"}

gold = json.load(open(os.path.join(HERE, "gold.json")))
rows = gold["rows"]
errors = []

# (1) structure
ids = [r["id"] for r in rows]
if len(ids) != len(set(ids)):
    errors.append("duplicate row ids")
for r in rows:
    e = r["expect"]
    if e["disposition"] in OUTCOMES:
        if e["reasons"]:
            errors.append(f"{r['id']}: outcome with reasons")
    elif e["disposition"] == "unresolved":
        if not e["reasons"] or not set(e["reasons"]) <= REASONS:
            errors.append(f"{r['id']}: bad reason set {e['reasons']}")
        if e["reasons"] != sorted(e["reasons"]):
            errors.append(f"{r['id']}: reasons not sorted")
    else:
        errors.append(f"{r['id']}: bad disposition {e['disposition']}")
    if not set(r["cite"]) <= CLAUSES or not r["cite"]:
        errors.append(f"{r['id']}: bad cite {r['cite']}")

# (2) registered exclusion classes: THE SET IS EMPTY. X1 was retired on 2026-08-18
#     (round-1 finding R1-2; reference/refA/PACK-CHANGE-001.md) because the repaired arm-A
#     reference answers the prose over the whole space, so no gold row is forbidden any
#     more. The machinery is kept with an empty registry: adding a class back is a data
#     edit with a written reason, and until one exists this loop excludes nothing.
#     The retired predicate is kept below as a NON-GATING census so that "gold now covers
#     the region the retired class used to forbid" is measured rather than asserted.
REGISTERED_EXCLUSIONS = {}    # name -> predicate(inputs) -> bool

def retired_x1(i):
    if i["newVendor"] != "yes" or i["risk"] is None or not 40 <= int(i["risk"]) < 70:
        return False
    return ((i["country"] == "LOW" and i["spend"] is None)
            or (i["country"] is None and i["spend"] is not None
                and Decimal(i["spend"]) <= Decimal("100000.00")))

for r in rows:
    for name, predicate in REGISTERED_EXCLUSIONS.items():
        if predicate(r["inputs"]):
            errors.append(f"{r['id']}: row is inside the registered exclusion {name}")
retired_x1_rows = [r["id"] for r in rows if retired_x1(r["inputs"])]
if not retired_x1_rows:
    errors.append("no gold row covers the region the retired X1 class used to forbid; "
                  "the repair (reference/refA/PACK-CHANGE-001.md) is unwitnessed")

# (3) clause coverage
cited = {c for r in rows for c in r["cite"]}
for missing in sorted(CLAUSES - cited):
    errors.append(f"clause never cited: {missing}")

# (4) boundary witnesses
def has(pred):
    return any(pred(r["inputs"]) for r in rows)
for lit, adj in [("40", "39"), ("70", "69"), ("90", "89")]:
    if not has(lambda i, v=lit: i["risk"] == v):
        errors.append(f"no row with risk at literal {lit}")
    if not has(lambda i, v=adj: i["risk"] == v):
        errors.append(f"no row with risk adjacent to {lit} ({adj})")
for lit in ["100000.00", "500000.00", "2000000.00"]:
    up = str(Decimal(lit) + Decimal("0.01"))
    if not has(lambda i, v=lit: i["spend"] == v):
        errors.append(f"no row with spend at literal {lit}")
    if not has(lambda i, v=up: i["spend"] == v):
        errors.append(f"no row with spend adjacent to {lit} ({up})")

# (5) floor gate: both engines reproduce every expectation
def jpack_eval(i):
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
    with tempfile.TemporaryDirectory(dir=SCRATCH) as td:
        f, e = os.path.join(td, "f.json"), os.path.join(td, "e.json")
        json.dump({"vendor": vendor}, open(f, "w")); json.dump(ev, open(e, "w"))
        p = subprocess.run([JPACK, "experimental", "evaluate",
                            os.path.join(REF, "refA", "pack.json"),
                            "--facts", f, "--evidence", e, "--format", "json"],
                           capture_output=True, text=True, cwd=td)
        payload = json.loads(p.stdout)
    d = payload["disposition"]
    if d["kind"] == "outcome":
        return d["outcomeId"], []
    return "unresolved", sorted(d["reasons"])

def opa_eval(i):
    vendor_parts = []
    for src, dst in [("risk", "riskScore"), ("spend", "requestedSpend")]:
        if i[src] is not None:
            vendor_parts.append(f'"{dst}": {i[src]}')  # unquoted: exact JSON number
    for src, dst in [("sanctions", "sanctionsStatus"), ("country", "countryRisk"),
                     ("newVendor", "newVendor"), ("critical", "criticalSupplier"),
                     ("prior", "priorEnforcement")]:
        if i[src] is not None:
            vendor_parts.append(f'"{dst}": "{i[src]}"')
    ev_parts = []
    if i["finEvidence"] is not None:
        ev_parts.append(f'"financial-evidence": "{i["finEvidence"]}"')
    if i["insurance"] is not None:
        ev_parts.append(f'"insurance-certificate": "{i["insurance"]}"')
    doc = '{"vendor": {%s}, "evidence": {%s}}' % (", ".join(vendor_parts), ", ".join(ev_parts))
    with tempfile.TemporaryDirectory(dir=SCRATCH) as td:
        inp = os.path.join(td, "in.json")
        open(inp, "w").write(doc)
        env = dict(os.environ, TZ="UTC")
        p = subprocess.run([OPA, "eval", "--format", "json", "--fail",
                            "--strict-builtin-errors", "--capabilities", CAPS,
                            "--timeout", "10s",
                            "--data", os.path.join(REF, "refB", "policy.rego"),
                            "--input", inp, "data.study.decision"],
                           capture_output=True, text=True, env=env, cwd=td)
        v = json.loads(p.stdout)["result"][0]["expressions"][0]["value"]
    return v["disposition"], sorted(v["reasons"])

floor_fail = 0
for r in rows:
    want = (r["expect"]["disposition"], sorted(r["expect"]["reasons"]))
    for name, fn in [("jpack", jpack_eval), ("opa", opa_eval)]:
        try:
            got = fn(r["inputs"])
        except Exception as ex:
            errors.append(f"{r['id']}: {name} error: {ex}"); floor_fail += 1
            continue
        if got != want:
            errors.append(f"{r['id']}: {name} gives {got}, gold expects {want}")
            floor_fail += 1

print(f"{len(rows)} rows; {len(errors)} failures ({floor_fail} floor-gate); "
      f"registered exclusion classes {len(REGISTERED_EXCLUSIONS)}; "
      f"rows inside the retired X1 region {len(retired_x1_rows)} "
      f"({', '.join(retired_x1_rows)})")
for e in errors:
    print(" *", e)
sys.exit(1 if errors else 0)
