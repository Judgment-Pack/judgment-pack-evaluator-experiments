"""The composed ceremony over one cell — two layers, one verdict object.

Layer CURRENCY is Study 016's frozen `registry/verify_currency.py`, consumed
as a digest-pinned unmodified upstream (decision D-2). Layer WITNESS is this
study's one added step (`witness/verify_witness.py`). Each layer records
`{verdict, code, detail}` independently so the detection matrix can
attribute; the combined verdict is pass iff both layers pass.

Run: python harness/run_verify.py --cell fixtures/cells/pos-consistent
"""

import argparse
import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "witness"))

import build_fixtures  # noqa: E402
import upstream016  # noqa: E402
import verify_witness  # noqa: E402


def outcome_of(record):
    if record["verdict"] == "pass":
        return "pass"
    if record["verdict"] == "unavailable":
        return "unavailable"
    return "fail:%s" % record["code"] if record["code"] else "fail"


def read(directory, name):
    path = Path(directory) / name
    return path.read_bytes() if path.is_file() else None


def parse_commitment(data):
    """Strict parse of the retained synthetic commitment tuple."""
    if data is None:
        return None
    try:
        def no_duplicates(pairs):
            members = {}
            for key, value in pairs:
                if key in members:
                    raise ValueError("duplicate member name: %s" % key)
                members[key] = value
            return members
        return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates)
    except Exception:
        return None


def manifest_problems(directory):
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


def verify_cell(cell_dir):
    """Run both layers independently and derive the combined verdict."""
    ns = upstream016.load()
    commitment = parse_commitment(read(cell_dir, "commitment.json"))
    snapshot = read(cell_dir, "snapshot.json")
    currency = ns.verify_currency.layer_currency(
        commitment, snapshot, read(cell_dir, "trustconfig.json")
    )
    witness = verify_witness.layer_witness(
        commitment, snapshot,
        read(cell_dir, "witnessconfig.json"), read(cell_dir, "sightings.json"),
    )
    layers = {
        "currency": dict(currency, outcome=outcome_of(currency)),
        "witness": dict(witness, outcome=outcome_of(witness)),
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
                          "problems": ["cell is not registered in the matrix"]}, indent=2))
        return 2
    problems = manifest_problems(directory) + required_file_problems(directory, cell)
    if problems:
        print(json.dumps({"cell": directory.name, "pipelineInvalid": True,
                          "problems": problems}, indent=2))
        return 2
    result = verify_cell(directory)
    result["cell"] = directory.name
    result["pipelineInvalid"] = False
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
