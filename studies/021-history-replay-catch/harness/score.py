"""Aggregate the replay cells and adjudicate the registered expectations.

Reads every `cells.json` under an attempt root (one per policy), and writes:

- `CATCH-RATES.json` -- per policy, defect class, stratum and n: cells,
  caught, the catch rate, and its exact 95% Clopper-Pearson interval;
- `SIGNATURE.json` -- per policy, class and stratum: caught cells, how many
  carried the line-moved signature, and the same interval;
- `ADJUDICATION.json` -- every registered cell of harness/MATRIX.json against
  what was observed: `holds`, or `diverges` with the observed value. R1 is
  `holds` iff no registered cell diverges and the pipeline was valid; the
  decision is written last, after every file above.

The scorer refuses an attempt root that already holds an ADJUDICATION.json,
refuses a runtime whose digest is not the pinned one, and labels the attempt
REGISTERED only when every freeze pin in PINS.json is non-null and matches.

Run: python harness/score.py --attempt-root DIR [--include-holdout]
"""
import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import jp

STUDY = Path(__file__).resolve().parent.parent


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval, by bisection on the regularized incomplete beta."""
    if n == 0:
        return None
    def beta_cdf(x, a, b):
        # continued fraction for I_x(a,b) (Numerical Recipes betacf), adequate for n <= 10^4
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
        def betacf(a, b, x):
            maxit, eps, fpmin = 400, 3e-14, 1e-300
            qab, qap, qam = a + b, a + 1, a - 1
            c, d = 1.0, 1 - qab * x / qap
            d = 1 / (d if abs(d) > fpmin else fpmin); h = d
            for m in range(1, maxit + 1):
                m2 = 2 * m
                aa = m * (b - m) * x / ((qam + m2) * (a + m2))
                d = 1 + aa * d; d = 1 / (d if abs(d) > fpmin else fpmin)
                c = 1 + aa / (c if abs(c) > fpmin else fpmin); h *= d * c
                aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
                d = 1 + aa * d; d = 1 / (d if abs(d) > fpmin else fpmin)
                c = 1 + aa / (c if abs(c) > fpmin else fpmin); dl = d * c; h *= dl
                if abs(dl - 1) < eps: break
            return h
        if x < (a + 1) / (a + b + 2):
            return math.exp(lbeta) * betacf(a, b, x) / a
        return 1 - math.exp(lbeta) * betacf(b, a, 1 - x) / b
    def solve(target, a, b):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if beta_cdf(mid, a, b) < target: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(alpha / 2, k, n - k + 1)
    upper = 1.0 if k == n else solve(1 - alpha / 2, k + 1, n - k)
    return [round(lower, 4), round(upper, 4)]


def stratum_of(ledger):
    if ledger == "literal":
        return "literal", None
    _, n, _ = ledger.split("-")
    return "random", int(n)


def aggregate(cells_by_policy):
    rates, sigs = [], []
    for policy, cells in sorted(cells_by_policy.items()):
        groups = defaultdict(list)
        for c in cells:
            stratum, n = stratum_of(c["ledger"])
            groups[(c["class"], stratum, n)].append(c)
        for (cls, stratum, n), cs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or 0)):
            caught = sum(c["caught"] for c in cs)
            rates.append({"policy": policy, "class": cls, "stratum": stratum, "n": n, "cells": len(cs), "caught": caught,
                          "rate": round(caught / len(cs), 4), "ci95": clopper_pearson(caught, len(cs))})
            withsig = [c for c in cs if c["caught"] and c["signature"].get("applicable")]
            moved = sum(1 for c in withsig if c["signature"].get("lineMoved"))
            if withsig:
                sigs.append({"policy": policy, "class": cls, "stratum": stratum, "n": n, "caughtWithThreshold": len(withsig),
                             "lineMoved": moved, "rate": round(moved / len(withsig), 4), "ci95": clopper_pearson(moved, len(withsig))})
    return rates, sigs


def observe(cells_by_policy, cell):
    """The observed value of one registered cell's endpoint."""
    cs = [c for c in cells_by_policy.get(cell["policy"], []) if c["defect"] == cell["defect"]]
    stratum, n = cell["stratum"], cell.get("n")
    cs = [c for c in cs if stratum_of(c["ledger"]) == (stratum, n)]
    if not cs:
        return {"observed": None, "cells": 0}
    if cell["endpoint"] == "caught":
        return {"observed": round(sum(c["caught"] for c in cs) / len(cs), 4), "cells": len(cs)}
    if cell["endpoint"] == "lineMovedWhenCaught":
        caught = [c for c in cs if c["caught"]]
        if not caught:
            return {"observed": None, "cells": 0, "note": "no caught replicate"}
        return {"observed": round(sum(1 for c in caught if c["signature"].get("lineMoved")) / len(caught), 4), "cells": len(caught)}
    raise ValueError("unknown endpoint " + cell["endpoint"])


def adjudicate(matrix, cells_by_policy):
    rows = []
    for cell in matrix["cells"]:
        got = observe(cells_by_policy, cell)
        expected = cell["expected"]
        holds = None
        if got["observed"] is not None:
            lo, hi = expected["min"], expected["max"]
            holds = lo <= got["observed"] <= hi
        elif expected.get("allowsNoCaught"):
            holds = True
        rows.append({"id": cell["id"], "role": cell.get("role", "endpoint"), "expected": expected, **got,
                     "verdict": "holds" if holds else ("diverges" if holds is False else "unobserved")})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt-root", required=True)
    ap.add_argument("--include-holdout", action="store_true")
    ap.add_argument("--pilot", action="store_true", help="label the attempt PILOT regardless of pins")
    args = ap.parse_args()
    root = Path(args.attempt_root)
    if (root / "ADJUDICATION.json").exists():
        sys.exit("refusing: %s already holds an adjudication" % root)
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text())
    digest = jp.binary_digest()
    if pins["jpack"]["sha256"] and pins["jpack"]["sha256"] != digest:
        sys.exit("refusing: the runtime's digest %s is not the pinned %s" % (digest, pins["jpack"]["sha256"]))
    registered = (not args.pilot) and all(pins["freeze"].get(k) for k in ("preregistration", "matrix", "studyManifest"))
    cells_by_policy = {}
    for f in sorted(root.glob("*/cells.json")):
        cells_by_policy[f.parent.name] = json.loads(f.read_text())
    rates, sigs = aggregate(cells_by_policy)
    (root / "CATCH-RATES.json").write_text(json.dumps(rates, indent=1))
    (root / "SIGNATURE.json").write_text(json.dumps(sigs, indent=1))
    matrices = [json.loads((STUDY / "harness" / "MATRIX.json").read_text())]
    if args.include_holdout and (STUDY / "harness" / "MATRIX-HOLDOUT.json").exists():
        matrices.append(json.loads((STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text()))
    adjudication = []
    for m in matrices:
        adjudication += adjudicate(m, cells_by_policy)
    diverging = [r for r in adjudication if r["verdict"] == "diverges"]
    gates = [r for r in adjudication if r["role"] == "control-gate" and r["verdict"] != "holds"]
    decision = "pipeline-invalid" if not cells_by_policy else ("control-gate-failed" if gates else ("R1 holds" if not diverging else "R1 falsified"))
    (root / "ADJUDICATION.json").write_text(json.dumps({"label": "REGISTERED" if registered else "PILOT", "jpackDigest": digest,
                                                          "decision": decision, "cells": adjudication}, indent=1))
    print("%s: %s (%d registered cells, %d diverge)" % ("REGISTERED" if registered else "PILOT", decision, len(adjudication), len(diverging)))


if __name__ == "__main__":
    main()
