"""Pin verification — refuses drifted state before any run and before any count.

Checks (review round 1, findings 2 and 6):
  1. every file in packs/MANIFEST.sha256 and upstream/MANIFEST.sha256 matches
  2. jpack-project/packs/* are byte-identical to packs/*
  3. $JPACK_BIN (when set) matches jpack.binarySha256
  4. mutated packs equal a fresh derivation into a TEMP directory —
     exact filename set and exact bytes; the study tree is never written
  5. goldens/EXPECT-CHECK.json exists and records zero disagreements
  6. the harness interpreter matches harnessPython (series enforced)
  7. $FORGE_VENV_PY (when set): `pip freeze` output matches
     harness/forge-freeze.txt byte-for-byte and its sha256 matches
     forge.pipFreezeSha256
  8. every causal study file matches harness/STUDY-MANIFEST.sha256
     (regenerate with --write-manifest after an intentional change)

Stdlib only. Run: python3 harness/integrity.py   (exit non-zero on any drift)
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent

MANIFEST_GLOBS = [
    "agents/*.py",
    "harness/*.py",
    "harness/PINS.json",
    "harness/forge-freeze.txt",
    "scenarios/jps/cases.json",
    "scenarios/jps/cohort2.yaml",
    "scenarios/jps/fixtures/*.json",
    "scenarios/mutations/MATRIX.json",
    "scenarios/mutations/packs/*.json",
    "goldens/*.json",
    "jpack-project/jpack.json",
    "jpack-project/matrix-*.json",
    "jpack-project/packs/*.json",
    "upstream/*.yaml",
    "upstream/fixtures/*.json",
]
MANIFEST_PATH = STUDY / "harness" / "STUDY-MANIFEST.sha256"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest_files():
    files = set()
    for pattern in MANIFEST_GLOBS:
        files.update(STUDY.glob(pattern))
    files.discard(MANIFEST_PATH)
    return sorted(f for f in files if f.is_file())


def write_manifest():
    lines = ["{}  {}".format(sha256(f), f.relative_to(STUDY)) for f in manifest_files()]
    MANIFEST_PATH.write_text("\n".join(lines) + "\n")
    print("wrote {} entries to {}".format(len(lines), MANIFEST_PATH.relative_to(STUDY)))


def check_manifest(manifest, base):
    errors = []
    for line in manifest.read_text().splitlines():
        digest, name = line.split(None, 1)
        target = base / name.strip()
        if not target.exists():
            errors.append("missing: {}".format(target.relative_to(STUDY)))
        elif sha256(target) != digest:
            errors.append("drifted: {}".format(target.relative_to(STUDY)))
    return errors


def check_study_manifest():
    if not MANIFEST_PATH.exists():
        return ["harness/STUDY-MANIFEST.sha256 missing (run --write-manifest)"]
    errors = check_manifest(MANIFEST_PATH, STUDY)
    listed = {line.split(None, 1)[1].strip() for line in MANIFEST_PATH.read_text().splitlines()}
    actual = {str(f.relative_to(STUDY)) for f in manifest_files()}
    for extra in sorted(actual - listed):
        errors.append("unmanifested causal file: {}".format(extra))
    return errors


def check_mutated_packs():
    errors = []
    committed = STUDY / "scenarios" / "mutations" / "packs"
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, str(STUDY / "harness" / "mutate_packs.py"), "--out", tmp],
            capture_output=True,
        )
        if proc.returncode != 0:
            return ["mutate_packs re-derivation failed: " + proc.stderr.decode()[:200]]
        fresh = {p.name: p.read_bytes() for p in Path(tmp).glob("*.json")}
    existing = {p.name: p.read_bytes() for p in committed.glob("*.json")}
    if set(fresh) != set(existing):
        errors.append("mutated pack set differs from a fresh derivation: {} vs {}".format(
            sorted(fresh), sorted(existing)))
    for name in set(fresh) & set(existing):
        if fresh[name] != existing[name]:
            errors.append("mutated pack drifted from derivation: {}".format(name))
    return errors


def check_python(pins):
    wanted = pins["harnessPython"]
    running = platform.python_version()
    if platform.python_implementation() != wanted["implementation"]:
        return ["interpreter is {} not {}".format(
            platform.python_implementation(), wanted["implementation"])]
    if not running.startswith(wanted["series"] + "."):
        return ["python {} is outside pinned series {}".format(running, wanted["series"])]
    return []


def check_forge_venv(pins):
    venv_python = os.environ.get("FORGE_VENV_PY")
    if not venv_python:
        return []
    proc = subprocess.run([venv_python, "-m", "pip", "freeze"], capture_output=True)
    if proc.returncode != 0:
        return ["pip freeze failed in the Forge venv"]
    frozen = proc.stdout
    digest = hashlib.sha256(frozen).hexdigest()
    errors = []
    if digest != pins["forge"]["pipFreezeSha256"]:
        errors.append("Forge venv freeze digest does not match forge.pipFreezeSha256")
    retained = STUDY / "harness" / "forge-freeze.txt"
    if not retained.exists():
        errors.append("harness/forge-freeze.txt missing (retain the venv freeze bytes)")
    elif retained.read_bytes() != frozen:
        errors.append("harness/forge-freeze.txt does not match the live venv freeze")
    return errors


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--write-manifest":
        write_manifest()
        return 0
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text())
    errors = []
    errors += check_manifest(STUDY / "packs" / "MANIFEST.sha256", STUDY / "packs")
    errors += check_manifest(STUDY / "upstream" / "MANIFEST.sha256", STUDY / "upstream")
    for pack in sorted((STUDY / "jpack-project" / "packs").glob("*.json")):
        if sha256(pack) != sha256(STUDY / "packs" / pack.name):
            errors.append("jpack-project copy drifted: {}".format(pack.name))
    jpack = os.environ.get("JPACK_BIN")
    if jpack and sha256(jpack) != pins["jpack"]["binarySha256"]:
        errors.append("JPACK_BIN digest does not match jpack.binarySha256")
    errors += check_mutated_packs()
    check = STUDY / "goldens" / "EXPECT-CHECK.json"
    if not check.exists():
        errors.append("goldens/EXPECT-CHECK.json missing")
    elif json.loads(check.read_text())["disagreements"] != 0:
        errors.append("goldens record disagreements with cases.json")
    errors += check_python(pins)
    errors += check_forge_venv(pins)
    errors += check_study_manifest()
    for e in errors:
        print("INTEGRITY:", e, file=sys.stderr)
    print("integrity: {} checks failed".format(len(errors)) if errors else "integrity: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
