"""The composed ceremony over one cell — two layers, one verdict object.

Layer CURRENCY is Study 016's frozen `registry/verify_currency.py`, consumed as
a digest-pinned unmodified upstream: its output stays exactly "membership at
snapshot". Layer TRANSITION is this study's rule evaluator, which consumes that
verdict **as a fact** and answers a different question — usability under a
stated rule. The separation is the point (RFC 0011 §2a), and the study fails if
the two ever merge.

Run: python harness/run_verify.py --cell fixtures/cells/div-grandfather-on-cited-support
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "rule"))

import build_fixtures  # noqa: E402
import transition  # noqa: E402
import upstream016  # noqa: E402


def outcome_of(record):
    if record["verdict"] in ("pass", "usable"):
        return record["verdict"]
    if record["verdict"] == "unavailable":
        return "unavailable"
    return "%s:%s" % (record["verdict"], record["code"]) if record["code"] else record["verdict"]


def read(directory, name):
    path = Path(directory) / name
    return path.read_bytes() if path.is_file() else None


def strict_json(data):
    if data is None:
        return None
    try:
        def no_duplicates(pairs):
            members = {}
            for key, value in pairs:
                if key in members:
                    raise ValueError("duplicate member: %s" % key)
                members[key] = value
            return members
        return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates)
    except Exception:
        return None


def snapshot_view(snapshot_bytes):
    """(digests, payloads) recomputed from the snapshot's own bytes, or (None, None)."""
    ns = upstream016.load()
    try:
        snapshot = json.loads(snapshot_bytes.decode("utf-8"))
        digests, payloads = [], []
        for record in snapshot["checkpoints"]:
            canonical = ns.verify_currency._canonical(
                ns.verify_currency.DOMAIN_CHECKPOINT, record["checkpoint"])
            digests.append("sha256:" + hashlib.sha256(canonical).hexdigest())
            payloads.append(record["checkpoint"])
        return (digests or None), payloads
    except Exception:
        return None, None


def manifest_problems(directory):
    directory = Path(directory)
    manifest = directory / build_fixtures.MANIFEST_NAME
    if not manifest.is_file():
        return ["manifest is absent"]
    problems, listed = [], {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip():
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
    ns = upstream016.load()
    commitment = strict_json(read(cell_dir, "commitment.json"))
    snapshot = read(cell_dir, "snapshot.json")
    currency = ns.verify_currency.layer_currency(
        commitment, snapshot, read(cell_dir, "trustconfig.json"))
    currency_outcome = ("pass" if currency["verdict"] == "pass"
                        else "unavailable" if currency["verdict"] == "unavailable"
                        else "fail:%s" % currency["code"])
    digests, payloads = snapshot_view(snapshot) if snapshot is not None else (None, None)
    rule = transition.layer_transition(
        commitment, digests, payloads, read(cell_dir, "citation.json"),
        read(cell_dir, "ruleconfig.json"), currency_outcome,
        fold=ns.verify_currency.fold_supported)
    layers = {
        "currency": dict(currency, outcome=currency_outcome),
        "transition": dict(rule, outcome=outcome_of(rule)),
    }
    # Usable requires an ADJUDICABLE currency answer plus the rule's
    # permission — not both layers permitting. A binding outside the
    # supported set still composes to `usable` under a rule that allows it,
    # which is the study's whole subject; what is refused is an
    # unauthenticated or unavailable registry answer (round-1 R1-1).
    composed = ("usable" if layers["transition"]["outcome"] == "usable"
                and layers["currency"]["outcome"] in transition.ADJUDICABLE_CURRENCY
                else layers["transition"]["outcome"])
    return dict(layers, combined=composed)


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
