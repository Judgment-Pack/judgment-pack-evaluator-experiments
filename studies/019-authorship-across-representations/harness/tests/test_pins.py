"""The registered label rule: any null freeze pin makes the run a PILOT.

Study 014's round 3 found a REGISTERED run reachable with only the
preregistration digest filled, which left the registry the attempt adjudicated
unpinned. The rule this study registers is over the WHOLE freeze set, and it is
decided in exactly one function. These tests drive that function over the
committed registry and over mutated copies of it — one null at a time — so
"every pin" is asserted pin by pin rather than as a sentence.
"""
import copy

import integrity


def test_the_committed_registry_is_pre_freeze_and_labels_pilot(pins):
    assert integrity.study_label(pins) == "PILOT"
    # And it says WHICH pins are null, in registered order, so a PILOT label is
    # actionable rather than a mood.
    assert integrity.unfilled_pins(pins) == \
        [name for name, _path in integrity.FREEZE_PINS]


def _fill(pins):
    """The committed registry with every freeze pin filled with a plausible
    digest — the only state in which REGISTERED is reachable."""
    filled = copy.deepcopy(pins)
    for _name, path in integrity.FREEZE_PINS:
        node = filled
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = "sha256:" + "0" * 64
    return filled


def test_a_fully_filled_registry_labels_registered(pins):
    assert integrity.study_label(_fill(pins)) == "REGISTERED"


def test_every_single_null_pin_is_enough_to_make_it_a_pilot(pins):
    filled = _fill(pins)
    for name, path in integrity.FREEZE_PINS:
        one_null = copy.deepcopy(filled)
        node = one_null
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = None
        assert integrity.study_label(one_null) == "PILOT", name
        assert integrity.unfilled_pins(one_null) == [name]


def test_a_missing_parent_object_counts_as_null_rather_than_raising(pins):
    filled = _fill(pins)
    del filled["references"]
    assert integrity.study_label(filled) == "PILOT"
    assert integrity.unfilled_pins(filled) == ["referenceA", "referenceB"]


def test_the_freeze_pin_set_is_the_registered_one():
    """The registry's own label rule names the pins in prose; the code names
    them in a tuple. A one-sided edit names its own drift site."""
    assert [name for name, _path in integrity.FREEZE_PINS] == [
        "preregistration", "policyProse", "goldSuite",
        "matrixA", "matrixB", "matrixC",
        "mutantManifests", "referenceA", "referenceB",
        "offGoldCertificate", "studyManifest"]


def test_the_registry_states_the_rule_the_code_implements(pins):
    rule = pins["registeredLabelRule"]
    assert "REGISTERED only when EVERY freeze pin below is non-null" in rule
    assert "Any null makes it a PILOT" in rule
    for name, _path in integrity.FREEZE_PINS:
        assert name in rule, name


def test_the_resolved_toolchain_blocks_are_marked_and_carry_digests(pins):
    """The design-time resolutions are pins already: they are enforced under
    both labels, and they are marked so a reader cannot mistake a resolved
    digest for a freeze pin."""
    for name in ("jpack", "opa", "codex"):
        assert pins[name]["resolvedAtDesignTime"] is True, name
    assert pins["jpack"]["binarySha256"].startswith("sha256:")
    assert pins["opa"]["assetSha256"].startswith("sha256:")
    assert pins["codex"]["binarySha256"].startswith("sha256:")
    # …and the two that are NOT resolved yet are null rather than plausible.
    assert pins["codex"]["model"] is None
    assert pins["opa"]["capabilitiesSha256"] is None
    assert pins["jpack"]["reproducibleBuildAttestation"] is None


def test_the_anchor_order_is_linear_and_says_so(pins):
    assert pins["anchorOrder"].startswith("LINEAR")
    assert "covers NEITHER itself NOR this file" in pins["anchorOrder"]
