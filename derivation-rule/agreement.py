"""Agreement harness for the portable derivation rule (SPEC.md, ADR-0002).

Drives two implementations of the *Agreement interface* over the corpus and
diffs their stdout and exit status. Byte-identical output on every case is the
evidence that layer-4 derivation fidelity is a portable, independently
implementable property -- not a private convention of one program, which is the
circularity studies 006/007 could not escape.

Each implementation is a command reading one JSON request on stdin. The
reference is `python3 derive_cli.py`. A second implementation is passed as the
argv command (e.g. a built Go binary). With no second command, the harness runs
the reference against the corpus's frozen `expected` claims instead, so it is
useful even before a second implementation exists.
"""

import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCE = [sys.executable, os.path.join(HERE, "derive_cli.py")]


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _run(command, request):
    proc = subprocess.run(command, input=request, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout


def _load_rule(case):
    # A case's rule is either an inline object or a path relative to this dir.
    if isinstance(case["rule"], dict):
        return case["rule"]
    with open(os.path.join(HERE, case["rule"])) as handle:
        return json.load(handle)


def _cases():
    for path in sorted(glob.glob(os.path.join(HERE, "corpus", "*.json"))):
        with open(path) as handle:
            case = json.load(handle)
        request = _canon({
            "rule": _load_rule(case),
            "artifact": case["artifact"],
            "params": case.get("params", {}),
        })
        yield os.path.basename(path), case, request


def main(argv):
    second = argv[1:] or None
    total = agreed = 0
    failures = []
    for name, case, request in _cases():
        total += 1
        ref_code, ref_out = _run(REFERENCE, request)
        # A case is either an accept case (frozen `expected` claim) or a reject
        # case (`"reject": true` -- both implementations must exit nonzero with
        # empty stdout).
        if case.get("reject"):
            if ref_code == 0 or ref_out != b"":
                failures.append("%s: reference did not reject" % name)
                continue
        else:
            expected = _canon(case["expected"])
            if ref_code != 0 or ref_out != expected:
                failures.append("%s: reference disagrees with frozen corpus" % name)
                continue
        if second is None:
            agreed += 1
            continue
        two_code, two_out = _run(second, request)
        if (two_code == 0) == (ref_code == 0) and two_out == ref_out:
            agreed += 1
        else:
            failures.append(
                "%s: implementations disagree\n    ref  (exit %d): %r\n    other(exit %d): %r"
                % (name, ref_code, ref_out, two_code, two_out)
            )

    label = "reference vs corpus" if second is None else "reference vs %s" % " ".join(second)
    print("%s: %d/%d agreed" % (label, agreed, total))
    for failure in failures:
        print("  DISAGREE " + failure)
    return 0 if agreed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
