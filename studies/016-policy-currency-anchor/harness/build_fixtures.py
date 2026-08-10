"""One-time deterministic fixture construction for every registered cell.

A Study 016 cell is `(chain, retained artifacts, registry snapshot, verifier
trust configuration)`. The chain-build surface is deliberately tiny — four
chains serve the whole matrix, all built through Study 014's frozen build
machinery consumed as a pinned upstream (decision D-1, `harness/upstream014.py`):

  baseline    the v0.1.0 decision chain (014's pos-baseline construction,
              rebuilt under the v0.17.0 replay tuple);
  successor   the same scenario decided under pack v0.2.0;
  remint      the e22-analog: the baseline judgment commitment re-bound under a
              different, equally valid work order (014's e22 construction —
              a remint, not a rollback: OWP has no contract ordering);
  neg-owp     the baseline bundle with one signature character flipped.

Every other cell varies only the signed registry history and the verifier's
out-of-band pins over the baseline chain's bytes — the study's central design
move: the world-that-moved is itself a retained, signed, pinned artifact, which
is what makes currency observable where Study 014's section 4c could not.

Byte-identity is registered, not accidental: `cur-concurrent-set` and
`cur-older-snapshot-unpinned` are the same bytes (the freshness floor — an
offline verifier cannot distinguish a withheld newer snapshot from a world that
genuinely stopped), and the two `dem-freshness-*` cells are byte-copies of
`cur-retired-reuse` (the verdict provably cannot carry the legitimate-audit vs
stale-reuse distinction). `harness/MATRIX.json` registers the identity groups
and the scorer re-verifies them.

Run:
    JPACK_BIN=... OWP_SOURCE=... python harness/build_fixtures.py [--out DIR] [--force]
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "registry"))

import checkpoint as registry  # noqa: E402
import upstream014  # noqa: E402

SERIES_ID = "https://example.com/judgment-packs/expense-approval"
OTHER_SERIES_ID = "https://example.com/judgment-packs/other-policy"

PACK_V1_PATH = STUDY / "fixtures" / "packs" / "minimal-expense-approval-0.1.0.pack.json"
PACK_V2_PATH = STUDY / "fixtures" / "packs" / "minimal-expense-approval-0.2.0.pack.json"
PACK_V1_SHA256 = "76651c8aa6ba9862650fcdf4e34537dd41381d534d39d118bce71b247e641d60"
PACK_V2_SHA256 = "fc7896121e98d840ca7ba30505e4dc4c63bf5ae0ec7ac9a9c8bdd0529af42c70"

CELL_FILES = (
    "pack.json",
    "facts.json",
    "evidence.json",
    "evaluation.json",
    "commitment.json",
    "bundle.json",
    "snapshot.json",
    "trustconfig.json",
)
MANIFEST_NAME = "MANIFEST.sha256"

# effectiveFrom constants: carried on every checkpoint, compared by nothing
# (decision D-5; no clock exists anywhere in the ceremony).
T1 = "2026-01-01T00:00:00Z"
T2 = "2026-01-15T00:00:00Z"
T3 = "2026-02-01T00:00:00Z"

REBOUND_DIGEST = "sha256:" + hashlib.sha256(b"study-016/rebound-digest").hexdigest()
OTHER_SERIES_DIGEST = (
    "sha256:" + hashlib.sha256(b"study-016/other-series-pack").hexdigest()
)


class BuildError(RuntimeError):
    """A cell could not be constructed as registered."""


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def write_packs():
    """Vendor pack v0.1.0 from the frozen 014 fixture; derive v0.2.0 from it."""
    source = upstream014.STUDY_014 / "fixtures" / "minimal-expense-approval.pack.json"
    v1 = source.read_bytes()
    if sha256_hex(v1) != PACK_V1_SHA256:
        raise BuildError("the frozen 014 pack fixture does not match its digest")
    v2 = v1.replace(b'"version": "0.1.0"', b'"version": "0.2.0"').replace(
        b'"5000"', b'"6000"'
    )
    if v2 == v1 or sha256_hex(v2) != PACK_V2_SHA256:
        raise BuildError("the derived v0.2.0 pack does not match its pinned digest")
    PACK_V1_PATH.parent.mkdir(parents=True, exist_ok=True)
    PACK_V1_PATH.write_bytes(v1)
    PACK_V2_PATH.write_bytes(v2)
    return v1, v2


# --------------------------------------------------------------------------
# registries — every history the matrix registers
# --------------------------------------------------------------------------

def event(kind, version, digest=None, effective=T1, series=SERIES_ID):
    entry = {
        "event": kind,
        "seriesId": series,
        "packVersion": version,
        "effectiveFrom": effective,
    }
    if digest is not None:
        entry["packDigest"] = digest
    return entry


def registries(authority, foreign, v1_digest, v2_digest):
    """Every registered history and snapshot, keyed by name."""
    add_v1 = event("add", "0.1.0", v1_digest, T1)

    current = registry.build_registry(authority, [add_v1])
    retiring = registry.build_registry(
        authority,
        [add_v1, event("add", "0.2.0", v2_digest, T2), event("retire", "0.1.0", effective=T3)],
    )
    reinstated = registry.build_registry(
        authority,
        [add_v1, event("retire", "0.1.0", effective=T2),
         event("reinstate", "0.1.0", effective=T3)],
    )
    rebound = registry.build_registry(
        authority,
        [add_v1, event("retire", "0.1.0", effective=T2),
         event("add", "0.1.0", REBOUND_DIGEST, T3)],
    )
    other = registry.build_registry(
        authority,
        [event("add", "1.0.0", OTHER_SERIES_DIGEST, T1, series=OTHER_SERIES_ID)],
    )
    impostor = registry.build_registry(foreign, [add_v1])
    # The split view: one authority, one genesis, two internally valid
    # continuations. Registered expected-undetected for a fresh two-pin
    # verifier — the empirical case for transparency-log-style governance.
    view_a = registry.build_registry(
        authority, [add_v1, event("add", "0.2.0", v2_digest, T3)]
    )
    view_b = registry.build_registry(
        authority, [add_v1, event("retire", "0.1.0", effective=T3)]
    )
    if view_a[0]["checkpointDigest"] != view_b[0]["checkpointDigest"]:
        raise BuildError("the split views do not share their genesis")

    # The chain break: checkpoint 2 re-signed by the authority over a previous
    # digest that is not checkpoint 1's — signatures valid, linkage broken.
    broken_second = registry.build_checkpoint(
        authority,
        sequence=2,
        series_id=SERIES_ID,
        event="add",
        pack_version="0.2.0",
        pack_digest=v2_digest,
        effective_from=T2,
        previous="sha256:" + hashlib.sha256(b"study-016/not-the-genesis").hexdigest(),
    )
    broken = [current[0], broken_second]

    genesis_head = current[0]["checkpointDigest"]
    snapshots = {
        "current": registry.snapshot_of(authority, current),
        "retiring": registry.snapshot_of(authority, retiring),
        "retiring-prefix-2": registry.snapshot_of(authority, retiring, position=2),
        "reinstated": registry.snapshot_of(authority, reinstated),
        "rebound": registry.snapshot_of(authority, rebound),
        "other-series": registry.snapshot_of(authority, other),
        "impostor": registry.snapshot_of(foreign, impostor),
        "view-a": registry.snapshot_of(authority, view_a),
        "view-b": registry.snapshot_of(authority, view_b),
        "chain-break": registry.snapshot_of(authority, broken),
    }
    heads = {
        "genesis": genesis_head,
        "retiring-head": retiring[-1]["checkpointDigest"],
        "other-genesis": other[0]["checkpointDigest"],
        "view-a-head": view_a[1]["checkpointDigest"],
    }
    return snapshots, heads


def broken_signature_snapshot(snapshot):
    """The positive snapshot with one attestation-signature character flipped."""
    doctored = json.loads(registry.snapshot_bytes(snapshot).decode("utf-8"))
    signature = doctored["attestation"]["signature"]
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    first = signature[0]
    index = alphabet.index(first) if first in alphabet else 0
    doctored["attestation"]["signature"] = (
        alphabet[(index + 1) % len(alphabet)] + signature[1:]
    )
    if doctored["attestation"]["signature"] == signature:
        raise BuildError("attestation signature flip did not apply")
    return doctored


# --------------------------------------------------------------------------
# cells
# --------------------------------------------------------------------------

def trustconfig(authority, *, genesis, minimum=None, unpin_genesis=False,
                series=SERIES_ID):
    return registry.trustconfig_bytes(
        series_id=series,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=None if unpin_genesis else genesis,
        minimum_head_pin=minimum,
    )


def cell_payload(chain_payload, snapshot, trustconfig_bytes_value):
    payload = dict(chain_payload)
    payload["snapshot.json"] = registry.snapshot_bytes(snapshot)
    payload["trustconfig.json"] = trustconfig_bytes_value
    return payload


def manifest_text(directory):
    directory = Path(directory)
    lines = []
    for name in sorted(CELL_FILES):
        path = directory / name
        if path.is_file():
            lines.append("%s  %s" % (sha256_hex(path.read_bytes()), name))
    return "\n".join(lines) + "\n"


def write_cell(directory, payload):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name in CELL_FILES:
        target = directory / name
        if name in payload and payload[name] is not None:
            _atomic_write(target, payload[name])
        elif target.is_file():
            target.unlink()
    _atomic_write(directory / MANIFEST_NAME, manifest_text(directory).encode("utf-8"))


def _atomic_write(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def build_payloads(jpack_bin, work_root, owp_source):
    """Every registered cell's payload, keyed by cell id."""
    ns = upstream014.load(build=True)
    bf14 = ns.build_fixtures
    v1_bytes, v2_bytes = write_packs()
    executable_digest = "sha256:" + ns.verify.sha256_file(jpack_bin)

    judgments = Path(tempfile.mkdtemp(prefix="study016-jps-", dir=str(work_root)))
    base = bf14.decide(
        jpack_bin, judgments, v1_bytes, bf14.FACTS_BASE, bf14.EVIDENCE_PRESENT
    )
    successor = bf14.decide(
        jpack_bin, judgments, v2_bytes, bf14.FACTS_BASE, bf14.EVIDENCE_PRESENT
    )
    for name, decision in (("baseline", base), ("successor", successor)):
        if decision["disposition"].get("outcomeId") != "approve":
            raise BuildError("the %s decision does not approve" % name)
    if successor["envelope"].get("packVersion") != "0.2.0":
        raise BuildError("the successor envelope does not carry packVersion 0.2.0")

    base_commitment = bf14.commitment_for(base, executable_digest)
    successor_commitment = bf14.commitment_for(successor, executable_digest)
    v1_digest = base_commitment["judgment"]["packDigest"]
    v2_digest = successor_commitment["judgment"]["packDigest"]
    if v1_digest != "sha256:" + PACK_V1_SHA256 or v2_digest != "sha256:" + PACK_V2_SHA256:
        raise BuildError("commitment pack digests do not match the pinned packs")

    baseline = bf14.flow_cell(
        work_root, base, base_commitment, salt="baseline-016", owp_source=owp_source
    )
    successor_chain = bf14.flow_cell(
        work_root, successor, successor_commitment, salt="successor-016",
        owp_source=owp_source,
    )
    # The e22-analog: identical judgment commitment, different validly signed
    # work order — 014's registered construction, rebuilt under this study's
    # replay tuple. A pack-version registry accepts it; that acceptance is the
    # registered scope boundary (RFC 0011 R-1).
    remint = bf14.flow_cell(
        work_root, base, base_commitment, salt="workorder-remint-016",
        owp_source=owp_source,
        work_order_updates={
            "quota_ceiling": {"tool_calls": 200, "repair_rounds": 2},
            "acceptance_criteria": "The fixed verifier exits with status zero.",
        },
    )
    neg_bundle = bf14.bundle_of(baseline)
    neg_bundle["acceptance_receipt"]["signature"] = bf14.flip_character(
        neg_bundle["acceptance_receipt"]["signature"]
    )
    neg_owp = bf14.with_bundle(baseline, neg_bundle)
    # BINDING/REPLAY aliveness controls under the v0.17.0 tuple (round-1
    # R1-8): 014's a01 and e23 constructions, one negative control per
    # otherwise always-pass layer.
    drifted_pack = v1_bytes.replace(b'"5000"', b'"6000"')
    if drifted_pack == v1_bytes:
        raise BuildError("pack threshold edit did not apply")
    neg_binding = dict(baseline, **{"pack.json": drifted_pack})
    neg_replay = bf14.flow_cell(
        work_root, base,
        bf14.commitment_for(
            base, executable_digest,
            overrides={
                "executableDigest": "sha256:"
                + hashlib.sha256(b"study-016/wrong-executable").hexdigest(),
                "evaluatorRelease": "0.16.0",
            },
        ),
        salt="neg-replay-016", owp_source=owp_source,
    )

    authority = registry.private_key(registry.AUTHORITY_SEED)
    foreign = registry.private_key(registry.FOREIGN_SEED)
    snapshots, heads = registries(authority, foreign, v1_digest, v2_digest)
    genesis = heads["genesis"]
    tc = trustconfig(authority, genesis=genesis)

    cells = {}

    # ---- control gates ----------------------------------------------------
    cells["pos-current"] = cell_payload(baseline, snapshots["current"], tc)
    cells["unchanged"] = dict(cells["pos-current"])
    cells["neg-owp-alive"] = cell_payload(neg_owp, snapshots["current"], tc)
    cells["neg-snapshot-signature"] = cell_payload(
        baseline, broken_signature_snapshot(snapshots["current"]), tc
    )
    cells["neg-authority-unpinned"] = cell_payload(baseline, snapshots["impostor"], tc)
    cells["neg-chain-break"] = cell_payload(baseline, snapshots["chain-break"], tc)
    cells["neg-binding-alive"] = cell_payload(neg_binding, snapshots["current"], tc)
    cells["neg-replay-alive"] = cell_payload(neg_replay, snapshots["current"], tc)

    # ---- R: registry state ------------------------------------------------
    cells["cur-retired-reuse"] = cell_payload(baseline, snapshots["retiring"], tc)
    cells["cur-successor-current"] = cell_payload(
        successor_chain, snapshots["retiring"], tc
    )
    cells["cur-concurrent-set"] = cell_payload(
        baseline, snapshots["retiring-prefix-2"], tc
    )
    cells["cur-reinstated"] = cell_payload(baseline, snapshots["reinstated"], tc)
    cells["cur-rebind-refused"] = cell_payload(baseline, snapshots["rebound"], tc)
    # The second registered trust root (round-1 R1-10, registered rather than
    # silent): the verifier's per-series pins point it at a registry log that
    # carries no events for the pinned series - an empty answer, distinct from
    # a retirement. The seriesId stays the expense series; the genesis pin is
    # the other log's, both recorded in PINS.json.
    cells["cur-series-unknown"] = cell_payload(
        baseline, snapshots["other-series"],
        trustconfig(authority, genesis=heads["other-genesis"]),
    )

    # ---- S: scope boundaries ------------------------------------------------
    # 014's registered e22 construction rebuilt under this study's tuple: an
    # alternative, equally valid WorkOrder remint - NOT a rollback (round-1
    # R1-2): OWP has no contract ordering, so nothing is "older". Descriptive,
    # excluded from R1 credit, exactly 014's e22 precedent.
    cells["cur-workorder-remint-accepted"] = cell_payload(
        remint, snapshots["current"], tc
    )
    cells["cur-split-view-a"] = cell_payload(baseline, snapshots["view-a"], tc)
    cells["cur-split-view-b"] = cell_payload(baseline, snapshots["view-b"], tc)
    # The stateful arm (round-1 R1-4): a verifier that previously accepted
    # view A at position 2 - provisioned as its minimum head pin - refuses
    # view B at the same position by prefix containment. The fresh-verifier
    # silence in the pair above is exactly statelessness.
    cells["cur-split-view-b-stateful"] = cell_payload(
        baseline, snapshots["view-b"],
        trustconfig(
            authority, genesis=genesis,
            minimum={"head": heads["view-a-head"], "position": 2},
        ),
    )

    # ---- V: verifier configuration ----------------------------------------
    cells["cur-older-snapshot-pinned"] = cell_payload(
        baseline, snapshots["retiring-prefix-2"],
        trustconfig(
            authority, genesis=genesis,
            minimum={"head": heads["retiring-head"], "position": 3},
        ),
    )
    cells["cur-genesis-unpinned"] = cell_payload(
        baseline, snapshots["current"],
        trustconfig(authority, genesis=genesis, unpin_genesis=True),
    )

    # ---- D: demonstrations (byte-copies; the registered identity groups) --
    cells["dem-freshness-legit"] = dict(cells["cur-retired-reuse"])
    cells["dem-freshness-stale"] = dict(cells["cur-retired-reuse"])

    return cells


def cell_directory(out_root, cell_id):
    return Path(out_root) / "cells" / cell_id


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(STUDY / "fixtures"))
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args(argv)

    jpack_bin = os.environ.get("JPACK_BIN")
    owp_source = os.environ.get("OWP_SOURCE")
    if not jpack_bin or not Path(jpack_bin).is_file():
        raise SystemExit("JPACK_BIN is not available")
    if not owp_source or not Path(owp_source).is_dir():
        raise SystemExit("OWP_SOURCE is not available")

    out_root = Path(arguments.out)
    cells_root = out_root / "cells"
    if cells_root.exists():
        if not arguments.force:
            raise SystemExit("fixtures already exist; pass --force to rebuild")
        shutil.rmtree(cells_root)

    work_root = Path(tempfile.mkdtemp(prefix="study016-build-"))
    try:
        cells = build_payloads(jpack_bin, work_root, owp_source)
    finally:
        shutil.rmtree(work_root, ignore_errors=True)

    for cell_id, payload in sorted(cells.items()):
        write_cell(cell_directory(out_root, cell_id), payload)
    print("built %d cells under %s" % (len(cells), out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# --------------------------------------------------------------------------
# the reviewer-authored holdout stratum — implemented, NEVER run pre-freeze
# --------------------------------------------------------------------------
#
# Hooks for the round-2 reviewer's cells (harness/MATRIX-HOLDOUT.json,
# committed verbatim with attribution). They are library entry points the
# scorer alone drives, inside a post-freeze attempt: every route requires a
# `HoldoutAttemptContext` whose digests are re-derived from disk and whose
# validity requires every freeze pin non-null — so pre-freeze, any context
# fails and nothing here can execute. There is deliberately no command-line
# route (014 round-4's lesson). Every construction is a deterministic byte or
# registry operation over the frozen locked fixtures and the registry writer;
# none drives an upstream OWP publication path, so construction statuses are
# `built` or `harness-error` only (the 014 upstream-refusal class does not
# apply, stated in the holdout registry's note).

import dataclasses  # noqa: E402


@dataclasses.dataclass(frozen=True)
class HoldoutAttemptContext:
    """Minted by harness/score.py after its freeze gates pass; verified here."""
    attempt_root: str
    pins_raw_sha256: str
    preregistration_sha256: str
    matrix_holdout_sha256: str


class HoldoutRefused(RuntimeError):
    """The holdout route was driven without a valid post-freeze context."""


def holdout_context_problems(context):
    """Re-derive every digest from disk; refuse pre-freeze or forged contexts."""
    if not isinstance(context, HoldoutAttemptContext):
        return ["holdout construction requires a HoldoutAttemptContext"]
    problems = []
    pins_raw = (STUDY / "harness" / "PINS.json").read_bytes()
    if hashlib.sha256(pins_raw).hexdigest() != context.pins_raw_sha256:
        problems.append("context pins digest does not match the live registry")
    pins = json.loads(pins_raw.decode("utf-8"))
    for member in ("preregistration", "matrix", "matrixHoldout", "registrySpec",
                   "studyManifest"):
        if (pins.get(member) or {}).get("sha256") is None:
            problems.append("freeze pin %s is null: the stratum executes only "
                            "after the freeze" % member)
    for attribute, relative in (
        ("preregistration_sha256", "PREREGISTRATION.md"),
        ("matrix_holdout_sha256", "harness/MATRIX-HOLDOUT.json"),
    ):
        live = hashlib.sha256((STUDY / relative).read_bytes()).hexdigest()
        if getattr(context, attribute) != live:
            problems.append("context %s does not match the live file" % attribute)
    if not Path(context.attempt_root).is_dir():
        problems.append("context attempt root does not exist")
    return problems


def _require_context(context):
    problems = holdout_context_problems(context)
    if problems:
        raise HoldoutRefused("; ".join(problems))


def _locked_cell_payload(cell_id):
    """The frozen locked cell's bytes, verified against its own manifest."""
    directory = cell_directory(STUDY / "fixtures", cell_id)
    manifest = (directory / MANIFEST_NAME).read_text(encoding="utf-8")
    payload = {}
    listed = {}
    for line in manifest.splitlines():
        if line.strip():
            digest, _, name = line.partition("  ")
            listed[name] = digest
    for name in CELL_FILES:
        path = directory / name
        if not path.is_file():
            raise BuildError("%s: %s is absent" % (cell_id, name))
        data = path.read_bytes()
        if listed.get(name) != sha256_hex(data):
            raise BuildError("%s: %s does not match its frozen manifest" % (cell_id, name))
        payload[name] = data
    return payload


def _replace_once(data, old, new, what):
    text = data.decode("utf-8")
    if text.count(old) != 1:
        raise BuildError("%s: expected exactly one occurrence of %r" % (what, old))
    return text.replace(old, new).encode("utf-8")


def _authority():
    import checkpoint as registry
    return registry, registry.private_key(registry.AUTHORITY_SEED)


def _holdout_h01(context):
    payload = _locked_cell_payload("pos-current")
    payload["trustconfig.json"] = _replace_once(
        payload["trustconfig.json"], '"minimumHeadPin": null',
        '"minimumHeadPin": null,\n  "minimumHeadPin": null', "h01 trustconfig",
    )
    return payload


def _holdout_h02(context):
    payload = _locked_cell_payload("pos-current")
    payload["snapshot.json"] = _replace_once(
        payload["snapshot.json"], '"position": 1', '"position": true',
        "h02 snapshot",
    )
    return payload


def _holdout_h03(context):
    registry, authority = _authority()
    payload = _locked_cell_payload("pos-current")
    d1 = "sha256:" + PACK_V1_SHA256
    d2 = "sha256:" + PACK_V2_SHA256
    presented = registry.build_registry(authority, [
        event("add", "0.1.0", d1, T1), event("retire", "0.1.0", effective=T2),
        event("add", "0.1.0", d2, T3),
    ])
    sibling = registry.build_registry(authority, [
        event("add", "0.1.0", d1, T1), event("add", "0.2.0", d2, T2),
    ])
    payload["snapshot.json"] = registry.snapshot_bytes(
        registry.snapshot_of(authority, presented)
    )
    payload["trustconfig.json"] = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=presented[0]["checkpointDigest"],
        minimum_head_pin={"head": sibling[1]["checkpointDigest"], "position": 2},
    )
    return payload


def _holdout_h04(context):
    registry, authority = _authority()
    payload = _locked_cell_payload("pos-current")
    records = registry.build_registry(authority, [
        event("add", "0.1.0", "sha256:" + PACK_V1_SHA256, T1),
        event("add", "0.1.0", "sha256:" + PACK_V2_SHA256, T2),
    ])
    payload["snapshot.json"] = registry.snapshot_bytes(
        registry.snapshot_of(authority, records)
    )
    payload["trustconfig.json"] = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=records[0]["checkpointDigest"],
    )
    return payload


def _retiring_snapshot_and_trust():
    registry, authority = _authority()
    records = registry.build_registry(authority, [
        event("add", "0.1.0", "sha256:" + PACK_V1_SHA256, T1),
        event("add", "0.2.0", "sha256:" + PACK_V2_SHA256, T2),
        event("retire", "0.1.0", effective=T3),
    ])
    snapshot = registry.snapshot_bytes(registry.snapshot_of(authority, records))
    trust = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=records[0]["checkpointDigest"],
    )
    return snapshot, trust


def _holdout_h05(context):
    payload = _locked_cell_payload("neg-replay-alive")
    payload["snapshot.json"], payload["trustconfig.json"] = _retiring_snapshot_and_trust()
    return payload


def _holdout_h06(context):
    registry, authority = _authority()
    payload = _locked_cell_payload("cur-successor-current")
    records = registry.build_registry(authority, [
        event("add", "0.1.0", "sha256:" + PACK_V1_SHA256, T1),
    ])
    payload["snapshot.json"] = registry.snapshot_bytes(
        registry.snapshot_of(authority, records)
    )
    payload["trustconfig.json"] = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=records[0]["checkpointDigest"],
    )
    return payload


def _holdout_h07(context):
    registry, authority = _authority()
    payload = _locked_cell_payload("pos-current")
    d1 = "sha256:" + PACK_V1_SHA256
    events = [event("add", "0.1.0", d1, T1)]
    events += [event("add", "9.0.%d" % n, d1, T2) for n in range(1, 512)]
    records = registry.build_registry(authority, events)
    payload["snapshot.json"] = registry.snapshot_bytes(
        registry.snapshot_of(authority, records)
    )
    payload["trustconfig.json"] = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=records[0]["checkpointDigest"],
    )
    return payload


def _holdout_h08(context):
    registry, authority = _authority()
    payload = _locked_cell_payload("pos-current")
    events = [event("add", "0.1.0", "sha256:" + PACK_V1_SHA256, T1)]
    events += [
        event("add", "1.0.%d" % n, OTHER_SERIES_DIGEST, T2, series=OTHER_SERIES_ID)
        for n in range(1, 1024)
    ]
    records = registry.build_registry(authority, events)
    snapshot = registry.snapshot_bytes(registry.snapshot_of(authority, records))
    if len(records) != 1024:
        raise BuildError("h08: expected exactly 1024 checkpoints")
    payload["snapshot.json"] = snapshot
    payload["trustconfig.json"] = registry.trustconfig_bytes(
        series_id=SERIES_ID,
        authority_public_key=registry.public_key_b64(authority),
        genesis_head=records[0]["checkpointDigest"],
    )
    return payload


def _holdout_h09(context):
    payload = _locked_cell_payload("pos-current")
    target = 1_048_576
    snapshot = payload["snapshot.json"]
    if len(snapshot) >= target:
        raise BuildError("h09: baseline snapshot is not below the byte limit")
    payload["snapshot.json"] = snapshot + b" " * (target - len(snapshot))
    return payload


def _holdout_h10(context):
    payload = _locked_cell_payload("pos-current")
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    authority_id = pins["registryAuthority"]["authorityKeyId"]
    foreign_id = pins["registryAuthority"]["foreignKeyId"]
    text = payload["snapshot.json"].decode("utf-8")
    if authority_id not in text:
        raise BuildError("h10: authority key id not present in the snapshot")
    payload["snapshot.json"] = text.replace(authority_id, foreign_id).encode("utf-8")
    return payload


HOLDOUT_HOOKS = {
    "h01": _holdout_h01, "h02": _holdout_h02, "h03": _holdout_h03,
    "h04": _holdout_h04, "h05": _holdout_h05, "h06": _holdout_h06,
    "h07": _holdout_h07, "h08": _holdout_h08, "h09": _holdout_h09,
    "h10": _holdout_h10,
}


def builder_version_digest():
    return sha256_hex(Path(__file__).read_bytes())


def construct_holdout(context, out_root, cells):
    """Build every registered holdout cell inside the attempt. Scorer-only.

    Returns per-cell construction records; every outcome is persisted as
    `<out_root>/<id>/CONSTRUCTION.json` with status `built` or `harness-error`
    (see the module note on why the 014 `refused` class does not apply here).
    `SystemExit`/`KeyboardInterrupt` propagate to the scorer's terminal path.
    """
    _require_context(context)
    out_root = Path(out_root)
    if Path(context.attempt_root).resolve() not in out_root.resolve().parents:
        raise HoldoutRefused("holdout output must live inside the context's attempt")
    records = {}
    for cell in cells:
        cell_id = cell["id"]
        directory = out_root / cell_id
        record = {"cell": cell_id, "builderVersionDigest": builder_version_digest()}
        hook = HOLDOUT_HOOKS.get(cell_id)
        try:
            if hook is None:
                raise BuildError("no construction hook is registered for " + cell_id)
            payload = hook(context)
            write_cell(directory, payload)
            record["status"] = "built"
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as error:
            record["status"] = "harness-error"
            record["harnessError"] = "%s: %s" % (type(error).__name__, error)
        directory.mkdir(parents=True, exist_ok=True)
        _atomic_write(
            directory / "CONSTRUCTION.json",
            (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        )
        records[cell_id] = record
    return records
