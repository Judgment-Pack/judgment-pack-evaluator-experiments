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
import os
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
# One shared explanation string: the arms must differ only in claim and basis.
EXPLANATION = "Host-assembled from the attested artifact."

FROZEN_INPUTS = {
    "rule": RULE_PATH,
    "portableEvaluator": EXPERIMENT / "derivation-rule" / "derive.py",
    "s007Harness": S007 / "harness" / "study.py",
    # The verifier's semantics live partly in these: digest, attest,
    # verify_attestation, canonical. Freezing study.py alone left them loose.
    "s007Common": S007 / "harness" / "common.py",
    "s007Gateway": S007 / "harness" / "acquisition_gateway.py",
    "cases": S007 / "fixtures" / "cases.json",
    "bindingLock": S007 / "fixtures" / "binding-lock.json",
    "gatewayKey": S007 / "fixtures" / "gateway.key",
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
        EXPLANATION)


def arm_c(inputs, document, binding, rule):
    """The portable rule; basis is the pointer set the evaluation actually read."""
    derived = portable.derive(rule, inputs["payload"], {
        "subject": document["request"]["legalName"],
        "asOf": document["asOf"],
        "maxAgeSeconds": binding["maxAgeSeconds"],
    })
    return derived, envelope(
        derived, derived["basis"], binding, inputs["receiptDigest"], inputs["artifactDigest"],
        EXPLANATION)


def arm_control_wide(inputs, document, binding):
    """CALIBRATION CONTROL (not a registered endpoint). Arm B's claim carried with
    an un-derived kitchen-sink basis: every top-level pointer in the payload. The
    verifier's basis check is a SUPERSET test (007 study.py:499), so if this is
    admitted, admission does not evidence that a *derived* basis beats an authored
    one -- it only rules out lists that are too short."""
    derived = s007.derive_payload(
        inputs["payload"], document["request"]["legalName"], document["asOf"],
        binding["maxAgeSeconds"])
    wide = {"/" + str(k).replace("~", "~0").replace("/", "~1") for k in inputs["payload"]}
    return derived, envelope(derived, wide, binding, inputs["receiptDigest"],
                             inputs["artifactDigest"], EXPLANATION)


def arm_control_short(inputs, document, binding):
    """CALIBRATION CONTROL (not a registered endpoint). Arm B's basis minus one
    pointer: the complementary control, expected to be rejected. Together with the
    wide control this brackets what D1 can and cannot distinguish."""
    derived = s007.derive_payload(
        inputs["payload"], document["request"]["legalName"], document["asOf"],
        binding["maxAgeSeconds"])
    short = sorted(derived["basis"])[1:]
    return derived, envelope(derived, short, binding, inputs["receiptDigest"],
                             inputs["artifactDigest"], EXPLANATION)


def _resolve_common_dir(reported):
    """Resolve `git rev-parse --git-common-dir` output. A plain checkout reports it
    RELATIVE to the directory git ran in (STUDY); a worktree reports it absolute.
    Resolving a relative report against the process working directory instead of
    STUDY makes the study runnable from exactly one directory, which defeats the
    third-party reproducibility this study claims."""
    path = Path(reported)
    return (path if path.is_absolute() else (STUDY / path)).resolve()


def _bind_sibling_repos():
    """Study 007 locates the runtime binary and pack as siblings of the experiment
    repository's git toplevel. In a git worktree that toplevel is the worktree, so
    resolve the siblings from the *common* git dir instead. Path resolution only --
    no verifier or evaluation semantics change."""
    common = _resolve_common_dir(subprocess.run(
        ["git", "rev-parse", "--git-common-dir"], cwd=str(STUDY), check=True,
        stdout=subprocess.PIPE, text=True).stdout.strip())
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


def cell_data_digest():
    """One digest over every per-cell input the study replays, so the DATA is
    frozen and not merely the code that reads it."""
    parts = []
    for cell_id in cells():
        trial = S007 / "trials" / cell_id
        for relative in ("cell.json", "final.json"):
            if (trial / relative).exists():
                parts.append("%s/%s=%s" % (cell_id, relative, sha256_file(trial / relative)))
        for sub in ("artifacts", "receipts"):
            for path in sorted((trial / "gateway" / sub).glob("*.json")):
                parts.append("%s/%s/%s=%s" % (cell_id, sub, path.name, sha256_file(path)))
    return "sha256:" + hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def verify_committed_freeze():
    """FREEZE.json must be committed before `run`, so a third party can see the
    freeze preceded the results. Study 007 had this control; Study 008 initially
    dropped it (see DEVIATIONS.md)."""
    repo = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(STUDY),
                               check=True, stdout=subprocess.PIPE, text=True).stdout.strip())
    relative = str(FREEZE_PATH.relative_to(repo))
    committed = subprocess.run(["git", "show", "HEAD:" + relative], cwd=str(repo),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if committed.returncode != 0:
        raise StudyError("FREEZE.json is not committed at HEAD; commit the freeze before `run`")
    if committed.stdout != FREEZE_PATH.read_bytes():
        raise StudyError("FREEZE.json differs from the committed copy")


def cmd_freeze():
    dump(FREEZE_PATH, {
        "frozenInputs": {name: sha256_file(path) for name, path in FROZEN_INPUTS.items()},
        "cellData": cell_data_digest(),
        "cells": cells(),
        "note": "Frozen before the first scored cell. Endpoints D1-D5 are defined in "
                "PREREGISTRATION.md and computed only by `score`.",
    })
    print("freeze: wrote %s" % FREEZE_PATH.name)


def cmd_run():
    if not FREEZE_PATH.exists():
        raise StudyError("run `freeze` before `run`")
    manifest = load(FREEZE_PATH)
    frozen = manifest["frozenInputs"]
    for name, path in FROZEN_INPUTS.items():
        if sha256_file(path) != frozen[name]:
            raise StudyError("frozen input changed since freeze: %s" % name)
    if cell_data_digest() != manifest["cellData"]:
        raise StudyError("per-cell data changed since freeze")
    if os.environ.get("STUDY008_ALLOW_UNCOMMITTED_FREEZE") != "1":
        verify_committed_freeze()

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
        _, wide_env = arm_control_wide(inputs, document, binding)
        _, short_env = arm_control_short(inputs, document, binding)

        # The admission authority is Study 007's verifier, used unchanged.
        b_errors = s007.verify_candidate(b_env, inputs["store"], document, binding, key)
        c_errors = s007.verify_candidate(c_env, inputs["store"], document, binding, key)
        wide_errors = s007.verify_candidate(wide_env, inputs["store"], document, binding, key)
        short_errors = s007.verify_candidate(short_env, inputs["store"], document, binding, key)

        record = {
            "cellId": cell_id,
            "scenarioId": inputs["cell"]["scenarioId"],
            "expected": inputs["cell"]["expected"],
            "armA": {
                "admitted": arm_a_admitted().get(cell_id),
                "basisPointers": (inputs["modelFinal"] or {}).get("lineage", {})
                                  .get("evidenceClaim", {}).get("basisPointers"),
            },
            "armB": {"reason": b_claim["reason"], "basisPointers": sorted(b_claim["basis"]),
                     "admitted": not b_errors, "errors": b_errors},
            "armC": {"reason": c_claim["reason"], "basisPointers": sorted(c_claim["basis"]),
                     "admitted": not c_errors, "errors": c_errors},
            # Calibration controls: not registered endpoints. They bracket what the
            # verifier's superset basis test can and cannot distinguish.
            "controlWideBasis": {"admitted": not wide_errors, "errors": wide_errors,
                                 "basisPointers": wide_env["lineage"]["evidenceClaim"]["basisPointers"]},
            "controlShortBasis": {"admitted": not short_errors, "errors": short_errors},
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
    d4 = sum(1 for r in both
             if r["armB"].get("disposition") is not None
             and r["armB"].get("disposition") == r["armC"].get("disposition"))
    d5 = sum(1 for r in records if r["cellId"] in arm_a_lost and r["armC"]["admitted"])

    results = {
        "D1_armC_admitted": {"value": d1, "of": 24, "threshold": ">= 22", "predicted": 24},
        "D2_armC_claim_equals_expected": {"value": d2, "of": 24, "predicted": 24},
        "D3_armC_basis_equals_armB_basis": {"value": d3, "of": 24, "predicted": 24},
        "D4_disposition_agreement": {"value": d4, "of": len(both), "predicted": len(both)},
        "D5_armA_losses_recovered": {"value": d5, "of": 3, "predicted": 3},
        "armB_admitted": sum(1 for r in records if r["armB"]["admitted"]),
        "armA_admitted_per_study007": sum(1 for r in records if r["armA"]["admitted"]),
        "CONTROL_wideBasis_admitted": {
            "value": sum(1 for r in records if r["controlWideBasis"]["admitted"]), "of": 24,
            "note": "Un-derived kitchen-sink basis carrying Arm B's claim. Admission here means "
                    "D1 does not evidence that a derived basis beats an authored one."},
        "CONTROL_shortBasis_admitted": {
            "value": sum(1 for r in records if r["controlShortBasis"]["admitted"]), "of": 24,
            "note": "Arm B's basis minus one pointer; expected 0."},
        "runtimeInputsIdenticalAcrossArms": sum(
            1 for r in records if r["armB"]["admitted"] and r["armC"]["admitted"]),
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


def arm_a_admitted():
    """Per-cell Arm A admission read from Study 007's own RESULTS.json, so the
    reference column is derived rather than transcribed."""
    results = load(S007 / "RESULTS.json")
    admitted = {}
    for cell in results.get("cells", []):
        if isinstance(cell, dict) and "cellId" in cell:
            # M2 is Study 007's "exact verified preparation" endpoint: admission.
            admitted[cell["cellId"]] = bool(cell["M2"])
    return admitted


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
