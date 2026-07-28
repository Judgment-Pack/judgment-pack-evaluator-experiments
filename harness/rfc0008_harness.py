#!/usr/bin/env python3
"""Cross-implementation agreement harness for draft RFC 0008 (bounded collection quantifiers).

Modelled on `agreement_harness.py`, with two differences forced by RFC 0008:

  1. Every case carries its OWN pack. RFC 0008 rows differ in the condition under
     test, not only in the facts, so there is no single shared pack to pass in.
  2. Both implementations must be opted in to the draft grammar -- the Go
     reference runtime with `--rfc0008-quantifiers`, the clean-room Python
     implementation with `--enable-rfc0008`. A pack using `exists`, `every`, or
     `uniform` is not valid under JPS 0.1.0-draft, and neither flag changes that.

Like the RFC 0006 harness, this is referee tooling: it knows both output shapes
and is NOT part of either clean-room deliverable. Agreement rows are evidence the
RFC's prose pins the semantics; divergence rows are candidate spec ambiguities
(or bugs) and must be adjudicated against the RFC TEXT, never by making one
implementation copy the other.

Usage:
  rfc0008_harness.py cases       <go-binary> <python-repo-dir> <rfc0008_cases.json> [--json-out F]
  rfc0008_harness.py equivalence <go-binary> <python-repo-dir> <equivalence-dir>    [--json-out F]

`cases` runs the Conformance-section corpus. A row AGREES when the two
implementations' dispositions match on kind + outcomeId + reasons (as a set) +
handoff, or when both refuse with the same class of refusal.

`equivalence` runs the check the RFC's Conformance section asks any
implementation to run: re-encode the three quantifier-expressible census facts as
quantifiers against facts carrying the arrays, leave each room's remaining
prepared booleans in place, and confirm the dispositions match the
prepared-boolean packs. Both implementations must produce the same disposition
for the original pack and for its twin.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile


class RawJSON:
    """A JSON document carried as verbatim text, for tokens json.dump cannot re-emit."""

    def __init__(self, text):
        self.text = text


# --- error classification -------------------------------------------------
#
# Neither implementation's error vocabulary is specified: RFC 0008 says limit
# exhaustion is "an explicit evaluation error, never a disposition" and that a
# depth-three document is structurally invalid, but Core 0.1.0-draft has no
# evaluation-error contract to name either one (that is the RFC 0006 dependency
# recorded in Compatibility). So error rows are compared at the level of the
# CLASS of refusal, and the raw codes are carried through to the report so the
# coarseness of that mapping stays visible.

GO_ERROR_CLASS = {
    "JPS-EVALUATION-RFC0008-GRAMMAR": "structural-refusal",
    "JPS-EVALUATION-RFC0008-DEPTH": "structural-refusal",
    "JPS-RESOURCE-EVALUATION-WORK-LIMIT": "resource-limit",
    "JPS-RESOURCE-INPUT-BYTE-LIMIT": "resource-limit",
    "JPS-RESOURCE-COLLECTION-SIZE-LIMIT": "resource-limit",
}

PY_ERROR_CLASS = {
    # `invalid-input` is a broader bucket than Go's dedicated RFC 0008 codes; in
    # this corpus its only members are the aggregate-depth refusals.
    "invalid-input": "structural-refusal",
    "resource-limit": "resource-limit",
    "unsupported-extension": "unsupported-extension",
}


def _tmp(value):
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    if isinstance(value, RawJSON):
        handle.write(value.text)  # verbatim: preserves numeric tokens json.dump cannot
    else:
        json.dump(value, handle)
    handle.close()
    return handle.name


def run_go(binary, pack, facts, evidence, supported=()):
    paths = [_tmp(pack), _tmp(facts)]
    args = [binary, "experimental", "evaluate", paths[0],
            "--facts", paths[1], "--rfc0008-quantifiers", "--format", "json"]
    if evidence is not None:
        paths.append(_tmp(evidence))
        args += ["--evidence", paths[-1]]
    for ext in supported:
        args += ["--supported-extension", ext]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=120)
    for path in paths:
        os.unlink(path)
    payload = None
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except ValueError:
            payload = None
    if payload is None:
        return {"error": "unparseable", "class": "unparseable",
                "code": None, "detail": (proc.stdout + proc.stderr)[:300]}
    if payload.get("status") == "error" or "disposition" not in payload:
        diagnostics = payload.get("diagnostics") or [{}]
        code = diagnostics[0].get("code")
        detail = diagnostics[0].get("message", "")
        # The operation-layer wrapper quotes the first inner diagnostic; prefer
        # the inner code when it is present, since it is the specific refusal.
        for inner in GO_ERROR_CLASS:
            if inner != code and inner in detail:
                code = inner
                break
        return {"error": "refused", "class": GO_ERROR_CLASS.get(code, "other"),
                "code": code, "detail": detail[:300]}
    return payload.get("disposition")


def run_py(repo, pack, facts, evidence, supported=()):
    paths = [_tmp(pack), _tmp(facts)]
    args = [sys.executable, "-m", "jps_evaluator",
            "--pack", paths[0], "--facts", paths[1], "--enable-rfc0008"]
    if evidence is not None:
        paths.append(_tmp(evidence))
        args += ["--evidence", paths[-1]]
    if supported:
        args += ["--supported-extension"] + list(supported)
    proc = subprocess.run(args, capture_output=True, text=True, timeout=120,
                          cwd=repo)
    for path in paths:
        os.unlink(path)
    text = proc.stdout.strip() or proc.stderr.strip()
    if not text:
        return {"error": "unparseable", "class": "unparseable", "code": None,
                "detail": "exit %d, no output" % proc.returncode}
    try:
        payload = json.loads(text)
    except ValueError:
        return {"error": "unparseable", "class": "unparseable", "code": None,
                "detail": text[:300]}
    if "error" in payload:
        kind = payload["error"].get("kind")
        return {"error": "refused", "class": PY_ERROR_CLASS.get(kind, "other"),
                "code": kind, "detail": payload["error"].get("message", "")[:300]}
    return payload.get("disposition", payload)


def normalize(d):
    # Shape-tolerant, exactly as the RFC 0006 harness: impl #1 emits handoff as
    # {state, target}; impl #2 as a bare string with no target echo. Core
    # semantics compared here: kind, outcomeId, reasons set, handoff state.
    # Errors pass through as their class plus their raw code.
    if d is None:
        return None
    if "error" in d:
        return {"error": d.get("class"), "code": d.get("code")}
    handoff = d.get("handoff")
    state = handoff.get("state") if isinstance(handoff, dict) else handoff
    return {
        "kind": d.get("kind"),
        "outcomeId": d.get("outcomeId") or None,
        "reasons": sorted(d.get("reasons") or []),
        "handoff": state,
    }


def rows_agree(a, b):
    """A row agrees on kind + outcomeId + reasons(set) + handoff, or on the same
    class of refusal. Error codes are recorded but not required to match: the
    two vocabularies are implementation-defined, since Core 0.1.0-draft has no
    evaluation-error contract."""
    if a is None or b is None:
        return False
    if "error" in a or "error" in b:
        return ("error" in a and "error" in b
                and a["error"] == b["error"] and a["error"] != "other")
    return a == b


EXPECTED = {
    "outcome:cond-true": {"kind": "outcome", "outcomeId": "cond-true", "reasons": []},
    "outcome:cond-false": {"kind": "outcome", "outcomeId": "cond-false", "reasons": []},
    "unresolved:unknown": {"kind": "unresolved", "outcomeId": None, "reasons": ["unknown"]},
    "error:structural-refusal": {"error": "structural-refusal"},
    "error:resource-limit": {"error": "resource-limit"},
}


def meets_expectation(observed, expectation):
    """Compare an observed normalized result with the RFC's pinned expectation.
    Handoff is deliberately excluded: RFC 0006's disposition sketch pins the
    member but not its serialization, and RFC 0008 pins condition values rather
    than handoff configuration."""
    want = EXPECTED.get(expectation)
    if want is None:
        return None  # 'unpinned' or an unrecognized expectation string
    if observed is None:
        return False
    if "error" in want:
        return observed.get("error") == want["error"]
    if "error" in observed:
        return False
    return all(observed.get(k) == v for k, v in want.items())


def run_cases(args):
    cases = json.load(open(args.cases))
    results, agree = [], 0
    for case in cases:
        facts = (RawJSON(case["facts_raw"]) if case.get("facts_raw") is not None
                 else case["facts"])
        go = normalize(run_go(args.go_binary, case["pack"], facts,
                              case.get("evidence")))
        py = normalize(run_py(args.python_repo, case["pack"], facts,
                              case.get("evidence")))
        ok = rows_agree(go, py)
        agree += bool(ok)
        expectation = case.get("rfc_expectation", "unpinned")
        go_meets = meets_expectation(go, expectation)
        py_meets = meets_expectation(py, expectation)
        if not ok:
            # A divergence on a row the RFC does not pin is a finding about the
            # RFC, not about either implementation: it is reported and does not
            # fail the run.
            verdict = "divergent-unpinned" if expectation == "unpinned" else "DIVERGENT"
        elif go_meets is None:
            verdict = "agree-unpinned"
        elif go_meets and py_meets:
            verdict = "matches-rfc"
        else:
            verdict = "AGREE-OFF-EXPECTATION"
        results.append({"name": case["name"], "go": go, "python": py,
                        "agree": bool(ok), "rfc_expectation": expectation,
                        "verdict": verdict, "note": case.get("note")})
        print("%-9s %-56s go=%s py=%s" % (
            "AGREE" if ok else "DIVERGE", case["name"],
            json.dumps(go, sort_keys=True), json.dumps(py, sort_keys=True)))
    diverged = [r["name"] for r in results if r["verdict"] == "DIVERGENT"]
    unpinned = [r["name"] for r in results if r["verdict"] == "divergent-unpinned"]
    off = [r["name"] for r in results if r["verdict"] == "AGREE-OFF-EXPECTATION"]
    print("\n%d/%d rows agree." % (agree, len(results)))
    print("divergences on pinned rows: %s" % (diverged or "none"))
    print("divergences on rows the RFC leaves unpinned: %s" % (unpinned or "none"))
    print("agree-but-off-RFC-expectation: %s" % (off or "none"))
    if args.json_out:
        json.dump({"mode": "cases", "rows": results,
                   "total": len(results), "agree": agree,
                   "divergences": diverged, "unpinned_divergences": unpinned,
                   "off_expectation": off},
                  open(args.json_out, "w"), indent=1)
    return 0 if not diverged and not off else 1


def run_equivalence(args):
    root = args.equivalence_dir
    manifest = json.load(open(os.path.join(root, "manifest.json")))
    results, mismatches = [], []
    for room in manifest:
        original = json.load(open(os.path.join(root, room["original_pack"])))
        twin = json.load(open(os.path.join(root, room["twin_pack"])))
        for scenario in room["scenarios"]:
            evidence = None
            if scenario.get("evidence"):
                evidence = json.load(open(os.path.join(root, scenario["evidence"])))
            of = json.load(open(os.path.join(root, scenario["original_facts"])))
            tf = json.load(open(os.path.join(root, scenario["twin_facts"])))
            cell = {
                "go_original": normalize(run_go(args.go_binary, original, of, evidence)),
                "py_original": normalize(run_py(args.python_repo, original, of, evidence)),
                "go_twin": normalize(run_go(args.go_binary, twin, tf, evidence)),
                "py_twin": normalize(run_py(args.python_repo, twin, tf, evidence)),
            }
            equal = (cell["go_original"] == cell["py_original"] ==
                     cell["go_twin"] == cell["py_twin"])
            row = {"room": room["room"], "fact": room["fact"],
                   "operator": room["operator"], "scenario": scenario["name"],
                   "equivalent": equal}
            row.update(cell)
            results.append(row)
            if not equal:
                mismatches.append("%s/%s" % (room["room"], scenario["name"]))
            print("%-6s %-8s %-22s %s" % (
                "EQUIV" if equal else "DIFFER", room["room"], scenario["name"],
                json.dumps(cell["go_original"], sort_keys=True)))
            if not equal:
                for key in ("go_original", "py_original", "go_twin", "py_twin"):
                    print("    %-12s %s" % (key, json.dumps(cell[key], sort_keys=True)))
    print("\n%d/%d room-scenario pairs equivalent across both implementations."
          % (len(results) - len(mismatches), len(results)))
    if args.json_out:
        json.dump({"mode": "equivalence", "rows": results,
                   "mismatches": mismatches}, open(args.json_out, "w"), indent=1)
    return 0 if not mismatches else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    c = sub.add_parser("cases", help="run the RFC 0008 Conformance-section corpus")
    c.add_argument("go_binary")
    c.add_argument("python_repo")
    c.add_argument("cases")
    c.add_argument("--json-out")
    c.set_defaults(func=run_cases)

    e = sub.add_parser("equivalence", help="run the census prepared-boolean/quantifier check")
    e.add_argument("go_binary")
    e.add_argument("python_repo")
    e.add_argument("equivalence_dir")
    e.add_argument("--json-out")
    e.set_defaults(func=run_equivalence)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
