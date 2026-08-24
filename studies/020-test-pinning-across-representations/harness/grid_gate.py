"""The canonical grid's freeze-time assertion — registered, and now RUN.

**ROUND-8 FINDING R8-8.** Two documents in this tree register an assertion that
runs AT THE FREEZE over the whole grid, and no code ran it and no step named it:

    design/BRIEF.md §2.3   "The canonical grid is authored as decimal strings
                            with a registered fixed scale per numeric field
                            (string->number is total and lossless; number->string
                            is where decimal identity dies — `"70.10"` must never
                            round-trip to `"70.1"`). The Rego projection is
                            `to_number` over those exact bytes, with a
                            freeze-time round-trip assertion over the full grid
                            (project -> re-serialize -> byte-equal, exit nonzero
                            otherwise)."

    design/POLICY-DRAFT.md "The canonical grid carries no malformed or
                            out-of-range values, asserted at freeze."

Both sentences describe a gate. Neither had one. `harness/SCAFFOLD.md`'s
freeze-fill enumerated the adequacy lemma, the off-gold certificate, the
clean-room re-run, the OC table, the artifacts, round 7's three new documents
and the pins — and not this. A registered assertion outside the ceremony is a
promise, and this study's whole subject is the difference.

WHAT THIS MODULE ASSERTS, OVER EVERY ROW OF EVERY GRID IN THE TREE
------------------------------------------------------------------------------
1. **Shape.** The grid is the registered object, its rows are objects, each row
   carries an `id` and an `inputs` object, and `inputs` carries EXACTLY the nine
   canonical cells. A surplus cell is a fact this policy family does not carry;
   a missing one is a cell nobody authored.

2. **Range and form** — `e4lib/domain.py`'s registered domain, in arm A's wire
   form, which is the canonical one. This is not a second implementation of the
   domain: the grid is checked by the same function the scorer applies to every
   enumerated case, so a grid the gate admits is a grid inside the space the
   off-gold certificate covers. The canonical grid writes an OMITTED input as a
   JSON `null` (`design/gold/gold_author.py`: "null = the input is omitted from
   the engine") and the projection drops it; the WIRE form registers omission as
   an absent member, and `domain.py` refuses a wire-form null. The two are the
   same statement in the two places it is made, so the null is translated here,
   at the one point that knows the grid's authoring convention.

3. **Fixed scale.** Risk is scale 0 and spend is scale 2, exactly — the registered
   per-field scale. `"70.1"` where the registration says scale 2 is not a
   rounding difference, it is a different registered value.

4. **The round trip, byte for byte.** Each numeric literal is projected the way
   `design/gold/check_gold.py` projects it for arm B — `to_number` over those
   exact bytes — and re-serialized, and the result must be the SAME BYTES. The
   projection here reads JSON numbers as exact decimals; the ordinary one reads
   them as binary floats, and `json.dumps(json.loads("70.10"))` is `70.1`. That
   is the failure the BRIEF names, it is one decoder argument away at all times,
   and this is the assertion that would catch it having been made.

WHICH GRIDS
------------------------------------------------------------------------------
`gold/GOLD.json` is the frozen suite and does not exist yet;
`design/gold/gold.json` is the authored grid it will be frozen FROM and exists
today. Both are checked when present, and a tree with neither is refused rather
than passed — a gate that is vacuous before the freeze is a gate that has never
run when the freeze arrives. `harness/make_manifest.py --freeze` and
`--freeze-gates` invoke `grid_problems()`, `harness/SCAFFOLD.md` item F names
the step, and `harness/tests/test_grid_gate.py` runs it against a seeded
non-canonical decimal and a seeded range violation.

Run: <the pinned interpreter> harness/grid_gate.py [--check]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from decimal import Decimal, InvalidOperation

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# The grids this gate covers, in the order it reports them. The frozen suite
# first, because after the freeze it is the one that decides anything.
GRID_PATHS = ("gold/GOLD.json", "design/gold/gold.json")

# The canonical cell schema, shared with `design/gold/gold_author.py`'s row
# writer and `design/gold/check_gold.py`'s two projections.
CANONICAL_CELLS = ("risk", "spend", "sanctions", "country", "newVendor",
                   "critical", "prior", "finEvidence", "insurance")

# The registered fixed scale per numeric field (BRIEF §2.3, and the naming
# appendix's wire forms: "risk scale 0, spend scale 2, no leading zeros").
REGISTERED_SCALE = {"risk": 0, "spend": 2}


class GridError(Exception):
    """The grid cannot be read as a grid at all."""


# --------------------------------------------------------------------------
# the projection, and its inverse
# --------------------------------------------------------------------------

def project(literal: str) -> Decimal:
    """`to_number` over those exact bytes, as an EXACT decimal.

    This is arm B's registered projection: `design/gold/check_gold.py` writes
    the canonical string into the input document unquoted — "unquoted: exact
    JSON number" — so the bytes the engine reads are the canonical bytes, and
    what the projection must not do is lose the decimal identity of those bytes
    on the way in."""
    if not isinstance(literal, str):
        raise GridError("a canonical numeric cell is a decimal STRING and this "
                        "one is a JSON %s" % type(literal).__name__)
    try:
        value = json.loads(literal, parse_float=Decimal, parse_int=Decimal)
    except ValueError as error:
        raise GridError("%r is not a JSON number: %s" % (literal, error))
    if not isinstance(value, Decimal):
        raise GridError("%r projects to a JSON %s and the registered projection "
                        "is over a number" % (literal, type(value).__name__))
    return value


def reserialize(value: Decimal) -> str:
    """The number back to its bytes, at the scale it carries. `format(…, "f")`
    rather than `str()`, because `str()` of a `Decimal` may choose an exponent
    form and an exponent form is not a wire form this study registers."""
    return format(value, "f")


def roundtrip_problem(cell: str, literal) -> str:
    """`project -> re-serialize -> byte-equal`, the BRIEF's assertion, for one
    cell. Returns None when the bytes survive."""
    try:
        value = project(literal)
    except GridError as error:
        return "%s %s" % (cell, error)
    written = reserialize(value)
    if written != literal:
        return ("%s projects %r and re-serializes to %r; the registered "
                "projection is byte-preserving and decimal identity died on "
                "the way through" % (cell, literal, written))
    return None


def scale_problem(cell: str, literal: str) -> str:
    """The registered fixed scale, stated as a scale rather than as a regex —
    `"70.1"` and `"70.10"` are two different registered values, and only one of
    them is in a grid whose spend field is scale 2."""
    try:
        value = Decimal(literal)
    except (InvalidOperation, ValueError, ArithmeticError):
        return "%s is %r and is not a readable decimal" % (cell, literal)
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int):
        return "%s is %r and carries no finite scale" % (cell, literal)
    scale = -exponent
    if scale != REGISTERED_SCALE[cell]:
        return ("%s is %r, which is scale %d; the registered fixed scale for "
                "%s is %d" % (cell, literal, scale, cell,
                              REGISTERED_SCALE[cell]))
    return None


# --------------------------------------------------------------------------
# one row
# --------------------------------------------------------------------------

def row_problems(row_id, inputs) -> list:
    """Every way one canonical row leaves the registration, sorted.

    The domain half is `e4lib/domain.py`'s own function in arm A's wire form —
    one implementation of the registered domain, applied here to the grid and at
    the attempt to every enumerated case."""
    from e4lib import domain as domain_module

    problems = []
    if not isinstance(inputs, dict):
        return ["%s: `inputs` is a JSON %s and a row's inputs are an object"
                % (row_id, type(inputs).__name__)]
    surplus = sorted(set(inputs) - set(CANONICAL_CELLS))
    missing = [cell for cell in CANONICAL_CELLS if cell not in inputs]
    for cell in surplus:
        problems.append("%s: %s is not a canonical grid cell" % (row_id, cell))
    for cell in missing:
        problems.append("%s: the canonical cell %s is absent; the grid's "
                        "omission encoding is a JSON null, not a missing member"
                        % (row_id, cell))
    signature = {}
    for cell in CANONICAL_CELLS:
        value = inputs.get(cell)
        # The grid writes an omitted input as a JSON null and the projection
        # drops it; the WIRE form registers omission as an absent member. The
        # translation happens here, once, at the layer that knows the grid's
        # convention — never inside `domain.py`, which must go on refusing a
        # wire-form null.
        signature[cell] = None if value is None else value
    for problem in domain_module.domain_problems(signature, "string"):
        problems.append("%s: %s" % (row_id, problem))
    for cell in sorted(REGISTERED_SCALE):
        literal = signature.get(cell)
        if literal is None or not isinstance(literal, str):
            continue                      # omitted, or already named above
        for problem in (scale_problem(cell, literal),
                        roundtrip_problem(cell, literal)):
            if problem:
                problems.append("%s: %s" % (row_id, problem))
    return sorted(problems)


# --------------------------------------------------------------------------
# the whole grid
# --------------------------------------------------------------------------

def _rows(relative, data):
    """`(rows, refusal)` — the registered grid shapes and nothing else."""
    if isinstance(data, list):
        return data, None
    if not isinstance(data, dict):
        return None, ("%s is a JSON %s and a grid is an object with a `rows` "
                      "list" % (relative, type(data).__name__))
    rows = data.get("rows")
    if not isinstance(rows, list):
        return None, "%s carries no top-level `rows` list" % relative
    return rows, None


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _value in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object keys")
    return dict(pairs)


def grid_problems(study=None) -> list:
    """Every registered grid in the tree, row by row, problems sorted.

    A tree carrying NEITHER grid is a problem in itself: the whole point of a
    freeze-time assertion is that it has run over the bytes being frozen."""
    root = study or STUDY
    problems, seen = [], []
    for relative in GRID_PATHS:
        path = os.path.join(root, relative)
        if not os.path.isfile(path):
            continue
        seen.append(relative)
        with open(path, "rb") as handle:
            raw = handle.read()
        try:
            data = json.loads(raw.decode("utf-8"),
                              object_pairs_hook=_refuse_duplicate_keys)
        except (ValueError, UnicodeDecodeError) as error:
            problems.append("%s is not readable JSON (%s: %s)"
                            % (relative, type(error).__name__, error))
            continue
        rows, refusal = _rows(relative, data)
        if refusal is not None:
            problems.append(refusal)
            continue
        if not rows:
            problems.append("%s carries no rows" % relative)
            continue
        identities = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                problems.append("%s row %d is a JSON %s and a row is an object"
                                % (relative, index, type(row).__name__))
                continue
            identity = row.get("id")
            if not isinstance(identity, str) or not identity.strip():
                problems.append("%s row %d carries no string `id`"
                                % (relative, index))
                identity = "row %d" % index
            identities.append(identity)
            if "inputs" not in row:
                problems.append("%s %s carries no `inputs`" % (relative, identity))
                continue
            problems.extend("%s %s" % (relative, problem)
                            for problem in row_problems(identity, row["inputs"]))
        for identity in sorted(set(identities)):
            if identities.count(identity) > 1:
                problems.append("%s carries %d rows with the id %s"
                                % (relative, identities.count(identity), identity))
    if not seen:
        problems.append(
            "no canonical grid is present (%s); the registered freeze-time "
            "assertion is over the grid being frozen, and a gate with nothing "
            "to read has never run" % ", ".join(GRID_PATHS))
    return sorted(problems)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="run the registered freeze-time grid assertion")
    parser.parse_args(argv)
    problems = grid_problems()
    for problem in problems:
        print("grid assertion failed: " + problem)
    if not problems:
        print("canonical grid assertion holds over %s"
              % ", ".join(relative for relative in GRID_PATHS
                          if os.path.isfile(os.path.join(STUDY, relative))))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
