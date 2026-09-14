"""Aggregate the replay cells, hold the gates, and adjudicate the registered cells.

Reads an attempt root and writes, in this order:

- `CATCH-RATES.json` -- per policy, defect INSTANCE, stratum and n: cells,
  caught, the catch rate and its exact 95% Clopper-Pearson interval (the
  thirty seeded ledgers of one instance at one n are independent draws, so
  the interval is exact for that instance); and per class, pooled over the
  instances of the class, the same counts with a binomial reference interval
  that carries NO nominal coverage claim, since instances share ledgers;
- `SIGNATURE.json` -- per policy, class and stratum: caught cells, how many
  carried the line-moved signature (a caught cell without a threshold counts
  as carrying none), how many had no threshold at all, and the same
  per-instance exact / per-class reference intervals;
- `ADJUDICATION.json` -- the gates, every registered cell against what was
  observed, and the decision, written last.

Enforcement, before any cell is read: the runtime's digest against the pin;
the freeze pins (preregistration, matrix, holdout, manifest) against the
files' bytes where non-null; the manifest against the tree. An attempt is
labelled REGISTERED only when every pin is non-null and matches, the holdout
is included and non-empty, ATTEMPT.json is present, and every policy holds
exactly the registered ledger set (the literal ledger and the reserved seeds
at every n). Missing observations are pipeline-invalid, never "holds".

Run: python harness/score.py --attempt-root DIR [--include-holdout] [--pilot]
"""
import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import build_ledgers
import jp
import make_manifest

STUDY = Path(__file__).resolve().parent.parent
POLICIES = ("data-request-intake-triage", "expense-approval", "sanctions-screening", "vendor-onboarding")


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval, by bisection on the regularized incomplete beta."""
    if n == 0:
        return None

    def beta_cdf(x, a, b):
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)

        def betacf(a, b, x):
            maxit, eps, fpmin = 400, 3e-14, 1e-300
            qab, qap, qam = a + b, a + 1, a - 1
            c, d = 1.0, 1 - qab * x / qap
            d = 1 / (d if abs(d) > fpmin else fpmin)
            h = d
            for m in range(1, maxit + 1):
                m2 = 2 * m
                aa = m * (b - m) * x / ((qam + m2) * (a + m2))
                d = 1 + aa * d
                d = 1 / (d if abs(d) > fpmin else fpmin)
                c = 1 + aa / (c if abs(c) > fpmin else fpmin)
                h *= d * c
                aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
                d = 1 + aa * d
                d = 1 / (d if abs(d) > fpmin else fpmin)
                c = 1 + aa / (c if abs(c) > fpmin else fpmin)
                dl = d * c
                h *= dl
                if abs(dl - 1) < eps:
                    break
            return h
        if x < (a + 1) / (a + b + 2):
            return math.exp(lbeta) * betacf(a, b, x) / a
        return 1 - math.exp(lbeta) * betacf(b, a, 1 - x) / b

    def solve(target, a, b):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if beta_cdf(mid, a, b) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(alpha / 2, k, n - k + 1)
    upper = 1.0 if k == n else solve(1 - alpha / 2, k + 1, n - k)
    return [round(lower, 4), round(upper, 4)]


def stratum_of(ledger):
    if ledger == "literal":
        return "literal", None, None
    _, n, seed = ledger.split("-")
    return "random", int(n), int(seed)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_matrix(path):
    """A matrix file is an object with `cells`, or -- a reviewer's holdout, kept byte-for-byte -- a bare array of cells."""
    doc = json.loads(Path(path).read_text())
    return doc if isinstance(doc, list) else doc.get("cells", [])


def aggregate(cells_by_policy):
    rates, sigs = [], []
    for policy, cells in sorted(cells_by_policy.items()):
        by_instance = defaultdict(list)
        for c in cells:
            stratum, n, _ = stratum_of(c["ledger"])
            by_instance[(c["class"], c["defect"], stratum, n)].append(c)
        by_class = defaultdict(list)
        for (cls, defect, stratum, n), cs in sorted(by_instance.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3] or 0)):
            caught = sum(c["caught"] for c in cs)
            rates.append({"policy": policy, "class": cls, "defect": defect, "site": cs[0]["site"], "stratum": stratum, "n": n, "cells": len(cs),
                          "caught": caught, "rate": round(caught / len(cs), 4), "ci95exact": clopper_pearson(caught, len(cs))})
            caught_cells = [c for c in cs if c["caught"]]
            moved = sum(1 for c in caught_cells if c["signature"].get("lineMoved"))
            no_threshold = sum(1 for c in caught_cells if not c["signature"].get("applicable"))
            sigs.append({"policy": policy, "class": cls, "defect": defect, "stratum": stratum, "n": n, "caught": len(caught_cells),
                         "lineMoved": moved, "noThreshold": no_threshold, "rate": (round(moved / len(caught_cells), 4) if caught_cells else None),
                         "ci95exact": clopper_pearson(moved, len(caught_cells)) if caught_cells else None})
            by_class[(cls, stratum, n)].extend(cs)
        for (cls, stratum, n), cs in sorted(by_class.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or 0)):
            caught = sum(c["caught"] for c in cs)
            caught_cells = [c for c in cs if c["caught"]]
            moved = sum(1 for c in caught_cells if c["signature"].get("lineMoved"))
            rates.append({"policy": policy, "class": cls, "defect": "*", "stratum": stratum, "n": n, "cells": len(cs), "caught": caught,
                          "rate": round(caught / len(cs), 4), "referenceInterval": clopper_pearson(caught, len(cs)),
                          "note": "pooled over the class's instances, which share ledgers: a binomial reference interval with no nominal coverage"})
            sigs.append({"policy": policy, "class": cls, "defect": "*", "stratum": stratum, "n": n, "caught": len(caught_cells), "lineMoved": moved,
                         "noThreshold": sum(1 for c in caught_cells if not c["signature"].get("applicable")),
                         "rate": (round(moved / len(caught_cells), 4) if caught_cells else None),
                         "referenceInterval": clopper_pearson(moved, len(caught_cells)) if caught_cells else None,
                         "note": "pooled over the class's instances: a reference interval with no nominal coverage"})
    return rates, sigs


def observe(cells_by_policy, cell):
    """The observed value of one registered cell's endpoint, or None with the reason."""
    cs = [c for c in cells_by_policy.get(cell["policy"], []) if c["defect"] == cell["defect"]]
    stratum, n = cell["stratum"], cell.get("n")
    cs = [c for c in cs if stratum_of(c["ledger"])[:2] == (stratum, n)]
    expected_count = 1 if stratum == "literal" else 30
    if len(cs) != expected_count:
        return {"observed": None, "cells": len(cs), "note": "expected %d ledgers, found %d" % (expected_count, len(cs))}
    if cell["endpoint"] == "caught":
        return {"observed": round(sum(c["caught"] for c in cs) / len(cs), 4), "cells": len(cs)}
    if cell["endpoint"] == "lineMovedWhenCaught":
        caught = [c for c in cs if c["caught"]]
        if not caught:
            return {"observed": None, "cells": len(cs), "caught": 0, "note": "no caught ledger among the complete set"}
        return {"observed": round(sum(1 for c in caught if c["signature"].get("lineMoved")) / len(caught), 4), "cells": len(caught)}
    raise ValueError("unknown endpoint " + cell["endpoint"])


def adjudicate(cells, cells_by_policy):
    rows = []
    for cell in cells:
        got = observe(cells_by_policy, cell)
        expected = cell["expected"]
        if got["observed"] is not None:
            verdict = "holds" if expected["min"] <= got["observed"] <= expected["max"] else "diverges"
        elif expected.get("allowsNoCaught") and got.get("caught") == 0:
            verdict = "holds"
        else:
            verdict = "unobserved"
        rows.append({"id": cell["id"], "role": cell.get("role", "endpoint"), "expected": expected, **got, "verdict": verdict})
    return rows


def gate_checks(root, cells_by_policy, registered):
    """G1: the unplanted pack mismatches nothing; G2: no instance dropped; the ledger set is complete. Every failure is named."""
    failures = []
    sizes = build_ledgers.SIZES
    seeds = range(build_ledgers.RESERVED_SEEDS[0], build_ledgers.RESERVED_SEEDS[1] + 1)
    for policy in POLICIES:
        if policy not in cells_by_policy:
            failures.append("%s: no cells" % policy)
            continue
        cells = cells_by_policy[policy]
        ledgers = sorted({c["ledger"] for c in cells})
        if registered:
            wanted = ["literal"] + ["random-%d-%d" % (n, s) for n in sizes for s in seeds]
            if sorted(wanted) != ledgers:
                failures.append("%s: the ledger set is not the registered one (%d found, %d wanted)" % (policy, len(ledgers), len(wanted)))
        index_path = root / policy / "defects" / "INDEX.json"
        if not index_path.exists():
            failures.append("%s: no defect index" % policy)
        else:
            index = json.loads(index_path.read_text())
            dropped = [d["id"] for d in index if not d["valid"]]
            if dropped:
                failures.append("%s: instances dropped as invalid: %s" % (policy, ", ".join(dropped)))
            valid = {d["id"] for d in index if d["valid"]}
            seen = {c["defect"] for c in cells}
            if valid != seen:
                failures.append("%s: cells cover %d instances of %d" % (policy, len(seen), len(valid)))
            if len(cells) != len(valid) * len(ledgers):
                failures.append("%s: %d cells for %d instances x %d ledgers" % (policy, len(cells), len(valid), len(ledgers)))
        gate_path = root / policy / "cells.gate.json"
        if not gate_path.exists():
            failures.append("%s: no gate record (the unplanted replay did not run)" % policy)
        else:
            gate = json.loads(gate_path.read_text())
            if sorted(g["ledger"] for g in gate) != ledgers:
                failures.append("%s: the gate record does not cover every ledger" % policy)
            for g in gate:
                if g.get("status") not in ("passed", "mismatch") or g.get("mismatched"):
                    failures.append("%s: the unplanted pack did not replay %s clean (%s, %s mismatched)" % (policy, g["ledger"], g.get("status"), g.get("mismatched")))
    return failures


def determinism_check(root):
    """G3: rebuild one random ledger per policy under the pinned runtime and compare bytes."""
    failures = []
    import tempfile
    for policy in POLICIES:
        candidates = sorted((root / policy).glob("random-5-*.matrix.json")) if (root / policy).exists() else []
        if not candidates:
            failures.append("%s: no random ledger to rebuild" % policy)
            continue
        path = candidates[0]
        _, n, seed = stratum_of(path.stem.replace(".matrix", ""))
        pack, base = build_ledgers.load_policy(policy)
        with tempfile.TemporaryDirectory() as tmp:
            project = jp.project(tmp, policy, pack)
            rebuilt, _ = build_ledgers.random_ledger(policy, pack, base, project, n, seed)
        if json.dumps(rebuilt, indent=1) != path.read_text():
            failures.append("%s: %s rebuilt differently" % (policy, path.name))
    return failures


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
    files = {"preregistration": "PREREGISTRATION.md", "matrix": "harness/MATRIX.json", "matrixHoldout": "harness/MATRIX-HOLDOUT.json",
             "studyManifest": "harness/STUDY-MANIFEST.sha256"}
    for key, relative in files.items():
        pinned = pins["freeze"].get(key)
        if pinned and pinned != sha256_file(STUDY / relative):
            sys.exit("refusing: %s does not match its freeze pin" % relative)
    if (STUDY / "harness" / "STUDY-MANIFEST.sha256").read_text() != make_manifest.render():
        sys.exit("refusing: harness/STUDY-MANIFEST.sha256 does not match the tree")
    holdout = load_matrix(STUDY / "harness" / "MATRIX-HOLDOUT.json") if args.include_holdout else []
    if args.include_holdout and not holdout:
        sys.exit("refusing: --include-holdout with an empty holdout matrix")
    all_pinned = bool(pins["jpack"]["sha256"]) and all(pins["freeze"].get(k) for k in files)
    registered = (not args.pilot) and all_pinned and args.include_holdout and (root / "ATTEMPT.json").exists()
    cells_by_policy = {}
    for f in sorted(root.glob("*/cells.json")):
        cells_by_policy[f.parent.name] = json.loads(f.read_text())
    if not cells_by_policy:
        decision, rates, sigs, adjudication, gate_failures = "pipeline-invalid", [], [], [], ["no cells under the attempt root"]
    else:
        rates, sigs = aggregate(cells_by_policy)
        (root / "CATCH-RATES.json").write_text(json.dumps(rates, indent=1))
        (root / "SIGNATURE.json").write_text(json.dumps(sigs, indent=1))
        gate_failures = gate_checks(root, cells_by_policy, registered) + determinism_check(root)
        adjudication = adjudicate(load_matrix(STUDY / "harness" / "MATRIX.json") + holdout, cells_by_policy)
        unobserved = [r["id"] for r in adjudication if r["verdict"] == "unobserved"]
        diverging = [r for r in adjudication if r["verdict"] == "diverges"]
        if unobserved:
            decision = "pipeline-invalid"
            gate_failures = gate_failures + ["unobserved registered cells: %d (first: %s)" % (len(unobserved), unobserved[0])]
        elif gate_failures:
            decision = "control-gate-failed"
        else:
            decision = "R1 holds" if not diverging else "R1 falsified"
    (root / "ADJUDICATION.json").write_text(json.dumps({"label": "REGISTERED" if registered else "PILOT", "jpackDigest": digest,
                                                          "jpackVersion": jp.runtime_version(), "holdoutIncluded": bool(holdout),
                                                          "decision": decision, "gateFailures": gate_failures, "cells": adjudication}, indent=1))
    print("%s: %s (%d registered cells, %d diverge, %d gate failures)" % ("REGISTERED" if registered else "PILOT", decision, len(adjudication),
          sum(1 for r in adjudication if r["verdict"] == "diverges"), len(gate_failures)))
    if decision in ("pipeline-invalid", "control-gate-failed"):
        for f in gate_failures[:8]:
            print("  ", f)


if __name__ == "__main__":
    main()
