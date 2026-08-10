"""The composed ceremony over one cell — three layers, one verdict object.

Checks the cell's manifest first: a fixture that fails its own manifest, or whose
artifacts are incomplete in a way the matrix did not register, is *pipeline-invalid*
(PREREGISTRATION section 6) and is reported as such rather than as a detection —
the JSON carries `pipelineInvalid: true` and the process exits 2.

Run: JPACK_BIN=... python harness/run_verify.py --cell fixtures/baseline
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import score  # noqa: E402
import verify  # noqa: E402


def registered_cell(cell_id):
    registry = json.loads(
        (STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8")
    )
    for cell in registry["cells"]:
        if cell["id"] == cell_id:
            return cell
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cell", required=True)
    arguments = parser.parse_args(argv)

    directory = Path(arguments.cell).resolve()
    cell_id = "pos-baseline" if directory.name == "baseline" else directory.name
    cell = registered_cell(cell_id)
    if cell is None:
        print(json.dumps({"cell": cell_id, "pipelineInvalid": True,
                          "problems": ["cell is not registered in the matrix"]}, indent=2))
        return 2

    pins = json.loads(
        (STUDY / "harness" / "PINS.json").read_text(encoding="utf-8")
    )
    jpack_bin = os.environ.get("JPACK_BIN")
    problems = score.pipeline_problems(directory, cell)
    if not jpack_bin or not Path(jpack_bin).is_file():
        problems.append("JPACK_BIN is not available")
    elif verify.sha256_file(jpack_bin) != pins["jpack"]["binarySha256"]:
        problems.append("JPACK_BIN does not match the pinned digest")

    if problems:
        print(
            json.dumps(
                {"cell": cell_id, "pipelineInvalid": True, "problems": problems},
                indent=2,
            )
        )
        return 2

    work_root = Path(tempfile.mkdtemp(prefix="study014-verify-"))
    try:
        result = verify.verify_cell(directory, jpack_bin, work_root)
    finally:
        shutil.rmtree(work_root, ignore_errors=True)
    result["cell"] = cell_id
    result["pipelineInvalid"] = False
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
