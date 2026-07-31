"""Study 008 harness — portable-derivation admission.

Replays Study 007's retained trial artifacts byte-for-byte and builds two host-side
lineage envelopes per cell:

  Arm B  Study 007's own `candidate_from_gateway` over its hand-written
         `derive_payload`, whose evidence basis is hand-curated per branch.
  Arm C  the same envelope assembly, but the claim and the basis come from
         evaluating the portable rule (derivation-rule/rules/screening.rule.json)
         with derivation-rule/derive.py, whose basis is the set of pointers the
         evaluation actually read.

Both are judged by Study 007's UNCHANGED `verify_candidate`. No model runs; no
network; no API budget. Arm A (model-authored) is read from Study 007's retained
`final.json` as a reference column and is never re-run.

See PREREGISTRATION.md. Endpoints D1-D5 are computed only by `score`.
"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
STUDIES = STUDY.parent
EXPERIMENT = STUDIES.parent
S007 = STUDIES / "007-evidence-lineage-model-replication"


def _load(name, path, search):
    """Load a module by file path. Study 008 has its own `harness` package, which
    would otherwise shadow Study 007's, so neither is imported by package name."""
    if str(search) not in sys.path:
        sys.path.insert(0, str(search))
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Study 007's harness, used unchanged: it is the admission authority (Arm B too).
s007 = _load("s007_study", S007 / "harness" / "study.py", S007 / "harness")
# The portable rule evaluator under test.
portable = _load("portable_derive", EXPERIMENT / "derivation-rule" / "derive.py",
                 EXPERIMENT / "derivation-rule")

RULE_PATH = EXPERIMENT / "derivation-rule" / "rules" / "screening.rule.json"
TRIALS = STUDY / "trials"
FREEZE_PATH = STUDY / "FREEZE.json"

# Files whose bytes must not change during the study; frozen before the first
# scored cell so a third party can confirm nothing was tuned mid-run.
FROZEN_INPUTS = {
    "rule": RULE_PATH,
    "portableEvaluator": EXPERIMENT / "derivation-rule" / "derive.py",
    "s007Harness": S007 / "harness" / "study.py",
    "cases": S007 / "fixtures" / "cases.json",
    "bindingLock": S007 / "fixtures" / "binding-lock.json",
}


class StudyError(Exception):
    pass


def sha256_file(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cells():
    return sorted(p.name for p in (S007 / "trials").iterdir() if p.is_dir())


def cell_inputs(cell_id):
    """The retained, content-addressed inputs for one Study 007 cell."""
    trial = S007 / "trials" / cell_id
    store = trial / "gateway"
    artifacts = sorted((store / "artifacts").glob("*.json"))
    receipts = sorted((store / "receipts").glob("*.json"))
    if len(artifacts) != 1 or len(receipts) != 1:
        raise StudyError("%s: expected exactly one retained artifact and receipt" % cell_id)
    return {
        "trial": trial,
        "store": store,
        "cell": load(trial / "cell.json"),
        "modelFinal": load(trial / "final.json") if (trial / "final.json").exists() else None,
        "payload": load(artifacts[0]),
        "receipt": load(receipts[0]),
        # The receipt is content-addressed by its file name: the digest comes from
        # the store, never from anything a model or a claim asserted.
        "receiptDigest": "sha256:" + receipts[0].stem,
        "artifactDigest": "sha256:" + artifacts[0].stem,
    }


def envelope(claim, basis, binding, receipt_digest, artifact_digest, explanation):
    """Assemble a lineage envelope. Identical for Arm B and Arm C except for the
    claim and basis passed in, so an admission difference is attributable to the
    derivation alone."""
    fact_claims = []
    if claim["acquisitionStatus"] == "resolved":
        fact_claims.append({
            "target": "/screening/matchCount",
            "jsonPointer": "/matchCount",
            "value": claim["facts"]["screening"]["matchCount"],
        })
    return {
        "facts": claim["facts"],
        "evidenceAvailability": claim["evidenceAvailability"],
        "acquisitionStatus": claim["acquisitionStatus"],
        "sourceRef": binding["sourceRef"],
        "lineage": {
            "receiptDigest": receipt_digest,
            "artifactDigest": artifact_digest,
            "factClaims": fact_claims,
            "evidenceClaim": {
                "requirementId": "screening-record",
                "availability": claim["evidenceAvailability"]["screening-record"],
                "basisPointers": sorted(basis),
            },
        },
        "explanation": explanation,
    }


def arm_b(inputs, document, binding):
    """Study 007's hand-written derivation with hand-curated basis sets."""
    derived = s007.derive_payload(
        inputs["payload"], document["request"]["legalName"], document["asOf"],
        binding["maxAgeSeconds"])
    return derived, envelope(
        derived, derived["basis"], binding, inputs["receiptDigest"], inputs["artifactDigest"],
        "Prepared from the gateway-linked synthetic source artifact.")


def arm_c(inputs, document, binding, rule):
    """The portable rule; basis is the pointer set the evaluation actually read."""
    derived = portable.derive(rule, inputs["payload"], {
        "subject": document["request"]["legalName"],
        "asOf": document["asOf"],
        "maxAgeSeconds": binding["maxAgeSeconds"],
    })
    return derived, envelope(
        derived, derived["basis"], binding, inputs["receiptDigest"], inputs["artifactDigest"],
        "Derived by the portable derivation rule over the attested artifact.")


def _bind_sibling_repos():
    """Study 007 locates the runtime binary and pack as siblings of the experiment
    repository's git toplevel. In a git worktree that toplevel is the worktree, so
    resolve the siblings from the *common* git dir instead. Path resolution only --
    no verifier or evaluation semantics change."""
    common = Path(subprocess.run(
        ["git", "rev-parse", "--git-common-dir"], cwd=str(STUDY), check=True,
        stdout=subprocess.PIPE, text=True).stdout.strip()).resolve()
    parent = common.parent.parent  # <real experiment repo>/.git -> repo -> parent
    s007.runtime_binary = lambda: parent / "judgment-pack-runtime" / "bin" / "judgment-pack"
    s007.screening_pack = lambda: (parent / "judgment-pack-demo" / "projects" /
                                   "enterprise-demo" / "packs" / "sanctions-screening.pack.json")
    for name, path in (("runtime binary", s007.runtime_binary()), ("screening pack", s007.screening_pack())):
        if not path.exists():
            raise StudyError("%s not found at %s" % (name, path))


def disposition_of(directory, claim):
    """Real-runtime disposition for an admitted claim (D4)."""
    output, metadata = s007.evaluate_input(directory, claim["facts"], claim["evidenceAvailability"])
    if output is None:
        return None, metadata
    evaluation = output.get("evaluation", output)
    return {
        "outcome": evaluation.get("outcome"),
        "disposition": evaluation.get("disposition"),
        "reasons": evaluation.get("reasons"),
    }, metadata


def cmd_validate():
    missing = [name for name, path in FROZEN_INPUTS.items() if not Path(path).exists()]
    if missing:
        raise StudyError("missing frozen inputs: %s" % ", ".join(missing))
    ids = cells()
    if len(ids) != 24:
        raise StudyError("expected 24 Study 007 cells, found %d" % len(ids))
    for cell_id in ids:
        cell_inputs(cell_id)
    portable._validate_rule(load(RULE_PATH))
    print("validate: 24 cells, frozen inputs present, rule valid")


def cmd_freeze():
    dump(FREEZE_PATH, {
        "frozenInputs": {name: sha256_file(path) for name, path in FROZEN_INPUTS.items()},
        "cells": cells(),
        "note": "Frozen before the first scored cell. Endpoints D1-D5 are defined in "
                "PREREGISTRATION.md and computed only by `score`.",
    })
    print("freeze: wrote %s" % FREEZE_PATH.name)


def cmd_run():
    if not FREEZE_PATH.exists():
        raise StudyError("run `freeze` before `run`")
    frozen = load(FREEZE_PATH)["frozenInputs"]
    for name, path in FROZEN_INPUTS.items():
        if sha256_file(path) != frozen[name]:
            raise StudyError("frozen input changed since freeze: %s" % name)

    _bind_sibling_repos()
    document = load(S007 / "fixtures" / "cases.json")
    binding = load(S007 / "fixtures" / "binding-lock.json")
    key = (S007 / "fixtures" / "gateway.key").read_bytes().strip()  # as Study 007 loads it
    rule = load(RULE_PATH)

    if TRIALS.exists():
        shutil.rmtree(TRIALS)
    for cell_id in cells():
        inputs = cell_inputs(cell_id)
        out = TRIALS / cell_id
        out.mkdir(parents=True, exist_ok=True)

        b_claim, b_env = arm_b(inputs, document, binding)
        c_claim, c_env = arm_c(inputs, document, binding, rule)

        # The admission authority is Study 007's verifier, used unchanged.
        b_errors = s007.verify_candidate(b_env, inputs["store"], document, binding, key)
        c_errors = s007.verify_candidate(c_env, inputs["store"], document, binding, key)

        record = {
            "cellId": cell_id,
            "scenarioId": inputs["cell"]["scenarioId"],
            "expected": inputs["cell"]["expected"],
            "armA": {
                "admitted": inputs["cell"].get("armAAdmitted"),
                "basisPointers": (inputs["modelFinal"] or {}).get("lineage", {})
                                  .get("evidenceClaim", {}).get("basisPointers"),
            },
            "armB": {"reason": b_claim["reason"], "basisPointers": sorted(b_claim["basis"]),
                     "admitted": not b_errors, "errors": b_errors},
            "armC": {"reason": c_claim["reason"], "basisPointers": sorted(c_claim["basis"]),
                     "admitted": not c_errors, "errors": c_errors},
        }

        # D4: real-runtime disposition for cells each arm admits.
        for arm, claim, errors in (("armB", b_claim, b_errors), ("armC", c_claim, c_errors)):
            if not errors:
                verdict, metadata = disposition_of(out / arm, claim)
                record[arm]["disposition"] = verdict
                record[arm]["runtime"] = {"returnCode": metadata.get("returnCode")}

        dump(out / "result.json", record)
        dump(out / "armB-envelope.json", b_env)
        dump(out / "armC-envelope.json", c_env)
        print("%s  B=%s C=%s  reason=%s" % (
            cell_id, "admit" if not b_errors else "REJECT",
            "admit" if not c_errors else "REJECT", c_claim["reason"]))
    print("run: 24 cells written to trials/")


def cmd_score():
    records = [load(TRIALS / cell_id / "result.json") for cell_id in cells()]
    arm_a_lost = ["r02-s07", "r03-s02", "r03-s05"]  # Study 007's three registered losses

    d1 = sum(1 for r in records if r["armC"]["admitted"])
    d2 = sum(1 for r in records if _claim_matches_expected(r))
    d3 = sum(1 for r in records if r["armC"]["basisPointers"] == r["armB"]["basisPointers"])
    both = [r for r in records if r["armB"]["admitted"] and r["armC"]["admitted"]]
    d4 = sum(1 for r in both if r["armB"].get("disposition") == r["armC"].get("disposition"))
    d5 = sum(1 for r in records if r["cellId"] in arm_a_lost and r["armC"]["admitted"])

    results = {
        "D1_armC_admitted": {"value": d1, "of": 24, "threshold": ">= 22", "predicted": 24},
        "D2_armC_claim_equals_expected": {"value": d2, "of": 24, "predicted": 24},
        "D3_armC_basis_equals_armB_basis": {"value": d3, "of": 24, "predicted": 24},
        "D4_disposition_agreement": {"value": d4, "of": len(both), "predicted": len(both)},
        "D5_armA_losses_recovered": {"value": d5, "of": 3, "predicted": 3},
        "armB_admitted": sum(1 for r in records if r["armB"]["admitted"]),
        "basisDisagreements": [
            {"cellId": r["cellId"], "armB": r["armB"]["basisPointers"], "armC": r["armC"]["basisPointers"]}
            for r in records if r["armC"]["basisPointers"] != r["armB"]["basisPointers"]],
        "armCRejections": [
            {"cellId": r["cellId"], "errors": r["armC"]["errors"]}
            for r in records if not r["armC"]["admitted"]],
    }
    dump(STUDY / "RESULTS.json", results)
    for key, value in results.items():
        if isinstance(value, dict) and "value" in value:
            print("%-38s %s/%s" % (key, value["value"], value["of"]))
    print("score: wrote RESULTS.json")


def _claim_matches_expected(record):
    expected = record["expected"]
    envelope_path = TRIALS / record["cellId"] / "armC-envelope.json"
    actual = load(envelope_path)
    return (actual["facts"] == expected["facts"]
            and actual["evidenceAvailability"] == expected["evidenceAvailability"]
            and actual["acquisitionStatus"] == expected["acquisitionStatus"])


COMMANDS = {"validate": cmd_validate, "freeze": cmd_freeze, "run": cmd_run, "score": cmd_score}


def main(argv):
    if len(argv) != 2 or argv[1] not in COMMANDS:
        sys.stderr.write("usage: study.py {%s}\n" % "|".join(COMMANDS))
        return 2
    try:
        COMMANDS[argv[1]]()
    except (StudyError, portable.RuleError) as error:
        sys.stderr.write("error: %s\n" % error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
