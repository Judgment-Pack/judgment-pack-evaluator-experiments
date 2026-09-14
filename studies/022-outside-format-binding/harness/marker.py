"""The attempt marker's validation, shared by the scorer and by the holdout construction guard (harness/cells.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells as constructions  # noqa: E402
import pins as pinning  # noqa: E402

PILOT, REGISTERED = "PILOT", "REGISTERED"


def marker_problems(marker, gateway_digest, label, actual_root):
    """Every way a marker is not this attempt's: members, label, interpreter, root (the directory the evidence is read
    from, and for a registered attempt the literal primary root), gateway digest, pins digest, key id, cell set, id."""
    problems = []
    if marker is None:
        return ["no attempt marker"]
    if not isinstance(marker, dict):
        return ["the attempt marker is not an object"]
    for key in ("attemptId", "attemptRoot", "label", "gatewaySha256", "pinsRawSha256", "adapterKeyid", "python", "cells", "startedAt"):
        if key not in marker:
            problems.append("marker lacks %s" % key)
    if problems:
        return problems
    if marker["label"] != label:
        problems.append("marker label is %s, not %s" % (marker["label"], label))
    if marker["python"] != sys.version.split()[0]:
        problems.append("marker's interpreter %s is not this interpreter %s" % (marker["python"], sys.version.split()[0]))
    if not isinstance(marker["attemptRoot"], str) or Path(marker["attemptRoot"]).resolve() != Path(actual_root).resolve():
        problems.append("marker's root %s is not the root being read, %s" % (marker["attemptRoot"], Path(actual_root).resolve()))
    if label == REGISTERED and (not isinstance(marker["attemptRoot"], str) or Path(marker["attemptRoot"]).resolve() != constructions.PRIMARY_ROOT.resolve()):
        problems.append("a registered attempt's root is results/primary-attempt-001, not %s" % marker["attemptRoot"])
    if marker["gatewaySha256"] != gateway_digest:
        problems.append("marker's gateway digest is not this binary's")
    if marker["pinsRawSha256"] != pinning.raw_sha256():
        problems.append("marker's pins digest is not the current harness/PINS.json")
    if marker["adapterKeyid"] != pinning.adapter_keyid():
        problems.append("marker's adapter key id is not the pinned one")
    expected_cells = sorted(constructions.ALL_CELLS) if label == REGISTERED else sorted(constructions.CELLS)
    if not isinstance(marker["cells"], list) or sorted(marker["cells"]) != expected_cells:
        problems.append("marker's cell set is not the registered constructions (%s)" % ("locked and holdout" if label == REGISTERED else "locked"))
    if not isinstance(marker["attemptId"], str) or len(marker["attemptId"]) != 32:
        problems.append("marker's attempt id is not a 32-character token")
    return problems
