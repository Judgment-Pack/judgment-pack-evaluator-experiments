#!/usr/bin/env python3
"""§3.3's partition and the scorer's are one list, or they are two claims and
the second one is prose.

§3.3 registers the partition exhaustively, code by code, and says in its own
text that "a harness test parses this table out of this file and diffs it
against the scorer's own partition table and against the codes its admission
can actually return". This is that test, and it is three-way on purpose:

  the PREREGISTRATION's table   ==   `score_rates.CODE_PARTITION`   ==   the
  codes `admit()` and `score_run()` can actually return

Two of the three would not be enough. A table that matches the file but names
a code no function returns is a registered outcome that cannot happen; a
function that returns a code the table does not carry is an outcome with no
registered partition, and §4.2's arithmetic would have nowhere to put it.

The table is located by its SHAPE — the pipe table whose header is
`| outcome | partition |` — so it is still found when the file is edited
above it, and a line number never becomes part of the registration.
"""
from __future__ import annotations
import ast

import fixtures
import score_rates

# §3.3: "Three codes are new to this study", each closing a route round 1 or
# round 2 found open. They are the reason C4 registers three extra fixtures,
# and the reason this file checks the table rather than trusting it.
NEW_CODES = ("arm-mismatch", "schedule-mismatch", "session-reused")
# §3.3's two valid outcomes, which carry no code: the row for a completion with
# no parseable array, and the row for an ordinary valid run.
VALID_ROWS = ("(no code, no parseable array)", "(no code)")


def partition_table(body: str) -> tuple:
    """({outcome: partition}, [the no-code rows]) as §3.3's table registers
    them, parsed out of the frozen preregistration by the table's shape."""
    for header, rows in fixtures.markdown_tables(body):
        if [fixtures.plain(cell) for cell in header] != ["outcome", "partition"]:
            continue
        codes, valid = {}, []
        for outcome, partition in rows:
            outcome = fixtures.plain(outcome)
            partition = fixtures.plain(partition)
            if outcome.startswith("("):
                valid.append((outcome, partition))
            else:
                codes[outcome.strip("`")] = partition
        return codes, valid
    raise AssertionError("§3.3's | outcome | partition | table is not in the "
                         "preregistration: the partition is not registered")


def returnable_codes() -> set:
    """Every code `admit()` and `score_run()` can name, read off the source
    rather than off a comment: the first member of every tuple they return or
    assign to the `(code, detail, empty)` triple."""
    with open(score_rates.__file__.replace(".pyc", ".py"), "rb") as handle:
        tree = ast.parse(handle.read().decode("utf-8"))
    codes = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef)
                and node.name in ("admit", "score_run")):
            continue
        for inner in ast.walk(node):
            value = getattr(inner, "value", None) if isinstance(
                inner, (ast.Return, ast.Assign)) else None
            if isinstance(value, ast.Tuple) and value.elts:
                first = value.elts[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    codes.add(first.value)
    return codes


def test_the_registered_partition_is_the_scorers_partition(preregistration):
    registered, _valid = partition_table(preregistration)
    assert registered == score_rates.CODE_PARTITION, (
        "PREREGISTRATION.md §3.3 and score_rates.CODE_PARTITION disagree: %r"
        % sorted(set(registered.items()) ^ set(score_rates.CODE_PARTITION.items())))


def test_the_partition_is_exhaustive_over_one_class(preregistration):
    """Every code in §3.3's table is pipeline-invalid — the partition has one
    invalid class, and §4.2 counts it into the primary denominator rather than
    out of it, so a second class would silently change what a rate is over."""
    registered, _valid = partition_table(preregistration)
    assert set(registered.values()) == {"pipeline-invalid"}
    assert set(score_rates.CODE_PARTITION.values()) == {"pipeline-invalid"}


def test_the_codes_the_scorer_can_return_are_the_codes_it_registers(preregistration):
    registered, _valid = partition_table(preregistration)
    returnable = returnable_codes()
    assert returnable == set(score_rates.CODE_PARTITION), (
        "admit()/score_run() and CODE_PARTITION disagree: %r"
        % sorted(returnable ^ set(score_rates.CODE_PARTITION)))
    assert returnable == set(registered), (
        "admit()/score_run() and PREREGISTRATION.md §3.3 disagree: %r"
        % sorted(returnable ^ set(registered)))


def test_the_two_valid_outcomes_carry_no_code(preregistration):
    """§3.3's last two rows: a completion with no parseable JSON array is
    `authoring-empty` — valid, in every denominator, covering nothing — and an
    ordinary valid run carries no code either. Neither is a refusal, and the
    scorer names both."""
    _registered, valid = partition_table(preregistration)
    assert [row[0] for row in valid] == list(VALID_ROWS)
    assert "authoring-empty" in valid[0][1]
    assert "valid" in valid[1][1]
    assert score_rates.VALID_OUTCOMES == ("valid", "authoring-empty")
    for outcome in score_rates.VALID_OUTCOMES:
        assert outcome not in score_rates.CODE_PARTITION


def test_the_three_new_codes_are_registered_and_encoded(preregistration):
    """The three codes §3.3 marks as new to this study — the ones C4's extra
    fixtures exist for. They are in the table, they are in the scorer's
    partition, and `admit()` can actually return each of them."""
    registered, _valid = partition_table(preregistration)
    returnable = returnable_codes()
    for code in NEW_CODES:
        assert code in registered, code
        assert code in score_rates.CODE_PARTITION, code
        assert code in returnable, code
    # …and the preregistration marks exactly these three as new, in the
    # sentence that introduces them.
    introduction = preregistration.split("**Three codes are new to this study**")[1]
    introduction = introduction.split("Every other code")[0]
    named = [code for code in score_rates.CODE_PARTITION
             if "**`%s`**" % code in introduction]
    assert sorted(named) == sorted(NEW_CODES)


def test_the_partition_carries_no_code_the_prose_forgot(preregistration):
    """A code that appears in the table but nowhere in the file's prose is a
    code no reader was told about; a code in the prose that the table omits is
    an outcome with no partition. The first is what this checks, because the
    second is what the diff above already catches."""
    registered, _valid = partition_table(preregistration)
    for code in registered:
        assert "`%s`" % code in preregistration, code


def test_the_seal_failure_is_deliberately_not_a_code(preregistration):
    """§3.3's closing paragraph: a slot whose recomputed `SLOT-MANIFEST.json`
    disagrees with the ledger is NOT given a refusal code, because a code would
    understate it — it invalidates confirmatory scoring for the whole batch.
    The scorer's partition must therefore hold no manifest or chain code."""
    registered, _valid = partition_table(preregistration)
    assert not [code for code in registered
                if "manifest" in code or "seal" in code or "chain" in code]
    assert "One class of failure is deliberately *not* a refusal code" in preregistration
    # `verify_seal()` returns a SENTENCE and not a code, and `score()`'s caller
    # decides what the batch's verdicts are worth (C5 rule 6).
    assert score_rates.verify_seal.__doc__.strip().startswith(
        "None when this slot's seal holds, else the discrepancy in one sentence")
