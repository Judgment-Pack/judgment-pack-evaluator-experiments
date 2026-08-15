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

# (2) X1 exclusion: newVendor=yes AND 40<=risk<70 AND (LOW with spend unreadable
#     OR country unreadable with spend <= 100000.00)
for r in rows:
    i = r["inputs"]
    if i["newVendor"] == "yes" and i["risk"] is not None and 40 <= int(i["risk"]) < 70:
        low_unread = i["country"] == "LOW" and i["spend"] is None
        cn_small = (i["country"] is None and i["spend"] is not None
                    and Decimal(i["spend"]) <= Decimal("100000.00"))
        if low_unread or cn_small:
            errors.append(f"{r['id']}: row is inside the registered X1 exclusion")

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

print(f"{len(rows)} rows; {len(errors)} failures ({floor_fail} floor-gate)")
for e in errors:
    print(" *", e)
sys.exit(1 if errors else 0)
