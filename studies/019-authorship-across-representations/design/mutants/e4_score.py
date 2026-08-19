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
   FIRST, in all three arms and before anything is evaluated: the REGISTERED PER-CASE
              DOMAIN CHECK (Sec 4), called in the harness rather than reimplemented here
              (`registered_domain_failures()` below; round-3 finding R3-4). An
              out-of-domain case is an identity failure categorised
              `out-of-domain-case`, so its run is excluded from every kill rate exactly
              as any other identity failure is, and a suite whose cases cannot be
              enumerated is the registered authoring code `unparseable-artifact`.
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
   arms B/C -- `opa test <mutant> <suite> --format json ...`; the suite KILLS the
              mutant iff a NAMED TEST FAILED ITS ASSERTION, read from the result
              document. Nothing is keyed on the exit status (round-1 R1-8), and a
              reported failure is ADJUDICATED before it counts (round-2 R2-3):
              `opa test` has no `--strict-builtin-errors` at v1.19.0, so an
              evaluation fault inside a test body makes the body undefined and the
              test reports `fail: true` with no `error` member. Every reported
              failure is therefore re-evaluated as a query under
              `opa eval --strict-builtin-errors`; a fault comes back as an
              `eval_builtin_error` and REFUSES, and an undefined body is the real
              assertion failure and kills. A refused mutant is scored NEITHER way:
              it is not a kill and not a survivor, and it stays in the denominator
              so no refusal inflates a rate by shrinking one.
   `notAdequate` mutants (empty witness set -- no gold row kills them) are scored but
   reported SEPARATELY: the headline kill rate is over the adequate own-language mutants.

4. OUTPUT E4-PILOT-v4.json (`OUT` below; the current issue) + a printed summary, both
   labelled NON-CITABLE PILOT. Every earlier issue stays on disk carrying a
   `supersededBy` member naming its successor, so the chain from the first issue to the
   current one is walkable and is walked by a test.

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

import argparse
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
OUT = os.path.join(HERE, "E4-PILOT-v4.json")

# --- ROUND-3 FINDING R3-4: the registered per-case domain check, and it is the
# HARNESS's, imported rather than reimplemented -----------------------------
#
# v3 reported arm C at identity 5/5 and a paired kill mean of 0.855385 while its
# own banner admitted that this prototype "runs no per-case registered-domain
# check" and that four of the five arm-C suites contain an out-of-domain case.
# §4 registers the check as part of the identity control — "each enumerated case
# is validated against the registered domain BEFORE identity and mutation
# execution, identically in A, B and C. An out-of-domain case is an identity
# failure categorised `out-of-domain-case`" — so those four runs are identity
# failures and the numbers computed over them were computed under a rule the
# study does not have.
#
# The repair is not a second implementation of §4 in this file. Two
# implementations of one registered rule is what produced the disagreement in
# the first place (round-2 R2-2, the denominator; round-3 R3-4, the domain), and
# the tie-break has been the same both times: the PRIMARY path is the registered
# one and the pilot moves to it. So this prototype consumes
# `harness/e4lib/{e4,engines}.py` directly — the same functions
# `harness/score.py` calls, on the same inputs — or it REFUSES to run at all. A
# pilot that silently scored without the check is exactly what R3-4 found.
HARNESS = os.path.abspath(os.path.join(DESIGN, os.pardir, "harness"))
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)
try:
    from e4lib import e4 as harness_e4              # noqa: E402
    from e4lib import engines as harness_engines    # noqa: E402
except ImportError as _error:                       # pragma: no cover
    raise SystemExit(
        "REFUSED: this pilot scorer applies the registered per-case domain "
        "check by calling the harness (%s), and the harness did not import "
        "(%s). It does not have a second implementation to fall back on, and "
        "scoring without the check is the round-3 R3-4 defect."
        % (HARNESS, _error))

HARNESS_PINS = os.path.join(HARNESS, "PINS.json")

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


_harness_tools = None


def harness_tools():
    """The harness `Toolchain`, over THIS script's pinned binaries, or refuse.

    ROUND-3 R3-4. `e4lib.rego_case_signatures()` reaches the pinned parser
    through a `Toolchain`, so the enumeration the primary path performs is
    available here only with one built. It is built from the harness registry
    and from the same three binaries this file already resolves, and a toolchain
    carrying any problem REFUSES: a domain check that quietly did not run is the
    finding, and a domain check that quietly ran against an unpinned binary
    would be its sibling."""
    global _harness_tools
    if _harness_tools is None:
        with open(HARNESS_PINS) as fh:
            pins = json.load(fh)
        tools = harness_engines.Toolchain(
            pins, {"JPACK_BIN": JPACK, "OPA_BIN": OPA, "OPA_CAPS": CAPS})
        if tools.problems:
            raise SystemExit(
                "REFUSED: the registered per-case domain check runs through the "
                "pinned toolchain and it does not resolve: %s"
                % "; ".join(tools.problems))
        _harness_tools = tools
    return _harness_tools


def registered_domain_failures(arm, suite_path, root):
    """§4's per-case domain validation for one suite — THE PRIMARY PATH'S.

    ROUND-3 R3-4, and every line of the check itself lives in the harness:
    arm A's cases come from `e4lib.load_matrix()` and are signed by
    `e4lib.matrix_domain_signature()`; arms B and C are enumerated from the
    suite's own syntax tree by `e4lib.rego_case_signatures()` through the pinned
    parser; both are judged by `e4lib.domain_failures()` against the one
    registered domain, with arm A's wire form `string` and B/C's `number`. This
    function chooses which of those to call and nothing else.

    A suite that cannot be enumerated is `unparseable-artifact` — the registered
    authoring code — reported here as the identity failure §4 makes it, never as
    a pass."""
    tools = harness_tools()
    workdir = worker_dir(root)
    if arm == "A":
        cases, _note = harness_e4.load_matrix(suite_path)
        named = [(case[0], harness_e4.matrix_domain_signature(case[1], case[2]))
                 for case in cases]
        wire = "string"
    else:
        named = harness_e4.rego_case_signatures(tools, suite_path, workdir,
                                                REF_B)
        wire = "number"
    return harness_e4.domain_failures(named, wire)


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


TEST_PASS = "pass"
TEST_FAILED = "failed"
TEST_ERRORED = "errored"
TEST_INVOCATION_REFUSED = "invocation-refused"
TEST_TIMEOUT = "timeout"
TEST_UNREADABLE = "unreadable-result-document"

# The two statuses that are evidence ABOUT THE SUITE. Every other status is
# evidence about the apparatus. Identical to `harness/e4lib/engines.py`'s, and
# deliberately so: the pilot read and the primary read are the same taxonomy or
# the pilot is not a pilot of this study (round-2 findings R2-2 and R2-3).
TEST_SUITE_STATUSES = (TEST_PASS, TEST_FAILED)


def _run(argv, wd):
    try:
        finished = subprocess.run(argv, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  timeout=ENGINE_TIMEOUT_S, cwd=wd,
                                  env=clean_env(wd))
    except subprocess.TimeoutExpired:
        return 124, b"", b""
    return finished.returncode, finished.stdout, finished.stderr


def evaluation_fault(policy_path, suite_path, test_name, wd):
    """The named test re-evaluated in STRICT builtin-error mode: the fault code
    when the body could not be evaluated, or None when it merely did not hold."""
    query = test_name.split("/")[0]
    argv = [OPA, "eval", "--format", "json", "--strict-builtin-errors",
            "--capabilities", CAPS, "--timeout", "10s",
            "--data", policy_path, "--data", suite_path, query]
    code, out, _err = _run(argv, wd)
    try:
        document = json.loads(out.decode("utf-8", "replace") or "{}")
    except ValueError:
        return "unreadable-adjudication"
    if not isinstance(document, dict):
        return "unreadable-adjudication"
    errors = document.get("errors")
    if isinstance(errors, list) and errors:
        codes = sorted({entry.get("code") for entry in errors
                        if isinstance(entry, dict)
                        and isinstance(entry.get("code"), str)})
        return ",".join(codes) or "eval-error"
    if code != 0:
        return "adjudication-exit-%d" % code
    return None


def opa_test(policy_path, suite_path, root):
    """-> the RESULT-DOCUMENT record: `{exitCode, tests, failed, errored,
    evaluationFaults, status}`.

    ROUND-1 R1-8 and ROUND-2 R2-3, together. This returned `(exit code, class
    label)` and the caller killed on any nonzero, so a compile failure, a load
    failure and this script's own timeout each killed every mutant they touched;
    and the class table it recorded had the v1.19.0 statuses backwards. The
    status is now RECORDED and read by nothing, the kill signal is a named test
    that failed its assertion, and a reported failure that is really an
    evaluation fault refuses instead of killing."""
    wd = worker_dir(root)
    argv = [OPA, "test", policy_path, suite_path,
            "--capabilities", CAPS, "--timeout", "10s", "--format", "json"]
    code, out, err = _run(argv, wd)
    record = {"exitCode": code, "tests": 0, "failed": [], "errored": [],
              "evaluationFaults": [], "status": None}
    if code == 124:
        record["status"] = TEST_TIMEOUT
        return record
    text = out.decode("utf-8", "replace")
    try:
        document = json.loads(text)
    except ValueError:
        document = None
    if not isinstance(document, list):
        record["status"] = (TEST_INVOCATION_REFUSED if not text.strip()
                            else TEST_UNREADABLE)
        record["diagnosticBytes"] = len(err)
        return record
    reported = []
    for entry in document:
        if not isinstance(entry, dict):
            record["status"] = TEST_UNREADABLE
            return record
        record["tests"] += 1
        name = "%s.%s" % (entry.get("package"), entry.get("name"))
        if entry.get("error") is not None:
            record["errored"].append(name)
        elif entry.get("fail"):
            reported.append(name)
    # DETERMINISM, and it is a registered property of what this produces.
    # `opa test --format json` does not order its result list (`--sort` defaults
    # to `none`), so "the first reported failure" is not a stable choice and two
    # scorings of one batch disagreed on which named test they recorded. Sorting
    # here makes the adjudication order — and therefore the retained
    # `failedTests` — a function of the data and not of the run.
    for name in sorted(reported):
        fault = evaluation_fault(policy_path, suite_path, name, wd)
        if fault is None:
            record["failed"].append(name)
            break
        record["evaluationFaults"].append({"test": name, "fault": fault})
        record["errored"].append(name)
    record["errored"].sort()
    if record["failed"]:
        record["status"] = TEST_FAILED
    elif record["errored"]:
        record["status"] = TEST_ERRORED
    else:
        record["status"] = TEST_PASS
    return record


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

    per_run, id_failures, refused_runs = [], [], []
    for suite in suites:
        entry = {"run": suite["run"],
                 "suiteFile": os.path.relpath(suite["path"], DESIGN),
                 "suiteBytes": suite["bytes"]}

        # ROUND-3 R3-4: the registered domain check runs FIRST, in all three
        # arms, through the harness — before identity and before any mutant is
        # touched, which is the order §4 registers. An out-of-domain case is an
        # identity failure, so the run is excluded from the kill rates exactly
        # as any other identity failure is.
        try:
            failures = registered_domain_failures(arm, suite["path"], root)
            entry["outOfDomainCases"] = [f["case"] for f in failures]
        except harness_e4.MatrixError as error:
            entry["identityPass"] = False
            entry["excludedFromKillRates"] = True
            entry["dropCode"] = "unparseable-artifact"
            entry["identityFailures"] = [
                {"case": "<suite>", "expected": "<enumerable cases>",
                 "got": "unparseable-artifact", "problems": [str(error)]}]
            entry["identityFailureCount"] = 1
            id_failures.append(entry["run"])
            per_run.append(entry)
            continue
        if failures:
            entry["identityPass"] = False
            entry["excludedFromKillRates"] = True
            entry["identitySource"] = ("harness e4lib.domain_failures — §4's "
                                       "registered per-case domain check")
            entry["identityFailures"] = failures[:20]
            entry["identityFailureCount"] = len(failures)
            id_failures.append(entry["run"])
            per_run.append(entry)
            continue

        if arm == "A":
            cases, note = load_matrix(suite["path"])
            entry.update(note)
            ident_ok, failures = identity_arm_a(cases, root)
        else:
            cases = None
            probe = opa_test(REF_B, suite["path"], root)
            # ROUND-1 R1-8: `pass` is the control held and `failed` is a real
            # identity failure. Every other status is the APPARATUS, and a suite
            # is not scored zero for an invocation this script could not make.
            entry["identityStatus"] = probe["status"]
            entry["identityExitCode"] = probe["exitCode"]
            if probe["status"] not in TEST_SUITE_STATUSES:
                entry["identityPass"] = None
                entry["engineRefused"] = probe["status"]
                entry["excludedFromKillRates"] = True
                entry["apparatusRefusal"] = True
                refused_runs.append(entry["run"])
                per_run.append(entry)
                continue
            ident_ok = (probe["status"] == TEST_PASS)
            failures = [] if ident_ok else [{"status": probe["status"],
                                             "failedTests": probe["failed"][:5]}]
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
            # ROUND-2 R2-3: a kill is a named test that FAILED ITS ASSERTION and
            # survived the strict-mode adjudication. Everything else — an
            # errored test, an evaluation fault, an invocation that never ran the
            # tests, a timeout — is a REFUSAL, scored neither way.
            killed = [r["status"] == TEST_FAILED for r in results]
            refused = [m["id"] for m, r in zip(scored, results)
                       if r["status"] not in TEST_SUITE_STATUSES]
            detail = {m["id"]: {"exitCode": r["exitCode"], "status": r["status"],
                                "failedTests": r["failed"][:3],
                                "evaluationFaults": r["evaluationFaults"][:3]}
                      for m, r in zip(scored, results)
                      if r["status"] != TEST_PASS}
            entry["refusedMutants"] = refused
            entry["refusedMutantCount"] = len(refused)

        kill_of = dict(zip((m["id"] for m in scored), killed))
        n_ad = sum(1 for m in adequate if kill_of[m["id"]])
        n_na = sum(1 for m in not_adequate if kill_of[m["id"]])
        n_pa = sum(1 for m in paired_adequate if kill_of[m["id"]])
        classes = {}
        for v in detail.values():
            if "status" in v:
                classes[v["status"]] = classes.get(v["status"], 0) + 1

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
        "apparatusRefusedRuns": refused_runs,
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


def high_kill_layer(doc, tau):
    """E4's decision layer, at the REGISTERED denominator.

    R1-1, verbatim: *"The scorer derives one cutoff -- 77 -- from the JPS count and passes
    it to all arms, while each arm's kill denominator remains language-specific ... A
    perfect B/C suite therefore kills at most 73 and can never be high-kill. Fix: derive
    and publish language-specific cuts ... with an assertion that each cut is no larger
    than its run's denominator."*

    So the cut is computed PER LANGUAGE from that language's own paired-adequate
    denominator, published as an integer next to the denominator it came from, and
    asserted to be reachable.

    ROUND-2 FINDING R2-2, and it was a disagreement between two scorers about ONE
    registered rule. This layer divided by the identity-PASSING runs; §5 registers the
    denominator as §1a's "attempted runs whose apparatus succeeded", with authoring
    outcomes retained as not-high-kill and "identity-control exclusions ... reported,
    never silently dropped". On a two-run arm with one identity-passing high-kill run and
    one identity failure the two rules answer 1/1 and 1/2, and `harness/score.py` has
    always answered 1/2. The registered rule is the primary scorer's; this now computes
    it, and the pilot's published rates moved.

    An identity-failing suite carries `highKill: null` — never False, because it was never
    asked — and is IN the denominator all the same. A suite the ENGINE refused on is
    neither: an apparatus failure is not an attempted run whose apparatus succeeded, so it
    leaves the denominator and is published as its own count."""
    lang_of = {"A": "jps", "B": "rego", "C": "rego"}
    cuts = {}
    for lang, arm in (("jps", "A"), ("rego", "B")):
        n = doc["perArm"][arm]["mutantsPairedAdequate"]
        cut = -(-int(round(tau * 1000000)) * n // 1000000)   # exact ceil(tau*n), no floats
        assert cut <= n, ("cut %d exceeds the paired denominator %d for %s: no suite could "
                          "ever be high-kill" % (cut, n, lang))
        cuts[lang] = {"pairedAdequateMutants": n, "tau": tau, "integerCut": cut,
                      "cutAsFraction": round(cut / n, 6) if n else None,
                      "assertionCutReachable": cut <= n}
    for arm in ("A", "B", "C"):
        a = doc["perArm"][arm]
        cut = cuts[lang_of[arm]]["integerCut"]
        high = 0
        denominator = 0
        for e in a["perRun"]:
            if e.get("apparatusRefusal"):
                e["highKill"] = None          # outside the population entirely
                continue
            denominator += 1
            if not e.get("identityPass"):
                e["highKill"] = None          # in the denominator, never asked
                continue
            e["highKill"] = e["killedPaired"] >= cut
            high += 1 if e["highKill"] else 0
        a["highKill"] = {
            "language": lang_of[arm],
            "integerCut": cut,
            "pairedAdequateMutants": cuts[lang_of[arm]]["pairedAdequateMutants"],
            "admittedRuns": denominator,
            "identityFailingRunsInDenominator": len(a["identityFailedRuns"]),
            "apparatusRefusedRuns": len(a.get("apparatusRefusedRuns") or []),
            "highKillRuns": high,
            "highKillRate": round(high / denominator, 6) if denominator else None,
            "note": "denominator is §1a's ADMITTED runs (attempted runs whose apparatus "
                    "succeeded), so identity-failing suites are IN it carrying "
                    "highKill: null and are reported separately; an engine refusal is an "
                    "apparatus failure and leaves it (round-2 R2-2)",
        }
    return {"tau": tau,
            "rule": "high-kill iff the suite kills at least ceil(tau * N) of ITS OWN "
                    "language's paired adequate mutant subset, over §1a's admitted-run "
                    "denominator",
            "perLanguage": cuts,
            "finding": "round-1 R1-1 (one cut derived from the JPS count was applied to "
                       "every arm) and round-2 R2-2 (the denominator here excluded "
                       "identity-failing runs and the registered rule retains them)"}


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT,
                    help="output path (E4-PILOT-v4.json for the current issue)")
    ap.add_argument("--tau", type=float, default=0.95)
    args = ap.parse_args()
    OUT = args.out
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
        "issue": "v4",
        "supersedes": ["E4-PILOT.json", "E4-PILOT-v2.json", "E4-PILOT-v3.json"],
        "supersedingBanner":
            "THIS ISSUE SUPERSEDES E4-PILOT-v3.json, WHICH SUPERSEDED v2 AND v1. "
            "ROUND-3 FINDING R3-4 is the reason this issue exists and the reason no "
            "arm-C figure from any earlier issue survives it: the registered per-case "
            "DOMAIN CHECK of Sec 4 is APPLIED HERE, and it was applied in no earlier "
            "issue. v3's own banner said so and published arm C's identity count and "
            "kill rates anyway, over suites Sec 4 makes identity failures. The check is "
            "not reimplemented in this prototype: it is CALLED IN THE HARNESS "
            "(`e4lib.load_matrix`, `e4lib.matrix_domain_signature`, "
            "`e4lib.rego_case_signatures`, `e4lib.domain_failures`), the same functions "
            "on the same inputs `harness/score.py` runs, and this script REFUSES to "
            "score at all if the harness or the pinned toolchain does not resolve -- two "
            "implementations of one registered rule is what produced R2-2's denominator "
            "split and R3-4's domain omission, and the tie-break both times was that the "
            "PRIMARY path is the registered one and the pilot moves to it. Every identity "
            "count, identity-failing run list and kill rate below is therefore over runs "
            "that passed BOTH the domain check and the arm's own identity control, and "
            "`outOfDomainCases` names the offending cases per run. The denominator does "
            "NOT move with them: Sec 1a/Sec 5 register admitted runs, so an "
            "identity-failing run stays in it carrying `highKill: null` -- read "
            "`perArm.<arm>.highKill.admittedRuns`, never the length of the scored-run "
            "list. This issue also carries the corpus the round-3 adequacy repair "
            "produced (gold 0.2-draft, both MANIFESTs re-witnessed), so the pairing, the "
            "paired subsets and both integer cuts differ from v3's as well. v3, v2 and v1 "
            "are bannered, not deleted, and each names its successor. "
            "WHAT v3 CARRIED FORWARD, unchanged and still true: R2-3 -- arms B and C "
            "counted every nonzero "
            "`opa test` exit as a kill, so an invocation that never ran the tests, a "
            "timeout, and an evaluation fault inside a test body would each have killed "
            "every mutant they touched. A kill is now a NAMED TEST THAT FAILED ITS "
            "ASSERTION, read from the result document and adjudicated under "
            "`opa eval --strict-builtin-errors` because `opa test` has no such flag at "
            "v1.19.0. Measured: 0 refused mutants and 0 evaluation faults across all ten "
            "Rego runs -- v2's per-run `killFailureClasses` of {error: 126} and the like "
            "were a LABELLING defect (this script's class table had v1.19.0's exit "
            "taxonomy backwards; exit 2 is a failed test, not an error), not "
            "errors-counted-as-kills. R2-2 -- the high-kill denominator here was the "
            "identity-PASSING runs, and Sec 5 registers Sec 1a's admitted runs, which "
            "RETAIN identity-control exclusions carrying `highKill: null`; "
            "`harness/score.py` has always used the registered one. On v3's inputs that "
            "rule change moved nothing because v3 had no identity failure anywhere; on "
            "THIS issue's inputs it is load-bearing, and it is why arm C's high-kill "
            "fraction below is over five admitted runs and not over the one that passed "
            "the domain check.",
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
    doc["highKillCuts"] = high_kill_layer(doc, args.tau)
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
    hk = doc.get("highKillCuts")
    if hk:
        print("HIGH-KILL CUTS (per language, tau = %s)" % hk["tau"])
        for lang, c in sorted(hk["perLanguage"].items()):
            print("  %-5s paired adequate %3d -> integer cut %3d (%.4f of the denominator)"
                  % (lang, c["pairedAdequateMutants"], c["integerCut"], c["cutAsFraction"]))
        for arm in ("A", "B", "C"):
            a = doc["perArm"][arm]["highKill"]
            print("  arm %s: high-kill %d/%d admitted runs (cut %d, %s) = %s"
                  % (arm, a["highKillRuns"], a["admittedRuns"], a["integerCut"],
                     a["language"], a["highKillRate"]))
        print()
    print("wrote %s  [%s]" % (OUT, LABEL))


if __name__ == "__main__":
    sys.exit(main())
