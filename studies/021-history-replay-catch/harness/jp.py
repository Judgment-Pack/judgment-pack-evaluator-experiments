"""The pinned runtime, and the two things every harness step does with it.

Everything the study executes goes through `jpack` -- a project directory
written for the purpose, the pack under test declared in its jpack.json, and
one of three verbs: `experimental evaluate --rehearsal --format json` (decide
one facts document, record nothing), `packs suggest --write` (derive the
literal-adjacent candidates), `packs test --format json` (replay a matrix and
read the profile). The binary is named by JPACK (default: jpack on PATH); the
scorer pins its digest (harness/PINS.json) and refuses a mismatch.
"""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

JPACK = os.environ.get("JPACK", "jpack")


def binary_digest():
    path = subprocess.run(["sh", "-c", "command -v " + JPACK], capture_output=True, text=True).stdout.strip() or JPACK
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def runtime_version():
    return subprocess.run([JPACK, "version"], capture_output=True, text=True).stdout.strip()


def run(args, cwd, stdin=None, check=True):
    proc = subprocess.run([JPACK] + args, cwd=str(cwd), input=stdin, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError("jpack %s failed (%d): %s" % (" ".join(args), proc.returncode, proc.stderr.strip()[:600]))
    return proc


def project(root, decision_id, pack, matrix=None):
    """Write a minimal configVersion 3 project declaring one pack (and a matrix)."""
    root = Path(root)
    (root / "packs").mkdir(parents=True, exist_ok=True)
    (root / "packs" / "policy.pack.json").write_text(json.dumps(pack, indent=1))
    entry = {"path": "packs/policy.pack.json", "description": decision_id, "expectedVersion": pack["version"]}
    if matrix is not None:
        (root / "packs" / "policy.matrix.json").write_text(json.dumps(matrix, indent=1))
        entry["matrix"] = "packs/policy.matrix.json"
    (root / "jpack.json").write_text(json.dumps({"configVersion": "3", "packs": {decision_id: entry}}, indent=1))
    return root


def decide(root, decision_id, facts, evidence):
    """One rehearsal evaluation: the disposition, or the error class of a refusal."""
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "facts.json"; f.write_text(json.dumps(facts))
        e = Path(tmp) / "evidence.json"; e.write_text(json.dumps(evidence))
        proc = run(["experimental", "evaluate", "--pack-id", decision_id, "--facts", str(f), "--evidence", str(e), "--rehearsal", "--format", "json"], root, check=False)
    if proc.returncode != 0:
        try:
            payload = json.loads(proc.stdout or "{}")
        except ValueError:
            payload = {}
        return {"refused": True, "errorClass": payload.get("errorClass") or payload.get("error", {}).get("class") or proc.stderr.strip()[:200]}
    return {"refused": False, "disposition": json.loads(proc.stdout)["disposition"]}


def suggest(root, decision_id, base_row=None):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "candidates.json"
        args = ["packs", "suggest", "--id", decision_id, "--write", str(out), "--max", "2000"]
        if base_row:
            args += ["--base", base_row]
        run(args, root)
        return json.loads(out.read_text())


def test(root):
    proc = run(["packs", "test", "--format", "json"], root, check=False)
    try:
        return json.loads(proc.stdout)
    except ValueError:
        raise RuntimeError("packs test produced no JSON (%d): %s" % (proc.returncode, proc.stderr.strip()[:400]))
