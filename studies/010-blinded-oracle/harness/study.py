#!/usr/bin/env python3
"""Study 010 driver: lock | timestamp-lock | publish | witness | draw |
validate | freeze | run | score (PREREGISTRATION.md §8's ordering).

`lock` writes PROTOCOL-LOCK.json after proving pack C matches POLICY.md on
the 44-probe battery, every family patch applies, and the witness keys,
Rekor log key, codex binary, and drand chain constants are pinned;
`timestamp-lock` puts the lock commit in the Rekor transparency log. The
authoring call happens through transcription/authoring_call.sh (immutable
call-N slots); records_compile.py turns the transcript-bound completion
into records/. `publish` makes the records commit's Rekor inclusion — the
publication whose AUTHENTICATED integratedTime is the draw clock.
`witness` is the online uniqueness check over both locked keys. `draw`
computes the target drand round, fetches it from two relays by chain hash,
derives the sampled index, and derives DEFECT.json from the PUBLISHED
commit tree, never the worktree. `freeze` re-runs the uniqueness check
itself and pins everything; `run` and `score` carry the four-way E1.

Endpoints are computed only in `score`, from files `run` retained. `run`
opens the attempt ledger before any fallible work and seals every exit;
the primary attempt is the FIRST attempt started under the current freeze,
whatever its terminal state — a crashed primary scores pipeline-invalid.
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
MODEL = "gpt-5.6-sol"
# Hard pins, in reviewed bytes (PREREGISTRATION.md §5): the lock RECORDS
# these, but verification compares against the constants below, so a
# hand-edited lock cannot substitute an attacker chain or log key. The
# drand mainnet default chain's identity and schedule:
DRAND_CHAIN_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
DRAND_PUBLIC_KEY = ("868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a56"
                    "9937c529eeda66c7293784a9402801af31")
DRAND_GENESIS = 1595431050
DRAND_PERIOD = 30
DRAND_SCHEME = "pedersen-bls-chained"
# The production Rekor log's public key (fetched from
# https://rekor.sigstore.dev/api/v1/log/publicKey and pinned here).
REKOR_LOG_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE2G2Y+2tabdTV5BcGiBIx0a9fAFwr
kBbmLSGtks4L3qX6yYY0zufBnhC8Ur/iy55GhWP/9A/bY2LhC30M9+RYtw==
-----END PUBLIC KEY-----
"""
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
AUTHORING_DIR = os.path.join(STUDY, "transcription", "authoring")
MAX_AUTHORING_CALLS = 3
WITNESS_DIR = os.path.join(STUDY, "transcription", "witness")
# Two locked public keys (PREREGISTRATION.md §5): one signs the lock
# timestamp, the other signs exactly one records publication — separate
# keys make "the minimal-logIndex entry under the records key" unambiguous.
LOCK_PUB = os.path.join(STUDY, "transcription", "witness-lock-pub.pem")
RECORDS_PUB = os.path.join(STUDY, "transcription", "witness-records-pub.pem")
# The private keys never enter the repository; substituting different keys
# is inert because every verification runs against the LOCKED public keys.
_KEY_BASE = os.environ.get("STUDY010_WITNESS_KEYDIR") or os.path.expanduser("~")
LOCK_KEY = os.path.join(_KEY_BASE, ".study-010-witness-lock.key")
RECORDS_KEY = os.path.join(_KEY_BASE, ".study-010-witness-records.key")

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
    "transcription/witness-lock-pub.pem",
    "transcription/witness-records-pub.pem",
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

# The artifact freeze adds what the authoring calls, the compiler, the
# witness, and the draw generated (§8 step 3). Record files and the
# authoring retention (every call slot) are enumerated at freeze time.
GENERATED_BASE = [
    "RECORDS.md",
    "DRAW.json",
    "DEFECT.json",
    "packs/vendor-screening-defective.pack.json",
    "transcription/witness/INCLUSION.json",
    "transcription/witness/LOCK-INCLUSION.json",
    "transcription/witness/SEARCH.json",
]


LOCK_MEMBERS = {"lockedInputs", "jpack", "python", "probesChecked", "codex",
                "drand", "rekor", "drawRule", "githubRepo", "note"}
DRAW_RULE_MEMBERS = {"publication", "offsetSeconds", "deadlineSeconds", "round",
                     "preimage", "index", "familyDigest", "randomness"}
DRAND_MEMBERS = {"chainHash", "publicKey", "genesisTime", "periodSeconds",
                 "scheme", "relays", "rawInfo"}
REKOR_MEMBERS = {"log", "logPublicKeyPem", "lockWitnessKey", "recordsWitnessKey"}
FREEZE_MEMBERS = {"frozenInputs", "protocolLock", "jpack", "python", "invocation",
                  "preregistrationCommit", "note"}


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
    retained = []
    for base, _, names in os.walk(AUTHORING_DIR):
        for name in names:
            path = os.path.join(base, name)
            retained.append(os.path.relpath(path, STUDY))
    return LOCKED + GENERATED_BASE + sorted(retained) + _record_files()


def authoring_call() -> tuple[str, str]:
    """(the admissible call directory, its completion path): call slots are
    transcription/authoring/call-N; the admissible slot is the single one
    whose CALL.json records integer exit 0 — every earlier slot must be a
    retained transport failure (nonzero exit), and a second completed slot
    is a refused retry-after-completion (PREREGISTRATION.md §4)."""
    slots = sorted(name for name in os.listdir(AUTHORING_DIR)
                   if name.startswith("call-")) if os.path.isdir(AUTHORING_DIR) else []
    if not slots or slots != ["call-%d" % n for n in range(1, len(slots) + 1)]:
        raise StudyError("authoring call slots are missing or non-contiguous: %r" % slots)
    if len(slots) > MAX_AUTHORING_CALLS:
        raise StudyError("more than %d authoring call slots exist" % MAX_AUTHORING_CALLS)
    completed = []
    for name in slots:
        call = json.load(open(os.path.join(AUTHORING_DIR, name, "CALL.json")))
        status = call.get("exitStatus")
        sessions = call.get("newSessionCount")
        if isinstance(status, int) and not isinstance(status, bool) and status == 0:
            if not (isinstance(sessions, int) and not isinstance(sessions, bool) and sessions == 1):
                raise StudyError("%s completed without exactly one new session" % name)
            for required in ("session.jsonl", "completion.txt", "stdout.raw", "stderr.raw"):
                if not os.path.isfile(os.path.join(AUTHORING_DIR, name, required)):
                    raise StudyError("%s completed without retaining %s" % (name, required))
            completed.append(name)
    if len(completed) != 1:
        raise StudyError("exactly one completed authoring call is admissible, found %d"
                         % len(completed))
    admissible = completed[0]
    for name in slots:
        if name > admissible:
            raise StudyError("a call slot follows the completed call: %s" % name)
    call_dir = os.path.join(AUTHORING_DIR, admissible)
    return call_dir, os.path.join(call_dir, "completion.txt")


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


def http_get_text(url: str, timeout: int = 60) -> str:
    request = urllib.request.Request(url)
    request.add_header("User-Agent", "study-010-harness/1")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode()


# ------------------------------------------------------------- witness


def manifest_bytes(prefix: str, oid: str) -> bytes:
    if len(oid) != 40 or any(c not in "0123456789abcdef" for c in oid):
        raise StudyError("not a 40-hex commit OID: %r" % oid)
    return ("%s\n%s\n" % (prefix, oid)).encode("ascii")


def _openssl_sign(key_path: str, payload: bytes) -> bytes:
    """P-256/SHA-256 signature with an uncommitted witness private key."""
    import tempfile
    if not os.path.exists(key_path):
        raise StudyError("no witness private key at %s" % key_path)
    with tempfile.NamedTemporaryFile(delete=False) as handle:
        handle.write(payload)
        payload_path = handle.name
    try:
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key_path, payload_path],
            capture_output=True, check=True)
        return completed.stdout
    finally:
        os.unlink(payload_path)


def _openssl_verify(pub_path: str, payload: bytes, signature: bytes) -> bool:
    import tempfile
    paths = {}
    for name, blob in (("payload", payload), ("signature", signature)):
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            handle.write(blob)
            paths[name] = handle.name
    try:
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify", pub_path,
             "-signature", paths["signature"], paths["payload"]],
            capture_output=True)
        return completed.returncode == 0
    finally:
        for path in paths.values():
            os.unlink(path)


def witness_verify(pub_path: str, payload: bytes, signature: bytes) -> None:
    if not _openssl_verify(pub_path, payload, signature):
        raise StudyError("the witness signature does not verify under %s"
                         % os.path.basename(pub_path))


def _pem_der(pem_path: str) -> bytes:
    import base64
    pem = open(pem_path).read()
    return base64.b64decode("".join(
        line for line in pem.splitlines() if "-----" not in line))


def rekor_include(key_path: str, pub_path: str, payload: bytes) -> dict:
    """Upload one hashedrekord entry over payload; return the log's record
    with the raw response retained."""
    import base64
    signature = _openssl_sign(key_path, payload)
    body = {
        "kind": "hashedrekord", "apiVersion": "0.0.1",
        "spec": {
            "signature": {
                "content": base64.b64encode(signature).decode(),
                "publicKey": {"content": base64.b64encode(open(pub_path, "rb").read()).decode()},
            },
            "data": {"hash": {"algorithm": "sha256",
                              "value": hashlib.sha256(payload).hexdigest()}},
        },
    }
    entry = http_json_retry(REKOR + "/api/v1/log/entries", body)
    uuid, record = next(iter(entry.items()))
    return {"uuid": uuid, "logIndex": record["logIndex"],
            "integratedTime": record["integratedTime"],
            "logID": record["logID"],
            "body": record["body"], "verification": record.get("verification", {}),
            "signature": base64.b64encode(signature).decode(),
            "artifactSha256": hashlib.sha256(payload).hexdigest(),
            "manifest": payload.decode("ascii"),
            "publicKeyFile": os.path.basename(pub_path),
            "rawResponse": entry}


def verify_inclusion(inclusion: dict, pub_path: str, expected_manifest: bytes,
                     rekor_pub_pem: str) -> None:
    """Offline authentication of a retained Rekor inclusion
    (PREREGISTRATION.md §5): the entry's body binds the manifest and the
    locked witness key; the UUID is the leaf hash of that body; and the
    log's signed entry timestamp authenticates integratedTime/logIndex
    under the pinned Rekor log key. After this, the publication clock is
    the log's word, not the operator's."""
    import base64
    import tempfile
    if inclusion["artifactSha256"] != hashlib.sha256(expected_manifest).hexdigest():
        raise StudyError("the inclusion's artifact digest does not bind the manifest")
    witness_verify(pub_path, expected_manifest, base64.b64decode(inclusion["signature"]))
    body_bytes = base64.b64decode(inclusion["body"])
    body = json.loads(body_bytes)
    if body.get("kind") != "hashedrekord":
        raise StudyError("the inclusion body is not a hashedrekord")
    spec = body.get("spec", {})
    if spec.get("data", {}).get("hash", {}).get("value") != inclusion["artifactSha256"]:
        raise StudyError("the inclusion body does not carry the manifest digest")
    if spec.get("signature", {}).get("content") != inclusion["signature"]:
        raise StudyError("the inclusion body does not carry the witness signature")
    body_pub = base64.b64decode(spec.get("signature", {}).get("publicKey", {}).get("content", ""))
    if body_pub != open(pub_path, "rb").read():
        raise StudyError("the inclusion body does not carry the locked witness key")
    leaf = hashlib.sha256(b"\x00" + body_bytes).hexdigest()
    if not inclusion["uuid"].endswith(leaf):
        raise StudyError("the inclusion UUID is not the leaf hash of its body")
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as handle:
        handle.write(rekor_pub_pem)
        rekor_pub_path = handle.name
    try:
        der = _pem_der(rekor_pub_path)
        if hashlib.sha256(der).hexdigest() != inclusion["logID"]:
            raise StudyError("the inclusion's logID is not the pinned Rekor log key")
        set_payload = json.dumps({
            "body": inclusion["body"],
            "integratedTime": inclusion["integratedTime"],
            "logID": inclusion["logID"],
            "logIndex": inclusion["logIndex"],
        }, sort_keys=True, separators=(",", ":")).encode()
        set_signature = base64.b64decode(inclusion["verification"]["signedEntryTimestamp"])
        if not _openssl_verify(rekor_pub_path, set_payload, set_signature):
            raise StudyError("the log's signed entry timestamp does not verify; "
                             "integratedTime is unauthenticated")
    finally:
        os.unlink(rekor_pub_path)


def head_oid(repo_root: str) -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root,
                          capture_output=True, text=True, check=True).stdout.strip()


# ---------------------------------------------------------------- lock


def cmd_lock() -> None:
    jpack = os.environ.get("JPACK_BIN", "")
    if not jpack or sha256_file(jpack) != JPACK_DIGEST:
        raise StudyError("JPACK_BIN must be the pinned v0.15.0 binary")
    for key_path, pub_path in ((LOCK_KEY, LOCK_PUB), (RECORDS_KEY, RECORDS_PUB)):
        if not os.path.exists(pub_path):
            os.makedirs(os.path.dirname(pub_path), exist_ok=True)
            subprocess.run(["openssl", "ecparam", "-genkey", "-name", "prime256v1",
                            "-noout", "-out", key_path], check=True, capture_output=True)
            os.chmod(key_path, 0o600)
            subprocess.run(["openssl", "ec", "-in", key_path, "-pubout",
                            "-out", pub_path], check=True, capture_output=True)
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
    rekor_pub = http_get_text(REKOR + "/api/v1/log/publicKey")
    if "BEGIN PUBLIC KEY" not in rekor_pub:
        raise StudyError("the Rekor log key endpoint did not return a PEM")
    codex = shutil.which("codex")
    if not codex:
        raise StudyError("no codex CLI on PATH to pin")
    codex_version = subprocess.run(["codex", "--version"], capture_output=True,
                                   text=True, check=True).stdout.strip()
    body = {
        "lockedInputs": {relative: sha256_file(os.path.join(STUDY, relative))
                         for relative in LOCKED},
        "jpack": JPACK_DIGEST,
        "python": {"implementation": platform.python_implementation(),
                   "version": platform.python_version()},
        "probesChecked": checked,
        "codex": {"binarySha256": sha256_file(codex), "version": codex_version,
                  "model": MODEL},
        "drand": {
            "chainHash": info["chain_hash"],
            "publicKey": info["public_key"],
            "genesisTime": info["genesis_time"],
            "periodSeconds": info["period"],
            "scheme": info["scheme"],
            "relays": list(DRAND_RELAYS),
            "rawInfo": info,
        },
        "rekor": {"log": REKOR,
                  "logPublicKeyPem": rekor_pub,
                  "lockWitnessKey": sha256_file(LOCK_PUB),
                  "recordsWitnessKey": sha256_file(RECORDS_PUB)},
        "drawRule": {
            "publication": "the authenticated Rekor integratedTime over the records-commit manifest",
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


def repo_prefix() -> str:
    return subprocess.run(["git", "rev-parse", "--show-prefix"], cwd=STUDY,
                          capture_output=True, text=True, check=True).stdout.strip()


def head_blob(relative: str) -> bytes:
    """The committed bytes of a study-relative path, required to be a
    regular (non-symlink, non-executable-surprise) blob in HEAD."""
    listed = subprocess.run(
        ["git", "ls-tree", "HEAD", "--", relative], cwd=STUDY,
        capture_output=True, text=True, check=True).stdout.strip()
    if not listed:
        raise StudyError("%s is not in the HEAD tree" % relative)
    mode = listed.split()[0]
    if mode not in ("100644", "100755"):
        raise StudyError("%s is not a regular file in HEAD (mode %s)" % (relative, mode))
    shown = subprocess.run(["git", "show", "HEAD:./" + relative], cwd=STUDY,
                           capture_output=True)
    if shown.returncode != 0:
        raise StudyError("cannot read %s from HEAD" % relative)
    return shown.stdout


def verify_lock() -> dict:
    """The canonical-manifest check (PREREGISTRATION.md §8): the lock's key
    set is exactly the registered list; every locked input matches BOTH the
    worktree and its HEAD blob; the draw constants are the module's; the
    lock file itself equals its committed bytes."""
    if not os.path.exists(LOCK):
        raise StudyError("no PROTOCOL-LOCK.json; run lock and commit it first")
    locked = json.load(open(LOCK))
    if set(locked["lockedInputs"]) != set(LOCKED):
        raise StudyError("the lock's input set is not the registered list: %s"
                         % sorted(set(locked["lockedInputs"]) ^ set(LOCKED)))
    for relative in LOCKED:
        digest = locked["lockedInputs"][relative]
        path = os.path.join(STUDY, relative)
        if os.path.islink(path) or not os.path.isfile(path):
            raise StudyError("locked input is not a regular file: %s" % relative)
        if sha256_file(path) != digest:
            raise StudyError("locked input drifted: %s" % relative)
        committed = "sha256:" + hashlib.sha256(head_blob(relative)).hexdigest()
        if committed != digest:
            raise StudyError("locked input's HEAD blob differs from the lock: %s" % relative)
    # Every constant is compared against THIS FILE's reviewed bytes, not
    # merely read from the lock: a hand-edited lock cannot shift the chain
    # schedule (which would move the drawn round), swap the log key (which
    # would let a forged signed timestamp pass), or loosen the draw rule.
    if set(locked) != LOCK_MEMBERS:
        raise StudyError("the lock's member set is not the registered schema: %s"
                         % sorted(set(locked) ^ LOCK_MEMBERS))
    rule = locked["drawRule"]
    if set(rule) != DRAW_RULE_MEMBERS:
        raise StudyError("the lock's draw rule is not the registered schema")
    if rule["offsetSeconds"] != DRAW_OFFSET_SECONDS \
            or rule["deadlineSeconds"] != DRAW_DEADLINE_SECONDS:
        raise StudyError("the lock's draw constants are not the registered constants")
    chain = locked["drand"]
    if set(chain) != DRAND_MEMBERS:
        raise StudyError("the lock's chain object is not the registered schema")
    if (chain["chainHash"], chain["publicKey"], chain["genesisTime"],
            chain["periodSeconds"], chain["scheme"]) != (
            DRAND_CHAIN_HASH, DRAND_PUBLIC_KEY, DRAND_GENESIS, DRAND_PERIOD, DRAND_SCHEME):
        raise StudyError("the lock's chain constants are not the pinned mainnet chain")
    raw = chain["rawInfo"]
    if (raw.get("chain_hash"), raw.get("public_key"), raw.get("genesis_time"),
            raw.get("period"), raw.get("scheme")) != (
            DRAND_CHAIN_HASH, DRAND_PUBLIC_KEY, DRAND_GENESIS, DRAND_PERIOD, DRAND_SCHEME):
        raise StudyError("the lock's retained chain info disagrees with its own constants")
    if chain["relays"] != list(DRAND_RELAYS):
        raise StudyError("the lock's relay list is not the registered pair")
    if locked["probesChecked"] != 44:
        raise StudyError("the lock does not record the 44-probe battery")
    if locked["jpack"] != JPACK_DIGEST:
        raise StudyError("the lock does not pin the registered jpack digest")
    if locked["python"].get("implementation") != platform.python_implementation() \
            or locked["python"].get("version") != platform.python_version():
        raise StudyError("the lock's interpreter is not this interpreter")
    if locked["codex"].get("model") != MODEL:
        raise StudyError("the lock does not pin the registered model")
    rekor = locked["rekor"]
    if set(rekor) != REKOR_MEMBERS:
        raise StudyError("the lock's rekor object is not the registered schema")
    for member, pub_path in (("lockWitnessKey", LOCK_PUB), ("recordsWitnessKey", RECORDS_PUB)):
        if rekor[member] != sha256_file(pub_path):
            raise StudyError("the lock does not pin %s" % member)
    if rekor["lockWitnessKey"] == rekor["recordsWitnessKey"]:
        raise StudyError("the two witness keys must differ")
    if rekor["logPublicKeyPem"].strip() != REKOR_LOG_KEY.strip():
        raise StudyError("the lock's Rekor log key is not the pinned production key")
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
    locked = verify_lock()
    os.makedirs(WITNESS_DIR, exist_ok=True)
    target = os.path.join(WITNESS_DIR, "LOCK-INCLUSION.json")
    if os.path.exists(target):
        raise StudyError("the lock is already timestamped")
    lock_commit = head_oid(STUDY)
    payload = manifest_bytes("study-010-lock-commit", lock_commit)
    entry = rekor_include(LOCK_KEY, LOCK_PUB, payload)
    entry["lockCommit"] = lock_commit
    verify_inclusion(entry, LOCK_PUB, payload, locked["rekor"]["logPublicKeyPem"])
    with open(target, "w") as handle:
        json.dump(entry, handle, indent=2)
        handle.write("\n")
    print("lock timestamped and authenticated: logIndex %d, integratedTime %d; commit the inclusion"
          % (entry["logIndex"], entry["integratedTime"]))


def cmd_publish() -> None:
    locked = verify_lock()
    call_dir, completion = authoring_call()
    records_compile.cmd_verify(completion)
    transcript_check.check(
        os.path.join(call_dir, "session.jsonl"),
        os.path.join(STUDY, "transcription/PROMPT.txt"),
        completion,
        os.path.join(call_dir, "CALL.json"),
        model=MODEL)
    revision = records_commit()
    os.makedirs(WITNESS_DIR, exist_ok=True)
    target = os.path.join(WITNESS_DIR, "INCLUSION.json")
    if os.path.exists(target):
        raise StudyError("a records publication already exists; it is binding")
    payload = manifest_bytes("study-010-records-commit", revision)
    entry = rekor_include(RECORDS_KEY, RECORDS_PUB, payload)
    entry["recordsCommit"] = revision
    verify_inclusion(entry, RECORDS_PUB, payload, locked["rekor"]["logPublicKeyPem"])
    with open(target, "w") as handle:
        json.dump(entry, handle, indent=2)
        handle.write("\n")
    print("published: records commit %s at authenticated integratedTime %d (logIndex %d); commit and push, then draw"
          % (revision[:12], entry["integratedTime"], entry["logIndex"]))


def witness_search() -> tuple[dict, list]:
    """One online uniqueness OBSERVATION (PREREGISTRATION.md §5).

    Rekor's search index is an unauthenticated convenience API and is
    eventually consistent: a rehearsal found an entry that was retrievable
    by UUID and SET-verified, yet still absent from its key search a
    quarter of an hour later. Absence therefore proves nothing and cannot
    gate the study — the binding evidence is the AUTHENTICATED inclusion,
    which stands on the log's signed entry timestamp alone. A stranger
    returned under a locked key is meaningful in the other direction, and
    refuses. Returns (the retained observation, the stranger list)."""
    import base64
    inclusion = json.load(open(os.path.join(WITNESS_DIR, "INCLUSION.json")))
    lock_path = os.path.join(WITNESS_DIR, "LOCK-INCLUSION.json")
    known = {inclusion["uuid"]: "records"}
    if os.path.exists(lock_path):
        known[json.load(open(lock_path))["uuid"]] = "lock"
    hits_by_key = {}
    for name, pub_path in (("lock", LOCK_PUB), ("records", RECORDS_PUB)):
        body = {"publicKey": {"format": "x509",
                              "content": base64.b64encode(open(pub_path, "rb").read()).decode()}}
        uuids = http_json_retry(REKOR + "/api/v1/index/retrieve", body)
        entries = []
        for uuid in uuids:
            entry = http_json_retry(REKOR + "/api/v1/log/entries/" + uuid)
            record = next(iter(entry.values()))
            entries.append({"uuid": uuid, "logIndex": record["logIndex"],
                            "integratedTime": record["integratedTime"]})
        hits_by_key[name] = entries
    strangers = [entry for name, entries in hits_by_key.items() for entry in entries
                 if known.get(entry["uuid"]) != name]
    search = {
        "queried": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hits": hits_by_key,
        "known": known,
        "recordsUuid": inclusion["uuid"],
        "recordsIndexed": any(entry["uuid"] == inclusion["uuid"]
                              for entry in hits_by_key["records"]),
        "strangers": strangers,
        "note": ("An unauthenticated, eventually consistent observation. "
                 "recordsIndexed false means the index had not caught up, "
                 "not that the inclusion is absent: INCLUSION.json's "
                 "authenticated entry is the binding evidence."),
    }
    return search, strangers


def cmd_witness() -> None:
    verify_lock()
    search, strangers = witness_search()
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
        json.dump(search, handle, indent=2)
        handle.write("\n")
    if strangers:
        raise StudyError("unknown inclusions under a witness key: %r" % strangers)
    print("witness: no strangers (%d lock + %d records hits; records entry %s)"
          % (len(search["hits"]["lock"]), len(search["hits"]["records"]),
             "indexed" if search["recordsIndexed"] else "not yet indexed"))


# ---------------------------------------------------------------- draw


def tree_files(revision: str, relative_dirs: list) -> dict:
    """{study-relative path: bytes} for the named paths as committed in
    revision — regular blobs only, read from the tree, never the worktree.
    ls-tree pathspecs are cwd-relative, so the listing runs from the repo
    root with the study prefix applied."""
    prefix = repo_prefix()
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=STUDY,
                          capture_output=True, text=True, check=True).stdout.strip()
    listed = subprocess.run(
        ["git", "ls-tree", "-r", revision, "--"] + [prefix + d for d in relative_dirs],
        cwd=root, capture_output=True, text=True, check=True).stdout
    result = {}
    for line in listed.splitlines():
        meta, path = line.split("\t", 1)
        mode = meta.split()[0]
        if mode not in ("100644", "100755"):
            raise StudyError("%s is not a regular file in %s (mode %s)" % (path, revision[:12], mode))
        relative = path[len(prefix):]
        shown = subprocess.run(["git", "show", "%s:%s" % (revision, path)],
                               cwd=STUDY, capture_output=True, check=True)
        result[relative] = shown.stdout
    return result


def locked_snapshot() -> dict:
    """The locked derivation inputs read from HEAD's blobs, once, BEFORE
    the beacon wait (PREREGISTRATION.md §5). Everything the sampled index
    and the tables depend on — FAMILY.json's exact bytes, pack C, the
    controls — is taken from this snapshot, never re-read from a mutable
    worktree afterwards: a whitespace variant of FAMILY.json parses to the
    same mutations but hashes differently, and re-reading it after the
    round is known would hand the operator the index."""
    snapshot = {}
    for relative in ("FAMILY.json", "packs/vendor-screening-correct.pack.json",
                     "controls/k-wrong-1.json", "controls/k-wrong-2.json"):
        blob = head_blob(relative)
        if blob != open(os.path.join(STUDY, relative), "rb").read():
            raise StudyError("%s differs from its HEAD blob" % relative)
        snapshot[relative] = blob
    return snapshot


def snapshot_family(snapshot: dict) -> tuple[dict, str]:
    """(the parsed family, its digest) from snapshot bytes only."""
    blob = snapshot["FAMILY.json"]
    return json.loads(blob.decode("utf-8")), hashlib.sha256(blob).hexdigest()


def published_tree(revision: str) -> dict:
    """The published records commit's own bytes for everything the draw
    depends on (PREREGISTRATION.md §5): records, the ledger, the authoring
    retention. Derivation reads THESE, never the worktree."""
    files = tree_files(revision, ["records", "RECORDS.md", "transcription/authoring"])
    if not any(path.startswith("records/") for path in files):
        raise StudyError("the records commit holds no records")
    return files


def assert_worktree_is(files: dict, revision: str, relative_dirs: list) -> None:
    """The worktree's view of the published paths must equal the published
    tree exactly — same file set, same bytes, regular files only."""
    actual = set()
    for relative_dir in relative_dirs:
        base = os.path.join(STUDY, relative_dir)
        if os.path.isfile(base):
            actual.add(relative_dir)
            continue
        for walk_base, _, names in os.walk(base):
            for name in names:
                path = os.path.join(walk_base, name)
                actual.add(os.path.relpath(path, STUDY))
    expected = {path for path in files
                if any(path == d or path.startswith(d.rstrip("/") + "/") for d in relative_dirs)}
    if actual != expected:
        raise StudyError("the worktree's published paths differ from the records commit: %s"
                         % sorted(actual ^ expected))
    for relative in sorted(expected):
        path = os.path.join(STUDY, relative)
        if os.path.islink(path) or not os.path.isfile(path):
            raise StudyError("%s is not a regular file in the worktree" % relative)
        if open(path, "rb").read() != files[relative]:
            raise StudyError("%s differs from the records commit %s" % (relative, revision[:12]))


def fetch_round(chain_hash: str, target_round: int) -> list[dict]:
    """The fixed round from both relays, by chain hash, raw bytes retained,
    byte-equal signatures and previous signatures required."""
    responses = []
    for relay in DRAND_RELAYS:
        url = "%s/%s/public/%d" % (relay, chain_hash, target_round)
        last = None
        raw = None
        for attempt in range(8):
            try:
                raw = http_get_text(url)
                break
            except Exception as error:  # noqa: BLE001 - refused after the loop
                last = error
                time.sleep(5 * (attempt + 1))
        if raw is None:
            raise StudyError("unreachable after 8 attempts: %s (%r)" % (url, last))
        parsed = json.loads(raw)
        responses.append({"relay": relay, "url": url, "raw": raw,
                          "retrievedAt": int(time.time()), **parsed})
    signatures = {response["signature"] for response in responses}
    previous = {response.get("previous_signature") for response in responses}
    rounds = {response["round"] for response in responses}
    if len(signatures) != 1 or rounds != {target_round}:
        raise StudyError("the relays disagree: %r" % responses)
    if len(previous) != 1 or None in previous or "" in previous:
        raise StudyError("previous_signature is missing or disagrees between relays")
    return responses


def draw_index(randomness_hex: str, commit_hex: str, family_hex: str) -> tuple[bytes, int]:
    if len(randomness_hex) != 64 or len(commit_hex) != 40 or len(family_hex) != 64:
        raise StudyError("draw preimage fields are not the registered widths")
    preimage = ("study-010-draw-v1\n%s\n%s\n%s\n"
                % (randomness_hex, commit_hex, family_hex)).encode("ascii")
    return preimage, int.from_bytes(hashlib.sha256(preimage).digest(), "big") % 6


def canonical_json(value) -> bytes:
    """The one serializer for every artifact this study byte-compares."""
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def derive_defect(published: dict, snapshot: dict, mutation: dict, index: int) -> dict:
    """DEFECT.json's canonical body, derived from the PUBLISHED record
    bytes and the pre-beacon LOCKED SNAPSHOT only (PREREGISTRATION.md §5).
    validate recomputes this same body and byte-compares."""
    authored = {}
    for relative, blob in published.items():
        if relative.startswith("records/") and relative.endswith(".json"):
            record = json.loads(blob.decode("utf-8"))
            authored[record["caseId"]] = record
    controls = {name: json.loads(snapshot["controls/%s.json" % name].decode("utf-8"))
                for name in ("k-wrong-1", "k-wrong-2")}
    sets = {"H": [], "Q": [], "F": [], "K": sorted(controls)}
    tables = {}
    for case_id in sorted(authored):
        vendor = authored[case_id]["vendor"]
        tables[case_id] = table_entry(vendor, mutation)
        if policy_mirror.predicate_matches(mutation["predicate"], vendor):
            sets["F"].append(case_id)
        if authored[case_id]["decision"]["outcome"] == policy_mirror.verdict(vendor):
            sets["H"].append(case_id)
        else:
            sets["Q"].append(case_id)
    for case_id in sets["K"]:
        tables[case_id] = table_entry(controls[case_id]["vendor"], mutation)
    return {
        "sampledIndex": index,
        "mutation": mutation,
        "sets": {name: sorted(ids) for name, ids in sets.items()},
        "expectedDispositions": {"perRecord": tables},
    }


def cmd_draw() -> None:
    locked = verify_lock()
    _, completion = authoring_call()
    records_compile.cmd_verify(completion)
    revision = records_commit()
    inclusion = json.load(open(os.path.join(WITNESS_DIR, "INCLUSION.json")))
    if inclusion["recordsCommit"] != revision:
        raise StudyError("the publication binds %s, not the records commit %s"
                         % (inclusion["recordsCommit"], revision))
    expected_manifest = manifest_bytes("study-010-records-commit", revision)
    verify_inclusion(inclusion, RECORDS_PUB, expected_manifest,
                     locked["rekor"]["logPublicKeyPem"])
    published_files = published_tree(revision)
    # Snapshot every locked derivation input BEFORE the wait: nothing the
    # index depends on is re-read from the worktree once the round is known.
    snapshot = locked_snapshot()
    family_manifest, family_digest = snapshot_family(snapshot)
    published = inclusion["integratedTime"]
    genesis = locked["drand"]["genesisTime"]
    period = locked["drand"]["periodSeconds"]
    target_time = published + locked["drawRule"]["offsetSeconds"]
    target_round = (target_time - genesis + period - 1) // period + 1
    scheduled = genesis + (target_round - 1) * period
    if scheduled < target_time:
        raise StudyError("round arithmetic is wrong: %d < %d" % (scheduled, target_time))
    while time.time() < scheduled:
        time.sleep(min(15, scheduled - time.time() + 1))
    responses = fetch_round(locked["drand"]["chainHash"], target_round)
    # The deadline binds retrieval COMPLETION (PREREGISTRATION.md §5).
    if max(r["retrievedAt"] for r in responses) > scheduled + locked["drawRule"]["deadlineSeconds"]:
        raise StudyError("round %d was not retrieved inside the deadline; the attempt is pipeline-invalid"
                         % target_round)
    # The records commit must still be what the worktree holds — a record
    # set swapped during the beacon wait fails here, and derivation below
    # reads the PUBLISHED tree regardless.
    if records_commit() != revision:
        raise StudyError("the records commit changed during the beacon wait")
    assert_worktree_is(published_files, revision,
                       ["records", "RECORDS.md", "transcription/authoring"])
    signature = responses[0]["signature"]
    # drand's chained scheme defines the round's randomness as
    # sha256(signature); the signature itself is the externally verifiable
    # object (BLS over previous_signature + round, against the chain key).
    randomness = hashlib.sha256(bytes.fromhex(signature)).hexdigest()
    preimage, index = draw_index(randomness, revision, family_digest)
    draw = {
        "recordsCommit": revision,
        "publication": inclusion,
        "publishedEpoch": published,
        "targetRound": target_round,
        "scheduledTime": scheduled,
        "randomness": randomness,
        "signature": signature,
        "previousSignature": responses[0]["previous_signature"],
        "relayResponses": responses,
        "chain": locked["drand"],
        "familyDigest": "sha256:" + family_digest,
        "preimage": preimage.decode("ascii"),
        "index": index,
    }
    with open(os.path.join(STUDY, "DRAW.json"), "w") as handle:
        json.dump(draw, handle, indent=2)
        handle.write("\n")

    matches = [m for m in family_manifest["mutations"] if m["index"] == index]
    if len(matches) != 1:
        raise StudyError("the snapshot family has no unique member at index %d" % index)
    mutation = matches[0]
    correct = json.loads(snapshot["packs/vendor-screening-correct.pack.json"].decode("utf-8"))
    defective = apply_patch(correct, mutation["patch"])
    with open(os.path.join(STUDY, "packs/vendor-screening-defective.pack.json"), "wb") as handle:
        handle.write(canonical_json(defective))

    manifest = derive_defect(published_files, snapshot, mutation, index)
    with open(os.path.join(STUDY, "DEFECT.json"), "wb") as handle:
        handle.write(canonical_json(manifest))
    sets = manifest["sets"]
    in_h = sorted(set(sets["H"]) & set(sets["F"]))
    print("draw: round %d -> index %d (%s); |F|=%d, |H∩F|=%d; commit DRAW.json, DEFECT.json, pack D"
          % (target_round, index, mutation["title"], len(sets["F"]), len(in_h)))


# ---------------------------------------------------------------- validate


def cmd_validate() -> None:
    locked_manifest = verify_lock()
    for relative in frozen_inputs():
        if not os.path.exists(os.path.join(STUDY, relative)):
            raise StudyError("missing input: " + relative)
    call_dir, completion = authoring_call()
    records_compile.cmd_verify(completion)
    transcript_check.check(
        os.path.join(call_dir, "session.jsonl"),
        os.path.join(STUDY, "transcription/PROMPT.txt"),
        completion,
        os.path.join(call_dir, "CALL.json"),
        model=MODEL)
    call = json.load(open(os.path.join(call_dir, "CALL.json")))
    if call.get("binarySha256") != locked_manifest["codex"]["binarySha256"]:
        raise StudyError("the authoring call did not use the locked codex binary")
    # Every derivation input comes from the locked snapshot (HEAD blobs),
    # and DEFECT.json / pack D are compared as canonical BYTES, so a
    # retyped literal (JSON false vs 0, which Python equates) or a
    # whitespace variant cannot pass as the sampled mutation.
    snapshot = locked_snapshot()
    family_manifest, family_digest = snapshot_family(snapshot)
    manifest = defect()
    mutation = manifest["mutation"]
    fam = [m for m in family_manifest["mutations"] if m["index"] == manifest["sampledIndex"]]
    if len(fam) != 1 or canonical_json(mutation) != canonical_json(fam[0]):
        raise StudyError("DEFECT.json's mutation is not the snapshot family's sampled member")
    mutation = fam[0]
    draw = json.load(open(os.path.join(STUDY, "DRAW.json")))
    if draw["index"] != manifest["sampledIndex"]:
        raise StudyError("DRAW.json and DEFECT.json disagree on the index")
    if draw["familyDigest"] != "sha256:" + family_digest:
        raise StudyError("DRAW.json's family digest is not the locked family")
    preimage, index = draw_index(draw["randomness"], draw["recordsCommit"], family_digest)
    if preimage.decode("ascii") != draw["preimage"] or index != draw["index"]:
        raise StudyError("the sampled index does not recompute from the draw")
    if hashlib.sha256(bytes.fromhex(draw["signature"])).hexdigest() != draw["randomness"]:
        raise StudyError("the draw's randomness is not sha256(signature)")
    responses = draw["relayResponses"]
    if len(responses) != 2 or [r["relay"] for r in responses] != list(DRAND_RELAYS):
        raise StudyError("the retained relay responses are not the two registered relays")
    for response in responses:
        parsed = json.loads(response["raw"])
        if parsed["signature"] != draw["signature"] or parsed["round"] != draw["targetRound"] \
                or parsed.get("previous_signature") != draw["previousSignature"]:
            raise StudyError("a retained raw relay response does not carry the drawn round")
    if not draw["previousSignature"]:
        raise StudyError("the draw retains no previous_signature")
    locked = json.load(open(LOCK))
    if draw["chain"] != locked["drand"]:
        raise StudyError("the draw's chain constants are not the locked chain")
    inclusion = draw["publication"]
    if inclusion["recordsCommit"] != draw["recordsCommit"]:
        raise StudyError("the publication does not bind the records commit")
    expected_manifest = manifest_bytes("study-010-records-commit", draw["recordsCommit"])
    verify_inclusion(inclusion, RECORDS_PUB, expected_manifest,
                     locked["rekor"]["logPublicKeyPem"])
    on_disk = json.load(open(os.path.join(WITNESS_DIR, "INCLUSION.json")))
    if on_disk != inclusion:
        raise StudyError("DRAW.json's publication is not the retained inclusion")
    # The lock timestamp is authenticated too, and its commit must be an
    # ancestor of the records commit: lock-before-authoring is checkable.
    lock_inclusion = json.load(open(os.path.join(WITNESS_DIR, "LOCK-INCLUSION.json")))
    lock_commit = lock_inclusion.get("lockCommit", "")
    verify_inclusion(lock_inclusion, LOCK_PUB,
                     manifest_bytes("study-010-lock-commit", lock_commit),
                     locked["rekor"]["logPublicKeyPem"])
    if subprocess.run(["git", "merge-base", "--is-ancestor", lock_commit,
                       draw["recordsCommit"]], cwd=STUDY).returncode != 0:
        raise StudyError("the timestamped lock commit is not an ancestor of the records commit")
    if lock_inclusion["integratedTime"] > inclusion["integratedTime"]:
        raise StudyError("the lock was timestamped after the records publication")
    genesis = locked["drand"]["genesisTime"]
    period = locked["drand"]["periodSeconds"]
    target_time = inclusion["integratedTime"] + locked["drawRule"]["offsetSeconds"]
    expected_round = (target_time - genesis + period - 1) // period + 1
    if expected_round != draw["targetRound"]:
        raise StudyError("the target round does not recompute from the publication clock")
    if genesis + (draw["targetRound"] - 1) * period != draw["scheduledTime"]:
        raise StudyError("the scheduled time does not recompute")
    if max(r["retrievedAt"] for r in responses) > draw["scheduledTime"] \
            + locked["drawRule"]["deadlineSeconds"]:
        raise StudyError("the retained retrieval finished after the deadline")
    # The published tree is the derivation source (PREREGISTRATION.md §5):
    # the worktree must equal it, and DEFECT.json must byte-recompute from
    # it — one canonical body, no separate patch authority, exact sets.
    published_files = published_tree(draw["recordsCommit"])
    assert_worktree_is(published_files, draw["recordsCommit"],
                       ["records", "RECORDS.md", "transcription/authoring"])
    recomputed = derive_defect(published_files, snapshot, mutation, draw["index"])
    if canonical_json(recomputed) != open(os.path.join(STUDY, "DEFECT.json"), "rb").read():
        raise StudyError("DEFECT.json is not the canonical recomputation from the published records")
    everyone = record_ids()
    sets = manifest["sets"]
    if sorted(sets["H"] + sets["Q"] + sets["K"]) != everyone:
        raise StudyError("H+Q+K do not cover exactly the record ids")
    for case_id in sets["K"]:
        record = load_record(case_id)
        if policy_mirror.predicate_matches(mutation["predicate"], record["vendor"]):
            raise StudyError("control %s intersects the sampled predicate" % case_id)
    for case_id in everyone:
        if load_record(case_id)["caseId"] != case_id:
            raise StudyError("record %s misnames itself" % case_id)
    correct = json.loads(snapshot["packs/vendor-screening-correct.pack.json"].decode("utf-8"))
    expected_d = canonical_json(apply_patch(correct, mutation["patch"]))
    if expected_d != open(os.path.join(STUDY, "packs/vendor-screening-defective.pack.json"), "rb").read():
        raise StudyError("pack D is not the canonical C-with-the-sampled-patch bytes")
    pnf_check.check(json.load(open(os.path.join(STUDY, "transcription/record.rule.json"))))
    print("validate: ok (%d records+controls, publication authenticated, draw bound, "
          "DEFECT recomputed, rule is the registered projection)" % len(everyone))


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
    # The freeze gate runs the uniqueness check ITSELF (PREREGISTRATION.md
    # §8): a hand-authored search file convinces nobody; the online result
    # is retained as evidence inside the freeze, then everything validates.
    verify_lock()
    search, strangers = witness_search()
    target = os.path.join(WITNESS_DIR, "SEARCH.json")
    with open(target, "w") as handle:
        json.dump(search, handle, indent=2)
        handle.write("\n")
    if strangers:
        raise StudyError("unknown inclusions under a witness key: %r" % strangers)
    # The first committed freeze is the freeze: re-freezing after a crash
    # would change the digest and silently re-elect the primary attempt.
    committed = subprocess.run(["git", "cat-file", "-e", "HEAD:./FREEZE.json"],
                               cwd=STUDY, capture_output=True)
    if committed.returncode == 0:
        raise StudyError("a committed FREEZE.json already governs; it is immutable")
    cmd_validate()
    with open(FREEZE, "wb") as handle:
        handle.write(canonical_json(freeze_body()))
    print("froze %d inputs; commit FREEZE.json before running" % len(frozen_inputs()))


def verify_freeze() -> dict:
    """The canonical-manifest check for the artifact freeze: exact key set,
    worktree AND HEAD blob agreement for every input, the lock bound, the
    interpreter and binary pinned."""
    if not os.path.exists(FREEZE):
        raise StudyError("no FREEZE.json; run freeze and commit it first")
    frozen = json.load(open(FREEZE))
    if set(frozen) != FREEZE_MEMBERS:
        raise StudyError("the freeze's member set is not the registered schema")
    if frozen["jpack"] != JPACK_DIGEST:
        raise StudyError("the freeze does not pin the registered jpack digest")
    if frozen["python"].get("implementation") != platform.python_implementation():
        raise StudyError("the freeze's interpreter implementation is not this one")
    if set(frozen["frozenInputs"]) != set(frozen_inputs()):
        raise StudyError("the freeze's input set is not the enumerated set: %s"
                         % sorted(set(frozen["frozenInputs"]) ^ set(frozen_inputs())))
    for relative, digest in frozen["frozenInputs"].items():
        path = os.path.join(STUDY, relative)
        if os.path.islink(path) or not os.path.isfile(path):
            raise StudyError("frozen input is not a regular file: %s" % relative)
        if sha256_file(path) != digest:
            raise StudyError("frozen input drifted: %s" % relative)
        committed = "sha256:" + hashlib.sha256(head_blob(relative)).hexdigest()
        if committed != digest:
            raise StudyError("frozen input's HEAD blob differs from the freeze: %s" % relative)
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
    # The attempt ledger opens BEFORE any fallible prerequisite work
    # (PREREGISTRATION.md §6): a validation failure is a crashed primary
    # attempt that scores pipeline-invalid, never a silent non-attempt. The
    # only pre-attempt requirement is that a freeze file exists to bind to.
    if not os.path.exists(FREEZE):
        raise StudyError("no FREEZE.json; run freeze and commit it first")
    attempt = start_attempt()
    try:
        with open(os.path.join(attempt, "FREEZE-DIGEST"), "w") as handle:
            handle.write(sha256_file(FREEZE) + "\n")
        frozen = verify_freeze()
        cmd_validate()
        jpack = os.environ["JPACK_BIN"]
        _run_body(frozen, jpack, attempt)
    except BaseException as error:
        # Every exit receives a terminal state and a seal: a crashed
        # primary attempt scores pipeline-invalid, it is not skipped.
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
        bound = os.path.isfile(digest_path) and open(digest_path).read().strip() == current
        if bound:
            verify_seal(attempt)
            done_path = os.path.join(attempt, "DONE")
            done = os.path.isfile(done_path) and not os.path.islink(done_path)
            return number, attempt, done
        number += 1
    raise StudyError("no attempt under the current freeze")


def verify_seal(attempt: str) -> None:
    """The sealed set must be EXACT: every manifested file unchanged, and
    no file present that the manifest does not name — an added DONE or a
    removed CRASHED.json is a drifted seal, not a promotion."""
    manifest = json.load(open(os.path.join(attempt, "MANIFEST.json")))
    actual = set()
    for base, dirs, names in os.walk(attempt):
        for name in dirs:
            path = os.path.join(base, name)
            if os.path.islink(path):
                raise StudyError("the sealed attempt holds a symlinked directory: %s" % name)
        for name in names:
            path = os.path.join(base, name)
            if os.path.islink(path) or not os.path.isfile(path):
                raise StudyError("the sealed attempt holds a non-regular file: %s" % name)
            actual.add(os.path.relpath(path, attempt))
    terminal = {"DONE", "CRASHED.json"} & actual
    if len(terminal) != 1:
        raise StudyError("the attempt has %d terminal markers, not one" % len(terminal))
    if actual != set(manifest) | {"MANIFEST.json"}:
        raise StudyError("the sealed attempt's file set drifted: %s"
                         % sorted(actual ^ (set(manifest) | {"MANIFEST.json"})))
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
    number = 0
    try:
        verify_freeze()
        number, attempt, done = primary_attempt()
        _score_body(number, attempt, done)
    except Exception as error:  # noqa: BLE001 - E1's partition is total
        # E1's partition is total (PREREGISTRATION.md §6): malformed or
        # missing retained data is pipeline-invalid, not a bare exception.
        write_results({
            "attempt": number,
            "prerequisites": {"scoring": "malformed or missing retained data"},
            "endpoints": {"E1": {"outcome": "pipeline-invalid", "error": repr(error)}},
            "pipelineValid": False,
        })


def _score_body(number: int, attempt: str, done: bool) -> None:
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
