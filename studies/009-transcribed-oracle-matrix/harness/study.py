#!/usr/bin/env python3
"""Study 009 driver: validate | freeze | run | score (PREREGISTRATION.md §10).

Endpoints are computed only in `score`, from files `run` retained. `run`
refuses an unverified or uncommitted freeze, creates an exclusive attempt
ledger before any work, and never overwrites an attempt. Attempt 1 is
primary; there is no retry rule.
"""
from __future__ import annotations
import hashlib
import hmac as hmac_module
import json
import os
import platform
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
LINE = os.path.dirname(os.path.dirname(STUDY))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LINE, "acquisition-proxy"))
sys.path.insert(0, os.path.join(LINE, "derivation-rule"))
sys.path.insert(0, os.path.join(LINE, "fabrication-gate"))

import attest  # noqa: E402
import pnf_check  # noqa: E402
import importlib.util as _importlib_util

_spec = _importlib_util.spec_from_file_location("study_gate", os.path.join(HERE, "gate.py"))
study_gate = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(study_gate)

AUTHORITY = "study-009:records"
TOOL = "get_record"
JPACK_DIGEST = "sha256:a76091a30b2e595dd7259161d423066805664ad30394d313ffeb0e8d7e0ce782"
DECIMAL = re.compile(r"^(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$")
FREEZE = os.path.join(STUDY, "FREEZE.json")
TRIALS = os.path.join(STUDY, "trials")

FROZEN = [
    "policy/POLICY.md",
    "packs/vendor-screening-correct.pack.json",
    "packs/vendor-screening-defective.pack.json",
    "DEFECT.json",
    "RECORDS.md",
    "source/record_source.py",
    "transcription/record.rule.json",
    "transcription/transcribe.py",
    "harness/study.py",
    "harness/pnf_check.py",
    "harness/gate.py",
    "harness/test_study.py",
    "../../acquisition-proxy/attest.py",
    "../../derivation-rule/derive.py",
    "../../fabrication-gate/gate.py",
]

RECORD_MEMBERS = {"caseId", "vendor", "decision"}
VENDOR_MEMBERS = {"legalName", "sanctionsHit", "riskScore"}
DECISION_MEMBERS = {"outcome", "decidedBy", "decidedAt"}


class StudyError(Exception):
    pass


def sha256_file(path: str) -> str:
    return "sha256:" + hashlib.sha256(open(path, "rb").read()).hexdigest()


def defect() -> dict:
    return json.load(open(os.path.join(STUDY, "DEFECT.json")))


def record_ids() -> list[str]:
    return sorted(name[:-5] for name in os.listdir(os.path.join(STUDY, "records"))
                  if name.endswith(".json"))


def load_record(case_id: str) -> dict:
    return json.load(open(os.path.join(STUDY, "records", case_id + ".json")))


def apply_patch(pack: dict, patch: list[dict]) -> dict:
    import copy
    patched = copy.deepcopy(pack)
    for entry in patch:
        tokens = [t.replace("~1", "/").replace("~0", "~") for t in entry["path"].split("/")[1:]]
        node = patched
        for token in tokens[:-1]:
            node = node[int(token)] if isinstance(node, list) else node[token]
        last = tokens[-1]
        target = int(last) if isinstance(node, list) else last
        if node[target] != entry["old"]:
            raise StudyError("patch preimage mismatch at %s: %r" % (entry["path"], node[target]))
        node[target] = entry["new"]
    return patched


def cmd_validate() -> None:
    for relative in FROZEN:
        if not os.path.exists(os.path.join(STUDY, relative)):
            raise StudyError("missing frozen input: " + relative)
    manifest = defect()
    sets = manifest["sets"]
    all_ids = sets["F"] + sets["K"] + sets["H"]
    if len(set(all_ids)) != len(all_ids):
        raise StudyError("the F/K/H sets are not disjoint")
    if set(all_ids) != set(record_ids()):
        raise StudyError("the sets do not cover exactly the record files")
    tables = manifest["expectedDispositions"]["perRecord"]
    if set(tables) != set(all_ids):
        raise StudyError("the disposition tables do not cover exactly the record ids")
    for case_id in all_ids:
        record = load_record(case_id)
        if set(record) != RECORD_MEMBERS or set(record["vendor"]) != VENDOR_MEMBERS \
                or set(record["decision"]) != DECISION_MEMBERS:
            raise StudyError("record %s is not the closed schema" % case_id)
        if record["caseId"] != case_id:
            raise StudyError("record %s misnames itself" % case_id)
        vendor = record["vendor"]
        if not isinstance(vendor["sanctionsHit"], bool) or not isinstance(vendor["riskScore"], str) \
                or not DECIMAL.match(vendor["riskScore"]):
            raise StudyError("record %s breaks the canonical value domains" % case_id)
        in_f = vendor["sanctionsHit"] is False and vendor["riskScore"] == "70"
        if in_f != (case_id in sets["F"]):
            raise StudyError("record %s disagrees with the defect predicate" % case_id)
    for case_id in sets["K"]:
        entry = tables[case_id]
        if entry["underC"] != entry["underD"]:
            raise StudyError("K row %s must behave identically under C and D" % case_id)
    correct = json.load(open(os.path.join(STUDY, "packs/vendor-screening-correct.pack.json")))
    defective = json.load(open(os.path.join(STUDY, "packs/vendor-screening-defective.pack.json")))
    if apply_patch(correct, manifest["patch"]) != defective:
        raise StudyError("C with the registered patch applied is not D")
    pnf_check.check(json.load(open(os.path.join(STUDY, "transcription/record.rule.json"))))
    print("validate: ok (%d records, patch bound, rule is the registered projection)" % len(all_ids))


def freeze_body() -> dict:
    revision = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "PREREGISTRATION.md"],
        cwd=STUDY, capture_output=True, text=True, check=True).stdout.strip()
    return {
        "frozenInputs": {relative: sha256_file(os.path.join(STUDY, relative)) for relative in FROZEN},
        "jpack": JPACK_DIGEST,
        "python": {"implementation": platform.python_implementation(),
                   "version": platform.python_version()},
        "invocation": {
            "authority": AUTHORITY,
            "tool": TOOL,
            "arguments": {"caseId": "<id>"},
            "evaluate": ["<jpack>", "experimental", "evaluate", "<pack>", "--facts", "<facts>", "--format", "json"],
            "packsValidate": ["<jpack>", "packs", "validate", "--format", "json"],
            "packsTest": ["<jpack>", "packs", "test", "--format", "json"],
            "mcp": ["<jpack>", "mcp"],
            "environment": ["PATH", "HOME", "JPACK_CONFIG"],
            "cwd": "<the arm's generated project directory>",
        },
        "preregistrationCommit": revision,
        "note": "PREREGISTRATION.md governs; this file only pins bytes.",
    }


def cmd_freeze() -> None:
    cmd_validate()
    with open(FREEZE, "w") as handle:
        json.dump(freeze_body(), handle, indent=2)
        handle.write("\n")
    print("froze %d inputs; commit FREEZE.json before running" % len(FROZEN))


def verify_freeze() -> dict:
    if not os.path.exists(FREEZE):
        raise StudyError("no FREEZE.json; run freeze and commit it first")
    frozen = json.load(open(FREEZE))
    for relative, digest in frozen["frozenInputs"].items():
        actual = sha256_file(os.path.join(STUDY, relative))
        if actual != digest:
            raise StudyError("frozen input drifted: %s" % relative)
    committed = subprocess.run(
        ["git", "show", "HEAD:./FREEZE.json"], cwd=STUDY, capture_output=True)
    if committed.returncode != 0 or committed.stdout != open(FREEZE, "rb").read():
        raise StudyError("FREEZE.json is not the committed freeze")
    jpack = os.environ.get("JPACK_BIN", "")
    if not jpack or sha256_file(jpack) != frozen["jpack"]:
        raise StudyError("JPACK_BIN is not the frozen 0.14.0 binary")
    return frozen


def start_attempt() -> str:
    os.makedirs(TRIALS, exist_ok=True)
    number = 1
    while os.path.exists(os.path.join(TRIALS, "ATTEMPT-%d" % number)):
        number += 1
    attempt = os.path.join(TRIALS, "ATTEMPT-%d" % number)
    os.makedirs(attempt)
    fd = os.open(os.path.join(attempt, "STARTED"), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, b"attempt %d\n" % number)
    os.fsync(fd)
    os.close(fd)
    return attempt


def acquire(attempt: str) -> tuple[str, bytes, list[dict]]:
    """One fresh store, one session, one tools/call per record, in id order."""
    store = os.path.join(attempt, "gateway")
    key_path = os.path.join(attempt, "acquisition.key")
    key = os.urandom(32)
    with open(key_path, "wb") as handle:
        handle.write(key)
    env = {name: os.environ[name] for name in ("PATH", "HOME") if name in os.environ}
    env["RECORDS_DIR"] = os.path.join(STUDY, "records")
    proxy = subprocess.Popen(
        [sys.executable, os.path.join(LINE, "acquisition-proxy", "attest.py"),
         "wrap", store, key_path, "--authority", AUTHORITY, "--",
         sys.executable, os.path.join(STUDY, "source", "record_source.py")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env, text=True)

    def call(message):
        proxy.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        proxy.stdin.flush()
        return json.loads(proxy.stdout.readline())

    call({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})
    for index, case_id in enumerate(record_ids()):
        reply = call({"jsonrpc": "2.0", "id": index + 1, "method": "tools/call",
                      "params": {"name": TOOL, "arguments": {"caseId": case_id}}})
        if "error" in reply or reply.get("result", {}).get("caseId") != case_id:
            proxy.kill()
            raise StudyError("acquisition failed for %s: %r" % (case_id, reply))
    proxy.stdin.close()
    proxy.wait(timeout=30)

    sessions = os.listdir(os.path.join(store, "receipts"))
    if len(sessions) != 1:
        raise StudyError("the fresh store must hold exactly the spawned session")
    session = sessions[0]
    refs = []
    for index, case_id in enumerate(record_ids()):
        refs.append({"caseId": case_id, "sessionId": session, "callIndex": index})
    return store, key, refs


def check_acquisition(store: str, key: bytes, refs: list[dict]) -> list[dict]:
    """P-ACQ, beyond what admit() already runs per row."""
    ok, findings = attest.verify(store, key, expected_authority=AUTHORITY)
    receipts_dir = os.path.join(store, "receipts")
    if not ok or not os.path.isdir(receipts_dir):
        raise StudyError("acquisition verification failed: %r" % findings)
    manifest = []
    for ref in refs:
        receipt = json.load(open(os.path.join(
            receipts_dir, ref["sessionId"], "%d.json" % ref["callIndex"])))
        if receipt["tool"] != TOOL or receipt["authority"] != AUTHORITY or receipt.get("isError"):
            raise StudyError("receipt %d is not this study's call" % ref["callIndex"])
        expected_digest = "hmac-sha256:" + hmac_module.new(
            key, b"args:" + attest.canon({"caseId": ref["caseId"]}), hashlib.sha256).hexdigest()
        if receipt["argumentsDigest"] != expected_digest:
            raise StudyError("receipt %d does not answer this study's arguments" % ref["callIndex"])
        artifact = open(os.path.join(
            store, "artifacts", receipt["resultDigest"].split(":", 1)[1]), "rb").read()
        frozen_record = attest.canon(load_record(ref["caseId"]))
        if artifact != frozen_record:
            raise StudyError("retained artifact != frozen record for %s" % ref["caseId"])
        manifest.append({"caseId": ref["caseId"], "sessionId": ref["sessionId"],
                         "callIndex": ref["callIndex"], "resultDigest": receipt["resultDigest"]})
    return manifest


def jpack_run(jpack: str, args: list[str], cwd: str, config: str | None = None) -> dict:
    env = {name: os.environ[name] for name in ("PATH", "HOME") if name in os.environ}
    if config is not None:
        env["JPACK_CONFIG"] = config
    completed = subprocess.run([jpack] + args, cwd=cwd, env=env,
                               capture_output=True, text=True, timeout=120)
    try:
        return {"exit": completed.returncode, "payload": json.loads(completed.stdout)}
    except ValueError:
        raise StudyError("jpack %s emitted no JSON: %s" % (args, completed.stderr[:400]))


def write_project(attempt: str, arm: str, pack_file: str, matrix: dict) -> str:
    project = os.path.join(attempt, "projects", arm)
    os.makedirs(project)
    shutil.copy(os.path.join(STUDY, "packs", pack_file), os.path.join(project, "pack.json"))
    with open(os.path.join(project, "matrix.json"), "w") as handle:
        json.dump(matrix, handle, indent=2)
        handle.write("\n")
    with open(os.path.join(project, "jpack.json"), "w") as handle:
        json.dump({"configVersion": "1", "packs": {"screening": {
            "path": "pack.json", "matrix": "matrix.json"}}}, handle, indent=2)
        handle.write("\n")
    return project


def mcp_test_packs(jpack: str, project: str) -> dict:
    env = {name: os.environ[name] for name in ("PATH", "HOME") if name in os.environ}
    env["JPACK_CONFIG"] = os.path.join(project, "jpack.json")
    lines = (json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n" +
             json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                         "params": {"name": "experimental_test_packs"}}) + "\n")
    completed = subprocess.run([jpack, "mcp"], input=lines, cwd=project, env=env,
                               capture_output=True, text=True, timeout=120)
    for line in completed.stdout.splitlines():
        message = json.loads(line)
        if message.get("id") == 2:
            return message["result"]["structuredContent"]
    raise StudyError("the MCP run returned no experimental_test_packs result")


def cmd_run() -> None:
    frozen = verify_freeze()
    cmd_validate()
    jpack = os.environ["JPACK_BIN"]
    attempt = start_attempt()
    rule_digest = frozen["frozenInputs"]["transcription/record.rule.json"]

    store, key, refs = acquire(attempt)
    manifest = check_acquisition(store, key, refs)
    with open(os.path.join(attempt, "acquisition-manifest.json"), "w") as handle:
        json.dump(manifest, handle, indent=2)

    refs_path = os.path.join(attempt, "refs.json")
    with open(refs_path, "w") as handle:
        json.dump(refs, handle)
    matrix_b_path = os.path.join(attempt, "matrix-b.json")
    subprocess.run([sys.executable, os.path.join(STUDY, "transcription", "transcribe.py"),
                    "--store", store, "--key", os.path.join(attempt, "acquisition.key"),
                    "--refs", refs_path, "--rule", os.path.join(STUDY, "transcription", "record.rule.json"),
                    "--authority", AUTHORITY, "--out", matrix_b_path], check=True)
    matrix_b = json.load(open(matrix_b_path))

    lineages = study_gate.admit_matrix(matrix_b, refs, store, key, AUTHORITY, rule_digest)
    with open(os.path.join(attempt, "lineage.json"), "w") as handle:
        json.dump(lineages, handle, indent=2)

    # Arm A: the circular oracle — D's own dispositions copied verbatim.
    pack_d = os.path.join(STUDY, "packs", "vendor-screening-defective.pack.json")
    cases_a = []
    for row in matrix_b["cases"]:
        facts_path = os.path.join(attempt, "facts-tmp.json")
        with open(facts_path, "w") as handle:
            json.dump(row["facts"], handle)
        outcome = jpack_run(jpack, ["experimental", "evaluate", pack_d,
                                    "--facts", facts_path, "--format", "json"], attempt)
        cases_a.append({
            "id": row["id"],
            "origin": "circular:%s" % row["id"],
            "facts": row["facts"],
            "evidenceAvailability": {},
            "expectedDisposition": outcome["payload"]["disposition"],
        })
    os.remove(os.path.join(attempt, "facts-tmp.json"))
    matrix_a = {"matrixVersion": "1", "cases": cases_a}

    runs = {}
    for arm, pack_file, matrix in (
        ("A-circular-D", "vendor-screening-defective.pack.json", matrix_a),
        ("B-transcribed-D", "vendor-screening-defective.pack.json", matrix_b),
        ("Bprime-transcribed-C", "vendor-screening-correct.pack.json", matrix_b),
    ):
        project = write_project(attempt, arm, pack_file, matrix)
        config = os.path.join(project, "jpack.json")
        validated = jpack_run(jpack, ["packs", "validate", "--format", "json"], project, config)
        tested = jpack_run(jpack, ["packs", "test", "--format", "json"], project, config)
        runs[arm] = {"validate": validated, "test": tested}
    runs["Bprime-mcp"] = {"structuredContent": mcp_test_packs(jpack, os.path.join(attempt, "projects", "Bprime-transcribed-C"))}

    with open(os.path.join(attempt, "runs.json"), "w") as handle:
        json.dump(runs, handle, indent=2)
    with open(os.path.join(attempt, "DONE"), "w") as handle:
        handle.write("complete\n")
    print("run: retained under %s" % attempt)


def rows_of(test_payload: dict) -> dict:
    rows = {}
    for pack in test_payload["packs"]:
        for row in pack["rows"]:
            rows[row["id"]] = row
    return rows


def primary_attempt() -> tuple[int, str]:
    """The first attempt that reached DONE. Crashed attempts stay on disk
    with their exit metadata and are never overwritten (DEVIATIONS.md
    records why one exists)."""
    number = 1
    while os.path.exists(os.path.join(TRIALS, "ATTEMPT-%d" % number)):
        attempt = os.path.join(TRIALS, "ATTEMPT-%d" % number)
        if os.path.exists(os.path.join(attempt, "DONE")):
            return number, attempt
        number += 1
    raise StudyError("no completed attempt to score")


def cmd_score() -> None:
    number, attempt = primary_attempt()
    runs = json.load(open(os.path.join(attempt, "runs.json")))
    manifest = defect()
    sets = manifest["sets"]
    tables = manifest["expectedDispositions"]["perRecord"]
    results = {"attempt": number, "prerequisites": {}, "endpoints": {}}

    # P-A: the circular arm is a deterministic self-replay, completely run.
    test_a = runs["A-circular-D"]["test"]["payload"]
    rows_a = rows_of(test_a)
    results["prerequisites"]["P-A"] = {
        "status": test_a["status"],
        "rowIds": sorted(rows_a) == record_ids(),
        "mismatches": [i for i, r in rows_a.items() if r["status"] != "passed"],
        "pass": test_a["status"] == "passed" and sorted(rows_a) == record_ids(),
    }

    def endpoint(arm: str, under: str, expected_set: list[str]) -> dict:
        payload = runs[arm]["test"]["payload"]
        rows = rows_of(payload)
        table_conform, mismatched = [], []
        for case_id, row in rows.items():
            actual = json.loads(row["actual"]) if isinstance(row["actual"], str) else row["actual"]
            if actual != tables[case_id][under]:
                table_conform.append(case_id)
            if row["status"] != "passed":
                mismatched.append(case_id)
        return {
            "tableDivergences": sorted(table_conform),
            "mismatchedRows": sorted(mismatched),
            "expectedMismatches": sorted(expected_set),
            "pass": not table_conform and sorted(mismatched) == sorted(expected_set),
        }

    results["endpoints"]["E2"] = endpoint("B-transcribed-D", "underD", sets["F"] + sets["K"])
    results["endpoints"]["E3"] = endpoint("Bprime-transcribed-C", "underC", sets["K"])

    cli = dict(runs["Bprime-transcribed-C"]["test"]["payload"])
    wire = dict(runs["Bprime-mcp"]["structuredContent"])
    for field in ("command",):
        cli.pop(field, None)
        wire.pop(field, None)
    origins = all(row.get("origin", "").startswith("transcribed:")
                  for row in rows_of(runs["Bprime-transcribed-C"]["test"]["payload"]).values())
    results["endpoints"]["E5"] = {
        "validatePassed": runs["Bprime-transcribed-C"]["validate"]["payload"]["status"] == "valid",
        "originsEchoed": origins,
        "wireEqualsShell": cli == wire,
        "pass": runs["Bprime-transcribed-C"]["validate"]["payload"]["status"] == "valid"
                and origins and cli == wire,
    }
    results["pass"] = (results["prerequisites"]["P-A"]["pass"]
                       and all(e["pass"] for e in results["endpoints"].values()))
    with open(os.path.join(STUDY, "RESULTS.json"), "w") as handle:
        json.dump(results, handle, indent=2)
        handle.write("\n")
    print(json.dumps(results, indent=2))


COMMANDS = {"validate": cmd_validate, "freeze": cmd_freeze, "run": cmd_run, "score": cmd_score}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in COMMANDS:
        print("usage: study.py validate|freeze|run|score", file=sys.stderr)
        return 2
    try:
        COMMANDS[argv[1]]()
    except (StudyError, pnf_check.PNFError, study_gate.GateError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
