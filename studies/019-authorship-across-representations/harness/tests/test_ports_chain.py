"""The port chain over the WHOLE port table — SCAFFOLD item M1, points 1-3.

`harness/PORTS.md` grew from five rows to seven when the scorer's two ported
modules landed, and three registered things had to move behind it: the registry's
`ownPorts.sha256`, `integrity.REQUIRED_PORTS` and `integrity.TIER1_TWELVE_PATHS`.
Nothing in the suite held any of the three, which is why the chain could refuse
for a week without a test naming the reason.

What is asserted here, and why each one is a separate case:

* the registered destination set is EXACTLY the table's — a row added is as loud
  as a row deleted, which is the only property that makes an exact set worth
  having;
* every row of the committed table verifies two-sided against the authority that
  row actually has — Study 012's own DESTINATION cell for the six tier-1 rows,
  the recorded commit's working file for the one untiered row;
* the two scorer rows are TIER 1 and are bound to 012's registered paths, so
  `harness/e4lib/stats.py` answers to 012's `harness/score_rates.py` and
  `harness/e4lib/census.py` to 012's `harness/census.py`;
* a mutated table refuses in BOTH directions (a row removed, a row added), over
  a copy, so the check has power rather than a passing tree.

The mutation cases rebuild the registry's `ownPorts` pin over the mutated copy,
because otherwise they would pass on the digest gate one link earlier and prove
nothing about the destination set.
"""
import json
import os
import re

import pytest

import integrity

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
PORTS = os.path.join(HARNESS, "PORTS.md")
REGISTRY = os.path.join(HARNESS, "PINS.json")

# The rows the scorer's assembly added, and the paths Study 012's own PORTS.md
# records them under. Named here as data so a mapping edited on one side of the
# port names its own drift site.
SCORER_ROWS = {
    "harness/e4lib/stats.py": "harness/score_rates.py",
    "harness/e4lib/census.py": "harness/census.py",
}


def _rows():
    return integrity.parse_ports(PORTS)


def test_the_registered_destination_set_is_exactly_the_tables():
    assert set(row[2] for row in _rows()) == set(integrity.REQUIRED_PORTS)


def test_the_registered_set_has_seven_rows_and_names_the_scorer_modules():
    assert len(integrity.REQUIRED_PORTS) == 7
    for destination in SCORER_ROWS:
        assert destination in integrity.REQUIRED_PORTS, destination


def test_the_two_scorer_rows_are_tier_one_at_012s_own_paths():
    for destination, twelve_path in SCORER_ROWS.items():
        assert integrity.TIER1_TWELVE_PATHS.get(destination) == twelve_path
        assert destination not in integrity.UNPINNED_SOURCES


def test_every_row_is_bound_to_the_authority_it_has():
    """The whole two-sided verification, over every row including the new ones.

    `verify_chain()` is the function that does it; this case is the one that
    fails when it stops doing it for a row."""
    result = integrity.verify_chain()
    assert len(result["rows"]) == len(integrity.REQUIRED_PORTS)
    assert set(row[2] for row in result["rows"]) == set(integrity.REQUIRED_PORTS)


def test_each_tier_one_source_cell_is_study_012s_own_destination_cell():
    twelve_ports = os.path.join(integrity.TWELVE, "harness", "PORTS.md")
    twelve = {row[2]: row for row in integrity.parse_ports(twelve_ports)}
    for source, source_sha, destination, _destination_sha in _rows():
        if destination not in integrity.TIER1_TWELVE_PATHS:
            continue
        path = integrity.TIER1_TWELVE_PATHS[destination]
        assert source == path, destination
        assert source_sha == twelve[path][3], destination
        assert integrity.digest(os.path.join(integrity.TWELVE, path)) == source_sha


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


# --- ROUND-3 R3-1's neighbour: the design-lineage stamps, and what they are ---
#
# The port table carries a SECOND table under "assembled from this study's own
# design code", and its third column is a different kind of cell from the port
# rows above it: an AS-ASSEMBLED stamp of the prototype the module was carried
# from, not a pin on the prototype's current bytes. Round 3 rebuilt
# `design/mutants/oc_table.py` and `design/mutants/e4_score.py`, so those two
# stamps no longer match the files on disk — correctly, because what they record
# is what was inherited.
#
# That leaves exactly one property worth enforcing, and it is enforced: the
# stamp is written in TWO places, the assembled module's own docstring and the
# table, and the two must agree. A digest edited on one side and not the other
# is a lineage claim nobody can check.

_LINEAGE_SECTION = "| assembled module | design prototype | prototype sha256 |"


def _lineage_rows():
    with open(PORTS, "rb") as handle:
        text = handle.read().decode("utf-8")
    body = text.split(_LINEAGE_SECTION, 1)[1].split("\n\n", 1)[0]
    rows = []
    for line in body.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        # The module cell may carry a parenthetical scope after the path
        # (`harness/e4lib/stats.py` (contrast half only)); the path is the
        # backticked span, which is what the row is about.
        match = re.match(r"`([^`]+)`", cells[0])
        if not match:
            continue
        module = match.group(1)
        # Full 64-hex stamps only. The engines row abbreviates two of its three
        # to `09da06b3…`, and an abbreviation is not a digest to check against.
        rows.append((module, re.findall(r"\b[0-9a-f]{64}\b", cells[2])))
    return rows


def test_the_design_lineage_table_names_modules_that_exist():
    rows = _lineage_rows()
    assert len(rows) >= 5, rows
    for module, _shas in rows:
        assert os.path.isfile(os.path.join(STUDY, module)), module


def test_every_lineage_stamp_is_the_one_the_assembled_module_states():
    """The two-place property. A stamp that appears in the table must appear in
    the module the table names, byte for byte.

    Deliberately NOT asserted: that the stamp equals the design file's current
    digest. It is a record of what was carried, the design tree moves on, and
    re-pinning it on every design edit would make it say nothing."""
    problems = []
    for module, shas in _lineage_rows():
        if not shas:
            continue
        with open(os.path.join(STUDY, module), "rb") as handle:
            source = handle.read().decode("utf-8")
        for sha in shas:
            if sha not in source:
                problems.append("%s does not state the stamp %s the port "
                                "table records for it" % (module, sha[:12]))
    assert problems == [], "\n  ".join([""] + problems)


def test_the_lineage_stamps_are_declared_as_as_assembled_not_as_current():
    """The sentence that makes the exemption above legible rather than a silent
    gap — R1-20's rule, applied to the one column nothing re-digests."""
    with open(PORTS, "rb") as handle:
        flat = " ".join(handle.read().decode("utf-8").split())
    assert "AS-ASSEMBLED stamp, not a currency pin" in flat
    assert "Nothing verifies these digests against the current design tree" in flat


def test_the_run_time_derived_row_carries_no_as_assembled_stamp():
    """`harness/leak_tokens.py` is the one lineage row whose source is read at
    RUN time — it derives `LEAK_TOKENS` from `design/POLICY-DRAFT.md` on every
    call — so an as-assembled stamp is the wrong kind of cell for it and was a
    stale one: the digest it carried had drifted from the prose two revisions
    before this was noticed. The digest of the file actually read is published by
    `report()` and asserted by `tests/test_leak_tokens.py`; this asserts the
    table does not offer a second, unchecked one."""
    rows = dict(_lineage_rows())
    assert "harness/leak_tokens.py" in rows
    assert rows["harness/leak_tokens.py"] == [], (
        "the run-time-derived row must not carry an as-assembled digest")
    for module, shas in _lineage_rows():
        if module != "harness/leak_tokens.py":
            assert shas, "%s states no lineage stamp at all" % module
