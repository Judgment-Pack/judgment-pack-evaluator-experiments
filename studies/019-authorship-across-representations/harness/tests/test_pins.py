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
    them in a tuple. A one-sided edit names its own drift site.

    ROUND-1 FINDING R1-9's enforcing test. The set stopped at eleven, so
    REGISTERED was reachable while the capabilities digest, the model, the
    golden capture, the probe prompt, the isolation assent, the jpack build
    attestation and the sealed reviewer set were all null. Seven members are
    added, and this list is what makes a silent re-shrinking impossible."""
    assert [name for name, _path in integrity.FREEZE_PINS] == [
        "preregistration", "policyProse", "goldSuite",
        "matrixA", "matrixB", "matrixC",
        "mutantManifests", "referenceA", "referenceB",
        "offGoldCertificate", "studyManifest",
        "opaCapabilities", "jpackBuildAttestation", "model",
        "probePrompt", "goldenContext", "isolationAssent",
        "reviewerMutantSet"]


def test_every_freeze_pin_names_the_artifact_it_is_filled_from(pins):
    """ROUND-7 FINDING R7-8. `reviewerMutantSet.sha256` has been a mandatory
    freeze pin since round 1, and the exhaustive freeze-fill procedure filled
    the other seventeen and then claimed `REGISTERED` — because nothing in the
    tree said what this pin's value is or where it comes from. A null pin was
    reported by name; what was missing is the rest of the sentence.

    The two tables must have exactly the same members, so a pin added without a
    source, or a source orphaned by a deleted pin, fails here. And the sealed
    set's source is asserted by name, because that is the one the ceremony could
    complete without."""
    assert sorted(integrity.PIN_SOURCES) == sorted(
        name for name, _path in integrity.FREEZE_PINS), (
        "every freeze pin names the artifact its value is computed from")
    for name, source in sorted(integrity.PIN_SOURCES.items()):
        assert isinstance(source, str) and source.strip(), name
    assert "controls/reviewer-mutants/MANIFEST.json" in \
        integrity.PIN_SOURCES["reviewerMutantSet"], (
        "the reviewer-set pin must name the manifest its digest is taken over")
    unfilled = dict(integrity.unfilled_pin_sources(pins))
    assert set(unfilled) == set(integrity.unfilled_pins(pins))
    if "reviewerMutantSet" in unfilled:
        assert "controls/reviewer-mutants/MANIFEST.json" in \
            unfilled["reviewerMutantSet"]


def test_every_pin_r1_9_added_is_reachable_from_the_committed_registry(pins):
    """Each new pin's PATH resolves in the committed registry and is null there.

    A freeze pin whose path does not exist would read as null forever and could
    never be filled — a member that makes REGISTERED unreachable is as wrong as
    one that makes it too easy."""
    added = ("opaCapabilities", "jpackBuildAttestation", "model",
             "probePrompt", "goldenContext", "isolationAssent",
             "reviewerMutantSet")
    paths = dict(integrity.FREEZE_PINS)
    for name in added:
        node = pins
        for key in paths[name][:-1]:
            assert isinstance(node, dict) and key in node, (name, key)
            node = node[key]
        assert paths[name][-1] in node, name
        assert node[paths[name][-1]] is None, name


def test_the_two_ceremony_pins_are_freeze_pins_and_are_named_as_exempt():
    """The golden capture and the isolation control WRITE two of the freeze
    pins, so the driver's pre-ceremony gate cannot demand them — and nothing
    else may exempt them.

    Both halves are asserted: they are in the freeze set (so no REGISTERED
    attempt is reachable while either is null) and they are exactly the exempt
    tuple (so the exemption cannot quietly widen)."""
    names = [name for name, _path in integrity.FREEZE_PINS]
    assert set(integrity.CEREMONY_LIFECYCLE_PINS) <= set(names)
    assert integrity.CEREMONY_LIFECYCLE_PINS == ("goldenContext",
                                                 "isolationAssent")


def test_the_ceremony_exemption_removes_those_two_and_nothing_else(pins):
    filled = _fill(pins)
    for path in (("golden", "sha256"), ("isolationNegative", "assent")):
        node = filled
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = None
    assert integrity.study_label(filled) == "PILOT"
    assert integrity.unfilled_pins(filled) == ["goldenContext",
                                               "isolationAssent"]
    assert integrity.ceremony_unfilled_pins(filled) == []
    # One more null, and the exemption does not cover it.
    filled["studyManifest"]["sha256"] = None
    assert integrity.ceremony_unfilled_pins(filled) == ["studyManifest"]


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
