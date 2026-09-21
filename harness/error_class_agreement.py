#!/usr/bin/env python3
"""Cross-implementation agreement on Core §8.4 evaluation-error classes.

`class_agreement.py` compares dispositions and treats any error as a non-result, so it says
nothing about WHICH error two implementations report. §8.4 fixes four classes and one order
between them "so that two conforming implementations report the same class for the same
inputs"; this driver checks exactly that.

The rows are the specification's STAGED evaluation rows (RFC 0013), vendored under
reference/conformance-evaluation-staged/. They are in no corpus: no `suiteVersion` contains
them, and nothing here is a corpus result or evidence for a §3.4.1 claim. Each row is run
through BOTH implementations and three things are compared — the Go class, the Python class,
and the class the row expects — because a staged row may itself be the thing that is wrong.
A divergence is adjudicated against the TEXT, never by preferring an implementation or a row.

A row passes only if both implementations refuse (§8.4: an error MUST NOT come with a
disposition), report the same class, and that class is the row's. The phase each reports is
printed and never compared to an expectation: §8.4 requires a class, not a phase, and the
staged rows assert none.

Usage: error_class_agreement.py <go-binary> <python-repo-dir>
"""
import json
import os
import subprocess
import sys
import tempfile

STAGED = os.path.join("reference", "conformance-evaluation-staged")


def _object(text):
    try:
        payload = json.loads(text)
    except (TypeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def report_of(result_text, error_text, error_member):
    """What one implementation said: (kind, class, phase).

    kind is "error" (an error envelope with a class), "disposition" (a result was emitted),
    "both" (an error AND a disposition, which §8.4 forbids), or "unparsed".

    §8.4 fixes the class identifier and deliberately leaves "the transport, exit status, and wire
    format of an evaluation error" undefined, and the two implementations differ on all three: the
    Go runtime writes an `evaluationError` member to stdout, the Python evaluator writes an `error`
    member to stderr. So the caller says where a result would be (`result_text`), where an error
    would be (`error_text`) and what the error member is called. Only the class is compared.
    """
    error = _object(error_text).get(error_member)
    has_error = isinstance(error, dict) and isinstance(error.get("class"), str)
    has_disposition = _object(result_text).get("disposition") is not None
    if has_error and has_disposition:
        return ("both", error["class"], error.get("phase"))
    if has_error:
        return ("error", error["class"], error.get("phase"))
    if has_disposition:
        return ("disposition", None, None)
    return ("unparsed", None, None)


def verdict(expected, go, py):
    """Why a row fails, or None if it passes. `go` and `py` are report_of() results."""
    for name, (kind, _, _) in (("go", go), ("py", py)):
        if kind == "disposition":
            return f"{name} emitted a disposition where §8.4 requires an error"
        if kind == "both":
            return f"{name} emitted a disposition together with an error, which §8.4 forbids"
        if kind != "error":
            return f"{name} output could not be read as an evaluation error"
    if go[1] != py[1]:
        return "the implementations report different classes"
    if go[1] != expected:
        return "both implementations agree with each other and not with the row"
    return None


def run_case(gobin, pyrepo, base, case):
    pack = os.path.join(base, case["pack"])
    temporary = []

    def write(value):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(value, handle)
        temporary.append(handle.name)
        return handle.name

    try:
        facts = write(case["facts"])
        goargs = [gobin, "experimental", "evaluate", pack, "--facts", facts, "--format", "json"]
        pyargs = [sys.executable, "-m", "jps_evaluator", "--pack", pack, "--facts", facts]
        if case.get("evidenceAvailability") is not None:
            evidence = write(case["evidenceAvailability"])
            goargs += ["--evidence", evidence]
            pyargs += ["--evidence", evidence]
        for extension in case.get("supportedExtensions", []):
            goargs += ["--supported-extension", extension]
            pyargs += ["--supported-extension", extension]
        # Run from a directory with no project configuration, so neither implementation reads
        # one or appends an audit record on account of where the harness happens to be run.
        with tempfile.TemporaryDirectory() as empty:
            g = subprocess.run(goargs, capture_output=True, text=True, timeout=60, cwd=empty)
        p = subprocess.run(pyargs, capture_output=True, text=True, timeout=60, cwd=pyrepo)
    finally:
        for path in temporary:
            os.unlink(path)
    return (
        report_of(g.stdout, g.stdout, "evaluationError"),
        report_of(p.stdout, p.stderr, "error"),
    )


def main():
    gobin, pyrepo = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.join(root, STAGED)
    with open(os.path.join(base, "cases.json")) as handle:
        staged = json.load(handle)
    if staged.get("status") != "staged" or "suiteVersion" in staged:
        raise SystemExit("reference rows are not a staged file; refusing to treat a corpus as one")

    failures = 0
    for case in staged["cases"]:
        expected = case.get("expectedErrorClass")
        if expected is None:
            raise SystemExit(f"{case['id']} expects no error class; this driver is for those that do")
        go, py = run_case(gobin, pyrepo, base, case)
        why = verdict(expected, go, py)
        failures += why is not None
        print(f"{'DIFF ' if why else 'AGREE'} {case['id']}")
        print(f"        row={expected}  go={go[1]} ({go[2]})  py={py[1]} ({py[2]})")
        if why:
            print(f"        {why}")
    total = len(staged["cases"])
    print(f"\n{total - failures}/{total} staged rows: both implementations refuse, agree on the class, "
          "and agree with the row")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
