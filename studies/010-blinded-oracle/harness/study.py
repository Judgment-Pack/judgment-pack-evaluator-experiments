#!/usr/bin/env python3
"""Study 010 driver: lock | draw | validate | freeze | run | score
(PREREGISTRATION.md §8's ordering).

`lock` writes PROTOCOL-LOCK.json (the protocol lock) after proving pack C
matches POLICY.md on all 24 truth regions and every family patch applies.
The authoring call happens outside this driver (its artifacts land in
transcription/authoring/); records_compile.py turns its stdout into
records/. `draw` runs after the records commit is pushed: it computes the
target drand round from the commit's public timestamp, fetches the round,
derives the sampled index, writes DRAW.json, generates pack D, and derives
DEFECT.json's sets and per-record disposition tables. `freeze` then pins
everything executable and generated; `run` and `score` are Study 009's
repaired forms with the four-way E1.

Endpoints are computed only in `score`, from files `run` retained. `run`
refuses an unverified or uncommitted freeze, creates an exclusive attempt
ledger before any work, and never overwrites an attempt. The first DONE
attempt under the current freeze is primary.
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
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
LINE = os.path.dirname(os.path.dirname(STUDY))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LINE, "acquisition-proxy"))
sys.path.insert(0, os.path.join(LINE, "derivation-rule"))
sys.path.insert(0, os.path.join(LINE, "fabrication-gate"))

import attest  # noqa: E402
import pnf_check  # noqa: E402
import policy_mirror  # noqa: E402
import records_compile  # noqa: E402
import regions_check  # noqa: E402
import transcript_check  # noqa: E402
import importlib.util as _importlib_util

_spec = _importlib_util.spec_from_file_location("study_gate", os.path.join(HERE, "gate.py"))
study_gate = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(study_gate)

AUTHORITY = "study-010:records"
TOOL = "get_record"
JPACK_DIGEST = "sha256:417ee1ae86325713930e714b659432246c7845be1cdfa4c33f211bfad1ce970d"
GITHUB_REPO = "Judgment-Pack/judgment-pack-evaluator-experiments"
DRAND_INFO = "https://api.drand.sh/v2/beacons/default/info"
# Both relays are addressed by chain hash (the cryptographic identity, not
# the "default" alias) and must return byte-identical signatures.
DRAND_RELAYS = ("https://api.drand.sh", "https://drand.cloudflare.com")
REKOR = "https://rekor.sigstore.dev"
DRAW_OFFSET_SECONDS = 300
DRAW_DEADLINE_SECONDS = 3600
LOCK = os.path.join(STUDY, "PROTOCOL-LOCK.json")
FREEZE = os.path.join(STUDY, "FREEZE.json")
TRIALS = os.path.join(STUDY, "trials")
COMPLETION = os.path.join(STUDY, "transcription", "authoring", "completion.txt")
WITNESS_DIR = os.path.join(STUDY, "transcription", "witness")
WITNESS_PUB = os.path.join(STUDY, "transcription", "witness-pub.pem")
# The private key never enters the repository; substituting a different key
# is inert because every verification runs against the LOCKED public key.
WITNESS_KEY = os.environ.get("STUDY010_WITNESS_KEY") or os.path.expanduser("~/.study-010-witness.key")

# The protocol lock: everything that must exist, byte-pinned, before the
# authoring call may begin (PREREGISTRATION.md §8 step 1).
LOCKED = [
    "PREREGISTRATION.md",
    "PREREG-REVIEW.md",
    "policy/POLICY.md",
    "packs/vendor-screening-correct.pack.json",
    "FAMILY.json",
    "transcription/PROMPT.txt",
    "transcription/record.rule.json",
    "transcription/transcribe.py",
    "transcription/authoring_call.sh",
    "transcription/witness-pub.pem",
    "controls/k-wrong-1.json",
    "controls/k-wrong-2.json",
    "source/record_source.py",
    "harness/study.py",
    "harness/gate.py",
    "harness/pnf_check.py",
    "harness/policy_mirror.py",
    "harness/records_compile.py",
    "harness/regions_check.py",
    "harness/transcript_check.py",
    "harness/test_study.py",
    "../../acquisition-proxy/attest.py",
    "../../derivation-rule/derive.py",
    "../../fabrication-gate/gate.py",
]

# The artifact freeze adds what the authoring call, the compiler, the
# witness, and the draw generated (§8 step 3). Record files and remaining
# authoring retention are enumerated at freeze time.
GENERATED_BASE = [
    "RECORDS.md",
    "DRAW.json",
    "DEFECT.json",
    "packs/vendor-screening-defective.pack.json",
    "transcription/authoring/stdout.raw",
    "transcription/authoring/completion.txt",
    "transcription/authoring/CALL.json",
    "transcription/witness/INCLUSION.json",
    "transcription/witness/LOCK-INCLUSION.json",
    "transcription/witness/SEARCH.json",
]


class StudyError(Exception):
    pass


def sha256_file(path: str) -> str:
    return "sha256:" + hashlib.sha256(open(path, "rb").read()).hexdigest()


def _record_files() -> list[str]:
    records = os.path.join(STUDY, "records")
    if not os.path.isdir(records):
        return []
    return sorted("records/" + name for name in os.listdir(records) if name.endswith(".json"))


def frozen_inputs() -> list[str]:
    transcript_dir = os.path.join(STUDY, "transcription", "authoring")
    transcripts = sorted(
        "transcription/authoring/" + name for name in os.listdir(transcript_dir)
        if name not in ("stdout.raw", "CALL.json"))
    return LOCKED + GENERATED_BASE + transcripts + _record_files()


def family() -> dict:
    return json.load(open(os.path.join(STUDY, "FAMILY.json")))


def defect() -> dict:
    return json.load(open(os.path.join(STUDY, "DEFECT.json")))


def record_ids() -> list[str]:
    """Every id an arm evaluates: authored records plus the K controls."""
    authored = [name[:-5] for name in os.listdir(os.path.join(STUDY, "records"))
                if name.endswith(".json")]
    return sorted(authored + ["k-wrong-1", "k-wrong-2"])


def load_record(case_id: str) -> dict:
    for base in ("records", "controls"):
        path = os.path.join(STUDY, base, case_id + ".json")
        if os.path.exists(path):
            return json.load(open(path))
    raise StudyError("no record file for %s" % case_id)


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


def wrapper(outcome_id: str) -> dict:
    return {"kind": "outcome", "outcomeId": outcome_id, "reasons": [], "handoff": {"state": "none"}}


def unresolved(reasons: list[str]) -> dict:
    return {"kind": "unresolved", "reasons": sorted(reasons), "handoff": {"state": "none"}}


def table_entry(vendor: dict, mutation: dict) -> dict:
    """The derived {underC, underD} row for one record (§5 step 5): underC is
    the policy mirror's outcome (regions_check proved pack C agrees on every
    truth region); underD diverges to the registered unresolved reasons
    exactly on the sampled predicate."""
    verdict = policy_mirror.verdict(vendor)
    under_c = wrapper(verdict)
    if policy_mirror.predicate_matches(mutation["predicate"], vendor):
        for entry in mutation["reasonsUnderD"]:
            personal = entry["handlesPersonalData"]
            if personal is None or vendor["handlesPersonalData"] is personal:
                return {"underC": under_c, "underD": unresolved(entry["reasons"])}
        raise StudyError("no reasonsUnderD entry matches the record")
    return {"underC": under_c, "underD": under_c}


def http_json(url: str, body: dict | None = None, timeout: int = 30) -> dict:
    request = urllib.request.Request(url)
    # Cloudflare's relay bot-filters urllib's default User-Agent with 403.
    request.add_header("User-Agent", "study-010-harness/1")
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, data=data, timeout=timeout) as response:
        return json.loads(response.read().decode())


def http_json_retry(url: str, body: dict | None = None, attempts: int = 5) -> dict:
    last = None
    for attempt in range(attempts):
        try:
            return http_json(url, body, timeout=60)
        except Exception as error:  # noqa: BLE001 - refused after the loop
            last = error
            time.sleep(5 * (attempt + 1))
    raise StudyError("unreachable after %d attempts: %s (%r)" % (attempts, url, last))


# ------------------------------------------------------------- witness


def manifest_bytes(prefix: str, oid: str) -> bytes:
    if len(oid) != 40 or any(c not in "0123456789abcdef" for c in oid):
        raise StudyError("not a 40-hex commit OID: %r" % oid)
    return ("%s\n%s\n" % (prefix, oid)).encode("ascii")


def witness_sign(payload: bytes) -> bytes:
    """P-256/SHA-256 signature with the uncommitted witness private key."""
    import tempfile
    if not os.path.exists(WITNESS_KEY):
        raise StudyError("no witness private key at %s" % WITNESS_KEY)
    with tempfile.NamedTemporaryFile(delete=False) as handle:
        handle.write(payload)
        payload_path = handle.name
    try:
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", WITNESS_KEY, payload_path],
            capture_output=True, check=True)
        return completed.stdout
    finally:
        os.unlink(payload_path)


def witness_verify(payload: bytes, signature: bytes) -> None:
    import tempfile
    paths = {}
    for name, blob in (("payload", payload), ("signature", signature)):
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            handle.write(blob)
            paths[name] = handle.name
    try:
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify", WITNESS_PUB,
             "-signature", paths["signature"], paths["payload"]],
            capture_output=True)
        if completed.returncode != 0:
            raise StudyError("the witness signature does not verify")
    finally:
        for path in paths.values():
            os.unlink(path)


def rekor_include(payload: bytes) -> dict:
    """Upload one hashedrekord entry over payload; return the log's record."""
    import base64
    signature = witness_sign(payload)
    body = {
        "kind": "hashedrekord", "apiVersion": "0.0.1",
        "spec": {
            "signature": {
                "content": base64.b64encode(signature).decode(),
                "publicKey": {"content": base64.b64encode(open(WITNESS_PUB, "rb").read()).decode()},
            },
            "data": {"hash": {"algorithm": "sha256",
                              "value": hashlib.sha256(payload).hexdigest()}},
        },
    }
    entry = http_json_retry(REKOR + "/api/v1/log/entries", body)
    uuid, record = next(iter(entry.items()))
    return {"uuid": uuid, "logIndex": record["logIndex"],
            "integratedTime": record["integratedTime"],
            "body": record["body"], "verification": record.get("verification", {}),
            "signature": base64.b64encode(signature).decode(),
            "artifactSha256": hashlib.sha256(payload).hexdigest(),
            "manifest": payload.decode("ascii")}


def head_oid(repo_root: str) -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root,
                          capture_output=True, text=True, check=True).stdout.strip()


# ---------------------------------------------------------------- lock


def cmd_lock() -> None:
    jpack = os.environ.get("JPACK_BIN", "")
    if not jpack or sha256_file(jpack) != JPACK_DIGEST:
        raise StudyError("JPACK_BIN must be the pinned v0.15.0 binary")
    if not os.path.exists(WITNESS_PUB):
        os.makedirs(os.path.dirname(WITNESS_PUB), exist_ok=True)
        subprocess.run(["openssl", "ecparam", "-genkey", "-name", "prime256v1",
                        "-noout", "-out", WITNESS_KEY], check=True, capture_output=True)
        os.chmod(WITNESS_KEY, 0o600)
        subprocess.run(["openssl", "ec", "-in", WITNESS_KEY, "-pubout",
                        "-out", WITNESS_PUB], check=True, capture_output=True)
    pnf_check.check(json.load(open(os.path.join(STUDY, "transcription/record.rule.json"))))
    correct = json.load(open(os.path.join(STUDY, "packs/vendor-screening-correct.pack.json")))
    manifest = family()
    if [m["index"] for m in manifest["mutations"]] != list(range(6)):
        raise StudyError("FAMILY.json must hold exactly indexes 0-5 in order")
    for mutation in manifest["mutations"]:
        patched = apply_patch(correct, mutation["patch"])
        if patched == correct:
            raise StudyError("mutation %d does not change the pack" % mutation["index"])
    for control in ("k-wrong-1", "k-wrong-2"):
        record = json.load(open(os.path.join(STUDY, "controls", control + ".json")))
        vendor = record["vendor"]
        if record["decision"]["outcome"] == policy_mirror.verdict(vendor):
            raise StudyError("%s is not wrong against POLICY.md" % control)
        for mutation in manifest["mutations"]:
            if policy_mirror.predicate_matches(mutation["predicate"], vendor):
                raise StudyError("%s intersects family predicate %d" % (control, mutation["index"]))
    checked = regions_check.check(jpack)
    info = http_json_retry(DRAND_INFO)
    body = {
        "lockedInputs": {relative: sha256_file(os.path.join(STUDY, relative))
                         for relative in LOCKED},
        "jpack": JPACK_DIGEST,
        "python": {"implementation": platform.python_implementation(),
                   "version": platform.python_version()},
        "probesChecked": checked,
        "drand": {
            "chainHash": info["chain_hash"],
            "publicKey": info["public_key"],
            "genesisTime": info["genesis_time"],
            "periodSeconds": info["period"],
            "scheme": info["scheme"],
            "relays": list(DRAND_RELAYS),
            "rawInfo": info,
        },
        "rekor": {"log": REKOR, "witnessPublicKey": sha256_file(WITNESS_PUB)},
        "drawRule": {
            "publication": "the Rekor inclusion's integratedTime over the records-commit manifest",
            "offsetSeconds": DRAW_OFFSET_SECONDS,
            "deadlineSeconds": DRAW_DEADLINE_SECONDS,
            "round": "the first R with genesisTime + (R-1)*period >= integratedTime + offset",
            "preimage": "ascii('study-010-draw-v1\\n' + randomness_hex + '\\n' + commit_oid_hex + '\\n' + family_digest_hex + '\\n')",
            "index": "int.from_bytes(sha256(preimage).digest(), 'big') mod 6, selecting the FAMILY.json entry with that index member",
            "familyDigest": "the sha256 hex digest of the locked FAMILY.json bytes",
            "randomness": "sha256(signature bytes), drand's chained-scheme definition",
        },
        "githubRepo": GITHUB_REPO,
        "note": "PREREGISTRATION.md governs; this file pins the protocol before authoring. It does not digest itself; the lock commit binds its bytes.",
    }
    with open(LOCK, "w") as handle:
        json.dump(body, handle, indent=2)
        handle.write("\n")
    print("locked %d inputs (%d probes agree); commit, push, then timestamp-lock"
          % (len(LOCKED), checked))


def verify_lock() -> dict:
    if not os.path.exists(LOCK):
        raise StudyError("no PROTOCOL-LOCK.json; run lock and commit it first")
    locked = json.load(open(LOCK))
    for relative, digest in locked["lockedInputs"].items():
        if sha256_file(os.path.join(STUDY, relative)) != digest:
            raise StudyError("locked input drifted: %s" % relative)
    committed = subprocess.run(
        ["git", "show", "HEAD:./PROTOCOL-LOCK.json"], cwd=STUDY, capture_output=True)
    if committed.returncode != 0 or committed.stdout != open(LOCK, "rb").read():
        raise StudyError("PROTOCOL-LOCK.json is not the committed lock")
    return locked


# ------------------------------------------- timestamp-lock and publish


def records_commit() -> str:
    revision = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "records", "RECORDS.md",
         "transcription/authoring"],
        cwd=STUDY, capture_output=True, text=True, check=True).stdout.strip()
    if not revision:
        raise StudyError("no records commit exists yet")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", "records", "RECORDS.md",
         "transcription/authoring"],
        cwd=STUDY, capture_output=True, text=True, check=True).stdout.strip()
    if status:
        raise StudyError("records/ or the authoring artifacts are not committed clean")
    return revision


def cmd_timestamp_lock() -> None:
    verify_lock()
    os.makedirs(WITNESS_DIR, exist_ok=True)
    target = os.path.join(WITNESS_DIR, "LOCK-INCLUSION.json")
    if os.path.exists(target):
        raise StudyError("the lock is already timestamped")
    entry = rekor_include(manifest_bytes("study-010-lock-commit", head_oid(STUDY)))
    with open(target, "w") as handle:
        json.dump(entry, handle, indent=2)
        handle.write("\n")
    print("lock timestamped: logIndex %d, integratedTime %d; commit the inclusion"
          % (entry["logIndex"], entry["integratedTime"]))


def cmd_publish() -> None:
    verify_lock()
    records_compile.cmd_verify(COMPLETION)
    transcript_check.check(
        os.path.join(STUDY, "transcription/authoring/session.jsonl"),
        os.path.join(STUDY, "transcription/PROMPT.txt"),
        COMPLETION,
        os.path.join(STUDY, "transcription/authoring/CALL.json"))
    revision = records_commit()
    os.makedirs(WITNESS_DIR, exist_ok=True)
    target = os.path.join(WITNESS_DIR, "INCLUSION.json")
    if os.path.exists(target):
        raise StudyError("a records publication already exists; it is binding")
    entry = rekor_include(manifest_bytes("study-010-records-commit", revision))
    entry["recordsCommit"] = revision
    with open(target, "w") as handle:
        json.dump(entry, handle, indent=2)
        handle.write("\n")
    print("published: records commit %s at integratedTime %d (logIndex %d); commit and push, then draw"
          % (revision[:12], entry["integratedTime"], entry["logIndex"]))


def cmd_witness() -> None:
    """The online minimal-logIndex check: no earlier inclusion under the
    witness key may exist. Rekor's search index lags; run this before the
    freeze and again in the post-run review."""
    import base64
    inclusion = json.load(open(os.path.join(WITNESS_DIR, "INCLUSION.json")))
    body = {"publicKey": {"format": "x509",
                          "content": base64.b64encode(open(WITNESS_PUB, "rb").read()).decode()}}
    hits = http_json_retry(REKOR + "/api/v1/index/retrieve", body)
    known = {inclusion["uuid"]}
    lock_path = os.path.join(WITNESS_DIR, "LOCK-INCLUSION.json")
    if os.path.exists(lock_path):
        known.add(json.load(open(lock_path))["uuid"])
    records = []
    for uuid in hits:
        entry = http_json_retry(REKOR + "/api/v1/log/entries/" + uuid)
        record = next(iter(entry.values()))
        records.append({"uuid": uuid, "logIndex": record["logIndex"]})
    strangers = [r for r in records if r["uuid"] not in known]
    # Before the freeze, SEARCH.json may be overwritten (the wait-for-index
    # loop). Once FREEZE.json exists it is a frozen input, so later re-runs
    # — the post-run review's included — land in numbered siblings.
    target = os.path.join(WITNESS_DIR, "SEARCH.json")
    if os.path.exists(FREEZE):
        number = 2
        while os.path.exists(target):
            target = os.path.join(WITNESS_DIR, "SEARCH-%d.json" % number)
            number += 1
    with open(target, "w") as handle:
        json.dump({"queried": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "hits": records, "known": sorted(known)}, handle, indent=2)
        handle.write("\n")
    # Every inclusion under the key must be one of the two the protocol
    # made; with strangers refused, the records inclusion is minimal among
    # records-manifest entries by construction.
    if strangers:
        raise StudyError("unknown inclusions under the witness key: %r" % strangers)
    indexed = [r["logIndex"] for r in records if r["uuid"] == inclusion["uuid"]]
    print("witness: %d inclusions under the key, all known (records entry %s)"
          % (len(records), "logIndex %d" % indexed[0] if indexed else "not yet indexed"))


# ---------------------------------------------------------------- draw


def fetch_round(chain_hash: str, target_round: int) -> list[dict]:
    """The fixed round from both relays, by chain hash, byte-equal."""
    responses = []
    for relay in DRAND_RELAYS:
        responses.append(http_json_retry(
            "%s/%s/public/%d" % (relay, chain_hash, target_round), attempts=8))
    signatures = {response["signature"] for response in responses}
    rounds = {response["round"] for response in responses}
    if len(signatures) != 1 or rounds != {target_round}:
        raise StudyError("the relays disagree: %r" % responses)
    return responses


def draw_index(randomness_hex: str, commit_hex: str, family_hex: str) -> tuple[bytes, int]:
    if len(randomness_hex) != 64 or len(commit_hex) != 40 or len(family_hex) != 64:
        raise StudyError("draw preimage fields are not the registered widths")
    preimage = ("study-010-draw-v1\n%s\n%s\n%s\n"
                % (randomness_hex, commit_hex, family_hex)).encode("ascii")
    return preimage, int.from_bytes(hashlib.sha256(preimage).digest(), "big") % 6


def cmd_draw() -> None:
    locked = verify_lock()
    records_compile.cmd_verify(COMPLETION)
    revision = records_commit()
    inclusion = json.load(open(os.path.join(WITNESS_DIR, "INCLUSION.json")))
    if inclusion["recordsCommit"] != revision:
        raise StudyError("the publication binds %s, not the records commit %s"
                         % (inclusion["recordsCommit"], revision))
    expected_manifest = manifest_bytes("study-010-records-commit", revision)
    if inclusion["artifactSha256"] != hashlib.sha256(expected_manifest).hexdigest():
        raise StudyError("the inclusion's artifact digest does not bind the records commit")
    import base64
    witness_verify(expected_manifest, base64.b64decode(inclusion["signature"]))
    published = inclusion["integratedTime"]
    genesis = locked["drand"]["genesisTime"]
    period = locked["drand"]["periodSeconds"]
    target_time = published + locked["drawRule"]["offsetSeconds"]
    target_round = (target_time - genesis + period - 1) // period + 1
    scheduled = genesis + (target_round - 1) * period
    if scheduled < target_time:
        raise StudyError("round arithmetic is wrong: %d < %d" % (scheduled, target_time))
    if time.time() > scheduled + locked["drawRule"]["deadlineSeconds"]:
        raise StudyError("the retrieval deadline for round %d has passed; the attempt is pipeline-invalid"
                         % target_round)
    while time.time() < scheduled:
        time.sleep(min(15, scheduled - time.time() + 1))
    responses = fetch_round(locked["drand"]["chainHash"], target_round)
    signature = responses[0]["signature"]
    # drand's chained scheme defines the round's randomness as
    # sha256(signature); the signature itself is the externally verifiable
    # object (BLS over previous_signature + round, against the chain key).
    randomness = hashlib.sha256(bytes.fromhex(signature)).hexdigest()
    family_digest = hashlib.sha256(
        open(os.path.join(STUDY, "FAMILY.json"), "rb").read()).hexdigest()
    preimage, index = draw_index(randomness, revision, family_digest)
    draw = {
        "recordsCommit": revision,
        "publication": inclusion,
        "publishedEpoch": published,
        "targetRound": target_round,
        "scheduledTime": scheduled,
        "randomness": randomness,
        "signature": signature,
        "previousSignature": responses[0].get("previous_signature", ""),
        "relayResponses": responses,
        "chain": locked["drand"],
        "familyDigest": "sha256:" + family_digest,
        "preimage": preimage.decode("ascii"),
        "index": index,
    }
    with open(os.path.join(STUDY, "DRAW.json"), "w") as handle:
        json.dump(draw, handle, indent=2)
        handle.write("\n")

    mutation = family()["mutations"][index]
    correct = json.load(open(os.path.join(STUDY, "packs/vendor-screening-correct.pack.json")))
    defective = apply_patch(correct, mutation["patch"])
    with open(os.path.join(STUDY, "packs/vendor-screening-defective.pack.json"), "w") as handle:
        json.dump(defective, handle, indent=2)
        handle.write("\n")

    sets = {"H": [], "Q": [], "F": [], "K": ["k-wrong-1", "k-wrong-2"]}
    tables = {}
    for case_id in record_ids():
        record = load_record(case_id)
        vendor = record["vendor"]
        tables[case_id] = table_entry(vendor, mutation)
        if case_id in sets["K"]:
            continue
        if policy_mirror.predicate_matches(mutation["predicate"], vendor):
            sets["F"].append(case_id)
        if record["decision"]["outcome"] == policy_mirror.verdict(vendor):
            sets["H"].append(case_id)
        else:
            sets["Q"].append(case_id)
    manifest = {
        "sampledIndex": index,
        "mutation": mutation,
        "patch": mutation["patch"],
        "sets": {name: sorted(ids) for name, ids in sets.items()},
        "expectedDispositions": {"perRecord": tables},
    }
    with open(os.path.join(STUDY, "DEFECT.json"), "w") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    in_h = sorted(set(sets["H"]) & set(sets["F"]))
    print("draw: round %d -> index %d (%s); |F|=%d, |H∩F|=%d; commit DRAW.json, DEFECT.json, pack D"
          % (target_round, index, mutation["title"], len(sets["F"]), len(in_h)))


# ---------------------------------------------------------------- validate


def cmd_validate() -> None:
    verify_lock()
    for relative in frozen_inputs():
        if not os.path.exists(os.path.join(STUDY, relative)):
            raise StudyError("missing input: " + relative)
    records_compile.cmd_verify(COMPLETION)
    transcript_check.check(
        os.path.join(STUDY, "transcription/authoring/session.jsonl"),
        os.path.join(STUDY, "transcription/PROMPT.txt"),
        COMPLETION,
        os.path.join(STUDY, "transcription/authoring/CALL.json"))
    manifest = defect()
    sets = manifest["sets"]
    everyone = record_ids()
    accepted = sorted(sets["H"] + sets["Q"])
    if sorted(accepted + sets["K"]) != everyone:
        raise StudyError("H+Q+K do not cover exactly the record ids")
    if set(sets["H"]) & set(sets["Q"]):
        raise StudyError("H and Q intersect")
    if not set(sets["F"]).isdisjoint(sets["K"]):
        raise StudyError("F must not contain controls")
    tables = manifest["expectedDispositions"]["perRecord"]
    if set(tables) != set(everyone):
        raise StudyError("the disposition tables do not cover exactly the record ids")
    mutation = manifest["mutation"]
    fam = family()["mutations"][manifest["sampledIndex"]]
    if mutation != fam:
        raise StudyError("DEFECT.json's mutation is not FAMILY.json's at the sampled index")
    draw = json.load(open(os.path.join(STUDY, "DRAW.json")))
    if draw["index"] != manifest["sampledIndex"]:
        raise StudyError("DRAW.json and DEFECT.json disagree on the index")
    family_digest = hashlib.sha256(open(os.path.join(STUDY, "FAMILY.json"), "rb").read()).hexdigest()
    if draw["familyDigest"] != "sha256:" + family_digest:
        raise StudyError("DRAW.json's family digest is not the locked family")
    preimage, index = draw_index(draw["randomness"], draw["recordsCommit"], family_digest)
    if preimage.decode("ascii") != draw["preimage"] or index != draw["index"]:
        raise StudyError("the sampled index does not recompute from the draw")
    if hashlib.sha256(bytes.fromhex(draw["signature"])).hexdigest() != draw["randomness"]:
        raise StudyError("the draw's randomness is not sha256(signature)")
    signatures = {response["signature"] for response in draw["relayResponses"]}
    rounds = {response["round"] for response in draw["relayResponses"]}
    if len(draw["relayResponses"]) < 2 or signatures != {draw["signature"]} \
            or rounds != {draw["targetRound"]}:
        raise StudyError("the retained relay responses do not agree on the round")
    inclusion = draw["publication"]
    if inclusion["recordsCommit"] != draw["recordsCommit"]:
        raise StudyError("the publication does not bind the records commit")
    expected_manifest = manifest_bytes("study-010-records-commit", draw["recordsCommit"])
    if inclusion["artifactSha256"] != hashlib.sha256(expected_manifest).hexdigest():
        raise StudyError("the inclusion's artifact digest does not bind the records commit")
    import base64
    witness_verify(expected_manifest, base64.b64decode(inclusion["signature"]))
    on_disk = json.load(open(os.path.join(WITNESS_DIR, "INCLUSION.json")))
    if on_disk != inclusion:
        raise StudyError("DRAW.json's publication is not the retained inclusion")
    locked = json.load(open(LOCK))
    genesis = locked["drand"]["genesisTime"]
    period = locked["drand"]["periodSeconds"]
    target_time = inclusion["integratedTime"] + locked["drawRule"]["offsetSeconds"]
    expected_round = (target_time - genesis + period - 1) // period + 1
    if expected_round != draw["targetRound"]:
        raise StudyError("the target round does not recompute from the publication clock")
    if genesis + (draw["targetRound"] - 1) * period != draw["scheduledTime"]:
        raise StudyError("the scheduled time does not recompute")
    for case_id in everyone:
        record = load_record(case_id)
        vendor = record["vendor"]
        if record["caseId"] != case_id:
            raise StudyError("record %s misnames itself" % case_id)
        expected = table_entry(vendor, mutation)
        if tables[case_id] != expected:
            raise StudyError("table row %s does not recompute" % case_id)
        in_f = policy_mirror.predicate_matches(mutation["predicate"], vendor)
        if case_id in sets["K"]:
            if in_f:
                raise StudyError("control %s intersects the sampled predicate" % case_id)
            if record["decision"]["outcome"] == policy_mirror.verdict(vendor):
                raise StudyError("control %s is not wrong against POLICY.md" % case_id)
            continue
        if in_f != (case_id in sets["F"]):
            raise StudyError("record %s disagrees with the F set" % case_id)
        concordant = record["decision"]["outcome"] == policy_mirror.verdict(vendor)
        if concordant != (case_id in sets["H"]):
            raise StudyError("record %s disagrees with the H/Q split" % case_id)
    correct = json.load(open(os.path.join(STUDY, "packs/vendor-screening-correct.pack.json")))
    defective = json.load(open(os.path.join(STUDY, "packs/vendor-screening-defective.pack.json")))
    if apply_patch(correct, manifest["patch"]) != defective:
        raise StudyError("C with the sampled patch applied is not D")
    pnf_check.check(json.load(open(os.path.join(STUDY, "transcription/record.rule.json"))))
    print("validate: ok (%d records+controls, draw bound, patch bound, rule is the registered projection)"
          % len(everyone))


# ---------------------------------------------------------------- freeze


def freeze_body() -> dict:
    revision = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "PREREGISTRATION.md"],
        cwd=STUDY, capture_output=True, text=True, check=True).stdout.strip()
    return {
        "frozenInputs": {relative: sha256_file(os.path.join(STUDY, relative))
                         for relative in frozen_inputs()},
        "protocolLock": sha256_file(LOCK),
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
    search_path = os.path.join(WITNESS_DIR, "SEARCH.json")
    if not os.path.exists(search_path):
        raise StudyError("run witness (online minimal-logIndex check) before freezing")
    search = json.load(open(search_path))
    inclusion = json.load(open(os.path.join(WITNESS_DIR, "INCLUSION.json")))
    if inclusion["uuid"] not in [hit["uuid"] for hit in search["hits"]]:
        raise StudyError("the records inclusion is not yet indexed; re-run witness until it is")
    with open(FREEZE, "w") as handle:
        json.dump(freeze_body(), handle, indent=2)
        handle.write("\n")
    print("froze %d inputs; commit FREEZE.json before running" % len(frozen_inputs()))


def verify_freeze() -> dict:
    if not os.path.exists(FREEZE):
        raise StudyError("no FREEZE.json; run freeze and commit it first")
    frozen = json.load(open(FREEZE))
    for relative, digest in frozen["frozenInputs"].items():
        if sha256_file(os.path.join(STUDY, relative)) != digest:
            raise StudyError("frozen input drifted: %s" % relative)
    if frozen["protocolLock"] != sha256_file(LOCK):
        raise StudyError("the freeze does not bind the committed protocol lock")
    committed = subprocess.run(
        ["git", "show", "HEAD:./FREEZE.json"], cwd=STUDY, capture_output=True)
    if committed.returncode != 0 or committed.stdout != open(FREEZE, "rb").read():
        raise StudyError("FREEZE.json is not the committed freeze")
    jpack = os.environ.get("JPACK_BIN", "")
    if not jpack or sha256_file(jpack) != frozen["jpack"]:
        raise StudyError("JPACK_BIN is not the frozen 0.15.0 binary")
    if frozen["python"]["version"] != platform.python_version():
        raise StudyError("the interpreter is not the frozen one")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", frozen["preregistrationCommit"], "HEAD"],
        cwd=STUDY)
    if ancestry.returncode != 0:
        raise StudyError("the preregistration commit is not an ancestor of HEAD")
    return frozen


# ---------------------------------------------------------------- run


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
    env["RECORDS_DIRS"] = os.pathsep.join(
        [os.path.join(STUDY, "records"), os.path.join(STUDY, "controls")])
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
    if proxy.wait(timeout=30) != 0:
        raise StudyError("the acquisition proxy exited nonzero")

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
    session_dir = os.path.join(receipts_dir, refs[0]["sessionId"])
    receipt_files = [n for n in os.listdir(session_dir) if n.endswith(".json")]
    if len(receipt_files) != len(refs):
        raise StudyError("the store holds %d receipts for %d records" % (len(receipt_files), len(refs)))
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


def seal_attempt(attempt: str) -> None:
    manifest = {}
    for base, _, names in os.walk(attempt):
        for name in names:
            path = os.path.join(base, name)
            manifest[os.path.relpath(path, attempt)] = sha256_file(path)
    with open(os.path.join(attempt, "MANIFEST.json"), "w") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
    for base, _, names in os.walk(attempt):
        for name in names:
            os.chmod(os.path.join(base, name), 0o444)


def cmd_run() -> None:
    frozen = verify_freeze()
    cmd_validate()
    jpack = os.environ["JPACK_BIN"]
    attempt = start_attempt()
    with open(os.path.join(attempt, "FREEZE-DIGEST"), "w") as handle:
        handle.write(sha256_file(FREEZE) + "\n")
    try:
        _run_body(frozen, jpack, attempt)
    except BaseException as error:
        # Every exit receives a terminal state and a seal (PREREGISTRATION.md
        # §6): a crashed primary attempt scores pipeline-invalid, it is not
        # skipped.
        import traceback
        with open(os.path.join(attempt, "CRASHED.json"), "w") as handle:
            json.dump({"error": repr(error), "traceback": traceback.format_exc(),
                       "argv": sys.argv, "freeze": sha256_file(FREEZE)}, handle, indent=2)
        seal_attempt(attempt)
        raise


def _run_body(frozen, jpack, attempt) -> None:
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
    runs["Bprime-mcp"] = {"structuredContent": mcp_test_packs(
        jpack, os.path.join(attempt, "projects", "Bprime-transcribed-C"))}

    with open(os.path.join(attempt, "runs.json"), "w") as handle:
        json.dump(runs, handle, indent=2)
    with open(os.path.join(attempt, "DONE"), "w") as handle:
        handle.write("complete\n")
    seal_attempt(attempt)
    print("run: retained and sealed under %s" % attempt)


# ---------------------------------------------------------------- score


def primary_attempt() -> tuple[int, str, bool]:
    """(number, path, done) for the FIRST attempt started under the CURRENT
    committed freeze, whatever its terminal state (PREREGISTRATION.md §6): a
    crashed primary scores pipeline-invalid rather than being skipped. Later
    attempts are sensitivity data recorded in DEVIATIONS.md."""
    current = sha256_file(FREEZE)
    number = 1
    while os.path.exists(os.path.join(TRIALS, "ATTEMPT-%d" % number)):
        attempt = os.path.join(TRIALS, "ATTEMPT-%d" % number)
        digest_path = os.path.join(attempt, "FREEZE-DIGEST")
        bound = os.path.exists(digest_path) and open(digest_path).read().strip() == current
        if bound:
            verify_seal(attempt)
            return number, attempt, os.path.exists(os.path.join(attempt, "DONE"))
        number += 1
    raise StudyError("no attempt under the current freeze")


def verify_seal(attempt: str) -> None:
    manifest = json.load(open(os.path.join(attempt, "MANIFEST.json")))
    for relative, digest in manifest.items():
        if relative == "MANIFEST.json":
            continue
        if sha256_file(os.path.join(attempt, relative)) != digest:
            raise StudyError("the sealed attempt drifted: %s" % relative)


def rows_of(test_payload: dict) -> dict:
    rows = {}
    total = 0
    for pack in test_payload["packs"]:
        for row in pack["rows"]:
            total += 1
            rows[row["id"]] = row
    if total != len(rows):
        raise StudyError("duplicate row ids in a test payload")
    return rows


def parse_disposition(value):
    return json.loads(value) if isinstance(value, str) else value


def coverage_profile(sets: dict, manifest: dict) -> list[dict]:
    profile = []
    for mutation in family()["mutations"]:
        in_h = sorted(case_id for case_id in sets["H"]
                      if policy_mirror.predicate_matches(
                          mutation["predicate"], load_record(case_id)["vendor"]))
        in_q = sorted(case_id for case_id in sets["Q"]
                      if policy_mirror.predicate_matches(
                          mutation["predicate"], load_record(case_id)["vendor"]))
        profile.append({"index": mutation["index"], "title": mutation["title"],
                        "sampled": mutation["index"] == manifest["sampledIndex"],
                        "H": in_h, "Q": in_q, "covered": bool(in_h)})
    return profile


def write_results(results: dict) -> None:
    with open(os.path.join(STUDY, "RESULTS.json"), "w") as handle:
        json.dump(results, handle, indent=2)
        handle.write("\n")
    print(json.dumps(results, indent=2))


def cmd_score() -> None:
    verify_freeze()
    number, attempt, done = primary_attempt()
    manifest = defect()
    sets = {name: set(ids) for name, ids in manifest["sets"].items()}
    h_and_f = sorted(sets["H"] & sets["F"])
    q_and_f = sorted(sets["Q"] & sets["F"])
    sizes = {"records": len(sets["H"] | sets["Q"]), "H": len(sets["H"]),
             "Q": len(sets["Q"]), "F": len(sets["F"]),
             "HandF": len(h_and_f), "QandF": len(q_and_f)}
    if not done:
        # E1's ordered partition, step 1: the primary attempt has no DONE —
        # pipeline-invalid, with the crash retained beside it.
        crash = {}
        crash_path = os.path.join(attempt, "CRASHED.json")
        if os.path.exists(crash_path):
            crash = json.load(open(crash_path))
        write_results({
            "attempt": number, "sampledIndex": manifest["sampledIndex"],
            "prerequisites": {"terminalState": "crashed"},
            "endpoints": {
                "E1": {"outcome": "pipeline-invalid", "HandF": h_and_f,
                       "QandF": q_and_f, "F": sorted(sets["F"]),
                       "crash": crash.get("error", "no DONE marker")},
                "E3": {"sizes": sizes,
                       "coverageProfile": coverage_profile(sets, manifest)},
            },
            "pipelineValid": False,
        })
        return
    runs = json.load(open(os.path.join(attempt, "runs.json")))
    matrix_b = json.load(open(os.path.join(attempt, "matrix-b.json")))
    origins = {row["id"]: row["origin"] for row in matrix_b["cases"]}
    tables = manifest["expectedDispositions"]["perRecord"]
    everyone = record_ids()
    results = {"attempt": number, "prerequisites": {}, "endpoints": {},
               "sampledIndex": manifest["sampledIndex"]}
    pipeline_valid = True

    # P-A: complete deterministic self-replay — full row set, one valid
    # actual disposition per row, all passed, run status passed.
    test_a = runs["A-circular-D"]["test"]["payload"]
    rows_a = rows_of(test_a)
    pa_ok = (test_a["status"] == "passed" and sorted(rows_a) == everyone
             and all(r["status"] == "passed" and parse_disposition(r.get("actual"))
                     for r in rows_a.values()))
    results["prerequisites"]["P-A"] = {"status": test_a["status"],
                                       "rowIds": sorted(rows_a) == everyone,
                                       "pass": bool(pa_ok)}
    pipeline_valid = pipeline_valid and bool(pa_ok)

    def arm_report(arm: str, under: str) -> dict:
        """Recompute an arm's mismatch set and hold it to the derived tables
        (E2's derived-not-hard-coded rule)."""
        payload = runs[arm]["test"]["payload"]
        rows = rows_of(payload)
        if sorted(rows) != everyone:
            raise StudyError("%s did not run the full row set" % arm)
        table_divergences, entailed, reported = [], [], []
        for case_id, row in rows.items():
            actual = parse_disposition(row.get("actual"))
            expected = parse_disposition(row.get("expected"))
            wrapped = wrapper(load_record(case_id)["decision"]["outcome"])
            if expected != wrapped:
                raise StudyError("%s row %s expectation is not the gated wrapper" % (arm, case_id))
            if actual != tables[case_id][under]:
                table_divergences.append(case_id)
            if actual != expected:
                entailed.append(case_id)
            if row["status"] != "passed":
                reported.append(case_id)
        if sorted(entailed) != sorted(reported):
            raise StudyError("%s's reported mismatches disagree with the recomputation" % arm)
        derived = sorted(case_id for case_id in everyone
                         if tables[case_id][under] != wrapper(load_record(case_id)["decision"]["outcome"]))
        return {
            "tableDivergences": sorted(table_divergences),
            "mismatchedRows": sorted(reported),
            "derivedMismatches": derived,
            "pass": not table_divergences and sorted(reported) == derived,
        }

    e2_d = arm_report("B-transcribed-D", "underD")
    e2_c = arm_report("Bprime-transcribed-C", "underC")
    results["endpoints"]["E2"] = {"underD": e2_d, "underC": e2_c,
                                  "pass": e2_d["pass"] and e2_c["pass"]}
    pipeline_valid = pipeline_valid and results["endpoints"]["E2"]["pass"]

    # E5: surface conformance, as Study 009.
    validates = all(runs[arm]["validate"]["payload"]["status"] == "valid"
                    for arm in ("A-circular-D", "B-transcribed-D", "Bprime-transcribed-C"))
    origin_exact = True
    for arm in ("B-transcribed-D", "Bprime-transcribed-C"):
        for case_id, row in rows_of(runs[arm]["test"]["payload"]).items():
            if row.get("origin") != origins[case_id]:
                origin_exact = False
    cli = dict(runs["Bprime-transcribed-C"]["test"]["payload"])
    wire = dict(runs["Bprime-mcp"]["structuredContent"])
    for field in ("command",):
        cli.pop(field, None)
        wire.pop(field, None)
    results["endpoints"]["E5"] = {
        "allProjectsValidate": validates,
        "originsExact": origin_exact,
        "wireEqualsShell": cli == wire,
        "pass": validates and origin_exact and cli == wire,
    }
    pipeline_valid = pipeline_valid and results["endpoints"]["E5"]["pass"]

    # E1: the ordered four-way partition (PREREGISTRATION.md §6). E2 having
    # passed makes the caught label a statement about the evaluator's actual
    # dispositions; the redundant per-row check below can only demote to
    # pipeline-invalid, never promote.
    if not pipeline_valid:
        e1 = "pipeline-invalid"
    elif h_and_f:
        caught = [case_id for case_id in h_and_f
                  if case_id not in e2_c["mismatchedRows"]
                  and case_id in e2_d["mismatchedRows"]]
        e1 = "caught" if sorted(caught) == h_and_f else "pipeline-invalid"
    elif q_and_f:
        e1 = "authoring-label-failure"
    else:
        e1 = "coverage-miss"
    results["endpoints"]["E1"] = {
        "outcome": e1,
        "HandF": h_and_f,
        "QandF": q_and_f,
        "F": sorted(sets["F"]),
    }

    # E3: the descriptive coverage profile over the whole family.
    results["endpoints"]["E3"] = {
        "sizes": sizes,
        "coverageProfile": coverage_profile(sets, manifest),
    }

    results["pipelineValid"] = pipeline_valid and e1 != "pipeline-invalid"
    write_results(results)


COMMANDS = {"lock": cmd_lock, "timestamp-lock": cmd_timestamp_lock,
            "publish": cmd_publish, "witness": cmd_witness, "draw": cmd_draw,
            "validate": cmd_validate, "freeze": cmd_freeze, "run": cmd_run,
            "score": cmd_score}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in COMMANDS:
        print("usage: study.py lock|timestamp-lock|publish|witness|draw|validate|freeze|run|score",
              file=sys.stderr)
        return 2
    try:
        COMMANDS[argv[1]]()
    except (StudyError, pnf_check.PNFError, study_gate.GateError,
            records_compile.CompileError, regions_check.RegionError,
            transcript_check.TranscriptError) as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
