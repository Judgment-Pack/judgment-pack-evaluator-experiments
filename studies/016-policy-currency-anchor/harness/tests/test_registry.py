"""Layer CURRENCY unit suite: every registered code reachable, ordering exact.

No toolchain needed: these tests exercise `registry/verify_currency.py` against
minimal synthetic snapshots built with `registry/checkpoint.py`. The commitment
is a synthetic tuple — the layer reads only `judgment.{packId,packVersion,
packDigest}` and this suite pins that surface.
"""

import copy
import hashlib
import json

import checkpoint as cp
import verify_currency as vc

SERIES = "https://example.com/judgment-packs/expense-approval"
OTHER = "https://example.com/judgment-packs/other-policy"
D1 = "sha256:" + hashlib.sha256(b"pack-one").hexdigest()
D2 = "sha256:" + hashlib.sha256(b"pack-two").hexdigest()

AUTH = cp.private_key(cp.AUTHORITY_SEED)
FOREIGN = cp.private_key(cp.FOREIGN_SEED)


def commitment(version="0.1.0", digest=D1, series=SERIES):
    return {"commitmentVersion": "1",
            "judgment": {"packId": series, "packVersion": version,
                         "packDigest": digest}}


def registry_events(*entries):
    return cp.build_registry(AUTH, [
        {"event": kind, "seriesId": series, "packVersion": version,
         **({"packDigest": digest} if digest else {})}
        for kind, version, digest, series in entries
    ])


def snap_bytes(records, key=AUTH, position=None):
    return cp.snapshot_bytes(cp.snapshot_of(key, records, position=position))


def trust(records, minimum=None, genesis=True, authority=True):
    return json.loads(cp.trustconfig_bytes(
        authority_public_key=cp.public_key_b64(AUTH) if authority else None,
        genesis_head=records[0]["checkpointDigest"] if genesis else None,
        persisted_minimum_head=minimum,
    ).decode("utf-8"))


BASE = registry_events(("add", "0.1.0", D1, SERIES))


def outcome(result):
    if result["verdict"] == "pass":
        return "pass"
    if result["verdict"] == "unavailable":
        return "unavailable"
    return "fail:" + result["code"]


# ---- pass and unavailable -------------------------------------------------

def test_membership_passes():
    assert outcome(vc.layer_currency(commitment(), snap_bytes(BASE), trust(BASE))) == "pass"


def test_no_authority_pin_is_unavailable():
    result = vc.layer_currency(commitment(), snap_bytes(BASE), trust(BASE, authority=False))
    assert (result["verdict"], result["code"]) == ("unavailable", "currency-unavailable")


def test_no_genesis_pin_is_unavailable():
    result = vc.layer_currency(commitment(), snap_bytes(BASE), trust(BASE, genesis=False))
    assert (result["verdict"], result["code"]) == ("unavailable", "currency-unavailable")


def test_missing_snapshot_is_unavailable():
    result = vc.layer_currency(commitment(), None, trust(BASE))
    assert (result["verdict"], result["code"]) == ("unavailable", "currency-unavailable")


def test_missing_commitment_is_unavailable():
    result = vc.layer_currency(None, snap_bytes(BASE), trust(BASE))
    assert (result["verdict"], result["code"]) == ("unavailable", "currency-unavailable")


def test_unavailable_wins_over_any_snapshot_defect():
    """Ordering: pins are checked before the snapshot is even parsed."""
    result = vc.layer_currency(commitment(), b"not json", trust(BASE, genesis=False))
    assert result["code"] == "currency-unavailable"


# ---- signature and authority ----------------------------------------------

def test_foreign_signed_snapshot_is_authority_unpinned():
    impostor = cp.build_registry(FOREIGN, [
        {"event": "add", "seriesId": SERIES, "packVersion": "0.1.0", "packDigest": D1}
    ])
    result = vc.layer_currency(
        commitment(), snap_bytes(impostor, key=FOREIGN), trust(BASE)
    )
    assert outcome(result) == "fail:snapshot-authority-unpinned"


def test_flipped_attestation_signature_is_invalid():
    snapshot = json.loads(snap_bytes(BASE).decode("utf-8"))
    signature = snapshot["attestation"]["signature"]
    snapshot["attestation"]["signature"] = ("A" if signature[0] != "A" else "B") + signature[1:]
    result = vc.layer_currency(
        commitment(), json.dumps(snapshot).encode("utf-8"), trust(BASE)
    )
    assert outcome(result) == "fail:snapshot-signature-invalid"


def test_key_identity_is_checked_before_signature_math():
    """A foreign-signed snapshot with a doctored chain still reports the key."""
    impostor = cp.build_registry(FOREIGN, [
        {"event": "add", "seriesId": SERIES, "packVersion": "0.1.0", "packDigest": D1}
    ])
    snapshot = json.loads(snap_bytes(impostor, key=FOREIGN).decode("utf-8"))
    snapshot["checkpoints"][0]["checkpoint"]["sequence"] = 7
    result = vc.layer_currency(
        commitment(), json.dumps(snapshot).encode("utf-8"), trust(BASE)
    )
    assert outcome(result) == "fail:snapshot-authority-unpinned"


# ---- chain structure -------------------------------------------------------

def test_resigned_broken_linkage_is_chain_inconsistent():
    second = cp.build_checkpoint(
        AUTH, sequence=2, series_id=SERIES, event="add", pack_version="0.2.0",
        pack_digest=D2, effective_from="2026-01-15T00:00:00Z",
        previous="sha256:" + hashlib.sha256(b"not-the-genesis").hexdigest(),
    )
    result = vc.layer_currency(
        commitment(), snap_bytes([BASE[0], second]), trust(BASE)
    )
    assert outcome(result) == "fail:snapshot-chain-inconsistent"


def test_wrong_genesis_pin_is_chain_inconsistent():
    config = trust(BASE)
    config["genesisHead"] = "sha256:" + hashlib.sha256(b"other-genesis").hexdigest()
    result = vc.layer_currency(commitment(), snap_bytes(BASE), config)
    assert outcome(result) == "fail:snapshot-chain-inconsistent"


def test_attestation_head_mismatch_is_chain_inconsistent():
    two = registry_events(("add", "0.1.0", D1, SERIES), ("add", "0.2.0", D2, SERIES))
    snapshot = json.loads(snap_bytes(two).decode("utf-8"))
    snapshot["checkpoints"] = snapshot["checkpoints"][:1]
    result = vc.layer_currency(commitment(), json.dumps(snapshot).encode("utf-8"), trust(two))
    assert outcome(result) == "fail:snapshot-chain-inconsistent"


def test_retire_of_non_current_is_chain_inconsistent():
    records = registry_events(("add", "0.1.0", D1, SERIES), ("retire", "0.2.0", None, SERIES))
    result = vc.layer_currency(commitment(), snap_bytes(records), trust(records))
    assert outcome(result) == "fail:snapshot-chain-inconsistent"


def test_reinstate_of_non_retired_is_chain_inconsistent():
    records = registry_events(("add", "0.1.0", D1, SERIES), ("reinstate", "0.1.0", None, SERIES))
    result = vc.layer_currency(commitment(), snap_bytes(records), trust(records))
    assert outcome(result) == "fail:snapshot-chain-inconsistent"


# ---- rebind, recency, fold -------------------------------------------------

def test_rebind_is_its_own_code():
    records = registry_events(
        ("add", "0.1.0", D1, SERIES), ("retire", "0.1.0", None, SERIES),
        ("add", "0.1.0", D2, SERIES),
    )
    result = vc.layer_currency(commitment(), snap_bytes(records), trust(records))
    assert outcome(result) == "fail:binding-rebound"


def test_older_snapshot_refused_iff_minimum_head_persisted():
    records = registry_events(
        ("add", "0.1.0", D1, SERIES), ("add", "0.2.0", D2, SERIES),
        ("retire", "0.1.0", None, SERIES),
    )
    prefix = snap_bytes(records, position=2)
    unpinned = vc.layer_currency(commitment(), prefix, trust(records))
    assert outcome(unpinned) == "pass"
    minimum = {"head": records[2]["checkpointDigest"], "position": 3}
    pinned = vc.layer_currency(commitment(), prefix, trust(records, minimum=minimum))
    assert outcome(pinned) == "fail:snapshot-older-than-accepted-head"


def test_same_length_fork_refused_by_prefix_containment():
    """The persisted head is containment, not position arithmetic."""
    view_a = registry_events(("add", "0.1.0", D1, SERIES), ("add", "0.2.0", D2, SERIES))
    view_b = registry_events(("add", "0.1.0", D1, SERIES), ("retire", "0.1.0", None, SERIES))
    minimum = {"head": view_a[1]["checkpointDigest"], "position": 2}
    result = vc.layer_currency(
        commitment(), snap_bytes(view_b), trust(view_b, minimum=minimum)
    )
    assert outcome(result) == "fail:snapshot-older-than-accepted-head"


def test_split_view_halves_are_individually_silent():
    """Both views verify with no fork-revealing code; the contradiction is the pair."""
    view_a = registry_events(("add", "0.1.0", D1, SERIES), ("add", "0.2.0", D2, SERIES))
    view_b = registry_events(("add", "0.1.0", D1, SERIES), ("retire", "0.1.0", None, SERIES))
    assert view_a[0]["checkpointDigest"] == view_b[0]["checkpointDigest"]
    a = vc.layer_currency(commitment(), snap_bytes(view_a), trust(view_a))
    b = vc.layer_currency(commitment(), snap_bytes(view_b), trust(view_b))
    assert outcome(a) == "pass"
    assert outcome(b) == "fail:not-current-at-snapshot"


def test_series_unknown_is_distinct_from_not_current():
    other = registry_events(("add", "1.0.0", D2, OTHER))
    unknown = vc.layer_currency(commitment(), snap_bytes(other), trust(other))
    assert outcome(unknown) == "fail:series-unknown-at-snapshot"
    retired = registry_events(("add", "0.1.0", D1, SERIES), ("retire", "0.1.0", None, SERIES))
    not_current = vc.layer_currency(commitment(), snap_bytes(retired), trust(retired))
    assert outcome(not_current) == "fail:not-current-at-snapshot"


def test_reinstated_version_is_current_again():
    records = registry_events(
        ("add", "0.1.0", D1, SERIES), ("retire", "0.1.0", None, SERIES),
        ("reinstate", "0.1.0", None, SERIES),
    )
    assert outcome(vc.layer_currency(commitment(), snap_bytes(records), trust(records))) == "pass"


def test_concurrent_set_membership_not_maximum():
    records = registry_events(("add", "0.1.0", D1, SERIES), ("add", "0.2.0", D2, SERIES))
    config = trust(records)
    assert outcome(vc.layer_currency(commitment(), snap_bytes(records), config)) == "pass"
    assert outcome(vc.layer_currency(commitment("0.2.0", D2), snap_bytes(records), config)) == "pass"


def test_effective_from_is_never_compared():
    """No clock: absurd effectiveFrom values change nothing (decision D-5)."""
    records = cp.build_registry(AUTH, [{
        "event": "add", "seriesId": SERIES, "packVersion": "0.1.0",
        "packDigest": D1, "effectiveFrom": "9999-12-31T23:59:59Z",
    }])
    assert outcome(vc.layer_currency(commitment(), snap_bytes(records), trust(records))) == "pass"


def test_every_registered_code_is_reachable():
    """The union of codes exercised above equals the registered vocabulary."""
    reached = {
        "currency-unavailable", "snapshot-authority-unpinned",
        "snapshot-signature-invalid", "snapshot-chain-inconsistent",
        "binding-rebound", "snapshot-older-than-accepted-head",
        "series-unknown-at-snapshot", "not-current-at-snapshot",
    }
    assert reached == set(vc.CODES)


def test_verifier_never_imports_the_writer():
    import verify_currency
    source = open(verify_currency.__file__, encoding="utf-8").read()
    assert "import checkpoint" not in source
