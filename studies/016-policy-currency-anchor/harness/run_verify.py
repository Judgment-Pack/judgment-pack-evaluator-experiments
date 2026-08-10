"""The composed ceremony over one cell — four layers, one verdict object.

Layers OWP / BINDING / REPLAY are Study 014's, run by its frozen
`adapter/verify.py` unmodified (decision D-1). Layer CURRENCY is this study's
one added step (`registry/verify_currency.py`): membership of the verified
chain's `(packVersion, packDigest)` in the series' supported set at the pinned
registry snapshot. Each layer records `{verdict, code, detail}` independently
so the detection matrix can attribute; the combined verdict is pass iff every
layer passes.

Run: JPACK_BIN=... python harness/run_verify.py --cell fixtures/cells/pos-current
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "registry"))

import build_fixtures  # noqa: E402  (this study's; manifest + CELL_FILES)
import upstream014  # noqa: E402
import verify_currency  # noqa: E402


def outcome_of(record):
    if record["verdict"] == "pass":
        return "pass"
    if record["verdict"] == "unavailable":
        return "unavailable"
    return "fail:%s" % record["code"] if record["code"] else "fail"


def manifest_problems(directory):
    """Manifest integrity over this study's cell files."""
    directory = Path(directory)
    manifest = directory / build_fixtures.MANIFEST_NAME
    if not manifest.is_file():
        return ["manifest is absent"]
    problems = []
    listed = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, name = line.partition("  ")
        listed[name] = digest
    for name, digest in sorted(listed.items()):
        path = directory / name
        if not path.is_file():
            problems.append("listed file is absent: " + name)
        elif build_fixtures.sha256_hex(path.read_bytes()) != digest:
            problems.append("listed file does not match its digest: " + name)
    for name in sorted(build_fixtures.CELL_FILES):
        if (directory / name).is_file() and name not in listed:
            problems.append("present file is not listed: " + name)
    return problems


def required_file_problems(directory, cell):
    """Every cell file must be present unless the registry authorized absence."""
    absences = set(cell.get("registeredAbsences", ()))
    problems = []
    for name in build_fixtures.CELL_FILES:
        stem = name.rsplit(".", 1)[0]
        present = (Path(directory) / name).is_file()
        if not present and stem not in absences:
            problems.append("artifact is absent without registration: " + name)
        if present and stem in absences:
            problems.append("artifact is present despite registered absence: " + name)
    return problems


def verify_cell(cell_dir, jpack_bin, work_dir):
    """Run the four layers independently and derive the combined verdict."""
    ns = upstream014.load()
    three = ns.verify.verify_cell(cell_dir, jpack_bin, work_dir)
    cell = ns.verify.Cell(cell_dir)
    commitment = ns.verify.commitment_at_binding_point(cell)
    currency = verify_currency.layer_currency(
        commitment,
        cell.read("snapshot.json"),
        cell.json("trustconfig.json"),
    )
    layers = {
        "owp": dict(three["owp"]),
        "binding": dict(three["binding"]),
        "replay": dict(three["replay"]),
        "currency": dict(currency, outcome=outcome_of(currency)),
    }
    outcomes = {name: record["outcome"] for name, record in layers.items()}
    return dict(
        layers,
        combined="pass" if all(v == "pass" for v in outcomes.values()) else "fail",
    )


def registered_cell(cell_id):
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    for cell in matrix["cells"]:
        if cell["id"] == cell_id:
            return cell
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cell", required=True)
    arguments = parser.parse_args(argv)

    directory = Path(arguments.cell).resolve()
    cell = registered_cell(directory.name)
    if cell is None:
        print(json.dumps({"cell": directory.name, "pipelineInvalid": True,
                          "problems": ["cell is not registered in the matrix"]},
                         indent=2))
        return 2

    ns = upstream014.load()
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    jpack_bin = os.environ.get("JPACK_BIN")
    problems = manifest_problems(directory) + required_file_problems(directory, cell)
    if not jpack_bin or not Path(jpack_bin).is_file():
        problems.append("JPACK_BIN is not available")
    elif ns.verify.sha256_file(jpack_bin) != pins["jpack"]["binarySha256"]:
        problems.append("JPACK_BIN does not match the pinned digest")

    if problems:
        print(json.dumps({"cell": directory.name, "pipelineInvalid": True,
                          "problems": problems}, indent=2))
        return 2

    work_root = Path(tempfile.mkdtemp(prefix="study016-verify-"))
    try:
        result = verify_cell(directory, jpack_bin, work_root)
    finally:
        shutil.rmtree(work_root, ignore_errors=True)
    result["cell"] = directory.name
    result["pipelineInvalid"] = False
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
