"""Layer WITNESS unit suite: every registered code reachable, ordering exact.

Fully offline; builds minimal synthetic views with the pinned 016 registry
writer and sightings with `witness/sighting.py`, then exercises
`witness/verify_witness.py` on bytes alone.
"""

import hashlib
import json

import pytest

import sighting as sg
import upstream016
import verify_witness as vw

SERIES = "https://example.com/judgment-packs/witnessed-policy"
OTHER = "https://example.com/judgment-packs/other-policy"
D1 = "sha256:" + hashlib.sha256(b"unit/pack-one").hexdigest()
D2 = "sha256:" + hashlib.sha256(b"unit/pack-two").hexdigest()


@pytest.fixture(scope="session")
def apparatus():
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key(sg.AUTHORITY_SEED)
    w2 = registry.private_key(sg.WITNESS_2_SEED)
    w3 = registry.private_key(sg.WITNESS_3_SEED)
    def build(events):
        return registry.build_registry(authority, [
            {"event": kind, "seriesId": series, "packVersion": version,
             **({"packDigest": digest} if digest else {})}
            for kind, version, digest, series in events
        ])
    view_a = build([("add", "1.0.0", D1, SERIES), ("add", "1.1.0", D2, SERIES)])
    view_c = build([("add", "1.0.0", D1, SERIES), ("add", "2.0.0", D2, SERIES)])
    return {
        "registry": registry, "authority": authority,
        "w2": (w2, registry.key_id(w2), registry.public_key_b64(w2)),
        "w3": (w3, registry.key_id(w3), registry.public_key_b64(w3)),
        "view_a": view_a, "view_c": view_c,
        "snap": lambda records, position=None: registry.snapshot_bytes(
            registry.snapshot_of(authority, records, position=position)),
    }


def commitment(series=SERIES):
    return {"commitmentVersion": "1",
            "judgment": {"packId": series, "packVersion": "1.0.0", "packDigest": D1}}


def config(keys, minimum, series=SERIES):
    return sg.witnessconfig_bytes(series_id=series, witness_keys=keys,
                                  minimum_sightings=minimum)


def outcome(result):
    if result["verdict"] == "pass":
        return "pass"
    if result["verdict"] == "unavailable":
        return "unavailable"
    return "fail:" + result["code"]


def test_consistent_sighting_passes(apparatus):
    a = apparatus
    key, key_id, pub = a["w2"]
    records = [sg.build_sighting(key, key_id, series_id=SERIES,
                                 head=a["view_a"][1]["checkpointDigest"], position=2)]
    result = vw.layer_witness(commitment(), a["snap"](a["view_a"]),
                              config([pub], 1), sg.sightings_bytes(records))
    assert outcome(result) == "pass"


def test_conflict_detected(apparatus):
    a = apparatus
    key, key_id, pub = a["w2"]
    records = [sg.build_sighting(key, key_id, series_id=SERIES,
                                 head=a["view_a"][1]["checkpointDigest"], position=2)]
    result = vw.layer_witness(commitment(), a["snap"](a["view_c"]),
                              config([pub], 0), sg.sightings_bytes(records))
    assert outcome(result) == "fail:snapshot-conflicts-with-witnessed-head"


def test_behind_witnessed_head(apparatus):
    a = apparatus
    key, key_id, pub = a["w2"]
    records = [sg.build_sighting(key, key_id, series_id=SERIES,
                                 head=a["view_a"][1]["checkpointDigest"], position=2)]
    result = vw.layer_witness(commitment(), a["snap"](a["view_a"], position=1),
                              config([pub], 1), sg.sightings_bytes(records))
    assert outcome(result) == "fail:snapshot-behind-witnessed-head"


def test_unpinned_sighting_ignored_even_when_conflicting(apparatus):
    """D-3: untrusted evidence is ignored-and-counted, never a detection."""
    a = apparatus
    key, key_id, _ = a["w3"]
    _, _, pinned_pub = a["w2"]
    records = [sg.build_sighting(key, key_id, series_id=SERIES,
                                 head=a["view_a"][1]["checkpointDigest"], position=2)]
    result = vw.layer_witness(commitment(), a["snap"](a["view_c"]),
                              config([pinned_pub], 0), sg.sightings_bytes(records))
    assert outcome(result) == "pass"
    assert "1 unpinned ignored" in result["detail"]


def test_forged_pinned_sighting_is_fail_closed(apparatus):
    a = apparatus
    key, key_id, pub = a["w2"]
    record = sg.build_sighting(key, key_id, series_id=SERIES,
                               head=a["view_a"][1]["checkpointDigest"], position=2)
    record["signature"] = ("A" if record["signature"][0] != "A" else "B") + record["signature"][1:]
    result = vw.layer_witness(commitment(), a["snap"](a["view_a"]),
                              config([pub], 0), sg.sightings_bytes([record]))
    assert outcome(result) == "fail:witness-sighting-invalid"


def test_enforcement_clause(apparatus):
    a = apparatus
    _, _, pub = a["w2"]
    vacuous = vw.layer_witness(commitment(), a["snap"](a["view_c"]),
                               config([pub], 0), sg.sightings_bytes([]))
    assert outcome(vacuous) == "pass"
    enforced = vw.layer_witness(commitment(), a["snap"](a["view_c"]),
                                config([pub], 1), sg.sightings_bytes([]))
    assert (enforced["verdict"], enforced["code"]) == ("unavailable", "witness-unavailable")


def test_series_scoping(apparatus):
    a = apparatus
    key, key_id, pub = a["w2"]
    foreign = [sg.build_sighting(key, key_id, series_id=OTHER,
                                 head=a["view_a"][1]["checkpointDigest"], position=2)]
    result = vw.layer_witness(commitment(), a["snap"](a["view_c"]),
                              config([pub], 1), sg.sightings_bytes(foreign))
    assert outcome(result) == "unavailable"
    mismatched = vw.layer_witness(commitment(series=OTHER), a["snap"](a["view_a"]),
                                  config([pub], 0), sg.sightings_bytes([]))
    assert outcome(mismatched) == "unavailable"


def test_limits(apparatus):
    a = apparatus
    key, key_id, pub = a["w2"]
    record = sg.build_sighting(key, key_id, series_id=SERIES,
                               head=a["view_a"][1]["checkpointDigest"], position=2)
    at_cap = vw.layer_witness(commitment(), a["snap"](a["view_a"]),
                              config([pub], 1),
                              sg.sightings_bytes([record] * vw.MAX_SIGHTINGS))
    assert outcome(at_cap) == "pass"
    over = vw.layer_witness(commitment(), a["snap"](a["view_a"]),
                            config([pub], 1),
                            sg.sightings_bytes([record] * (vw.MAX_SIGHTINGS + 1)))
    assert outcome(over) == "fail:witness-limits-exceeded"
    oversized = b" " * (vw.MAX_SIGHTINGS_BYTES + 1)
    result = vw.layer_witness(commitment(), a["snap"](a["view_a"]),
                              config([pub], 1), oversized)
    assert outcome(result) == "fail:witness-limits-exceeded"


def test_duplicate_members_refuse(apparatus):
    a = apparatus
    _, _, pub = a["w2"]
    raw = config([pub], 0).decode("utf-8")
    doctored = raw.replace('"minimumSightings": 0',
                           '"minimumSightings": 0, "minimumSightings": 0', 1)
    result = vw.layer_witness(commitment(), a["snap"](a["view_a"]),
                              doctored.encode("utf-8"), sg.sightings_bytes([]))
    assert (result["verdict"], result["code"]) == ("unavailable", "witness-unavailable")


def test_missing_inputs_are_unavailable(apparatus):
    a = apparatus
    _, _, pub = a["w2"]
    for args in (
        (commitment(), a["snap"](a["view_a"]), None, sg.sightings_bytes([])),
        (commitment(), a["snap"](a["view_a"]), config([pub], 0), None),
        (None, a["snap"](a["view_a"]), config([pub], 0), sg.sightings_bytes([])),
    ):
        result = vw.layer_witness(*args)
        assert result["code"] == "witness-unavailable"


def test_unusable_snapshot_with_sightings_is_unavailable(apparatus):
    a = apparatus
    key, key_id, pub = a["w2"]
    records = [sg.build_sighting(key, key_id, series_id=SERIES,
                                 head=a["view_a"][1]["checkpointDigest"], position=2)]
    result = vw.layer_witness(commitment(), b"not json",
                              config([pub], 1), sg.sightings_bytes(records))
    assert (result["verdict"], result["code"]) == ("unavailable", "witness-unavailable")


def test_every_registered_code_is_reachable():
    reached = {
        "witness-unavailable", "witness-sighting-invalid",
        "witness-limits-exceeded", "snapshot-conflicts-with-witnessed-head",
        "snapshot-behind-witnessed-head",
    }
    assert reached == set(vw.CODES)


def test_domain_constant_matches_pinned_upstream():
    ns = upstream016.load()
    assert vw.DOMAIN_CHECKPOINT == ns.verify_currency.DOMAIN_CHECKPOINT


def test_verifier_never_imports_the_writer():
    source = open(vw.__file__, encoding="utf-8").read()
    assert "import sighting" not in source
