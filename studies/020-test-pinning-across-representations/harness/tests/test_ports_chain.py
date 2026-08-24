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
