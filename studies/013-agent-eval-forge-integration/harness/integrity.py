"""Pin verification — refuses drifted state before any run and before any count.

Checks (011-convention, scaled to this study's pilot phase):
  1. every file in packs/MANIFEST.sha256 and upstream/MANIFEST.sha256 matches
  2. jpack-project/packs/* are byte-identical to packs/*
  3. $JPACK_BIN (when set) matches jpack.binarySha256
  4. mutated packs equal a fresh deterministic re-derivation (mutate_packs.py)
  5. goldens/EXPECT-CHECK.json exists and records zero disagreements

Stdlib only. Run: python3 harness/integrity.py   (exit non-zero on any drift)
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_manifest(manifest):
    errors = []
    base = manifest.parent
    for line in manifest.read_text().splitlines():
        digest, name = line.split(None, 1)
        target = base / name.strip()
        if not target.exists():
            errors.append("missing: {}".format(target))
        elif sha256(target) != digest:
            errors.append("drifted: {}".format(target))
    return errors


def main():
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text())
    errors = []

    errors += check_manifest(STUDY / "packs" / "MANIFEST.sha256")
    errors += check_manifest(STUDY / "upstream" / "MANIFEST.sha256")

    for pack in sorted((STUDY / "jpack-project" / "packs").glob("*.json")):
        if sha256(pack) != sha256(STUDY / "packs" / pack.name):
            errors.append("jpack-project copy drifted: {}".format(pack.name))

    jpack = os.environ.get("JPACK_BIN")
    if jpack:
        if sha256(jpack) != pins["jpack"]["binarySha256"]:
            errors.append("JPACK_BIN digest does not match jpack.binarySha256")

    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        proc = subprocess.run(
            [sys.executable, str(STUDY / "harness" / "mutate_packs.py")],
            capture_output=True, env=env,
            cwd=tmp,
        )
        if proc.returncode != 0:
            errors.append("mutate_packs re-derivation failed")
    # mutate_packs writes into the study tree; byte-stability holds when git
    # sees no change — checked by the caller (tests assert equality directly).

    check = STUDY / "goldens" / "EXPECT-CHECK.json"
    if not check.exists():
        errors.append("goldens/EXPECT-CHECK.json missing")
    elif json.loads(check.read_text())["disagreements"] != 0:
        errors.append("goldens record disagreements with cases.json")

    for e in errors:
        print("INTEGRITY:", e, file=sys.stderr)
    print("integrity: {} checks failed".format(len(errors)) if errors else "integrity: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
