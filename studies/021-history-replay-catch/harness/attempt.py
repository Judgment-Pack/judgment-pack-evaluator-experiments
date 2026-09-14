"""The attempt marker and the pin checks every registered step shares.

An attempt root holds `ATTEMPT.json`, written by the runner before anything
else: an attempt id, the label, the runtime's version and digest, the raw
digest of harness/PINS.json as it then was, the seeds, the sizes and the
policies. A REGISTERED attempt requires every freeze pin non-null and
matching its file, the runtime digest equal to the pin, and a marker whose
label, seeds, sizes, policies, runtime digest and pins digest all match the
current tree -- checked by the builder before a reserved draw and by the
scorer before a registered adjudication. A pilot marker says PILOT, and a
pilot draws no reserved seed.
"""
import hashlib
import json
import re
from pathlib import Path

import jp

STUDY = Path(__file__).resolve().parent.parent
PINS_PATH = STUDY / "harness" / "PINS.json"
POLICIES = ("data-request-intake-triage", "expense-approval", "sanctions-screening", "vendor-onboarding")
SIZES = (5, 10, 20, 50)
RESERVED_SEEDS = (101, 130)
REGISTERED_LABEL = "REGISTERED"
PILOT_LABEL = "PILOT"
FREEZE_FILES = {"preregistration": "PREREGISTRATION.md", "matrix": "harness/MATRIX.json",
                "matrixHoldout": "harness/MATRIX-HOLDOUT.json", "studyManifest": "harness/STUDY-MANIFEST.sha256"}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pins_raw_sha256():
    return hashlib.sha256(PINS_PATH.read_bytes()).hexdigest()


def load_pins():
    return json.loads(PINS_PATH.read_text())


def pin_problems(pins, runtime_digest, require_all=False):
    """Every way the tree disagrees with its pins; with require_all, every null pin too."""
    problems = []
    pinned = pins["jpack"]["sha256"]
    if pinned and pinned != runtime_digest:
        problems.append("the runtime's digest %s is not the pinned %s" % (runtime_digest, pinned))
    if require_all and not pinned:
        problems.append("the runtime digest is not pinned")
    for key, relative in FREEZE_FILES.items():
        expected = pins["freeze"].get(key)
        if expected and expected != sha256_file(STUDY / relative):
            problems.append("%s does not match its freeze pin" % relative)
        if require_all and not expected:
            problems.append("%s is not pinned" % relative)
    import make_manifest
    if (STUDY / "harness" / "STUDY-MANIFEST.sha256").read_text() != make_manifest.render():
        problems.append("harness/STUDY-MANIFEST.sha256 does not match the tree")
    return problems


def read_marker(root):
    path = Path(root) / "ATTEMPT.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def marker_problems(marker, runtime_digest, label):
    """Every way a marker fails to describe a valid attempt of the given label."""
    problems = []
    if not isinstance(marker, dict):
        return ["no marker"]
    for key in ("attemptId", "label", "jpackVersion", "jpackDigest", "pinsRawSha256", "seeds", "sizes", "policies", "startedAt"):
        if key not in marker:
            problems.append("marker lacks %s" % key)
    if problems:
        return problems
    if marker["label"] != label:
        problems.append("marker label is %s, not %s" % (marker["label"], label))
    if marker["jpackDigest"] != runtime_digest:
        problems.append("marker's runtime digest %s is not this runtime's %s" % (marker["jpackDigest"], runtime_digest))
    if marker["pinsRawSha256"] != pins_raw_sha256():
        problems.append("marker's pins digest is not the current harness/PINS.json's")
    expected_seeds = list(RESERVED_SEEDS) if label == REGISTERED_LABEL else [1, 30]
    if marker["seeds"] != expected_seeds:
        problems.append("marker seeds %s are not %s" % (marker["seeds"], expected_seeds))
    if marker["sizes"] != list(SIZES):
        problems.append("marker sizes %s are not %s" % (marker["sizes"], list(SIZES)))
    if marker["policies"] != list(POLICIES):
        problems.append("marker policies are not the four registered ones")
    if not isinstance(marker["attemptId"], str) or not re.fullmatch(r"[0-9a-f]{32}", marker["attemptId"]):
        problems.append("marker attempt id is not a 32-hex token")
    return problems


def registered_context_problems(root):
    """What keeps a root from being a valid, active REGISTERED attempt: pins, runtime, marker."""
    digest = jp.binary_digest()
    problems = pin_problems(load_pins(), digest, require_all=True)
    marker = read_marker(root)
    problems += marker_problems(marker, digest, REGISTERED_LABEL)
    return problems, marker
