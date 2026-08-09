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
    "scenarios/mutations/MATRIX-HOLDOUT.json",
    "scenarios/mutations/packs/*.json",
    "scenarios/upstream-expected-unscored.json",
    "PREREGISTRATION.md",
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
    if running != wanted["version"]:
        return ["python {} is not the pinned {}".format(running, wanted["version"])]
    return []


def check_forge_venv(pins):
    venv_python = os.environ.get("FORGE_VENV_PY")
    if not venv_python:
        return ["FORGE_VENV_PY is not set (mandatory: the venv is a pinned identity)"]
    proc = subprocess.run(
        [venv_python, "-c", "import platform; print(platform.python_version())"],
        capture_output=True, text=True)
    if proc.returncode != 0:
        return ["Forge venv python did not run"]
    if proc.stdout.strip() != pins["forge"]["venvPython"]:
        return ["Forge venv python {} is not the pinned {}".format(
            proc.stdout.strip(), pins["forge"]["venvPython"])]
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
    if not jpack:
        errors.append("JPACK_BIN is not set (mandatory: the evaluator is a pinned identity)")
    elif sha256(jpack) != pins["jpack"]["binarySha256"]:
        errors.append("JPACK_BIN digest does not match jpack.binarySha256")
    clone = os.environ.get("FORGE_CLONE")
    if not clone:
        errors.append("FORGE_CLONE is not set (mandatory: the editable checkout is "
                      "a pinned identity)")
    else:
        head = subprocess.run(["git", "-C", clone, "rev-parse", "HEAD"],
                              capture_output=True, text=True)
        dirty = subprocess.run(["git", "-C", clone, "status", "--porcelain"],
                               capture_output=True, text=True)
        if head.returncode != 0 or dirty.returncode != 0:
            errors.append("FORGE_CLONE is not a usable git checkout")
        else:
            if head.stdout.strip() != pins["forge"]["commit"]:
                errors.append("FORGE_CLONE HEAD {} is not the pinned commit".format(
                    head.stdout.strip()[:12]))
            if dirty.stdout.strip():
                errors.append("FORGE_CLONE working tree is dirty")
        # The venv must IMPORT this exact checkout (round 3, R3-4): an
        # unrelated clean clone at the pin must not stand in for a dirty
        # editable source.
        venv_python = os.environ.get("FORGE_VENV_PY")
        if venv_python:
            src = subprocess.run(
                [venv_python, "-c",
                 "import evalforge, os; print(os.path.realpath("
                 "os.path.dirname(os.path.dirname(os.path.dirname("
                 "evalforge.__file__)))))"],
                capture_output=True, text=True)
            if src.returncode != 0:
                errors.append("could not resolve the venv's evalforge source")
            elif os.path.realpath(src.stdout.strip()) != os.path.realpath(clone):
                errors.append("venv imports evalforge from {} which is not "
                              "FORGE_CLONE".format(src.stdout.strip()))
            impl = subprocess.run(
                [venv_python, "-c", "import platform; print(platform.python_implementation())"],
                capture_output=True, text=True)
            if impl.returncode != 0 or impl.stdout.strip() != "CPython":
                errors.append("Forge venv interpreter implementation is not CPython")
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
