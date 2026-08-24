"""The port chain over the WHOLE port table.

Study 019's version of this module existed because its table grew from five
rows to seven and three registered things had to move behind it — the
registry's `ownPorts.sha256`, `integrity.REQUIRED_PORTS` and the tier map —
and nothing in the suite held any of the three, so the chain could refuse for a
week without a test naming the reason. **REBUILT FOR 020**, because the table's
SHAPE changed: twenty rows rather than seven, two source-side tiers rather than
a tier and a commit, and no design-lineage table at all.

What is asserted here, and why each one is a separate case:

* the registered destination set is EXACTLY the table's — a row added is as loud
  as a row deleted, which is the only property that makes an exact set worth
  having — and the COUNT is read out of the constant rather than out of a
  reader's memory, which is Study 019's round-1 finding R1-20 applied to its own
  successor;
* every row verifies two-sided against the authority that row actually has:
  Study 019's exact-set manifest for all twenty, PLUS 019's own PORTS.md
  destination cell for the seven that have one, with the two required to AGREE;
* the new module is deliberately NOT in the set, because it was not inherited;
* a mutated table refuses in BOTH directions (a row removed, a row added, and a
  duplicate destination), over a copy, so the check has power rather than a
  passing tree;
* Study 019's lineage is recorded as HISTORY and the recorded history is 019's
  own, not a summary this study wrote for itself.

The mutation cases rebuild the registry's `ownPorts` pin over the mutated copy,
because otherwise they would pass on the digest gate one link earlier and prove
nothing about the destination set.
"""
import json
import os

import pytest

import integrity

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
PORTS = os.path.join(HARNESS, "PORTS.md")
REGISTRY = os.path.join(HARNESS, "PINS.json")
SOURCE_MANIFEST = os.path.join(integrity.NINETEEN, "harness",
                               "STUDY-MANIFEST.sha256")


def _rows():
    return integrity.parse_ports(PORTS)


def test_the_registered_destination_set_is_exactly_the_tables():
    assert set(row[2] for row in _rows()) == set(integrity.REQUIRED_PORTS)


def test_the_registered_set_is_the_whole_executable_surface():
    """The count is DERIVED from the two tier maps, never written here: a row
    added to one map and to no table is the drift R1-20 found, and a number in
    this file would be a third place to keep in step."""
    tiers = set(integrity.TIER_PORTS_PATHS) | set(integrity.TIER_MANIFEST_PATHS)
    assert tiers == set(integrity.REQUIRED_PORTS)
    assert len(integrity.REQUIRED_PORTS) == len(tiers)
    assert set(integrity.TIER_PORTS_PATHS) & \
        set(integrity.TIER_MANIFEST_PATHS) == set(), (
        "a destination in both tiers would be bound by whichever branch ran")
    # Every module the scorer, the driver and the wrapper execute.
    for name in ("harness/score.py", "harness/batch.py",
                 "harness/authoring_call.sh", "harness/integrity.py",
                 "harness/make_manifest.py", "harness/render_round_status.py",
                 "harness/e4lib/e4.py", "harness/e4lib/admit.py"):
        assert name in integrity.REQUIRED_PORTS, name


def test_the_new_module_is_not_in_the_port_set():
    """`harness/e4lib/presence_idiom.py` is new in 020 (§3.2). A row for it
    would claim an inheritance that does not exist, and its ABSENCE from the
    exact set is the loudest available way to say it was not inherited. It is
    still covered by the exact-set manifest like every other harness source."""
    assert "harness/e4lib/presence_idiom.py" not in integrity.REQUIRED_PORTS
    assert os.path.isfile(os.path.join(HARNESS, "e4lib", "presence_idiom.py"))
    import make_manifest
    assert "harness/e4lib/presence_idiom.py" in make_manifest.manifest_entries()


def test_every_row_is_bound_to_the_authority_it_has():
    """The whole two-sided verification, over every row.

    `verify_chain()` is the function that does it; this case is the one that
    fails when it stops doing it for a row."""
    result = integrity.verify_chain()
    assert len(result["rows"]) == len(integrity.REQUIRED_PORTS)
    assert set(row[2] for row in result["rows"]) == set(integrity.REQUIRED_PORTS)


def _source_manifest():
    entries = {}
    with open(SOURCE_MANIFEST, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                digest, name = line.rstrip("\n").split("  ", 1)
                entries[name] = digest
    return entries


def test_every_source_cell_is_study_019s_own_manifest_entry():
    """Authority 1, for all twenty rows. The manifest is pinned by 019's own
    registry, so the source cell answers to the SOURCE study and not to a
    digest this study chose."""
    manifest = _source_manifest()
    for source, source_sha, destination, _dest in _rows():
        assert manifest.get(source) == source_sha, destination
        assert integrity.digest(
            os.path.join(integrity.NINETEEN, source)) == source_sha, destination


def test_the_stronger_tier_agrees_with_019s_own_ports_cell():
    """Authority 2, for the seven rows that have one. The point of the tier is
    that the two authorities must AGREE — a row where 019's ports cell and 019's
    manifest disagree is refused rather than resolved in either direction."""
    source_ports = os.path.join(integrity.NINETEEN, "harness", "PORTS.md")
    published = {row[2]: row for row in integrity.parse_ports(source_ports)}
    manifest = _source_manifest()
    assert len(integrity.TIER_PORTS_PATHS) == 7
    for source, source_sha, destination, _dest in _rows():
        if destination not in integrity.TIER_PORTS_PATHS:
            continue
        path = integrity.TIER_PORTS_PATHS[destination]
        assert source == path, destination
        assert source_sha == published[path][3], destination
        assert source_sha == manifest[path], destination


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
    and a second table of as-assembled stamps. 020 has no design prototypes —
    its design phase produced prose that governs the registration and no code —
    and the empty section says so rather than being omitted, because a missing
    section reads as an oversight and an empty one reads as a fact."""
    with open(PORTS, "rb") as handle:
        flat = " ".join(handle.read().decode("utf-8").split())
    assert "## Assembled from this study's own work" in flat
    assert "Nothing yet, and the empty section is deliberate" in flat
    assert "| assembled module | design prototype |" not in flat
