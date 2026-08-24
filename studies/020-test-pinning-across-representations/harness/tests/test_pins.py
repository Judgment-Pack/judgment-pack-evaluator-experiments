"""The registered label rule: any null freeze pin makes the run a PILOT.

Study 014's round 3 found a REGISTERED run reachable with only the
preregistration digest filled, which left the registry the attempt adjudicated
unpinned. The rule this study registers is over the WHOLE freeze set, and it is
decided in exactly one function. These tests drive that function over the
committed registry and over mutated copies of it — one null at a time — so
"every pin" is asserted pin by pin rather than as a sentence.
"""
import copy

import pytest

import integrity


def test_the_committed_registry_labels_by_its_own_unfilled_pins(pins):
    """PILOT while any freeze pin is null; the null list is the registered order's
    suffix of what remains.

    The pre-ceremony form of this test asserted ALL pins null. The freeze-fill is
    running (SCAFFOLD §F): the artifact pins are filled from committed artifacts,
    and what remains null is exactly the ceremony's tail — the manifest and
    preregistration digests (F7/F8, filled after CORRECTION-TARGETS.md lands) and
    the three operational pins (G1 capture, G2 assent). The label must stay PILOT
    until the LAST of them fills, and the unfilled list must stay actionable — a
    subset of the registered order, never an invention."""
    unfilled = integrity.unfilled_pins(pins)
    registered = [name for name, _path in integrity.FREEZE_PINS]
    assert [n for n in registered if n in unfilled] == unfilled
    if unfilled:
        assert integrity.study_label(pins) == "PILOT"
    else:
        assert integrity.study_label(pins) == "REGISTERED"


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
        # Pre-ceremony this asserted null; during and after the freeze-fill the
        # member holds its filled value. What must stay true forever is that the
        # PATH resolves — a pin whose path vanished could never be read again —
        # and that a still-null member is one the ceremony has not reached
        # (integrity.unfilled_pins names it), not one it cannot reach.
        if node[paths[name][-1]] is None:
            assert name in integrity.unfilled_pins(pins), name


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
    """§7 DELTA 6: `registeredLabelRule` is restated, and this is the assertion
    that it says what the code does rather than what 019's code did.

    Three things the delta adds to the sentence, each checked here:
    `codex.reasoningEffort`; the null-⇒-PILOT rule stated for the freeze set;
    and §2.1's `--sweep` exemption. The freeze-pin names are checked too, so a
    pin added to `FREEZE_PINS` without a word in the registry fails here."""
    rule = pins["registeredLabelRule"]
    assert "REGISTERED only when EVERY freeze pin below is non-null" in rule
    assert "any null one makes the run a PILOT" in rule
    for name, _path in integrity.FREEZE_PINS:
        assert name in rule, name
    # The delta's three additions.
    assert "codex.reasoningEffort" in rule
    assert "--sweep" in rule
    assert "resolvedAtDesignTime" in rule
    assert "WHETHER OR NOT THE FREEZE HAS HAPPENED" in rule
    # …and the exemption is stated as ONE member, not as a class of them.
    assert "codex.reasoningEffort ALONE" in rule


# --- §7 delta 6, driven PIN BY PIN ------------------------------------------
#
# §2.1: "registeredLabelRule is restated with the new member and its
# null-⇒-PILOT test, moved out of §7's ported-unchanged list, and driven in
# harness/tests/test_pins.py PIN BY PIN." The freeze half is driven above
# (`test_every_single_null_pin_is_enough_to_make_it_a_pilot`); this is the
# design-time half, which is a different rule with a different consequence — a
# null design-time pin does not change the LABEL, it refuses the CALL.

def test_the_design_time_pins_are_exactly_the_registry_members_marked_so(pins):
    """Every member `batch.DESIGN_TIME_PINS` names must live under a block the
    registry marks `resolvedAtDesignTime`, and no design-time pin may also be a
    freeze pin. §2.1 rules `codex.model` and `codex.reasoningEffort` "registered
    as design-time-resolved pins, NOT freeze pins", and a member that is both
    would be governed by two rules with two consequences."""
    import batch
    freeze_paths = {path for _name, path in integrity.FREEZE_PINS}
    for path, why in batch.DESIGN_TIME_PINS:
        assert pins[path[0]].get("resolvedAtDesignTime") is True, path
        assert why, path
    # `codex.model` IS in the freeze set in the ported registry, and §2.1's
    # ruling says it should not be governed by the freeze rule. The two tables
    # are compared here rather than silently overlapping, so the disagreement is
    # a named finding and not a thing a reader has to notice.
    overlap = sorted(".".join(path) for path, _why in batch.DESIGN_TIME_PINS
                     if path in freeze_paths)
    assert overlap == ["codex.model"], overlap


def test_every_single_null_design_time_pin_refuses_the_call(pins):
    """PIN BY PIN, on an otherwise-full registry: each design-time pin, nulled
    alone, must refuse — and must refuse by NAME, so the operator is told which
    value is missing rather than that something is."""
    import batch
    freeze_paths = {path for _name, path in integrity.FREEZE_PINS}
    filled = copy.deepcopy(_fill(pins))
    for path, _why in batch.DESIGN_TIME_PINS:
        node = filled
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = "resolved"
    batch.require_design_time_pins(filled)          # the full registry passes
    for path, _why in batch.DESIGN_TIME_PINS:
        one_null = copy.deepcopy(filled)
        node = one_null
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = None
        with pytest.raises(batch.BatchError) as raised:
            batch.require_design_time_pins(one_null)
        assert ".".join(path) in str(raised.value), path
        # …and the LABEL is untouched by it: a design-time pin is not a freeze
        # pin, so nulling one refuses the call without making the study a PILOT.
        #
        # `codex.model` is the ONE exception and it is a FINDING, not a
        # convention: §2.1 rules it a design-time-resolved pin and NOT a freeze
        # pin, and the ported `integrity.FREEZE_PINS` still carries it — so
        # nulling it changes the label as well as refusing the call. The
        # exception is written here, named, rather than the assertion being
        # weakened for every pin; `test_the_design_time_pins_are_exactly_the_
        # registry_members_marked_so` asserts the overlap is exactly this one
        # member, so a second one cannot appear unnoticed.
        expected = "PILOT" if path in freeze_paths else "REGISTERED"
        assert integrity.study_label(one_null) == expected, path


def test_a_stand_in_design_time_pin_is_not_a_resolution(pins):
    """`integrity.pin_is_filled()` decides FILLED here too, so a registry
    carrying `"TODO(prereg)"` for the effort value is refused exactly as a null
    one is. The salvage audit's finding — eighteen freeze pins set to `""` read
    as REGISTERED — has the same shape on this side of the rule."""
    import batch
    for stand_in in (None, "", "  ", "TODO(prereg)", "tbd", "n/a", 0, [], {}):
        registry = {"codex": {"reasoningEffort": stand_in}}
        assert "codex.reasoningEffort" in batch.design_time_unfilled(registry)


def test_the_sweep_label_exempts_the_effort_pin_and_nothing_else(pins):
    """§2.1, M-25, ruled as drafted: "a distinct `--sweep` label that exempts
    `codex.reasoningEffort` ALONE from the null check".

    The exemption is driven from both sides: the effort pin passes under
    `--sweep` and is refused under every other label, and EVERY OTHER
    design-time pin is refused under `--sweep` too — which is what makes it an
    exemption of one member rather than of the gate."""
    import batch
    assert batch.SWEEP_EXEMPT_PINS == (("codex", "reasoningEffort"),)
    filled = copy.deepcopy(_fill(pins))
    for path, _why in batch.DESIGN_TIME_PINS:
        node = filled
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = "resolved"
    effort_null = copy.deepcopy(filled)
    effort_null["codex"]["reasoningEffort"] = None
    # Exempt under --sweep…
    batch.require_design_time_pins(effort_null, "sweep")
    # …and refused under the pilot label and under the primary batch's.
    for mode in (None, "pilot"):
        with pytest.raises(batch.BatchError) as raised:
            batch.require_design_time_pins(effort_null, mode)
        assert "codex.reasoningEffort" in str(raised.value)
    # Every OTHER design-time pin is still refused under --sweep.
    for path, _why in batch.DESIGN_TIME_PINS:
        if path in batch.SWEEP_EXEMPT_PINS:
            continue
        one_null = copy.deepcopy(filled)
        node = one_null
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = None
        with pytest.raises(batch.BatchError) as raised:
            batch.require_design_time_pins(one_null, "sweep")
        assert ".".join(path) in str(raised.value), path


def test_an_unregistered_calibration_label_is_refused(pins):
    """A mode is one of the two §2.1 and §2a.2 register. A third spelling would
    be a third pin state nobody registered."""
    import batch
    assert batch.CALIBRATION_MODES == ("sweep", "pilot")
    with pytest.raises(batch.BatchError):
        batch.design_time_unfilled(pins, "smoke")


def test_the_effort_pin_exists_and_carries_the_unwitnessed_sentence(pins):
    """M-24, ruled as drafted. The pin exists beside `model` / `version` /
    `binarySha256`, and the registry carries §2.1's own sentence about what it
    can and cannot prove: "A pin nobody can check is a recorded intention, and
    this preregistration says so." The sentence is a REGISTRY member because it
    "travels with every published record of the condition", and a note kept
    only in the preregistration does not travel."""
    assert "reasoningEffort" in pins["codex"]
    note = pins["codex"]["note"]
    assert "SELF-REPORT" in note
    assert "recorded intention" in note
    assert "design-time-resolved pins, NOT freeze pins" in note


def test_the_resolved_toolchain_blocks_are_marked_and_carry_digests(pins):
    """The design-time resolutions are pins already: they are enforced under
    both labels, and they are marked so a reader cannot mistake a resolved
    digest for a freeze pin."""
    for name in ("jpack", "opa", "codex"):
        assert pins[name]["resolvedAtDesignTime"] is True, name
    assert pins["jpack"]["binarySha256"].startswith("sha256:")
    assert pins["opa"]["assetSha256"].startswith("sha256:")
    assert pins["codex"]["binarySha256"].startswith("sha256:")
    # …and the three the ceremony fills are either still null (the ceremony has
    # not reached them) or carry the SHAPE their member registers — never a
    # placeholder that reads as filled. The model is a name, not a digest
    # (Study 012's correction); the capabilities member is a digest; the
    # attestation is a sentence recording a reproduction, and the word
    # "reproduc" is what separates it from a build note.
    model = pins["codex"]["model"]
    assert model is None or (isinstance(model, str) and model and
                             not model.startswith("sha256:"))
    caps = pins["opa"]["capabilitiesSha256"]
    assert caps is None or (caps.startswith("sha256:") and
                            len(caps) == len("sha256:") + 64)
    attestation = pins["jpack"]["reproducibleBuildAttestation"]
    assert attestation is None or "reproduc" in attestation


def test_the_anchor_order_is_linear_and_says_so(pins):
    assert pins["anchorOrder"].startswith("LINEAR")
    assert "covers NEITHER itself NOR this file" in pins["anchorOrder"]


# --------------------------------------------------------------------------
# a stand-in is not a value — salvage audit, defect a
# --------------------------------------------------------------------------
#
# The rule above was `node is not None`, and the audit probed it directly: with
# all EIGHTEEN freeze pins set to `""`, `"TODO(prereg)"`, `0`, `[]`, `{}` or
# `False`, `study_label()` answered REGISTERED and `unfilled_pins()` answered
# `[]`. A registry of eighteen empty strings adjudicated a registered attempt.
# Study 012 registered the neighbouring refusal — no `(port time)` cell may
# remain in `harness/PORTS.md` or `harness/PINS.json`, because an unfinished
# port is not a soft state — but it lived in the ports parser and never reached
# the label rule.
#
# Every case below fills the WHOLE set, so none of them can pass because some
# other pin was null.

STAND_INS = ("", "   ", "\t\n", "TODO", "todo", "  TODO  ", "TODO(prereg)",
             "tbd", "TBD", "FIXME", "fixme(digest)", "xxx", "pending", "n/a",
             "N/A", "na", "none", "None", "null", "NULL", "nil", "-", "?",
             "(port time)", 0, 0.0, False, [], {})


def _fill_with(pins, value):
    filled = copy.deepcopy(pins)
    for _name, path in integrity.FREEZE_PINS:
        node = filled
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = copy.deepcopy(value)
    return filled


@pytest.mark.parametrize("value", STAND_INS)
def test_a_registry_of_stand_ins_is_not_a_registration(pins, value):
    """Eighteen stand-ins are eighteen unfilled pins, and the label says so by
    naming every one of them — not a REGISTERED run over a registry in which
    nothing has been determined."""
    filled = _fill_with(pins, value)
    assert integrity.study_label(filled) == "PILOT"
    assert integrity.unfilled_pins(filled) == \
        [name for name, _path in integrity.FREEZE_PINS]


@pytest.mark.parametrize("value", STAND_INS)
def test_one_stand_in_pin_is_enough_to_make_it_a_pilot(pins, value):
    """Pin by pin, exactly as the null rule is driven above: a single stand-in
    on an otherwise-full registry is a PILOT, and the label names THAT pin. A
    rule that only caught a registry made entirely of stand-ins would miss the
    case that actually happens — one member a hurried ceremony left behind."""
    for name, path in integrity.FREEZE_PINS:
        one_stand_in = _fill(pins)
        node = one_stand_in
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = copy.deepcopy(value)
        assert integrity.study_label(one_stand_in) == "PILOT", (name, value)
        assert integrity.unfilled_pins(one_stand_in) == [name], (name, value)


@pytest.mark.parametrize("value", [
    "sha256:" + "0" * 64,
    "granted",                       # isolationNegative.assent's real value
    "gpt-5-codex",                   # a plausible codex.model
    True,                            # a build attestation recorded as a flag
    "0" * 64,
    "todos",                         # a stand-in PREFIX is not a stand-in
    "no-tbd-here",
    ["sha256:" + "0" * 64],
])
def test_a_real_value_is_still_filled(pins, value):
    """The control, and it is the half that decides whether the rule is usable.
    A refusal that also rejected real values would make REGISTERED unreachable
    and would look, from the label alone, exactly like the pre-freeze state. The
    substring cases are here because a rule matching `"todo" in value` would
    reject `"todos"` and `"no-tbd-here"`; this one matches the STRIPPED, folded
    WHOLE value, plus the `TODO(`-style prefixes whose parenthetical varies."""
    assert integrity.study_label(_fill_with(pins, value)) == "REGISTERED"
    assert integrity.unfilled_pins(_fill_with(pins, value)) == []


def test_the_rule_decides_filled_and_not_correct(pins):
    """Stated as a test so nobody reads more into the label than it carries: a
    pin filled with a real-shaped digest of the wrong bytes is FILLED. Whether
    the digest matches the file is `verify()`'s business, it is checked under
    both labels, and this function is not a second, weaker copy of it."""
    assert integrity.pin_is_filled("sha256:" + "f" * 64) is True
    assert integrity.pin_is_filled("not-a-digest-at-all") is True



def test_every_placeholder_prefix_is_alive_in_a_case():
    """The independent mutation audit (A1) removed `"tbd("` from
    `PIN_PLACEHOLDER_PREFIXES` and the suite stayed green: the prefix was dead
    code, so a registry filled with `tbd(2026-08-19)` would have labelled
    REGISTERED the day someone typed it. One case per prefix, both cases the
    audit demonstrated."""
    assert integrity.pin_is_filled("tbd(2026-08-19)") is False
    assert integrity.pin_is_filled("TBD(after the freeze)") is False
    assert integrity.pin_is_filled("todo(prereg)") is False
    assert integrity.pin_is_filled("fixme(digest)") is False
