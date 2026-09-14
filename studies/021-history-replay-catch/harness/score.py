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
files' bytes where non-null; the manifest against the tree; the attempt
marker parsed and matched -- its label, runtime digest, pins digest, seeds,
sizes and policies -- and, for a registered adjudication, every pin non-null,
the holdout included and non-empty. The records are then loaded only as a
complete, unique, internally consistent set bound to their inputs and to the
attempt (evidence()); anything short of that is pipeline-invalid, never
"holds". Missing observations are pipeline-invalid.

Run: python harness/score.py --attempt-root DIR [--include-holdout] [--pilot]
"""
import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import attempt
import build_ledgers
import jp
import plant

STUDY = Path(__file__).resolve().parent.parent
POLICIES = attempt.POLICIES


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
            exact = clopper_pearson(caught, len(cs)) if stratum == "random" else None
            rates.append({"policy": policy, "class": cls, "defect": defect, "site": cs[0]["site"], "stratum": stratum, "n": n, "cells": len(cs),
                          "caught": caught, "rate": round(caught / len(cs), 4), "ci95exact": exact,
                          **({} if stratum == "random" else {"note": "one deterministic ledger: a count, not a sample; no interval"})})
            caught_cells = [c for c in cs if c["caught"]]
            moved = sum(1 for c in caught_cells if c["signature"].get("lineMoved"))
            no_threshold = sum(1 for c in caught_cells if not c["signature"].get("applicable"))
            sigs.append({"policy": policy, "class": cls, "defect": defect, "stratum": stratum, "n": n, "caught": len(caught_cells),
                         "lineMoved": moved, "noThreshold": no_threshold, "rate": (round(moved / len(caught_cells), 4) if caught_cells else None),
                         "ci95exact": clopper_pearson(moved, len(caught_cells)) if (caught_cells and stratum == "random") else None})
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
    cs = list({c["ledger"]: c for c in cs if stratum_of(c["ledger"])[:2] == (stratum, n)}.values())
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


def canonical_instances(policy):
    """The planter's instance set for a vendored policy, in its enumeration order."""
    pack = json.loads((STUDY / "fixtures" / "policies" / (policy + ".pack.json")).read_text())
    return [{"id": "%s-%02d" % (i["class"], k), "class": i["class"], "site": i["site"]} for k, i in enumerate(plant.instances(pack))]


def evidence(root, marker):
    """Load the attempt's records only as a complete, unique, internally consistent set bound to its inputs.

    Every way the records fall short is a failure: the four policies exactly; each policy's
    defect index equal to the planter's canonical set with no instance dropped; every
    registered ledger present with its row count and no unregistered one; the gate record
    covering every ledger once, clean, bound to the ledger's bytes and the policy pack's; the
    cells exactly the Cartesian product of valid instances and ledgers, each bound to its
    ledger's and its defect's bytes, each with a verdict, a row count equal to the ledger's, a
    mismatch count within it, and caught equal to mismatched > 0; and every record stamped
    with the attempt's id.
    """
    failures = []
    cells_by_policy = {}
    if not marker:
        return ["no attempt marker: the records belong to no attempt"], {}
    seeds = range(marker["seeds"][0], marker["seeds"][1] + 1)
    expected_ledgers = ["literal"] + ["random-%d-%d" % (n, s) for n in marker["sizes"] for s in seeds]
    for policy in POLICIES:
        pdir = Path(root) / policy
        canon = canonical_instances(policy)
        index_path = pdir / "defects" / "INDEX.json"
        if not index_path.exists():
            failures.append("%s: no defect index" % policy)
            continue
        index = json.loads(index_path.read_text())
        if index.get("attemptId") != marker["attemptId"]:
            failures.append("%s: the defect index is not this attempt's" % policy)
        recorded = [(d.get("id"), d.get("class"), d.get("site"), d.get("valid")) for d in index.get("instances", [])]
        if recorded != [(c["id"], c["class"], c["site"], True) for c in canon]:
            failures.append("%s: the defect index is not the planter's canonical set with every instance valid" % policy)
        valid_ids = [c["id"] for c in canon]
        ledger_digest, ledger_rows = {}, {}
        for name in expected_ledgers:
            path = pdir / (name + ".matrix.json")
            if not path.exists():
                failures.append("%s: ledger %s is missing" % (policy, name))
                continue
            rows = len(json.loads(path.read_text()).get("cases", []))
            if name != "literal" and rows != int(name.split("-")[1]):
                failures.append("%s: ledger %s holds %d rows" % (policy, name, rows))
            if name == "literal" and rows == 0:
                failures.append("%s: the literal ledger is empty" % policy)
            ledger_digest[name] = attempt.sha256_file(path)
            ledger_rows[name] = rows
        present = {p.stem.replace(".matrix", "") for p in pdir.glob("*.matrix.json")}
        if present - set(expected_ledgers):
            failures.append("%s: unregistered ledgers present: %s" % (policy, ", ".join(sorted(present - set(expected_ledgers)))))
        gate_path = pdir / "cells.gate.json"
        if not gate_path.exists():
            failures.append("%s: no gate record (the unplanted replay did not run)" % policy)
        else:
            gate = json.loads(gate_path.read_text())
            if gate.get("attemptId") != marker["attemptId"]:
                failures.append("%s: the gate record is not this attempt's" % policy)
            if gate.get("policyPackSha256") != attempt.sha256_file(STUDY / "fixtures" / "policies" / (policy + ".pack.json")):
                failures.append("%s: the gate record was made with another policy pack" % policy)
            names = [g.get("ledger") for g in gate.get("ledgers", [])]
            if sorted(names) != sorted(expected_ledgers) or len(names) != len(set(names)):
                failures.append("%s: the gate record does not cover every ledger exactly once" % policy)
            for g in gate.get("ledgers", []):
                if g.get("status") != "passed" or g.get("mismatched") != 0 or g.get("rows") != ledger_rows.get(g.get("ledger")) \
                        or g.get("ledgerSha256") != ledger_digest.get(g.get("ledger")):
                    failures.append("%s: the unplanted pack did not replay %s clean and bound (%s)" % (policy, g.get("ledger"), g.get("status")))
        cells_path = pdir / "cells.json"
        if not cells_path.exists():
            failures.append("%s: no cells" % policy)
            continue
        doc = json.loads(cells_path.read_text())
        if doc.get("attemptId") != marker["attemptId"]:
            failures.append("%s: the cells are not this attempt's" % policy)
        cells = doc.get("cells", [])
        pairs = [(c.get("defect"), c.get("ledger")) for c in cells]
        wanted = {(d, l) for d in valid_ids for l in expected_ledgers}
        if len(pairs) != len(set(pairs)):
            failures.append("%s: a (defect, ledger) pair is recorded more than once" % policy)
        if set(pairs) != wanted:
            failures.append("%s: the cells are not exactly every valid instance against every ledger (%d of %d)" % (policy, len(set(pairs) & wanted), len(wanted)))
        site_of = {c["id"]: (c["class"], c["site"]) for c in canon}
        for c in cells:
            rows = ledger_rows.get(c.get("ledger"))
            defect_path = pdir / "defects" / (str(c.get("defect")) + ".pack.json")
            ok = (c.get("status") in ("passed", "mismatch") and isinstance(c.get("mismatched"), int) and rows is not None
                  and c.get("rows") == rows and 0 <= c["mismatched"] <= rows and c.get("caught") == (c["mismatched"] > 0)
                  and isinstance(c.get("signature"), dict) and isinstance(c["signature"].get("applicable"), bool)
                  and c.get("ledgerSha256") == ledger_digest.get(c.get("ledger"))
                  and defect_path.exists() and c.get("defectSha256") == attempt.sha256_file(defect_path)
                  and site_of.get(c.get("defect")) == (c.get("class"), c.get("site")))
            if not ok:
                failures.append("%s: cell %s x %s is not a complete, bound replay record" % (policy, c.get("defect"), c.get("ledger")))
                break
        cells_by_policy[policy] = cells
    return failures, cells_by_policy


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
    ap.add_argument("--pilot", action="store_true", help="score a PILOT attempt: its marker must say so, and the label is PILOT whatever the pins")
    args = ap.parse_args()
    root = Path(args.attempt_root)
    if (root / "ADJUDICATION.json").exists():
        sys.exit("refusing: %s already holds an adjudication" % root)
    digest = jp.binary_digest()
    pins = attempt.load_pins()
    problems = attempt.pin_problems(pins, digest, require_all=not args.pilot)
    marker = attempt.read_marker(root)
    problems += attempt.marker_problems(marker, digest, attempt.PILOT_LABEL if args.pilot else attempt.REGISTERED_LABEL)
    if problems:
        sys.exit("refusing to adjudicate %s:\n  " % root + "\n  ".join(problems))
    holdout = load_matrix(STUDY / "harness" / "MATRIX-HOLDOUT.json") if args.include_holdout else []
    if args.include_holdout and not holdout:
        sys.exit("refusing: --include-holdout with an empty holdout matrix")
    if not args.pilot and not holdout:
        sys.exit("refusing: a registered adjudication includes the holdout")
    registered = not args.pilot
    gate_failures, cells_by_policy = evidence(root, marker)
    if len(cells_by_policy) != len(POLICIES) or gate_failures:
        decision, rates, sigs, adjudication = ("pipeline-invalid" if len(cells_by_policy) != len(POLICIES) else "control-gate-failed"), [], [], []
        if len(cells_by_policy) == len(POLICIES):
            rates, sigs = aggregate(cells_by_policy)
    else:
        rates, sigs = aggregate(cells_by_policy)
        gate_failures = determinism_check(root)
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
    if rates:
        (root / "CATCH-RATES.json").write_text(json.dumps(rates, indent=1))
        (root / "SIGNATURE.json").write_text(json.dumps(sigs, indent=1))
    (root / "ADJUDICATION.json").write_text(json.dumps({"label": attempt.REGISTERED_LABEL if registered else attempt.PILOT_LABEL, "attemptId": marker["attemptId"],
                                                          "jpackDigest": digest, "jpackVersion": jp.runtime_version(), "holdoutIncluded": bool(holdout),
                                                          "decision": decision, "gateFailures": gate_failures, "cells": adjudication}, indent=1))
    print("%s: %s (%d registered cells, %d diverge, %d gate failures)" % (attempt.REGISTERED_LABEL if registered else attempt.PILOT_LABEL, decision, len(adjudication),
          sum(1 for r in adjudication if r["verdict"] == "diverges"), len(gate_failures)))
    if decision in ("pipeline-invalid", "control-gate-failed"):
        for f in gate_failures[:8]:
            print("  ", f)


if __name__ == "__main__":
    main()
