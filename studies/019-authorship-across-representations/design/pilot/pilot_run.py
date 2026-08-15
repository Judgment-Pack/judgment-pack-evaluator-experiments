#!/usr/bin/env python3
"""Study 019 CALIBRATION-PILOT DRIVER -- DESIGN-TIME, NON-CITABLE HARNESS-VALIDATION TOOLING.

    THIS IS NOT THE REGISTERED STUDY HARNESS.

    It exists to (a) validate that the marker/extraction/admission/evaluation path works
    end to end before anything is registered, and (b) drive the labelled, non-citable
    calibration pilots of BRIEF.md 4.2. It deliberately does NOT implement:
      * golden-context capture (two agreeing probes + isolation negative control),
      * transcript / isolation proof, binary-digest refusal, PINS.json anchoring,
      * the ITT population partition, E2's ordered Core 8.4 drop-code table in full,
        E3/E4/E5, or exact interval arithmetic.
    Those arrive with the ported Study 012 machinery at preregistration time. No number
    this script prints may be cited in the preregistration or in any result document
    except as a pilot rate explicitly labelled non-citable (BRIEF.md 4.2 step 3).

Subcommands
-----------
  call   one sequential authoring call to the operator's codex CLI, prompt on stdin
  score  extract -> admit -> evaluate -> score every run directory of one arm

Stdlib only. Python 3.8+.

Registered-at-design-time conventions this script implements (see
design/prompts/PROMPT-NOTES.md and design/prompts/ARM-*-INSTRUCTIONS.md):

  marker rule   arm A: the LAST line that is exactly `PACK:` followed (after optional
                blank lines) by a fenced block, and likewise `MATRIX:`.
                arms B/C: `POLICY:` and `TESTS:`. The fence info string may be the
                expected language (`json` / `rego`) or empty.
  admission     arm A: JSON parse, then `jpack spec validate --format json`, reading the
                payload's `status` (never the exit code).
                arms B/C: `opa check --strict --capabilities <caps>`.
                No repair of any kind, ever. Ordered drop codes:
                    1 no-marker  2 unparseable  3 invalid-artifact
                arm A: JSON parse failure -> unparseable; `status != "valid"` ->
                invalid-artifact (diagnostic CODES recorded, never message prose).
                arms B/C: an all-`rego_parse_error` check failure -> unparseable; every
                other check error (type / compile / capability) -> invalid-artifact.
  evaluation    every row of design/gold/gold.json, both engines invoked exactly as the
                reference build invoked them (arm A: facts+evidence documents, decimal
                strings; arms B/C: input document rendered TEXTUALLY so the canonical
                decimal strings appear as exact JSON numbers).
  scoring       a run is `perfect` iff it was admitted and agreed with gold on every row.
                A row-level engine error/undefined is a ROW FAILURE with its class
                recorded -- it never crashes the scorer and never drops the run.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, ".."))
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"

JPACK = os.environ.get("JPACK_BIN", os.path.join(SCRATCH, "pins", "jpack", "jpack"))
OPA = os.environ.get("OPA_BIN", os.path.join(SCRATCH, "pins", "opa", "opa_linux_amd64_static"))
CAPS = os.environ.get("OPA_CAPS", os.path.join(SCRATCH, "pins", "opa", "caps-filtered.json"))
GOLD = os.environ.get("GOLD_JSON", os.path.join(DESIGN, "gold", "gold.json"))

CODEX_ARGV = [
    "codex", "exec",
    "--skip-git-repo-check",
    "--sandbox", "read-only",
    "--color", "never",
    "-c", "mcp_servers={}",
    "-",                      # read the prompt from stdin
]

ENGINE_TIMEOUT_S = 60

# arm -> (scored marker, scored language, secondary marker, secondary language)
ARM_MARKERS = {
    "A": ("PACK", "json", "MATRIX", "json"),
    "B": ("POLICY", "rego", "TESTS", "rego"),
    "C": ("POLICY", "rego", "TESTS", "rego"),
}

DROP_ORDER = ["no-marker", "unparseable", "invalid-artifact"]

# gold input key -> (facts member, wire kind)
VENDOR_FIELDS = [
    ("risk", "riskScore", "number"),
    ("spend", "requestedSpend", "number"),
    ("sanctions", "sanctionsStatus", "string"),
    ("country", "countryRisk", "string"),
    ("newVendor", "newVendor", "string"),
    ("critical", "criticalSupplier", "string"),
    ("prior", "priorEnforcement", "string"),
]
EVIDENCE_FIELDS = [("finEvidence", "financial-evidence"), ("insurance", "insurance-certificate")]


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def run_dir_name(slot):
    return "run-%s" % str(slot).zfill(3)


# --------------------------------------------------------------------------- call


def cmd_call(args):
    arm = args.arm.upper()
    with open(args.prompt_file, "rb") as fh:
        prompt = fh.read()
    outdir = os.path.join(args.outdir, "arm-%s" % arm, run_dir_name(args.slot))
    if os.path.exists(outdir) and not args.overwrite:
        print("refusing to overwrite existing run directory: %s" % outdir, file=sys.stderr)
        return 2
    os.makedirs(outdir, exist_ok=True)

    started = now_iso()
    t0 = datetime.datetime.now(datetime.timezone.utc)
    try:
        proc = subprocess.run(
            CODEX_ARGV, input=prompt, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=args.timeout,
        )
        stdout, stderr, rc, timed_out = proc.stdout, proc.stderr, proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or b""
        stderr = (exc.stderr or b"") + b"\n[pilot_run] TIMEOUT after %ds\n" % args.timeout
        rc, timed_out = 124, True
    except FileNotFoundError as exc:
        print("codex CLI not found on PATH: %s" % exc, file=sys.stderr)
        return 3
    t1 = datetime.datetime.now(datetime.timezone.utc)

    with open(os.path.join(outdir, "completion.txt"), "wb") as fh:
        fh.write(stdout)
    with open(os.path.join(outdir, "stderr.txt"), "wb") as fh:
        fh.write(stderr)
    with open(os.path.join(outdir, "exit.txt"), "w") as fh:
        fh.write("%d\n" % rc)

    call = {
        "harness": "pilot_run.py (design-time, non-citable)",
        "arm": arm,
        "slot": str(args.slot).zfill(3),
        "argv": CODEX_ARGV,
        "promptFile": os.path.abspath(args.prompt_file),
        "promptSha256": sha256_bytes(prompt),
        "promptBytes": len(prompt),
        "completionSha256": sha256_bytes(stdout),
        "completionBytes": len(stdout),
        "startedAt": started,
        "endedAt": now_iso(),
        "durationSeconds": round((t1 - t0).total_seconds(), 3),
        "exitCode": rc,
        "timedOut": timed_out,
    }
    with open(os.path.join(outdir, "CALL.json"), "w") as fh:
        json.dump(call, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("arm=%s slot=%s exit=%d bytes=%d dur=%.1fs -> %s"
          % (arm, call["slot"], rc, len(stdout), call["durationSeconds"], outdir))
    return 0 if rc == 0 else 1


# ------------------------------------------------------------------------ extract


FENCE_RE = re.compile(r"^\s*```([A-Za-z0-9_+-]*)\s*$")


def extract_block(text, marker, lang):
    """Return (block_text, None) or (None, reason). Registered rule: the LAST line equal to
    `<marker>:` that is followed, after optional blank lines, by a fenced block whose info
    string is `lang` or empty. The block ends at the next closing fence."""
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.strip() == marker + ":"]
    for idx in reversed(starts):
        j = idx + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        if j >= len(lines):
            continue
        m = FENCE_RE.match(lines[j])
        if not m:
            continue
        info = m.group(1).lower()
        if info not in ("", lang):
            continue
        body = []
        k = j + 1
        closed = False
        while k < len(lines):
            if lines[k].strip() == "```":      # closing fence
                closed = True
                break
            body.append(lines[k])
            k += 1
        if not closed:
            continue
        return "\n".join(body) + "\n", None
    return None, "no-marker"


# ------------------------------------------------------------------------- admit


def jpack_json(argv, cwd=None, env=None):
    """Run a jpack command and return (payload_or_None, rc, raw_stdout, raw_stderr)."""
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=ENGINE_TIMEOUT_S, cwd=cwd, env=env)
    except subprocess.TimeoutExpired:
        return None, 124, "", "timeout"
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    try:
        return json.loads(out), p.returncode, out, err
    except Exception:
        return None, p.returncode, out, err


def clean_env(home):
    """Minimal environment: no inherited JPACK_CONFIG, TZ pinned to UTC."""
    return {
        "PATH": "/usr/bin:/bin",
        "TZ": "UTC",
        "HOME": home,
        "TMPDIR": home,
    }


def admit_arm_a(block, workdir):
    """-> (pack_path or None, dropCode or None, detail dict)"""
    detail = {}
    try:
        json.loads(block)
    except Exception as exc:
        detail["parseError"] = repr(exc)
        return None, "unparseable", detail
    path = os.path.join(workdir, "pack.json")
    with open(path, "w") as fh:
        fh.write(block)
    payload, rc, out, err = jpack_json(
        [JPACK, "spec", "validate", path, "--format", "json"],
        cwd=workdir, env=clean_env(workdir))
    if payload is None:
        detail["validateStdout"] = out[:2000]
        detail["validateStderr"] = err[:2000]
        detail["validateExit"] = rc
        return None, "invalid-artifact", detail
    detail["validateStatus"] = payload.get("status")
    if payload.get("status") != "valid":
        # codes and pointers only, never message prose
        detail["diagnostics"] = [
            {k: d.get(k) for k in ("code", "layer", "instancePath") if k in d}
            for d in (payload.get("diagnostics") or [])
            if d.get("severity") == "error"
        ][:10]
        detail["failedLayers"] = [
            l.get("name") for l in (payload.get("layers") or []) if l.get("status") == "failed"
        ]
        return None, "invalid-artifact", detail
    return path, None, detail


def admit_arm_rego(block, workdir):
    detail = {}
    if not block.strip():
        return None, "unparseable", detail
    path = os.path.join(workdir, "policy.rego")
    with open(path, "w") as fh:
        fh.write(block)
    try:
        p = subprocess.run(
            [OPA, "check", "--strict", "--capabilities", CAPS, "--format", "json", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=ENGINE_TIMEOUT_S,
            cwd=workdir, env=clean_env(workdir))
    except subprocess.TimeoutExpired:
        detail["checkExit"] = 124
        return None, "invalid-artifact", detail
    detail["checkExit"] = p.returncode
    if p.returncode != 0:
        # `opa check --format json` writes its error document to stderr.
        codes = []
        for stream in (p.stderr, p.stdout):
            try:
                doc = json.loads(stream.decode("utf-8", "replace"))
            except Exception:
                continue
            codes = sorted({str(e.get("code", "?")) for e in doc.get("errors", [])})
            if codes:
                break
        detail["checkErrorCodes"] = codes or ["unparseable-check-output"]
        # Parse failures are the Rego counterpart of arm A's JSON parse failure; every
        # other check error (type/compile/capability) is the counterpart of a
        # schema-invalid pack. Ordered: unparseable before invalid-artifact.
        if codes and all(c == "rego_parse_error" for c in codes):
            return None, "unparseable", detail
        return None, "invalid-artifact", detail
    return path, None, detail


# ---------------------------------------------------------------------- evaluate


def facts_documents(inputs):
    vendor = {}
    for src, member, _kind in VENDOR_FIELDS:
        if inputs.get(src) is not None:
            vendor[member] = inputs[src]
    evidence = {}
    for src, member in EVIDENCE_FIELDS:
        if inputs.get(src) is not None:
            evidence[member] = inputs[src]
    return {"vendor": vendor}, evidence


def render_rego_input(inputs):
    """Build the input document TEXTUALLY: riskScore / requestedSpend are spliced from the
    canonical decimal strings so OPA parses them as exact JSON numbers (no float
    round-trip anywhere)."""
    vend = []
    for src, member, kind in VENDOR_FIELDS:
        val = inputs.get(src)
        if val is None:
            continue                     # omitted member = unreadable / unreported
        vend.append('"%s": %s' % (member, val if kind == "number" else json.dumps(val)))
    ev = []
    for src, member in EVIDENCE_FIELDS:
        val = inputs.get(src)
        if val is None:
            continue
        ev.append('"%s": %s' % (member, json.dumps(val)))
    return '{"vendor": {%s}, "evidence": {%s}}\n' % (", ".join(vend), ", ".join(ev))


def eval_arm_a(pack_path, inputs, workdir):
    """-> (disposition, sorted_reasons) or ('ROW-ERROR', [class])."""
    facts, evidence = facts_documents(inputs)
    fpath = os.path.join(workdir, "facts.json")
    epath = os.path.join(workdir, "evidence.json")
    with open(fpath, "w") as fh:
        json.dump(facts, fh)
    with open(epath, "w") as fh:
        json.dump(evidence, fh)
    # cwd is a scratch directory containing no jpack.json, and JPACK_CONFIG is not inherited
    payload, rc, out, err = jpack_json(
        [JPACK, "experimental", "evaluate", pack_path,
         "--facts", fpath, "--evidence", epath, "--format", "json"],
        cwd=workdir, env=clean_env(workdir))
    if payload is None:
        return "ROW-ERROR", ["non-json-payload" if rc != 124 else "engine-timeout"]
    if payload.get("status") != "evaluated":
        err_obj = payload.get("error") or {}
        cls = err_obj.get("class") or payload.get("errorClass") or payload.get("status") or "refused"
        return "ROW-ERROR", [str(cls)]
    disp = payload.get("disposition") or {}
    kind = disp.get("kind")
    if kind == "outcome":
        return disp.get("outcomeId"), []
    if kind == "unresolved":
        reasons = disp.get("reasons") or []
        return "unresolved", sorted(str(r) for r in reasons)
    return "ROW-ERROR", ["unexpected-kind:%s" % kind]


def eval_arm_rego(policy_path, inputs, workdir):
    ipath = os.path.join(workdir, "input.json")
    with open(ipath, "w") as fh:
        fh.write(render_rego_input(inputs))
    try:
        p = subprocess.run(
            [OPA, "eval", "--format", "json", "--fail", "--strict-builtin-errors",
             "--capabilities", CAPS, "--timeout", "10s",
             "--data", policy_path, "--input", ipath, "data.study.decision"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=ENGINE_TIMEOUT_S,
            cwd=workdir, env=clean_env(workdir))
    except subprocess.TimeoutExpired:
        return "ROW-ERROR", ["engine-timeout"]
    out = p.stdout.decode("utf-8", "replace")
    try:
        doc = json.loads(out)
    except Exception:
        return "ROW-ERROR", ["non-json-payload"]
    if isinstance(doc, dict) and doc.get("errors"):
        codes = sorted({str(e.get("code", "?")) for e in doc["errors"]})
        return "ROW-ERROR", codes            # codes only, never message prose
    try:
        value = doc["result"][0]["expressions"][0]["value"]
    except Exception:
        return "ROW-ERROR", ["undefined"]
    if not isinstance(value, dict) or "disposition" not in value:
        return "ROW-ERROR", ["contract-shape"]
    disp = value.get("disposition")
    reasons = value.get("reasons", [])
    if not isinstance(disp, str) or not isinstance(reasons, list) \
            or not all(isinstance(r, str) for r in reasons):
        return "ROW-ERROR", ["contract-shape"]
    return disp, sorted(reasons)


# ------------------------------------------------------------------------- score


def score_run(arm, run_path, rows, scratch_root):
    slot = os.path.basename(run_path).split("-", 1)[1]
    rec = {"slot": slot, "perfect": False, "rowFailures": []}
    comp_path = os.path.join(run_path, "completion.txt")
    if not os.path.exists(comp_path):
        rec["dropCode"] = "no-marker"
        rec["detail"] = {"note": "no completion.txt"}
        return rec
    with open(comp_path, "rb") as fh:
        text = fh.read().decode("utf-8", "replace")

    marker, lang, sec_marker, sec_lang = ARM_MARKERS[arm]
    block, why = extract_block(text, marker, lang)
    sec_block, _sec_why = extract_block(text, sec_marker, sec_lang)
    rec["secondaryArtifact"] = {
        "marker": sec_marker,
        "present": sec_block is not None,
        "bytes": len(sec_block or ""),
    }
    if block is None:
        rec["dropCode"] = why
        return rec

    workdir = tempfile.mkdtemp(prefix="pilot-%s-%s-" % (arm, slot), dir=scratch_root)
    try:
        if arm == "A":
            art, drop, detail = admit_arm_a(block, workdir)
        else:
            art, drop, detail = admit_arm_rego(block, workdir)
        rec["detail"] = detail
        if sec_block is not None:
            with open(os.path.join(run_path, "secondary.%s" % sec_lang), "w") as fh:
                fh.write(sec_block)
        if drop is not None:
            rec["dropCode"] = drop
            return rec
        with open(os.path.join(run_path, "artifact.%s" % lang), "w") as fh:
            fh.write(block)

        failures = []
        errors_by_class = {}
        for row in rows:
            want = (row["expect"]["disposition"], sorted(row["expect"]["reasons"]))
            rowdir = os.path.join(workdir, "row")
            os.makedirs(rowdir, exist_ok=True)
            try:
                if arm == "A":
                    got = eval_arm_a(art, row["inputs"], rowdir)
                else:
                    got = eval_arm_rego(art, row["inputs"], rowdir)
            except Exception as exc:                      # never crash the scorer
                got = ("ROW-ERROR", ["scorer-exception:%s" % type(exc).__name__])
            if got[0] == "ROW-ERROR":
                for c in got[1]:
                    errors_by_class[c] = errors_by_class.get(c, 0) + 1
            if list(got) != list(want):
                failures.append({
                    "id": row["id"],
                    "cite": row.get("cite", []),
                    "expected": {"disposition": want[0], "reasons": want[1]},
                    "got": {"disposition": got[0], "reasons": got[1]},
                })
        rec["rowFailures"] = failures
        rec["rowsEvaluated"] = len(rows)
        if errors_by_class:
            rec["rowErrorClasses"] = errors_by_class
        rec["perfect"] = not failures
        return rec
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def cmd_score(args):
    arm = args.arm.upper()
    with open(args.gold) as fh:
        gold = json.load(fh)
    rows = gold["rows"]
    armdir = os.path.join(args.outdir, "arm-%s" % arm)
    if not os.path.isdir(armdir):
        print("no such arm directory: %s" % armdir, file=sys.stderr)
        return 2
    run_paths = sorted(
        os.path.join(armdir, d) for d in os.listdir(armdir)
        if d.startswith("run-") and os.path.isdir(os.path.join(armdir, d)))

    scratch_root = args.scratch or tempfile.gettempdir()
    os.makedirs(scratch_root, exist_ok=True)
    per_run = [score_run(arm, p, rows, scratch_root) for p in run_paths]

    admitted = sum(1 for r in per_run if "dropCode" not in r)
    perfect = sum(1 for r in per_run if r["perfect"])
    drops = {}
    for r in per_run:
        if "dropCode" in r:
            drops[r["dropCode"]] = drops.get(r["dropCode"], 0) + 1
    score = {
        "harness": "pilot_run.py (design-time, non-citable)",
        "arm": arm,
        "generatedAt": now_iso(),
        "goldVersion": gold.get("goldVersion"),
        "goldPolicy": gold.get("policy"),
        "goldRows": len(rows),
        "runs": len(per_run),
        "admitted": admitted,
        "perfect": perfect,
        "dropCodes": {c: drops.get(c, 0) for c in DROP_ORDER},
        "perRun": per_run,
    }
    with open(os.path.join(armdir, "SCORE.json"), "w") as fh:
        json.dump(score, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("arm=%s runs=%d admitted=%d perfect=%d drops={%s} rows=%d  [NON-CITABLE PILOT]"
          % (arm, len(per_run), admitted, perfect,
             ", ".join("%s:%d" % (c, drops.get(c, 0)) for c in DROP_ORDER), len(rows)))
    return 0


# -------------------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Study 019 calibration-pilot driver (DESIGN-TIME, NON-CITABLE).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("call", help="one sequential authoring call")
    c.add_argument("--arm", required=True, choices=list("ABCabc"))
    c.add_argument("--slot", required=True)
    c.add_argument("--prompt-file", required=True)
    c.add_argument("--outdir", required=True)
    c.add_argument("--timeout", type=int, default=900)
    c.add_argument("--overwrite", action="store_true")
    c.set_defaults(func=cmd_call)

    s = sub.add_parser("score", help="score every run directory of one arm")
    s.add_argument("--arm", required=True, choices=list("ABCabc"))
    s.add_argument("--outdir", required=True)
    s.add_argument("--gold", default=GOLD)
    s.add_argument("--scratch", default=None)
    s.set_defaults(func=cmd_score)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
