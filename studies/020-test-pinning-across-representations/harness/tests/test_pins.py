"""The registered label rule: any null pin the rule reads makes the run a PILOT.

Study 014's round 3 found a REGISTERED run reachable with only the
preregistration digest filled, which left the registry the attempt adjudicated
unpinned. The rule this study registers is over the WHOLE set, and it is
decided in exactly one function. These tests drive that function over the
committed registry and over mutated copies of it — one null at a time — so
"every pin" is asserted pin by pin rather than as a sentence.

**REBUILT FOR 020 (§7 delta 6, ruling M-25), and the rebuild is the point.**
The rule now reads TWO tuples. `FREEZE_PINS` is the freeze ceremony's, one
member shorter than 019's because `codex.model` left it; `DESIGN_TIME_PINS` is
new and holds `codex.model` and `codex.reasoningEffort`, both of which the
pre-pilot sweep resolves BEFORE the freeze. A null in either tuple is a PILOT,
so the move is not a relaxation — and the one registered exemption, the
`--sweep` label over `codex.reasoningEffort` alone, is driven here in both
directions: it must cover that pin under that label, and nothing else under
any label.
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
    registered = [name for name, _path
                  in integrity.FREEZE_PINS + integrity.DESIGN_TIME_PINS]
    assert [n for n in registered if n in unfilled] == unfilled
    if unfilled:
        assert integrity.study_label(pins) == "PILOT"
    else:
        assert integrity.study_label(pins) == "REGISTERED"


ALL_PINS = integrity.FREEZE_PINS + integrity.DESIGN_TIME_PINS


def _fill(pins):
    """The committed registry with every pin the label rule reads filled with a
    plausible digest — the only state in which REGISTERED is reachable."""
    filled = copy.deepcopy(pins)
    for _name, path in ALL_PINS:
        node = filled
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = "sha256:" + "0" * 64
    return filled


def test_a_fully_filled_registry_labels_registered(pins):
    assert integrity.study_label(_fill(pins)) == "REGISTERED"


def test_every_single_null_pin_is_enough_to_make_it_a_pilot(pins):
    filled = _fill(pins)
    for name, path in ALL_PINS:
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
        "opaCapabilities", "jpackBuildAttestation",
        "probePrompt", "goldenContext", "isolationAssent",
        "reviewerMutantSet", "censusStimulusCount"]
    # M-25: the two that left the freeze set are HERE, not gone. A pin deleted
    # from one tuple and added to neither is exactly the re-shrinking R1-9's
    # test exists to prevent, so the second list is asserted as tightly.
    assert [name for name, _path in integrity.DESIGN_TIME_PINS] == [
        "model", "reasoningEffort"]
    assert set(name for name, _ in integrity.FREEZE_PINS) & \
        set(name for name, _ in integrity.DESIGN_TIME_PINS) == set()


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
        name for name, _path in ALL_PINS), (
        "every pin the label rule reads names the artifact it is filled from")
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
             "reviewerMutantSet", "reasoningEffort")
    paths = dict(ALL_PINS)
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
    rule = pins["registeredLabelRule"]
    assert "REGISTERED only when EVERY pin the rule reads is filled" in rule
    assert "labels the run PILOT" in rule
    for name, _path in ALL_PINS:
        assert name in rule, name
    # The registry must state the ONE exemption and state its width, because a
    # reader who cannot see the exemption cannot audit it.
    assert "--sweep" in rule and "ALONE is exempt" in rule
    assert "codex.model is never exempt" in rule


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
    for _name, path in ALL_PINS:
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
        [name for name, _path in ALL_PINS]


@pytest.mark.parametrize("value", STAND_INS)
def test_one_stand_in_pin_is_enough_to_make_it_a_pilot(pins, value):
    """Pin by pin, exactly as the null rule is driven above: a single stand-in
    on an otherwise-full registry is a PILOT, and the label names THAT pin. A
    rule that only caught a registry made entirely of stand-ins would miss the
    case that actually happens — one member a hurried ceremony left behind."""
    for name, path in ALL_PINS:
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


# --------------------------------------------------------------------------
# M-25: the design-time pins, and the one exemption — §7's delta 6
# --------------------------------------------------------------------------


def test_the_sweep_exemption_covers_one_pin_and_one_label(pins):
    """The `--sweep` label exempts `codex.reasoningEffort` and NOTHING else.

    §2.1's problem, stated as it was found: `authoring_call.sh` refuses while
    `codex.model` is null and `registeredLabelRule` names design-time-resolved
    pins as checked whether or not the freeze has happened — so a sweep that
    must run BEFORE the effort value exists is either refused or unenforced.
    The registered answer is a distinct label that exempts ONE value, and the
    exemption is only defensible if it is exactly one value wide.

    Four assertions, and the last two are the ones a widening would trip:
    the exemption is declared as one pin; under the sweep label a registry
    missing only that pin is REGISTERED; under NO label the same registry is a
    PILOT; and `codex.model` null under the sweep label is still a PILOT."""
    assert integrity.SWEEP_EXEMPT_PINS == ("reasoningEffort",)
    filled = _fill(pins)
    filled["codex"]["reasoningEffort"] = None
    assert integrity.study_label(filled, integrity.SWEEP_LABEL) == "REGISTERED"
    assert integrity.unfilled_pins(filled, integrity.SWEEP_LABEL) == []
    assert integrity.study_label(filled) == "PILOT"
    assert integrity.unfilled_pins(filled) == ["reasoningEffort"]
    filled["codex"]["model"] = None
    assert integrity.study_label(filled, integrity.SWEEP_LABEL) == "PILOT"
    assert integrity.unfilled_pins(filled, integrity.SWEEP_LABEL) == ["model"]


def test_the_sweep_exemption_does_not_reach_any_freeze_pin(pins):
    """Pin by pin: no freeze pin becomes fillable by naming the sweep label."""
    for name, path in integrity.FREEZE_PINS:
        one_null = _fill(pins)
        node = one_null
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = None
        assert integrity.study_label(one_null,
                                     integrity.SWEEP_LABEL) == "PILOT", name


def test_an_unregistered_label_context_is_refused_rather_than_ignored(pins):
    """A typo that silently buys an exemption is the failure the argument
    exists to prevent, so an unknown context REFUSES instead of falling back to
    "no exemption" — which would pass every test above while a `--Sweep` in a
    runbook quietly ran under a label nothing implements."""
    with pytest.raises(integrity.IntegrityError):
        integrity.study_label(_fill(pins), "sweep")
    with pytest.raises(integrity.IntegrityError):
        integrity.study_label(_fill(pins), "PRIMARY")


def test_the_two_design_time_pins_are_null_in_the_committed_registry(pins):
    """Pre-sweep, both are null and the registry says why. `codex.model` was
    FILLED in Study 019's registry; carrying 019's value forward would pin a
    compute condition §2.1 registers as an output of a sweep that has not run."""
    assert pins["codex"]["model"] is None
    assert pins["codex"]["reasoningEffort"] is None
    assert "PILOT" in pins["codex"]["note"]
    assert "recorded intention" in pins["codex"]["reasoningEffortNote"]


def test_the_effort_pin_records_the_witness_branch_it_has_not_taken(pins):
    """M-24. The witness-resolution step is registered and has not run, so the
    two members it fills are null and the note carries BOTH branches — the
    gate-5 extension and the self-report fallback. A registration that named
    only the branch it hoped for would be a registration of a hope."""
    assert pins["codex"]["reasoningEffortFlag"] is None
    assert pins["codex"]["reasoningEffortWitness"] is None
    note = pins["codex"]["reasoningEffortNote"]
    assert "transcript gate 5" in note
    assert "self-report" in note
