#!/usr/bin/env python3
"""Study 019 E4 SCORING -- NON-CITABLE PILOT run over the calibration-pilot suites.

    THIS SCORES A LABELLED, NON-CITABLE CALIBRATION PILOT.

    Every number this script produces is a pilot rate. None of it may be cited in the
    preregistration or in any result document except as a pilot rate explicitly
    labelled non-citable (BRIEF.md 4.2 step 3). The suites it scores were produced by
    pilot_run.py (design-time driver), not by the registered harness.

What it implements (the REGISTERED E4 scoring rules, applied to pilot inputs)
---------------------------------------------------------------------------

1. PAIRING.  A JPS mutant (arm A / refA) and a Rego mutant (arms B,C / refB) are paired
   iff their witness sets -- the sorted lists of gold row ids that kill them, as recorded
   in each set's MANIFEST -- are IDENTICAL. Pairing is therefore many-to-many: it is a
   grouping by witness-set key, and the full grouping is written out as the pairing table.

   The empty witness set is a key like any other, and by construction every mutant with an
   empty witness set is exactly the set's `notAdequate` mutants (asserted at load). Pairing
   all empty-witness JPS mutants with all empty-witness Rego mutants is degenerate -- it
   pairs on the absence of a discriminating gold row rather than on a shared one -- so that
   group is emitted in the table FLAGGED (`degenerate: true`, `notAdequate: true`) and is
   excluded from the paired kill-rate subsets. Adequate paired subsets are therefore the
   mutants whose non-empty witness set also occurs in the other language.

2. IDENTITY CONTROL, per suite.
   arm A   -- every matrix case is evaluated against the UNMUTATED refA pack with
              `jpack experimental evaluate`, the case's `facts` as the facts document and
              its `evidenceAvailability` (default {}) as the evidence document, in a temp
              cwd holding no jpack.json and with JPACK_CONFIG not inherited (TZ=UTC).
              A case PASSES iff the evaluated disposition agrees with the case's
              `expectedDisposition` in ALIGNMENT SCOPE: kind, outcomeId and the sorted
              reasons list, and nothing else. `handoff`, the payload's `handoffTarget`, and
              the case's `expectedHandoffTarget` are IGNORED (ADR-0025's handoff assertion
              is out of the E4 scored surface). A refused evaluation is a case failure.
              A suite passes identity iff EVERY case passes.
   arms B/C -- `opa test <reference policy> <suite> --capabilities <caps> --timeout 10s`
              under TZ=UTC; identity passes iff exit 0.
   Suites failing identity are EXCLUDED from every kill rate. The per-arm identity-failure
   count is a first-class reported number, not a footnote.

3. KILL, for each identity-passing suite x each own-language mutant.
   arm A   -- every case re-evaluated against the mutant pack; the suite KILLS the mutant
              iff AT LEAST ONE case disagrees in alignment scope (evaluation in case order,
              short-circuited at the first disagreement; the first disagreeing case id is
              recorded). A refusal on a mutant counts as disagreement.
   arms B/C -- `opa test <mutant> <suite> ...`; kills iff exit is NONZERO. The failure
              class is recorded: exit 1 -> `test-failure`, exit 2 -> `error`,
              124 -> `timeout`, anything else -> `other`.
   `notAdequate` mutants (empty witness set -- no gold row kills them) are scored but
   reported SEPARATELY: the headline kill rate is over the adequate own-language mutants.

4. OUTPUT E4-PILOT.json + a printed summary, both labelled NON-CITABLE PILOT.

Diagnostics (NOT registered E4 numbers -- read `diagnostics`, never cite it)
---------------------------------------------------------------------------
The registered identity control is agreement with the ARM'S OWN REFERENCE, so it inherits
whatever that reference does on input points no gold row covers. Two diagnostics make that
inheritance visible instead of leaving it as an unexplained arm-A exclusion:

  referenceDivergence  -- every distinct input point appearing in any arm-A matrix,
                          evaluated three ways: refA (JPS pack), refB (Rego policy, the
                          other arm's reference) and the clean-room oracle
                          (design/cleanroom/oracle.py, the policy's executable reading).
                          Points where the two references disagree are listed with the
                          oracle's verdict, which says which reference is wrong there.
  armAOffProtocol      -- arm-A kill vectors recomputed with the identity-FAILING CASES
                          DROPPED from each suite. This is an off-protocol repair the
                          registered rules do not license; it exists only so the pilot
                          says something about arm-A suites that the registered rule
                          excludes wholesale.

Determinism
-----------
Fixed mutant/suite orderings (manifest order, sorted run ids), no timestamps, no random
seeds, JSON written with sorted keys. Engine calls run in a thread pool for wall-clock
only; every task is independent and results are reassembled in the fixed order.

Missing artifacts are RECORDED, never fabricated: a completed run (no `dropCode` in the
arm's SCORE.json) whose secondary artifact file is absent is reported under
`artifacts.missingSuites` and scored by nobody.

Stdlib only. Python 3.8+.
"""

import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, ".."))
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"

JPACK = os.environ.get("JPACK_BIN", os.path.join(SCRATCH, "pins", "jpack", "jpack"))
OPA = os.environ.get("OPA_BIN", os.path.join(SCRATCH, "pins", "opa", "opa_linux_amd64_static"))
CAPS = os.environ.get("OPA_CAPS", os.path.join(SCRATCH, "pins", "opa", "caps-filtered.json"))

PILOT = os.environ.get(
    "E4_PILOT_DIR",
    os.path.join(DESIGN, "pilots", "2026-08-15-calibration-pilot-01"))
REF_A = os.path.join(DESIGN, "reference", "refA", "pack.json")
REF_B = os.path.join(DESIGN, "reference", "refB", "policy.rego")
MUT_A_DIR = os.path.join(HERE, "refA")
MUT_B_DIR = os.path.join(HERE, "refB")
OUT = os.path.join(HERE, "E4-PILOT.json")

ENGINE_TIMEOUT_S = 60
WORKERS = int(os.environ.get("E4_WORKERS", str(min(16, (os.cpu_count() or 4)))))

# arm -> (language, secondary artifact filename)
ARMS = [("A", "jps", "secondary.json"),
        ("B", "rego", "secondary.rego"),
        ("C", "rego", "secondary.rego")]

LABEL = "NON-CITABLE PILOT"


# --------------------------------------------------------------------------- util


def clean_env(home):
    """Minimal environment: no inherited JPACK_CONFIG, TZ pinned to UTC."""
    return {"PATH": "/usr/bin:/bin", "TZ": "UTC", "HOME": home, "TMPDIR": home}


_tls = threading.local()


def worker_dir(root):
    """A per-thread scratch directory containing no jpack.json."""
    d = getattr(_tls, "dir", None)
    if d is None:
        d = tempfile.mkdtemp(prefix="w-", dir=root)
        _tls.dir = d
    return d


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


# ------------------------------------------------------------------- mutant sets


def load_mutants():
    """-> {'jps': [rec...], 'rego': [rec...]} in MANIFEST order, valid mutants only.

    rec = {id, path, witnessSet (sorted), witnessKey (tuple), notAdequate, class}
    """
    a_manifest = load_json(os.path.join(MUT_A_DIR, "MANIFEST.json"))
    jps = []
    for m in a_manifest:
        if m.get("validates") is not True:
            continue
        ws = sorted(m.get("witnessSet") or [])
        jps.append({"id": m["id"],
                    "path": os.path.join(MUT_A_DIR, m["id"] + ".json"),
                    "witnessSet": ws,
                    "witnessKey": tuple(ws),
                    "notAdequate": bool(m.get("notAdequate")),
                    "class": m.get("class")})

    b_manifest = load_json(os.path.join(MUT_B_DIR, "MANIFEST.json"))
    rego = []
    for m in b_manifest["mutants"]:
        if m.get("status") != "valid":
            continue
        ws = sorted(m.get("witnessSet") or [])
        rego.append({"id": m["id"],
                     "path": os.path.join(MUT_B_DIR, m["file"]),
                     "witnessSet": ws,
                     "witnessKey": tuple(ws),
                     "notAdequate": bool(m.get("notAdequate")),
                     "class": m.get("mutationClass")})

    for lang, recs in (("jps", jps), ("rego", rego)):
        for r in recs:
            if not os.path.exists(r["path"]):
                raise SystemExit("missing mutant file: %s" % r["path"])
            # the empty-witness <-> notAdequate identity the pairing rule leans on
            if r["notAdequate"] != (len(r["witnessSet"]) == 0):
                raise SystemExit(
                    "%s %s: notAdequate=%s but witnessSet size %d"
                    % (lang, r["id"], r["notAdequate"], len(r["witnessSet"])))
    return {"jps": jps, "rego": rego}


def build_pairing(mutants):
    """The registered pairing rule: identical sorted witness sets."""
    groups = {}
    for lang in ("jps", "rego"):
        for r in mutants[lang]:
            g = groups.setdefault(r["witnessKey"], {"jps": [], "rego": []})
            g[lang].append(r["id"])

    table = []
    for key in sorted(groups, key=lambda k: (len(k), k)):
        g = groups[key]
        paired = bool(g["jps"]) and bool(g["rego"])
        degenerate = paired and len(key) == 0
        table.append({
            "witnessSet": list(key),
            "witnessCount": len(key),
            "jpsMutants": g["jps"],
            "regoMutants": g["rego"],
            "jpsCount": len(g["jps"]),
            "regoCount": len(g["rego"]),
            "paired": paired,
            "notAdequate": len(key) == 0,
            "degenerate": degenerate,
            "countedInPairedSubset": paired and not degenerate,
        })

    paired_ids = {"jps": set(), "rego": set()}
    for row in table:
        if row["countedInPairedSubset"]:
            paired_ids["jps"].update(row["jpsMutants"])
            paired_ids["rego"].update(row["regoMutants"])
    return table, paired_ids


# ------------------------------------------------------------------ alignment scope


def align_expected(expected):
    """(kind, outcomeId, sorted reasons) from a matrix case's expectedDisposition."""
    if not isinstance(expected, dict):
        return None
    kind = expected.get("kind")
    if kind == "outcome":
        return ("outcome", expected.get("outcomeId"),
                tuple(sorted(str(r) for r in (expected.get("reasons") or []))))
    if kind == "unresolved":
        return ("unresolved", None,
                tuple(sorted(str(r) for r in (expected.get("reasons") or []))))
    return None


def eval_pack(pack_path, facts, evidence, root):
    """-> alignment-scope tuple, or ('ROW-ERROR', <class>, ()) for a refusal."""
    wd = worker_dir(root)
    fpath = os.path.join(wd, "facts.json")
    epath = os.path.join(wd, "evidence.json")
    with open(fpath, "w") as fh:
        json.dump(facts, fh)
    with open(epath, "w") as fh:
        json.dump(evidence, fh)
    argv = [JPACK, "experimental", "evaluate", pack_path,
            "--facts", fpath, "--evidence", epath, "--format", "json"]
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=ENGINE_TIMEOUT_S, cwd=wd, env=clean_env(wd))
    except subprocess.TimeoutExpired:
        return ("ROW-ERROR", "engine-timeout", ())
    try:
        payload = json.loads(p.stdout.decode("utf-8", "replace"))
    except Exception:
        return ("ROW-ERROR", "non-json-payload", ())
    if payload.get("status") != "evaluated":
        diags = payload.get("diagnostics") or []
        cls = ((payload.get("error") or {}).get("class")
               or (diags[0].get("code") if diags else None)
               or payload.get("status") or "refused")
        return ("ROW-ERROR", str(cls), ())
    disp = payload.get("disposition") or {}
    kind = disp.get("kind")
    reasons = tuple(sorted(str(r) for r in (disp.get("reasons") or [])))
    if kind == "outcome":
        return ("outcome", disp.get("outcomeId"), reasons)
    if kind == "unresolved":
        return ("unresolved", None, reasons)
    return ("ROW-ERROR", "unexpected-kind:%s" % kind, ())


def scope_str(t):
    if t is None:
        return "<unreadable-expectation>"
    if t[0] == "ROW-ERROR":
        return "ROW-ERROR:%s" % t[1]
    if t[0] == "outcome":
        return "outcome:%s" % t[1]
    return "unresolved:[%s]" % ",".join(t[2])


# ------------------------------------------------------------------------ arm A


def load_matrix(path):
    """-> (cases, note). Cases are (id, facts, evidence, expected_tuple, raw_ok)."""
    doc = load_json(path)
    cases = []
    for i, c in enumerate(doc.get("cases") or []):
        cid = c.get("id") if isinstance(c.get("id"), str) else "case[%d]" % i
        facts = c.get("facts")
        ev = c.get("evidenceAvailability") or {}
        exp = align_expected(c.get("expectedDisposition"))
        ok = isinstance(facts, dict) and exp is not None
        cases.append((cid, facts if isinstance(facts, dict) else {},
                      ev if isinstance(ev, dict) else {}, exp, ok))
    return cases, {"matrixVersion": doc.get("matrixVersion"), "caseCount": len(cases)}


def identity_arm_a(cases, root):
    failures = []
    for cid, facts, ev, exp, ok in cases:
        if not ok:
            failures.append({"case": cid, "expected": "<unreadable>", "got": "<not-run>",
                             "reason": "case missing facts or a readable expectedDisposition"})
            continue
        got = eval_pack(REF_A, facts, ev, root)
        if got != exp:
            failures.append({"case": cid, "expected": scope_str(exp), "got": scope_str(got)})
    return (len(failures) == 0), failures


def kill_arm_a(mutant_path, cases, root):
    """-> (killed, first_disagreeing_case_id or None)"""
    for cid, facts, ev, exp, ok in cases:
        if not ok:
            continue                      # an unscorable case can kill nothing
        got = eval_pack(mutant_path, facts, ev, root)
        if got != exp:
            return True, cid
    return False, None


# ---------------------------------------------------------------------- arms B/C


def opa_test(policy_path, suite_path, root):
    """-> (exit_code, class_label)"""
    wd = worker_dir(root)
    argv = [OPA, "test", policy_path, suite_path,
            "--capabilities", CAPS, "--timeout", "10s"]
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=ENGINE_TIMEOUT_S, cwd=wd, env=clean_env(wd))
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    if rc == 0:
        return rc, "pass"
    if rc == 1:
        return rc, "test-failure"
    if rc == 2:
        return rc, "error"
    if rc == 124:
        return rc, "timeout"
    return rc, "other"


# -------------------------------------------------------------------- diagnostics
#
# Nothing below feeds a registered number. It lands under `diagnostics`, labelled.

# matrix facts member -> (oracle cell key, wire kind)
VENDOR_MEMBERS = [("riskScore", "risk", "number"),
                  ("requestedSpend", "spend", "number"),
                  ("sanctionsStatus", "sanctions", "string"),
                  ("countryRisk", "country", "string"),
                  ("newVendor", "newVendor", "string"),
                  ("criticalSupplier", "critical", "string"),
                  ("priorEnforcement", "prior", "string")]
EVIDENCE_MEMBERS = [("financial-evidence", "finEvidence"),
                    ("insurance-certificate", "insurance")]


def case_signature(facts, evidence):
    vendor = (facts or {}).get("vendor") or {}
    sig = {}
    for member, cell, _kind in VENDOR_MEMBERS:
        sig[cell] = vendor.get(member)
    for member, cell in EVIDENCE_MEMBERS:
        sig[cell] = (evidence or {}).get(member)
    return sig


def render_rego_input(sig):
    """Numbers spliced TEXTUALLY from the canonical decimal strings (no float round-trip)."""
    vend, ev = [], []
    for member, cell, kind in VENDOR_MEMBERS:
        val = sig.get(cell)
        if val is None:
            continue                       # omitted member = unreadable / unreported
        vend.append('"%s": %s' % (member, val if kind == "number" else json.dumps(val)))
    for member, cell in EVIDENCE_MEMBERS:
        val = sig.get(cell)
        if val is None:
            continue
        ev.append('"%s": %s' % (member, json.dumps(val)))
    return '{"vendor": {%s}, "evidence": {%s}}\n' % (", ".join(vend), ", ".join(ev))


def eval_rego_point(policy_path, sig, root):
    wd = worker_dir(root)
    ipath = os.path.join(wd, "input.json")
    with open(ipath, "w") as fh:
        fh.write(render_rego_input(sig))
    argv = [OPA, "eval", "--format", "json", "--fail", "--strict-builtin-errors",
            "--capabilities", CAPS, "--timeout", "10s",
            "--data", policy_path, "--input", ipath, "data.study.decision"]
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=ENGINE_TIMEOUT_S, cwd=wd, env=clean_env(wd))
    except subprocess.TimeoutExpired:
        return "ROW-ERROR:engine-timeout"
    try:
        doc = json.loads(p.stdout.decode("utf-8", "replace"))
        value = doc["result"][0]["expressions"][0]["value"]
        disp, reasons = value["disposition"], sorted(value.get("reasons") or [])
    except Exception:
        return "ROW-ERROR:undefined"
    if disp == "unresolved":
        return "unresolved:[%s]" % ",".join(reasons)
    return "outcome:%s" % disp


def oracle_verdict(sig):
    try:
        cleanroom = os.path.join(DESIGN, "cleanroom")
        if cleanroom not in sys.path:
            sys.path.insert(0, cleanroom)
        from oracle import verdict            # noqa: E402  (optional diagnostic import)
    except Exception:
        return None
    try:
        v = verdict(dict(sig))
    except Exception as exc:
        return "ORACLE-ERROR:%s" % type(exc).__name__
    disp, reasons = v.get("disposition"), sorted(v.get("reasons") or [])
    if disp == "unresolved":
        return "unresolved:[%s]" % ",".join(reasons)
    return "outcome:%s" % disp


def reference_divergence(arm_a_suites, root):
    """refA vs refB vs the clean-room oracle on every distinct arm-A matrix input point."""
    points, order = {}, []
    for suite in arm_a_suites:
        cases, _ = load_matrix(suite["path"])
        for cid, facts, ev, exp, ok in cases:
            sig = case_signature(facts, ev)
            key = json.dumps(sig, sort_keys=True)
            if key not in points:
                points[key] = {"sig": sig, "cases": [], "expected": scope_str(exp) if ok else None,
                               "facts": facts, "evidence": ev}
                order.append(key)
            points[key]["cases"].append("%s/%s" % (suite["run"], cid))

    rows, diverging = [], []
    for key in order:
        pt = points[key]
        a = scope_str(eval_pack(REF_A, pt["facts"], pt["evidence"], root))
        b = eval_rego_point(REF_B, pt["sig"], root)
        o = oracle_verdict(pt["sig"])
        row = {"inputs": {k: v for k, v in sorted(pt["sig"].items()) if v is not None},
               "cases": pt["cases"], "matrixExpectation": pt["expected"],
               "refA": a, "refB": b, "oracle": o, "agree": a == b}
        rows.append(row)
        if a != b:
            diverging.append(row)
    return {
        "label": "DIAGNOSTIC -- not a registered E4 number",
        "what": "refA vs refB vs clean-room oracle on every distinct arm-A matrix input point",
        "points": len(rows),
        "divergentPoints": len(diverging),
        "oracleBacksRefA": sum(1 for r in diverging if r["oracle"] == r["refA"]),
        "oracleBacksRefB": sum(1 for r in diverging if r["oracle"] == r["refB"]),
        "oracleBacksNeither": sum(1 for r in diverging
                                  if r["oracle"] not in (r["refA"], r["refB"])),
        "divergent": diverging,
    }


def arm_a_off_protocol(arm_a, mutants, paired_ids, root, pool):
    """Arm-A kill vectors with the identity-FAILING cases dropped. Off-protocol."""
    scored = mutants["jps"]
    adequate = [m for m in scored if not m["notAdequate"]]
    paired_adequate = [m for m in adequate if m["id"] in paired_ids["jps"]]
    per_run, rates, prates = [], [], []
    for e in arm_a["perRun"]:
        if e.get("identityPass"):
            continue                       # registered path already scored this suite
        dropped = {f["case"] for f in e.get("identityFailures", [])}
        cases, _ = load_matrix(os.path.join(DESIGN, e["suiteFile"]))
        kept = [c for c in cases if c[0] not in dropped]
        futs = [pool.submit(kill_arm_a, m["path"], kept, root) for m in scored]
        killed = [f.result()[0] for f in futs]
        kill_of = dict(zip((m["id"] for m in scored), killed))
        n_ad = sum(1 for m in adequate if kill_of[m["id"]])
        n_pa = sum(1 for m in paired_adequate if kill_of[m["id"]])
        rate = round(n_ad / len(adequate), 6) if adequate else None
        prate = round(n_pa / len(paired_adequate), 6) if paired_adequate else None
        rates.append(rate)
        prates.append(prate)
        per_run.append({"run": e["run"], "casesKept": len(kept),
                        "casesDropped": sorted(dropped),
                        "killVector": "".join("1" if k else "0" for k in killed),
                        "killed": n_ad, "killRate": rate,
                        "killedPaired": n_pa, "killRatePaired": prate,
                        "killedNotAdequate": sum(1 for m in scored
                                                 if m["notAdequate"] and kill_of[m["id"]]),
                        "survivorsAdequate": [m["id"] for m in adequate
                                              if not kill_of[m["id"]]]})
    return {
        "label": "DIAGNOSTIC -- not a registered E4 number",
        "what": "arm-A kill rates after dropping the identity-failing cases from each "
                "suite; the registered rule excludes these suites entirely",
        "suites": len(per_run),
        "perRun": per_run,
        "meanKillRate": mean([r for r in rates if r is not None]),
        "meanKillRatePaired": mean([r for r in prates if r is not None]),
    }


# ------------------------------------------------------------------------- suites


def collect_suites(arm, filename):
    """Completed runs (no dropCode) and their secondary artifacts. Records misses."""
    arm_dir = os.path.join(PILOT, "arm-" + arm)
    score = load_json(os.path.join(arm_dir, "SCORE.json"))
    suites, missing, dropped = [], [], []
    for rec in sorted(score.get("perRun") or [], key=lambda r: r.get("slot", "")):
        slot = rec.get("slot")
        run = "run-%s" % slot
        if rec.get("dropCode"):
            dropped.append({"run": run, "dropCode": rec["dropCode"]})
            continue
        path = os.path.join(arm_dir, run, filename)
        claimed = bool((rec.get("secondaryArtifact") or {}).get("present"))
        if not os.path.exists(path):
            missing.append({"run": run, "expectedFile": os.path.relpath(path, DESIGN),
                            "scoreJsonClaimsPresent": claimed})
            continue
        suites.append({"run": run, "path": path,
                       "bytes": os.path.getsize(path),
                       "scoreJsonClaimsPresent": claimed})
    return suites, missing, dropped, score


# -------------------------------------------------------------------------- score


def mean(xs):
    return round(sum(xs) / len(xs), 6) if xs else None


def score_arm(arm, lang, filename, mutants, paired_ids, root, pool):
    suites, missing, dropped, score = collect_suites(arm, filename)
    scored = [m for m in mutants[lang]]
    adequate = [m for m in scored if not m["notAdequate"]]
    not_adequate = [m for m in scored if m["notAdequate"]]
    paired_adequate = [m for m in adequate if m["id"] in paired_ids[lang]]

    per_run, id_failures = [], []
    for suite in suites:
        entry = {"run": suite["run"],
                 "suiteFile": os.path.relpath(suite["path"], DESIGN),
                 "suiteBytes": suite["bytes"]}
        if arm == "A":
            cases, note = load_matrix(suite["path"])
            entry.update(note)
            ident_ok, failures = identity_arm_a(cases, root)
        else:
            cases = None
            rc, cls = opa_test(REF_B, suite["path"], root)
            ident_ok = (rc == 0)
            failures = [] if ident_ok else [{"exitCode": rc, "class": cls}]
            entry["identityExitCode"] = rc
        entry["identityPass"] = ident_ok
        if not ident_ok:
            entry["identityFailures"] = failures[:20]
            entry["identityFailureCount"] = len(failures)
            entry["excludedFromKillRates"] = True
            id_failures.append(entry["run"])
            per_run.append(entry)
            continue

        # ---- kill vector, in fixed manifest order over the scored mutants
        if arm == "A":
            futs = [pool.submit(kill_arm_a, m["path"], cases, root) for m in scored]
            results = [f.result() for f in futs]
            killed = [r[0] for r in results]
            detail = {m["id"]: {"killingCase": r[1]}
                      for m, r in zip(scored, results) if r[0]}
        else:
            futs = [pool.submit(opa_test, m["path"], suite["path"], root) for m in scored]
            results = [f.result() for f in futs]
            killed = [r[0] != 0 for r in results]
            detail = {m["id"]: {"exitCode": r[0], "class": r[1]}
                      for m, r in zip(scored, results) if r[0] != 0}

        kill_of = dict(zip((m["id"] for m in scored), killed))
        n_ad = sum(1 for m in adequate if kill_of[m["id"]])
        n_na = sum(1 for m in not_adequate if kill_of[m["id"]])
        n_pa = sum(1 for m in paired_adequate if kill_of[m["id"]])
        classes = {}
        for v in detail.values():
            if "class" in v:
                classes[v["class"]] = classes.get(v["class"], 0) + 1

        entry.update({
            "killVector": "".join("1" if k else "0" for k in killed),
            "killed": n_ad,
            "killRate": round(n_ad / len(adequate), 6) if adequate else None,
            "killedPaired": n_pa,
            "killRatePaired": round(n_pa / len(paired_adequate), 6) if paired_adequate else None,
            "killedNotAdequate": n_na,
            "killRateNotAdequate": round(n_na / len(not_adequate), 6) if not_adequate else None,
            "survivorsAdequate": [m["id"] for m in adequate if not kill_of[m["id"]]],
            "killDetail": detail,
        })
        if arm != "A":
            entry["killFailureClasses"] = classes
        per_run.append(entry)

    used = [e for e in per_run if e.get("identityPass")]
    rates = [e["killRate"] for e in used if e["killRate"] is not None]
    prates = [e["killRatePaired"] for e in used if e["killRatePaired"] is not None]
    nrates = [e["killRateNotAdequate"] for e in used if e["killRateNotAdequate"] is not None]
    return {
        "label": LABEL,
        "arm": arm,
        "language": lang,
        "suites": len(suites),
        "identityPass": len(used),
        "identityFail": len(id_failures),
        "identityFailedRuns": id_failures,
        "droppedRuns": dropped,
        "missingSuiteFiles": missing,
        "mutantsScored": len(scored),
        "mutantsAdequate": len(adequate),
        "mutantsNotAdequate": len(not_adequate),
        "mutantsPairedAdequate": len(paired_adequate),
        "perRun": per_run,
        "meanKillRate": mean(rates),
        "killRateRange": [min(rates), max(rates)] if rates else None,
        "meanKillRatePaired": mean(prates),
        "killRatePairedRange": [min(prates), max(prates)] if prates else None,
        "meanKillRateNotAdequate": mean(nrates),
    }


# --------------------------------------------------------------------------- main


def main():
    mutants = load_mutants()
    pairing, paired_ids = build_pairing(mutants)

    root = tempfile.mkdtemp(prefix="e4-")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            per_arm = {}
            for arm, lang, filename in ARMS:
                sys.stderr.write("[%s] scoring arm %s (%s)...\n" % (LABEL, arm, lang))
                sys.stderr.flush()
                per_arm[arm] = score_arm(arm, lang, filename, mutants,
                                         paired_ids, root, pool)
            sys.stderr.write("[%s] diagnostics...\n" % LABEL)
            sys.stderr.flush()
            a_suites, _, _, _ = collect_suites("A", "secondary.json")
            diagnostics = {
                "label": "DIAGNOSTIC SECTION -- none of these are registered E4 numbers",
                "referenceDivergence": reference_divergence(a_suites, root),
                "armAOffProtocol": arm_a_off_protocol(per_arm["A"], mutants,
                                                      paired_ids, root, pool),
            }
    finally:
        shutil.rmtree(root, ignore_errors=True)

    adequacy = {}
    for key, lang, name in (("A", "jps", "refA (JPS)"), ("B", "rego", "refB (Rego)")):
        recs = mutants[lang]
        adequacy[key] = {
            "set": name,
            "total": len(recs),
            "goldKills": sum(1 for m in recs if not m["notAdequate"]),
            "goldSurvivors": sum(1 for m in recs if m["notAdequate"]),
            "source": "MANIFEST witness sets (gold rows that kill the mutant)",
        }
    adequacy["C"] = dict(adequacy["B"], note="arm C scores the same refB (Rego) set as arm B")

    doc = {
        "label": LABEL,
        "citable": False,
        "study": "019-authorship-across-representations",
        "analysis": "E4 (mutation kill rate) applied to the calibration pilot",
        "warning": "NON-CITABLE PILOT: pilot suites from pilot_run.py, gold 0-draft; "
                   "no number here may be cited except as a labelled pilot rate.",
        "pilot": os.path.relpath(PILOT, DESIGN),
        "scoredSurface": "alignment scope only: kind + outcomeId + sorted reasons "
                         "(handoff, handoffTarget and expectedHandoffTarget ignored)",
        "pairingRule": "identical sorted witness sets; the empty-witness group is "
                       "flagged degenerate and excluded from paired subsets",
        "mutantIndex": {
            "jps": [m["id"] for m in mutants["jps"]],
            "rego": [m["id"] for m in mutants["rego"]],
            "note": "killVector is a 0/1 string indexed by these orders",
        },
        "pairing": pairing,
        "pairingSummary": {
            "groups": len(pairing),
            "pairedGroups": sum(1 for r in pairing if r["countedInPairedSubset"]),
            "degenerateGroups": sum(1 for r in pairing if r["degenerate"]),
            "pairedJpsMutants": len(paired_ids["jps"]),
            "pairedRegoMutants": len(paired_ids["rego"]),
        },
        "perArm": per_arm,
        "adequacy": adequacy,
        "diagnostics": diagnostics,
    }
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print_summary(doc)
    return 0


def print_summary(doc):
    p = doc["pairingSummary"]
    print("=" * 78)
    print("Study 019 E4 -- %s (nothing here is citable)" % LABEL)
    print("=" * 78)
    print("pairing (identical sorted witness sets)")
    print("  groups %d | paired non-degenerate %d | degenerate (empty-witness) %d"
          % (p["groups"], p["pairedGroups"], p["degenerateGroups"]))
    print("  paired adequate mutants: JPS %d, Rego %d"
          % (p["pairedJpsMutants"], p["pairedRegoMutants"]))
    print()
    for arm in ("A", "B", "C"):
        a = doc["perArm"][arm]
        print("arm %s (%s): suites %d | identity pass %d | identity FAIL %d"
              % (arm, a["language"], a["suites"], a["identityPass"], a["identityFail"]))
        if a["missingSuiteFiles"]:
            print("  MISSING suite files: %s"
                  % ", ".join(m["run"] for m in a["missingSuiteFiles"]))
        if a["droppedRuns"]:
            print("  dropped runs (not scored): %s"
                  % ", ".join("%s/%s" % (d["run"], d["dropCode"]) for d in a["droppedRuns"]))
        print("  mutants scored %d (adequate %d, notAdequate %d, paired adequate %d)"
              % (a["mutantsScored"], a["mutantsAdequate"],
                 a["mutantsNotAdequate"], a["mutantsPairedAdequate"]))
        for e in a["perRun"]:
            if not e.get("identityPass"):
                print("    %s  IDENTITY FAIL (%s) -- excluded"
                      % (e["run"], e.get("identityFailureCount", e.get("identityExitCode"))))
                continue
            print("    %s  kill %3d/%3d = %.3f | paired %2d/%2d = %.3f | notAdequate %2d/%2d"
                  % (e["run"], e["killed"], a["mutantsAdequate"], e["killRate"],
                     e["killedPaired"], a["mutantsPairedAdequate"], e["killRatePaired"],
                     e["killedNotAdequate"], a["mutantsNotAdequate"]))
        rng = a["killRateRange"]
        prng = a["killRatePairedRange"]
        print("  mean kill rate %s (range %s) | mean paired %s (range %s)"
              % (a["meanKillRate"], rng, a["meanKillRatePaired"], prng))
        print()
    print("adequacy (how many mutants the gold suite kills)")
    for k in ("A", "B"):
        ad = doc["adequacy"][k]
        print("  %s %s: %d/%d killed by gold (%d survive gold)"
              % (k, ad["set"], ad["goldKills"], ad["total"], ad["goldSurvivors"]))
    print("  C: same refB set as arm B")
    print()
    d = doc["diagnostics"]
    rd = d["referenceDivergence"]
    print("DIAGNOSTICS (not registered E4 numbers -- do not cite as kill rates)")
    print("  reference divergence over arm-A matrix input points: %d/%d points where "
          "refA and refB disagree" % (rd["divergentPoints"], rd["points"]))
    print("    clean-room oracle backs refA on %d, refB on %d, neither on %d"
          % (rd["oracleBacksRefA"], rd["oracleBacksRefB"], rd["oracleBacksNeither"]))
    for r in rd["divergent"][:10]:
        print("      %s" % json.dumps(r["inputs"], sort_keys=True))
        print("        refA %-24s refB %-16s oracle %-16s matrix %s"
              % (r["refA"], r["refB"], r["oracle"], r["matrixExpectation"]))
    op = d["armAOffProtocol"]
    print("  arm A with identity-failing cases dropped (OFF-PROTOCOL): %d suites, "
          "mean kill %s, mean paired %s"
          % (op["suites"], op["meanKillRate"], op["meanKillRatePaired"]))
    for e in op["perRun"]:
        print("      %s  kept %d cases | kill %3d/%3d = %.3f | paired %2d = %.3f"
              % (e["run"], e["casesKept"], e["killed"],
                 doc["perArm"]["A"]["mutantsAdequate"], e["killRate"],
                 e["killedPaired"], e["killRatePaired"]))
    print()
    print("wrote %s  [%s]" % (OUT, LABEL))


if __name__ == "__main__":
    sys.exit(main())
