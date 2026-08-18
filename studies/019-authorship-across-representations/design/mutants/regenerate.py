#!/usr/bin/env python3
"""Study 019 — ONE deterministic end-to-end regeneration command per language.

Round-1 finding R1-12, verbatim: *"The advertised deterministic regeneration does not
reproduce the manifests the scorer consumes. Both generators promise byte-identical
manifests but emit their pre-adequacy shapes … Fix: provide one deterministic end-to-end
regeneration command covering generation, adequacy, semantic engine-supplied
classification, and manifest formatting, with a byte-comparison test."*

This is that command. Each generator's own docstring still describes only its own step;
**this file is the reproducibility claim**, and `--check` is the test that keeps the claim
true — it regenerates into a scratch COPY of the design tree and byte-compares every
committed artifact, so running it can never damage the committed corpus.

    regenerate.py --arm A                 # regenerate arm A's corpus in place
    regenerate.py --arm B
    regenerate.py --arm both
    regenerate.py --arm both --check      # regenerate into a copy, byte-compare, report

WHAT IS AND IS NOT IN THE CHAIN
-------------------------------
In:  mutant payload generation, witness sets over the CURRENT gold, manifest + registry
     formatting, and the dense `engineSuppliedKill` classification (R1-11).
Out: the ADEQUACY DISPOSITION STAMP (`adequacy_search.py --manifests/--registry`). It is
     deliberately not in this chain and the chain FAILS CLOSED while it is missing:
     stamping requires a hand-written drop mechanism for every empty-witness mutant, and
     hand-written prose is not something a regeneration command may invent. `--check`
     therefore reports the undispositioned empty-witness mutants as a named, blocking
     condition rather than letting a reader read "reproduces byte-identical" as "the
     adequacy gate is satisfied". The two claims are different and this file keeps them
     apart.

Determinism: every step is RNG-free and timestamp-free; ids are assigned in class order
and, within a class, in reference-file order; JSON is written with a fixed indent and
sorted keys by the step that writes it.

RUNS OF RECORD (the history `REGENERATION-CHECK.json` cannot hold, because each run
overwrites it)
---------------------------------------------------------------------------------
* **2026-08-18, `--arm both --check`: 371/372 byte-identical.** Every arm-A artifact
  (183 mutant payloads + MANIFEST + REGISTRY + adequacy_engine_supplied.json) and every
  arm-B payload (185 `.rego` files) reproduced exactly. **One file did not:**
  `refB/MANIFEST.json`, and three runs produced three different digests.
* **Cause, diagnosed rather than retried:** `m-b-170` is a mutant OPA refuses to evaluate
  (`eval_conflict_error`), and its `dropDetail` recorded OPA's error payload verbatim —
  including the **absolute path** of the policy file. The manifest was therefore
  reproducible only from the directory it was first generated in. That is also a hygiene
  break: this study's artifacts do not carry absolute paths.
* **Fix:** `refB/gen_mutants.py` now scrubs every directory it knows about out of the
  diagnostic before recording it (`<mutant-dir>`, `<work-dir>`, `<mutants-refB>`,
  `<design>`, `<scratch>`), keeping the diagnostic's meaning and dropping its address.
* **2026-08-18, `--arm B --check` after the fix: 186/186 byte-identical.** That is the
  `REGENERATION-CHECK.json` currently committed. A `--arm both --check` re-run (~30-45 min,
  dominated by the dense census) is owed before the freeze so one file carries both arms.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
PY = sys.executable

# design subtrees a regeneration needs: the references and gold are INPUTS, mutants is the
# output. Nothing else is copied for --check.
COPY_TREES = ["reference", "gold", "mutants", "cleanroom"]

# (label, argv, cwd-relative-to-design) per arm, in order.
CHAIN = {
    "A": [
        ("generate arm-A mutants + manifest + registry",
         [PY, "gen_mutants.py", "--jobs", "{jobs}"], "mutants/refA"),
        ("dense engineSuppliedKill census + manifest stamp (R1-11)",
         [PY, "adequacy_search.py", "--engine-supplied-census"], "mutants"),
    ],
    "B": [
        ("generate arm-B mutants + manifest",
         [PY, "gen_mutants.py", "--jobs", "{jobs}"], "mutants/refB"),
        ("engineSuppliedKill stamp for the Rego set (structurally false; R1-11)",
         [PY, "adequacy_search.py", "--rego-engine-supplied-stamp"], "mutants"),
    ],
}

# committed artifacts each arm's chain must reproduce byte-for-byte
def outputs(arm, root):
    m = os.path.join(root, "mutants")
    if arm == "A":
        d = os.path.join(m, "refA")
        return ([os.path.join(d, f) for f in sorted(os.listdir(d))
                 if f.startswith("m-a-") and f.endswith(".json")]
                + [os.path.join(d, "MANIFEST.json"), os.path.join(d, "REGISTRY.json"),
                   os.path.join(m, "adequacy_engine_supplied.json")])
    d = os.path.join(m, "refB")
    return ([os.path.join(d, f) for f in sorted(os.listdir(d))
             if f.startswith("m-b-") and f.endswith(".rego")]
            + [os.path.join(d, "MANIFEST.json")])


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run_chain(arm, root, jobs, env):
    for label, argv, cwd in CHAIN[arm]:
        argv = [a.format(jobs=str(jobs)) for a in argv]
        print("  [%s] %s" % (arm, label), flush=True)
        proc = subprocess.run(argv, cwd=os.path.join(root, cwd), env=env,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout[-4000:] + proc.stderr[-4000:])
            raise SystemExit("step failed (%s): %s" % (arm, label))


def undispositioned(root):
    """Empty-witness mutants with no adequacy disposition: the fail-closed condition."""
    out = {}
    mana = json.load(open(os.path.join(root, "mutants", "refA", "MANIFEST.json")))
    out["A"] = sorted(m["id"] for m in mana
                      if m.get("notAdequate") and "adequacy" not in m)
    manb = json.load(open(os.path.join(root, "mutants", "refB", "MANIFEST.json")))
    out["B"] = sorted(m["id"] for m in manb["mutants"]
                      if m.get("notAdequate") and "adequacy" not in m)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["A", "B", "both"], required=True)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--check", action="store_true",
                    help="regenerate into a scratch copy and byte-compare; changes nothing")
    args = ap.parse_args()
    arms = ["A", "B"] if args.arm == "both" else [args.arm]
    env = {k: v for k, v in os.environ.items() if k != "JPACK_CONFIG"}
    env["ADQ_JOBS"] = str(args.jobs)
    env["TZ"] = "UTC"

    if not args.check:
        for arm in arms:
            run_chain(arm, DESIGN, args.jobs, env)
        u = undispositioned(DESIGN)
        print("regenerated arms %s" % ", ".join(arms))
        for arm in arms:
            print("  arm %s undispositioned empty-witness mutants: %d %s"
                  % (arm, len(u[arm]), " ".join(u[arm]) or "-"))
        return 0

    work = tempfile.mkdtemp(prefix="s019-regen-")
    try:
        root = os.path.join(work, "design")
        os.makedirs(root)
        for tree in COPY_TREES:
            shutil.copytree(os.path.join(DESIGN, tree), os.path.join(root, tree))
        for arm in arms:
            run_chain(arm, root, args.jobs, env)
        rows, bad = [], []
        for arm in arms:
            committed = {os.path.relpath(p, DESIGN): p for p in outputs(arm, DESIGN)}
            regenerated = {os.path.relpath(p, root): p for p in outputs(arm, root)}
            for rel in sorted(set(committed) | set(regenerated)):
                a = sha256(committed[rel]) if rel in committed else None
                b = sha256(regenerated[rel]) if rel in regenerated else None
                rows.append({"arm": arm, "path": rel, "committed": a, "regenerated": b,
                             "identical": a is not None and a == b})
                if a != b:
                    bad.append(rows[-1])
        u = undispositioned(DESIGN)
        report = {
            "record": "end-to-end regeneration byte-comparison (R1-12)",
            "arms": arms,
            "filesCompared": len(rows),
            "identical": sum(1 for r in rows if r["identical"]),
            "differing": bad,
            "byteIdentical": not bad,
            "adequacyStampPresent": {arm: not u[arm] for arm in arms},
            "undispositionedEmptyWitnessMutants": {arm: u[arm] for arm in arms},
            "pass": (not bad) and all(not u[arm] for arm in arms),
            "note": "byteIdentical is the reproducibility claim; `pass` additionally "
                    "requires the adequacy disposition stamp, which this command may not "
                    "invent (see the module docstring).",
        }
        with open(os.path.join(HERE, "REGENERATION-CHECK.json"), "w") as fh:
            json.dump(report, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print("byte-comparison: %d/%d identical" % (report["identical"], report["filesCompared"]))
        for r in bad[:20]:
            print("  DIFFERS %s committed=%s regenerated=%s"
                  % (r["path"], (r["committed"] or "-")[:12], (r["regenerated"] or "-")[:12]))
        for arm in arms:
            print("  arm %s undispositioned empty-witness mutants: %d"
                  % (arm, len(u[arm])))
        print("wrote", os.path.join(HERE, "REGENERATION-CHECK.json"))
        return 0 if report["pass"] else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
