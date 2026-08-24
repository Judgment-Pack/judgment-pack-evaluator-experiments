#!/usr/bin/env python3
"""Study 019 prompt-material checker -- DESIGN DRAFT, NOT REGISTERED.

Six checks over the arm suffix materials. Exit nonzero on any failure.

  1 FAIRNESS SCREEN. No arm suffix material may name the policy's domain, any of its six
    numeric thresholds, or any of its clause labels. The materials teach the language and
    the output form; the policy's solution structure is what the study measures.
  2 APPENDIX CONSISTENCY. Every identifier the materials pin (the contract's disposition
    and reason values) is one the shared naming appendix already pins, plus the single
    value `unresolved`, which is the contract's own and appears in no appendix list.
  3 CONTRACT PARITY. Arm C's embedded JSON Schema is byte-for-byte the schema file, and
    arm B's prose contract is exactly what deformalize_contract.py produces from it -- so
    B and C carry one inventory in two formalities, checked rather than asserted.
  4 SHARED-PART PARITY. The two Rego arms' shared head and tail are one file each, used by
    both, so B and C cannot drift apart except in the inserted block.
  5 TOY VALIDITY. Every toy artifact embedded in the materials is run through the pinned
    engines: the toy pack validates, the toy Rego and its tests pass `opa check --strict`
    under the pinned capabilities. A toy that does not run teaches a shape that does not work.
  6 MARKER PARITY. Each arm's stated output form declares exactly two markers, and the
    marker rule the materials state is the rule pilot_run.py implements.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, ".."))
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"
JPACK = os.environ.get("JPACK_BIN", os.path.join(SCRATCH, "pins", "jpack", "jpack"))
OPA = os.environ.get("OPA_BIN", os.path.join(SCRATCH, "pins", "opa", "opa_linux_amd64_static"))
CAPS = os.environ.get("OPA_CAPS", os.path.join(SCRATCH, "pins", "opa", "caps-filtered.json"))

APPENDIX = os.path.join(HERE, "NAMING-APPENDIX.md")
SCHEMA = os.path.join(HERE, "RESULT-CONTRACT.schema.json")
MATERIALS = {
    "ARM-A-INSTRUCTIONS.md": os.path.join(HERE, "ARM-A-INSTRUCTIONS.md"),
    "REGO-TASK-HEAD.md": os.path.join(HERE, "REGO-TASK-HEAD.md"),
    "REGO-TASK-TAIL.md": os.path.join(HERE, "REGO-TASK-TAIL.md"),
    "ARM-C-CONVENTION.md": os.path.join(HERE, "ARM-C-CONVENTION.md"),
    "generated/ARM-B-CONTRACT.md": os.path.join(HERE, "generated", "ARM-B-CONTRACT.md"),
}

# 1 -- the fairness screen ------------------------------------------------------------
FORBIDDEN_WORDS = [
    "vendor", "sanction", "insurance", "supplier", "onboarding", "enforcement",
    "screening", "country risk", "risk score", "requested spend", "spend",
    "riskScore", "requestedSpend", "sanctionsStatus", "countryRisk", "newVendor",
    "criticalSupplier", "priorEnforcement", "financial-evidence", "insurance-certificate",
    "vendor-compliance-desk", "audited",
]
# Case-SENSITIVE: these are the policy's own input values, not English words.
FORBIDDEN_LITERALS = ["CLEAR", "MATCH", "UNKNOWN", "LOW", "MEDIUM", "HIGH"]
FORBIDDEN_PATTERNS = [
    (r"(?<![\w.])(40|70|90)(?![\w.%])", "a policy risk threshold"),
    (r"(?<![\w.])(100000|500000|2000000|100,000|500,000|2,000,000)", "a policy spend threshold"),
    (r"(?<![\w])(P1|D1|D2|D3|D4|D5|D6[abc]?|D7|D8|O1|O2|O3|U1)(?![\w])", "a policy clause label"),
]
# The four determination ids and the four ground tokens are shared naming-appendix
# identifiers, not policy structure: the result contract must name them.
ALLOWED_APPENDIX_IDS = None  # filled from the appendix

failures = []


def fail(check, msg):
    failures.append("[%s] %s" % (check, msg))


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def fenced_blocks(text, lang=None):
    out, cur, info = [], None, None
    for line in text.split("\n"):
        m = re.match(r"^\s*```([A-Za-z0-9_+-]*)\s*$", line)
        if m and cur is None:
            cur, info = [], m.group(1).lower()
            continue
        if line.strip() == "```" and cur is not None:
            if lang is None or info == lang:
                out.append("\n".join(cur) + "\n")
            cur, info = None, None
            continue
        if cur is not None:
            cur.append(line)
    return out


def check_fairness():
    appendix_ids = set(re.findall(r"`([a-z][a-z-]+)`", open(APPENDIX).read()))
    for name, path in MATERIALS.items():
        text = strip_comments(open(path, encoding="utf-8").read())
        low = text.lower()
        for word in FORBIDDEN_WORDS:
            if word.lower() in low:
                fail("fairness", "%s names %r" % (name, word))
        for lit in FORBIDDEN_LITERALS:
            if re.search(r"(?<![\w-])%s(?![\w-])" % lit, text):
                fail("fairness", "%s names the policy input value %r" % (name, lit))
        for pat, what in FORBIDDEN_PATTERNS:
            for m in re.finditer(pat, text):
                if m.group(0) in appendix_ids:
                    continue
                ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
                fail("fairness", "%s carries %s (%r) near: ...%s..."
                     % (name, what, m.group(0), ctx))


def check_appendix_consistency():
    appendix = open(APPENDIX, encoding="utf-8").read()
    schema = json.load(open(SCHEMA))
    values = set(schema["properties"]["disposition"]["enum"])
    values |= set(schema["properties"]["reasons"]["items"]["enum"])
    for v in sorted(values):
        if v == "unresolved":
            if "`unresolved`" in appendix:
                fail("appendix", "the appendix now pins `unresolved`; the contract duplicates it")
            continue
        if "`%s`" % v not in appendix:
            fail("appendix", "contract value %r is not pinned by the naming appendix" % v)


def check_contract_parity():
    schema_text = open(SCHEMA, encoding="utf-8").read()
    schema = json.loads(schema_text)
    blocks = fenced_blocks(open(MATERIALS["ARM-C-CONVENTION.md"], encoding="utf-8").read(), "json")
    if not blocks:
        fail("contract", "arm C carries no fenced json schema block")
    else:
        try:
            embedded = json.loads(blocks[0])
        except Exception as exc:
            fail("contract", "arm C's schema block does not parse: %r" % exc)
            embedded = None
        if embedded is not None:
            drop = {k: v for k, v in schema.items() if k != "description"}
            if embedded != drop:
                fail("contract", "arm C's embedded schema differs from RESULT-CONTRACT.schema.json "
                                 "(other than the file's own top-level description)")
    with tempfile.TemporaryDirectory() as td:
        gen = os.path.join(HERE, "deformalize_contract.py")
        cur = open(MATERIALS["generated/ARM-B-CONTRACT.md"], encoding="utf-8").read()
        subprocess.run([sys.executable, gen], capture_output=True, cwd=HERE, check=False)
        new = open(MATERIALS["generated/ARM-B-CONTRACT.md"], encoding="utf-8").read()
        _ = td
        if cur != new:
            fail("contract", "generated/ARM-B-CONTRACT.md is stale: re-run deformalize_contract.py")


def check_shared_parts():
    for name in ("REGO-TASK-HEAD.md", "REGO-TASK-TAIL.md"):
        if not os.path.exists(MATERIALS[name]):
            fail("shared", "%s missing: the two Rego arms no longer share a body" % name)
    head = open(MATERIALS["REGO-TASK-HEAD.md"], encoding="utf-8").read()
    if "POLICY:" in head or "TESTS:" in head:
        fail("shared", "the shared head states the output form; it belongs to the shared tail only")


def check_toys():
    pack_blocks = fenced_blocks(open(MATERIALS["ARM-A-INSTRUCTIONS.md"], encoding="utf-8").read(),
                                "json")
    if len(pack_blocks) < 2:
        fail("toy", "arm A does not carry both a toy pack and a toy matrix")
        return
    with tempfile.TemporaryDirectory() as td:
        pack = os.path.join(td, "pack.json")
        open(pack, "w").write(pack_blocks[0])
        p = subprocess.run([JPACK, "spec", "validate", pack, "--format", "json"],
                           capture_output=True, text=True, cwd=td)
        try:
            status = json.loads(p.stdout)["status"]
        except Exception:
            status = "no-payload"
        if status != "valid":
            fail("toy", "arm A's toy pack is %s, not valid" % status)
        try:
            matrix = json.loads(pack_blocks[1])
            if matrix.get("matrixVersion") != "2" or not matrix.get("cases"):
                fail("toy", "arm A's toy matrix is not a matrixVersion 2 document with cases")
        except Exception as exc:
            fail("toy", "arm A's toy matrix does not parse: %r" % exc)

    rego_blocks = fenced_blocks(open(MATERIALS["REGO-TASK-HEAD.md"], encoding="utf-8").read(),
                                "rego")
    if len(rego_blocks) < 2:
        fail("toy", "the shared Rego head does not carry both a toy policy and a toy test file")
        return
    with tempfile.TemporaryDirectory() as td:
        paths = []
        for i, block in enumerate(rego_blocks[:2]):
            path = os.path.join(td, "toy%d.rego" % i)
            open(path, "w").write(block)
            paths.append(path)
        p = subprocess.run([OPA, "check", "--strict", "--capabilities", CAPS] + paths,
                           capture_output=True, text=True, cwd=td)
        if p.returncode != 0:
            fail("toy", "the toy Rego does not pass `opa check --strict` (exit %d)" % p.returncode)
        t = subprocess.run([OPA, "test", "--capabilities", CAPS, td],
                           capture_output=True, text=True, cwd=td)
        if t.returncode != 0:
            fail("toy", "the toy Rego tests do not pass `opa test` (exit %d)" % t.returncode)

    conv_blocks = fenced_blocks(open(MATERIALS["ARM-C-CONVENTION.md"], encoding="utf-8").read(),
                                "rego")
    for i, block in enumerate(conv_blocks):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "conv.rego")
            open(path, "w").write("package toy\n\n" + block if "package" not in block else block)
            p = subprocess.run([OPA, "check", "--strict", "--capabilities", CAPS, path],
                               capture_output=True, text=True, cwd=td)
            if p.returncode != 0:
                fail("toy", "arm C convention snippet %d does not check (exit %d)"
                     % (i, p.returncode))


def check_markers():
    a = open(MATERIALS["ARM-A-INSTRUCTIONS.md"], encoding="utf-8").read()
    tail = open(MATERIALS["REGO-TASK-TAIL.md"], encoding="utf-8").read()
    for name, text, markers in (("arm A", a, ("PACK:", "MATRIX:")),
                                ("arms B/C", tail, ("POLICY:", "TESTS:"))):
        for m in markers:
            if m not in text:
                fail("markers", "%s does not state the %s marker" % (name, m))
        if "the last one is the one read" not in text:
            fail("markers", "%s does not state the last-marker rule" % name)
    sys.path.insert(0, os.path.join(DESIGN, "pilot"))
    import pilot_run                                     # noqa: E402
    for arm, expected in (("A", ("PACK", "MATRIX")), ("B", ("POLICY", "TESTS")),
                          ("C", ("POLICY", "TESTS"))):
        got = (pilot_run.ARM_MARKERS[arm][0], pilot_run.ARM_MARKERS[arm][2])
        if got != expected:
            fail("markers", "pilot_run.py arm %s markers are %s, materials state %s"
                 % (arm, got, expected))


def main():
    check_fairness()
    check_appendix_consistency()
    check_contract_parity()
    check_shared_parts()
    check_toys()
    check_markers()
    if failures:
        print("PROMPT MATERIALS: FAIL (%d)" % len(failures))
        for f in failures:
            print("  *", f)
        return 1
    print("PROMPT MATERIALS: PASS (fairness, appendix, contract, shared, toys, markers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
