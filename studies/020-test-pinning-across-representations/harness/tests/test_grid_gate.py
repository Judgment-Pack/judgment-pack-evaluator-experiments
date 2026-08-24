"""ROUND-8 FINDING R8-8: the registered freeze-time grid assertion, exercised.

`harness/grid_gate.py` implements two sentences that were registered and never
run — `design/BRIEF.md` §2.3's full-grid `project -> re-serialize -> byte-equal`
round trip with a nonzero exit, and `design/POLICY-DRAFT.md`'s "the canonical
grid carries no malformed or out-of-range values, asserted at freeze".

A gate is worth what its refusals are worth, so every assertion here is run in
BOTH directions: over the real authored grid, which must hold, and over a seeded
copy of it, which must fail and must name the seed. The seeds are the ones the
registration itself names — the `70.10 -> 70.1` scale loss and an out-of-range
value — plus the failure mode the round trip exists for, which is the ordinary
JSON decoder: `json.dumps(json.loads("70.10"))` is `70.1`, one decoder argument
away from the projection at all times.
"""
import json
import os

import pytest

import grid_gate

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))
DESIGN_GRID = os.path.join(STUDY, "design", "gold", "gold.json")


@pytest.fixture(scope="module")
def design_grid():
    if not os.path.isfile(DESIGN_GRID):
        pytest.skip("the authored grid is not in this tree")
    with open(DESIGN_GRID, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _scratch_grid(root, grid):
    where = root / "design" / "gold"
    where.mkdir(parents=True, exist_ok=True)
    (where / "gold.json").write_text(json.dumps(grid), encoding="utf-8")
    return str(root)


# --- the projection, and the defect it exists to catch ----------------------

def test_the_registered_projection_is_byte_preserving_and_the_ordinary_one_is_not():
    """The BRIEF's own sentence, as two assertions: "string->number is total and
    lossless; number->string is where decimal identity dies — `"70.10"` must
    never round-trip to `"70.1"`". The registered projection reads the exact
    bytes as an exact decimal; the ordinary decoder reads them as a binary float,
    and that is the whole failure this assertion is registered against."""
    for literal in ("70.10", "50000.00", "0.00", "2000000.00", "100", "0"):
        assert grid_gate.reserialize(grid_gate.project(literal)) == literal
        assert grid_gate.roundtrip_problem("spend", literal) is None

    assert json.dumps(json.loads("70.10")) == "70.1", (
        "the ordinary decoder is what makes this assertion necessary")
    assert grid_gate.reserialize(grid_gate.project("70.10")) == "70.10"

    # …and the assertion REFUSES in the other direction, on the literals whose
    # decimal identity does not survive the trip. An exponent form is a JSON
    # number and is not a wire form this study registers: `7.010E+3` and `7e1`
    # come back as `7010` and `70`, which are different bytes and therefore a
    # different registered value.
    for literal, written in (("7.010E+3", "7010"), ("7e1", "70"),
                             ("1E+2", "100")):
        problem = grid_gate.roundtrip_problem("spend", literal)
        assert problem and "re-serializes to %r" % written in problem, \
            (literal, problem)


def test_a_non_string_or_unreadable_numeric_cell_is_a_named_refusal():
    assert "decimal STRING" in grid_gate.roundtrip_problem("spend", 70.1)
    assert "decimal STRING" in grid_gate.roundtrip_problem("risk", None)
    assert "not a JSON number" in grid_gate.roundtrip_problem("spend", "seventy")
    assert "over a number" in grid_gate.roundtrip_problem("spend", '"70.10"')


def test_the_registered_fixed_scale_is_asserted_as_a_scale():
    """Risk is scale 0 and spend is scale 2, exactly. `"70.1"` is not `"70.10"`
    rounded, it is a different registered value."""
    assert grid_gate.scale_problem("spend", "70.10") is None
    assert grid_gate.scale_problem("risk", "70") is None
    assert "scale 1" in grid_gate.scale_problem("spend", "70.1")
    assert "scale 2" in grid_gate.scale_problem("risk", "70.00")


# --- the whole grid ---------------------------------------------------------

def test_the_assertion_holds_over_the_authored_grid(design_grid):
    """The positive direction, over the bytes that will be frozen. 117 rows of
    canonical decimal strings, every one of them in the registered domain and
    every numeric literal surviving the round trip."""
    problems = grid_gate.grid_problems(STUDY)
    assert problems == [], "\n  ".join([""] + problems)
    assert len(design_grid["rows"]) > 100, "the grid under assertion is real"


def test_a_seeded_non_canonical_decimal_fails_the_assertion(tmp_path, design_grid):
    """The construction the BRIEF names, seeded into a copy of the real grid:
    a spend authored at scale 1. The gate must name it and `--check` must exit
    nonzero."""
    seeded = json.loads(json.dumps(design_grid))
    row = next(entry for entry in seeded["rows"]
               if isinstance(entry["inputs"].get("spend"), str))
    row["inputs"]["spend"] = "70.1"
    root = _scratch_grid(tmp_path, seeded)
    problems = grid_gate.grid_problems(root)
    assert any("scale 1" in problem for problem in problems), problems
    assert any(row["id"] in problem for problem in problems), problems

    # and the round trip's own construction, seeded into the same grid: an
    # exponent form is a JSON number the projection reads and cannot write back
    seeded = json.loads(json.dumps(design_grid))
    row = next(entry for entry in seeded["rows"]
               if isinstance(entry["inputs"].get("spend"), str))
    row["inputs"]["spend"] = "7.010E+3"
    problems = grid_gate.grid_problems(_scratch_grid(tmp_path / "exponent",
                                                     seeded))
    assert any("re-serializes to" in problem for problem in problems), problems


def test_a_seeded_range_violation_fails_the_assertion(tmp_path, design_grid):
    """The other registered half — "no malformed or out-of-range values" — on
    both numeric axes and on an enumerated one."""
    for cell, value, needle in (("risk", "120", "0..100"),
                                ("spend", "20000000.00", "0.00..10000000.00"),
                                ("sanctions", "PROBABLY", "CLEAR/MATCH/UNKNOWN")):
        seeded = json.loads(json.dumps(design_grid))
        seeded["rows"][0]["inputs"][cell] = value
        root = _scratch_grid(tmp_path / cell, seeded)
        problems = grid_gate.grid_problems(root)
        assert any(needle in problem for problem in problems), (cell, problems)


def test_a_malformed_cell_set_is_a_refusal(tmp_path, design_grid):
    """The row's cells are EXACTLY the nine canonical ones: a surplus cell is a
    fact this policy family does not carry, and a missing one is a cell nobody
    authored — the grid writes an omitted input as a JSON null."""
    seeded = json.loads(json.dumps(design_grid))
    seeded["rows"][0]["inputs"]["tenure"] = "long"
    problems = grid_gate.grid_problems(_scratch_grid(tmp_path / "surplus", seeded))
    assert any("not a canonical grid cell" in problem for problem in problems), \
        problems

    seeded = json.loads(json.dumps(design_grid))
    del seeded["rows"][0]["inputs"]["insurance"]
    problems = grid_gate.grid_problems(_scratch_grid(tmp_path / "missing", seeded))
    assert any("canonical cell insurance is absent" in problem
               for problem in problems), problems


def test_a_duplicate_row_identity_and_a_duplicate_member_are_refused(
        tmp_path, design_grid):
    """Two rows with one id have no per-row result, and a duplicate JSON member
    is a grid readable two ways — the same rule the round-state block keeps."""
    seeded = json.loads(json.dumps(design_grid))
    seeded["rows"].append(json.loads(json.dumps(seeded["rows"][0])))
    problems = grid_gate.grid_problems(_scratch_grid(tmp_path / "dup", seeded))
    assert any("rows with the id" in problem for problem in problems), problems

    where = tmp_path / "ambiguous" / "design" / "gold"
    where.mkdir(parents=True)
    (where / "gold.json").write_text(
        '{"rows": [], "rows": [{"id": "x", "inputs": {}}]}', encoding="utf-8")
    problems = grid_gate.grid_problems(str(tmp_path / "ambiguous"))
    assert any("duplicate object keys" in problem for problem in problems), \
        problems


def test_a_tree_with_no_grid_at_all_is_refused(tmp_path):
    """A gate that is vacuous is a gate that has never run. The freeze-time
    assertion is over the grid being frozen, so a tree carrying neither the
    frozen suite nor the authored grid is a refusal rather than a pass."""
    problems = grid_gate.grid_problems(str(tmp_path))
    assert any("no canonical grid is present" in problem
               for problem in problems), problems


def test_the_command_line_reports_nonzero_on_failure(tmp_path, design_grid,
                                                     monkeypatch, capsys):
    """"exit nonzero otherwise", in the BRIEF's own words."""
    assert grid_gate.main(["--check"]) == 0
    seeded = json.loads(json.dumps(design_grid))
    seeded["rows"][0]["inputs"]["risk"] = "999"
    root = _scratch_grid(tmp_path, seeded)
    monkeypatch.setattr(grid_gate, "STUDY", root)
    assert grid_gate.main(["--check"]) == 1
    assert "grid assertion failed" in capsys.readouterr().out
