"""The port chain over the WHOLE port table, and over the ported artifacts.

WHAT THIS FILE DOES
-------------------
Drives `harness/integrity.py`'s two-sided binding for Study 020's port of Study
019: the source study's LOCK is verified first, every row of `harness/PORTS.md`
is bound to 019's line for the same path on both sides, and every registered
artifact §4.1 ports by digest is bound to that same lock (or, for the three arm
prompts, to 019's registry). Every refusal the port re-points introduces has a
case here, and each case is mutation-checked in the program's standing
discipline — the mutation is applied to a COPY, the named case is watched to
fail, and the tree on disk is untouched.

Study 019's version of this file asserted a seven-row table bound to Study 012's
`PORTS.md` destination cells. Neither of those authorities exists for this port:
020 takes 019's whole harness, and 019 publishes a digest for every byte of it in
one frozen lock. What is asserted is therefore the same PROPERTY over a different
authority — a row added is as loud as a row deleted, and no cell is a
transcription nobody checks.

DELIBERATELY DOES NOT DO
------------------------
It does not assert anything about `design/`. 019's manifest covers no path under
`design/`, so the carried design tree is bound to the recorded port commit and to
nothing older; `harness/PORTS.md` says so in prose and this file does not pretend
to a digest that does not exist. It also does not re-check 019's own internal
consistency: that 019's lock describes 019's tree is 019's freeze, not this
study's claim.
"""
import json
import os
import shutil

import pytest

import integrity

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
PORTS = os.path.join(HARNESS, "PORTS.md")
REGISTRY = os.path.join(HARNESS, "PINS.json")


def _rows():
    return integrity.parse_ports(PORTS)


# --- the registered set ----------------------------------------------------


def test_the_registered_destination_set_is_exactly_the_tables():
    assert set(row[2] for row in _rows()) == set(integrity.REQUIRED_PORTS)


def _harness_files_on_disk():
    present = set()
    for name in sorted(os.listdir(HARNESS)):
        if name.endswith((".py", ".sh")):
            present.add("harness/" + name)
    for name in sorted(os.listdir(os.path.join(HARNESS, "e4lib"))):
        if name.endswith(".py"):
            present.add("harness/e4lib/" + name)
    for name in sorted(os.listdir(HERE)):
        if name.endswith(".py"):
            present.add("harness/tests/" + name)
    return present


def test_the_registered_set_is_every_harness_file_on_disk():
    """The exact-set property, stated against the DIRECTORY rather than against
    a count. A count is a number somebody has to keep in step; this fails when a
    harness file is added and not registered, which is the mistake.

    The registered set is in TWO halves because §7's deltas 3 and 5 register new
    machinery, and new machinery has no source-side file to be ported by digest
    from. Asserting the UNION is what keeps the original failure loud: a harness
    file in neither half is still a harness file nobody registered."""
    assert _harness_files_on_disk() == set(integrity.REGISTERED_HARNESS_FILES)


def test_the_two_halves_of_the_registered_set_are_disjoint():
    """A path that is both ported by digest and new in 020 would be governed by
    two rules with two consequences, so it is refused rather than resolved."""
    assert not (set(integrity.REQUIRED_PORTS) & set(integrity.NEW_IN_020))
    assert set(integrity.REGISTERED_HARNESS_FILES) == \
        set(integrity.REQUIRED_PORTS) | set(integrity.NEW_IN_020)


def test_new_in_020_is_new_in_the_source_studys_own_lock():
    """What makes NEW_IN_020 membership CHECKABLE rather than declared: for each
    member, Study 019's frozen lock carries no entry. A file the source study
    has is a file this port owes a `PORTS.md` row for; being listed here does
    not make it new, 019's lock does."""
    lock = integrity.source_lock()["entries"]
    for relative in sorted(integrity.NEW_IN_020):
        assert relative not in lock, relative
        assert os.path.isfile(os.path.join(STUDY, relative)), relative


def test_the_source_study_is_019_and_the_lineage_names_it():
    assert integrity.NINETEEN.endswith("019-authorship-across-representations")
    assert os.path.isdir(integrity.NINETEEN)
    assert not hasattr(integrity, "TIER1_TWELVE_PATHS"), (
        "the 012-era tier table is not this port's authority and must not "
        "survive as a second, unread one")


# --- the source study's lock, verified first --------------------------------


def test_the_source_lock_is_at_the_digest_019s_own_registry_pins():
    source = integrity.source_lock()
    pins_path = os.path.join(integrity.NINETEEN, "harness", "PINS.json")
    assert integrity.digest(pins_path) == integrity.NINETEEN_PINS_SHA256
    recorded = json.loads(open(pins_path, encoding="utf-8").read())
    assert integrity.bare(recorded["studyManifest"]["sha256"]) \
        == source["lockSha256"]
    lock_path = os.path.join(integrity.NINETEEN, integrity.NINETEEN_LOCK_PATH)
    assert integrity.digest(lock_path) == source["lockSha256"]


def test_a_lock_line_that_is_not_a_digest_and_a_path_refuses(tmp_path):
    lock = tmp_path / "LOCK"
    lock.write_text("not a lock line at all\n", encoding="utf-8")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.parse_lock(str(lock))
    assert "sha256  path" in str(caught.value)


def test_a_lock_that_names_one_path_twice_refuses(tmp_path):
    lock = tmp_path / "LOCK"
    lock.write_text("%s  a.py\n%s  a.py\n" % ("0" * 64, "1" * 64),
                    encoding="utf-8")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.parse_lock(str(lock))
    assert "twice" in str(caught.value)


def test_an_empty_lock_refuses(tmp_path):
    lock = tmp_path / "LOCK"
    lock.write_text("\n\n", encoding="utf-8")
    with pytest.raises(integrity.IntegrityError):
        integrity.parse_lock(str(lock))


# --- every row, two-sided ---------------------------------------------------


def test_every_row_is_bound_to_the_authority_it_has():
    """The whole two-sided verification, over every row.

    `verify_chain()` is the function that does it; this case is the one that
    fails when it stops doing it for a row."""
    result = integrity.verify_chain()
    assert len(result["rows"]) == len(integrity.REQUIRED_PORTS)
    assert set(row[2] for row in result["rows"]) == set(integrity.REQUIRED_PORTS)


def test_each_source_cell_is_019s_own_lock_line_for_that_path():
    entries = integrity.source_lock()["entries"]
    for source, source_sha, destination, _destination_sha in _rows():
        assert source == destination, destination
        assert entries.get(source) == source_sha, destination
        assert integrity.digest(os.path.join(integrity.NINETEEN, source)) \
            == source_sha, destination


def _mutated(tmp_path, text):
    """A ports table and a registry that pins it, so the mutation is tested at
    the destination-set check and not at the digest gate one link earlier."""
    ports = tmp_path / "PORTS.md"
    ports.write_text(text, encoding="utf-8")
    with open(REGISTRY, "rb") as handle:
        pins = json.loads(handle.read().decode("utf-8"))
    pins["ownPorts"]["sha256"] = "sha256:" + integrity.digest(str(ports))
    registry = tmp_path / "PINS.json"
    registry.write_text(json.dumps(pins, indent=2), encoding="utf-8")
    return str(ports), str(registry)


def test_a_new_in_020_file_the_source_study_actually_has_refuses(monkeypatch):
    """The refusal that makes the second half of the set honest. Naming a
    PORTED file "new in 020" would be the way to drop its two-sided digest check
    while looking registered — so the claim is checked against 019's lock, and a
    path 019's lock names cannot be new."""
    monkeypatch.setattr(integrity, "NEW_IN_020",
                        frozenset(["harness/e4lib/census.py"]))
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain()
    assert "harness/e4lib/census.py" in str(caught.value)
    assert "019's lock names it" in str(caught.value)


def test_a_new_in_020_file_that_is_not_on_disk_refuses(monkeypatch):
    monkeypatch.setattr(integrity, "NEW_IN_020",
                        frozenset(["harness/e4lib/never_written.py"]))
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain()
    assert "harness/e4lib/never_written.py" in str(caught.value)
    assert "not on disk" in str(caught.value)


def test_a_path_in_both_halves_of_the_registered_set_refuses(monkeypatch):
    monkeypatch.setattr(integrity, "NEW_IN_020",
                        frozenset(["harness/score.py"]))
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain()
    assert "harness/score.py" in str(caught.value)
    assert "one or the other" in str(caught.value)


def test_a_row_removed_from_the_table_refuses(tmp_path):
    with open(PORTS, "rb") as handle:
        text = handle.read().decode("utf-8")
    kept = [line for line in text.splitlines()
            if not (integrity.ROW.match(line.strip())
                    and integrity.ROW.match(line.strip()).group(3)
                    == "harness/e4lib/census.py")]
    ports, registry = _mutated(tmp_path, "\n".join(kept) + "\n")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain(ports_path=ports, pins_path=registry)
    assert "harness/e4lib/census.py" in str(caught.value)


def test_a_row_added_to_the_table_refuses(tmp_path):
    with open(PORTS, "rb") as handle:
        text = handle.read().decode("utf-8")
    extra = ("| `harness/unregistered.py` | `%s` | `harness/unregistered.py` "
             "| `%s` | invented |" % ("0" * 64, "1" * 64))
    ports, registry = _mutated(tmp_path, text + "\n" + extra + "\n")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain(ports_path=ports, pins_path=registry)
    assert "harness/unregistered.py" in str(caught.value)


def test_a_row_whose_source_digest_is_not_019s_lock_line_refuses(tmp_path):
    """The one that matters: the destination bytes are right, the table's
    SOURCE cell is not the lock's. A port that lets this pass is a port whose
    source side is a transcription."""
    with open(PORTS, "rb") as handle:
        text = handle.read().decode("utf-8")
    entries = integrity.source_lock()["entries"]
    original = entries["harness/score.py"]
    forged = ("0" * 64) if original != "0" * 64 else "1" * 64
    ports, registry = _mutated(tmp_path, text.replace(original, forged, 1))
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain(ports_path=ports, pins_path=registry)
    assert "019's own lock records" in str(caught.value)


def test_a_row_that_renames_the_file_refuses(tmp_path):
    """This port is whole-file and by digest, so source path == destination
    path. A row that claims otherwise is claiming an authority it does not
    have."""
    with open(PORTS, "rb") as handle:
        text = handle.read().decode("utf-8")
    ports, registry = _mutated(
        tmp_path,
        text.replace("| `harness/score.py` |", "| `harness/scorer.py` |", 1))
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain(ports_path=ports, pins_path=registry)
    assert "whole-file and by digest" in str(caught.value)


# --- the ported artifacts ---------------------------------------------------


def test_every_registered_artifact_is_bound_to_019s_lock():
    result = integrity.verify_ported_artifacts()
    for relative in integrity.PORTED_ARTIFACTS:
        assert relative in result["portedArtifacts"], relative
    for arm in integrity.ARMS:
        assert integrity.PROMPT_PATHS[arm] in result["portedArtifacts"], arm


def test_the_artifact_set_carries_no_path_019s_lock_does_not_cover():
    entries = integrity.source_lock()["entries"]
    for relative in integrity.PORTED_ARTIFACTS:
        assert relative in entries, relative


def test_the_arm_prompts_answer_to_019s_registry_and_not_to_its_lock():
    """The one artifact class 019's manifest does NOT cover. Binding it to the
    lock would silently bind it to nothing, so it is bound to the registry
    member the call wrapper's own prompt-digest gate reads."""
    entries = integrity.source_lock()["entries"]
    pins = integrity.source_lock()["pins"]
    for arm in integrity.ARMS:
        relative = integrity.PROMPT_PATHS[arm]
        assert relative not in entries, relative
        pinned = integrity.bare(pins["arms"][arm]["promptSha256"])
        assert integrity.digest(os.path.join(STUDY, relative)) == pinned


def _study_copy(tmp_path):
    """A copy of the study's artifact tree, so a mutation is tested against a
    real verification and the tree on disk is never touched."""
    root = tmp_path / "study"
    root.mkdir()
    for relative in ("policy", "gold", "mutants", "reference", "controls",
                     "verification", "arms"):
        source = os.path.join(STUDY, relative)
        if os.path.isdir(source):
            shutil.copytree(source, str(root / relative))
    return str(root)


def test_an_edited_artifact_refuses(tmp_path):
    root = _study_copy(tmp_path)
    with open(os.path.join(root, "gold", "GOLD.json"), "ab") as handle:
        handle.write(b"\n")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_ported_artifacts(study=root)
    assert "gold/GOLD.json" in str(caught.value)


def test_a_missing_mutant_payload_refuses(tmp_path):
    root = _study_copy(tmp_path)
    victim = sorted(name for name in os.listdir(os.path.join(root, "mutants", "jps"))
                    if name.endswith(".json"))[0]
    os.remove(os.path.join(root, "mutants", "jps", victim))
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_ported_artifacts(study=root)
    assert "mutants/jps" in str(caught.value)


def test_a_mutant_payload_019_never_had_refuses(tmp_path):
    root = _study_copy(tmp_path)
    with open(os.path.join(root, "mutants", "jps", "m-a-999999.json"), "w",
              encoding="utf-8") as handle:
        handle.write("{}\n")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_ported_artifacts(study=root)
    assert "unexpected" in str(caught.value)


def test_an_edited_arm_prompt_refuses(tmp_path):
    root = _study_copy(tmp_path)
    with open(os.path.join(root, "arms", "B", "PROMPT.txt"), "ab") as handle:
        handle.write(b" ")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_ported_artifacts(study=root)
    assert "arms/B/PROMPT.txt" in str(caught.value)


# --- the SECOND source-side authority, and the lineage behind 019 -----------
#
# Spliced from the sweep line's own suite: the apparatus line moved every row to
# 019's lock, and the seven rows 019 ITSELF ported still have a second authority
# — 019's own `PORTS.md` destination cell — which `verify_chain()` requires to
# AGREE with the lock line. Neither branch's rule is dropped for the other's.


def test_the_stronger_tier_agrees_with_019s_own_ports_cell():
    """Authority 2, for the seven rows that have one. The point of the tier is
    that the two authorities must AGREE — a row where 019's ports cell and 019's
    lock disagree is refused rather than resolved in either direction."""
    source_ports = os.path.join(integrity.NINETEEN, "harness", "PORTS.md")
    published = {row[2]: row for row in integrity.parse_ports(source_ports)}
    lock = integrity.source_lock()["entries"]
    assert len(integrity.TIER_PORTS_PATHS) == 7
    for source, source_sha, destination, _dest in _rows():
        if destination not in integrity.TIER_PORTS_PATHS:
            continue
        path = integrity.TIER_PORTS_PATHS[destination]
        assert source == path, destination
        assert source_sha == published[path][3], destination
        assert source_sha == lock[path], destination


def test_the_recorded_lineage_is_study_019s_own(pins):
    """The history before 019 is RECORDED, not walked — and what is checked is
    that it is 019's history rather than a summary this study wrote."""
    history = pins["pinnedFrom"]["history"]
    assert sorted(history) == sorted(integrity.HISTORY_STUDIES)
    source = integrity.load_json(
        os.path.join(integrity.NINETEEN, "harness", "PINS.json"))
    assert integrity.bare(
        history["studies/012-policy-perturbation"]["pins"]["sha256"]) == \
        integrity.bare(source["pinnedFrom"]["pins"]["sha256"])
    assert history["studies/014-openworkproof-binding"]["file"] == \
        source["pinnedFrom"]["alsoTakenFrom"]["file"]


def test_a_falsified_history_refuses(tmp_path):
    with open(REGISTRY, "rb") as handle:
        pins = json.loads(handle.read().decode("utf-8"))
    pins["pinnedFrom"]["history"]["studies/012-policy-perturbation"]["pins"][
        "sha256"] = "sha256:" + "0" * 64
    registry = tmp_path / "PINS.json"
    registry.write_text(json.dumps(pins, indent=2), encoding="utf-8")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain(pins_path=str(registry))
    assert "Study 012 registry digest" in str(caught.value)


def test_a_second_row_for_one_destination_refuses(tmp_path):
    """Study 019 stated this in prose — "a second row naming `harness/batch.py`
    as its destination refuses, whatever it names as its source" — and checked
    it nowhere: the destination SET comparison passes over a duplicate, and the
    row loop would then verify the same file twice against two different source
    cells and accept whichever came second."""
    with open(PORTS, "rb") as handle:
        text = handle.read().decode("utf-8")
    extra = ("| `harness/e4lib/e4.py` | `%s` | `harness/batch.py` | `%s` "
             "| a second claim on one destination |" % ("0" * 64, "1" * 64))
    ports, registry = _mutated(tmp_path, text + "\n" + extra + "\n")
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain(ports_path=ports, pins_path=registry)
    assert "rows for" in str(caught.value)


def test_the_table_declares_that_nothing_was_assembled_from_a_prototype():
    """Study 019 carried five modules assembled from its own design prototypes
    and a second table of as-assembled stamps. 020 has no design prototypes of
    its own — it carries 019's `design/` tree unpinned and wrote no code from it
    — and the empty section says so rather than being omitted, because a missing
    section reads as an oversight and an empty one reads as a fact."""
    with open(PORTS, "rb") as handle:
        flat = " ".join(handle.read().decode("utf-8").split())
    assert "## Assembled from this study's own work" in flat
    assert "Nothing yet, and the empty section is deliberate" in flat
    assert "| assembled module | design prototype |" not in flat


# --- two cases the merge added, because the ones inherited could not
#     discriminate the safeguards they are named for -------------------------


def test_the_new_in_020_lock_check_is_reached_and_not_masked(monkeypatch):
    """`test_a_new_in_020_file_the_source_study_actually_has_refuses` above
    CANNOT DISCRIMINATE the check it names, and that is why this case exists.

    It sets `NEW_IN_020` to `harness/e4lib/census.py`, which is also in
    `REQUIRED_PORTS` — so the DISJOINTNESS refusal fires one branch earlier, and
    its message happens to contain the same words ("019's lock names it"). With
    the lock check deleted the test still passes. Measured: `if relative in
    lock_entries:` replaced by `if False and …` leaves the whole file green.

    `harness/PORTS.md` is the witness that reaches the branch: 019's lock names
    it, this study has it, and it is NOT a port row — so the overlap check
    cannot fire and only the lock check can."""
    monkeypatch.setattr(integrity, "NEW_IN_020", frozenset(["harness/PORTS.md"]))
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain()
    assert "harness/PORTS.md" in str(caught.value)
    assert "019's lock names it" in str(caught.value)
    assert "one or the other" not in str(caught.value), (
        "the disjointness branch fired instead of the lock branch; this case "
        "is meant to reach the lock check and nothing else")


def test_a_tier_ports_row_with_no_019_ports_cell_refuses(monkeypatch):
    """The SECOND source-side authority, driven through `verify_chain()`.

    `test_the_stronger_tier_agrees_with_019s_own_ports_cell` reads the two
    tables and compares them; it never calls `verify_chain()`, so deleting the
    tier branch from the chain leaves it green — measured, by replacing `if
    destination in TIER_PORTS_PATHS:` with `if False and …`. This case puts a
    destination 019 published NO ports row for into the stronger tier, which
    only the branch inside `verify_chain()` can refuse."""
    widened = dict(integrity.TIER_PORTS_PATHS)
    widened["harness/score.py"] = "harness/score.py"
    monkeypatch.setattr(integrity, "TIER_PORTS_PATHS", widened)
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_chain()
    assert "carries no provenance row for harness/score.py" in str(caught.value)
